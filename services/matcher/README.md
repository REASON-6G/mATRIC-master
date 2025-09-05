# Matcher Service

This is a standalone service that manages subscriptions and topic queues for the mATRIC platform.  
It polls the `subscriptions` and `topics` tables in MongoDB and ensures RabbitMQ queues are properly bound for each subscriber.

---

## Table of Contents
- [Environment Variables](#environment-variables)  
- [Dependencies](#dependencies)  
- [Development Quick Start](#development-quick-start)  
- [Running in Docker](#running-in-docker)  

---

## Environment Variables

The Matcher Service reads configuration from environment variables. Create a `.env` file or duplicate `example.env` to set the following variables:

| Variable              | Description | Default / Notes |
|-----------------------|------------|----------------|
| `MONGO_URI`           | MongoDB connection string | `"mongodb://localhost:27017/matchingservice"` |
| `RABBITMQ_URL`        | RabbitMQ connection URL | `"amqp://admin:changeme@rabbitmq:5672/"` |
| `RABBITMQ_EXCHANGE`   | RabbitMQ exchange for topic messages | `"topics"` |
| `POLL_INTERVAL`       | Interval in seconds to poll subscriptions/topics | `5` |

---

## Dependencies

- Python 3.12+  
- [Poetry](https://python-poetry.org/) for dependency management
- `aio-pika` for async RabbitMQ connections
- `pymongo` for MongoDB access
- `python-dotenv` for `.env` support

Install Poetry if you don’t have it:

On Linux / macOS:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

On Windows PowerShell:

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

Ensure Poetry is in your system's PATH.

## Development Quick Start

poetry env activate
poetry install
poetry run matcher