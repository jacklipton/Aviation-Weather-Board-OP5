from __future__ import annotations

import requests
import json
import threading
from typing import List, Dict, Any, Optional

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

        # Ensure controller is ready
        self.controller.clear()

        used = []
        for st in stations:
            icao = st.get("icao", "").upper()
            if not icao:
                continue
            
            # Find the LED index assigned to this specific ICAO
            led_index = config.AIRPORT_LED_MAP.get(icao)
            
            cat = st.get("flight_category", "Unknown")
            # Extract rich data
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
                self.controller.set_pixel(led_index, color)
                rich_data["led_color"] = color

            used.append(rich_data)

        self.controller.show()
        
        with self._lock:
            self.last_weather_data = used

        return {"count": len(used), "airports": used}
