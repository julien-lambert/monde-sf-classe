# Construire un monde SF en Terminale

Vous construisez un monde fictif commun. Vous choisissez une étoile, une distance orbitale et une planète. Les mécanismes sont fournis : votre travail est de comprendre les relations, écrire un calcul manuel, coder une fonction, vérifier, tracer puis expliquer son effet collectif.

Les exemples Terre, Mars et Vénus ci-dessous servent à contrôler les calculs. Ils ne définissent ni la chronologie ni l'identité de votre monde. Chaque formule portant la mention « hypothèse pédagogique » est une loi de cette maquette, pas une vérité universelle.

40 élèves : 12 groupes de trois et un groupe de quatre. Chaque groupe conserve sa fiche et livre sa routine, trois essais justifiés et un graphique commenté. Le moteur de référence contient les corrigés simples pour vérifier et raccorder les contributions. Les rôles tournent ; chacun explique une formule et une vérification.

## Choisir les paramètres du monde

Les formules suivantes sont fournies pour le projet 4 et le moteur commun.

Flux reçu : S = L / (4 π d²). L est la luminosité de l'étoile (W), d la distance orbitale (m), S le flux reçu (W/m²). Orbite circulaire fixe, émission isotrope. Doubler d divise S par quatre. Exemple : L = 3,828 × 10²⁶ W et d = 1,496 × 10¹¹ m donnent environ 1361 W/m².

Surface : Aplanète = 4 π R² (m²). Gravité : g = G M/R² (m/s²), avec G = 6,67 × 10⁻¹¹ en SI, M masse (kg), R rayon (m). Exemple M = 5,97 × 10²⁴ kg et R = 6,371 × 10⁶ m : g ≈ 9,81 m/s². Réutiliser ces valeurs dans le module gaz.

Évolution stellaire fournie : S(t) = S0 × [a + (b − a)t/D]. a et b sont des rapports sans unité ; D la durée du scénario. Cette évolution linéaire est une hypothèse choisie. La durée de validité du scénario stellaire est fournie, sans évolution détaillée des étoiles ni changement de spectre UV automatique.

Modifier monde_sf.json puis lancer python3 construire_histoire.py. Le graphique sélectionne les 16 simulations recalculées. Les autres routines du moteur annuel utilisent leurs propres paramètres dans scenarios.py ; ne pas confondre les deux moteurs. Pour appliquer un monde au moteur annuel : calculer S, g, la surface, puis les reporter dans ses paramètres, ainsi que masse et rayon pour la rétention.

## Le contrat commun et la méthode

Fonction step(state, params, dt_yr). Retour exact : {"rates": {...}, "values": {}, "diag": {...}}. Les rates sont les variations par an ; values reste vide ; diag contient les grandeurs calculées. Le moteur additionne les taux et applique nouvelle valeur = ancienne valeur + dt × taux. Une fonction ne modifie pas les dictionnaires reçus.

La température est en K, les gaz en mol, les pressions en Pa, les réserves d'énergie en J. 1 bar = 100 000 Pa. 1 an = 31 557 600 s. Les flux sont en mol/an ou J/an. Le cycle hydrologique géologique emploie des stocks en kg, séparés des stocks molaires du moteur annuel ; conversion de vapeur : mol = kg/0,018.

Le groupe commence avec les diagnostics de substitution fournis dans sa fiche. Une routine peut être écrite seule même si elle lit ensuite une sortie d'un autre groupe. Avant raccordement : relire le calcul, vérifier le résultat connu, le cas limite, la variation attendue et les noms exacts. Retirer les diagnostics artificiels après raccordement.

L'ordre du moteur annuel est gaz, rétention, radiatif, eau, UV, énergie, dégazage, altération, oxygénation, glace, climat, démographie. Monte-Carlo appelle le moteur depuis l'extérieur.

Ajouts exacts au corrigé : le projet 11 rend aussi rates emitted_c_mol pour suivre les émissions cumulées ; ce compteur commence à zéro. Le projet 10 rend aussi diag greenhouse_K. Le projet 5 annuel rend water_domain et saturation_Pa. Consulter la carte des contrats dans COORDINATION_CLASSE.md.

Le pas variable du moteur géologique croît progressivement ; il ne garantit pas à lui seul une précision locale. Les essais de pas divisé par deux sont obligatoires pour un scénario modifié. Un contrôle automatique par un pas complet et deux demi-pas est une amélioration prévue, pas une fonctionnalité déjà livrée.

## Projet 1 Mesurer une atmosphère

**Question.** Pourquoi 95 % de CO2 sur Mars représentent-ils moins de CO2 que 96,5 % sur Vénus ? **Ancrage :** document 1, § 14–15, Dalton F4. Calcul direct accessible à tous.

**Entrées.** state : co2_mol, n2_mol, o2_mol, h2o_mol ; params : g_m_s2, area_m2 et masses molaires. Pour un premier exercice séparé, utiliser les pressions totales et fractions du tableau ci-dessous.

**Modèle.** Calculer la masse totale, puis P = masse × g/surface. Calculer chaque fraction molaire et chaque pression partielle. Si le stock total est nul, retourner P = 0, toutes les pressions nulles et des fractions nulles, sans division par zéro.

**Sorties.** diag : P_Pa, pco2_Pa, po2_Pa, ph2o_Pa, fractions, ce dernier dictionnaire ayant les clés CO2, N2, O2, H2O. Aucun taux. Ne jamais stocker un pourcentage à la place d’une fraction.

| Planète | P en bar | Fraction de CO2 | pCO2 attendu en bar |
|---|---|---|---|
| Vénus | 92 | 0,965 | 88,78 |
| Terre | 1 | 0,00042 | 0,00042 |
| Mars | 0,006 | 0,95 | 0,0057 |

**Travail.** Refaire les trois produits à la main ; implémenter la routine ; tester un mélange de 1 mol de CO2 et 1 mol de N2 ; tracer les trois pressions partielles avec un axe logarithmique si nécessaire.

**Validation.** Les fractions et les pressions partielles doivent respectivement sommer à 1 et P pour une atmosphère non vide. Dans le mélange 1 + 1 mol, les pressions partielles sont égales malgré les masses différentes. Doubler tous les stocks double P.

**Rendu.** Routine gaz.py, diagramme comparatif et trois phrases sur la différence entre proportion et quantité. **Prolongement :** relier une atmosphère de CO2 pur à 1,4e6 Gt C par bar ; expliquer pourquoi cette conversion du cours ne s’applique pas telle quelle au mélange terrestre.

## Projet 2 Garder ou perdre un gaz

**Question.** Une planète peut-elle garder H2, N2 ou CO2 ? **Ancrage :** document 1, § 3–8, F1 et F2 fournies non exigibles. Calcul direct et balayage.

**Entrées.** params : G, kB, NA, mass_kg, radius_m, T_exo_K ; liste des masses molaires H2, N2, CO2. L’état est lu mais ne change pas.

**Modèle.** `vlib = (2 * G * M/R)**0.5` ; m = masse_molaire/NA ; `v = (3 * kB * T/m)**0.5`. Le critère pédagogique est vlib > 6 × v. Il classe un gaz comme retenu dans ce modèle thermique ; il ne fournit ni une durée ni une quantité perdue.

**Sorties.** diag : vlib_m_s ; retention, dictionnaire de booléens par gaz. Aucun rates. La température utilisée doit être clairement affichée dans le compte rendu.

**Données.** Terre : 5,97e24 kg, 6,371e6 m ; Mars : 6,42e23 kg, 3,390e6 m. Les masses sont des valeurs usuelles ajoutées au tableau fourni, dont les lignes numériques en kg sont vides dans le PDF. Comparer d’abord 288 K et 210 K, comme le cours, puis 1000 K pour la Terre.

**Travail.** Calculer vlib ; comparer les trois gaz ; tracer 6v en fonction de T de 200 à 1500 K ; superposer vlib. Aucune simulation moléculaire n’est nécessaire.

**Validation.** Terre : vlib environ 11,2 km/s ; Mars : environ 5,03 km/s. À 288 K, 6v pour H2 terrestre vaut environ 11,4 km/s ; à 1000 K, N2 reste retenu selon le critère. Un doublement de M multiplie vlib par racine de 2.

**Rendu.** Routine retention.py et graphique annoté. **Limite à expliquer :** le modèle laisse de côté les mécanismes non thermiques et ne suffit pas à expliquer l’histoire de Mars. Un futur module de fuite devra avoir une loi de flux distincte, documentée.

## Projet 3 Les volcans remplissent un réservoir

**Question.** Combien de CO2 peut entrer dans l’atmosphère sans inventer du carbone ? **Ancrage :** document 1, § 9–13 ; document 5, réservoirs. Suite et conservation.

**Entrées.** state : mantle_c_mol, co2_mol ; params : volcanic_mol_yr. dt_yr doit être strictement positif. Les sorties N2 et vapeur du dégazage réel restent pour un prolongement avec réserves explicites.

**Modèle minimal.** Le flux F demandé est constant. Le flux réellement transféré est min(F, mantle_c_mol/dt_yr). Une mole de carbone du manteau devient une mole de CO2 atmosphérique. Notre réservoir est une réserve mobilisable fictive, pas tout le carbone réel du manteau.

**Sorties.** rates : co2_mol = +F_effectif, mantle_c_mol = −F_effectif. diag peut rester vide. Le moteur applique les deux taux ensemble.

**Données d’essai.** Stock du manteau : 100 mol ; CO2 : 0 mol ; F = 10 mol/an ; dt = 1 an. Utiliser de petites valeurs pour voir le bilan, puis changer d’échelle. Pour une expérience géologique fictive : 1e20 mol mobilisables et F = 1e13 mol/an.

**Travail.** Simuler 15 ans ; produire la courbe des deux réservoirs ; augmenter dt ; supprimer le flux. Ne pas appeler l’horloge depuis la routine.

**Validation.** Après 5 ans dans l’essai, les stocks valent 50 et 50 mol. Après 10 ans, le manteau est épuisé et le CO2 vaut 100 mol. Leur somme reste 100. Si dt = 20 ans, le transfert maximal reste 100 mol.

**Rendu.** Routine degazage.py, courbes et bilan de conservation. **Prolongement ⊕⊕ :** argon issu du potassium avec la loi de demi-vie du cours et la branche de 10,7 % ; créer des stocks distincts plutôt que d’ajouter l’argon au carbone.

## Projet 4 Le Soleil chauffe la planète

**Question.** Quelle température obtient-on avant de représenter l’effet de serre ? **Ancrage :** document 3, § 20–23, F5 ; document 9, § 44. Calcul direct.

**Entrées.** state : ice ; params : S_W_m2, sigma. Paramètres d’albédo : surface libre 0,30, surface englacée 0,60, valeurs du cours.

**Modèle.** A = 0,30 + 0,30 × ice ; flux absorbé moyen = S × (1 − A)/4 ; `Teq = (flux_absorbe/sigma)**0.25`. Le facteur 4 vient du rapport entre disque interceptant la lumière et surface de la sphère. L’interpolation d’albédo est notre choix pédagogique.

**Sorties.** diag : albedo, absorbed_W_m2, Teq_K. Aucun taux de température : cette sortie décrit un équilibre radiatif, pas la température instantanée de surface.

**Données.** S = 1361 W/m² ; sigma = 5,67e−8 W/m²/K⁴. Soleil jeune : S = 0,71 × 1361. Terre libre de glace : ice = 0 ; entièrement englacée : ice = 1.

**Travail.** Effectuer les trois calculs du cours ; tracer Teq selon S et ice ; comparer 254,6 K au 288 K observé. Ne pas ajouter automatiquement 33 K à toutes les planètes : c’est un écart terrestre actuel, pas une constante universelle.

**Validation.** Actuel libre de glace : environ 254,6 K ; Soleil jeune : environ 233,7 K ; actuel englacé : environ 221,4 K. Flux absorbé actuel libre : 238,2 W/m². Si A augmente, Teq diminue.

**Rendu.** Routine radiatif.py et graphique. Une phrase doit distinguer température d’équilibre sans serre et température de surface. **Prolongement :** définir S = 1361/distance_UA² pour comparer les distances ; l’albédo terrestre n’est alors qu’une hypothèse.

## Projet 5 Quand un océan devient possible

**Question.** Pourquoi ne suffit-il pas de dire « il fait moins de 100 °C » ? **Ancrage :** document 3, § 16–19, diagramme d’état. Lecture et interpolation.

**Entrées.** state : T_K ; diag : P_Pa, ph2o_Pa ; params : water_mode, choisi « pure_demo » ou « mixed_screen ». La routine ne retire aucun stock de vapeur.

**Données de frontière.** P en bar : 1, 10, 60, 100 ; températures d’ébullition arrondies en °C : 100, 180, 275, 311. Le point à 60 bar reprend la lecture du cours ; les autres valeurs arrondies sont ajoutées pour l’exercice. Les interpolations sont approximatives. Pas d’extrapolation hors 1–100 bar. Point triple : 0,01 °C et 610 Pa ; point critique : 374 °C et 221 bar.

**Modèle minimal.** En mode pure_demo, interpoler la température d’ébullition selon P et classer liquide si 273,15 K < T < Teb ; vapeur au-dessus ; frontière si égalité ; glace sous 273,15 K. C’est une approximation de l’eau pure limitée au domaine annoncé. Hors domaine, renvoyer « indetermine ».

**Mode du moteur.** En mélange, fixer ocean_possible = True seulement si T > 273,15 K et si ph2o_Pa dépasse la pression de saturation interpolée à T entre 100 et 311 °C. Aux autres températures, renvoyer None et water_domain = « indetermine ». Le test signale une possibilité de condensation, pas la quantité d’eau liquide. L’altération n’utilise True que dans ce domaine ou une valeur imposée explicitement par le scénario tempéré.

**Sorties.** diag : water_domain et ocean_possible. Aucun rates. En scénario tempéré, le professeur peut fournir un substitut « océan présent » avant l’assemblage du modèle de mélange.

**Validation.** Eau pure à 200 °C et 100 bar : liquide ; à 200 °C et 1 bar : vapeur. Tester une entrée hors domaine. Deux mélanges de même P et T mais de ph2o différent ne doivent pas être automatiquement classés de la même façon.

**Rendu.** Routine eau.py, diagramme et comparaison des deux modes. **Prolongement :** ajouter une table de saturation à basse température, puis un réservoir océanique conservant h2o total lors des transferts.

## Projet 6 Les roches retirent du carbone de l’air

**Question.** Une pompe à CO2 peut-elle stabiliser la planète ? **Ancrage :** document 5, § 24–31, F6 et rétroaction négative. Flux et conditions.

**Entrées.** state : T_K, ice, co2_mol ; diag : ocean_possible ; params : weather_mol_yr, land_fraction, co2_ref_mol. Données isolées : imposer ocean_possible = True pour tester la routine sans le groupe 5.

**Modèle ajouté.** F = F0 × land_fraction × (1 − ice) × max(0, 1 + (T − 288)/50) × co2_mol/co2_ref_mol si l’océan est possible ; sinon F = 0. Tous les facteurs sont sans unité. F0 est en mol/an. Limiter F à co2_mol/dt. Le facteur thermique est une approximation locale, pas une loi chimique du cours.

**Bilan chimique.** CaSiO3 + CO2 → CaCO3 + SiO2. Vérifier Ca, Si, C et O. Dans notre modèle de réservoirs, une mole de CO2 retirée ajoute une mole de carbone aux roches. Eau et pluie sont des conditions de fonctionnement ; elles ne sont pas encore des variables de flux.

**Sorties.** rates : co2_mol = −F, rock_c_mol = +F. Les volcans et les émissions peuvent ajouter du CO2, mais l’altération n’utilise que le stock atmosphérique du début de pas.

**Données.** Essai : CO2 = 100 mol, référence = 100 mol, F0 = 10 mol/an, land_fraction = 1, T = 288 K, ice = 0, dt = 1 an. Le premier transfert vaut 10 mol.

**Validation.** Sans océan, aucun transfert. Sous glace totale, aucun transfert. La somme carbone atmosphérique + roches est conservée par cette routine. À paramètres fixés, une hausse modérée de T accroît F.

**Rendu.** Routine alteration.py et chaîne causale complète. **Prolongement :** coupler au dégazage constant et chercher un état où les flux s’équilibrent ; annoncer l’échelle temporelle choisie, sans faire agir le thermostat géologique instantanément sur une société.

## Projet 7 Un puits retarde l’oxygénation

**Question.** Pourquoi produire du O2 ne signifie-t-il pas en accumuler dans l’air ? **Ancrage :** document 7, § 36–41, F7 et F8. Puits fini et bilan.

**Entrées.** state : fe_mol, oxide_fe_mol, o2_mol ; params : oxygen_mol_yr ; dt_yr. Le flux de production est imposé. Il remplace provisoirement un futur module vivant.

**Modèle.** Pendant dt, apport = production × dt. Le puits consomme used = min(o2_mol + apport, fe_mol/4). Consommer 1 mol de O2 oxyde 4 mol de Fe2+. Le bilan aqueux peut s’écrire 4 Fe2+ + O2 + 4 H2O → 2 Fe2O3 + 8 H+. Nous suivons les atomes de Fe transférés ; eau et acidité ne sont pas simulées.

**Sorties.** rates : o2_mol = production − used/dt ; fe_mol = −4 × used/dt ; oxide_fe_mol = +4 × used/dt. oxide_fe_mol compte des moles de Fe, pas des moles de Fe2O3. Le stock de O2 est réparti dans un réservoir global simplifié, sans transport atmosphère-océan.

**Données.** Fe initial = 40 mol ; O2 initial = 0 ; Fe oxydé = 0 ; production = 1 mol/an ; dt = 1 an. Le puits représente une capacité fictive, pas une datation réelle de la Grande Oxydation.

**Travail.** Simuler 20 ans et tracer O2, Fe dissous et Fe oxydé. Recommencer avec 80 mol de Fe. Expliquer le changement de délai.

**Validation.** Jusqu’à 10 ans, O2 reste nul ; ensuite il s’accumule. À 15 ans, O2 = 5 mol et Fe oxydé = 40 mol. Fe dissous + oxydé reste constant. Production nulle et stocks nuls donnent des taux nuls.

**Rendu.** Routine oxygenation.py, figure et trois indices géologiques du cours. **Prolongement :** relier une production prescrite au bilan 6 CO2 + 6 H2O → C6H12O6 + 6 O2 avec un réservoir organique ; prévoir aussi la respiration avant d’affirmer un bilan fermé.

## Projet 8 Une atmosphère filtre les UV

**Question.** Comment distinguer photons capables de dissocier O2 et UV transmis au sol ? **Ancrage :** document 11, § 50–53 ; Chapman et calcul photonique en ouverture. Calcul direct.

**Entrées.** params : lambda_nm, ozone_column_mol_m2, absorption_m2_mol, h, c, NA. state et son O2 peuvent être affichés pour le contexte, mais ne déterminent pas encore la colonne d’ozone.

**Modèle photonique.** E = h × c/(lambda_nm × 1e−9). Une liaison O=O nécessite 498 000/NA J. dissociation_possible indique E supérieur ou égal à ce seuil. Cela ne calcule pas une vitesse de production d’ozone.

**Filtrage pédagogique.** À une longueur d’onde choisie, tau = absorption_m2_mol × ozone_column_mol_m2 ; uv_fraction = exp(−tau). Si l’exponentielle n’est pas maîtrisée, math.exp est une fonction fournie que l’on explore avec un tableau ; aucune résolution analytique n’est demandée. Cette loi d’atténuation est ajoutée au cours.

**Sorties.** diag : photon_J, dissociation_possible, uv_fraction. Aucun taux. La colonne d’ozone est prescrite, non calculée à partir du seul stock de O2. Ne pas utiliser un coefficient unique pour tout le spectre.

**Données fictives d’absorption à une seule longueur d’onde.** Colonne 0, 0,01 ou 0,10 mol/m² ; coefficient 100 m²/mol. Pour le seuil de dissociation : 240, 255, 300 nm, avec les constantes du cours.

**Validation.** Colonne nulle : transmission 1 ; tau = 1 : environ 0,368 ; tau = 10 : environ 4,54e−5. Le seuil photonique est environ 240 nm avec les constantes arrondies du cours, proche des 242 nm annoncés. Un photon de 255 nm est sous ce seuil.

**Rendu.** Routine uv.py, courbe de transmission et distinction entre dissociation et absorption. **Prolongement :** tableau spectral dépendant de lambda ; chimie de Chapman dynamique réservée à une phase ultérieure.

## Projet 9 La glace change l’albédo

**Question.** Comment le froid peut-il s’amplifier ? **Ancrage :** document 9, § 43–49 ; systèmes dynamiques en ouverture. Suite récurrente.

**Entrées.** state : T_K, ice ; params : tau_ice_yr. L’albédo sera calculé par le projet 4 au prochain pas ; cette routine ne le produit pas elle-même.

**Modèle ajouté.** ice_target = 1 si T ≤ 263 K ; 0 si T ≥ 283 K ; sinon (283 − T)/20. Rate ice = (ice_target − ice)/tau_ice_yr. Les seuils et le temps de réponse sont fictifs. Pour un pas monotone et borné, choisir dt ≤ tau_ice_yr. Aucun min/max final ne doit dissimuler un pas trop grand.

**Sorties.** rates : ice. Aucun diagnostic nécessaire. Le moteur calcule ice_nouveau ; le projet 4 relit cette fraction au pas suivant.

**Données.** T = 260 K ; ice initial = 0 ; tau_ice = 20 ans ; dt = 1 an. Pour une première expérience isolée, garder T constant. Pour la seconde, raccorder radiatif et climat.

**Travail.** Tracer l’installation de la glace à 260 K et sa disparition à 290 K. Comparer dt = 1, 5 et 30 ans. Écrire la chaîne T diminue → glace augmente → albédo augmente → énergie absorbée diminue → T diminue.

**Validation.** Premier pas froid : ice = 0,05. Une cible égale à la fraction initiale donne un taux nul. Pour dt ≤ tau, ice reste entre son ancienne valeur et la cible. Avec dt = 30 ans et ice = 0, le modèle demande 1,5 : le moteur doit refuser ce pas.

**Rendu.** Routine glace.py, courbes et démonstration du signe de la rétroaction. **Prolongement :** avec le groupe 10, rechercher des états stables chaud et froid pour les mêmes paramètres. Leur existence dépend des lois choisies ; elle n’est pas garantie par le mot « attracteur ».

## Projet 10 Faire évoluer la température

**Question.** Le résultat dépend-il du pas de temps ou de l’état initial ? **Ancrage :** bilan radiatif et rétroactions des documents 3, 5 et 9. Euler explicite fourni.

**Entrées.** state : T_K ; diag : Teq_K, pco2_Pa ; params : pref_Pa, tau_T_yr. Pour travailler seul, fixer Teq = 254,6 K et pCO2 = pref = 42 Pa.

**Modèle pédagogique de serre.** delta_serre = 66 × pCO2/(pCO2 + pref) ; Ttarget = Teq + delta_serre. Il vaut 33 K lorsque pCO2 = pref. C’est une loi fictive, bornée et commode pour illustrer un couplage ; elle ne décrit pas Vénus ni une atmosphère à 60 bar.

**Dynamique.** rate T_K = (Ttarget − T_K)/tau_T_yr. C’est une relaxation vers une cible, pas un modèle climatique complet. Le moteur applique T_nouveau = T + dt × rate. Pour rester entre T et la cible à paramètres figés, dt ≤ tau_T. Pour étudier la stabilité, comparer des pas plus grands, sans les utiliser pour les expériences finales.

**Sorties.** diag : Ttarget_K ; rates : T_K. Teq reste un diagnostic du groupe 4. Le modèle ne prétend pas convertir la consommation énergétique humaine directement en cette température.

**Données.** T initial = 260 K ; tau_T = 10 ans ; dt = 1 an ; cible fixe = 287,6 K. Au premier pas, T devient 262,76 K. Essais à dt = 0,5, 1 et 2 ans sur la même durée de 100 ans.

**Validation.** Si T = cible, taux nul. Sans CO2, delta_serre = 0. Si dt = tau, une relaxation à cible fixe rejoint la cible en un pas. Une convergence du calcul ne prouve pas la validité physique de la loi.

**Rendu.** Routine climat.py, figure comparant les pas et deux états initiaux. **Prolongement :** remplacer la relaxation par C × dT/dt = flux absorbé − epsilon × sigma × T⁴ ; C en J/m²/K impose de convertir dt en secondes.

## Projet 11 Une société demande de l’énergie

**Question.** Comment relier besoins, production, réserves et émissions ? **Ancrage :** extension énergie demandée, sans chapitre correspondant dans l’archive. Bilan dimensionnel.

**Entrées.** state : population, fossil_J ; params : need_J_person_yr, renewable_J_yr, fossil_capacity_J_yr, carbon_mol_J. Le coefficient carbone est en mol de C par joule ; une mole de C émise devient une mole de CO2.

**Modèle.** Demande D = population × besoin individuel. Fourniture renouvelable R = min(D, capacité_renouvelable). Fourniture fossile F = min(max(0, D − R), capacité_fossile, fossil_J/dt). Déficit = D − R − F. Les capacités et besoins sont des énergies annuelles, pas des watts. fossil_J est une énergie disponible utile ; le rendement est déjà inclus dans cette définition simplifiée.

**Sorties.** diag : demand_J_yr, supplied_J_yr, deficit_fraction, power_W. deficit_fraction = déficit/D, ou 0 si D = 0 ; power_W = fourniture/31 557 600. rates : fossil_J = −F et co2_mol = F × carbon_mol_J. La réserve fossile est une source externe de carbone au bilan géologique restreint ; comptabiliser ses émissions cumulées à part.

**Données fictives.** Population 1000 ; besoin 1e9 J/personne/an ; renouvelable 4e11 J/an ; capacité fossile 3e11 J/an ; réserve 1e13 J ; coefficient 2e−6 mol/J ; dt = 1 an. Ne pas présenter ces valeurs comme des statistiques nationales.

**Validation.** Demande 1e12 J/an ; fourniture 7e11 ; déficit 0,30 ; puissance environ 22 181 W ; émissions 6e5 mol/an. Réserve nulle interdit le fossile. Population nulle donne demande et émissions nulles.

**Rendu.** Routine energie.py et figure de demande, fourniture et déficit. **Prolongement :** introduire des rendements ou des capacités dépendant du climat en conservant les unités ; expliquer pourquoi un thermostat lent ne neutralise pas automatiquement des émissions rapides.

## Projet 12 Une population évolue

**Question.** Quelles hypothèses fabriquent une croissance ou un déclin ? **Ancrage :** extension démographie demandée. Suites, taux et scénarios.

**Entrées.** state : population ; diag : deficit_fraction ; params : birth_rate_yr, death_rate_yr, deficit_death_rate_yr. Les trois taux sont en 1/an ; ils ne sont ni des pourcentages entiers ni des probabilités par pas.

**Modèle minimal.** Naissances/an = b × P ; décès/an = (d + k × déficit) × P. rate population = naissances − décès. La population représente une moyenne continue et peut donc être non entière. Le déficit de l’instant n agit sur le flux de ce pas. Aucun stock de personnes n’est changé par le module énergie.

**Sorties.** diag : births_yr, deaths_yr ; rates : population. En mode géologique, P = 0 et les trois paramètres valent 0. Un changement de mode démarre une nouvelle expérience, plutôt que de faire apparaître des humains au milieu d’une simulation primitive.

**Données fictives.** P = 1000 ; b = 0,020/an ; d = 0,010/an ; k = 0,020/an ; dt = 1 an. Sans déficit, P devient 1010 après un an. Avec déficit = 0,30, P devient 1004.

**Travail.** Comparer b = d, b > d et un déficit fixé. Raccorder ensuite à énergie sur 100 ans ; tracer population et déficit. Tester dt = 0,5 et 1 an. Décrire la boucle population → demande → déficit → décès comme une hypothèse de ce modèle.

**Validation.** P = 0 donne taux nul. b = d et déficit = 0 laisse P constant. Le moteur refuse une population négative ; un tel résultat impose de réduire dt ou de changer le modèle.

**Rendu.** Routine demographie.py, figure et paragraphe sur les hypothèses sociales. **Prolongement :** natalité variable ou structure par âge ; ajouter une contrainte logistique si utile. Cette population moyenne ne prédit pas une société réelle et ne couvre pas les migrations.

## Projet 13 Plusieurs planètes pour mesurer notre incertitude

**Question.** Nos conclusions tiennent-elles quand les paramètres changent ? **Ancrage :** comparaison de modèles, extension Monte-Carlo et IA. Groupe de quatre conseillé.

**Entrées.** initial, params, modules, steps, dt_yr ; graine ; nombre N de simulations ; intervalles de paramètres. Les copies de paramètres et d’état sont indépendantes pour chaque simulation.

**Modèle.** Tirer par exemple tau_T uniformément entre 5 et 15 ans et pref entre 30 et 60 Pa, puis appeler planet_evolution. Garder les stocks initiaux identiques. Utiliser Random(2026) seulement dans cette enveloppe, jamais dans step. Les bornes sont des hypothèses d’incertitude pédagogiques, pas des mesures.

**Sorties.** Un dictionnaire avec seed, samples, histories, summary et failures. summary contient médiane, quantiles empiriques 5 et 95 % et fraction de simulations avec ice_final > 0,9. Les quantiles portent ici sur T_final ; définir cette variable avant de calculer. failures contient les paramètres et l’erreur de chaque simulation invalidée. Ne pas compter un échec numérique comme une planète gelée.

**Données.** Débuter avec 20 simulations de 100 ans à dt = 1 an ; passer à 200 lorsque le coût est acceptable. Garder tau_ice ≥ 20 ans. Comparer à une simulation centrale et répéter l’ensemble avec dt = 0,5 an à durée identique.

**Validation.** Même graine et même configuration : mêmes résultats. Intervalles de largeur nulle : trajectoires identiques. En relançant une simulation seule avec ses paramètres tirés, on doit retrouver sa trajectoire. Pour N = 20, un quantile extrême est très grossier ; afficher N et les échecs.

**Rendu.** ensemble.py, histogramme des T_final et tableau des paramètres. **Ouverture IA :** fabriquer des couples paramètres → résultat avec le moteur puis comparer un prédicteur simple à une référence moyenne sur des simulations réservées. Aucun entraînement n’est obligatoire. Une IA qui imite le moteur hérite de ses simplifications ; elle ne valide pas sa physique.

## Complément fourni pour pluie et océans

Le projet 5 étudie d'abord le diagnostic de phase de sa fiche ; le complément suivant fournit toutes les lois de l'extension géologique. Elles sont pédagogiques. Il n'est pas demandé aux élèves de les deviner.

Entrées : T (K), fraction de glace i entre 0 et 1, vapeur V (kg), eau totale Wtot (kg), surface A (m²), pas dt (an). Paramètres : E0 = 5 × 10¹⁷ kg/an et tau = 0,02 an dans l'exemple. Ces valeurs se modifient avec le scénario.

Évaporation : E = E0 × (1 − i) × f(T), avec f(T) = exp[(T − 288)/30], borné entre 0,05 et 3. L'exponentielle est donnée et disponible par math.exp ; elle ne constitue pas un prérequis de cours. À 288 K et sans glace, E = E0 ; avec i = 1, E = 0.

Vapeur : dV/dt = E − V/tau. Sur un pas à E constant : Vnouveau = E tau + (Vancien − E tau) exp(−dt/tau). Le code limite la cible à Wtot. Précipitation moyenne : P = E − (Vnouveau − Vancien)/dt. Le débit instantané est V/tau. Distinguer ces deux valeurs dans les résultats.

Eau de surface = Wtot − V. Océan liquide = (1 − i)(Wtot − V). Eau glacée = i(Wtot − V). Bilan à vérifier : vapeur + océan + glace = Wtot. La couverture i est choisie comme proxy de la fraction massique gelée ; le modèle ne calcule pas les calottes ni la chaleur latente.

Pluie moyenne = P(1 − i)/A en mm/an ; neige = Pi/A en mm équivalent eau/an. 1 kg/m² d'eau correspond à 1 mm. À 288 K et i = 0, l'équilibre vapeur vaut E0 tau = 10¹⁶ kg. Pour A = 5,10 × 10¹⁴ m², la pluie vaut environ 980 mm/an. Ce résultat est une moyenne planétaire, pas la météo locale.

Altération du moteur géologique : k = (F0/Cref) × land × max[0, 1 + (T − 288)/50] × (P/E0) × (1 − i). Flux retiré instantané = kC. Avec F volcanique constant : Cnouveau = C exp(−kdt) + (F/k)[1 − exp(−kdt)] ; si k = 0, Cnouveau = C + Fdt. Le retrait est C + Fdt − Cnouveau ; la même quantité est ajoutée aux roches. Fdt est retiré du manteau. Les coefficients sont figés sur le pas, d'où la nécessité du test de convergence.

Figure : vapeur, océan et glace dans le temps ; pluie dans le temps ; comparer avec et sans action de la pluie sur l'altération. Tests : bilan eau, bilan du flux, état glacé et équilibre à 288 K. La boucle à expliquer : T augmente → évaporation et pluie augmentent → altération augmente → CO2 diminue → effet de serre diminue → T diminue.

Cette extension utilise des solutions analytiques et un équilibre climatique rapide. Elle ne se branche pas telle quelle comme taux dans le moteur annuel : ses stocks, son traitement du temps et ses unités sont décrits dans histoire_planete.py. L'assemblage des élèves commence avec le contrat annuel ; le professeur présente ensuite la réduction géologique.

## Fiche à remplir et livraison

Groupe, noms et version : …

Question scientifique : …

Entrées exactes, sens, unités et producteur : …

Sorties exactes, sens, unités et consommateurs : …

Formule fournie et hypothèses : …

Calcul manuel : entrées … ; calcul … ; résultat attendu …

Trois essais : calcul connu … ; cas limite … ; variation d'un paramètre …

Pour chacun : attendu … ; obtenu … ; conclusion …

Graphique : paramètre varié … ; abscisse/unité … ; ordonnée/unité … ; paramètres gardés fixes … ; prédiction … ; interprétation …

Raccordement : fournisseur … ; valeurs de substitution retirées … ; résultat collectif … ; limite du modèle …

Déposer la routine, les essais, cette fiche et la figure dans le dossier de votre groupe. Le professeur conserve le moteur commun et valide les livraisons. Douze groupes de trois et un groupe de quatre ; au moins cinq séances après la première heure, à adapter à l'expérience Python et au matériel.
