"""Un dossier court issu des états réellement calculés, sans service externe."""
from pathlib import Path
from html import escape
from math import log10, pi
import json
from histoire_planete import PARAMS

def nombre(v):
    if v == 0: return '0'
    if abs(v)>=1e5 or abs(v)<.001: return f'{v:.3g}'
    return f'{v:.3f}'.rstrip('0').rstrip('.')

def graphique(h, cle, titre, unite, facteur=1., offset=0., logarithme=False):
    valeurs=[s[cle]/facteur+offset for s in h]
    if logarithme:
        if min(valeurs)<=0: raise ValueError('Axe logarithmique : valeur non positive')
        valeurs=[log10(v) for v in valeurs]
    lo,hi=min(valeurs),max(valeurs)
    marge=max((hi-lo)*.08,abs(hi)*1e-6,1e-6)
    lo-=marge;hi+=marge
    if cle=='ice':lo,hi=0.,100.
    D=h[-1]['time_yr'] or 1
    points=' '.join(f'{80+400*s["time_yr"]/D:.2f},{190-130*(v-lo)/(hi-lo):.2f}' for s,v in zip(h,valeurs))
    axes=[]
    for j in range(4):
        y=190-130*j/3;v=lo+(hi-lo)*j/3
        label=nombre(10**v if logarithme else v)
        if cle=='ocean_kg': label=f'{v:.8f}'
        axes.append(f'<path d="M80 {y}H480" stroke="#d7e0e5"/><text x="73" y="{y+5}" text-anchor="end">{label}</text>')
    for j in range(5):
        x=80+400*j/4
        axes.append(f'<text x="{x}" y="215" text-anchor="middle">{nombre(D/1e9*j/4)}</text>')
    return f'''<svg viewBox="0 0 520 250" role="img" aria-label="{escape(titre)} en {escape(unite)}">
    <title>{escape(titre)}</title><text x="80" y="28">{escape(titre)} ({escape(unite)})</text>
    {''.join(axes)}<polyline points="{points}" fill="none" stroke="#126478" stroke-width="2"/>
    <text x="165" y="245">Temps depuis le début (Ga)</text></svg>'''

def generer(fichier=None):
    base=Path(__file__).resolve().parent/'resultats'
    fichier=Path(fichier) if fichier else base/'histoire_complete.json'
    data=json.loads(fichier.read_text())
    monde=data['monde'];p=dict(PARAMS,**data.get('params',{}));h=data['history']
    if not h: raise ValueError('Historique vide')
    if any(b['time_yr']<=a['time_yr'] for a,b in zip(h,h[1:])):raise ValueError('Temps non croissants')
    debut,fin=h[0],h[-1];D=fin['time_yr']-debut['time_yr']
    eau0=sum(debut[k] for k in ['vapor_kg','ocean_kg','ice_kg'])
    carbone0=sum(debut[k] for k in ['co2_mol','mantle_c_mol','rock_c_mol'])
    err_eau=max(abs(sum(s[k] for k in ['vapor_kg','ocean_kg','ice_kg'])-eau0)/max(1,eau0) for s in h)
    err_carbone=max(abs(sum(s[k] for k in ['co2_mol','mantle_c_mol','rock_c_mol'])-carbone0)/max(1,carbone0) for s in h)
    gelee=sum(s['ice']>=.9 for s in h)
    resume=(f"La température passe de {nombre(debut['T_K']-273.15)} °C à {nombre(fin['T_K']-273.15)} °C. "
            f"Elle reste entre {nombre(min(s['T_K'] for s in h)-273.15)} et {nombre(max(s['T_K'] for s in h)-273.15)} °C. "
            f"La fraction de glace finale vaut {nombre(100*fin['ice'])} %. "
            + ('Aucun état enregistré ne dépasse 90 % de glace.' if gelee==0 else f'{gelee} états enregistrés dépassent 90 % de glace ; leur nombre n’est pas une durée.'))
    if monde['distance_m']<=0:raise ValueError('Distance invalide')
    caracteristiques=[('Étoile : luminosité de référence',nombre(monde['luminosite_W'])+' W'),
      ('Luminosité / référence solaire',nombre(monde['luminosite_W']/3.828e26)),
      ('Distance orbitale',nombre(monde['distance_m']/1.496e11)+' UA'),
      ('Masse planétaire',nombre(monde['masse_kg'])+' kg'),
      ('Rayon planétaire',nombre(monde['rayon_m']/1000)+' km'),
      ('Gravité calculée',nombre(6.67e-11*monde['masse_kg']/monde['rayon_m']**2)+' m/s²'),
      ('Durée calculée',nombre(D/1e9)+' Ga'),
      ('Flux reçu : début → fin',nombre(debut['solar_W_m2'])+' → '+nombre(fin['solar_W_m2'])+' W/m²')]
    evolution=[('CO₂ atmosphérique','pco2_Pa','Pa'),('Pluie moyenne','rain_mm_yr','mm/an'),
      ('Océan liquide','ocean_kg','kg'),('Vapeur atmosphérique','vapor_kg','kg'),('Eau glacée','ice_kg','kg')]
    lignes=[(nom,nombre(debut[k]),nombre(fin[k]),unit) for nom,k,unit in evolution]
    bilan=f"Erreurs relatives maximales : eau {err_eau:.2e} ; carbone {err_carbone:.2e}. Ces bilans contrôlent les transferts du modèle."
    # Une comparaison de pas n'est attribuée à ce monde que si les états concordent.
    convergence='Comparaison de pas non disponible pour cette simulation.'
    cf=fichier.parent/'histoire_comparaisons.json'
    if cf.exists():
        c=json.loads(cf.read_text())
        if c.get('initial')==debut and c.get('final')==fin:
            convergence=f"Écart maximal de température pour des plafonds de pas successivement divisés par deux : {c['max_delta_T_half_K']:.4g} K puis {c['max_delta_T_quarter_K']:.4g} K."
    assumptions=('Les paramètres sont choisis, pas mesurés pour une planète réelle. L’étoile suit une loi linéaire de luminosité prescrite, valable sur la durée déclarée ; son spectre et sa durée de vie ne sont pas calculés. '
      'Le climat est un équilibre rapide avec une loi de serre bornée. Pluie et évaporation sont des moyennes planétaires. L’eau totale est conservée ; la fraction de glace sert aussi à partager la masse d’eau de surface. '
      'Nuages, météo, chaleur latente, vivant, tectonique détaillée et chimie complète sont absents. Un état tempéré ne démontre pas l’habitabilité.')
    table=lambda rows:'<table>'+''.join('<tr>'+''.join('<td>'+escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</table>'
    graphs=''.join(graphique(h,*args) for args in [
      ('T_K','Température','°C',1,-273.15,False),('pco2_Pa','CO₂ atmosphérique','Pa — axe log',1,0,True),
      ('rain_mm_yr','Pluie moyenne','mm/an',1,0,False),('solar_W_m2','Flux stellaire reçu','W/m²',1,0,False),
      ('ocean_kg','Océan liquide','10²¹ kg',1e21,0,False),('ice','Fraction de glace','%',.01,0,False)])
    title='Notre monde calculé '+str(monde['nom'])
    html=f'''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title>
    <style>body{{font:16px/1.45 system-ui;color:#193442;max-width:1000px;margin:30px auto;padding:0 22px}}h1,h2{{line-height:1.15}}h2{{font-size:21px;margin-top:25px}}table{{border-collapse:collapse;width:100%;font-size:14px}}td{{padding:5px 9px;border-bottom:1px solid #dde5e8}}td:first-child{{font-weight:600}}.graphs{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}svg{{width:100%;font:12px system-ui}}button{{font:inherit;padding:8px 14px}}.note{{color:#526876;font-size:14px}}@media(max-width:650px){{.graphs{{grid-template-columns:1fr}}}}@media print{{@page{{size:A4;margin:15mm}}body{{font-size:11px;margin:0;padding:0}}h1{{font-size:23px}}h2{{font-size:16px}}td{{font-size:10px;padding:3px 6px}}button,.navigation{{display:none}}svg{{break-inside:avoid}}.graphs{{break-before:page;grid-template-columns:1fr 1fr}}.limits{{break-before:page}}}}</style>
    <h1>{escape(title)}</h1><p>Une synthèse courte des résultats de notre simulation · {nombre(D/1e9)} milliards d’années</p>
    <button onclick="window.print()">Imprimer ou enregistrer en PDF</button><p class="navigation"><a href="planete_systemes.html">Explorer le graphe et les boucles</a></p>
    <h2>Le monde choisi</h2>{table(caracteristiques)}
    <h2>Ce que le calcul donne</h2><p>{escape(resume)}</p>
    {table([('Grandeur','Début','Fin','Unité')]+lignes)}
    <p class="note">Le début est l’état choisi avant sa relaxation. Les paramètres de référence solaire sont des unités de comparaison ; aucune chronologie terrestre n’est imposée.</p>
    <div class="graphs">{graphs}</div>
    <div class="limits"><h2>Comment interpréter ces courbes</h2><p>Comparer les variations du CO₂, du rayonnement reçu et de la température. La boucle d’altération peut compenser une partie du changement du rayonnement : température → pluie → altération → retrait du CO₂ → effet de serre. La boucle glace → albédo → refroidissement amplifie un état froid lorsqu’elle est sollicitée. Vérifier ces explications en désactivant une boucle dans le graphe ; une seule courbe ne prouve pas une causalité.</p>
    <h2>Contrôles numériques</h2><p>{escape(bilan)}</p><p>{escape(convergence)}</p>
    <h2>Les hypothèses à garder en tête</h2><p>{escape(assumptions)}</p>
    <h2>Conclusion de la classe</h2><p>Notre monde est… ; les deux mécanismes qui expliquent le mieux son évolution sont… ; la comparaison qui soutient notre explication est… ; notre principale limite est…</p>
    <p class="note">Données sources : {escape(fichier.name)}. Généré automatiquement à partir des états enregistrés. Les élèves complètent l’interprétation, pas les résultats calculés.</p></div></html>'''
    dossier=fichier.parent;out=dossier/'synthese_monde.html';out.write_text(html)
    md='# '+title+'\n\n'+resume+'\n\n## Le monde choisi\n\n'+''.join('- '+a+' : '+b+'\n' for a,b in caracteristiques)
    md+='\n## Contrôles\n\n'+bilan+'\n\n'+convergence+'\n\n## Hypothèses\n\n'+assumptions+'\n\nLes six graphiques sont dans synthese_monde.html, imprimable en PDF.\n'
    (dossier/'synthese_monde.md').write_text(md)
    return out

if __name__=='__main__':
    import sys
    print(generer(sys.argv[1] if len(sys.argv)>1 else None))
