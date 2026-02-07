#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate

echo "Seeding initial data..."
python initial_data.py

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Starting Server (Diagnostic Mode)..."
exec python manage.py runserver 0.0.0.0:7860
