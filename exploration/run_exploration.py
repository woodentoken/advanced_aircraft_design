import time
import ipdb

"""
This is an example of running a coupled aircraft design-mission optimization in Aviary using the
"level 2" API. It runs the same aircraft and mission as the `level1_example.py` script, but it uses
the AviaryProblem class to set up the problem. This exposes more options and flexibility to the user.

The same ".csv" file is used to define the aircraft, but now the phase_info dictionary is directly
imported from the file and passed as an argument. It is common for level 2 scripts to modify
existing phase_info, but here it is used as-is here to match the level 1 example.

We then call the correct methods in order to set up and run an Aviary optimization problem. Most
methods have optional arguments, but none are necessary here. The selection of the SLSQP optimizer
limited to 50 iterations are included to demonstrate of how those common settings are set.
"""

# this imports the two_dof_phase_info dictionary directly
import aviary.api as av

from height_energy_test import phase_info as he_phase_info
from two_dof_test import phase_info as td_phase_info

# he_phase_info["climb_1"]["user_options"]["mach_polynomial_order"] = 3
# he_phase_info["climb_1"]["user_options"]["altitude_polynomial_order"] = 3
# he_phase_info["cruise"]["user_options"]["mach_polynomial_order"] = 1
# he_phase_info["cruise"]["user_options"]["altitude_polynomial_order"] = 1
# he_phase_info["descent_1"]["user_options"]["mach_polynomial_order"] = 3
# he_phase_info["descent_1"]["user_options"]["altitude_polynomial_order"] = 3

# he_phase_info["climb_1"]["user_options"]["mach_optimize"] = True
# he_phase_info["climb_1"]["user_options"]["altitude_optimize"] = True
he_phase_info["cruise"]["user_options"]["mach_optimize"] = True
he_phase_info["cruise"]["user_options"]["altitude_optimize"] = True
# he_phase_info["descent_1"]["user_options"]["mach_optimize"] = True
# he_phase_info["descent_1"]["user_options"]["altitude_optimize"] = True

ac = "exploration_aircraft.csv"

prob = av.AviaryProblem()
prob.load_inputs(
    ac,
    he_phase_info,
)

# this divides based on reserve mission distinctions
prob.check_and_preprocess_inputs()

prob.build_model()

# optimizer and iteration limit are optional provided here
prob.add_driver("IPOPT", max_iter=200)

prob.add_design_variables()
prob.model.add_design_var(
    av.Aircraft.Wing.ASPECT_RATIO, lower=10.0, upper=14.0, ref=12.0
)

prob.add_objective()

prob.setup()


time_start = time.time()
prob.run_aviary_problem()
time_end = time.time()
print(f"Total optimization time: {time_end - time_start} seconds")

fixed_mission_fixed_wing_fuel_burn = prob.get_val(
    av.Mission.Summary.FUEL_BURNED, units="kg"
)[0]
fixed_mission_fixed_wing_aspect_ratio = prob.get_val(av.Aircraft.Wing.ASPECT_RATIO)[0]
print(fixed_mission_fixed_wing_fuel_burn)
print(fixed_mission_fixed_wing_aspect_ratio)
