"""OpenMDAO system for generating the aero tables that were typically printed in FLOPS."""

import numpy as np
import openmdao.api as om

from aviary.variable_info.functions import add_aviary_input, add_aviary_option, add_aviary_output
from aviary.variable_info.variables import Aircraft, Mission, Dynamic
from aviary.variable_info.variable_meta_data import _MetaData as _meta_data


class OVLLiftDrag(om.ExplicitComponent):
    """
    This will need to create an instance of the dynamic aero group, perhaps as a
    subproblem, and run it at the table of Mach numbers and lift coefficients. Right now,
    it is a placeholder, and also serves as a sink for all parts of the aircraft data
    structures that are passed to the dynamic portion, so that they can be overridden if
    needed.
    """

    def initialize(self):
        self.options.declare(
            'num_nodes', default=1, types=int, desc='Number of nodes along mission segment'
        )

    def setup(self):
        nn = self.options['num_nodes']

        # Aircraft Geometry Inputs
        add_aviary_input(self, Aircraft.Wing.AREA, units='ft**2')
        add_aviary_input(self, Aircraft.Wing.WETTED_AREA, units='ft**2')
        add_aviary_input(self, Aircraft.Wing.WETTED_AREA_SCALER, units='unitless')
        add_aviary_input(self, Aircraft.Wing.CHORD_PER_SEMISPAN_DIST, units='unitless')
        add_aviary_input(self, Aircraft.Wing.DIHEDRAL, units='deg')
        add_aviary_input(self, Aircraft.Wing.HEIGHT, units='ft')
        add_aviary_input(self, Aircraft.Wing.SPAN, units='ft')
        add_aviary_input(self, Aircraft.Wing.SWEEP, units='deg')
        add_aviary_input(self, Aircraft.Wing.TAPER_RATIO, units='unitless')
        add_aviary_input(self, Aircraft.Wing.THICKNESS_TO_CHORD_ROOT, units='unitless')
        add_aviary_input(self, Aircraft.Wing.MAX_CAMBER_AT_70_SEMISPAN, units='unitless')
        
        add_aviary_input(self, Aircraft.VerticalTail.AREA, units='ft**2')
        add_aviary_input(self, Aircraft.VerticalTail.ASPECT_RATIO, units='unitless')
        add_aviary_input(self, Aircraft.VerticalTail.SWEEP, units='deg')
        add_aviary_input(self, Aircraft.VerticalTail.TAPER_RATIO, units='unitless')
        add_aviary_input(self, Aircraft.VerticalTail.THICKNESS_TO_CHORD, units='unitless')
        
        add_aviary_input(self, Aircraft.HorizontalTail.AREA, units='ft**2')
        add_aviary_input(self, Aircraft.HorizontalTail.ASPECT_RATIO, units='unitless')
        add_aviary_input(self, Aircraft.HorizontalTail.SWEEP, units='deg')
        add_aviary_input(self, Aircraft.HorizontalTail.TAPER_RATIO, units='unitless')
        add_aviary_input(self, Aircraft.HorizontalTail.THICKNESS_TO_CHORD, units='unitless')
        
        add_aviary_input(self, Aircraft.Fuselage.LENGTH, units='ft')
        add_aviary_input(self, Aircraft.Fuselage.MAX_HEIGHT, units='ft')
        add_aviary_input(self, Aircraft.Fuselage.MAX_WIDTH, units='ft')
        
        # Aircraft Flow Conditions
        add_aviary_input(self, Dynamic.Atmosphere.MACH, shape=nn, units='unitless')
        add_aviary_input(self, Dynamic.Vehicle.ANGLE_OF_ATTACK, shape=nn, units='deg')
        add_aviary_input(self, Dynamic.Mission.ALTITUDE, shape=nn, units='ft')
        add_aviary_input(self, Dynamic.Atmosphere.DYNAMIC_PRESSURE, shape=nn, units='psf')
        
       # Declare outputs
        add_aviary_output(self, Dynamic.Vehicle.LIFT, shape=nn, units='lbf')
        add_aviary_output(self, Dynamic.Vehicle.DRAG, shape=nn, units='lbf')

    
    def setup_partials(self):
        nn = self.options['num_nodes']

        row_col = np.arange(nn)
        self.declare_partials('*','*', rows=row_col, cols=row_col)

    #AVL geometry file writer for a conventional aircraft
    def compute(self, inputs, outputs):
        import optvl as OVLSolver
        """Generate an AVL geometry file based on the aircraft geometry inputs."""
        vt_camber = 0.0  # Typically vertical tails are not cambered
        ht_camber = 0.0  # Typically horizontal tails are not cambered
        
        wing_area = inputs[Aircraft.Wing.AREA]
        wing_taper = inputs[Aircraft.Wing.TAPER_RATIO]
        wing_dihedral = inputs[Aircraft.Wing.DIHEDRAL]
        wing_height = inputs[Aircraft.Wing.HEIGHT]
        wing_span = inputs[Aircraft.Wing.SPAN]
        wing_sweep = inputs[Aircraft.Wing.SWEEP]
        wing_tc_root = inputs[Aircraft.Wing.THICKNESS_TO_CHORD_ROOT]
        wing_camber = inputs[Aircraft.Wing.MAX_CAMBER_AT_70_SEMISPAN]
        
        fus_length = inputs[Aircraft.Fuselage.LENGTH]
        fus_height = inputs[Aircraft.Fuselage.MAX_HEIGHT]
        fus_width = inputs[Aircraft.Fuselage.MAX_WIDTH]
        
        vt_area = inputs[Aircraft.VerticalTail.AREA]
        vt_AR = inputs[Aircraft.VerticalTail.ASPECT_RATIO]
        vt_sweep = inputs[Aircraft.VerticalTail.SWEEP]
        vt_taper = inputs[Aircraft.VerticalTail.TAPER_RATIO]
        vt_tc = inputs[Aircraft.VerticalTail.THICKNESS_TO_CHORD]
        
        ht_area = inputs[Aircraft.HorizontalTail.AREA]
        ht_AR = inputs[Aircraft.HorizontalTail.ASPECT_RATIO]
        ht_sweep = inputs[Aircraft.HorizontalTail.SWEEP]
        ht_taper = inputs[Aircraft.HorizontalTail.TAPER_RATIO]
        ht_tc = inputs[Aircraft.HorizontalTail.THICKNESS_TO_CHORD]
        
        filename = "aircraft_geometry.avl"
        
        # ---------- DERIVED VALUES ----------
        wing_c_root = (2 * wing_area) / (wing_span * (1 + wing_taper))
        wing_c_tip  = wing_c_root * wing_taper

        vt_span = (vt_area * vt_AR) ** 0.5
        vt_c_root = (2 * vt_area) / (vt_span * (1 + vt_taper))
        vt_c_tip = vt_c_root * vt_taper

        ht_span = (ht_area * ht_AR) ** 0.5
        ht_c_root = (2 * ht_area) / (ht_span * (1 + ht_taper))
        ht_c_tip = ht_c_root * ht_taper

        # Convert sweep to radians tangent form since AVL uses LE x-offset
        import math
        wing_LE_sweep_offset = (wing_span / 2) * math.tan(math.radians(wing_sweep))
        vt_LE_sweep_offset   = (vt_span / 2) * math.tan(math.radians(vt_sweep))
        ht_LE_sweep_offset   = (ht_span / 2) * math.tan(math.radians(ht_sweep))

        # NACA-style camber line encapsulation
        wing_airfoil = f"NACA {int(wing_camber*100)}{int(wing_tc_root*100)}"
        ht_airfoil   = f"NACA {int(ht_camber*100)}{int(ht_tc*100)}"
        vt_airfoil   = f"NACA {int(vt_camber*100)}{int(vt_tc*100)}"

        # ---------- WRITE AVL FILE ----------
        with open(filename, "w") as f:

            f.write("Generated AVL Aircraft\n")
            f.write("# --------------------------------------------------\n\n")

            # -------- AIRCRAFT PARAMETERS --------
            f.write("0.0  0.0  0.0    # reference x y z\n")
            f.write("1.0            # reference chord\n")
            f.write("0.0  0.0  0.0    # CG location\n")
            f.write("\n")

            # ============================
            #            WING
            # ============================
            f.write("SURFACE\n")
            f.write("Wing\n")
            f.write("10   1.0\n")  # Nspan, Sspace

            f.write("SECTION\n")
            f.write(f"{0.0:8.4f}  {wing_height:8.4f}  {0.0:8.4f}  {wing_c_root:8.4f}  {math.radians(wing_dihedral):8.4f}  0.0\n")
            f.write(f"AIRFOIL\n{wing_airfoil}\n")

            f.write("SECTION\n")
            f.write(f"{wing_LE_sweep_offset:8.4f}  {wing_height:8.4f + wing_span/2*math.sin(math.radians(wing_dihedral)):8.4f}  {wing_span/2:8.4f}  {wing_c_tip:8.4f}  {math.radians(wing_dihedral):8.4f}  0.0\n")
            f.write(f"AIRFOIL\n{wing_airfoil}\n")

            # ============================
            #         HORIZONTAL TAIL
            # ============================
            f.write("\nSURFACE\n")
            f.write("Horizontal Tail\n")
            f.write("6  1.0\n")

            f.write("SECTION\n")
            f.write(f"{fus_length*0.9:8.4f}  {0.0:8.4f}  {0.0:8.4f}  {ht_c_root:8.4f}  0.0  0.0\n")
            f.write(f"AIRFOIL\n{ht_airfoil}\n")

            f.write("SECTION\n")
            f.write(f"{fus_length*0.9 + ht_LE_sweep_offset:8.4f}  {0.0:8.4f}  {ht_span/2:8.4f}  {ht_c_tip:8.4f} 0.0 0.0\n")
            f.write(f"AIRFOIL\n{ht_airfoil}\n")

            # ============================
            #           VERTICAL TAIL
            # ============================
            f.write("\nSURFACE\n")
            f.write("Vertical Tail\n")
            f.write("8  1.0\n")

            f.write("SECTION\n")
            f.write(f"{fus_length*0.7:8.4f}  {0.0:8.4f}  {0.0:8.4f}  {vt_c_root:8.4f}  0.0  0.0\n")
            f.write(f"AIRFOIL\n{vt_airfoil}\n")

            f.write("SECTION\n")
            f.write(f"{fus_length*0.7 + vt_LE_sweep_offset:8.4f}  {0.0:8.4f}  {vt_span:8.4f}  {vt_c_tip:8.4f}  0.0  0.0\n")
            f.write(f"AIRFOIL\n{vt_airfoil}\n")

            # ============================
            #           FUSELAGE
            # (AVL doesn't model bodies directly;
            #  a dummy component can be added)
            # ============================

            f.write("\n# Fuselage INFO (for documentation)\n")
            f.write(f"# Length: {fus_length}\n")
            f.write(f"# Height: {fus_height}\n")
            f.write(f"# Width:  {fus_width}\n")

        # ----------------------------
        # AVL FILE
        # ----------------------------
        avl_geometry_file = "aircraft_geometry.avl"
        ovl = OVLSolver(geo_file=avl_geometry_file, debug=True)

        # Run AVL / OptVL solver
        ovl.set_variable("alpha", inputs[Dynamic.Vehicle.ANGLE_OF_ATTACK])
        ovl.set_parameter("Mach", inputs[Dynamic.Atmosphere.MACH])
        ovl.execute_run()
        results = ovl.get_total_forces()
        
        # Extract CL and CD
        S = inputs[Aircraft.Wing.AREA]
        q = inputs[Dynamic.Atmosphere.DYNAMIC_PRESSURE]
        CD = results["CD"]+results["CDi"]+results["CDv"]
        CL = results["CL"]
        
        # standard atmosphere from ISA (simple layer model) - replace with your atmosphere function
        # troposphere up to 11km, simple implementation:
        import math
        
        # Constants
        T0_R = 518.67      # Rankine (Sea level)
        p0_psf = 2116.22   # lbf/ft^2
        rho0 = 0.0023769   # slug/ft^3
        g = 32.174         # ft/s^2
        R = 1716.49        # ft*lbf/(slug*R)
        L = -0.00356616    # Temperature lapse rate [R/ft]
        h_ft = inputs[Dynamic.Mission.ALTITUDE]

        if h_ft <= 36089:  # Troposphere up to ~11 km
            T = T0_R + L*h_ft
            p = p0_psf * (T / T0_R)**(-g/(R*L))
        else:
            # Isothermal stratosphere block (simplified)
            T = 389.97
            p = 472.68 * math.exp(-g*(h_ft-36089)/(R*T))

        rho = p / (R * T)
        a = math.sqrt(1.4 * R * T)   
        
        # Convert Rankine to Kelvin
        T_K = T * (5.0/9.0)
        mu0 = 1.716e-5       # Pa*s
        T0 = 273.15          # K
        St = 110.4            # K
        # Compute μ in SI, convert to imperial
        mu_SI = mu0 * (T_K/T0)**1.5 * (T0 + St)/(T_K + St)
        mu_imp = mu_SI * 0.020885434273  # Pa*s → lb*s/ft²
        
        Re = (rho * inputs[Dynamic.Atmosphere.MACH] * a * wing_c_root) / mu_imp
        Cf_flat = 0.074 / Re**0.2
        FF_wing = 1.2
        Cff = Cf_flat * FF_wing * (inputs[Aircraft.Wing.WETTED_AREA_SCALER] * inputs[Aircraft.Wing.WETTED_AREA]) / S
        
        outputs[Dynamic.Vehicle.DRAG] = q * S * (CD + Cff)
        outputs[Dynamic.Vehicle.LIFT] = q * S * CL

class OVLAeroGroup(om.Group):
    def initialize(self):
        self.options.declare(
            'num_nodes', default=1, types=int, desc='Number of nodes along mission segment'
        )

    def setup(self):
        nn = self.options['num_nodes']

        self.add_subsystem(
            'LiftDrag',
            OVLLiftDrag(num_nodes=nn),
            promotes_inputs=[
                Dynamic.Atmosphere.DYNAMIC_PRESSURE,
                Dynamic.Atmosphere.MACH,
                Dynamic.Vehicle.ANGLE_OF_ATTACK,
                Dynamic.Mission.ALTITUDE,
                'aircraft:*',
            ],
            promotes_outputs=[Dynamic.Vehicle.LIFT,
                              Dynamic.Vehicle.DRAG
                              ],
        )