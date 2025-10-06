#!/bin/bash

source .env

DATABASE_URL="postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME}"
export DATABASE_URL

echo "Waiting for PostgreSQL to start..."
while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
  sleep 1
done
echo "PostgreSQL started"

echo "Creating schema $DATABASE_SCHEMA if not exists..."
psql $DATABASE_URL -c "CREATE SCHEMA IF NOT EXISTS $DATABASE_SCHEMA;" || exit 1
