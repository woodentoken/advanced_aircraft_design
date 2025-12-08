import time

import aviary.api as av
import dymos as dm
import openmdao.api as om

from missions.parametric_phase_infos import define_phase_info
from missions.sardine_phase_info import phase_info as sardine_height_energy_phases
# from missions.external_sardine_phase_info import phase_info as external_sardine_height_energy_phases
from missions.two_dof_default import phase_info as two_dof_phase_info

prob = av.AviaryProblem()

# GASP models
small_single_aisle_GASP = "C:\\Users\\tadco\\Desktop\\advanced_aircraft_design\\sardines\\aircraft\\small_single_aisle_GASP.csv"
sardine_turboprop_GASP = "C:\\Users\\tadco\\Desktop\\advanced_aircraft_design\\sardines\\aircraft\\sardine_turboprop_GASP.csv"

# FLOPS models
base_ASA = "C:\\Users\\tadco\\Desktop\\advanced_aircraft_design\\sardines\\aircraft\\advanced_single_aisle_FLOPS.csv"
sardine_ASA = "C:\\Users\\tadco\\Desktop\\advanced_aircraft_design\\sardines\\aircraft\\sardine_advanced_single_aisle_FLOPS.csv"

### Problem definition
prob.load_inputs(sardine_ASA, sardine_height_energy_phases)

prob.check_and_preprocess_inputs()

prob.build_model()

# optimizer and iteration limit are optional provided here
prob.add_driver("IPOPT", max_iter=100)
prob.driver.opt_settings["tol"] = 1.0e-4

prob.add_design_variables()

# add more design vars (these are just placeholders...)
# prob.model.add_design_var(
#     av.Aircraft.Wing.ASPECT_RATIO, lower=10.0, upper=20.0, ref=12.0
# )
# prob.model.add_design_var(
#     av.Aircraft.Wing.COMPOSITE_FRACTION, lower=0.25, upper=1.0, ref=0.5
# )
# prob.model.add_design_var(
#     av.Aircraft.Engine.SCALE_FACTOR, lower=0.25, upper=1.0, ref=0.5
# )

prob.add_objective()
prob.setup()
prob.set_initial_guesses()

start_time = time.time()
prob.run_aviary_problem()
end_time = time.time()
print(f"Total run time: {end_time - start_time} seconds")

# post mission reporting
burned_fuel = prob.get_val(av.Mission.Summary.FUEL_BURNED, units="lb")[0]
final_mass = prob.get_val(av.Mission.Summary.FINAL_MASS, units="lb")[0]
print(f"Fuel burned: {burned_fuel} lb")
print(f"Final mass: {final_mass} lb")
