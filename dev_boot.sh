#!/bin/bash
# this script is used to boot the app for developpement
FILE="data/ontology/ontology.json"     
if [ ! -f $FILE ]; then
    cp data/ontology/ontology_default.json data/ontology/ontology.json
fi
source .venv/bin/activate
flask db upgrade
python myoxia.py
flask run