import openmdao.api as om
import OpenMDAO_Sellar as dsc

# Set up the problem
prob = om.Problem()
prob.model = dsc.SellarMDAPromoteConnect()

# # setups the problem from dsc script
# prob.setup()

# # sets up the initial x and z values for the solver
# prob.set_val('indvar.x',2.0)
# prob.set_val('indvar.z',[-1.0,-1.0])

# # runs the model using the initial variables
# prob.run_model()

# # develop an N2 diagram for better understanding of variable alocation
# # generates n2 diagram of the prob (om.Problem()
# om.n2(prob)

# # prints the output into the terminal 
# print(f"y1 = {prob.get_val('cycle.d1.y1')}, y2 = {prob.get_val('cycle.d1.y2')}")

## we have to define the driver instead of the problem
prob.driver = om.ScipyOptimizeDriver()

# setup the type of optimizer using different options
prob.driver.options['optimizer'] = 'SLSQP' #optimizer type
prob.driver.options['maxiter'] = 100 # max iterations
prob.driver.options['tol'] = 1.0e-8 # set tolerance

# add design variables 
# NOTE: we need to setup promotions 
prob.model.add_design_var('x',lower=0.0,upper=10.0)  #sets the x variable with an upper and lower bound
prob.model.add_design_var('z',lower=0.0,upper=10.0)  #sets the v variable with an upper and lower bound

# add objective
prob.model.add_objective('obj')

# add constraint 
# since we have the constraints as a equality subsystem, we must call it here,
# but have it as an inequality for it to be a constraint and not a bound
prob.model.add_constraint('con1', upper=0.0)
prob.model.add_constraint('con2', upper=0.0)

# approximates the totals in the model
prob.model.approx_totals() # slows everything down

prob.set_solver_print(level=0) # prints an error if there is an error (-1 silences errors)

# setup the problem and run the driver/optimizer
prob.setup()
prob.run_driver()

print('minimum found at')
print(prob.get_val('x'))
print(prob.get_val('z'))

## to increase speed, we can list the partial derivatives rather than having the computer solve it
# instead of finite difference, we can use complex step as well