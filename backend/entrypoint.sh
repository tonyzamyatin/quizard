#!/bin/sh

if [ "$DEBUG" = 1 ]; then
    echo "Starting Flask in debug mode..."
    exec poetry run flask --app src/app run --host 0.0.0.0 --debug --reload
else
    echo "Starting Flask..."
    exec poetry run flask --app src/app run --host 0.0.0.0
fi
