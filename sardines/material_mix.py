import openmdao.api as om

class MaterialMixMassCost(om.ExplicitComponent):
    """
    Compute effective structural mass and cost factors from a three-material mix,
    and map them to the four structural mass_scalers.

    Fractions:
        x_al: Aluminum alloys
        x_ts: Thermoset CFRP (e.g. carbon/epoxy)
        x_2035: Hypothetical 2035 FRP

    Factors (relative to aluminum = 1.0):
        Mass: [1.0, 0.7, 0.5]
        Manufacturing: [1.0, 1.9, 2.5]
        Maintenance: [1.0, 0.8, 1.0]
        Cost = manuf + maint = [2.0, 2.7, 3.5]
    """

    def initialize(self):
        # Baseline mass_scaler values for each structural group
        self.options.declare('fus_mass0', types=float)
        self.options.declare('wing_mass0', types=float)
        self.options.declare('ht_mass0', types=float)
        self.options.declare('vt_mass0', types=float)

    def setup(self):
        self.add_input('x_al', val=1.0)   # start all-aluminum
        self.add_input('x_ts', val=0.0)
        self.add_input('x_2035', val=0.0)

        self.add_output('mass_factor', val=1.0)
        self.add_output('cost_factor', val=2.0)
        self.add_output('sum_fractions', val=1.0)

        fus0 = self.options['fus_mass0']
        wing0 = self.options['wing_mass0']
        ht0 = self.options['ht_mass0']
        vt0 = self.options['vt_mass0']

        self.add_output('fuselage_mass_scaler', val=fus0)
        self.add_output('wing_mass_scaler', val=wing0)
        self.add_output('horizontal_tail_mass_scaler', val=ht0)
        self.add_output('vertical_tail_mass_scaler', val=vt0)

        self.declare_partials('*', '*')

    def compute(self, inputs, outputs):
        x_al = inputs['x_al']
        x_ts = inputs['x_ts']
        x_2035 = inputs['x_2035']

        m_al, m_ts, m_2035 = 1.0, 0.7, 0.5
        c_al, c_ts, c_2035 = 2.0, 2.7, 3.5

        mass_factor = x_al*m_al + x_ts*m_ts + x_2035*m_2035
        cost_factor = x_al*c_al + x_ts*c_ts + x_2035*c_2035
        sum_fracs = x_al + x_ts + x_2035

        outputs['mass_factor'] = mass_factor
        outputs['cost_factor'] = cost_factor
        outputs['sum_fractions'] = sum_fracs

        fus0 = self.options['fus_mass0']
        wing0 = self.options['wing_mass0']
        ht0 = self.options['ht_mass0']
        vt0 = self.options['vt_mass0']

        # Apply the same mass_factor to all four structural groups
        outputs['fuselage_mass_scaler'] = mass_factor * fus0
        outputs['wing_mass_scaler'] = mass_factor * wing0
        outputs['horizontal_tail_mass_scaler'] = mass_factor * ht0
        outputs['vertical_tail_mass_scaler'] = mass_factor * vt0

    def compute_partials(self, inputs, partials):
        x_al = inputs['x_al']
        x_ts = inputs['x_ts']
        x_2035 = inputs['x_2035']

        m_al, m_ts, m_2035 = 1.0, 0.7, 0.5
        c_al, c_ts, c_2035 = 2.0, 2.7, 3.5

        fus0 = self.options['fus_mass0']
        wing0 = self.options['wing_mass0']
        ht0 = self.options['ht_mass0']
        vt0 = self.options['vt_mass0']

        # d(mass_factor)/dx
        dmf_dx_al = m_al
        dmf_dx_ts = m_ts
        dmf_dx_2035 = m_2035

        # d(cost_factor)/dx
        dcf_dx_al = c_al
        dcf_dx_ts = c_ts
        dcf_dx_2035 = c_2035

        partials['sum_fractions', 'x_al'] = 1.0
        partials['sum_fractions', 'x_ts'] = 1.0
        partials['sum_fractions', 'x_2035'] = 1.0

        partials['mass_factor', 'x_al'] = dmf_dx_al
        partials['mass_factor', 'x_ts'] = dmf_dx_ts
        partials['mass_factor', 'x_2035'] = dmf_dx_2035

        partials['cost_factor', 'x_al'] = dcf_dx_al
        partials['cost_factor', 'x_ts'] = dcf_dx_ts
        partials['cost_factor', 'x_2035'] = dcf_dx_2035

        partials['fuselage_mass_scaler', 'x_al'] = fus0 * dmf_dx_al
        partials['fuselage_mass_scaler', 'x_ts'] = fus0 * dmf_dx_ts
        partials['fuselage_mass_scaler', 'x_2035'] = fus0 * dmf_dx_2035

        partials['wing_mass_scaler', 'x_al'] = wing0 * dmf_dx_al
        partials['wing_mass_scaler', 'x_ts'] = wing0 * dmf_dx_ts
        partials['wing_mass_scaler', 'x_2035'] = wing0 * dmf_dx_2035

        partials['horizontal_tail_mass_scaler', 'x_al'] = ht0 * dmf_dx_al
        partials['horizontal_tail_mass_scaler', 'x_ts'] = ht0 * dmf_dx_ts
        partials['horizontal_tail_mass_scaler', 'x_2035'] = ht0 * dmf_dx_2035

        partials['vertical_tail_mass_scaler', 'x_al'] = vt0 * dmf_dx_al
        partials['vertical_tail_mass_scaler', 'x_ts'] = vt0 * dmf_dx_ts
        partials['vertical_tail_mass_scaler', 'x_2035'] = vt0 * dmf_dx_2035