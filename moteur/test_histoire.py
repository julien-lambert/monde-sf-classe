import unittest
from bisect import bisect_left
from histoire_planete import simuler, hydrologie, carbone, PARAMS

def ecart(a,b):
    ts=[s['time_yr'] for s in b]; erreurs=[]
    for s in a:
        i=max(1,min(len(b)-1,bisect_left(ts,s['time_yr'])))
        f=(s['time_yr']-ts[i-1])/(ts[i]-ts[i-1])
        valeur=b[i-1]['T_K']*(1-f)+b[i]['T_K']*f
        erreurs.append(abs(s['T_K']-valeur))
    return max(erreurs)

class HistoireTests(unittest.TestCase):
    def test_eau_et_flux(self):
        p=PARAMS; V=1e16; dt=1e6
        r=hydrologie(290,.2,V,dt,p)
        self.assertAlmostEqual((r['vapor_kg']+r['ocean_kg']+r['ice_kg'])/p['water_kg'],1)
        self.assertAlmostEqual((r['evap_kg_yr']-r['precip_kg_yr'])*dt/(r['vapor_kg']-V),1,places=7)
        self.assertGreater(r['rain_mm_yr'],0)
        froid=hydrologie(250,1,V,dt,p)
        self.assertEqual(froid['ocean_kg'],0)
        self.assertEqual(froid['rain_mm_yr'],0)
    def test_carbone_transfert(self):
        C,M,R,W=carbone(1e17,1e20,0,288,0,5e17,1,1e6,PARAMS)
        self.assertAlmostEqual((C+M+R)/(1e17+1e20),1)
        self.assertGreaterEqual(min(C,M,R,W),0)
    def test_bilans_toute_histoire(self):
        for s in simuler():
            self.assertAlmostEqual((s['vapor_kg']+s['ocean_kg']+s['ice_kg'])/PARAMS['water_kg'],1,places=12)
            self.assertAlmostEqual((s['co2_mol']+s['mantle_c_mol']+s['rock_c_mol'])/PARAMS['carbon_mol'],1,places=12)
        self.assertEqual(s['age_Ga'],0)
    def test_convergence_trajectoire(self):
        a=simuler();b=simuler(dt=5e5);c=simuler(dt=2.5e5)
        self.assertLess(ecart(a,b),.01)
        self.assertLess(ecart(b,c),ecart(a,b))
    def test_boucles_et_determinisme(self):
        a=simuler();b=simuler({'weather_feedback':False})
        self.assertEqual(a,simuler())
        self.assertGreater(b[-1]['T_K'],a[-1]['T_K']+10)
        for i in range(16):
            p={k:bool(i&(1<<j)) for j,k in enumerate(['weather_feedback','ice_feedback','water_feedback','solar_evolution'])}
            self.assertEqual(simuler(p)[-1]['age_Ga'],0)
    def test_erreurs(self):
        with self.assertRaises(ValueError):simuler(dt=0)
        with self.assertRaises(ValueError):simuler({'water_kg':-1})

if __name__=='__main__':unittest.main(verbosity=2)
