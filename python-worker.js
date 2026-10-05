let python=null;onmessage=async({data})=>{try{if(!python){postMessage({status:'Chargement de Python dans le navigateur…'});importScripts('https://cdn.jsdelivr.net/pyodide/v0.29.3/full/pyodide.js');python=await loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v0.29.3/full/'});const r=await fetch('partage/classe_commune.py');if(!r.ok)throw new Error('Moteur indisponible (HTTP '+r.status+').');python.runPython(await r.text());}postMessage({status:'Moteur chargé. Calcul de toutes les routines…'});python.globals.set('scenario_choisi',data.scenario);const sortie=await python.runPythonAsync(`import re, json
resultat = comparer_groupe(10, ROUTINES[10], scenario_choisi)
rapport = rapport_comparaison(resultat)
figures = re.findall(r"<svg\b.*?</svg>", rapport, flags=re.DOTALL)
assert len(figures) == 4
json.dumps({"html": "".join(figures), "version": VERSION_CLASSE})`);postMessage(JSON.parse(sortie));}catch(e){postMessage({error:String(e.message||e)});}};
