# Projet 1 : stocks en mol, pressions en Pa.
def step(s, p, dt):
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
