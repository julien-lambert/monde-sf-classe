# Projet 13 : le hasard est a l'exterieur du moteur.
from copy import deepcopy
from random import Random
from engine import planet_evolution

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
