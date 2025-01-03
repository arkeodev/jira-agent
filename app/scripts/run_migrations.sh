#!/bin/bash
set -e

echo "Waiting for database to be ready..."
until pg_isready -h db -p 5432 -U testuser; do
  echo "Waiting for database connection..."
  sleep 2
done

echo "Running database migrations..."
cd /app
alembic upgrade head

echo "Migrations completed successfully"
