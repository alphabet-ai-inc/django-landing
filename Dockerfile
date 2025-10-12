FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app

# Dependencies
COPY pyproject.toml poetry.lock README.md /app/
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --without test

# Code
COPY . /app

# Установка netcat для create_schema.sh
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Static files
RUN python manage.py collectstatic --noinput

# DB Schema
# RUN ./create_schema.sh

# Running app
CMD ["/app/entrypoint.sh"]