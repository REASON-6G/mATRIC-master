FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /app/

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry files
COPY ./pyproject.toml ./poetry.lock* /app/

# (Optional) dev deps flag remains harmless
ARG INSTALL_DEV=false

# Base system deps (keep ssh tools for Ansible use)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates git build-essential sshpass openssh-client \
 && rm -rf /var/lib/apt/lists/*

# --- Work around pip/packaging 25.0 uninstall bug that breaks Poetry installs ---
# Keep pip/setuptools/wheel up-to-date enough, and pin packaging < 25 before poetry install.
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install "packaging<25.0"

# Install deps via poetry (uses system interpreter, no venv)
RUN bash -lc 'if [ "$INSTALL_DEV" = "true" ]; then poetry install --no-root; else poetry install --no-root --only main; fi'

ENV PYTHONPATH=/app

# App files
COPY ./scripts/ /app/
COPY alembic.ini /app/
COPY ./prestart.sh /app/
COPY ./tests-start.sh /app/
COPY app /app/app

# --- Always install Ansible + requests into the runtime interpreter ---
# Use /usr/local/bin/python3 (the image's default). Then make /usr/bin/python3 a symlink
# so anything calling /usr/bin/python3 (e.g., the playbook) sees the same site-packages.
RUN /usr/local/bin/python3 -m pip install --no-cache-dir \
      "ansible==9.*" \
      "requests==2.32.3" && \
    ln -sf /usr/local/bin/python3 /usr/bin/python3 && \
    ln -sf /usr/local/bin/pip3   /usr/bin/pip3 && \
    /usr/local/bin/python3 - <<'PY'
import sys, requests
print("LOCAL  python:", sys.executable)
print("LOCAL  requests:", requests.__version__)
PY

# Double-check the /usr/bin symlink sees the same packages
RUN /usr/bin/python3 - <<'PY'
import sys, requests
print("USR-BIN python:", sys.executable)
print("USR-BIN requests:", requests.__version__)
PY

# Make sure anything invoking ansible uses the pip-installed launcher
ENV ANSIBLE_PLAYBOOK_BIN=/usr/local/bin/ansible-playbook

# No CMD here; compose sets it per service
