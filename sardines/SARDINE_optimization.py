import time
import ipdb
from copy import deepcopy

import aviary.api as av
import dymos as dm
import matplotlib.pyplot as plt
import numpy as np
import openmdao.api as om
import polars as pl
from missions.parametric_phase_infos import define_phase_info
from missions.sardine_phase_info import phase_info as sardine_height_energy_phases
from missions.two_dof_default import phase_info as two_dof_phase_info
# from missions.height_energy_test import phase_info as he_test
from missions.height_energy_test_SAR import phase_info as he_test_SAR
from rich import print
from itertools import product

from aviary.interface.methods_for_level2 import _load_off_design

# GASP models
small_single_aisle_GASP = "aircraft/small_single_aisle_GASP.csv"
sardine_turboprop_GASP = "aircraft/sardine_turboprop_GASP.csv"

# FLOPS models
base_ASA = "aircraft/advanced_single_aisle_FLOPS.csv"
sardine_ASA = "aircraft/sardine_advanced_single_aisle_FLOPS.csv"

# CONFIG
DRIVER_TYPE = "IPOPT"
MAX_ITER = 66


def main():
    # phase_info = optimization_run(sardine_height_energy_phases)

    # misc_cargo = np.arange(2000, 6000, 2000)
    # misc_mass = np.arange(80_000, 100_000, 10000)
    # misc_range = np.arange(1_000, 1_400, 200)
    cruise_alts = [20_000, 25_000, 30_000]
    cruise_alts = cruise_alts[::-1]
    cruise_machs = [0.5, 0.6, 0.7]
    # payloads = np.arange(0, 4_000, 2000)
    payloads = [
        0,
        5_000,
        10_000,
    ]

    iter_product = product(cruise_machs, cruise_alts, payloads)
    outputs = []
    for index, (cruise_mach, cruise_alt, payload) in enumerate(iter_product):
        # ipdb.set_trace()
        modified_he_test = modify_phase_info(he_test_SAR, cruise_alt, cruise_mach)
        print(f"###\nRunning cruise altitude: [bold blue]{cruise_alt}[/] ft")
        print(f"###\nRunning payload: [bold blue]{payload}[/] lb")
        print(f"###\nRunning cruise mach: [bold blue]{cruise_mach}[/]")

        fuel_burn, final_mass, design_mass, flown_range, payload_total = (
            optimization_run(phase_info=modified_he_test, payload=payload)
        )
        output = {
            "run_id": index,
            "cruise_alt": cruise_alt,
            "design_mass": design_mass,
            "fuel_burn": fuel_burn,
            "final_mass": final_mass,
            "flown_range": flown_range,
            "payload_total": payload_total,
            "cruise_mach": cruise_mach,
        }
        outputs.append(output)

    print(outputs)
    pl.dataframe(outputs).to_csv("sardine_sensitivity_basic.csv")

    # fallout_mission_runs(phase_info)


def modify_phase_info(phase_info, cruise_alt, cruise_mach):
    modified_shep = deepcopy(he_test_SAR)
    # modified_shep["pre_mission"]["optimize_mass"] = False
    # modified_shep["post_mission"]["constrain_range"] = True

    # TODO: include variation of cruise phase durations?


    modified_shep["climb_1"]["user_options"]["altitude_final"] = (
        cruise_alt,
        "ft",
    )
    modified_shep["climb_1"]["user_options"]["altitude_bounds"] = (
        (0, cruise_alt + 5000),
        "ft",
    )
    modified_shep["climb_1"]["user_options"]["mach_final"] = (cruise_mach, "unitless")

    modified_shep["cruise_1"]["user_options"]["altitude_optimize"] = True
    modified_shep["cruise_1"]["user_options"]["altitude_initial"] = (
        cruise_alt,
        "ft",
    )
    modified_shep["cruise_1"]["user_options"]["mach_initial"] = (cruise_mach, "unitless")
    modified_shep["cruise_1"]["user_options"]["mach_final"] = (cruise_mach, "unitless")
    modified_shep["cruise_1"]["user_options"]["mach_optimize"] = True
    modified_shep["cruise_1"]["user_options"]["mach_polynomial_order"] = 1
    modified_shep["cruise_1"]["user_options"]["mach_bounds"] = (
        (cruise_mach - 0.2, cruise_mach + 0.2),
        "unitless",
    )
    modified_shep["cruise_1"]["user_options"]["altitude_final"] = (
        cruise_alt,
        "ft",
    )
    modified_shep["cruise_1"]["user_options"]["altitude_bounds"] = (
        (cruise_alt - 5000, cruise_alt + 5000),
        "ft",
    )

    modified_shep["descent_1"]["user_options"]["mach_initial"] = (
        cruise_mach,
        "unitless",
    )
    modified_shep["descent_1"]["user_options"]["altitude_initial"] = (
        cruise_alt,
        "ft",
    )
    modified_shep["descent_1"]["user_options"]["altitude_bounds"] = (
        (0, cruise_alt + 5000),
        "ft",
    )
    return modified_shep


def strip_phase_info(phase_info, remove_altitudes=False, remove_mach=False):
    modified_phase_info = deepcopy(phase_info)
    if remove_altitudes:
        for phase, config in modified_phase_info.items():
            if "user_options" not in config.keys():
                continue
            else:
                if "mach_final" in config["user_options"]:
                    del config["user_options"]["altitude_final"]
                if "mach_initial" in config["user_options"]:
                    del config["user_options"]["altitude_initial"]
                if "mach_bounds" in config["user_options"]:
                    del config["user_options"]["altitude_bounds"]

    if remove_mach:
        for phase, config in modified_phase_info.items():
            if "user_options" not in config.keys():
                continue
            else:
                if "mach_final" in config["user_options"]:
                    del config["user_options"]["mach_final"]
                if "mach_initial" in config["user_options"]:
                    del config["user_options"]["mach_initial"]
                if "mach_bounds" in config["user_options"]:
                    del config["user_options"]["mach_bounds"]
    return modified_phase_info


### RUN AVIARY
def optimization_run(
    phase_info,
    payload,
    optimization_mode="range",
    driver_type=DRIVER_TYPE,
    remove_altitudes=False,
    remove_mach=False,
):
    prob = av.AviaryProblem()

    # optimizer and iteration limit are optional provided here
    if driver_type == "IPOPT":
        prob.add_driver("IPOPT", max_iter=MAX_ITER, verbosity=2)
        prob.driver.opt_settings["tol"] = 1.0e-3
        prob.driver.opt_settings["constr_viol_tol"] = 1e-3
        prob.driver.opt_settings["acceptable_tol"] = 1e-2
        prob.driver.opt_settings["acceptable_constr_viol_tol"] = 1e-3
        prob.driver.opt_settings["nlp_scaling_method"] = "gradient-based"
        prob.driver.opt_settings["hessian_approximation"] = "limited-memory"
    if driver_type == "SLSQP":
        prob.add_driver("SLSQP", max_iter=MAX_ITER)

    ### Problem definition
    # prob.load_inputs(sardine_ASA, sardine_height_energy_phases)
    prob.load_inputs(sardine_ASA, phase_info)
    prob.check_and_preprocess_inputs()
    prob.build_model()

    prob.add_design_variables()
    prob.aviary_inputs.set_val(
        av.Aircraft.CrewPayload.TOTAL_PAYLOAD_MASS,
        payload,
        units="lb",
    )
    prob.add_design_var_default(
        av.Aircraft.CrewPayload.TOTAL_PAYLOAD_MASS,
        lower=payload,
        upper=payload,
        units="lb",
        default_val=payload,
    )

    # prob.model.add_constraint(
    #     av.Mission.Constraints.EXCESS_FUEL_CAPACITY,
    #     lower=0,
    #     upper=0,
    #     ref=1000,
    #     units="lbm",
    #     alias=True,
    # )

    prob.add_objective(optimization_mode)
    prob.setup()

    prob.set_initial_guesses()

    start_time = time.time()
    prob.run_aviary_problem()
    end_time = time.time()
    print(f"Total run time: {end_time - start_time} seconds")

    # post mission reporting
    design_mass = prob.get_val(av.Mission.Design.GROSS_MASS, units="lb")[0]
    burned_fuel = prob.get_val(av.Mission.Summary.FUEL_BURNED, units="lb")[0]
    final_mass = prob.get_val(av.Mission.Summary.FINAL_MASS, units="lb")[0]
    flown_range = prob.get_val(av.Mission.Summary.RANGE, units="NM")[0]
    payload_total = prob.get_val(
        av.Aircraft.CrewPayload.TOTAL_PAYLOAD_MASS, units="lb"
    )[0]

    print(f"Design mass: {design_mass} lb")
    print(f"Fuel burned: {burned_fuel} lb")
    print(f"Final mass: {final_mass} lb")
    print(f"Flown range: {flown_range} nmi")
    print(f"Payload: {payload_total} lb")

    return burned_fuel, final_mass, design_mass, flown_range, payload_total


if __name__ == "__main__":
    main()
