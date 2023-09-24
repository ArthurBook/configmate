.PHONY: install test lint typecheck format clean

setup:
	poetry install --all-extras

test:
	poetry run pytest

lint:
	poetry run pylint src/ tests/

typecheck:
	poetry run mypy src/ tests/

format:
	poetry run black src/ tests/

tox:
	poetry run tox