import numpy as np
import openmdao.api as om


class SellarDis1(om.ExplicitComponent):
    """
    Component containing Discipline 1 -- no derivatives version.
    
    y1 = z2**2 + z2 + x1 - 0.2*y2
    """

    def setup(self):

        # Global Design Variable
        self.add_input('z', val=np.zeros(2)) #multi variables

        # Local Design Variable
        self.add_input('x', val=0.) # single variable

        # Coupling parameter: needs to get solved but not optimized
        self.add_input('y2', val=1.0) 

        # Coupling output: output that is being optimized for
        self.add_output('y1', val=1.0)
        
        # equivalent to setting up partial derivatives below
        # self.declare_partials('y1', ['z','x','y2'])

    # setting up partial derivatives
    def setup_partials(self):
        # Finite difference all partials.
        self.declare_partials('*', '*', method='fd') 
        # '*' means everything wrt everything, fd = finite difference (cs = complex step)

    # we need to compute something and evaluate the equation going in
    def compute(self, inputs, outputs):
        """
        Evaluates the equation
        y1 = z1**2 + z2 + x1 - 0.2*y2
        """
        #stored inputs locally
        z1 = inputs['z'][0] #first component in z array
        z2 = inputs['z'][1] #second component in z array
        x1 = inputs['x'] #only one x
        y2 = inputs['y2'] #only one y2

        #calculate the output by calculating the equation
        outputs['y1'] = z1**2 + z2 + x1 - 0.2*y2
        
        
# building second discipline class
class SellarDis2(om.ExplicitComponent):
    """
    Component containing Discipline 2 -- no derivatives version.
    """

    def setup(self):
        # Global Design Variable
        self.add_input('z', val=np.zeros(2))

        # Coupling parameter
        self.add_input('y1', val=1.0)

        # Coupling output
        self.add_output('y2', val=1.0)

    def setup_partials(self):
        # Finite difference all partials.
        self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):
        """
        Evaluates the equation
        y2 = y1**(.5) + z1 + z2
        """

        z1 = inputs['z'][0]
        z2 = inputs['z'][1]
        y1 = inputs['y1']

        # Note: this may cause some issues. However, y1 is constrained to be
        # above 3.16, so lets just let it converge, and the optimizer will
        # throw it out
        if y1.real < 0.0: # this is considered bad practice because it causes a discontinuity 
            y1 *= -1
        # since we constrained y1 to be above 3.16, being above 0 bound is 'okay'
        
        outputs['y2'] = y1**(.5) + z1 + z2 #negative number will output an imaginary number
        
### Both disciplines are independent and use local variables. In order to link them, we need to "group" them
## the disciplines we made ar ethe subsystems within a group

## Connection vs Promotion
    ## There are shortcuts and simplified ways
        
# Grouping and connecting components
class SellarMDA(om.Group): # Labeled as SellarMDAConnect in the MAE 298 Lecture 10/9/2025
    """
    Group containing the Sellar MDA.
    There are three different components
        Implicit Component
        Explicit Component
        Independent Variable
        
    In this case, we will be using Independent Variable for complex problems
    """
    
    def setup(self):
        # defined independent variables 
        indvar = self.add_subsystem('indvar', om.IndepVarComp())
        indvar.add_output('x', val=1.0)
        indvar.add_output('z', val=np.array([5.0, 2.0]))

        # Couple the cycle with a non-linear solver
        cycle = self.add_subsystem('cycle', om.Group())
        
        #adding subsystems into the cycle
        cycle.add_subsystem('d1', SellarDis1())
        cycle.add_subsystem('d2', SellarDis2())
        
        # connecting the cycle 
        cycle.connect('d1.y1', 'd2.y1') # disp 1 output goes to disp 2 output
        cycle.connect('d2.y2', 'd1.y2') # disp 2 output goes to disp 1 output
        
        # tell the cycle how to solve the subsystems/cycles
        # give it a non-linear block Gauss-seidel solver
        cycle.nonlinear_solver = om.NonlinearBlockGS()
        
        # At this point, they are in the same cycle and they will be solved however neither cycle shares information
        # We have to build objective and constraint functions (doesnt tell them any info on each other still)
        
        # you can technically build the om.ExecComp() into classes, and objective class and a constraint class
        self.add_subsystem('obj_cmp', om.ExecComp('obj = x**2 + z[1] + y1 + exp(-y2)',
                                                  z=np.array([0.0, 0.0]), x=0.0))
        
        # add constraints
        self.add_subsystem('obj_cmp1', om.ExecComp('con1 = 3.16 - y1'))
        self.add_subsystem('obj_cmp2', om.ExecComp('con2 = y2 - 24.0'))

        # we now need to connect the two disciplines by using the connect function
        self.connect('indvar.x',['cycle.d1.x','obj_cmp.x']) #tells OpenMDAO that all the x variables are connected (global variable)
        self.connect('indvar.z',['cycle.d1.z','cycle.d2.z','obj_cmp.z']) #repeats with z variables
        
        # linking output into the inputs
        self.connect('cycle.d1.y1',['obj_cmp.y1','obj_cmp1.y1'])
        self.connect('cycle.d2.y2',['obj_cmp.y2','obj_cmp2.y2'])
        
## Setup the promotions (take different exec things and if they have the same name, they prioritize)
## refer to n2 diagram levels

class SellarMDAPromoteConnect(om.Group):
    """
    Group containing the Sellar MDA. This version uses the disciplines without derivatives.
    """

    def setup(self):
        # defines cycle as a group and promotes everything (any input and output)
        cycle = self.add_subsystem('cycle', om.Group(), promotes=['*'])
         
        cycle.add_subsystem('d1', SellarDis1(),
                            promotes_inputs=['x', 'z','y2'], #input promo
                            promotes_outputs=['y1']) #output promo
        
        cycle.add_subsystem('d2', SellarDis2(),
                            promotes_inputs=['z','y1'],
                            promotes_outputs=['y2'])
        
        ## by promoting the variables, they share the variables and no longer needs to be connected

        # we set the input variables
        cycle.set_input_defaults('x', 1.0)
        cycle.set_input_defaults('z', np.array([5.0, 2.0]))

        # Nonlinear Block Gauss Seidel is a gradient free solver
        cycle.nonlinear_solver = om.NonlinearBlockGS()

        # building in the objectives WHILE promotoing variables
        self.add_subsystem('obj_cmp', om.ExecComp('obj = x**2 + z[1] + y1 + exp(-y2)',
                                                  z=np.array([0.0, 0.0]), x=0.0),
                           promotes_inputs=['x', 'z', 'y1', 'y2'],
                           promotes_outputs=['obj']) #variable promotion (no need to connect)

        # building in the constraints WHILE promoting variables
        # setting up subsystem that will later be called as a constraint
        self.add_subsystem('con_cmp1', om.ExecComp('con1 = 3.16 - y1'),
                           promotes_inputs=['y1'],
                           promotes_outputs=['con1'])
        self.add_subsystem('con_cmp2', om.ExecComp('con2 = y2 - 24.0'),
                           promotes_inputs=['y2'],
                           promotes_outputs=['con2'])


prob = om.Problem()
prob.model = SellarMDAPromoteConnect()

prob.setup()

prob.set_val('x', 2.0)
prob.set_val('z', [-1., -1.])

prob.run_model()