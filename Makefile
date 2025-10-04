SHELL := /bin/bash

# Python virtual environment
VENV := .venv
ACT := . $(VENV)/bin/activate;

# Tools
PY := python3
PIP := pip3

.PHONY: help venv install run run-mock run-hw clean \
	docker-build docker-run docker-stop docker-rm docker-push docker-prod-build docker-prod-push \
	dockerx-create dockerx-build dockerx-push

help:
	@echo "Targets:"
	@echo "  venv        - create a local Python virtualenv in .venv"
	@echo "  install     - install dependencies into .venv"
	@echo "  run         - run the app (uses .env if present)"
	@echo "  run-mock    - run in mock mode (ENVIRONMENT=local)"
	@echo "  run-hw      - run for Orange Pi (ENVIRONMENT=hardware, LED_TYPE=WS2812)"
	@echo "  clean       - remove caches and build artifacts"
	@echo ""
	@echo "Docker (devcontainer compose):"
	@echo "  docker-build   - build the devcontainer image"
	@echo "  docker-run     - up the devcontainer (port 8080 exposed)"
	@echo "  docker-stop    - stop the devcontainer"
	@echo "  docker-rm      - remove the devcontainer and its image"
	@echo ""
	@echo "Docker (production image for OP5):"
	@echo "  docker-prod-build  - build production image (requires IMAGE=<name>)"
	@echo "  docker-prod-push   - push production image (requires IMAGE=<name>)"
	@echo ""
	@echo "Docker Buildx (multi-arch):"
	@echo "  dockerx-create     - create & use a buildx builder"
	@echo "  dockerx-build      - build multi-arch image (requires IMAGE=<name>)"
	@echo "  dockerx-push       - build+push multi-arch image (requires IMAGE=<name>)"

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

# -------- Docker Devcontainer helpers --------
DEV_SVC := dev
DEV_DIR := .devcontainer

docker-build:
	docker compose -f $(DEV_DIR)/docker-compose.yml build $(DEV_SVC)

docker-run:
	docker compose -f $(DEV_DIR)/docker-compose.yml up -d $(DEV_SVC)

docker-stop:
	docker compose -f $(DEV_DIR)/docker-compose.yml down

docker-rm:
	docker compose -f $(DEV_DIR)/docker-compose.yml down --rmi all --volumes --remove-orphans

# -------- Production image (for OP5) --------
# Usage:
#   make docker-prod-build IMAGE=youruser/aviation-weather:latest
#   make docker-prod-push  IMAGE=youruser/aviation-weather:latest

IMAGE ?=

docker-prod-build:
	@if [ -z "$(IMAGE)" ]; then echo "Set IMAGE=name:tag (e.g., youruser/aviation-weather:latest)"; exit 1; fi
	docker build -f Dockerfile.prod -t $(IMAGE) .

docker-prod-push:
	@if [ -z "$(IMAGE)" ]; then echo "Set IMAGE=name:tag"; exit 1; fi
	docker push $(IMAGE)

# -------- Buildx helpers --------
dockerx-create:
	docker buildx create --use --name awx-builder || true
	docker buildx inspect --bootstrap

dockerx-build:
	@if [ -z "$(IMAGE)" ]; then echo "Set IMAGE=name:tag"; exit 1; fi
	docker buildx build --platform linux/amd64,linux/arm64 -f Dockerfile.prod -t $(IMAGE) --load .

dockerx-push:
	@if [ -z "$(IMAGE)" ]; then echo "Set IMAGE=name:tag"; exit 1; fi
	docker buildx build --platform linux/amd64,linux/arm64 -f Dockerfile.prod -t $(IMAGE) --push .