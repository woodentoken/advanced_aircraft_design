import openmdao.api as om
import aviary.api as av
from propeller_variables import Aircraft

class PropellerBuilder(av.SubsystemBuilderBase):
    """
    External subsystem builder for BWB fuel-tank sizing.
    - Runs in pre-mission (sizing) to compute capacity and tank structural mass.
    - Uses core Aviary wing area + mission fuel as inputs.
    - Provides capacity mass as an output you can constrain against.
    """
    def __init__(self, name='propeller_model'):
        super().__init__(name=name)
    def build_pre_mission(self, aviary_inputs):
        g = om.Group()
        g.add_subsystem(
            'propeller_model',
            PropellerBuilder(),
            promotes_inputs=[
                # From Aviary:
                # Wing area S_ref (you might change to the exact tag you use)
                ('ref_wing_area', av.Aircraft.Wing.AREA),
                ('scale_factor', av.Aircraft.Engine.SCALE_FACTOR),
                ('num_engines', av.Aircraft.Engine.NUM_ENGINES),
                # Variables to set for propeller design:
                ('diameter', Aircraft.Engine.Propeller.DIAMETER),
                ('gear_ratio',Aircraft.Engine.Gearbox.GEAR_RATIO),
            ],
            promotes_outputs=[
                ('num_blades', Aircraft.Engine.Propeller.NUM_BLADES),
                ('efficiency', Aircraft.Engine.Gearbox.EFFICIENCY)
            ],
        )
        return g