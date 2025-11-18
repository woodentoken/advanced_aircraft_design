# Unspecified Hierarchy Variables
These aviary inputs are unspecified in aviary_inputs, and may be using default values defined in the Aviary metadata.

| Name | Value | Units | Description | Absolute Paths
| :- |  :- |  :- | :- | :- |
| **aircraft:canard:area** | [0.] | ft**2 | canard theoretical area | ['pre_mission.core_subsystems.core_geometry.canard.aircraft:canard:area', 'pre_mission.core_subsystems.core_geometry.other_characteristic_lengths.aircraft:canard:area', 'pre_mission.core_subsystems.core_mass.canard.aircraft:canard:area']|
| **aircraft:canard:aspect_ratio** | [0.] | unitless | canard theoretical aspect ratio | ['pre_mission.core_subsystems.core_geometry.other_characteristic_lengths.aircraft:canard:aspect_ratio']|
| **aircraft:canard:taper_ratio** | [0.] | unitless | canard theoretical taper ratio | ['pre_mission.core_subsystems.core_mass.canard.aircraft:canard:taper_ratio']|
| **aircraft:canard:thickness_to_chord** | [0.] | unitless | canard thickness-chord ratio | ['pre_mission.core_subsystems.core_geometry.canard.aircraft:canard:thickness_to_chord', 'pre_mission.core_subsystems.core_geometry.other_characteristic_lengths.aircraft:canard:thickness_to_chord']|
| **aircraft:canard:wetted_area_scaler** | [1.] | unitless | canard wetted area scaler | ['pre_mission.core_subsystems.core_geometry.canard.aircraft:canard:wetted_area_scaler']|
| **aircraft:design:external_subsystems_mass** | [0.] | lbm | total mass of all user-defined external subsystems | ['pre_mission.core_subsystems.core_mass.total_mass.system_equip_mass.aircraft:design:external_subsystems_mass']|
| **aircraft:engine:thrust_reversers_mass_scaler** | [0.] | unitless | scaler for mass of thrust reversers on engines. In FLOPS/LEAPS1 default to 0.0 | ['pre_mission.core_subsystems.core_mass.thrust_rev.aircraft:engine:thrust_reversers_mass_scaler']|
| **aircraft:fuel:density** | [6.7] | lbm/galUS | fuel density (jet fuel typical density of 6.7 lbm/galUS used in the calculation of wing_capacity(if wing_capacity is not input) and in the calculation of fuel system weight. | ['pre_mission.core_subsystems.core_mass.fuel_capacity_group.wing_fuel_capacity.aircraft:fuel:density', 'pre_mission.core_subsystems.core_mass.unusable_fuel.aircraft:fuel:density']|
| **aircraft:fuel:fuel_margin** | [0.] | unitless | percentage of excess fuel volume required, essentially the amount of fuel above the design point that there has to be volume to carry | ['post_mission.fuel_calc.fuel_margin']|
| **aircraft:fuel:wing_ref_capacity** | [0.] | lbm | reference fuel volume | ['pre_mission.core_subsystems.core_mass.fuel_capacity_group.wing_fuel_capacity.aircraft:fuel:wing_ref_capacity']|
| **aircraft:fuel:wing_ref_capacity_area** | [0.] | unitless | reference wing area for fuel capacity | ['pre_mission.core_subsystems.core_mass.fuel_capacity_group.wing_fuel_capacity.aircraft:fuel:wing_ref_capacity_area']|
| **aircraft:fuel:wing_ref_capacity_term_A** | [0.] | unitless | scaling factor A | ['pre_mission.core_subsystems.core_mass.fuel_capacity_group.wing_fuel_capacity.aircraft:fuel:wing_ref_capacity_term_A']|
| **aircraft:fuel:wing_ref_capacity_term_B** | [0.] | unitless | scaling factor B | ['pre_mission.core_subsystems.core_mass.fuel_capacity_group.wing_fuel_capacity.aircraft:fuel:wing_ref_capacity_term_B']|
| **aircraft:fuselage:wetted_area_scaler** | [1.] | unitless | fuselage wetted area scaler | ['pre_mission.core_subsystems.core_geometry.fuselage.aircraft:fuselage:wetted_area_scaler']|
| **aircraft:wing:bwb_aft_body_mass** | [0.] | lbm | wing mass breakdown term 4 | ['pre_mission.core_subsystems.core_mass.wing_group.wing_total.aircraft:wing:bwb_aft_body_mass']|
| **mission:summary:reserve_fuel_burned** | [0.] | lbm | fuel burned during reserve phases, this does not include fuel burned in regular phases | ['post_mission.reserve_fuel.reserve_fuel_burned']|
| **mission:takeoff:ascent_duration** | [0.] | s | duration of the ascent phase of takeoff | ['fuel_obj.ascent_duration', 'range_obj.ascent_duration']|

# Unspecified Local Variables
These local subsystem inputs are unconnected, and may be using default values specified in the component.

| Name | Value | Units | Absolute Paths
| :- |  :- |  :- | :- |
| **pre_mission.other_characteristic_lengths.prep_geom:_Names:CROOT** | [0.] | unitless | ['pre_mission.core_subsystems.core_geometry.other_characteristic_lengths.prep_geom:_Names:CROOT']|
| **reserve_fuel_frac_mass** | [0.] | lbm | ['post_mission.reserve_fuel.reserve_fuel_frac_mass']|
| **target_range** | [1906.] | nmi | ['range_constraint.target_range']|
| **traj.climb.rhs_all.vectorize_performance.electric_power_in_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | kW | ['traj.phases.climb.rhs_all.solver_sub.core_propulsion.vectorize_performance.electric_power_in_0']|
| **traj.climb.rhs_all.vectorize_performance.shaft_power_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | hp | ['traj.phases.climb.rhs_all.solver_sub.core_propulsion.vectorize_performance.shaft_power_0']|
| **traj.climb.rhs_all.vectorize_performance.shaft_power_max_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | hp | ['traj.phases.climb.rhs_all.solver_sub.core_propulsion.vectorize_performance.shaft_power_max_0']|
| **traj.climb.rhs_all.vectorize_performance.t4_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | degR | ['traj.phases.climb.rhs_all.solver_sub.core_propulsion.vectorize_performance.t4_0']|
| **traj.cruise.rhs_all.vectorize_performance.electric_power_in_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | kW | ['traj.phases.cruise.rhs_all.solver_sub.core_propulsion.vectorize_performance.electric_power_in_0']|
| **traj.cruise.rhs_all.vectorize_performance.shaft_power_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | hp | ['traj.phases.cruise.rhs_all.solver_sub.core_propulsion.vectorize_performance.shaft_power_0']|
| **traj.cruise.rhs_all.vectorize_performance.shaft_power_max_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | hp | ['traj.phases.cruise.rhs_all.solver_sub.core_propulsion.vectorize_performance.shaft_power_max_0']|
| **traj.cruise.rhs_all.vectorize_performance.t4_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | degR | ['traj.phases.cruise.rhs_all.solver_sub.core_propulsion.vectorize_performance.t4_0']|
| **traj.descent.rhs_all.vectorize_performance.electric_power_in_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | kW | ['traj.phases.descent.rhs_all.solver_sub.core_propulsion.vectorize_performance.electric_power_in_0']|
| **traj.descent.rhs_all.vectorize_performance.shaft_power_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | hp | ['traj.phases.descent.rhs_all.solver_sub.core_propulsion.vectorize_performance.shaft_power_0']|
| **traj.descent.rhs_all.vectorize_performance.shaft_power_max_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | hp | ['traj.phases.descent.rhs_all.solver_sub.core_propulsion.vectorize_performance.shaft_power_max_0']|
| **traj.descent.rhs_all.vectorize_performance.t4_0** | [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.] | degR | ['traj.phases.descent.rhs_all.solver_sub.core_propulsion.vectorize_performance.t4_0']|


