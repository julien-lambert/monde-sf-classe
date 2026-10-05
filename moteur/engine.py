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
