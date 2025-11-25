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

# from SARDINE_aircraft.phase_info import (
#     two_dof_phase_info as sardine_phase_info,
# )
# from large_turboprop_freighter.phase_info import (
#     two_dof_phase_info as turboprop_phase_info,
# )

# import large_turboprop_freighter_GASP as large_turboprop_freighter_GASP
from phase_info import two_dof_phase_info, energy_phase_info

# from two_dof_test import phase_info

prob = av.AviaryProblem()

# prob.load_inputs(
#     "SARDINE_aircraft/sardine_turboprop_GASP.csv",
#     sardine_phase_info,
# )

prob.load_inputs(
    # "large_turboprop_freighter/large_turboprop_freighter_GASP.csv",
    # large_turboprop_freighter_GASP
    "large_turboprop_freighter_GASP.csv",
    # "generic_BWB_GASP.csv",
    # turboprop_phase_info,
    two_dof_phase_info,
)

# prob.aircraft.wing_span. =

prob.check_and_preprocess_inputs()

prob.build_model()

# optimizer and iteration limit are optional provided here
prob.add_driver("IPOPT", max_iter=150)
# prob.driver.options["tol"] = 1e-6

prob.add_design_variables()

prob.add_objective()

prob.setup()

prob.run_aviary_problem()
