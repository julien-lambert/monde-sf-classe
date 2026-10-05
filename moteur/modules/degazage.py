# Projet 3 : transfert conserve de carbone, mol/an.
def step(s, p, dt):
    flux = min(p["volcanic_mol_yr"], s["mantle_c_mol"] / dt)
    return {"rates": {"co2_mol": flux, "mantle_c_mol": -flux},
            "values": {}, "diag": {"volcanic_actual_mol_yr": flux}}
