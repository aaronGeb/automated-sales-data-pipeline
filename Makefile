.PHONY: install test lint format run

install:
	uv sync

test:
	uv run pytest

lint:
	uv run ruff check . && uv run mypy

format:
	uv run ruff format . && uv run ruff check . --fix

run:
	uv run sales-pipeline