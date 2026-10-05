# Projet 6 : une loi fictive locale, transfert CO2 -> roches.
def step(s, p, dt):
    flux = 0.0
    if s["diag"]["ocean_possible"] is True:
        chaleur = max(0.0, 1 + (s["T_K"] - 288) / 50)
        flux = (p["weather_mol_yr"] * p["land_fraction"]
                * (1 - s["ice"]) * chaleur
                * s["co2_mol"] / p["co2_ref_mol"])
    flux = min(flux, s["co2_mol"] / dt)
    return {"rates": {"co2_mol": -flux, "rock_c_mol": flux},
            "values": {}, "diag": {"weather_actual_mol_yr": flux}}
