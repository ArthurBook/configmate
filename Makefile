.PHONY: setup test lint typecheck format tox

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

linecount:
	find src/configmate/ -name '*.py' -exec wc -l {} +