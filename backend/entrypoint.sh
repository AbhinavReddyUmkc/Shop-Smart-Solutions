#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Run database migrations if needed
# This is a placeholder - in a production system, you'd use alembic or similar

# Start the application with Gunicorn
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app