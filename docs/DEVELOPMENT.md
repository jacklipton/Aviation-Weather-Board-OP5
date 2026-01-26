# Development Guide

This project supports development on both your local machine (Mac/PC) and directly on the Orange Pi 5.

## Architecture
- **Backend**: Python 3.11 with **FastAPI** (Async)
- **Frontend**: **React 18** with **Tailwind CSS** (Vite-based)
- **LED Driver**: Custom SPI bit-banging for WS2812 (on Hardware) / Mock Print (on Local)

## 1. Local Development (Mac/PC)

Develop the logic and web UI on your computer without needing the hardware.

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)

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
    # This creates a .venv, installs Python requirements, and runs npm install
    make install
    ```

### Running
```bash
make run-mock
```
This target will:
1. Build the frontend (`npm run build`).
2. Start the FastAPI server on `http://localhost:8080`.

**Note for UI Development**: 
If you are only editing the React frontend, you can run the Vite dev server for instant reloads:
```bash
cd frontend
npm run dev
```
(Vite is configured to proxy `/api` requests to the Python server at `:8080`).

### Testing
```bash
make test
```

## 2. Hardware Development (Orange Pi 5)

### Using Docker (Recommended)
See [DEPLOYMENT_OP5.md](DEPLOYMENT_OP5.md) for the Docker Compose workflow.

### Direct Execution
1.  Ensure `SPI` is enabled (`orangepi-config`).
2.  Install system deps: `sudo apt install python3-venv gcc python3-dev nodejs npm`
3.  `make install`
4.  Run: `make run-hw`

## Project Structure

- `src/main.py`: Entry point (Uvicorn launcher).
- `src/web_app.py`: FastAPI application and background async worker.
- `src/weather_service.py`: Fetches and caches rich METAR data.
- `src/light_controller.py`: Hardware abstraction for LEDs.
- `frontend/`: React source code.
- `frontend/dist/`: Built static assets (served by FastAPI).
- `Dockerfile.prod`: Multi-stage build (Node -> Python).