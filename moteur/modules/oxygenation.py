# Projet 7 : flux externe O2, puits fini de Fe ; stocks en mol.
def step(s, p, dt):
    production = p["oxygen_mol_yr"]
    utilise = min(s["o2_mol"] + production * dt, s["fe_mol"] / 4)
    return {"rates": {"o2_mol": production - utilise / dt,
                       "fe_mol": -4 * utilise / dt,
                       "oxide_fe_mol": 4 * utilise / dt},
            "values": {}, "diag": {"oxygen_used_mol_yr": utilise / dt}}
