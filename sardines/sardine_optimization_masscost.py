import aviary.api as av
import openmdao.api as om
from copy import deepcopy
import time

from material_mix import MaterialMixMassCost

aircraft_data = "aircraft/advanced_single_aisle_FLOPS.csv"

optimizer = "IPOPT"
restart_filename = None
max_iter = 100
phase_info = deepcopy(av.default_height_energy_phase_info)
prob = av.AviaryProblem()
prob.load_inputs(aircraft_data, phase_info)
prob.check_and_preprocess_inputs()
prob.build_model()
model = prob.model

# Default mass_scaler's
fus0 = model.aviary_inputs.get_item("aircraft:fuselage:mass_scaler")[0]
wing0 = model.aviary_inputs.get_item("aircraft:wing:mass_scaler")[0]
ht0 = model.aviary_inputs.get_item("aircraft:horizontal_tail:mass_scaler")[0]
vt0 = model.aviary_inputs.get_item("aircraft:vertical_tail:mass_scaler")[0]

# Material mix component
model.add_subsystem(
    "material_mix",
    MaterialMixMassCost(
        fus_mass0=fus0,
        wing_mass0=wing0,
        ht_mass0=ht0,
        vt_mass0=vt0,
    ),
    promotes_inputs=["x_al", "x_ts", "x_2035"],
    promotes_outputs=[
        "mass_factor",
        "cost_factor",
        "sum_fractions",
        "fuselage_mass_scaler",
        "wing_mass_scaler",
        "horizontal_tail_mass_scaler",
        "vertical_tail_mass_scaler",
    ],
)

model.connect("fuselage_mass_scaler", "aircraft:fuselage:mass_scaler")
model.connect("wing_mass_scaler", "aircraft:wing:mass_scaler")
model.connect("horizontal_tail_mass_scaler", "aircraft:horizontal_tail:mass_scaler")
model.connect("vertical_tail_mass_scaler", "aircraft:vertical_tail:mass_scaler")

prob.add_design_variables()

# Material percentages between 0 and 1
model.add_design_var("x_al", lower=0.0, upper=1.0)
model.add_design_var("x_ts", lower=0.0, upper=1.0)
model.add_design_var("x_2035", lower=0.0, upper=1.0)

# Fractions sum to 1
model.add_constraint("sum_fractions", equals=1.0)

# Cost base line (100% Aluminum): 1.0 + 1.0 = 2.0
MIN_MATERIAL_COST = 3.0 # User Defined, must >= 2.0
MAX_MATERIAL_COST = 3.5 # User defined, must >= MIN_MATERIAL_COST & <=3.5
model.add_constraint("cost_factor", lower = MIN_MATERIAL_COST, upper=MAX_MATERIAL_COST)


prob.add_driver(optimizer, max_iter=max_iter)
prob.driver.opt_settings["tol"] = 1.0e-4
prob.add_objective("fuel_burned")

prob.setup()
prob.set_initial_guesses()

start_time = time.time()
prob.run_aviary_problem(restart_filename=restart_filename)
end_time = time.time()
print(f"Total run time: {end_time - start_time:.1f} s")

x_al = prob.get_val("x_al")[0]
x_ts = prob.get_val("x_ts")[0]
x_2035 = prob.get_val("x_2035")[0]
mass_factor = prob.get_val("mass_factor")[0]
cost_factor = prob.get_val("cost_factor")[0]

print("\n=== Optimal material mix ===")
print(f"Aluminum fraction = {x_al:.3f}")
print(f"Thermoset CFRP fraction = {x_ts:.3f}")
print(f"2035 FRP fraction = {x_2035:.3f}")
print(f"Material mass factor = {mass_factor:.3f}") # Between 0.5 & 1.0
print(f"Material cost factor = {cost_factor:.3f}") # Between MIN_MATERIAL_COST & MAX_MATERIAL_COST

print("\nStructural mass_scalers (applied to Aviary):")
print("Fuselage mass_scaler =", prob.get_val("aircraft:fuselage:mass_scaler")[0])
print("Wing mass_scaler =", prob.get_val("aircraft:wing:mass_scaler")[0])
print("Horizontal tail mass_scaler =", prob.get_val("aircraft:horizontal_tail:mass_scaler")[0])
print("Vertical tail mass_scaler =", prob.get_val("aircraft:vertical_tail:mass_scaler")[0])

burned_fuel = prob.get_val(av.Mission.Summary.FUEL_BURNED, units="lb")[0]
print(f"\nTotal fuel burned = {burned_fuel:.3f} lb")