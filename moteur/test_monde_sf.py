import json,tempfile,unittest
from pathlib import Path
from monde_sf import preparer
from histoire_planete import simuler

class MondeTests(unittest.TestCase):
    def test_flux_gravite(self):
        monde,p=preparer()
        self.assertAlmostEqual(p['stellar_flux_W_m2'],1361,delta=1)
        self.assertAlmostEqual(p['gravity_m_s2'],9.81,delta=.01)
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'test.json';monde['distance_m']*=2;f.write_text(json.dumps(monde))
            _,q=preparer(f)
            self.assertAlmostEqual(q['stellar_flux_W_m2'],p['stellar_flux_W_m2']/4)
    def test_cinq_milliards(self):
        monde,p=preparer();h=simuler(p,duree=monde['duree_yr'])
        self.assertEqual(h[-1]['time_yr'],5e9)
        self.assertEqual(h[-1]['age_Ga'],0)
        for s in h:
            self.assertAlmostEqual((s['vapor_kg']+s['ocean_kg']+s['ice_kg'])/p['water_kg'],1,places=12)
            self.assertAlmostEqual((s['co2_mol']+s['mantle_c_mol']+s['rock_c_mol'])/1e23,1,places=12)
    def test_validite_stellaire(self):
        m,p=preparer()
        with self.assertRaises(ValueError):simuler(p,duree=p['stellar_validity_yr']*2)
