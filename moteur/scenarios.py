"""Tous les chiffres de scenario sont visibles ici. Lois pedagogiques."""
from modules import gaz, retention, radiatif, eau, uv, energie
from modules import degazage, alteration, oxygenation, glace, climat, demographie

MODULES = [gaz.step, retention.step, radiatif.step, eau.step, uv.step,
           energie.step, degazage.step, alteration.step, oxygenation.step,
           glace.step, climat.step, demographie.step]

def base():
    s = {"time_yr": 0., "T_K": 290., "ice": 0.,
         "co2_mol": 7.49e16, "n2_mol": 1.39e20, "o2_mol": 3.74e19,
         "h2o_mol": 0., "mantle_c_mol": 1e20, "rock_c_mol": 0.,
         "fe_mol": 0., "oxide_fe_mol": 0., "population": 0.,
         "fossil_J": 0., "emitted_c_mol": 0., "diag": {}}
    p = {"g_m_s2": 9.81, "area_m2": 5.10e14, "G": 6.67e-11,
         "kB": 1.38e-23, "NA": 6.02e23, "h": 6.63e-34, "c": 3e8,
         "mass_kg": 5.97e24, "radius_m": 6.371e6, "T_exo_K": 1000.,
         "S_W_m2": 1361., "sigma": 5.67e-8, "pref_Pa": 42.,
         "tau_T_yr": 10., "tau_ice_yr": 20.,
         "water_mode": "mixed_screen", "ocean_prescribed": True,
         "volcanic_mol_yr": 0., "weather_mol_yr": 0.,
         "land_fraction": 1., "co2_ref_mol": 7.49e16,
         "oxygen_mol_yr": 0., "lambda_nm": 255.,
         "ozone_column_mol_m2": .10, "absorption_m2_mol": 100.,
         "need_J_person_yr": 1e9, "renewable_J_yr": 4e11,
         "fossil_capacity_J_yr": 3e11, "carbon_mol_J": 2e-6,
         "birth_rate_yr": 0., "death_rate_yr": 0., "deficit_death_rate_yr": 0.}
    return s, p

def scenario(nom):
    s, p = base()
    duree, dt = 500., 1.
    if nom == "chaude":
        pass
    elif nom == "gelee":
        s.update(T_K=250., ice=1.)
    elif nom == "deglaciation":
        s.update(T_K=250., ice=1.)
        p.update(volcanic_mol_yr=1e13, weather_mol_yr=1e13,
                 tau_T_yr=10000., tau_ice_yr=20000.)
        duree, dt = 1000000., 1000.
    elif nom == "societe":
        s.update(population=1000., fossil_J=1e13)
        p.update(birth_rate_yr=.02, death_rate_yr=.01,
                 deficit_death_rate_yr=.02)
        duree, dt = 100., 1.
    elif nom == "oxygenation":
        s.update(o2_mol=0., fe_mol=40.)
        p.update(oxygen_mol_yr=1.)
        duree, dt = 20., 1.
    else:
        raise ValueError("Scenario inconnu : " + nom)
    return s, p, int(duree / dt), dt
