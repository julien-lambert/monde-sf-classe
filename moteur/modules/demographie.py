# Projet 12 : population moyenne continue, taux en 1/an.
def step(s, p, dt):
    naissances = p["birth_rate_yr"] * s["population"]
    deces = (p["death_rate_yr"] + p["deficit_death_rate_yr"]
             * s["diag"]["deficit_fraction"]) * s["population"]
    return {"rates": {"population": naissances - deces}, "values": {},
            "diag": {"births_yr": naissances, "deaths_yr": deces}}
