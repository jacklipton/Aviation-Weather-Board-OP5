# Development guide

This project is designed to be developed primarily inside a Dev Container and deployed as a Docker image to run on Orange Pi 5.

## Options

- Dev Container (recommended)
- Local venv (optional)

## Dev Container workflow

1) Start the container
```bash
make docker-run
```

2) Open in VS Code Dev Containers or attach a shell, then run the app
```bash
# Mock mode on your laptop
make run-mock

# Hardware mode on the OP5
make run-hw
```

3) Environment configuration
- Copy `.env.example` to `.env` and edit as needed.
- Important keys:
  - `ENVIRONMENT`: local | hardware
  - `LED_TYPE`: WS2812
  - `CHECKWX_API_KEY`: your CheckWX key
  - `AUTH_USERNAME`/`AUTH_PASSWORD`: Basic Auth for the phone UI
  - `AIRPORTS`, `LED_ORDER`, `LED_COUNT`: mapping and count
  - `WS2812_SPI_BUS`/`DEVICE`/`SPEED_HZ`: SPI device to use for the data pin

4) Stop the container
```bash
make docker-stop
```

5) Remove container + image
```bash
make docker-rm
```

## Local venv workflow (optional)

```bash
make venv
make install
make run-mock  # or: make run
```

## Makefile targets

- `venv` / `install` / `run` / `run-mock` / `run-hw` / `clean`
- Docker (devcontainer): `docker-build`, `docker-run`, `docker-stop`, `docker-rm`
- Docker (prod): `docker-prod-build IMAGE=...`, `docker-prod-push IMAGE=...`
- Docker Buildx (multi-arch): `dockerx-create`, `dockerx-build IMAGE=...`, `dockerx-push IMAGE=...`

## Phone UI

Open `http://<host>:8080`. If `AUTH_USERNAME`/`AUTH_PASSWORD` are set, a Basic Auth prompt appears.

- Start: begins periodic weather refresh
- Stop: turns off LEDs and stops refreshing
- Refresh Now: fetches and applies latest weather immediately
