import json,tempfile,unittest
from pathlib import Path
from monde_sf import preparer
from histoire_planete import simuler,PARAMS
from rapport_synthese import generer

class RapportTests(unittest.TestCase):
    def test_donnees_et_six_graphiques(self):
        monde,p=preparer();monde['nom']='<Asteria>'
        h=simuler(p,duree=1e7)
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'monde.json';f.write_text(json.dumps({'monde':monde,'params':p,'history':h}))
            r=generer(f);s=r.read_text()
            self.assertEqual(s.count('<svg '),6)
            self.assertIn('&lt;Asteria&gt;',s)
            self.assertIn('Comparaison de pas non disponible',s)
            self.assertTrue((Path(d)/'synthese_monde.md').exists())
    def test_pas_de_fausse_convergence(self):
        monde,p=preparer();h=simuler(p,duree=1e6)
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'monde.json';f.write_text(json.dumps({'monde':monde,'params':p,'history':h}))
            c={'initial':h[0],'final':dict(h[-1],T_K=999),'max_delta_T_half_K':.001,'max_delta_T_quarter_K':.0005}
            (Path(d)/'histoire_comparaisons.json').write_text(json.dumps(c))
            self.assertIn('non disponible',generer(f).read_text())
