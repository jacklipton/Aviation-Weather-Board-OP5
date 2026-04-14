from __future__ import annotations

import logging
import requests
import json
import threading
from typing import List, Dict, Any, Optional

logger = logging.getLogger("WeatherBoard")

from . import config
from .light_controller import BaseLightController, color_for_flight_category


class WeatherService:
    def __init__(self, controller: BaseLightController):
        self.controller = controller
        self.last_weather_data: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def get_current_weather(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self.last_weather_data)

    def fetch_and_update(self) -> dict:
        """Fetch weather, update the lightboard, and cache the data.

        Returns a summary dict for UI.
        """
        airports_csv = config.AIRPORTS
        api_key = config.CHECKWX_API_KEY
        if not api_key:
            # Fallback or specific behavior if no key? 
            # For now, raising error as before, but maybe log it.
            raise RuntimeError("Missing CHECKWX_API_KEY in environment/.env")

        url = f"https://api.checkwx.com/metar/{airports_csv}/decoded"
        headers = {"X-API-Key": api_key}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()

        data = r.json()
        stations = data.get("data", [])

        # Build a lookup of last known data so we can fall back to it for any
        # airport the API omits in a partial response.
        with self._lock:
            last_by_icao = {d["icao"]: d for d in self.last_weather_data}

        # Parse fresh data from the API response.
        fresh_by_icao: dict = {}
        for st in stations:
            icao = st.get("icao", "").upper()
            if not icao:
                continue

            led_index = config.AIRPORT_LED_MAP.get(icao)
            cat = st.get("flight_category", "Unknown")
            rich_data = {
                "icao": icao,
                "flight_category": cat,
                "led_index": led_index,
                "observed": st.get("observed"),
                "wind": st.get("wind", {}),
                "visibility": st.get("visibility", {}),
                "clouds": st.get("clouds", []),
                "temperature": st.get("temperature", {}),
                "dewpoint": st.get("dewpoint", {}),
                "barometer": st.get("barometer", {}),
                "raw_text": st.get("raw_text", ""),
                "station_name": st.get("station", {}).get("name", "")
            }
            if led_index is not None:
                color = color_for_flight_category(cat)
                rich_data["led_color"] = color
            fresh_by_icao[icao] = rich_data

        # For any configured airport missing from this response, keep its last
        # known data so a partial API response doesn't blank out LEDs.
        missing = [icao for icao in config.AIRPORT_LIST if icao not in fresh_by_icao]
        if missing:
            logger.warning("API response missing %d airport(s): %s — using last known state", len(missing), missing)
        for icao in missing:
            if icao in last_by_icao:
                fresh_by_icao[icao] = last_by_icao[icao]

        # Rebuild display in configured airport order so LED indices are consistent.
        used = [fresh_by_icao[icao] for icao in config.AIRPORT_LIST if icao in fresh_by_icao]

        # Update LEDs. Clear first, then paint every airport we have data for.
        self.controller.clear()
        for entry in used:
            led_index = entry.get("led_index")
            color = entry.get("led_color")
            if led_index is not None and color is not None:
                self.controller.set_pixel(led_index, color)
        self.controller.show()

        with self._lock:
            self.last_weather_data = used

        return {"count": len(used), "airports": used}
