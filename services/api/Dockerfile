FROM python:3.12-slim

WORKDIR /app

# Copy pyproject.toml and poetry.lock (if exists)
COPY pyproject.toml poetry.lock* /app/

# Install Poetry
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry

# Install dependencies (without creating a virtualenv)
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY matching_service_api /app/matching_service_api

# Expose port
ENV PORT=8000

# Start the app
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:create_app()"]
