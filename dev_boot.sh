#!/bin/bash
# this script is used by ./docker/dev_build_run.sh to boot the app for developpement
FILE="data/ontology/ontology.json"
if [ ! -f $FILE ]; then
    cp data/ontology/ontology_default.json data/ontology/ontology.json
fi

# Check if running in a container or not.
if [ -f /.dockerenv ]; then
    flask db upgrade
    flask run --host=0.0.0.0;
else
    source .venv/bin/activate
    flask db upgrade
    flask run
fi
