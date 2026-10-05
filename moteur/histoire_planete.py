"""Maquette de temps long : eau conservée, carbone conservé, climat rapide.
Les fonctions sont courtes et les hypothèses explicites. Ce n'est pas une
reconstruction de la Terre. Les flux d'eau rapides sont intégrés exactement.
"""
from math import exp, isfinite

DUREE = 4.031e9  # début de l'Archeen arrondi, jusqu'au présent
PARAMS = {'water_kg': 1.4e21, 'carbon_mol': 1e23,
          'co2_initial_mol': 3e19, 'volcanic_mol_yr': 1e13,
          'weather_mol_yr': 1e13, 'co2_ref_mol': 7.49e16,
          'pref_Pa': 42., 'rain_ref_kg_yr': 5e17,
          'vapor_tau_yr': .02, 'area_m2': 5.10e14,
          'weather_feedback': True, 'ice_feedback': True,
          'water_feedback': True, 'solar_evolution': True}

def climat(co2, vapor, soleil, precedent, p):
    """Climat rapide à CO2 fixé ; la branche dépend de l'état précédent."""
    T = precedent
    for _ in range(400):
        ice = max(0., min(1., (283-T)/20)) if p['ice_feedback'] else 0.
        albedo = .30 + .30*ice
        teq = (soleil*(1-albedo)/4/5.67e-8)**.25
        # Approximation de la pression de CO2 : fond N2 moderne fixe.
        mass = co2*.044 + p.get('n2_mol',1.39e20)*.028 + vapor
        P = mass*p.get('gravity_m_s2',9.81)/p['area_m2']
        pco2 = P*co2/(co2+p.get('n2_mol',1.39e20)+vapor/.018)
        serre = 66*pco2/(pco2+p['pref_Pa'])
        cible = teq+serre
        if abs(cible-T) < 1e-8:
            return cible, ice, pco2, albedo
        T = .5*(T+cible)
    raise ValueError('Climat rapide non convergé')

def hydrologie(T, ice, vapor, dt, p):
    """Atmosphère <-évaporation-- océan ; atmosphère --pluie/neige-> surface.
    Le stock vapeur suit dV/dt=E-V/tau, intégré exactement. Les précipitations
    sont obtenues par bilan, sans des milliards de petits pas annuels.
    La fraction ice partitionne la surface eau/glace, sans créer d'eau.
    """
    ouvert = max(0., 1-ice)
    facteur = max(.05, min(3., exp((T-288)/30)))
    E = p['rain_ref_kg_yr']*ouvert*facteur
    cible = min(E*p['vapor_tau_yr'], p['water_kg'])
    nouveau = cible+(vapor-cible)*exp(-dt/p['vapor_tau_yr'])
    P = E-(nouveau-vapor)/dt
    surface = p['water_kg']-nouveau
    return {'vapor_kg':nouveau,'ocean_kg':surface*(1-ice),
            'ice_kg':surface*ice,'evap_kg_yr':E,
            'precip_kg_yr':P,'rain_mm_yr':P*(1-ice)/p['area_m2'],
            'snow_mm_yr':P*ice/p['area_m2']}

def carbone(C, manteau, roches, T, ice, rain, land, dt, p):
    """dC/dt=F-kC ; solution exacte pour k et F figés sur le pas.
    Transfert identique vers les roches, et prélèvement dans le manteau.
    """
    F = min(p['volcanic_mol_yr'], manteau/dt)
    if p['weather_feedback']:
        chaleur = max(0., 1+(T-288)/50)
        pluie = rain/p['rain_ref_kg_yr'] if p['water_feedback'] else 1.
        k = p['weather_mol_yr']/p['co2_ref_mol']*land*chaleur*pluie*(1-ice)
    else:
        k = 0.
    if k > 0:
        r = exp(-k*dt)
        nouveau = C*r+F/k*(1-r)
    else:
        nouveau = C+F*dt
    transfert = C+F*dt-nouveau
    return nouveau, manteau-F*dt, roches+transfert, transfert/dt

def simuler(p=None, dt=1e6, duree=DUREE):
    p = dict(PARAMS, **(p or {}))
    if not isfinite(dt) or dt<=0 or not 0<duree<=p.get('stellar_validity_yr',1e10):
        raise ValueError('Pas/durée invalide')
    for key in ['water_kg','carbon_mol','co2_ref_mol','pref_Pa','vapor_tau_yr','area_m2','rain_ref_kg_yr']:
        if not isfinite(p[key]) or p[key]<=0: raise ValueError('Paramètre positif requis : '+key)
    if not 0<=p['co2_initial_mol']<=p['carbon_mol']: raise ValueError('Stock initial CO2 invalide')
    for key in ['volcanic_mol_yr','weather_mol_yr']:
        if not isfinite(p[key]) or p[key]<0: raise ValueError('Flux invalide')
    C=p['co2_initial_mol']; M=p['carbon_mol']-C; R=0.; V=1e16; T=300.; t=0.
    h=[]
    pas_adaptatif=min(dt,100.)
    while True:
        fraction=t/duree
        flux=p.get('stellar_flux_W_m2',1361.)
        debut=p.get('stellar_initial_ratio',.75)
        fin=p.get('stellar_final_ratio',1.)
        soleil=flux*(debut+(fin-debut)*fraction) if p['solar_evolution'] else flux
        land=.15+.85*fraction  # efficacité relative d'altération, hypothèse imposée
        T,ice,pc,A=climat(C,V,soleil,T,p)
        # Diagnostics instantanés de pluie E=V/tau après relaxation rapide.
        eau=hydrologie(T,ice,V,1.,p)
        point={'time_yr':t,'age_Ga':(duree-t)/1e9,'T_K':T,'ice':ice,
               'co2_mol':C,'mantle_c_mol':M,'rock_c_mol':R,
               'pco2_Pa':pc,'albedo':A,'solar_W_m2':soleil,'land_factor':land,
               'vapor_kg':V,'ocean_kg':(p['water_kg']-V)*(1-ice),
               'ice_kg':(p['water_kg']-V)*ice,
               'evap_kg_yr':eau['evap_kg_yr'],
               'precip_kg_yr':V/p['vapor_tau_yr'],
               'rain_mm_yr':V/p['vapor_tau_yr']*(1-ice)/p['area_m2'],
               'snow_mm_yr':V/p['vapor_tau_yr']*ice/p['area_m2']}
        for k,v in point.items():
            if not isfinite(v) or v < -1e-6: raise ValueError('État invalide : '+k)
        h.append(point)
        if t>=duree: break
        pas=min(pas_adaptatif,duree-t)
        pas_adaptatif=min(dt,pas_adaptatif*1.05)
        fluxeau=hydrologie(T,ice,V,pas,p)
        C,M,R,W=carbone(C,M,R,T,ice,fluxeau['precip_kg_yr'],land,pas,p)
        # Moyennes sur [t,t+pas] séparées des diagnostics instantanés.
        point['interval_evap_kg_yr']=fluxeau['evap_kg_yr']
        point['interval_precip_kg_yr']=fluxeau['precip_kg_yr']
        point['interval_weather_mol_yr']=W
        V=fluxeau['vapor_kg']; t+=pas
    return h
