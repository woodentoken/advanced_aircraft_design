import time

import aviary.api as av
import dymos as dm
import ipdb
import openmdao.api as om
from aviary.core.pre_mission_group import PreMissionGroup
from aviary.mission.flops_based.phases.energy_phase import EnergyPhase
from aviary.models.missions.height_energy_default import phase_info
from aviary.utils.aviary_values import AviaryValues
from aviary.variable_info.enums import Verbosity
from aviary.variable_info.functions import setup_model_options, setup_trajectory_params
from aviary.variable_info.variable_meta_data import _MetaData as BaseMetaData
from aviary.variable_info.variables import Aircraft, Dynamic, Mission
from icecream import ic

from missions.loiter_phase import phase_info as loiter_phase_info
from missions.parametric_phase_infos import define_phase_info
from missions.outputted_phase_info import phase_info as designed_he_phase_info
from two_dof_default import phase_info as two_dof_phase_info

# this is the mission file
parametric_phase_infos = define_phase_info()

prob = av.AviaryProblem()

small_single_aisle_GASP = "aircraft/small_single_aisle_GASP.csv"
sardine_turboprop_GASP = "aircraft/sardine_turboprop_GASP.csv"
advanced_single_aisle_FLOPS = "aircraft/advanced_single_aisle_FLOPS.csv"

# aviary_inputs, something = av.create_vehicle(csv_path)
# working combos
# prob.load_inputs(
#     "models/aircraft/advanced_single_aisle/advanced_single_aisle_FLOPS.csv"
#     loiter_phase_info,
# )

# prob.load_inputs(
#     small_single_aisle_GASP,
#     parametric_phase_infos["two_dof_phase_info"],
# )

prob.load_inputs(
    advanced_single_aisle_FLOPS,
    designed_he_phase_info,
)

# aviary_inputs.set_val(Mission.Summary.RANGE, 1906.0, units="NM")
prob.check_and_preprocess_inputs()
# prob.add_pre_mission_systems()
# prob.add_phases()
# prob.add_post_mission_systems()

prob.build_model()

# optimizer and iteration limit are optional provided here
prob.add_driver("IPOPT", max_iter=100)
prob.driver.opt_settings["tol"] = 1.0e-4


prob.add_design_variables()
prob.add_objective()
prob.setup()
prob.set_initial_guesses()

prob.verbosity = Verbosity.VERBOSE


start_time = time.time()
prob.run_aviary_problem()
# (prob_fallout_max_fuel_plus_payload, prob_fallout_ferry) = prob.run_payload_range(
#     verbosity=2
# )
end_time = time.time()
print(f"Total run time: {end_time - start_time} seconds")
