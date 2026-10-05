# Projet 11 : energies annuelles en J/an, reserves en J.
def step(s, p, dt):
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
