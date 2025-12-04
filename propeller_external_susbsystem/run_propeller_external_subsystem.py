"""Example mission using the a detailed battery model."""

from aviary.api import default_height_energy_phase_info as phase_info
from propeller_builder import PropellerBuilder
from propeller_variable_meta_data import ExtendedMetaData
from aviary.interface.methods_for_level2 import AviaryProblem
from aviary.utils.functions import get_aviary_resource_path

propeller_builder = PropellerBuilder()

# add the battery model to each mission phase, as well as pre-mission for sizing
phase_info['pre_mission']['external_subsystems'] = [propeller_builder]
phase_info['climb']['external_subsystems'] = [propeller_builder]
phase_info['cruise']['external_subsystems'] = [propeller_builder]
phase_info['descent']['external_subsystems'] = [propeller_builder]

if __name__ == '__main__':
    prob = AviaryProblem()

    # Load aircraft and options data from user
    # Allow for user overrides here
    prob.load_inputs('test_scripts/modified_aircraft_for_bench_FwFm.csv', phase_info, meta_data=ExtendedMetaData)

    prob.check_and_preprocess_inputs()

    prob.build_model()

    prob.add_driver('IPOPT')

    prob.add_design_variables()

    prob.add_objective('fuel_burned')
    # prob.model.add_objective(
    #     f'traj.climb.states:{Dynamic.Battery.STATE_OF_CHARGE}', index=-1, ref=-1)

    prob.setup()

    prob.run_aviary_problem()
