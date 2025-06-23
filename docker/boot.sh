#!/bin/bash
# this script is used to boot a Docker container
while true; do
    FILE="data/ontology/ontology.json"
    if [ ! -f $FILE ]; then
        cp data/ontology/ontology.json.demo data/ontology/ontology.json
    fi

    DB="data/database/app.db"
    if [ ! -f $DB ]; then
        cp data/database/app.db.demo data/database/app.db
    fi

    uv run flask db upgrade -d src/impatient/migrations

    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done
exec uv run gunicorn -b :7860 --access-logfile - --error-logfile - --timeout 900 --workers 4 --threads 8 --preload src.impatient.impatient_app:app
