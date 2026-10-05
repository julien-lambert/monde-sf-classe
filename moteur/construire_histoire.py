import sys,json,unittest,io
from pathlib import Path
root=Path(__file__).resolve().parent;sys.path.insert(0,str(root))
(root/'resultats').mkdir(exist_ok=True)
from histoire_planete import simuler,PARAMS
from monde_sf import preparer
monde,monde_params=preparer()
def simuler_reference(p=None,dt=1e6):
    return simuler(dict(monde_params,**(p or {})),dt=dt,duree=monde["duree_yr"])
from test_histoire import ecart
import test_histoire
r=io.StringIO(); suite=unittest.defaultTestLoader.loadTestsFromModule(test_histoire)
res=unittest.TextTestRunner(stream=r,verbosity=2).run(suite)
(root/'resultats/verification_histoire.txt').write_text(r.getvalue())
print(r.getvalue())
assert res.wasSuccessful()
scenarios={}
for i in range(16):
 p={k:bool(i&(1<<j)) for j,k in enumerate(['weather_feedback','ice_feedback','water_feedback','solar_evolution'])}
 h=simuler_reference(p)
 # Garder les débuts courts et ~500 points répartis dans le temps.
 kept=h[:195]+h[195::8]
 if kept[-1]!=h[-1]:kept.append(h[-1])
 keys=['age_Ga','T_K','ice','pco2_Pa','rain_mm_yr','ocean_kg','vapor_kg','ice_kg','solar_W_m2','evap_kg_yr']
 scenarios[str(i)]={k:[round(s[k],8) for s in kept] for k in keys}
h=simuler_reference(); b=simuler_reference(dt=5e5); c=simuler_reference(dt=2.5e5)
(root/'resultats/histoire_complete.json').write_text(json.dumps({'monde':monde,'params':dict(PARAMS,**monde_params),'history':h},indent=2))
(root/'resultats/histoire_comparaisons.json').write_text(json.dumps({'max_delta_T_half_K':ecart(h,b),'max_delta_T_quarter_K':ecart(b,c),'initial':h[0],'final':h[-1]},indent=2))
(root/'resultats/histoire_scenarios.js').write_text('const scenarios='+json.dumps(scenarios,separators=(',',':'))+';')

from rapport_synthese import generer
print("Synthèse :",generer())

from html import escape
page=(root/'interface/planete_systemes.html').read_text()
page=page.replace('Monde SF Asteria · cinq milliards', 'Monde SF '+escape(monde['nom'])+' · '+str(monde['duree_yr']/1e9)+' milliards')
(root/'resultats/planete_systemes.html').write_text(page)
