#!/bin/bash
exec poetry run gunicorn django_landing.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --log-level info