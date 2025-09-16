# Use official Python slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry and project files
COPY pyproject.toml poetry.lock* /app/

# Install poetry
RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir poetry

# Install dependencies
RUN poetry install --no-root --no-interaction --no-ansi

# Copy the matcher source
COPY matcher /app/matcher

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV POLL_INTERVAL=5

# Run matcher service
CMD ["poetry", "run", "matcher"]
