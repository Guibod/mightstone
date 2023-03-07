#
# vim:ft=make
# Makefile
#
.DEFAULT_GOAL := help
.PHONY: test help


help:  ## these help instructions
	@sed -rn 's/^([a-zA-Z_-]+):.*?## (.*)$$/"\1" "\2"/p' < $(MAKEFILE_LIST)|xargs printf "make %-20s# %s\n"

hidden: # example undocumented, for internal usage only
	@true

pydoc: ## Run a pydoc server and open the browser
	poetry run python -m pydoc -b

install: ## Run `poetry install`
	poetry install

showdeps: ## run poetry to show deps
	@echo "CURRENT:"
	poetry show --tree
	@echo
	@echo "LATEST:"
	poetry show --latest

lint: ## Runs black, isort, bandit, flake8 in check mode
	poetry run black --check .
	poetry run isort --check .
	poetry run bandit -r src
	poetry run flake8 src tests
	poetry run mypy src tests

doc:
	poetry run sphinx-build -M html "docs/source" "docs/build"
	open docs/build/html/index.html

format: ## Formats you code with Black
	poetry run isort .
	poetry run black --preview .

test: hidden ## run pytest with coverage
	poetry run pytest -v --cov mightstone

build: install lint test ## run `poetry build` to build source distribution and wheel
	poetry build

pyinstaller: install lint test ## Create a binary executable using pyinstaller
	poetry run pyinstaller src/mightstone/cli.py --onefile --name mightstone

run: ## run `poetry run mightstone`
	poetry run mightstone
