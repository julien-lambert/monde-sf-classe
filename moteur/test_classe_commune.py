import unittest,sys
from pathlib import Path
from copy import deepcopy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'partage'))
import classe_commune as c

class ClasseTests(unittest.TestCase):
    def test_toutes_routines(self):
        self.assertEqual(len(c.ROUTINES),12)
        for nom in ['chaude','gelee','deglaciation','societe','oxygenation']:
            s,p,n,dt=c.scenario_classe(nom)
            self.assertEqual(len(c.planet_evolution(s,p,c.MODULES,n,dt)),n+1)
    def test_remplacement_local_et_rapport(self):
        avant=dict(c.ROUTINES)
        r=c.comparer_groupe(12,c.ROUTINES[12])
        self.assertEqual(r['commun'],r['avec_ma_routine'])
        def population_fixe(s,p,dt):
            return {'rates':{'population':0},'values':{},'diag':{'births_yr':0,'deaths_yr':0}}
        r=c.comparer_groupe(12,population_fixe)
        self.assertNotEqual(r['commun'][-1]['population'],r['avec_ma_routine'][-1]['population'])
        self.assertEqual(c.ROUTINES,avant)
        self.assertIn(c.VERSION_CLASSE,c.rapport_comparaison(r))
        self.assertEqual(c.rapport_comparaison(r).count('<svg'),4)
    def test_isolement(self):
        def mauvaise(s,p,dt):
            s['T_K']=1
            return c.ROUTINES[1](s,p,dt)
        with self.assertRaises(ValueError):c.comparer_groupe(1,mauvaise)
    def test_monte_carlo_commun(self):
        s,p,n,dt=c.scenario_classe('societe')
        r=c.ensemble(s,p,c.MODULES,n,dt,nombre=3)
        self.assertEqual(r['summary']['successes'],3)
