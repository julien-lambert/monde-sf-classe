# Projet 8 : colonne d'ozone prescrite, coefficient a une longueur d'onde.
from math import exp

def step(s, p, dt):
    photon = p["h"] * p["c"] / (p["lambda_nm"] * 1e-9)
    seuil = 498000 / p["NA"]
    transmission = exp(-p["absorption_m2_mol"] * p["ozone_column_mol_m2"])
    return {"rates": {}, "values": {}, "diag": {
        "photon_J": photon, "dissociation_possible": photon >= seuil,
        "uv_fraction": transmission}}
