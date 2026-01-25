# Development Guide

This project supports development on both your local machine (Mac/PC) and directly on the Orange Pi 5.

## Architecture
- **Language**: Python 3.11
- **Web Framework**: Flask
- **LED Driver**: Custom SPI bit-banging for WS2812 (on Hardware) / Mock Print (on Local)

## 1. Local Development (Mac/PC)

Develop the logic and web UI on your computer without needing the hardware.

### Setup
1.  Clone the repo.
2.  Create `.env` from the example:
    ```bash
    cp .env.example .env
    # Set ENVIRONMENT=local
    # Set CHECKWX_API_KEY
    ```
3.  Setup environment and install dependencies:
    ```bash
    # This automatically creates a .venv and installs requirements
    make install
    ```

### Running
```bash
make run-mock
```
Open `http://localhost:8080`.
The console will print "Mock lights" status instead of trying to access SPI hardware.

### Testing
Unit tests mock the API and Hardware to ensure logic correctness.
```bash
make test
```

## 2. Hardware Development (Orange Pi 5)

When testing the actual LED strip.

### Using Docker (Recommended)
See [DEPLOYMENT_OP5.md](DEPLOYMENT_OP5.md) for the Docker Compose workflow. This is the production-like way to run it.

### Direct Execution
If you want to run without Docker for debugging:
1.  Ensure `SPI` is enabled on the Pi (`orangepi-config`).
2.  Install system deps:
    ```bash
    sudo apt install python3-venv gcc python3-dev
    ```
3.  Setup Environment:
    ```bash
    # This automatically creates a .venv and installs requirements
    make install
    ```
4.  Configure `.env`:
    ```ini
    ENVIRONMENT=hardware
    LED_TYPE=WS2812
    # ... checks API key ...
    ```
5.  Run:
    ```bash
    make run-hw
    ```
    *(Note: Running SPI hardware may require root privileges. You can use `sudo -E make run-hw` if necessary).*

## Project Structure

- `src/main.py`: Application entry point.
- `src/web_server.py`: Flask app and background thread management.
- `src/weather_service.py`: Fetches METARs from CheckWX.
- `src/light_controller.py`:
    - `MockLightController`: Prints to console (Local mode).
    - `WS2812SPIController`: Drives LEDs via SPI (Hardware mode).
- `Dockerfile.prod`: The production image definition.