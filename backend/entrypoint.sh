#!/bin/sh

if [ "$APP_SERVICE" = "api" ]; then
    echo "Starting Flask API..."
    if [ "$ENVIRONMENT" = "development" ]; then
        echo "Running in development mode..."
        python -m src.rest.flask_app
    else
        echo "Running in production mode with Gunicorn..."
        gunicorn -b 0.0.0.0:8080 src.rest.flask_app:flask_app
    fi
elif [ "$APP_SERVICE" = "worker" ]; then
    echo "Starting Celery Worker..."
    celery -A src.celery.celery_worker worker -l info
else
    echo "No valid service specified, exiting..."
    exit 1
fi
