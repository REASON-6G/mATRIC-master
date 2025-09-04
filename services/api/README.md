# Flask Matching Service API

This is the backend API for managing publishers, subscribers, topics, and the matching service in the mATRIC platform.

---

## Table of Contents
- [Environment Variables](#environment-variables)  
- [Dependencies](#dependencies)  
- [Development Quick Start](#development-quick-start)  
- [API Structure](#api-structure)  

---

## Environment Variables

The Flask API reads configuration from environment variables. Create a `.env` file or duplicate `example.env` to set the following variables:

| Variable                     | Description | Default / Notes |
|-------------------------------|------------|----------------|
| `SECRET_KEY`                  | Flask secret key (used for sessions, etc.) | `"dev"` |
| `JWT_SECRET`                  | Secret key for JWT token encoding | `"dev"` |
| `ACCESS_TOKEN_EXPIRES`        | JWT access token expiry in seconds | `900` |
| `REFRESH_TOKEN_EXPIRES`       | JWT refresh token expiry in seconds | `1209600` |
| `MONGO_URI`                   | MongoDB connection string | `"mongodb://localhost:27017/matchingservice"` |
| `RABBITMQ_URL`                | RabbitMQ connection URL | `""amqp://admin:changeme@rabbitmq:5672/"` |
| `RABBITMQ_EXCHANGE`           | RabbitMQ exchange for topic messages | `"topics"` |
| `INFLUX_URL`                  | URL of InfluxDB | `"http://influxdb:8086"` |
| `INFLUX_TOKEN`                | InfluxDB API token | `"devtoken"` |
| `INFLUX_ORG`                  | InfluxDB organization | `"matric"` |
| `INFLUX_BUCKET`               | InfluxDB bucket for topic metrics | `"topics"` |
---

## Dependencies

- Python 3.11+  
- [Poetry](https://python-poetry.org/) (preferred) for dependency management

Install Poetry if you don’t have it:

On Linux:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

or from Windows

```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

Ensure poetry is in your system's PATH.


## Development Quick Start

```bash
poetry env activate
poetry install
poetry run python run.py
```
