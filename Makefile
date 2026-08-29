VENV ?= .venv

ifeq ($(OS),Windows_NT)
PYTHON ?= py -3.12
PYTHON_BIN := $(VENV)/Scripts/python.exe
else
PYTHON ?= python3.12
PYTHON_BIN := $(VENV)/bin/python
endif

INSTALL_MARKER := $(VENV)/.installed

.PHONY: install frontend-install frontend-build run run-prod test

install: $(INSTALL_MARKER)

$(INSTALL_MARKER): pyproject.toml
	$(PYTHON) -m venv $(VENV)
	$(PYTHON_BIN) -m pip install -e .
	$(PYTHON_BIN) -c "from pathlib import Path; Path('$(INSTALL_MARKER)').touch()"

frontend-install:
	cd frontend && bun install

frontend-build: frontend-install
	cd frontend && bun run build

run: $(INSTALL_MARKER) frontend-install
	@$(PYTHON_BIN) -m financial_engineering.app & backend_pid=$$!; \
	(cd frontend && bun run dev --host 127.0.0.1) & frontend_pid=$$!; \
	trap 'kill $$backend_pid $$frontend_pid 2>/dev/null || true' INT TERM EXIT; \
	wait $$backend_pid $$frontend_pid

run-prod: $(INSTALL_MARKER) frontend-build
	$(PYTHON_BIN) -m financial_engineering.app

test: $(INSTALL_MARKER)
	$(PYTHON_BIN) -m unittest discover -s tests -v
