# ---------------------------
# Base image
# ---------------------------
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry and project files
COPY ./services/emulator/pyproject.toml ./services/emulator/poetry.lock* /app/

# Install poetry
RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir poetry

# Copy the emulator source
COPY ./services/emulator /app

# Copy the sibling client library into the image
COPY ./services/client /app/../client

# Install dependencies including the local client library
RUN poetry install --no-root --no-interaction --no-ansi --only main

# Set working dir to emulator service
WORKDIR /app

CMD ["poetry", "run", "python", "run.py"]
