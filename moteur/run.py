"""Lancer les experiences, verifier, puis fabriquer un rapport sans dependances."""
from pathlib import Path
from html import escape
import csv
import io
import json
import unittest
from engine import planet_evolution
from scenarios import scenario, MODULES
from ensemble import ensemble
import tests

DOSSIER = Path(__file__).resolve().parent
RESULTATS = DOSSIER / 'resultats'

def courbe(histoire, cle, titre, unite):
    valeurs = [s[cle] for s in histoire]
    bas, haut = min(valeurs), max(valeurs)
    if haut == bas:
        bas -= max(1, abs(bas)*.01)
        haut += max(1, abs(haut)*.01)
    temps = histoire[-1]['time_yr'] or 1
    points = []
    for s in histoire:
        x = 65 + 590*s['time_yr']/temps
        y = 205 - 160*(s[cle]-bas)/(haut-bas)
        points.append(f'{x:.2f},{y:.2f}')
    return f'''<svg viewBox="0 0 700 260" role="img" aria-label="{escape(titre)}">
    <rect width="700" height="260" fill="white"/>
    <text x="65" y="25">{escape(titre)} ({escape(unite)})</text>
    <path d="M65 40 V205 H655" fill="none" stroke="#aaa"/>
    <polyline points="{' '.join(points)}" fill="none" stroke="#216090" stroke-width="2"/>
    <text x="5" y="50">{haut:.4g}</text><text x="5" y="205">{bas:.4g}</text>
    <text x="65" y="235">0</text><text x="535" y="235">{temps:g} ans</text></svg>'''

def main():
    RESULTATS.mkdir(exist_ok=True)
    sortie = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
    verification = unittest.TextTestRunner(stream=sortie, verbosity=2).run(suite)
    (RESULTATS/'verification.txt').write_text(sortie.getvalue())
    if not verification.wasSuccessful():
        print(sortie.getvalue())
        raise SystemExit('Verification echouee : consulter resultats/verification.txt')
    experiences = {}
    morceaux = []
    resume = {}
    for nom in ['chaude', 'gelee', 'deglaciation', 'societe', 'oxygenation']:
        initial, params, n, dt = scenario(nom)
        h = planet_evolution(initial, params, MODULES, n, dt)
        experiences[nom] = h
        final = h[-1]
        carbone0 = initial['co2_mol'] + initial['mantle_c_mol'] + initial['rock_c_mol']
        erreurs = []
        for s in h:
            total = s['co2_mol'] + s['mantle_c_mol'] + s['rock_c_mol']
            attendu = carbone0 + s['emitted_c_mol']
            erreurs.append(abs(total-attendu)/max(1, abs(attendu)))
        h_demi = planet_evolution(initial, params, MODULES, n*2, dt/2)
        fin_demi = h_demi[-1]
        ecart_trajectoire = max(abs(a['T_K']-h_demi[2*i]['T_K']) for i,a in enumerate(h))
        bilan = {'T_initial_K': initial['T_K'], 'T_final_K': final['T_K'],
                 'ice_final': final['ice'], 'population_final': final['population'],
                 'carbon_relative_error_max': max(erreurs),
                 'delta_T_dt_half_K': abs(final['T_K']-fin_demi['T_K']),
                 'delta_ice_dt_half': abs(final['ice']-fin_demi['ice']),
                 'max_delta_T_trajectory_K': ecart_trajectoire,
                 'duration_yr': n*dt, 'dt_yr': dt}
        resume[nom] = bilan
        (RESULTATS/(nom+'.json')).write_text(json.dumps({'initial': initial, 'params': params,
                                                       'history': h}, indent=2))
        cles = ['time_yr', 'T_K', 'ice', 'co2_mol', 'rock_c_mol', 'mantle_c_mol',
                'o2_mol', 'fe_mol', 'oxide_fe_mol', 'population', 'fossil_J', 'emitted_c_mol']
        with (RESULTATS/(nom+'.csv')).open('w', newline='') as fichier:
            writer = csv.DictWriter(fichier, fieldnames=cles)
            writer.writeheader()
            writer.writerows({k:s[k] for k in cles} for s in h)
        texte = (f"{n*dt:g} ans, pas {dt:g} an(s). Température finale {final['T_K']:.2f} K. "
                 f"Glace {100*final['ice']:.2f} %. Écart de T avec un pas divisé par deux : "
                 f"{bilan['delta_T_dt_half_K']:.4g} K ; écart maximal sur la trajectoire : {ecart_trajectoire:.4g} K. Erreur relative maximale du bilan carbone : "
                 f"{max(erreurs):.2e}.")
        dessins = courbe(h, 'T_K', 'Température de surface', 'K') + courbe(h, 'ice', 'Fraction de glace', '0 à 1')
        if nom == 'deglaciation':
            dessins += courbe(h, 'co2_mol', 'Stock atmosphérique de CO2', 'mol')
        if nom == 'societe':
            dessins += courbe(h, 'population', 'Population moyenne', 'personnes')
            dessins += courbe(h, 'fossil_J', 'Réserve énergétique fossile', 'J')
        if nom == 'oxygenation':
            dessins += courbe(h, 'o2_mol', 'O2 après saturation du puits', 'mol')
        morceaux.append(f'<section><h2>{escape(nom.capitalize())}</h2><p>{texte}</p><div class="plots">{dessins}</div></section>')
        print(nom, ':', round(final['T_K'], 2), 'K ; glace', round(final['ice'], 4))
    initial, params, _, _ = scenario('chaude')
    resultat = ensemble(initial, params, MODULES, 100, 1, nombre=50)
    (RESULTATS/'monte_carlo.json').write_text(json.dumps(resultat, indent=2))
    resume['monte_carlo'] = resultat['summary']
    (RESULTATS/'resume.json').write_text(json.dumps(resume, indent=2))
    mc = resultat['summary']
    page = '''<!doctype html><html lang="fr"><meta charset="utf-8">
    <title>Évolution de notre planète numérique</title><style>
    body{font:17px/1.5 system-ui;color:#172936;max-width:1100px;margin:40px auto;padding:0 22px;background:#f5f7f9}
    h1,h2{line-height:1.2}section{background:white;padding:22px;margin:28px 0;border-radius:10px}
    .plots{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
    svg{width:100%;font:14px system-ui}code{background:#e7eef3;padding:2px 4px}
    </style><h1>Notre planète évolue</h1>
    <p>Douze routines simples, un moteur déterministe et une expérience Monte-Carlo.
    Les lois ajoutées sont pédagogiques ; elles ne prédisent pas le climat réel.</p>'''
    page += f'<p><strong>{verification.testsRun} vérifications réussies.</strong> Les paramètres et les trajectoires sont enregistrés dans les fichiers JSON et CSV voisins.</p>'
    page += '''<section><h2>Comment fonctionne le moteur</h2>
    <p>Le moteur regarde les stocks à un instant. Les routines calculent les pressions,
    l’équilibre radiatif et les flux à partir de ce même état. Le moteur additionne les flux,
    les multiplie par la durée du pas, puis met tous les stocks à jour ensemble.</p>
    <p>Exemple : 100 mol de carbone et un transfert de 10 mol/an pendant 1 an donnent
    90 mol dans le manteau et 10 mol de plus dans l’air. La somme est conservée.</p>
    <p>Les diagnostics et les stocks enregistrés correspondent au même instant. Le hasard
    intervient seulement quand Monte-Carlo choisit les paramètres de plusieurs expériences.</p></section>'''
    page += ''.join(morceaux)
    page += f'''<section><h2>Monte-Carlo</h2><p>50 jeux de paramètres, graine 2026.
    {len(resultat['failures'])} échec(s). Médiane finale : {mc['median_T_K']:.2f} K ;
    quantiles 5 et 95 % : {mc['q05_T_K']:.2f} et {mc['q95_T_K']:.2f} K.
    Il s’agit d’une incertitude fictive sur les paramètres, pas d’un intervalle de prévision terrestre.</p></section>
    <section><h2>Lire correctement les résultats</h2><p>La déglaciation utilise des temps de réponse
    géologiques de 10 000 et 20 000 ans. La société utilise des temps de 10 et 20 ans.
    Nous ne mélangeons pas les pas de ces expériences.</p>
    <p>L’océan et la colonne d’ozone sont prescrits. Le modèle d’eau ne transfère pas de vapeur
    vers un océan ; la production de O2 est extérieure. Les émissions du petit scénario société
    sont trop faibles pour modifier visiblement la température globale. La réserve fossile, elle,
    s’épuise et le déficit énergétique agit sur la démographie fictive.</p>
    <p>Un bilan conservé et un calcul convergent vérifient le programme. Ils ne prouvent pas que
    toutes ses lois décrivent correctement une planète réelle.</p></section></html>'''
    (RESULTATS/'rapport.html').write_text(page)
    print('Rapport :', RESULTATS/'rapport.html')

if __name__ == '__main__':
    main()
