"""Builder for a simple drag calculation that replaces Aviary's calculation."""

import aviary.api as av
from ovl_lift_drag import OVLAeroGroup
from aviary.subsystems.subsystem_builder_base import SubsystemBuilderBase
from aviary.variable_info.variables import Aircraft, Dynamic
from aviary.variable_info.variable_meta_data import _MetaData


class ExternalAeroBuilder(SubsystemBuilderBase):
    """
    Prototype of a subsystem that overrides an aviary internally computed var.

    It also provides a method to build OpenMDAO systems for the pre-mission and mission computations of the subsystem.

    Attributes
    ----------
    name : str ('simple_aero')
        object label
    """

    def __init__(self, name='external_aero', altitude=None, mach=None, angle_of_attack=None):
        super().__init__(name)
        self.altitude = altitude
        self.mach = mach
        self.angle_of_attack = angle_of_attack

    def build_mission(self, num_nodes, aviary_inputs, **kwargs):
        """
        Build an OpenMDAO system for the mission computations of the subsystem.

        Returns
        -------
        mission_sys : openmdao.core.System
            An OpenMDAO system containing all computations that need to happen
            during the mission. This includes time-dependent states that are
            being integrated as well as any other variables that vary during
            the mission.
        """
        aero_group = OVLAeroGroup(
            num_nodes=num_nodes,
        )
        return aero_group

    def mission_inputs(self, **kwargs):
        promotes = [
                Dynamic.Atmosphere.DYNAMIC_PRESSURE,
                Dynamic.Atmosphere.MACH,
                Dynamic.Vehicle.ANGLE_OF_ATTACK,
                Dynamic.Mission.ALTITUDE,
                'aircraft:*',
                'mission:*',
            ],
        return promotes

    def mission_outputs(self, **kwargs):
        promotes = [
            Dynamic.Vehicle.DRAG,
            Dynamic.Vehicle.LIFT,
        ]
        return promotes

    def get_parameters(self, aviary_inputs=None, phase_info=None):
        """
        Return a dictionary of fixed values for the subsystem.

        Optional, used if subsystems have fixed values.

        Used in the phase builders (e.g. cruise_phase.py) when other parameters are added to the phase.

        This is distinct from `get_design_vars` in a nuanced way. Design variables
        are variables that are optimized by the problem that are not at the phase level.
        An example would be something that occurs in the pre-mission level of the problem.
        Parameters are fixed values that are held constant throughout a phase, but if
        `opt=True`, they are able to change during the optimization.

        Parameters
        ----------
        phase_info : dict
            The phase_info subdict for this phase.

        Returns
        -------
        fixed_values : dict
            A dictionary where the keys are the names of the fixed variables
            and the values are dictionaries with the following keys:

            - 'value': float or array
                The fixed value for the variable.
            - 'units': str
                The units for the fixed value (optional).
            - any additional keyword arguments required by OpenMDAO for the fixed
              variable.
        """
        params = {}
        for var in COMPUTED_CORE_INPUTS:
            meta = _MetaData[var]

            val = meta['default_value']
            if val is None:
                val = 0.0  # _unspecified
            units = meta['units']

            if var in aviary_inputs:
                try:
                    val = aviary_inputs.get_val(var, units)
                except TypeError:
                    val = aviary_inputs.get_val(var)

            params[var] = {'val': val, 'units': units, 'static_target': True}
        return params

    def needs_mission_solver(self, aviary_inputs):
        """
        Return True if the mission subsystem needs to be in the solver loop in mission, otherwise
        return False. Aviary will only place it in the solver loop when True. The default is
        True.
        """
        return True

COMPUTED_CORE_INPUTS = [
        Aircraft.Wing.AREA,
        Aircraft.Wing.WETTED_AREA,
        Aircraft.Wing.WETTED_AREA_SCALER,
        Aircraft.Wing.CHORD_PER_SEMISPAN_DIST,
        Aircraft.Wing.DIHEDRAL,
        Aircraft.Wing.HEIGHT,
        Aircraft.Wing.SPAN,
        Aircraft.Wing.SWEEP, 
        Aircraft.Wing.TAPER_RATIO, 
        Aircraft.Wing.THICKNESS_TO_CHORD_ROOT, 
        Aircraft.Wing.MAX_CAMBER_AT_70_SEMISPAN,
        
        Aircraft.VerticalTail.AREA,
        Aircraft.VerticalTail.ASPECT_RATIO,
        Aircraft.VerticalTail.SWEEP,
        Aircraft.VerticalTail.TAPER_RATIO,
        Aircraft.VerticalTail.THICKNESS_TO_CHORD,
        
        Aircraft.HorizontalTail.AREA,
        Aircraft.HorizontalTail.ASPECT_RATIO,
        Aircraft.HorizontalTail.SWEEP,
        Aircraft.HorizontalTail.TAPER_RATIO,
        Aircraft.HorizontalTail.THICKNESS_TO_CHORD,
        
        Aircraft.Fuselage.LENGTH, 
        Aircraft.Fuselage.MAX_HEIGHT, 
        Aircraft.Fuselage.MAX_WIDTH, 
        
        # Aircraft Flow Conditions
        Dynamic.Atmosphere.MACH,
        Dynamic.Vehicle.ANGLE_OF_ATTACK,
        Dynamic.Mission.ALTITUDE,
        Dynamic.Atmosphere.DYNAMIC_PRESSURE,
]