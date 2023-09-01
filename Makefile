.PHONY: \
	tests \
	lint \
	verify \
	install \
	.pre-commit \
	.install-deps

# Project constants
PYTHONDONTWRITEBYTECODE = 1 # To avoid .pyc files

PYTHON_VERSION ?= 2
PYTHON = python$(PYTHON_VERSION)
PYTHON_VENV = venv$(PYTHON_VERSION)

PYLINT_ARGS ?=
PYTEST_ARGS ?= --cov

PYTEST_CALL = python -m pytest $(PYTEST_ARGS)
PYLINT_CALL = pylint --rcfile=.pylintrc $(PYLINT_ARGS) scripts/* tests/*

install-deps:
	virtualenv -p '$(PYTHON)' $(PYTHON_VENV); \
	. $(PYTHON_VENV)/bin/activate; \
	pip install --upgrade -r requirements.txt
	touch $@

pre-commit:
	pre-commit install --install-hooks
	touch $@

install: install-deps pre-commit

tests: install-deps
	. $(PYTHON_VENV)/bin/activate; \
	$(PYTEST_CALL)

lint: install-deps
	. $(PYTHON_VENV)/bin/activate; \
	$(PYLINT_CALL)

verify: install-deps
	. $(PYTHON_VENV)/bin/activate; \
	$(PYLINT_CALL) && $(PYTEST_CALL)
