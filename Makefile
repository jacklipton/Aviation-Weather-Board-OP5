SHELL := /bin/bash

# Python virtual environment
VENV := .venv
ACT := . $(VENV)/bin/activate;

# Tools
PY := python3
PIP := pip3

.PHONY: help venv install run run-mock run-hw clean

help:
	@echo "Targets:"
	@echo "  venv        - create a local Python virtualenv in .venv"
	@echo "  install     - install dependencies into .venv"
	@echo "  run         - run the app (uses .env if present)"
	@echo "  run-mock    - run in mock mode (ENVIRONMENT=local)"
	@echo "  run-hw      - run for Orange Pi (ENVIRONMENT=hardware, LED_TYPE=WS2812)"
	@echo "  clean       - remove caches and build artifacts"

venv:
	$(PY) -m venv $(VENV)

install: venv
	$(ACT) $(PIP) install --upgrade pip
	$(ACT) $(PIP) install -r requirements.txt

run: install
	$(ACT) $(PY) run.py

run-mock: install
	ENVIRONMENT=local $(ACT) $(PY) run.py

run-hw: install
	ENVIRONMENT=hardware LED_TYPE=WS2812 $(ACT) $(PY) run.py

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache .mypy_cache build dist *.egg-info