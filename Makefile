SHELL := /bin/bash

.PHONY: up down logs build fmt api-shell matcher-shell

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

build:
	docker compose build --no-cache

api-shell:
	docker compose exec api bash

matcher-shell:
	docker compose exec matcher bash
