#!/bin/bash
# this script is used by ./docker/dev_build_run.sh to boot the app for developpement
FILE="data/ontology/ontology.json"     
if [ ! -f $FILE ]; then
    cp data/ontology/ontology_default.json data/ontology/ontology.json
fi
# Activate venv depending if a container or not.
if [ ! -f ".venv/bin/activate" ]; then
    source ../.venv/bin/activate
else
    source .venv/bin/activate
fi
flask db upgrade

# Check if running in a container or not.
if [ -f /.dockerenv ]; then
    flask run --host=0.0.0.0;
else
    flask run
fi
