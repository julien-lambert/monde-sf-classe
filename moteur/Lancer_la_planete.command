#!/bin/zsh
cd "${0:A:h}" || exit 1
PYTHON=$(command -v python3)
if [[ -z "$PYTHON" ]]; then
    echo "Utiliser les notebooks dans Basthon, ou installer Python 3 pour le moteur local."
else
    "$PYTHON" run.py && /usr/bin/open resultats/rapport.html
fi
echo "Appuyer sur Entrée pour fermer."
read reponse
