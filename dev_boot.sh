#!/bin/bash
# this script is used by ./docker/dev_build_run.sh to boot the app for developpement
FILE="data/ontology/ontology.json"
if [ ! -f $FILE ]; then
    cp data/ontology/ontology.json.demo data/ontology/ontology.json
fi

DB="data/database/app.db"
if [ ! -f $DB ]; then
    cp data/database/app.db.demo data/database/app.db
fi

uv run flask db upgrade -d src/impatient/migrations
uv run flask --debug run --host=0.0.0.0 --port=7860;
