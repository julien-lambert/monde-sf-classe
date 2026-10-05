# Projet 2 : un critere de retention, pas un taux de fuite.
def step(s, p, dt):
    vlib = (2 * p["G"] * p["mass_kg"] / p["radius_m"]) ** .5
    retenus = {}
    for gaz, masse_molaire in {"H2": .002, "N2": .028, "CO2": .044}.items():
        masse = masse_molaire / p["NA"]
        vitesse = (3 * p["kB"] * p["T_exo_K"] / masse) ** .5
        retenus[gaz] = vlib > 6 * vitesse
    return {"rates": {}, "values": {}, "diag": {
        "vlib_m_s": vlib, "retention": retenus}}
