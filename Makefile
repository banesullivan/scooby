# Simple makefile to simplify repetitive build env management tasks under posix

.DEFAULT_GOAL := test

.PHONY: all clean sync-deps lint test doctest coverage build

all: test

clean:
	@echo "Cleaning build and coverage artifacts"
	@rm -rf build dist .pytest_cache .ruff_cache htmlcov coverage*.xml coverage*.html .coverage *.egg-info

sync-deps:
	@echo "Installing dev dependencies"
	@uv sync --group dev

lint:
	@echo "Running pre-commit"
	@uv run pre-commit run --all-files

test:
	@echo "Running tests"
	@uv run pytest -v --cov scooby --cov-report xml

doctest:
	@echo "Running doctests"
	@uv run pytest -v --doctest-modules scooby

coverage:
	@echo "Running coverage with HTML report"
	@uv run pytest -v --cov scooby --cov-report html

build:
	@echo "Building distribution"
	@uv build
