from aviary.variable_info.variables import Mission

# defaults for height energy based phases

alt_optimize = True
mach_optimize = False
general_mach_optimize = False
general_mach_poly = 1
cruise_mach_poly = 3

phase_info = {
    "pre_mission": {"include_takeoff": False, "optimize_mass": False},
    "climb_1": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "num_segments": 5,
            "order": 3,
            "mach_optimize": general_mach_optimize,
            "mach_initial": (0.2, "unitless"),
            "mach_final": (0.72, "unitless"),
            "mach_bounds": ((0.18, 0.74), "unitless"),
            "mach_polynomial_order": general_mach_poly,
            "altitude_optimize": alt_optimize,
            "altitude_polynomial_order": 3,
            "altitude_initial": (0.0, "ft"),
            # "altitude_final": (32500.0, "ft"),
            "altitude_bounds": ((0.0, 35000.0), "ft"),
            "throttle_enforcement": "path_constraint",
            "time_initial": (0.0, "min"),
            "time_initial_bounds": ((0.0, 0.0), "min"),
            "time_duration_bounds": ((5.0, 30.0), "min"),
            "no_descent": True,
        },
        "initial_guesses": {"time": ([0, 8], "min")},
    },
    "cruise_1": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "num_segments": 8,
            "order": 3,
            "mach_optimize": mach_optimize,
            "mach_initial": (0.72, "unitless"),
            "mach_final": (0.72, "unitless"),
            "mach_bounds": ((0.7, 0.84), "unitless"),
            "mach_polynomial_order": cruise_mach_poly,
            "altitude_optimize": alt_optimize,
            "altitude_polynomial_order": 3,
            # "altitude_initial": (32500.0, "ft"),
            # "altitude_final": (36000.0, "ft"),
            # "altitude_bounds": ((30000.0, 45000.0), "ft"),
            "throttle_enforcement": "boundary_constraint",
            # "time_initial_bounds": ((20.0, 105.0), "min"),
            "time_duration_bounds": ((100, 800), "min"),
        },
        "initial_guesses": {"time": ([10, 400], "min")},
    },
    "descent_1": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "num_segments": 5,
            "order": 3,
            "mach_optimize": general_mach_optimize,
            "mach_initial": (0.72, "unitless"),
            "mach_final": (0.3, "unitless"),
            "mach_bounds": ((0.19, 0.84), "unitless"),
            "mach_polynomial_order": general_mach_poly,
            "altitude_polynomial_order": 3,
            "altitude_optimize": alt_optimize,
            # "altitude_initial": (36000.0, "ft"),
            "altitude_final": (15000.0, "ft"),
            "altitude_bounds": ((0.0, 35000.0), "ft"),
            "throttle_enforcement": "path_constraint",
            # "time_initial_bounds": ((166.5, 600.0), "min"),
            "time_duration_bounds": ((5.0, 40.0), "min"),
            "no_climb": True,
        },
        "initial_guesses": {"time": ([420, 20], "min")},
    },
    "cruise_2": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "num_segments": 8,
            "order": 3,
            "mach_optimize": mach_optimize,
            "mach_initial": (0.3, "unitless"),
            "mach_final": (0.3, "unitless"),
            "mach_bounds": ((0.2, 0.4), "unitless"),
            "mach_polynomial_order": cruise_mach_poly,
            "altitude_optimize": alt_optimize,
            "altitude_polynomial_order": 3,
            "altitude_initial": (15000.0, "ft"),
            # "altitude_final": (36000.0, "ft"),
            "altitude_bounds": ((10000.0, 20000.0), "ft"),
            "throttle_enforcement": "boundary_constraint",
            # "time_initial_bounds": ((222.0, 805.0), "min"),
            # "time_duration_bounds": ((21.5, 600), "min"),
            "time_duration": (180.0, "min"),
        },
        "initial_guesses": {"time": ([530, 180], "min")},
    },
    "descent_3": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "num_segments": 5,
            "order": 3,
            "mach_optimize": general_mach_optimize,
            "mach_initial": (0.3, "unitless"),
            "mach_final": (0.3, "unitless"),
            "mach_bounds": ((0.19, 0.84), "unitless"),
            "mach_polynomial_order": general_mach_poly,
            "altitude_optimize": alt_optimize,
            "altitude_polynomial_order": 3,
            # "altitude_initial": (36000.0, "ft"),
            "altitude_final": (1500.0, "ft"),
            "altitude_bounds": ((0.0, 20000.0), "ft"),
            "throttle_enforcement": "path_constraint",
            # "time_initial_bounds": ((400.5, 600.0), "min"),
            "time_duration_bounds": ((10.0, 40.0), "min"),
            "no_climb": True,
        },
        "initial_guesses": {"time": ([750, 20], "min")},
    },
    "post_mission": {
        "include_landing": False,
        # "constrain_range": True,
        # "target_range": (4000.0, "nmi"),
    },
}


def phase_info_parameterization(phase_info, post_mission_info, aviary_inputs):
    """
    Modify the values in the phase_info dictionary to accommodate different values
    for the following mission design inputs: cruise altitude, cruise Mach number,
    cruise range, design gross mass.

    Parameters
    ----------
    phase_info : dict
        Dictionary of phase settings for a mission profile
    post_mission_info : dict
        Dictionary of phase settings for a post mission profile
    aviary_inputs : <AviaryValues>
        Object containing values and units for all aviary inputs and options

    Returns
    -------
    dict
        Modified phase_info and post_mission_info that have been changed to match
        the new mission parameters
    """
    alt_cruise = aviary_inputs.get_val(Mission.Design.CRUISE_ALTITUDE, units="ft")
    mach_cruise = aviary_inputs.get_val(Mission.Summary.CRUISE_MACH)

    # Range
    old_range_cruise, range_units = post_mission_info["target_range"]
    range_cruise = aviary_inputs.get_val(Mission.Design.RANGE, units=range_units)
    if range_cruise != old_range_cruise:
        new_val = post_mission_info["target_range"][0] * range_cruise / old_range_cruise
        post_mission_info["target_range"] = (new_val, range_units)

    # Altitude
    old_alt_cruise = 32000.0
    if alt_cruise != old_alt_cruise:
        new_alt = (alt_cruise, "ft")

        climb = phase_info["climb"]
        user = climb["user_options"]
        if "altitude_final" in user and user["altitude_final"][0] is not None:
            user["altitude_final"] = new_alt

        if "initial_guesses" in climb and "altitude" in climb["initial_guesses"]:
            if climb["initial_guesses"]["altitude"][0] is not None:
                init = climb["initial_guesses"]["altitude"][0][0]
                climb["initial_guesses"]["altitude"] = ([init, alt_cruise], "ft")

        cruise = phase_info["cruise"]
        user = cruise["user_options"]
        if "altitude_initial" in user and user["altitude_initial"][0] is not None:
            user["altitude_initial"] = new_alt

        if "altitude_final" in user and user["altitude_final"][0] is not None:
            user["altitude_final"] = new_alt

        if "initial_guesses" in cruise and "altitude" in cruise["initial_guesses"]:
            if cruise["initial_guesses"]["altitude"][0] is not None:
                cruise["initial_guesses"]["altitude"] = ([alt_cruise, alt_cruise], "ft")

        descent = phase_info["descent"]
        user = descent["user_options"]
        if "altitude_initial" in user and user["altitude_initial"][0] is not None:
            user["altitude_initial"] = new_alt

        if "initial_guesses" in descent and "altitude" in descent["initial_guesses"]:
            if descent["initial_guesses"]["altitude"][0] is not None:
                final = climb["initial_guesses"]["altitude"][0][0]
                descent["initial_guesses"]["altitude"] = ([alt_cruise, final], "ft")

    # Mach
    old_mach_cruise = 0.72
    if mach_cruise != old_mach_cruise:
        new_mach = (mach_cruise, "unitless")

        climb = phase_info["climb"]
        user = climb["user_options"]
        if "mach_final" in user and user["mach_final"][0] is not None:
            user["mach_final"] = new_mach

        if "initial_guesses" in climb and "mach" in climb["initial_guesses"]:
            if climb["initial_guesses"]["mach"][0] is not None:
                init = climb["initial_guesses"]["mach"][0][0]
                climb["initial_guesses"]["mach"] = ([init, mach_cruise], "unitless")

        cruise = phase_info["cruise"]
        user = cruise["user_options"]
        if "mach_initial" in user and user["mach_initial"][0] is not None:
            user["mach_initial"] = new_mach

        if "mach_final" in user and user["mach_final"][0] is not None:
            user["mach_final"] = new_mach

        if "initial_guesses" in cruise and "mach" in cruise["initial_guesses"]:
            if cruise["initial_guesses"]["mach"][0] is not None:
                cruise["initial_guesses"]["mach"] = (
                    [mach_cruise, mach_cruise],
                    "unitless",
                )

        descent = phase_info["descent"]
        user = descent["user_options"]
        if "mach_initial" in user and user["mach_initial"][0] is not None:
            user["mach_initial"] = new_mach

        if "initial_guesses" in descent and "mach" in descent["initial_guesses"]:
            if descent["initial_guesses"]["mach"][0] is not None:
                final = climb["initial_guesses"]["mach"][0][0]
                descent["initial_guesses"]["mach"] = ([mach_cruise, final], "unitless")

    return phase_info, post_mission_info
