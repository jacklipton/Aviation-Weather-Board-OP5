from __future__ import annotations

import requests
import json
from typing import List

import config
from light_controller import BaseLightController, color_for_flight_category


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
        for i, st in enumerate(stations):
            if i >= len(config.LED_ORDER):
                break
            cat = st.get("flight_category", "") or ""
            color = color_for_flight_category(cat)
            led_index = config.LED_ORDER[i]
            self.controller.set_pixel(led_index, color)
            used.append({
                "icao": st.get("icao", st.get("station", {}).get("name", f"#{i}")),
                "flight_category": cat,
                "led": led_index,
                "color": color,
            })

        self.controller.show()
        return {"count": len(used), "airports": used}
