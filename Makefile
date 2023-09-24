# Simple makefile to simplify repetitive build env management tasks under posix

CODESPELL_DIRS ?= ./
CODESPELL_SKIP ?= "*.pyc,*.txt,*.gif,*.png,*.jpg,*.ply,*.vtk,*.vti,*.js,*.html,*.doctree,*.ttf,*.woff,*.woff2,*.eot,*.mp4,*.inv,*.pickle,*.ipynb,flycheck*,./.git/*,./.hypothesis/*,*.yml,./doc/_build/*,./doc/images/*,./dist/*,*~,.hypothesis*,./doc/examples/*,*.mypy_cache/*,*cover,./tests/tinypages/_build/*,*/_autosummary/*"


stylecheck: codespell lint
test: apitest doctest

codespell:
	@echo "Running codespell"
	@codespell $(CODESPELL_DIRS) -S $(CODESPELL_SKIP)

pydocstyle:
	@echo "Running pydocstyle"
	@pydocstyle scooby --match='(?!coverage).*.py'

lint:
	@echo "Linting with flake8"
	flake8 --ignore=E501,W503,D10,E123,E203 scooby tests

doctest:
	@echo "Running module doctesting"
	pytest -v --doctest-modules scooby

apitest:
	@echo "Running full API tests"
	pytest -v --cov scooby --cov-report xml

format:
	@echo "Formatting"
	black .
	isort .
