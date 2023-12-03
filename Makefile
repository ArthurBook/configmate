.PHONY: all

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: setup
setup: # Installs project dependencies including all extras with Poetry.
	poetry install --all-extras

.PHONY: test
test: # Runs automated tests using pytest.
	export PYTHONPATH=./src/:$PYTHONPATH
	poetry run pytest

.PHONY: lint
lint: # Lints the code in the src/ and tests/ directories using pylint.
	poetry run pylint src/ tests/

.PHONY: typecheck
typecheck: # Performs type checking in the src/ and tests/ directories using mypy.
	poetry run mypy src/ tests/

.PHONY: format
format: # Formats the code in the src/ and tests/ directories using black.
	poetry run black src/ tests/

.PHONY: tox
tox: # Runs tests in multiple environments using tox.
	poetry run tox

.PHONY: linecount
linecount: # Counts the number of lines of Python code in the src/configmate/ directory.
	find src/configmate/ -name '*.py' -exec wc -l {} +