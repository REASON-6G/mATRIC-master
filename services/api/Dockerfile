FROM python:3.12-slim

WORKDIR /app

# Copy pyproject.toml, poetry.lock, and gunicorn config
COPY pyproject.toml poetry.lock* gunicorn.conf.py /app/

# Install Poetry
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir "poetry==2.2.0"

# Install dependencies
RUN poetry env activate 
RUN poetry install --no-root --no-interaction --no-ansi

# Copy application code
COPY matching_service_api /app/matching_service_api

# Expose port
EXPOSE 8000

# Start the app
CMD ["poetry", "run", "gunicorn", "-c", "gunicorn.conf.py", "matching_service_api:create_app()"]
