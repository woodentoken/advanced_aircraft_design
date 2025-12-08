"""Run the a mission with a simple external component that computes aircraft lift and drag."""

from copy import deepcopy
import time

import aviary.api as av
import dymos as dm
import openmdao.api as om
from ExternalAero.external_aero_builder import ExternalAeroBuilder
from missions.sardine_phase_info import phase_info as sardine_height_energy_phases

phase_info = deepcopy(sardine_height_energy_phases)
sardine_ASA = "C:\\Users\\tadco\\Desktop\\advanced_aircraft_design\\sardines\\aircraft\\sardine_advanced_single_aisle_FLOPS.csv"

# # Just do cruise in this example.
# phase_info.pop('climb')
# phase_info.pop('descent')

# Add custom aero.
# TODO: This API for replacing aero will be changed an upcoming release.
phase_info['cruise']['external_subsystems'] = [ExternalAeroBuilder()]

# Disable internal aero
# TODO: This API for replacing aero will be changed an upcoming release.
phase_info['cruise']['subsystem_options']['core_aerodynamics'] = {
    'method': 'external',
}

# Start cruise at t=0.
del phase_info['cruise']['user_options']['time_initial_bounds']
phase_info['cruise']['user_options']['time_initial'] = (0.0, 'min')


if __name__ == '__main__':
    prob = av.AviaryProblem()

    # Load aircraft and options data from user
    # Allow for user overrides here
    prob.load_inputs(sardine_ASA, phase_info)


    prob.check_and_preprocess_inputs()

    prob.build_model()

    # Note, SLSQP has trouble here.
    prob.add_driver('IPOPT')

    prob.add_design_variables()

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
    print('done')
