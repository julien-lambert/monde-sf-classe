"""Paramètres choisis pour notre monde fictif, sans calendrier terrestre."""
from pathlib import Path
from math import pi, isfinite
import json

def preparer(chemin=None):
    chemin=Path(chemin) if chemin else Path(__file__).with_name('monde_sf.json')
    monde=json.loads(chemin.read_text())
    for k in ['luminosite_W','distance_m','masse_kg','rayon_m','duree_yr',
              'stellar_validity_yr','stellar_initial_ratio','stellar_final_ratio','water_kg']:
        if not isfinite(monde[k]) or monde[k]<=0: raise ValueError('Paramètre positif requis : '+k)
    if monde['duree_yr']>monde['stellar_validity_yr']:
        raise ValueError('Durée au-delà de la validité du scénario stellaire')
    for k in ['co2_initial_mol','n2_mol']:
        if not isfinite(monde[k]) or monde[k]<0: raise ValueError('Stock invalide : '+k)
    R=monde['rayon_m'];M=monde['masse_kg'];d=monde['distance_m'];L=monde['luminosite_W']
    p={k:monde[k] for k in ['stellar_validity_yr','stellar_initial_ratio','stellar_final_ratio',
                            'water_kg','co2_initial_mol','n2_mol']}
    p.update(stellar_flux_W_m2=L/(4*pi*d*d),gravity_m_s2=6.67e-11*M/(R*R),area_m2=4*pi*R*R)
    return monde,p

if __name__=='__main__':
    from histoire_planete import simuler
    monde,p=preparer();h=simuler(p,duree=monde['duree_yr'])
    out=Path(__file__).with_name('resultats');out.mkdir(exist_ok=True)
    (out/'monde_sf_complet.json').write_text(json.dumps({'monde':monde,'params':p,'history':h},indent=2))
    from rapport_synthese import generer
    print('Synthèse :',generer(out/'monde_sf_complet.json'))
    print(monde['nom'],len(h),'états ; T finale',round(h[-1]['T_K'],2),'K')
