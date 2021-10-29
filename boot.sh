#!/bin/bash
# this script is used to boot a Docker container
source /home/myoxia/.venv/bin/activate
while true; do
    flask db upgrade
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done
exec gunicorn -b :5000 --access-logfile - --error-logfile - --timeout 900 --workers 4 --threads 8 --preload myoxia:app