DEVPI_URL ?= https://devpi.qa.stormsec.com.br/deploy/dev/+simple

.PHONY: clean clean-test clean-pyc clean-build docs help tests uninstall_all install install_dev
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

define UNINSTALL_ALL_PYSCRIPT
import os
from requirements import requirements

for package in [x.split('==')[0] for x in requirements]:
	print('package')
	if package.strip():
		os.system('pip uninstall --yes %s' % package)
endef

export UNINSTALL_ALL_PYSCRIPT

uninstall_all:
	@python -c "$$UNINSTALL_ALL_PYSCRIPT"

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

tests:
	@python3 -m pytest -s -vv --cov=tests --cov=playerstars_graphql_adapters -W ignore::DeprecationWarning --cov-report html --cov-report term-missing:skip-covered
	@echo "Linting..."
	@flake8 playerstars_graphql_adapters/ --max-complexity=5
	@flake8 tests/ --ignore=S101,S311,F811
	@echo "\033[32mTudo certo!"

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/playerstars_graphql_adapters.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ playerstars_graphql_adapters
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

install_dev: install
	pip install -r requirements_dev.txt

install: clean  uninstall_all  ## install the package to the active Python's site-packages
	pip install devpi-client
	devpi use $(DEVPI_URL) --always-set-cfg=yes
	pip install -e .

upload: clean
	pip install devpi-client
	devpi use $(DEVPI_URL) --always-set-cfg=yes
	devpi login $(DEVPI_USER) --password=$(DEVPI_PASSWORD)
	python setup.py bdist_wheel
	devpi upload --from-dir dist/
