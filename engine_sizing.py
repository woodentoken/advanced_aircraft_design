"""
This is an example of running constrained optimization in Aviary using the "level 2" API. It runs
the same aircraft and mission as the `level1_example.py` script, but it uses the AviaryProblem class
to set up the problem.

The same ".csv" file is used to define the aircraft, but wing area and engine scale factor are added
as design variables. Then, wing loading and thrust-to-weight ratio are constrained to arbitrary
limits. If this example is run without these constraints, wing area is increased to its upper bound
and engine scale factor is reduced to its lower bound.
"""

from aviary.models.missions.height_energy_default import phase_info

import aviary.api as av
Aircraft = av.Aircraft

# Suppress outputs
prob = av.AviaryProblem(verbosity=0)

# Load aircraft and options data from provided sources
prob.load_inputs('test_scripts/mod_advanced_single_aisle_FLOPS.csv', phase_info)

# # define the minimum option set for a turboprop
# options = av.AviaryValues()

# # top-level turboprop settings
# options.set_val(av.Settings.VERBOSITY, 0)  # quiet unneeded printouts
# options.set_val(Aircraft.Engine.FIXED_RPM, 13820, units='rpm')

# # EngineDeck minimum option set
# options.set_val(Aircraft.Engine.DATA_FILE, av.get_path('test_scripts/mod_advanced_single_aisle_FLOPS.csv'))

# # Gearbox model minimum option set
# options.set_val(Aircraft.Engine.Gearbox.GEAR_RATIO, 20.0, 'unitless') # changed from 13.55
# options.set_val(Aircraft.Engine.Gearbox.SHAFT_POWER_DESIGN, 4465, 'hp')

# # Hamilton Standard propeller minimum option set
# options.set_val(Aircraft.Engine.Propeller.TIP_MACH_MAX, 1.0)
# options.set_val(Aircraft.Engine.Propeller.NUM_BLADES, val=8, units='unitless') # changed from 4
# options.set_val(Aircraft.Engine.Propeller.COMPUTE_INSTALLATION_LOSS, True)

prob.check_and_preprocess_inputs()

prob.add_pre_mission_systems()

prob.add_phases()

prob.add_post_mission_systems()

prob.link_phases()

# Optimizer and iteration limit are optional provided here
prob.add_driver('IPOPT', max_iter=30)

# Add the default design variables needed to size the aircraft
prob.add_design_variables()

# Add wing area and engine scaling as additional design variables
#prob.model.add_design_var(av.Aircraft.Engine.SCALE_FACTOR, lower=0.8, upper=1.2, ref=1)
prob.model.add_design_var(av.Aircraft.Engine.MASS_SCALER, lower=0.8, upper=1.5, ref=1.15)
prob.model.add_design_var(av.Aircraft.Wing.AREA, lower=1200, upper=1800, units='ft**2', ref=1400)
prob.model.add_design_var(av.Aircraft.Engine.WING_LOCATIONS, lower=0.1, upper=0.8, ref=0.3)
#prob.model.add_design_var(av.Aircraft.Engine.Propeller.ACTIVITY_FACTOR, lower=100, upper=200, ref=167)
#prob.model.add_design_var(av.Aircraft.Engine.MASS, lower=6000, upper=8000, ref=7000, units='lbm')


prob.add_objective('fuel_burned')

# Constrain wing loading and thrust-to-weight ratio
prob.model.add_constraint(av.Aircraft.Design.WING_LOADING, lower=70, units='lbf/ft**2')
prob.model.add_constraint(av.Aircraft.Design.THRUST_TO_WEIGHT_RATIO, lower=0.35)

prob.setup()

prob.run_aviary_problem(run_driver=True)

print(f'\nTakeoff Gross Weight = {prob.get_val(av.Mission.Summary.GROSS_MASS, units="lbm")} lbm')
print('\nDesign Variables\n---------------')
#print(f'Engine Scale Factor (started at 1) = {prob.get_val(av.Aircraft.Engine.SCALE_FACTOR)}')
print(f'Engine Mass Scaler (started at 1.15) = {prob.get_val(av.Aircraft.Engine.MASS_SCALER)}')
print(f'Engine Wing Location (started at 0.3) = {prob.get_val(av.Aircraft.Engine.WING_LOCATIONS)}')
print(f'Engine Mass (started at 7000) = {prob.get_val(av.Aircraft.Engine.MASS)}')
print(f'Wing Area (started at 1370) = {prob.get_val(av.Aircraft.Wing.AREA, units="ft**2")} ft^2')
#print(f'Num blades (started at 6)) = {prob.get_val(av.Aircraft.Engine.Propeller.ACTIVITY_FACTOR)}')
print('\nConstraints\n-----------')
print(f'Wing Loading = {prob.get_val(av.Aircraft.Design.WING_LOADING, units="lbf/ft**2")} lbf/ft^2')
print(f'Thrust/Weight Ratio = {prob.get_val(av.Aircraft.Design.THRUST_TO_WEIGHT_RATIO)}')
print(prob.get_val(av.Mission.Summary.FUEL_BURNED, units='lb'))
