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

def step(s, p, dt):
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
