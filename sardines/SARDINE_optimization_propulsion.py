import time

import aviary.api as av
import dymos as dm
import openmdao.api as om

Aircraft = av.Aircraft

from missions.parametric_phase_infos import define_phase_info
from missions.sardine_phase_info import phase_info as sardine_height_energy_phases
from missions.two_dof_default import phase_info as two_dof_phase_info

prob = av.AviaryProblem()
options = av.AviaryValues()

# GASP models
small_single_aisle_GASP = "aircraft/small_single_aisle_GASP.csv"
sardine_turboprop_GASP = "test_scripts/sardines/aircraft/sardine_turboprop_GASP.csv"

# FLOPS models
base_ASA = "aircraft/advanced_single_aisle_FLOPS.csv"
sardine_ASA = "test_scripts/sardines/aircraft/sardine_advanced_single_aisle_FLOPS.csv"

### Problem definition
prob.load_inputs(sardine_ASA, sardine_height_energy_phases)

prob.check_and_preprocess_inputs()

prob.build_model()

# optimizer and iteration limit are optional provided here
prob.add_driver("IPOPT", max_iter=100)
prob.driver.opt_settings["tol"] = 1.0e-4
prob.driver.opt_settings["constr_viol_tol"] = 1e-5
prob.driver.opt_settings["acceptable_tol"] = 1e-3
prob.driver.opt_settings["acceptable_constr_viol_tol"] = 1e-4
prob.driver.opt_settings["nlp_scaling_method"] = "gradient-based"

prob.add_design_variables()

# Setting values for carpet plots
# options.set_val(av.Aircraft.Wing.ASPECT_RATIO, 6)

# Propulsion design variables
prob.model.add_design_var(
    av.Aircraft.Engine.WING_LOCATIONS, lower=0.1, upper=0.8, ref=0.25
)
prob.model.add_design_var(
    av.Aircraft.Engine.MASS_SCALER, lower=0.8, upper=1
)
prob.model.add_design_var(
    av.Aircraft.Engine.SCALE_FACTOR, lower=0.25, upper=2.0, ref=1.0
)
# prob.model.add_design_var(
#     av.Aircraft.Engine.SCALED_SLS_THRUST, lower=15000, upper=25000, ref=20000
# )

# Add constraints
# Constrain wing loading and thrust-to-weight ratio
# prob.model.add_constraint(av.Aircraft.Design.WING_LOADING, lower = 60, units='lbf/ft**2')
prob.model.add_constraint(av.Aircraft.Engine.SCALED_SLS_THRUST, upper = 22000)
prob.model.add_constraint(av.Aircraft.Design.THRUST_TO_WEIGHT_RATIO, upper = 0.7)

prob.add_objective('fuel_burned')
prob.setup()
prob.set_initial_guesses()

start_time = time.time()
prob.run_aviary_problem()
end_time = time.time()
print(f"Total run time: {end_time - start_time} seconds")

# post mission reporting
burned_fuel = prob.get_val(av.Mission.Summary.FUEL_BURNED, units="lb")[0]
mtow = prob.get_val(av.Mission.Summary.GROSS_MASS, units = "lb")[0]
final_mass = prob.get_val(av.Mission.Summary.FINAL_MASS, units="lb")[0]
wing_locations = prob.get_val(av.Aircraft.Engine.WING_LOCATIONS)
mass_scaler = prob.get_val(av.Aircraft.Engine.MASS_SCALER)
scale_factor = prob.get_val(av.Aircraft.Engine.SCALE_FACTOR)
aspect_ratio = prob.get_val(av.Aircraft.Wing.ASPECT_RATIO)
print(f"Fuel burned: {burned_fuel} lb")
print(f"MTOW: {mtow} lb")
print(f"Final mass: {final_mass} lb")
print(f"Engine wing location :{wing_locations}")
print(f"Engine mass scaler :{mass_scaler}")
print(f"Engine scaler factor :{scale_factor}")
print("------------------------------------")
print('\nConstraints\n-----------')
print(f'Wing Loading = {prob.get_val(av.Aircraft.Design.WING_LOADING, units="lbf/ft**2")} lbf/ft^2')
print(f'Thrust/Weight Ratio = {prob.get_val(av.Aircraft.Design.THRUST_TO_WEIGHT_RATIO)}')


