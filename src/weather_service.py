from __future__ import annotations

import requests
import json
from typing import List

from . import config
from .light_controller import BaseLightController, color_for_flight_category


class WeatherService:
    def __init__(self, controller: BaseLightController):
        self.controller = controller

    def fetch_and_update(self) -> dict:
        """Fetch weather and update the lightboard.

        Returns a summary dict for UI.
        """
        airports_csv = config.AIRPORTS
        api_key = config.CHECKWX_API_KEY
        if not api_key:
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
            
            if led_index is not None:
                cat = st.get("flight_category", "") or ""
                color = color_for_flight_category(cat)
                self.controller.set_pixel(led_index, color)
                used.append({
                    "icao": icao,
                    "flight_category": cat,
                    "led": led_index,
                    "color": color,
                })

        self.controller.show()
        return {"count": len(used), "airports": used}
