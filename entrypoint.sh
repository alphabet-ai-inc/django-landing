#!/bin/bash
set -e

# Migrations
echo "🔄 Running migrations..."
python manage.py migrate --noinput

# Collect static
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

exec poetry run gunicorn django_landing.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --log-level info
