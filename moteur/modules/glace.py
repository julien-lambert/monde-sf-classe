# Projet 9 : relaxation vers une couverture de glace fictive.
def step(s, p, dt):
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
