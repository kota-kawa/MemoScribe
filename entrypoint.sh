#!/bin/bash
set -e

# Wait for database
echo "Waiting for database..."
while ! python -c "import psycopg; psycopg.connect('${DATABASE_URL:-postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}}')" 2>/dev/null; do
    sleep 1
done
echo "Database is ready!"

# Enable pgvector extension
echo "Enabling pgvector extension..."
python manage.py enable_pgvector || true

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute command
exec "$@"
