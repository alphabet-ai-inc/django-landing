FROM python:3.12
WORKDIR /app
ENV PYTHONPATH=/app
COPY pyproject.toml poetry.lock /app/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install
COPY . /app
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "django_landing.wsgi:application"]
