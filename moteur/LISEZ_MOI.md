# Planet Evolution — guide du professeur et des élèves

## Démarrer

Sur ce Mac, double-cliquer **Lancer_la_planete.command**. Le programme vérifie les routines, calcule cinq expériences et 50 simulations Monte-Carlo, puis ouvre le rapport dans le navigateur. Aucun paquet Python supplémentaire n'est nécessaire. Le lanceur utilise le Python déjà présent avec Codex, puis cherche `python3` si celui-ci n'est plus disponible. Si macOS refuse l'ouverture, lancer depuis Terminal : `python3 run.py`, dans ce dossier. Le code ne télécharge rien.

Pour consulter les résultats déjà calculés : **Ouvrir_le_rapport.command**, ou ouvrir `resultats/rapport.html`. Les CSV s'ouvrent dans un tableur ; les JSON contiennent les états et diagnostics complets. Relancer remplace uniquement les résultats de ce dossier.

## Notre histoire commune

Nous construisons une planète, depuis son atmosphère jusqu'à une société qui consomme de l'énergie. Chaque groupe répond à une question scientifique en écrivant une fonction. Le moteur assemble leurs réponses. Les chapitres atmosphère, eau, bilan radiatif, carbone, oxygénation, glaciation et UV viennent du cours fourni. Énergie, démographie et Monte-Carlo sont des extensions pédagogiques. Pour 40 élèves : 12 groupes de trois et un groupe de quatre ; ce dernier peut prendre Monte-Carlo et l'intégration.

## Comprendre le moteur

`scenarios.py` contient l'état initial, les paramètres et la liste des fonctions actives. `engine.py` contient la boucle temporelle. `run.py` lance les expériences et prépare les graphiques.

L'état est un dictionnaire : température `T_K`, fraction de glace `ice`, quantités de gaz en moles, réserves de carbone, population et réserve fossile en joules. Le temps est en années. Les paramètres décrivent les hypothèses fixes : flux solaire, constantes, production volcanique, capacités énergétiques, natalité, etc.

À chaque instant :

1. Le moteur lit un état commun et en donne une copie à chaque routine.
2. Les routines calculent des diagnostics (pression, puissance, température cible…) et des taux de variation.
3. Le moteur additionne les taux, puis applique **nouvelle valeur = ancienne valeur + pas × taux** : c'est la méthode d'Euler explicite.
4. Il avance le temps et vérifie les stocks, la température et la fraction de glace.
5. Il enregistre une copie indépendante. Les diagnostics enregistrés sont recalculés au même instant que les stocks, y compris au dernier instant.

Les diagnostics calculés par une routine peuvent être lus par les suivantes. L'ordre dans `MODULES` est donc important : gaz avant climat, radiatif avant climat, eau avant altération, énergie avant démographie. Les stocks ne sont jamais modifiés directement par les routines. Tous leurs changements sont appliqués ensemble à la fin du pas.

## Le contrat d'une routine

Chaque fonction a la signature `routine(state, params, dt_yr)` et renvoie :

```python
return {
    "rates": {"co2_mol": flux},
    "values": {},
    "diag": {"mon_diagnostic": resultat}
}
```

`rates` contient seulement les variables modifiées : mol/an, J/an, personnes/an, K/an ou fraction/an. `values` reste vide dans cette version pour éviter qu'un groupe écrase l'état d'un autre. Les noms de diagnostics doivent être uniques. Les fichiers fournis sont les corrigés simples, avec fonctions, conditions, dictionnaires et boucles usuelles. Pour brancher une nouvelle fonction, l'importer et l'ajouter au bon endroit dans `MODULES`.

Exemple : un dégazage de 10 mol/an pendant 2 ans ajoute 20 mol à l'atmosphère et retire 20 mol au manteau. On ne crée pas ce carbone. Quand la réserve est presque vide, le flux est limité à réserve/pas.

Attention aux unités : les formules de physique utilisent SI (Pa, K, kg, m, W), les stocks évoluent avec des taux annuels. Le module énergie convertit les J/an en W en divisant par 31 557 600 s/an. Une température en degrés Celsius doit recevoir +273,15 avant son utilisation comme température absolue.

## Les 13 projets et leur correction

| Projet | Fichier | Entrées principales | Sorties principales |
|---|---|---|---|
| 1. Atmosphère et Dalton | modules/gaz.py | stocks, gravité, surface | pression totale, pressions partielles |
| 2. Retenir les gaz | modules/retention.py | masse, rayon, température exosphérique | vitesses et critère de rétention |
| 3. Dégazage volcanique | modules/degazage.py | réserve du manteau, flux | transfert vers CO2 |
| 4. Bilan radiatif | modules/radiatif.py | flux solaire, glace | albédo, absorption, température d'équilibre |
| 5. Eau et condensation | modules/eau.py | température, pression, mode | diagnostic de phase/condensation |
| 6. Altération des roches | modules/alteration.py | CO2, température, eau, continents | transfert carbone vers roches |
| 7. Oxygénation et fer | modules/oxygenation.py | production O2, réserve Fe | O2 libre et fer oxydé |
| 8. UV et ozone | modules/uv.py | longueur d'onde, colonne d'ozone | énergie photonique et transmission |
| 9. Glace et rétroaction | modules/glace.py | température, glace, délai | évolution de la fraction de glace |
| 10. Climat dynamique | modules/climat.py | équilibre radiatif, CO2, délai | variation de température |
| 11. Énergie et émissions | modules/energie.py | population, capacités, réserve | consommation, déficit, émissions |
| 12. Démographie | modules/demographie.py | population, natalité, déficit | croissance moyenne |
| 13. Monte-Carlo | ensemble.py | scénario, bornes, nombre, graine | ensemble, quantiles, échecs |

Chaque fichier précise sa formule dans son code. Lire d'abord `gaz.py`, puis `degazage.py`, puis `engine.py`. Le projet 13 enveloppe le moteur : il ne s'exécute pas comme un flux à l'intérieur de la boucle. Le moteur reste déterministe pour des paramètres donnés. Monte-Carlo choisit des paramètres aléatoires ; une même graine reproduit les tirages. Les quantiles décrivent ces hypothèses, pas une incertitude climatique mesurée.

## Expériences et vérification

- **chaude** : la température rejoint un équilibre avec peu de glace.
- **gelee** : un autre état initial reste glacé sous le même éclairement ; l'albédo entretient cet état.
- **deglaciation** : le dégazage accumule du CO2 puis permet une sortie de glaciation dans ce modèle.
- **societe** : la réserve fossile s'épuise ; le déficit énergétique modifie la croissance démographique.
- **oxygenation** : le fer consomme d'abord l'oxygène produit, puis O2 s'accumule.

`tests.py` vérifie les lois élémentaires, les transferts, les seuils, l'isolation des routines, les erreurs et la reproductibilité. `run.py` exécute ces tests avant toute production de résultats. Il compare chaque expérience avec un pas deux fois plus petit, à la fin ET sur toute la trajectoire. Un équilibre final identique ne suffit pas à prouver que la trajectoire est bien résolue. Le bilan carbone inclut les émissions fossiles cumulées.

Pour changer une expérience, modifier une copie de l'état ou des paramètres dans `scenarios.py`, relancer, puis interpréter les courbes. Une erreur doit être discutée : le moteur refuse les stocks négatifs et les valeurs non finies. Pour les relaxations glace/climat, choisir un pas au plus égal au temps de relaxation. D'autres couplages peuvent demander un pas plus petit : vérifier la convergence après chaque changement.

## Limites scientifiques à expliquer aux élèves

C'est une maquette de systèmes couplés, pas un modèle climatique prédictif ni une reconstruction quantitative de l'histoire terrestre. L'effet de serre, les seuils de glace, l'altération et la démographie utilisent des lois choisies pour être lisibles. Les délais géologiques et humains diffèrent : chaque scénario choisit son pas et ses paramètres adaptés.

L'océan est prescrit ; le module eau donne un diagnostic et ne transfère pas de masse d'eau. En mode mélange, la pression partielle est comparée à une table de pression de vapeur saturante ; le mode vapeur pure est une autre expérience. Hors table, le résultat est indéterminé. La colonne d'ozone est prescrite, sans chimie O2–O3. La production d'oxygène est imposée, sans vivant. Le critère de rétention ne calcule pas un flux d'échappement. Les émissions d'une société de 1 000 habitants sont négligeables face au stock atmosphérique planétaire. Ne pas présenter leur effet thermique comme une projection du monde réel.

## Python pour la classe

Les élèves peuvent commencer avec Python 3 dans Thonny, ou avec Basthon dans le navigateur sans installation ni compte (https://notebook.basthon.fr). Sur un notebook, copier les petites fonctions et leurs exemples avant d'assembler le projet. Le lanceur Mac est réservé au dossier local ; il ne fonctionne pas dans Basthon. Colab est une autre possibilité avec compte Google. Pour le dossier complet, ouvrir un terminal dans ce dossier et exécuter `python3 run.py` ; pour les vérifications seules : `python3 -m unittest tests -v`.

Ne demander aux élèves que leur routine, un exemple calculé à la main, un graphique ou tableau, une vérification et les limites de leur hypothèse. Conserver une copie des corrigés avant de remplacer une routine.
