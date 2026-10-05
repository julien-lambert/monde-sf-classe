VERSION_CLASSE = 'c41ab9f89aae'
"""Version commune de la classe : indépendante de tout fichier annexe."""


"""Un moteur deterministe : lire, additionner les flux, avancer, verifier."""
from copy import deepcopy
from math import isfinite

STOCKS = ["co2_mol", "n2_mol", "o2_mol", "h2o_mol", "mantle_c_mol",
          "rock_c_mol", "fe_mol", "oxide_fe_mol", "population", "fossil_J",
          "emitted_c_mol"]
VARIABLES = STOCKS + ["T_K", "ice"]

def verifier_etat(s):
    for cle in VARIABLES + ["time_yr"]:
        if not isfinite(s[cle]) or s[cle] < 0:
            raise ValueError(f"Valeur invalide : {cle} = {s[cle]}")
    if s["ice"] > 1 or s["T_K"] <= 0:
        raise ValueError("Fraction de glace ou temperature invalide")

def verifier_diagnostic(x):
    if isinstance(x, dict):
        for valeur in x.values():
            verifier_diagnostic(valeur)
    elif isinstance(x, (int, float)) and not isfinite(x):
        raise ValueError("Diagnostic non fini")
    elif not isinstance(x, (str, bool, int, float, type(None))):
        raise ValueError("Type de diagnostic invalide")

def evaluer(s, p, modules, dt):
    travail = deepcopy(s)
    travail["diag"] = {}
    taux = {cle: 0.0 for cle in VARIABLES}
    for module in modules:
        try:
            r = module(deepcopy(travail), deepcopy(p), dt)
            if set(r) != {"rates", "values", "diag"} or r["values"]:
                raise ValueError("Contrat de sortie incorrect")
            for cle, valeur in r["rates"].items():
                if cle not in taux or not isfinite(valeur):
                    raise ValueError(f"Taux invalide : {cle}")
                taux[cle] += valeur
            for cle, valeur in r["diag"].items():
                if cle in travail["diag"]:
                    raise ValueError(f"Diagnostic duplique : {cle}")
                verifier_diagnostic(valeur)
                travail["diag"][cle] = valeur
        except (ValueError, KeyError, TypeError) as erreur:
            raise ValueError(f"{module.__module__}, t={s['time_yr']}, dt={dt} : {erreur}") from erreur
    return travail, taux

def planet_evolution(initial, params, modules, steps, dt_yr):
    if not isfinite(dt_yr) or dt_yr <= 0:
        raise ValueError("Le pas doit etre positif et fini")
    if not isinstance(steps, int) or steps < 0:
        raise ValueError("Le nombre de pas doit etre entier et >= 0")
    s = deepcopy(initial)
    verifier_etat(s)
    histoire = []
    for numero in range(steps + 1):
        # On enregistre les diagnostics du MEME instant que les stocks.
        travail, taux = evaluer(s, params, modules, dt_yr)
        histoire.append(deepcopy(travail))
        if numero == steps:
            break
        suivant = deepcopy(travail)
        for cle in VARIABLES:
            suivant[cle] = s[cle] + dt_yr * taux[cle]
        suivant["time_yr"] += dt_yr
        verifier_etat(suivant)
        s = suivant
    return histoire


# Projet 1 : stocks en mol, pressions en Pa.
def routine_1(s, p, dt):
    masses = {"co2_mol": .044, "n2_mol": .028,
              "o2_mol": .032, "h2o_mol": .018}
    total = sum(s[k] for k in masses)
    masse = sum(s[k] * masses[k] for k in masses)
    pression = masse * p["g_m_s2"] / p["area_m2"]
    fractions = {}
    for nom, cle in [("CO2", "co2_mol"), ("N2", "n2_mol"),
                     ("O2", "o2_mol"), ("H2O", "h2o_mol")]:
        fractions[nom] = s[cle] / total if total else 0.0
    return {"rates": {}, "values": {}, "diag": {
        "P_Pa": pression, "fractions": fractions,
        "pco2_Pa": pression * fractions["CO2"],
        "po2_Pa": pression * fractions["O2"],
        "ph2o_Pa": pression * fractions["H2O"]}}


# Projet 2 : un critere de retention, pas un taux de fuite.
def routine_2(s, p, dt):
    vlib = (2 * p["G"] * p["mass_kg"] / p["radius_m"]) ** .5
    retenus = {}
    for gaz, masse_molaire in {"H2": .002, "N2": .028, "CO2": .044}.items():
        masse = masse_molaire / p["NA"]
        vitesse = (3 * p["kB"] * p["T_exo_K"] / masse) ** .5
        retenus[gaz] = vlib > 6 * vitesse
    return {"rates": {}, "values": {}, "diag": {
        "vlib_m_s": vlib, "retention": retenus}}


# Projet 3 : transfert conserve de carbone, mol/an.
def routine_3(s, p, dt):
    flux = min(p["volcanic_mol_yr"], s["mantle_c_mol"] / dt)
    return {"rates": {"co2_mol": flux, "mantle_c_mol": -flux},
            "values": {}, "diag": {"volcanic_actual_mol_yr": flux}}


# Projet 4 : equilibre radiatif sans serre.
def routine_4(s, p, dt):
    albedo = .30 + .30 * s["ice"]
    absorbe = p["S_W_m2"] * (1 - albedo) / 4
    temperature = (absorbe / p["sigma"]) ** .25
    return {"rates": {}, "values": {}, "diag": {
        "albedo": albedo, "absorbed_W_m2": absorbe, "Teq_K": temperature}}


# Projet 5 : interpolation, eau pure ou possibilite de condensation.
# Table arrondie ajoutee au cours. Aucune masse d'eau n'est transferee.
TABLE = [(0.01, 610), (10, 1230), (20, 2340), (30, 4240),
         (50, 12350), (80, 47400), (100, 100000),
         (180, 1000000), (275, 6000000), (311, 10000000)]

def interpoler(x, points):
    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return None

def routine_5(s, p, dt):
    T = s["T_K"] - 273.15
    pression = s["diag"]["P_Pa"]
    saturation = interpoler(T, TABLE)
    possible = None
    domaine = "indetermine"
    if p["water_mode"] == "pure_demo":
        ebullition = interpoler(pression, [(v, t) for t, v in TABLE if v >= 1e5])
        if ebullition is not None:
            if T < 0:
                domaine, possible = "glace", False
            elif T == 0 or T == ebullition:
                domaine = "frontiere"
            elif T < ebullition:
                domaine, possible = "liquide", True
            else:
                domaine, possible = "vapeur", False
    elif saturation is not None:
        possible = s["diag"]["ph2o_Pa"] >= saturation
        domaine = "condensation_possible" if possible else "vapeur_non_saturee"
    # Un ocean deja present est une condition prescrite du scenario.
    # Son volume ne change pas : pas de simulation du cycle de l'eau.
    if p["ocean_prescribed"]:
        possible = s["ice"] < 1 and 273.15 < s["T_K"] < 373.15
        domaine = "ocean_prescrit" if possible else "ocean_prescrit_inactif"
    return {"rates": {}, "values": {}, "diag": {
        "water_domain": domaine, "ocean_possible": possible,
        "saturation_Pa": saturation}}


# Projet 6 : une loi fictive locale, transfert CO2 -> roches.
def routine_6(s, p, dt):
    flux = 0.0
    if s["diag"]["ocean_possible"] is True:
        chaleur = max(0.0, 1 + (s["T_K"] - 288) / 50)
        flux = (p["weather_mol_yr"] * p["land_fraction"]
                * (1 - s["ice"]) * chaleur
                * s["co2_mol"] / p["co2_ref_mol"])
    flux = min(flux, s["co2_mol"] / dt)
    return {"rates": {"co2_mol": -flux, "rock_c_mol": flux},
            "values": {}, "diag": {"weather_actual_mol_yr": flux}}


# Projet 7 : flux externe O2, puits fini de Fe ; stocks en mol.
def routine_7(s, p, dt):
    production = p["oxygen_mol_yr"]
    utilise = min(s["o2_mol"] + production * dt, s["fe_mol"] / 4)
    return {"rates": {"o2_mol": production - utilise / dt,
                       "fe_mol": -4 * utilise / dt,
                       "oxide_fe_mol": 4 * utilise / dt},
            "values": {}, "diag": {"oxygen_used_mol_yr": utilise / dt}}


# Projet 8 : colonne d'ozone prescrite, coefficient a une longueur d'onde.
from math import exp

def routine_8(s, p, dt):
    photon = p["h"] * p["c"] / (p["lambda_nm"] * 1e-9)
    seuil = 498000 / p["NA"]
    transmission = exp(-p["absorption_m2_mol"] * p["ozone_column_mol_m2"])
    return {"rates": {}, "values": {}, "diag": {
        "photon_J": photon, "dissociation_possible": photon >= seuil,
        "uv_fraction": transmission}}


# Projet 9 : relaxation vers une couverture de glace fictive.
def routine_9(s, p, dt):
    if dt > p["tau_ice_yr"]:
        raise ValueError("dt doit etre <= tau_ice_yr")
    if s["T_K"] <= 263:
        cible = 1.0
    elif s["T_K"] >= 283:
        cible = 0.0
    else:
        cible = (283 - s["T_K"]) / 20
    taux = (cible - s["ice"]) / p["tau_ice_yr"]
    return {"rates": {"ice": taux}, "values": {}, "diag": {}}


# Projet 10 : loi de serre fictive, Euler explicite.
def routine_10(s, p, dt):
    if dt > p["tau_T_yr"]:
        raise ValueError("dt doit etre <= tau_T_yr")
    co2 = s["diag"]["pco2_Pa"]
    serre = 66 * co2 / (co2 + p["pref_Pa"])
    cible = s["diag"]["Teq_K"] + serre
    taux = (cible - s["T_K"]) / p["tau_T_yr"]
    return {"rates": {"T_K": taux}, "values": {},
            "diag": {"Ttarget_K": cible, "greenhouse_K": serre}}


# Projet 11 : energies annuelles en J/an, reserves en J.
def routine_11(s, p, dt):
    demande = s["population"] * p["need_J_person_yr"]
    renouvelable = min(demande, p["renewable_J_yr"])
    fossile = min(max(0.0, demande - renouvelable),
                  p["fossil_capacity_J_yr"], s["fossil_J"] / dt)
    fourni = renouvelable + fossile
    deficit = (demande - fourni) / demande if demande else 0.0
    emissions = fossile * p["carbon_mol_J"]
    return {"rates": {"fossil_J": -fossile, "co2_mol": emissions,
                       "emitted_c_mol": emissions},
            "values": {}, "diag": {"demand_J_yr": demande,
            "supplied_J_yr": fourni, "deficit_fraction": deficit,
            "power_W": fourni / 31557600}}


# Projet 12 : population moyenne continue, taux en 1/an.
def routine_12(s, p, dt):
    naissances = p["birth_rate_yr"] * s["population"]
    deces = (p["death_rate_yr"] + p["deficit_death_rate_yr"]
             * s["diag"]["deficit_fraction"]) * s["population"]
    return {"rates": {"population": naissances - deces}, "values": {},
            "diag": {"births_yr": naissances, "deaths_yr": deces}}


ROUTINES = {1:routine_1, 2:routine_2, 3:routine_3, 4:routine_4, 5:routine_5, 6:routine_6, 7:routine_7, 8:routine_8, 9:routine_9, 10:routine_10, 11:routine_11, 12:routine_12}
ORDRE = [1, 2, 4, 5, 8, 11, 3, 6, 7, 9, 10, 12]
MODULES = [ROUTINES[i] for i in ORDRE]


def base():
    s = {"time_yr": 0., "T_K": 290., "ice": 0.,
         "co2_mol": 7.49e16, "n2_mol": 1.39e20, "o2_mol": 3.74e19,
         "h2o_mol": 0., "mantle_c_mol": 1e20, "rock_c_mol": 0.,
         "fe_mol": 0., "oxide_fe_mol": 0., "population": 0.,
         "fossil_J": 0., "emitted_c_mol": 0., "diag": {}}
    p = {"g_m_s2": 9.81, "area_m2": 5.10e14, "G": 6.67e-11,
         "kB": 1.38e-23, "NA": 6.02e23, "h": 6.63e-34, "c": 3e8,
         "mass_kg": 5.97e24, "radius_m": 6.371e6, "T_exo_K": 1000.,
         "S_W_m2": 1361., "sigma": 5.67e-8, "pref_Pa": 42.,
         "tau_T_yr": 10., "tau_ice_yr": 20.,
         "water_mode": "mixed_screen", "ocean_prescribed": True,
         "volcanic_mol_yr": 0., "weather_mol_yr": 0.,
         "land_fraction": 1., "co2_ref_mol": 7.49e16,
         "oxygen_mol_yr": 0., "lambda_nm": 255.,
         "ozone_column_mol_m2": .10, "absorption_m2_mol": 100.,
         "need_J_person_yr": 1e9, "renewable_J_yr": 4e11,
         "fossil_capacity_J_yr": 3e11, "carbon_mol_J": 2e-6,
         "birth_rate_yr": 0., "death_rate_yr": 0., "deficit_death_rate_yr": 0.}
    return s, p

def scenario(nom):
    s, p = base()
    duree, dt = 500., 1.
    if nom == "chaude":
        pass
    elif nom == "gelee":
        s.update(T_K=250., ice=1.)
    elif nom == "deglaciation":
        s.update(T_K=250., ice=1.)
        p.update(volcanic_mol_yr=1e13, weather_mol_yr=1e13,
                 tau_T_yr=10000., tau_ice_yr=20000.)
        duree, dt = 1000000., 1000.
    elif nom == "societe":
        s.update(population=1000., fossil_J=1e13)
        p.update(birth_rate_yr=.02, death_rate_yr=.01,
                 deficit_death_rate_yr=.02)
        duree, dt = 100., 1.
    elif nom == "oxygenation":
        s.update(o2_mol=0., fe_mol=40.)
        p.update(oxygen_mol_yr=1.)
        duree, dt = 20., 1.
    else:
        raise ValueError("Scenario inconnu : " + nom)
    return s, p, int(duree / dt), dt

# Projet 13 : le hasard est a l'exterieur du moteur.
from copy import deepcopy
from random import Random


def quantile(valeurs, fraction):
    ordre = sorted(valeurs)
    position = fraction * (len(ordre) - 1)
    i = int(position)
    j = min(i + 1, len(ordre) - 1)
    return ordre[i] + (ordre[j] - ordre[i]) * (position - i)

def ensemble(initial, params, modules, steps, dt, nombre=50, seed=2026,
             bornes=None):
    if nombre < 1:
        raise ValueError("Au moins une simulation")
    if bornes is None:
        bornes = {"tau_T_yr": (5., 15.), "pref_Pa": (30., 60.)}
    rng = Random(seed)
    resultats = {"seed": seed, "samples": [], "histories": [],
                 "summary": {}, "failures": []}
    for _ in range(nombre):
        p = deepcopy(params)
        for cle, (bas, haut) in bornes.items():
            if bas > haut:
                raise ValueError("Bornes inversees")
            p[cle] = rng.uniform(bas, haut)
        resultats["samples"].append(p)
        try:
            h = planet_evolution(initial, p, modules, steps, dt)
            resultats["histories"].append(h)
        except ValueError as erreur:
            resultats["histories"].append(None)
            resultats["failures"].append({"params": p, "error": str(erreur)})
    bonnes = [h for h in resultats["histories"] if h is not None]
    if bonnes:
        T = [h[-1]["T_K"] for h in bonnes]
        resultats["summary"] = {
            "successes": len(T), "q05_T_K": quantile(T, .05),
            "median_T_K": quantile(T, .5), "q95_T_K": quantile(T, .95),
            "frozen_fraction": sum(h[-1]["ice"] > .9 for h in bonnes) / len(T)}
    return resultats


from math import pi
MONDE = {'nom': 'Asteria', 'luminosite_W': 3.828e+26, 'distance_m': 149600000000.0, 'masse_kg': 5.97e+24, 'rayon_m': 6371000.0, 'duree_yr': 5000000000.0, 'stellar_validity_yr': 10000000000.0, 'stellar_initial_ratio': 0.75, 'stellar_final_ratio': 1.0, 'water_kg': 1.4e+21, 'co2_initial_mol': 3e+19, 'n2_mol': 1.39e+20}


ORIGINES = {'1': {'statut': 'référence professeur', 'fichier': 'moteur/modules/gaz.py'}, '2': {'statut': 'référence professeur', 'fichier': 'moteur/modules/retention.py'}, '3': {'statut': 'référence professeur', 'fichier': 'moteur/modules/degazage.py'}, '4': {'statut': 'référence professeur', 'fichier': 'moteur/modules/radiatif.py'}, '5': {'statut': 'référence professeur', 'fichier': 'moteur/modules/eau.py'}, '6': {'statut': 'référence professeur', 'fichier': 'moteur/modules/alteration.py'}, '7': {'statut': 'référence professeur', 'fichier': 'moteur/modules/oxygenation.py'}, '8': {'statut': 'référence professeur', 'fichier': 'moteur/modules/uv.py'}, '9': {'statut': 'référence professeur', 'fichier': 'moteur/modules/glace.py'}, '10': {'statut': 'référence professeur', 'fichier': 'moteur/modules/climat.py'}, '11': {'statut': 'référence professeur', 'fichier': 'moteur/modules/energie.py'}, '12': {'statut': 'référence professeur', 'fichier': 'moteur/modules/demographie.py'}, '13': {'statut': 'référence professeur', 'fichier': 'moteur/ensemble.py'}}


# Ce support est inclus dans le module autonome ; il ne change pas les routines.
from html import escape
import json

def scenario_classe(nom='societe'):
    s,p,n,dt=scenario(nom)
    p.update(S_W_m2=MONDE['luminosite_W']/(4*pi*MONDE['distance_m']**2),
             g_m_s2=6.67e-11*MONDE['masse_kg']/MONDE['rayon_m']**2,
             area_m2=4*pi*MONDE['rayon_m']**2,
             mass_kg=MONDE['masse_kg'],radius_m=MONDE['rayon_m'])
    return s,p,n,dt

def comparer_groupe(groupe,routine,nom='societe'):
    """La routine locale remplace un groupe ; les autres restent communes."""
    s,p,n,dt=scenario_classe(nom)
    if groupe not in ROUTINES:raise ValueError('Groupe 1 à 12 attendu')
    # Banc de raccordement : vérifier la sortie aux mêmes diagnostics que les voisins.
    avec_diag,_=evaluer(s,p,MODULES,dt)
    diagnostic,params=deepcopy(avec_diag),deepcopy(p)
    r=routine(diagnostic,params,dt)
    if diagnostic!=avec_diag or params!=p:raise ValueError('La routine modifie les entrées')
    if set(r)!={'rates','values','diag'} or r['values']:raise ValueError('Contrat incorrect')
    autres=[routine if i==groupe else ROUTINES[i] for i in ORDRE]
    commun=planet_evolution(s,p,MODULES,n,dt)
    local=planet_evolution(s,p,autres,n,dt)
    return {'version_classe':VERSION_CLASSE,'groupe':groupe,'scenario':nom,
            'monde':deepcopy(MONDE),'origines':deepcopy(ORIGINES),
            'commun':commun,'avec_ma_routine':local}

def rapport_comparaison(resultats):
    a=resultats['commun'];b=resultats['avec_ma_routine'];D=a[-1]['time_yr'] or 1
    figures=[]
    for k,titre,unite in [('T_K','Température','K'),('co2_mol','CO2 atmosphérique','mol'),
                          ('ice','Fraction de glace','fraction'),('population','Population moyenne','personnes')]:
        vals=[s[k] for h in [a,b] for s in h];lo,hi=min(vals),max(vals)
        marge=max((hi-lo)*.05,abs(hi)*1e-6,1);lo-=marge;hi+=marge
        if k=='ice':lo,hi=0.,1.
        lines=[]
        for h,color,dash in [(a,'#81949c',' stroke-dasharray="6 4"'),(b,'#126478','')]:
            points=' '.join(f'{80+400*s["time_yr"]/D:.2f},{190-125*(s[k]-lo)/(hi-lo):.2f}' for s in h)
            lines.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"{dash}/>')
        figures.append(f'<svg viewBox="0 0 520 245" role="img" aria-label="{titre}"><text x="80" y="25">{titre} ({unite})</text><path d="M80 60V190H480" stroke="#ccc" fill="none"/><text x="3" y="65">{hi:.4g}</text><text x="3" y="190">{lo:.4g}</text>{"".join(lines)}<text x="80" y="213">0</text><text x="435" y="213">{D:g} ans</text><text x="195" y="240">Temps depuis le début (an)</text></svg>')
    origine=' ; '.join('G'+str(i)+' : '+v['statut'] for i,v in sorted(((int(k),v) for k,v in resultats['origines'].items())))
    return f'''<!doctype html><html lang="fr"><meta charset="utf-8"><title>Notre contribution dans le monde commun</title><style>body{{font:16px/1.5 system-ui;max-width:1000px;margin:30px auto;padding:20px;color:#193442}}svg{{width:100%;font:12px system-ui}}.figures{{display:grid;grid-template-columns:1fr 1fr}}@media print{{button{{display:none}}}}@media(max-width:600px){{.figures{{grid-template-columns:1fr}}}}</style><h1>Notre contribution dans le monde commun</h1><p>Groupe {resultats['groupe']} · scénario {escape(resultats['scenario'])} · monde {escape(resultats['monde']['nom'])} · version commune {escape(resultats['version_classe'])}</p><button onclick="window.print()">Imprimer / PDF</button><p>Bleu : avec notre routine. Gris pointillé : version commune. Toutes les autres routines sont identiques dans les deux calculs.</p><div class="figures">{''.join(figures)}</div><h2>Ce que nous expliquons</h2><p>Notre changement : … ; effet attendu : … ; effet observé : … ; mécanisme : … ; limite : …</p><h2>Versions des contributions</h2><p>{escape(origine)}</p><p>Le cycle hydrologique géologique appartient à l’autre moteur ; ce raccordement annuel n’en simule pas les stocks. Les courbes ne démontrent pas l’habitabilité.</p></html>'''

