# Projet 4 : equilibre radiatif sans serre.
def step(s, p, dt):
    albedo = .30 + .30 * s["ice"]
    absorbe = p["S_W_m2"] * (1 - albedo) / 4
    temperature = (absorbe / p["sigma"]) ** .25
    return {"rates": {}, "values": {}, "diag": {
        "albedo": albedo, "absorbed_W_m2": absorbe, "Teq_K": temperature}}
