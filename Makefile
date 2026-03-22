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
	@echo "Available targets:"
	@echo "  make install              # install app + dev dependencies"
	@echo "  make install-prod         # install only runtime dependencies"
	@echo "  make lock                 # refresh poetry.lock"
	@echo "  make check                # run django system checks"
	@echo "  make makemigrations       # create migrations"
	@echo "  make migrate              # apply migrations"
	@echo "  make run                  # run Django dev server"
	@echo "  make test                 # run tests"
	@echo "  make schema               # validate and export OpenAPI schema"
	@echo "  make lint                 # run ruff"
	@echo "  make format               # run black"
	@echo "  make pre-commit-install   # install git hooks"
	@echo "  make pre-commit-run       # run pre-commit for all files"
	@echo "  make docker-dev-up        # build and start dev compose stack"
	@echo "  make docker-dev-down      # stop dev compose stack"
	@echo "  make docker-prod-up       # build and start prod compose stack"
	@echo "  make docker-prod-down     # stop prod compose stack"
	@echo "  make docker-logs          # tail compose logs"

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
	$(MANAGE) test

schema:
	$(MANAGE) spectacular --file schema.yaml --validate

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
