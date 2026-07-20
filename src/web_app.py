import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from . import config
from .light_controller import make_controller
from .weather_service import WeatherService

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WeatherBoard")

# --- Models ---

class WeatherData(BaseModel):
    icao: str
    flight_category: str
    led_index: Optional[int] = None
    led_color: Optional[tuple] = None
    observed: Optional[str] = None
    wind: Optional[Dict[str, Any]] = None
    visibility: Optional[Dict[str, Any]] = None
    clouds: Optional[List[Dict[str, Any]]] = None
    temperature: Optional[Dict[str, Any]] = None
    dewpoint: Optional[Dict[str, Any]] = None
    barometer: Optional[Dict[str, Any]] = None
    raw_text: Optional[str] = None
    station_name: Optional[str] = None

class SystemStatus(BaseModel):
    active: bool
    last_update: Optional[str] = None
    uptime_seconds: float = 0.0
    brightness: int = 255

class ControlResponse(BaseModel):
    ok: bool
    message: str

class BrightnessPayload(BaseModel):
    brightness: int

# --- Worker ---

class BackgroundWorker:
    def __init__(self, service: WeatherService):
        self.service = service
        self.active = True
        self.running = False
        self._task = None
        self._stop_event = asyncio.Event()
        self._trigger_event = asyncio.Event() # For instant refresh

    async def start(self):
        if self.running:
            return
        self.running = True
        self._stop_event.clear()
        self._task = asyncio.create_task(self._loop())
        logger.info("Background worker started.")

    async def stop(self):
        self.running = False
        self._stop_event.set()
        self._trigger_event.set() # Wake up to exit
        if self._task:
            await self._task
            self._task = None
        logger.info("Background worker stopped.")

    def trigger_refresh(self):
        self._trigger_event.set()

    async def _loop(self):
        while not self._stop_event.is_set():
            if self.active:
                try:
                    logger.info("Fetching weather update...")
                    # Run blocking sync code in thread pool
                    await asyncio.to_thread(self.service.fetch_and_update)
                    logger.info("Weather update complete.")
                except Exception as e:
                    logger.error(f"Error in background update: {e}")
            
            # Wait for refresh interval OR trigger
            try:
                # Wait for trigger or timeout
                await asyncio.wait_for(self._trigger_event.wait(), timeout=config.REFRESH_SECONDS)
                # If we get here, trigger happened
                self._trigger_event.clear()
            except asyncio.TimeoutError:
                # Timeout happened, just loop
                pass

# --- App Setup ---

controller = make_controller()
service = WeatherService(controller)
worker = BackgroundWorker(service)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        controller.setup()
        # Initial flash pattern
        if config.CHECKWX_API_KEY:
            controller.flash((0, 255, 0), 0.2, 1) # Green
        else:
            controller.flash((255, 0, 0), 0.2, 3) # Red

        await worker.start()
        yield
    finally:
        # Shutdown
        await worker.stop()
        controller.clear()

app = FastAPI(title="Aviation Weather Board", lifespan=lifespan)

# CORS (Allow local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints ---

@app.get("/api/status", response_model=SystemStatus)
async def get_status():
    return SystemStatus(
        active=worker.active,
        last_update=None, # Todo: Track timestamp in service
        uptime_seconds=0.0, # Todo: Track start time
        brightness=controller.spec.brightness
    )

@app.get("/api/weather", response_model=List[WeatherData])
async def get_weather():
    data = await asyncio.to_thread(service.get_current_weather)
    return data

@app.post("/api/control/start", response_model=ControlResponse)
async def start_board():
    controller.set_enabled(True) # Allow the strip to be painted again
    worker.active = True
    worker.trigger_refresh() # Instant update
    return ControlResponse(ok=True, message="Board started")

@app.post("/api/control/stop", response_model=ControlResponse)
async def stop_board():
    worker.active = False
    # Disable output first so any in-flight weather update can't relight the
    # strip after we clear it, then force every LED off. Run the clear in the
    # worker thread pool so hardware access stays off the event loop and shares
    # the controller lock with the update path.
    controller.set_enabled(False)
    await asyncio.to_thread(controller.clear)
    # We don't stop the loop, just the updates. The worker loop checks 'self.active'.
    return ControlResponse(ok=True, message="Board stopped")

@app.post("/api/control/refresh", response_model=ControlResponse)
async def refresh_board():
    worker.trigger_refresh()
    return ControlResponse(ok=True, message="Refresh triggered")

@app.post("/api/control/brightness", response_model=ControlResponse)
async def set_brightness(payload: BrightnessPayload):
    controller.set_brightness(payload.brightness)
    worker.trigger_refresh() # Re-render with new brightness
    return ControlResponse(ok=True, message=f"Brightness set to {payload.brightness}")

# --- Static Files ---
# Serve frontend if it exists, otherwise meaningful 404
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
else:
    @app.get("/")
    def index():
        return "Frontend not built. Please run 'npm run build' in frontend/ directory."
