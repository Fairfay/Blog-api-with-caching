SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

POETRY ?= poetry
COMPOSE ?= docker compose
PYTHON := $(POETRY) run python
MANAGE := $(PYTHON) manage.py

.PHONY: help \
	install install-prod lock \
	check makemigrations migrate run test schema \
	lint format pre-commit-install pre-commit-run \
	docker-dev-up docker-dev-down docker-prod-up docker-prod-down docker-logs \
	backend-dev backend-dev-down backend-prod backend-prod-down \
	run-project-dev down-project-dev run-project-prod down-project-prod upgrade \
	clean

help:
	@echo "Доступные команды:"
	@echo "  make install              # установить приложение и зависимости разработки"
	@echo "  make install-prod         # установить только основные зависимости"
	@echo "  make lock                 # обновить poetry.lock"
	@echo "  make check                # запустить django system checks"
	@echo "  make makemigrations       # создать миграции"
	@echo "  make migrate              # применить миграции"
	@echo "  make run                  # запустить dev-сервер Django"
	@echo "  make test                 # запустить тесты"
	@echo "  make schema               # проверить и выгрузить схему OpenAPI"
	@echo "  make lint                 # запустить ruff"
	@echo "  make format               # запустить black"
	@echo "  make pre-commit-install   # установить git hooks"
	@echo "  make pre-commit-run       # запустить pre-commit для всех файлов"
	@echo "  make docker-dev-up        # собрать и поднять dev-стек"
	@echo "  make docker-dev-down      # остановить dev-стек"
	@echo "  make docker-prod-up       # собрать и поднять продакшен-стек"
	@echo "  make docker-prod-down     # остановить продакшен-стек"
	@echo "  make docker-logs          # показать логи compose"

install:
	$(POETRY) install --with dev

install-prod:
	$(POETRY) install --only main

lock:
	$(POETRY) lock

check:
	$(MANAGE) check

makemigrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

run:
	$(MANAGE) runserver

test:
	$(POETRY) run pytest

schema:
	$(MANAGE) spectacular --file docs/schema.yml --validate

lint:
	$(POETRY) run ruff check .

format:
	$(POETRY) run black .

pre-commit-install:
	$(POETRY) run pre-commit install

pre-commit-run:
	$(POETRY) run pre-commit run --all-files

docker-dev-up:
	$(COMPOSE) up -d --build

docker-dev-down:
	$(COMPOSE) down

docker-prod-up:
	$(COMPOSE) -f docker-compose.prod.yml up -d --build

docker-prod-down:
	$(COMPOSE) -f docker-compose.prod.yml down

docker-logs:
	$(COMPOSE) logs -f

backend-dev: docker-dev-up

backend-dev-down: docker-dev-down

backend-prod: docker-prod-up

backend-prod-down: docker-prod-down

run-project-dev: docker-dev-up

down-project-dev: docker-dev-down

run-project-prod: docker-prod-up

down-project-prod: docker-prod-down

upgrade: docker-prod-up

clean:
	find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	find . -type d -name '__pycache__' -delete
