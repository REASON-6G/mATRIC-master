FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml /app/
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir .
COPY app /app/app
ENV PORT=8000
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:create_app()"]