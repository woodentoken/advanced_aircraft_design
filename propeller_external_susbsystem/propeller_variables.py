from aviary.variable_info.variables import Aircraft as av_Aircraft

AviaryAircraft = av_Aircraft


class Aircraft(AviaryAircraft):
    """Aircraft data hierarchy for propeller subsystem."""

    # cell = single cell, battery = one case plus multiple cells

    class Engine(AviaryAircraft.Engine):
        MASS_SCALER = 'aircraft:engine:mass_scaler'
        MASS_SPECIFIC = 'aircraft:engine:mass_specific'
        NUM_ENGINES = 'aircraft:engine:num_engines'
        POD_MASS_SCALER = 'aircraft:engine:pod_mass_scaler'
        PYLON_FACTOR = 'aircraft:engine:pylon_factor'
        REFERENCE_DIAMETER = 'aircraft:engine:reference_diameter'
        REFERENCE_SLS_THRUST = 'aircraft:engine:reference_sls_thrust'
        RPM_DESIGN = 'aircraft:engine:rpm_design'
        FIXED_RPM = 'aircraft:engine:fixed_rpm'
        SCALED_SLS_THRUST = 'aircraft:engine:scaled_sls_thrust'
        WING_LOCATIONS = 'aircraft:engine:wing_locations'

        class Propeller:
            NUM_BLADES = 'aircraft:engine:propeller:num_blades'
            ACTIVITY_FACTOR = 'aircraft:engine:propeller:activity_factor'
            DIAMETER = 'aircraft:engine:propeller:diameter'
            INTEGRATED_LIFT_COEFFICIENT = 'aircraft:engine:propeller:integrated_lift_coefficient'
            TIP_SPEED_MAX = 'aircraft:engine:propeller:tip_speed_max'
        
        class Gearbox:
            GEAR_RATIO = 'aircraft:engine:gearbox:gear_ratio'
            EFFICIENCY = 'aircraft:engine:gearbox:efficiency'
            SHAFT_POWER_DESIGN = 'aircraft:engine:gearbox:shaft_power_design'
            SPECIFIC_TORQUE = 'aircraft:engine:gearbox:specific_torque'
