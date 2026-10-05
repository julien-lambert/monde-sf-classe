# Faire travailler 40 élèves sur une planète commune

## Conclusion de la vérification pédagogique

Le dossier scientifique donne bien une question, les entrées et sorties, la relation, des essais connus et une figure pour chacun des 13 projets. Il est utilisable comme base. Le moteur corrigé fonctionne, mais cela ne démontre pas à lui seul que des élèves pourront se coordonner. Le protocole ci-dessous complète cette partie. Les routines sont indépendantes pour leur écriture et leurs tests ; les diagnostics créent des dépendances lors de l'assemblage.

Les corrigés complets restent dans le dossier professeur. Pour les élèves, distribuer leur fiche scientifique et le contrat, puis une amorce de fonction vide. Ils doivent écrire leur relation, calculer un exemple, implémenter et défendre leur vérification. Ne pas leur donner les cinq graphiques du corrigé comme production attendue à recopier.

## Une même démarche dans les treize groupes

1. **Décrire** : nom de chaque entrée et sortie, sens physique, unité, exemple numérique, provenance.
2. **Modéliser** : écrire la relation symbolique, les hypothèses, le domaine et un calcul à la main.
3. **Coder** : écrire une fonction sans saisie interactive, sans modifier les dictionnaires reçus.
4. **Vérifier** : résultat connu, cas limite et variation attendue. Écrire attendu, obtenu et conclusion ; « Python ne plante pas » ne suffit pas.
5. **Tracer** : annoncer ce que l'on fait varier, garder les autres paramètres fixes, mettre axes, unités et légende, puis expliquer le mécanisme observé.
6. **Raccorder** : remplacer les données de substitution par les diagnostics réels, refaire le test et comparer avant/après.

Chaque élève doit expliquer un calcul et une vérification. Les rôles scientifique, programmeur et vérificateur tournent à chaque séance. Le groupe de quatre ajoute une personne chargée de documenter les essais, sans lui déléguer toute la coordination.

## Le moteur reste à la charge du professeur

Les élèves développent les mécanismes ; le professeur conserve la version commune de engine.py, les unités, le schéma d'état et l'ordre MODULES. Un groupe modifie seulement son fichier et son fichier d'essais. Les changements de noms, d'unités ou de formule qui affectent un voisin sont d'abord inscrits au registre puis discutés. Il faut éviter treize versions du moteur et les modifications simultanées d'un même fichier.

Un dossier partagé contient `a_valider/G01`, …, `a_valider/G13`, puis `valide` et `commun`. Les élèves déposent ; seul le professeur remplace un fichier dans commun. Garder une copie datée avant chaque intégration. Un ENT suffit ; Git n'est pas un prérequis.

## Le paquet à livrer

Chaque groupe livre le fichier de routine, un script/notebook d'essais séparé, la fiche remplie, les données numériques de sa figure et la figure commentée. Nom proposé : G01_gaz_v01. Une livraison n'est acceptée que si les entrées/sorties correspondent, trois essais ont une conclusion, les unités sont explicites et la routine fonctionne avec les données de substitution. État du registre : formule à valider → tests isolés réussis → contrat accepté → raccordé → expérience collective vérifiée.

Le groupe 13 livre ensemble.py et ses essais d'ensembles ; il ne s'insère pas dans MODULES. Il commence avec le moteur de référence fourni, puis utilise le moteur assemblé. Aucun groupe ne doit attendre la fin d'un voisin pour commencer.

## Dépendances et essais de substitution

- Gaz (1) fournit les pressions à eau (5) et climat (10). Pour travailler seuls, ces groupes prescrivent explicitement ces pressions.
- Radiatif (4) fournit Teq_K à climat (10). Glace (9) influence le radiatif par l'état commun au pas suivant.
- Eau (5) fournit ocean_possible à altération (6). Le groupe 6 teste d'abord True puis False.
- Énergie (11) fournit deficit_fraction à démographie (12). Le groupe 12 teste d'abord 0 puis 0,30.
- Dégazage (3), altération (6) et énergie (11) contribuent au même stock CO2 ; ils rendent des taux additionnables. Aucun ne remplace la valeur du stock.
- Oxygénation (7), rétention (2) et UV (8) n'ont pas de liaison chimique automatique dans cette version. Ne pas demander à ces groupes de fabriquer ce couplage absent du modèle.

Les diagnostics artificiels servent uniquement aux tests isolés. Une fois raccordés, ils sont retirés ; ne pas conserver une pression ou un déficit imposé qui masque la sortie du voisin.

## Prévoir le temps de coordination

Prévoir une première heure commune, puis **cinq séances de 55 minutes au minimum comme hypothèse de préparation**, à ajuster à l'expérience Python et au matériel de la classe. Avec des débutants, une séance supplémentaire de prise en main peut être nécessaire. Ce n'est pas une durée garantie.

| Séance | Travail | Décision à prendre |
|---|---|---|
| 1 | Fiche, formule et calcul manuel | Contrat scientifique validé |
| 2 | Fonction et essais isolés | Corriger unités et cas limites |
| 3 | Expériences et graphique | Interprétation validée ; dépôt v01 |
| 4 | Intégration par lots ; autres groupes relisent un voisin | Accepter ou retourner chaque livraison |
| 5 | Comparaison collective de scénarios et restitution | Relier les mécanismes à la trajectoire |

Treize restitutions de trois minutes prennent déjà 39 minutes : ne pas prévoir aussi tout l'assemblage dans cette séance. Le professeur vérifie les premières livraisons entre les séances 3 et 4. Réserver cinq minutes au début et à la fin de chaque séance au registre des blocages, sans transformer cela en tour de table long.

## Assembler par lots

A : gaz, rétention, radiatif, eau, UV — contrôler les diagnostics. B : dégazage, altération, oxygénation — contrôler les transferts et bilans. C : glace et climat — comparer chaud/froid et diviser le pas. D : énergie et démographie — scénario contemporain distinct. E : Monte-Carlo — comparer des copies du même moteur.

À chaque lot : repartir d'une version acceptée, intégrer une routine à la fois, exécuter ses essais puis ceux du moteur, garder la durée physique identique pour les comparaisons. Une routine absente est indiquée comme absente dans l'expérience ; un corrigé utilisé provisoirement porte l'étiquette « référence professeur ».

## La production vraiment collective

La classe écrit ensemble la question : « Pourquoi deux planètes sous le même Soleil peuvent-elles évoluer différemment ? » Les groupes 4, 9 et 10 prédisent d'abord la chaîne glace → albédo → énergie absorbée → température → glace ; 1, 3 et 6 expliquent comment CO2 la modifie. La classe observe les courbes chaude, gelée et déglaciation et compare ses prédictions aux résultats. Les autres groupes présentent leurs branches dans les expériences adaptées, sans prétendre que tous les projets influencent le climat.

Chaque groupe signe une flèche du schéma causal, donne un résultat isolé vérifié puis un effet constaté dans l'expérience commune. Faire aussi un essai avec un flux annulé ou un paramètre changé, en conservant un scénario valide, pour vérifier l'explication causale. Le bilan final est rédigé par la classe : observations, mécanismes, bilans, limites. C'est ce raisonnement partagé, au-delà des treize fonctions juxtaposées, qui donne le caractère collectif.

## Carte des contrats de la version installée

Les noms ci-dessous ont été relevés dans le code corrigé. Les unités et formules sont dans les fiches scientifiques. `values` reste vide. Une ligne de taux représente une variation par an ; un diagnostic n'est pas un taux.

### Groupe 1 gaz

- État lu : `co2_mol`, `h2o_mol`, `n2_mol`, `o2_mol`.
- Paramètres lus : `area_m2`, `g_m_s2`.
- Diagnostics des voisins lus : aucun.
- Taux rendus : aucun.
- Diagnostics rendus : `P_Pa`, `fractions`, `pco2_Pa`, `po2_Pa`, `ph2o_Pa`.
- Figure à construire : Pressions partielles de trois atmosphères (Pa).

### Groupe 2 retention

- État lu : aucun.
- Paramètres lus : `G`, `NA`, `T_exo_K`, `kB`, `mass_kg`, `radius_m`.
- Diagnostics des voisins lus : aucun.
- Taux rendus : aucun.
- Diagnostics rendus : `vlib_m_s`, `retention`.
- Figure à construire : 6 × vitesse thermique en fonction de T (K), avec vitesse de libération.

### Groupe 4 radiatif

- État lu : `ice`.
- Paramètres lus : `S_W_m2`, `sigma`.
- Diagnostics des voisins lus : aucun.
- Taux rendus : aucun.
- Diagnostics rendus : `albedo`, `absorbed_W_m2`, `Teq_K`.
- Figure à construire : Température radiative en fonction de la fraction de glace (K, fraction).

### Groupe 5 eau

- État lu : `T_K`, `ice`.
- Paramètres lus : `ocean_prescribed`, `water_mode`.
- Diagnostics des voisins lus : `P_Pa`, `ph2o_Pa`.
- Taux rendus : aucun.
- Diagnostics rendus : `water_domain`, `ocean_possible`, `saturation_Pa`.
- Figure à construire : Pression de saturation en fonction de T (Pa, °C), avec points testés et domaine valide.

### Groupe 8 uv

- État lu : aucun.
- Paramètres lus : `NA`, `absorption_m2_mol`, `c`, `h`, `lambda_nm`, `ozone_column_mol_m2`.
- Diagnostics des voisins lus : aucun.
- Taux rendus : aucun.
- Diagnostics rendus : `photon_J`, `dissociation_possible`, `uv_fraction`.
- Figure à construire : Transmission en fonction de la colonne prescrite d’ozone (fraction, mol/m²).

### Groupe 11 energie

- État lu : `fossil_J`, `population`.
- Paramètres lus : `carbon_mol_J`, `fossil_capacity_J_yr`, `need_J_person_yr`, `renewable_J_yr`.
- Diagnostics des voisins lus : aucun.
- Taux rendus : `fossil_J`, `co2_mol`, `emitted_c_mol`.
- Diagnostics rendus : `demand_J_yr`, `supplied_J_yr`, `deficit_fraction`, `power_W`.
- Figure à construire : Demande et fourniture (J/an), puis déficit (fraction) en fonction du temps.

### Groupe 3 degazage

- État lu : `mantle_c_mol`.
- Paramètres lus : `volcanic_mol_yr`.
- Diagnostics des voisins lus : aucun.
- Taux rendus : `co2_mol`, `mantle_c_mol`.
- Diagnostics rendus : `volcanic_actual_mol_yr`.
- Figure à construire : Stocks manteau et CO2 en fonction du temps (mol, ans).

### Groupe 6 alteration

- État lu : `T_K`, `co2_mol`, `ice`.
- Paramètres lus : `co2_ref_mol`, `land_fraction`, `weather_mol_yr`.
- Diagnostics des voisins lus : `ocean_possible`.
- Taux rendus : `co2_mol`, `rock_c_mol`.
- Diagnostics rendus : `weather_actual_mol_yr`.
- Figure à construire : CO2 et carbone des roches en fonction du temps (mol, ans).

### Groupe 7 oxygenation

- État lu : `fe_mol`, `o2_mol`.
- Paramètres lus : `oxygen_mol_yr`.
- Diagnostics des voisins lus : aucun.
- Taux rendus : `o2_mol`, `fe_mol`, `oxide_fe_mol`.
- Diagnostics rendus : `oxygen_used_mol_yr`.
- Figure à construire : O2 libre et fer restant en fonction du temps (mol, ans).

### Groupe 9 glace

- État lu : `T_K`, `ice`.
- Paramètres lus : `tau_ice_yr`.
- Diagnostics des voisins lus : aucun.
- Taux rendus : `ice`.
- Diagnostics rendus : aucun.
- Figure à construire : Fraction de glace en fonction du temps pour deux températures imposées.

### Groupe 10 climat

- État lu : `T_K`.
- Paramètres lus : `pref_Pa`, `tau_T_yr`.
- Diagnostics des voisins lus : `Teq_K`, `pco2_Pa`.
- Taux rendus : `T_K`.
- Diagnostics rendus : `Ttarget_K`, `greenhouse_K`.
- Figure à construire : Température en fonction du temps pour deux pressions partielles de CO2 (K, ans).

### Groupe 12 demographie

- État lu : `population`.
- Paramètres lus : `birth_rate_yr`, `death_rate_yr`, `deficit_death_rate_yr`.
- Diagnostics des voisins lus : `deficit_fraction`.
- Taux rendus : `population`.
- Diagnostics rendus : `births_yr`, `deaths_yr`.
- Figure à construire : Population et déficit en fonction du temps (personnes, ans).

### Groupe 13 Monte Carlo

Entrées : initial, params, modules, steps, dt_yr, nombre, seed et bounds. Sorties : seed, samples, histories, summary, failures. Figure : histogramme des températures finales avec nombre de simulations et échecs. Vérifications : même graine, bornes de largeur nulle, reproduction d'une simulation tirée. Aucune sortie de taux.

## Ajustements par rapport au support initial

Le corrigé ajoute `emitted_c_mol` aux taux du groupe 11 pour suivre explicitement les émissions cumulées. L'état commun doit contenir ce compteur initialisé à zéro. Le groupe 10 produit aussi `greenhouse_K` comme diagnostic ; le groupe 5 produit `water_domain` et `saturation_Pa`. Le moteur calcule les diagnostics au même instant que l'état enregistré, y compris à la fin. Utiliser le moteur du dossier installé pour l'assemblage, plutôt que mélanger celui-ci avec l'amorce à deux routines du support initial. Ces ajouts doivent être annoncés avant distribution des contrats.

## Fiche commune à remplir et à faire relire

Groupe / version / relecteurs : …

| Entrée ou sortie exacte | Sens physique | Unité | Exemple | Producteur et consommateur |
|---|---|---|---|---|
| … | … | … | … | … |

Formule symbolique et hypothèses : …

| Essai | Paramètres et entrées | Résultat attendu et justification | Résultat obtenu | Conclusion |
|---|---|---|---|---|
| Calcul connu | … | … | … | … |
| Cas limite | … | … | … | … |
| Variation d'un paramètre | … | … | … | … |

Figure : abscisse/unité … ; ordonnée/unité … ; paramètre varié … ; autres paramètres fixes … ; prédiction … ; observation … ; explication …

Raccordement : fournisseur … ; données de substitution retirées … ; version commune utilisée … ; effet collectif attendu … ; effet observé … ; limite …
