import csv
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

from material_mix import MaterialMixMassCost
from missions.archive.default_height_energy import phase_info as default_he
from missions.basic import (
    generate_phase_info as generate_basic_SAR_profile,
)
from missions.optimization import (
    generate_phase_info as generate_SAR_profile,
)
from missions.sensitivity import phase_info as sensitivity_profile


# FLOPS models
base_ASA = "aircraft/baseline_ASA_10_crew.csv"
sardine_ASA = "aircraft/sardine_ASA_10_crew.csv"


# DETERMINE WHICH OPTIMIZATIONS TO RUN
OPTIMIZATIONS = ["geometry", "propulsion", "mass"]

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
        sensitivity_analysis(sensitivity_profile)


class WingAreaFromAR(om.ExplicitComponent):
    """
    Compute wing area from fixed span and AR:
        area = span0**2 / AR
    """

    def initialize(self):
        self.options.declare("span0", types=float, desc="Fixed wing span [ft]")

    def setup(self):
        self.add_input("AR", val=10.0)  # aspect ratio
        self.add_output("wing_area", val=900.0)  # wing area [ft**2]

        self.declare_partials("wing_area", "AR")

    def compute(self, inputs, outputs):
        AR = inputs["AR"]
        span0 = self.options["span0"]
        outputs["wing_area"] = span0 * span0 / AR

    def compute_partials(self, inputs, partials):
        AR = inputs["AR"]
        span0 = self.options["span0"]
        partials["wing_area", "AR"] = -span0 * span0 / (AR**2)


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

    # post mission reporting
    # propulsion variables
    wing_locations = prob.get_val(av.Aircraft.Engine.WING_LOCATIONS)[0]
    mass_scaler = prob.get_val(av.Aircraft.Engine.MASS_SCALER)[0]
    scale_factor = prob.get_val(av.Aircraft.Engine.SCALE_FACTOR)[0]
    engine_thrust = prob.get_val(av.Aircraft.Engine.SCALED_SLS_THRUST, units="lbf")[0]
    thrust_to_weight = prob.get_val(av.Aircraft.Design.THRUST_TO_WEIGHT_RATIO)[0]
    wing_loading = prob.get_val(av.Aircraft.Design.WING_LOADING, units="lbf/ft**2")
    burned_fuel = prob.get_val(av.Mission.Summary.FUEL_BURNED, units="lb")[0]

    # Propulsion print outs
    print(f"Engine wing location :{wing_locations}")
    print(f"Engine mass scaler :{mass_scaler}")
    print(f"Engine scaler factor :{scale_factor}")
    print(f"Engine thrust :{engine_thrust}")
    print(f"Aircraft T/W :{thrust_to_weight}")
    print(f"Wing Loading = {wing_loading} lbf/ft^2")
    print(f"Fuel burned: {burned_fuel} lb")

    AR_opt = prob.get_val("aircraft:wing:aspect_ratio")[0]
    span = prob.get_val("aircraft:wing:span", units="ft")[0]
    area = prob.get_val("aircraft:wing:area", units="ft**2")[0]
    taper = prob.get_val("aircraft:wing:taper_ratio")[0]
    sweep = prob.get_val("aircraft:wing:sweep", units="deg")[0]
    tc = prob.get_val("aircraft:wing:thickness_to_chord")[0]
    fuselage_len = prob.get_val("aircraft:fuselage:length", units="ft")[0]

    c_ref = area / span
    c_root = 2.0 * area / (span * (1.0 + taper))  # trapezoid assumption

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

    if "mass" in OPTIMIZATIONS:
        x_al = prob.get_val("x_al")[0]
        x_ts = prob.get_val("x_ts")[0]
        x_2035 = prob.get_val("x_2035")[0]
        mass_factor = prob.get_val("mass_factor")[0]
        cost_factor = prob.get_val("cost_factor")[0]

        print("\n=== Optimal material mix ===")
        print(f"Aluminum fraction = {x_al:.3f}")
        print(f"Thermoset CFRP fraction = {x_ts:.3f}")
        print(f"2035 FRP fraction = {x_2035:.3f}")
        print(f"Material mass factor = {mass_factor:.3f}")  # Between 0.5 & 1.0
        print(
            f"Material cost factor = {cost_factor:.3f}"
        )  # Between MIN_MATERIAL_COST & MAX_MATERIAL_COST

        print("\nStructural mass_scalers (applied to Aviary):")
        print(
            "Fuselage mass_scaler =", prob.get_val("aircraft:fuselage:mass_scaler")[0]
        )
        print("Wing mass_scaler =", prob.get_val("aircraft:wing:mass_scaler")[0])
        print(
            "Horizontal tail mass_scaler =",
            prob.get_val("aircraft:horizontal_tail:mass_scaler")[0],
        )
        print(
            "Vertical tail mass_scaler =",
            prob.get_val("aircraft:vertical_tail:mass_scaler")[0],
        )

    return summary


def configure_problem(
    prob,
    payload,
    driver_type=DRIVER_TYPE,
    optimization_mode="fuel_burned",
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
    prob.add_design_variables()

    if "mass" in OPTIMIZATIONS:
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
        model.connect(
            "horizontal_tail_mass_scaler", "aircraft:horizontal_tail:mass_scaler"
        )
        model.connect("vertical_tail_mass_scaler", "aircraft:vertical_tail:mass_scaler")

        # Material percentages between 0 and 1
        model.add_design_var("x_al", lower=0.0, upper=1.0)
        model.add_design_var("x_ts", lower=0.0, upper=1.0)
        model.add_design_var("x_2035", lower=0.0, upper=1.0)

        # Fractions sum to 1
        model.add_constraint("sum_fractions", equals=1.0)

        # Cost base line (100% Aluminum): 1.0 + 1.0 = 2.0
        MIN_MATERIAL_COST = 3.0  # User Defined, must >= 2.0
        MAX_MATERIAL_COST = 3.5  # User defined, must >= MIN_MATERIAL_COST & <=3.5
        model.add_constraint(
            "cost_factor", lower=MIN_MATERIAL_COST, upper=MAX_MATERIAL_COST
        )

    if "propulsion" in OPTIMIZATIONS:
        print("[bold green]Adding propulsion design variables...[/]")
        # Propulsion design variables
        prob.model.add_design_var(
            av.Aircraft.Engine.WING_LOCATIONS, lower=0.1, upper=0.8, ref=0.25
        )
        prob.model.add_design_var(av.Aircraft.Engine.MASS_SCALER, lower=0.8, upper=1)
        prob.model.add_design_var(
            av.Aircraft.Engine.SCALE_FACTOR, lower=0.25, upper=2.0, ref=1.0
        )

        # Add constraints
        # Constrain wing loading and thrust-to-weight ratio
        prob.model.add_constraint(
            av.Aircraft.Design.WING_LOADING, lower=60, units="lbf/ft**2"
        )
        prob.model.add_constraint(av.Aircraft.Engine.SCALED_SLS_THRUST, upper=22000)
        prob.model.add_constraint(av.Aircraft.Design.THRUST_TO_WEIGHT_RATIO, upper=0.7)

    if "geometry" in OPTIMIZATIONS:
        print("[bold green]Adding geometry design variables...[/]")
        feselage_length = prob.model.aviary_inputs.get_item("aircraft:fuselage:length")[
            0
        ]
        wing_thickness_to_chord = prob.model.aviary_inputs.get_item(
            "aircraft:wing:thickness_to_chord"
        )[0]
        wing_aspect_ratio = prob.model.aviary_inputs.get_item(
            "aircraft:wing:aspect_ratio"
        )[0]
        wing_sweep = prob.model.aviary_inputs.get_item("aircraft:wing:sweep")[0]
        wing_taper_ratio = prob.model.aviary_inputs.get_item(
            "aircraft:wing:taper_ratio"
        )[0]
        wing_span = prob.model.aviary_inputs.get_item("aircraft:wing:span")[0]

        model.add_subsystem(
            "wing_area_from_AR",
            WingAreaFromAR(span0=wing_span),
            promotes_inputs=[("AR", "aircraft:wing:aspect_ratio")],
            promotes_outputs=["wing_area"],
        )
        model.connect("wing_area", "aircraft:wing:area")

        lower_bound = 0.8
        upper_bound = 1.4

        prob.model.add_design_var(
            "aircraft:fuselage:length",
            lower=lower_bound * feselage_length,
            upper=upper_bound * feselage_length,
            ref=feselage_length,
        )

        prob.model.add_design_var(
            "aircraft:wing:thickness_to_chord",
            lower=lower_bound * wing_thickness_to_chord,
            upper=upper_bound * wing_thickness_to_chord,
            ref=wing_thickness_to_chord,
        )

        prob.model.add_design_var(
            "aircraft:wing:aspect_ratio",
            lower=lower_bound * wing_aspect_ratio,
            upper=upper_bound * wing_aspect_ratio,
            ref=wing_aspect_ratio,
        )

        prob.model.add_design_var(
            "aircraft:wing:sweep",
            lower_bound * wing_sweep,
            upper_bound * wing_sweep,
            ref=wing_sweep,
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


def sensitivity_analysis(phase_info=sensitivity_profile):
    # sensitivity analysis over cruise altitude, cruise mach, and payload
    # will run a grid of cases and output results to a csv file

    def modify_phase_info(phase_info, cruise_alt, cruise_mach):
        modified_phase_info = deepcopy(phase_info)

        # TODO: include variation of cruise phase durations?

        # CLIMB 1
        for climb_key in ["climb_1", "climb_3"]:
            if climb_key not in modified_phase_info:
                continue
            #     # del modified_phase_info[climb_key]["user_options"]["time_duration_bounds"]
            #     modified_phase_info[climb_key]["user_options"]["altitude_final"] = (
            #         cruise_alt,
            #         "ft",
            #     )
            modified_phase_info[climb_key]["user_options"]["altitude_bounds"] = (
                (0, cruise_alt + 5000),
                "ft",
            )
            if climb_key == "climb_3":
                modified_phase_info[climb_key]["user_options"]["mach_final"] = (
                    cruise_mach,
                    "unitless",
                )
            if climb_key == "climb_1":
                modified_phase_info[climb_key]["user_options"]["mach_final"] = (
                    cruise_mach,
                    "unitless",
                )

        # # CRUISE 1
        for cruise_key in ["cruise_1", "cruise_3"]:
            if cruise_key not in modified_phase_info:
                continue
            # del modified_phase_info[cruise_key]["user_options"]["target_distance"]
            #     modified_phase_info[cruise_key]["user_options"]["mach_optimize"] = True
            #     modified_phase_info[cruise_key]["user_options"]["altitude_optimize"] = True
            #     # del modified_phase_info[cruise_key]["user_options"]["time_duration_bounds"]

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
            #     modified_phase_info[cruise_key]["user_options"]["mach_polynomial_order"] = 1
            modified_phase_info[cruise_key]["user_options"]["mach_bounds"] = (
                (cruise_mach - 0.1, cruise_mach + 0.1),
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

        # # DESCENT 1
        for descent_key in ["descent_1", "descent_3"]:
            if descent_key not in modified_phase_info:
                continue
            #     # del modified_phase_info[descent_key]["user_options"]["time_duration_bounds"]
            #     modified_phase_info[descent_key]["user_options"]["mach_initial"] = (
            #         cruise_mach,
            #         "unitless",
            #     )
            #     modified_phase_info[descent_key]["user_options"]["altitude_initial"] = (
            #         cruise_alt,
            #         "ft",
            #     )
            if descent_key == "descent_3":
                pass
                # modified_phase_info[descent_key]["user_options"]["mach_initial"] = (
                #     cruise_mach,
                #     "unitless",
                # )
            if descent_key == "descent_1":
                modified_phase_info[descent_key]["user_options"]["mach_initial"] = (
                    cruise_mach,
                    "unitless",
                )
            modified_phase_info[descent_key]["user_options"]["altitude_bounds"] = (
                (0, cruise_alt + 5000),
                "ft",
            )
        return modified_phase_info

    cruise_alts = [20_000, 25_000, 30_000]
    # cruise_alts = cruise_alts[::-1]  # reverse for nicer output order
    cruise_machs = [0.5, 0.6, 0.7]
    payloads = [
        5_000,
        10_000,
        15_000,
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


# def strip_phase_info(
#     phase_info, remove_altitudes=False, remove_mach=False, remove_bounds=False
# ):
#     # convenience function to remove altitude and/or mach from phase info, which should let the optimizer decide these values
#     modified_phase_info = deepcopy(phase_info)
#     if remove_altitudes:
#         for phase, config in modified_phase_info.items():
#             if "user_options" not in config.keys():
#                 continue
#             else:
#                 if "altitude_final" in config["user_options"]:
#                     del config["user_options"]["altitude_final"]
#                 if "altitude_initial" in config["user_options"]:
#                     del config["user_options"]["altitude_initial"]
#                 if "altitude_bounds" in config["user_options"] and remove_bounds:
#                     del config["user_options"]["altitude_bounds"]

#     if remove_mach:
#         for phase, config in modified_phase_info.items():
#             if "user_options" not in config.keys():
#                 continue
#             else:
#                 if "mach_final" in config["user_options"]:
#                     del config["user_options"]["mach_final"]
#                 if "mach_initial" in config["user_options"]:
#                     del config["user_options"]["mach_initial"]
#                 if "mach_bounds" in config["user_options"] and remove_bounds:
#                     del config["user_options"]["mach_bounds"]
#     return modified_phase_info


if __name__ == "__main__":
    main()
