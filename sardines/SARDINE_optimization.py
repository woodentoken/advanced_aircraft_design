import time
from copy import deepcopy
from itertools import product
import csv

import aviary.api as av
import dymos as dm
import ipdb
import matplotlib.pyplot as plt
import numpy as np
import openmdao.api as om
import polars as pl
from rich import print

from missions.basic import (
    generate_phase_info as generate_basic_SAR_profile,
)
from missions.archive.default_height_energy import phase_info as default_he
from missions.optimization import (
    generate_phase_info as generate_SAR_profile,
)
from missions.sensitivity import phase_info as sensitivity_he


class WingAreaFromAR(om.ExplicitComponent):
    """
    Compute wing area from fixed span and AR:
        area = span0**2 / AR
    """

    def initialize(self):
        self.options.declare('span0', types=float, desc='Fixed wing span [ft]')

    def setup(self):
        self.add_input('AR', val=10.0)          # aspect ratio
        self.add_output('wing_area', val=900.0)  # wing area [ft**2]

        self.declare_partials('wing_area', 'AR')

    def compute(self, inputs, outputs):
        AR = inputs['AR']
        span0 = self.options['span0']
        outputs['wing_area'] = span0 * span0 / AR

    def compute_partials(self, inputs, partials):
        AR = inputs['AR']
        span0 = self.options['span0']
        partials['wing_area', 'AR'] = - span0 * span0 / (AR**2)

# FLOPS models
base_ASA = "aircraft/baseline_ASA_10_crew.csv"
sardine_ASA = "aircraft/sardine_ASA_10_crew.csv"

# CONFIG
DRIVER_TYPE = "IPOPT"
MAX_ITER = 200


# change the defaults here to run different cases (you can run multiple cases in one go)
def main(
    run_ASA_unscaled=False,
    run_SAR_baseline=True,
    run_SAR_optimized=False,
    run_sensitivity=False,
    payload=6000,
):
    summaries = []
    if run_ASA_unscaled:
        print("[bold blue]Running analysis on unscaled ASA...[/]")
        unscaled_summary = run_analysis(
            aircraft=base_ASA,
            phase_info=generate_basic_SAR_profile(
                altitude_optimize=False,
                general_mach_optimize=False,
                cruise_mach_optimize=False,
            ),
            optimization_mode="fuel_burned",
            payload=payload,
        )
        unscaled_summary["case"] = "ASA'"
        summaries.append(unscaled_summary)

    if run_SAR_baseline:
        print("[bold red]Running analysis on scaled ASA (SAR baseline)...[/]")
        baseline_summary = run_analysis(
            aircraft=sardine_ASA,
            phase_info=generate_basic_SAR_profile(
                altitude_optimize=False,
                general_mach_optimize=False,
                cruise_mach_optimize=False,
            ),
            optimization_mode="fuel_burned",
            payload=payload,
        )
        baseline_summary["case"] = "SAR"
        summaries.append(baseline_summary)

    if run_SAR_optimized:
        print(
            "[bold green]Running analysis on scaled ASA with optimizations(SAR optimized)...[/]"
        )
        optimized_summary = run_analysis(
            aircraft=sardine_ASA,
            phase_info=generate_SAR_profile(
                altitude_optimize=True,
                general_mach_optimize=False,
                cruise_mach_optimize=True,
            ),
            optimization_mode="fuel_burned",
            payload=payload,
        )
        optimized_summary["case"] = "SAR optimized"
        summaries.append(optimized_summary)

    summary_dataframe = pl.DataFrame(summaries)
    print(summary_dataframe)

    # print all the summaries if all three runs were done
    if np.all([run_ASA_unscaled, run_SAR_baseline, run_SAR_optimized]):
        unscaled_burn = summary_dataframe.filter(pl.col("case") == "ASA'")[
            "burned_fuel"
        ][0]
        baseline_burn = summary_dataframe.filter(pl.col("case") == "SAR")[
            "burned_fuel"
        ][0]

        summary_dataframe = summary_dataframe.with_columns(
            (pl.col("burned_fuel") / baseline_burn).alias("fuel_burn_ratio_SAR"),
            (pl.col("burned_fuel") / unscaled_burn).alias("fuel_burn_ratio_ASA'"),
        )

        summary_dataframe.write_csv("sardine_optimization_summary.csv")

    if run_sensitivity:
        print("[bold purple]Running sensitivity analysis...[/]")
        sensitivity_analysis(sensitivity_he)


def sensitivity_analysis(phase_info=sensitivity_he):
    # sensitivity analysis over cruise altitude, cruise mach, and payload
    # will run a grid of cases and output results to a csv file

    def modify_phase_info(phase_info, cruise_alt, cruise_mach):
        modified_phase_info = deepcopy(phase_info)

        # TODO: include variation of cruise phase durations?

        # CLIMB 1
        for climb_key in ["climb_1", "climb_3"]:
            if climb_key not in modified_phase_info:
                continue
            # del modified_phase_info[climb_key]["user_options"]["time_duration_bounds"]
            modified_phase_info[climb_key]["user_options"]["altitude_final"] = (
                cruise_alt,
                "ft",
            )
            modified_phase_info[climb_key]["user_options"]["altitude_bounds"] = (
                (0, cruise_alt + 5000),
                "ft",
            )
            modified_phase_info[climb_key]["user_options"]["mach_final"] = (
                cruise_mach,
                "unitless",
            )

        # CRUISE 1
        for cruise_key in ["cruise_1", "cruise_3"]:
            if cruise_key not in modified_phase_info:
                continue
            # del modified_phase_info[cruise_key]["user_options"]["target_distance"]
            modified_phase_info[cruise_key]["user_options"]["mach_optimize"] = True
            modified_phase_info[cruise_key]["user_options"]["altitude_optimize"] = True
            # del modified_phase_info[cruise_key]["user_options"]["time_duration_bounds"]

            modified_phase_info[cruise_key]["user_options"]["altitude_initial"] = (
                cruise_alt,
                "ft",
            )
            modified_phase_info[cruise_key]["user_options"]["mach_initial"] = (
                cruise_mach,
                "unitless",
            )
            modified_phase_info[cruise_key]["user_options"]["mach_final"] = (
                cruise_mach,
                "unitless",
            )
            modified_phase_info[cruise_key]["user_options"]["mach_polynomial_order"] = 1
            modified_phase_info[cruise_key]["user_options"]["mach_bounds"] = (
                (cruise_mach - 0.2, cruise_mach + 0.2),
                "unitless",
            )
            modified_phase_info[cruise_key]["user_options"]["altitude_final"] = (
                cruise_alt,
                "ft",
            )
            modified_phase_info[cruise_key]["user_options"]["altitude_bounds"] = (
                (cruise_alt - 5000, cruise_alt + 5000),
                "ft",
            )

        # DESCENT 1
        for descent_key in ["descent_1"]:
            if descent_key not in modified_phase_info:
                continue
            # del modified_phase_info[descent_key]["user_options"]["time_duration_bounds"]
            modified_phase_info[descent_key]["user_options"]["mach_initial"] = (
                cruise_mach,
                "unitless",
            )
            modified_phase_info[descent_key]["user_options"]["altitude_initial"] = (
                cruise_alt,
                "ft",
            )
            modified_phase_info[descent_key]["user_options"]["altitude_bounds"] = (
                (0, cruise_alt + 5000),
                "ft",
            )
        return modified_phase_info

    cruise_alts = [20_000, 25_000, 30_000]
    cruise_alts = cruise_alts[::-1]  # reverse for nicer output order
    cruise_machs = [0.5, 0.6, 0.7]
    payloads = [
        6_000,
        12_000,
        18_000,
    ]

    iter_product = product(cruise_machs, cruise_alts, payloads)

    outputs = []
    for index, (cruise_mach, cruise_alt, payload) in enumerate(iter_product):
        modified_phase_info = modify_phase_info(phase_info, cruise_alt, cruise_mach)
        print(f"###\nRunning cruise mach: [bold blue]{cruise_mach}[/]")
        print(f"###\nRunning cruise altitude: [bold blue]{cruise_alt}[/] ft")
        print(f"###\nRunning payload: [bold blue]{payload}[/] lb")

        output = run_analysis(
            phase_info=modified_phase_info,
            payload=payload,
            optimization_mode="range",
            aircraft=sardine_ASA,
            mach_override=cruise_mach,
        )
        output["run_id"] = index
        output["cruise_alt"] = cruise_alt
        output["cruise_mach"] = cruise_mach
        outputs.append(output)

    print(outputs)
    pl.DataFrame(outputs).write_csv("sardine_sensitivity.csv")


### RUN AVIARY
def run_analysis(
    phase_info,
    aircraft,
    optimization_mode="fuel_burned",
    payload=0,
    remove_altitudes=False,
    remove_mach=False,
    mach_override=None,
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
    if mach_override is not None:
        prob.model.aviary_inputs.set_val(av.Mission.Summary.CRUISE_MACH, mach_override)

    # configure problem with payload and optimization mode and run boilerplate code
    prob = configure_problem(prob, payload, optimization_mode=optimization_mode)
    # prob.check_partials(method="cs", compact_print=True)

    start_time = time.time()
    prob.run_aviary_problem()
    end_time = time.time()
    print(f"Total run time: {end_time - start_time} seconds")

    # post mission reporting
    success = prob.result.success
    design_mass = prob.get_val(av.Mission.Design.GROSS_MASS, units="lb")[0]
    burned_fuel = prob.get_val(av.Mission.Summary.FUEL_BURNED, units="lb")[0]
    final_mass = prob.get_val(av.Mission.Summary.FINAL_MASS, units="lb")[0]
    flown_range = prob.get_val(av.Mission.Summary.RANGE, units="NM")[0]
    payload_total = prob.get_val(
        av.Aircraft.CrewPayload.TOTAL_PAYLOAD_MASS, units="lb"
    )[0]

    print(f"Mission success: {success}")
    print(f"Design mass: {design_mass} lb")
    print(f"Fuel burned: {burned_fuel} lb")
    print(f"Final mass: {final_mass} lb")
    print(f"Flown range: {flown_range} nmi")
    print(f"Payload: {payload_total} lb")

    summary = {
        "success": success,
        "design_mass": design_mass,
        "burned_fuel": burned_fuel,
        "final_mass": final_mass,
        "flown_range": flown_range,
        "payload_total": payload_total,
    }

    AR_opt = prob.get_val('aircraft:wing:aspect_ratio')[0]
    span   = prob.get_val('aircraft:wing:span',  units='ft')[0]
    area   = prob.get_val('aircraft:wing:area',  units='ft**2')[0]
    taper  = prob.get_val('aircraft:wing:taper_ratio')[0]
    sweep  = prob.get_val('aircraft:wing:sweep', units='deg')[0]
    tc     = prob.get_val('aircraft:wing:thickness_to_chord')[0]
    fuselage_len = prob.get_val('aircraft:fuselage:length', units='ft')[0]

    c_ref  = area / span
    c_root = 2.0 * area / (span * (1.0 + taper)) # trapezoid assumption

    print("\n=== Geometry summary for aero teammate ===")
    print(f"Fuselage Length           = {fuselage_len:.4f} ft")
    print(f"Reference area S_ref      = {area:.3f} ft^2")
    print(f"Reference span b_ref      = {span:.3f} ft")
    print(f"Reference chord c_ref     = {c_ref:.3f} ft")
    print(f"Root chord c_root         = {c_root:.3f} ft")
    print(f"Taper ratio lambda        = {taper:.4f}")
    print(f"Sweep                     = {sweep:.3f} deg")
    print(f"Aspect ratio AR           = {AR_opt:.4f}")
    print(f"Thickness-to-chord (mean) = {tc:.4f}")

    # if aircraft == sardine_ASA:
    #     csv_filename = "optimized_geometry_sardine_to_aero.csv"
    # elif aircraft == base_ASA:
    #     csv_filename = "optimized_geometry_asa.csv"
    # else:
    #     csv_filename = "optimized_geometry.csv"

    # with open(csv_filename, mode="w", newline="") as f:
    #     writer = csv.writer(f)

    #     writer.writerow(["Parameter", "Value", "Units"])

    #     writer.writerow(["Reference Area S_ref", f"{area:.6f}", "ft^2"])
    #     writer.writerow(["Reference Chord c_ref", f"{c_ref:.6f}", "ft"])
    #     writer.writerow(["Reference Span b_ref", f"{span:.6f}", "ft"])
    #     writer.writerow(["Root Chord c_root", f"{c_root:.6f}", "ft"])
    #     writer.writerow(["Taper Ratio lambda", f"{taper:.6f}", "-"])
    #     writer.writerow(["Sweep", f"{sweep:.6f}", "deg"])
    #     writer.writerow(["Aspect Ratio AR", f"{AR_opt:.6f}", "-"])

    # print(f"\nCSV saved to: {csv_filename}")

    return summary


def configure_problem(
    prob, payload, driver_type=DRIVER_TYPE, optimization_mode="fuel_burned"
):
    # Configure the OpenMDAO problem with driver, design variables, objectives, etc.
    # most of this is boilerplate code for Aviary problems

    # optimizer and iteration limit are optional provided here
    if driver_type == "IPOPT":
        prob.add_driver("IPOPT", max_iter=MAX_ITER, verbosity=2)
        prob.driver.opt_settings["tol"] = 1e-4
        prob.driver.opt_settings["constr_viol_tol"] = 1e-4
        prob.driver.opt_settings["acceptable_tol"] = 1e-3
        prob.driver.opt_settings["acceptable_constr_viol_tol"] = 1e-4
        prob.driver.opt_settings["nlp_scaling_method"] = "gradient-based"
        prob.driver.opt_settings["hessian_approximation"] = "limited-memory"
        prob.driver.opt_settings["output_file"] = "ipopt_out.txt"
        prob.driver.opt_settings["print_level"] = 5
        # prob.driver.opt_settings[""]
    if driver_type == "SLSQP":
        prob.add_driver("SLSQP", max_iter=MAX_ITER)

    prob.check_and_preprocess_inputs()
    prob.build_model()

    model = prob.model

    feselage_length = prob.model.aviary_inputs.get_item('aircraft:fuselage:length')[0]
    wing_thickness_to_chord = prob.model.aviary_inputs.get_item('aircraft:wing:thickness_to_chord')[0]
    wing_aspect_ratio = prob.model.aviary_inputs.get_item('aircraft:wing:aspect_ratio')[0]
    wing_sweep = prob.model.aviary_inputs.get_item('aircraft:wing:sweep')[0]
    wing_taper_ratio = prob.model.aviary_inputs.get_item('aircraft:wing:taper_ratio')[0]
    wing_span = prob.model.aviary_inputs.get_item('aircraft:wing:span')[0]

    model.add_subsystem(
        'wing_area_from_AR',
        WingAreaFromAR(span0=wing_span),
        promotes_inputs=[('AR', 'aircraft:wing:aspect_ratio')],
        promotes_outputs=['wing_area'],
    )
    model.connect('wing_area', 'aircraft:wing:area')

    lower_bound = 0.8
    upper_bound = 1.4


    prob.add_design_variables()

    prob.model.add_design_var(
        'aircraft:fuselage:length',
        lower= lower_bound * feselage_length,
        upper= upper_bound* feselage_length,
        ref = feselage_length
    )

    # prob.model.add_design_var(
    #     'aircraft:wing:thickness_to_chord',
    #     lower=lower_bound * wing_thickness_to_chord,
    #     upper=upper_bound * wing_thickness_to_chord,
    #     ref = wing_thickness_to_chord
    # )

    prob.model.add_design_var(
        'aircraft:wing:aspect_ratio',
        lower=lower_bound * wing_aspect_ratio,
        upper=upper_bound * wing_aspect_ratio,
        ref = wing_aspect_ratio
    )

    prob.model.add_design_var(
        'aircraft:wing:sweep',
        lower_bound * wing_sweep,
        upper_bound * wing_sweep,
        ref = wing_sweep
    )

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

    if optimization_mode == "range":
        # add a model for range
        prob.model.add_subsystem(
            "range_objective",
            om.ExecComp(
                "reg_objective = actual_range + ascent_duration/30.",
                reg_objective={"val": 0.0, "units": "unitless"},
                ascent_duration={"units": "s", "shape": 1},
                actual_range={"val": prob.model.target_range, "units": "NM"},
            ),
            promotes_inputs=[
                ("actual_range", av.Mission.Summary.RANGE),
                ("ascent_duration", av.Mission.Takeoff.ASCENT_DURATION),
            ],
            promotes_outputs=[("reg_objective", av.Mission.Objectives.RANGE)],
        )
        # add the custom objective to the problem
        prob.model.add_objective(av.Mission.Objectives.RANGE, ref=3500)
        print("Optimization mode: maximizing range")
        # use all your fuel to go as far as possible
        prob.model.add_constraint(
            av.Mission.Constraints.EXCESS_FUEL_CAPACITY,
            lower=0,
            upper=0,
            ref=2000,
            units="lbm",
        )

    elif optimization_mode == "fuel_burned":
        taxi_fuel_burn = 443  # lbm, estimate for fuel burned during taxi, this value comes from Balikrishnan's linear models
        # save at least 5% fuel for reserves
        prob.model.add_constraint(
            av.Mission.Constraints.EXCESS_FUEL_CAPACITY,
            lower=taxi_fuel_burn
            + (
                0.05  # 5% of capacity
                * prob.aviary_inputs.get_val(
                    av.Aircraft.Fuel.TOTAL_CAPACITY, units="lbm"
                )
            ),
            ref=2000,
            units="lbm",
        )
        prob.model.add_objective(av.Mission.Summary.FUEL_BURNED, ref=20000)

    else:
        prob.model.add_constraint(
            av.Mission.Constraints.EXCESS_FUEL_CAPACITY,
            lower=0,
            ref=2000,
            units="lbm",
        )
        prob.model.add_objective(av.Mission.Summary.FUEL_BURNED, ref=20000)

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
    main()
