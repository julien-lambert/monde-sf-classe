"""Verification des calculs, de l'assemblage et des erreurs detectees."""
import unittest
from copy import deepcopy
from engine import planet_evolution
from scenarios import base, scenario, MODULES
from modules import gaz, retention, degazage, radiatif, eau, alteration
from modules import oxygenation, uv, glace, climat, energie, demographie
from ensemble import ensemble

class Verification(unittest.TestCase):
    def setUp(self):
        self.s, self.p = base()

    def test_dalton_et_melange(self):
        self.s.update(co2_mol=1., n2_mol=1., o2_mol=0., h2o_mol=0.)
        d = gaz.step(self.s, self.p, 1)['diag']
        self.assertAlmostEqual(d['fractions']['CO2'], .5)
        self.assertAlmostEqual(d['pco2_Pa'], d['P_Pa']/2)
        self.s.update(co2_mol=0., n2_mol=0.)
        self.assertEqual(gaz.step(self.s, self.p, 1)['diag']['P_Pa'], 0)

    def test_retention(self):
        d = retention.step(self.s, self.p, 1)['diag']
        self.assertAlmostEqual(d['vlib_m_s']/1000, 11.18, delta=.03)
        self.assertFalse(d['retention']['H2'])
        self.assertTrue(d['retention']['N2'])

    def test_degazage_epuisement(self):
        self.s.update(mantle_c_mol=100., co2_mol=0.)
        self.p['volcanic_mol_yr'] = 10.
        h = planet_evolution(self.s, self.p, [degazage.step], 15, 1)
        self.assertEqual(h[-1]['co2_mol'], 100)
        self.assertEqual(h[-1]['mantle_c_mol'], 0)
        for s in h:
            self.assertEqual(s['co2_mol'] + s['mantle_c_mol'], 100)

    def test_equilibre_radiatif(self):
        d = radiatif.step(self.s, self.p, 1)['diag']
        self.assertAlmostEqual(d['Teq_K'], 254.58, delta=.03)
        self.assertAlmostEqual(d['absorbed_W_m2'], 238.175)
        self.p['S_W_m2'] *= .71
        self.assertAlmostEqual(radiatif.step(self.s, self.p, 1)['diag']['Teq_K'], 233.69, delta=.05)

    def test_eau_pure_et_melange(self):
        self.p.update(water_mode='pure_demo', ocean_prescribed=False)
        self.s['T_K'] = 473.15
        self.s['diag'] = {'P_Pa': 1e7, 'ph2o_Pa': 1e7}
        self.assertTrue(eau.step(self.s, self.p, 1)['diag']['ocean_possible'])
        self.s['diag']['P_Pa'] = 1e5
        self.assertFalse(eau.step(self.s, self.p, 1)['diag']['ocean_possible'])
        self.p['water_mode'] = 'mixed_screen'
        self.s['T_K'] = 293.15
        self.s['diag'].update(P_Pa=1e5, ph2o_Pa=1000)
        self.assertFalse(eau.step(self.s, self.p, 1)['diag']['ocean_possible'])
        self.s['diag']['ph2o_Pa'] = 3000
        self.assertTrue(eau.step(self.s, self.p, 1)['diag']['ocean_possible'])
        self.s['T_K'] = 1000
        self.assertIsNone(eau.step(self.s, self.p, 1)['diag']['ocean_possible'])

    def test_alteration_transfert_et_arret(self):
        self.s.update(T_K=288., co2_mol=100.)
        self.s['diag'] = {'ocean_possible': True}
        self.p.update(weather_mol_yr=10., co2_ref_mol=100.)
        r = alteration.step(self.s, self.p, 1)['rates']
        self.assertEqual(r['co2_mol'], -10)
        self.assertEqual(sum(r.values()), 0)
        self.s['diag']['ocean_possible'] = None
        self.assertEqual(alteration.step(self.s, self.p, 1)['rates']['co2_mol'], 0)

    def test_puits_oxygene_et_fer(self):
        self.s.update(o2_mol=0., fe_mol=40.)
        self.p['oxygen_mol_yr'] = 1.
        h = planet_evolution(self.s, self.p, [oxygenation.step], 15, 1)
        self.assertEqual(h[10]['o2_mol'], 0)
        self.assertEqual(h[-1]['o2_mol'], 5)
        for s in h:
            self.assertEqual(s['fe_mol'] + s['oxide_fe_mol'], 40)

    def test_uv(self):
        self.p['ozone_column_mol_m2'] = 0.
        self.assertEqual(uv.step(self.s, self.p, 1)['diag']['uv_fraction'], 1)
        self.p['ozone_column_mol_m2'] = .01
        d = uv.step(self.s, self.p, 1)['diag']
        self.assertAlmostEqual(d['uv_fraction'], .367879, places=5)
        self.assertFalse(d['dissociation_possible'])
        self.p['lambda_nm'] = 239
        self.assertTrue(uv.step(self.s, self.p, 1)['diag']['dissociation_possible'])

    def test_glace_pas_et_cible(self):
        self.s.update(T_K=260., ice=0.)
        h = planet_evolution(self.s, self.p, [glace.step], 1, 1)
        self.assertAlmostEqual(h[-1]['ice'], .05)
        with self.assertRaises(ValueError):
            planet_evolution(self.s, self.p, [glace.step], 1, 30)

    def test_climat_et_serre(self):
        self.s.update(T_K=260.)
        self.s['diag'] = {'pco2_Pa': 42., 'Teq_K': 254.6}
        r = climat.step(self.s, self.p, 1)
        self.assertAlmostEqual(r['diag']['Ttarget_K'], 287.6)
        self.assertAlmostEqual(r['rates']['T_K'], 2.76)
        self.s['diag']['pco2_Pa'] = 0
        self.assertEqual(climat.step(self.s, self.p, 1)['diag']['greenhouse_K'], 0)

    def test_energie_demographie_et_reserve(self):
        self.s.update(population=1000., fossil_J=1e13)
        self.p.update(birth_rate_yr=.02, death_rate_yr=.01, deficit_death_rate_yr=.02)
        d = energie.step(self.s, self.p, 1)
        self.assertAlmostEqual(d['diag']['deficit_fraction'], .3)
        self.assertAlmostEqual(d['rates']['co2_mol'], 6e5)
        self.s['diag'] = d['diag']
        self.assertAlmostEqual(demographie.step(self.s, self.p, 1)['rates']['population'], 4)
        h = planet_evolution(self.s, self.p, [energie.step, demographie.step], 100, 1)
        self.assertEqual(h[-1]['fossil_J'], 0)
        self.assertAlmostEqual(h[-1]['emitted_c_mol'], 2e7, delta=1e-6)

    def test_isolement_et_instant_des_diagnostics(self):
        initial, params = deepcopy(self.s), deepcopy(self.p)
        h = planet_evolution(self.s, self.p, MODULES, 3, 1)
        self.assertEqual(self.s, initial)
        self.assertEqual(self.p, params)
        for s in h:
            self.assertEqual(s['diag']['Teq_K'], radiatif.step(s, params, 1)['diag']['Teq_K'])
        h[0]['diag']['P_Pa'] = 0
        self.assertGreater(h[1]['diag']['P_Pa'], 0)

    def test_erreurs_detectees(self):
        with self.assertRaises(ValueError):
            planet_evolution(self.s, self.p, MODULES, 1, 0)
        with self.assertRaises(ValueError):
            planet_evolution(self.s, self.p, [gaz.step, gaz.step], 1, 1)
        self.s['co2_mol'] = -1
        with self.assertRaises(ValueError):
            planet_evolution(self.s, self.p, MODULES, 1, 1)

    def test_conservation_geologie_et_convergence(self):
        s, p, n, dt = scenario('deglaciation')
        h = planet_evolution(s, p, MODULES, n, dt)
        carbone_initial = s['mantle_c_mol'] + s['co2_mol'] + s['rock_c_mol']
        for ligne in h:
            carbone = ligne['mantle_c_mol'] + ligne['co2_mol'] + ligne['rock_c_mol']
            self.assertAlmostEqual(carbone/carbone_initial, 1., delta=1e-12)
        fin = planet_evolution(s, p, MODULES, n*2, dt/2)[-1]
        self.assertLess(abs(fin['T_K'] - h[-1]['T_K']), .1)
        self.assertLess(abs(fin['ice'] - h[-1]['ice']), .01)

    def test_deux_etats_et_deglaciation(self):
        for nom, chaud in [('chaude', True), ('gelee', False), ('deglaciation', True)]:
            s, p, n, dt = scenario(nom)
            fin = planet_evolution(s, p, MODULES, n, dt)[-1]
            self.assertEqual(fin['T_K'] > 273.15, chaud)
            self.assertLess(fin['ice'], .01) if chaud else self.assertGreater(fin['ice'], .99)

    def test_monte_carlo_reproductible_et_constant(self):
        a = ensemble(self.s, self.p, MODULES, 10, 1, nombre=3)
        b = ensemble(self.s, self.p, MODULES, 10, 1, nombre=3)
        self.assertEqual(a, b)
        fixe = ensemble(self.s, self.p, MODULES, 10, 1, nombre=3,
                        bornes={'pref_Pa': (42., 42.)})
        self.assertEqual(fixe['histories'][0], fixe['histories'][1])
        echec = ensemble(self.s, self.p, MODULES, 10, 1, nombre=2,
                         bornes={'tau_T_yr': (.1, .1)})
        self.assertEqual(len(echec['failures']), 2)
        self.assertEqual(echec['summary'], {})

if __name__ == '__main__':
    unittest.main(verbosity=2)
