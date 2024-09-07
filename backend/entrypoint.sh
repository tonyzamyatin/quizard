#!/bin/sh
if [ "$APP_SERVICE" = "api" ]; then
    echo "Starting Flask API..."
    python -m src.rest.flask_app
elif [ "$APP_SERVICE" = "worker" ]; then
    echo "Starting Celery Worker..."
    celery -A src.celery.celery_worker worker -l info
else
    echo "No valid service specified, exiting..."
    exit 1
fi
