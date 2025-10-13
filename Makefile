#################################################################################
# GLOBALS                                                                       #
#################################################################################
PROJECT_NAME = proyecto_ing_datos
PYTHON_VERSION = 3.13
PYTHON_INTERPRETER = python

# Detectar si estamos en Windows
ifeq ($(OS),Windows_NT)
    VENV_PYTHON = .venv/Scripts/python.exe
    VENV_ACTIVATE = .venv/Scripts/activate
else
    VENV_PYTHON = .venv/bin/python
    VENV_ACTIVATE = .venv/bin/activate
endif

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python dependencies
.PHONY: requirements
requirements:
	$(PYTHON_INTERPRETER) -m pip install -U pip
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using ruff (use `make format` to do formatting)
.PHONY: lint
lint:
	ruff format --check
	ruff check

## Format source code with ruff
.PHONY: format
format:
	ruff check --fix
	ruff format

## Set up Python interpreter environment
.PHONY: create_environment
create_environment:
	python -m venv .venv
	@echo ">>> New virtualenv created. Activate with: .venv\Scripts\activate (Windows) or source .venv/bin/activate (Linux/Mac)"

## Download datasets
.PHONY: make_dataset
make_dataset:
	$(VENV_PYTHON) proyecto_ciencia_de_datos/data/make_dataset.py

## Clean and tidy datasets
.PHONY: tidy_data
tidy_data:
	$(VENV_PYTHON) proyecto_ciencia_de_datos/data/tidy_data.py

## Full pipeline: download and tidy
.PHONY: pipeline
pipeline:
	@echo ">>> Ejecutando pipeline completo..."
	@$(MAKE) make_dataset
	@$(MAKE) tidy_data
# 	@$(MAKE) verify_encoding
	@echo ">>> Pipeline completado."

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

## Make dataset
.PHONY: data
data: requirements
	$(PYTHON_INTERPRETER) proyecto_ciencia_de_datos/dataset.py

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "$(PRINT_HELP_PYSCRIPT)" < $(MAKEFILE_LIST)