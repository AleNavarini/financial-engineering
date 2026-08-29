VENV ?= .venv

ifeq ($(OS),Windows_NT)
PYTHON ?= py -3.12
PYTHON_BIN := $(VENV)/Scripts/python.exe
else
PYTHON ?= python3.12
PYTHON_BIN := $(VENV)/bin/python
endif

INSTALL_MARKER := $(VENV)/.installed

.PHONY: install run run-prod test

install: $(INSTALL_MARKER)

$(INSTALL_MARKER): pyproject.toml
	$(PYTHON) -m venv $(VENV)
	$(PYTHON_BIN) -m pip install -e .
	$(PYTHON_BIN) -c "from pathlib import Path; Path('$(INSTALL_MARKER)').touch()"

run: $(INSTALL_MARKER)
	$(PYTHON_BIN) -m financial_engineering.app

run-prod: $(INSTALL_MARKER)
	$(PYTHON_BIN) -m financial_engineering.app

test: $(INSTALL_MARKER)
	$(PYTHON_BIN) -m unittest discover -s tests -v
