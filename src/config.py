import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional


# Load .env from repo root regardless of CWD
REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / ".env")


def getenv(name: str, default: Optional[str] = None) -> Optional[str]:
    """Wrapper that trims whitespace and returns default when missing."""
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip()


ENVIRONMENT = getenv("ENVIRONMENT", "local")  # local | hardware

# Networking / Server
HOST = getenv("HOST", "0.0.0.0")
PORT = int(getenv("PORT", "8080"))

# Weather / API
CHECKWX_API_KEY = getenv("CHECKWX_API_KEY", "")

# Airports as CSV string
AIRPORTS = getenv(
    "AIRPORTS",
    "CYGK,CYHM,CYKF,CYND,CYOO,CYOW,CYPQ,CYQA,CYSN,CYTR,CYTZ,CYXU,CYYZ,KBUF,KIAG,KMSS,KOGS",
)

# Refresh interval in seconds (default 15 minutes)
REFRESH_SECONDS = int(getenv("REFRESH_SECONDS", "900"))

# Light board settings
LED_COUNT = int(getenv("LED_COUNT", "50"))
LED_PIN = int(getenv("LED_PIN", "14"))  # Original MicroPython used Pin 14
LED_BRIGHTNESS = int(getenv("LED_BRIGHTNESS", "64"))  # 0-255
LED_TYPE = getenv("LED_TYPE", "mock")  # mock | APA102 | WS2812

# WS2812 over SPI (single-wire emulation via MOSI)
WS2812_SPI_BUS = int(getenv("WS2812_SPI_BUS", "0"))
WS2812_SPI_DEVICE = int(getenv("WS2812_SPI_DEVICE", "0"))
WS2812_SPI_SPEED_HZ = int(getenv("WS2812_SPI_SPEED_HZ", "3200000"))  # 3.2 MHz

# Basic auth for web UI (optional)
AUTH_USERNAME = getenv("AUTH_USERNAME", "")
AUTH_PASSWORD = getenv("AUTH_PASSWORD", "")

# LED order mapping for airports — index aligned with AIRPORTS order
DEFAULT_LED_ORDER = [14, 41, 44, 8, 21, 7, 19, 26, 35, 17, 31, 48, 32, 38, 36, 4, 1]

# Optional: override via comma-separated ints
LED_ORDER = [
    int(x)
    for x in getenv(
        "LED_ORDER",
        ",".join(str(i) for i in DEFAULT_LED_ORDER),
    ).split(",")
]

