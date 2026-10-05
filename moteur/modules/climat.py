# Projet 10 : loi de serre fictive, Euler explicite.
def step(s, p, dt):
    if dt > p["tau_T_yr"]:
        raise ValueError("dt doit etre <= tau_T_yr")
    co2 = s["diag"]["pco2_Pa"]
    serre = 66 * co2 / (co2 + p["pref_Pa"])
    cible = s["diag"]["Teq_K"] + serre
    taux = (cible - s["T_K"]) / p["tau_T_yr"]
    return {"rates": {"T_K": taux}, "values": {},
            "diag": {"Ttarget_K": cible, "greenhouse_K": serre}}
