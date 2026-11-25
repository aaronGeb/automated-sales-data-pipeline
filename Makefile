.PHONY: install up down test lint format run report

install:
	uv sync

up:
	docker compose up -d

down:
	docker compose down

test:
	uv run pytest tests

lint:
	uv run ruff check . && uv run mypy

format:
	uv run ruff format . && uv run ruff check . --fix

run:
	uv run sales-pipeline run "$(FILE)"

report:
	uv run sales-pipeline report