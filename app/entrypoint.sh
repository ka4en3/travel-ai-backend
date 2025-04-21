#!/bin/bash
set -e

echo "Running Alembic migrations..."
alembic upgrade head

echo "Seeding fixture data..."
# python app/fixtures/load.py
python -m fixtures.load

echo "Starting FastAPI server..."
exec "$@"
