#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate

echo "Seeding initial data..."
python initial_data.py

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Starting Gunicorn with Verbose Logging..."
exec gunicorn voting_system.wsgi:application --bind 0.0.0.0:7860 --workers 2 --timeout 120 --log-level debug --access-logfile - --error-logfile - --capture-output
