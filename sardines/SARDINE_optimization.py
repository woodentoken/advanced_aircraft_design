import time

import aviary.api as av
import dymos as dm
import openmdao.api as om

from missions.parametric_phase_infos import define_phase_info
from missions.sardine_phase_info import phase_info as sardine_height_energy_phases
from missions.two_dof_default import phase_info as two_dof_phase_info

# GASP models
small_single_aisle_GASP = "aircraft/small_single_aisle_GASP.csv"
sardine_turboprop_GASP = "aircraft/sardine_turboprop_GASP.csv"

# FLOPS models
base_ASA = "aircraft/advanced_single_aisle_FLOPS.csv"
sardine_ASA = "aircraft/sardine_advanced_single_aisle_FLOPS.csv"

# CONFIG
driver_type = "IPOPT"


### RUN AVIARY
prob = av.AviaryProblem()

### Problem definition
prob.load_inputs(sardine_ASA, sardine_height_energy_phases)
prob.check_and_preprocess_inputs()
prob.build_model()

# optimizer and iteration limit are optional provided here
if driver_type == "IPOPT":
    prob.add_driver("IPOPT", max_iter=111)
    prob.driver.opt_settings["tol"] = 1.0e-3
    prob.driver.opt_settings["constr_viol_tol"] = 1e-4
    prob.driver.opt_settings["acceptable_tol"] = 1e-2
    prob.driver.opt_settings["acceptable_constr_viol_tol"] = 1e-3
    prob.driver.opt_settings["nlp_scaling_method"] = "gradient-based"
if driver_type == "SLSQP":
    prob.add_driver("SLSQP", max_iter=111)

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
