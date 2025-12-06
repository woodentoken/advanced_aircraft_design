import time
import ipdb
from copy import deepcopy

import aviary.api as av
import dymos as dm
import matplotlib.pyplot as plt
import numpy as np
import openmdao.api as om
import polars as pl
from missions.sardine_phase_info import generate_phase_info as generate_SAR_profile
from missions.basic_sardine_phase_info import (
    generate_phase_info as generate_basic_SAR_profile,
)
from missions.sensitivity_height_energy import phase_info as sensitivity_he
from missions.default_height_energy import phase_info as default_he
from rich import print
from itertools import product

# FLOPS models
base_ASA = "aircraft/baseline_ASA_10_crew.csv"
sardine_ASA = "aircraft/sardine_ASA_10_crew.csv"

# CONFIG
DRIVER_TYPE = "IPOPT"
MAX_ITER = 66


def main(run_baseline=True, run_optimized=True, run_sensitivity=True, payload=0):
    if run_baseline:
        print("[bold blue]Running basic analysis...[/]")
        basic_summary = run_analysis(
            aircraft=base_ASA,
            phase_info=generate_basic_SAR_profile(
                altitude_optimize=False,
                general_mach_optimize=False,
                cruise_mach_optimize=False,
            ),
            optimization_mode="fuel_burned",
            payload=payload,
        )

    if run_optimized:
        print("[bold green]Running optimized analysis...[/]")
        optimized_summary = run_analysis(
            aircraft=sardine_ASA,
            phase_info=generate_SAR_profile(
                altitude_optimize=True,
                general_mach_optimize=False,
                cruise_mach_optimize=False,
            ),
            optimization_mode="fuel_burned",
            payload=payload,
        )

    if run_sensitivity:
        print("[bold purple]Running sensitivity analysis...[/]")
        sensitivity_analysis(phase_info=sensitivity_he)


def sensitivity_analysis(phase_info=sensitivity_he):
    # sensitivity analysis over cruise altitude, cruise mach, and payload
    # will run a grid of cases and output results to a csv file

    def modify_phase_info(phase_info, cruise_alt, cruise_mach):
        modified_phase_info = deepcopy(phase_info)

        # TODO: include variation of cruise phase durations?

        # CLIMB 1
        modified_phase_info["climb_1"]["user_options"]["altitude_final"] = (
            cruise_alt,
            "ft",
        )
        modified_phase_info["climb_1"]["user_options"]["altitude_bounds"] = (
            (0, cruise_alt + 5000),
            "ft",
        )
        modified_phase_info["climb_1"]["user_options"]["mach_final"] = (
            cruise_mach,
            "unitless",
        )

        # CRUISE 1
        modified_phase_info["cruise_1"]["user_options"]["altitude_optimize"] = True
        modified_phase_info["cruise_1"]["user_options"]["altitude_initial"] = (
            cruise_alt,
            "ft",
        )
        modified_phase_info["cruise_1"]["user_options"]["mach_initial"] = (
            cruise_mach,
            "unitless",
        )
        modified_phase_info["cruise_1"]["user_options"]["mach_final"] = (
            cruise_mach,
            "unitless",
        )
        modified_phase_info["cruise_1"]["user_options"]["mach_optimize"] = True
        modified_phase_info["cruise_1"]["user_options"]["mach_polynomial_order"] = 1
        modified_phase_info["cruise_1"]["user_options"]["mach_bounds"] = (
            (cruise_mach - 0.2, cruise_mach + 0.2),
            "unitless",
        )
        modified_phase_info["cruise_1"]["user_options"]["altitude_final"] = (
            cruise_alt,
            "ft",
        )
        modified_phase_info["cruise_1"]["user_options"]["altitude_bounds"] = (
            (cruise_alt - 5000, cruise_alt + 5000),
            "ft",
        )

        # DESCENT 1
        modified_phase_info["descent_1"]["user_options"]["mach_initial"] = (
            cruise_mach,
            "unitless",
        )
        modified_phase_info["descent_1"]["user_options"]["altitude_initial"] = (
            cruise_alt,
            "ft",
        )
        modified_phase_info["descent_1"]["user_options"]["altitude_bounds"] = (
            (0, cruise_alt + 5000),
            "ft",
        )
        return modified_phase_info

    cruise_alts = [20_000, 25_000, 30_000]
    cruise_alts = cruise_alts[::-1]  # reverse for nicer output order
    cruise_machs = [0.5, 0.6, 0.7]
    payloads = [
        0,
        5_000,
        10_000,
    ]

    iter_product = product(cruise_machs, cruise_alts, payloads)

    outputs = []
    for index, (cruise_mach, cruise_alt, payload) in enumerate(iter_product):
        modified_phase_info = modify_phase_info(phase_info, cruise_alt, cruise_mach)
        print(f"###\nRunning cruise mach: [bold blue]{cruise_mach}[/]")
        print(f"###\nRunning cruise altitude: [bold blue]{cruise_alt}[/] ft")
        print(f"###\nRunning payload: [bold blue]{payload}[/] lb")

        fuel_burn, final_mass, design_mass, flown_range, payload_total = run_analysis(
            phase_info=modified_phase_info, payload=payload, optimization_mode="range"
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


### RUN AVIARY
def run_analysis(
    phase_info,
    aircraft,
    optimization_mode,
    payload=0,
    remove_altitudes=False,
    remove_mach=False,
):
    # main function to run an Aviary problem with given phase info and aircraft model
    prob = av.AviaryProblem()

    # optionally remove altitude and/or mach from phase info
    if remove_altitudes or remove_mach:
        phase_info = strip_phase_info(
            phase_info,
            remove_altitudes=remove_altitudes,
            remove_mach=remove_mach,
        )

    ### Problem definition
    prob.load_inputs(aircraft, phase_info)

    # configure problem with payload and optimization mode and run boilerplate code
    prob = configure_problem(prob, payload)

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

    summary = {
        "design_mass": design_mass,
        "burned_fuel": burned_fuel,
        "final_mass": final_mass,
        "flown_range": flown_range,
        "payload_total": payload_total,
    }

    return summary


def configure_problem(
    prob, payload, driver_type=DRIVER_TYPE, optimization_mode="fuel_burned"
):
    # Configure the OpenMDAO problem with driver, design variables, objectives, etc.
    # most of this is boilerplate code for Aviary problems

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

    prob.check_and_preprocess_inputs()
    prob.build_model()

    prob.add_design_variables()

    if payload:
        # the most reliable way to set a fixed payload is to set the value and then fix it as a design variable
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

    return prob


def strip_phase_info(
    phase_info, remove_altitudes=False, remove_mach=False, remove_bounds=False
):
    # convenience function to remove altitude and/or mach from phase info, which should let the optimizer decide these values
    modified_phase_info = deepcopy(phase_info)
    if remove_altitudes:
        for phase, config in modified_phase_info.items():
            if "user_options" not in config.keys():
                continue
            else:
                if "altitude_final" in config["user_options"]:
                    del config["user_options"]["altitude_final"]
                if "altitude_initial" in config["user_options"]:
                    del config["user_options"]["altitude_initial"]
                if "altitude_bounds" in config["user_options"] and remove_bounds:
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
                if "mach_bounds" in config["user_options"] and remove_bounds:
                    del config["user_options"]["mach_bounds"]
    return modified_phase_info


if __name__ == "__main__":
    main(run_baseline=True, run_optimized=False, run_sensitivity=False, payload=7000)
