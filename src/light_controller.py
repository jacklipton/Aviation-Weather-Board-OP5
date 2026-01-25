from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import List, Tuple

from . import config


Color = Tuple[int, int, int]  # GRB in original MicroPython order


@dataclass
class BoardSpec:
    led_count: int
    brightness: int = 64  # 0-255


class BaseLightController:
    def __init__(self, spec: BoardSpec):
        self.spec = spec

    def setup(self) -> None:
        raise NotImplementedError

    def set_pixel(self, index: int, color: Color) -> None:
        raise NotImplementedError

    def show(self) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        for i in range(self.spec.led_count):
            self.set_pixel(i, (0, 0, 0))
        self.show()

    def flash(self, color: Color, seconds: float = 0.5, repeats: int = 3) -> None:
        for _ in range(repeats):
            for i in range(self.spec.led_count):
                self.set_pixel(i, color)
            self.show()
            time.sleep(seconds)
            self.clear()
            time.sleep(seconds)


class MockLightController(BaseLightController):
    def __init__(self, spec: BoardSpec):
        super().__init__(spec)
        self._state: List[Color] = [(0, 0, 0)] * spec.led_count

    def setup(self) -> None:
        print("🧪 Mock lights ready:", self.spec)

    def set_pixel(self, index: int, color: Color) -> None:
        if 0 <= index < self.spec.led_count:
            self._state[index] = color

    def show(self) -> None:
        # Compact visualization: count non-black and show first few entries
        lit = sum(1 for c in self._state if c != (0, 0, 0))
        preview = ", ".join(str(self._state[i]) for i in range(min(8, self.spec.led_count)))
        print(f"✳️  Show: {lit} lit | [{preview}{'...' if self.spec.led_count>8 else ''}]")


class WS2812SPIController(BaseLightController):
    """WS2812/NeoPixel via SPI using bit expansion technique.

    Encodes each data bit into 3 SPI bits at ~3.2MHz to approximate WS2812 timing.
    Input color order remains (G, R, B) for compatibility with original code.
    """

    def __init__(self, spec: BoardSpec):
        super().__init__(spec)
        import spidev  # type: ignore
        self.spi = spidev.SpiDev()
        self.bus = config.WS2812_SPI_BUS
        self.dev = config.WS2812_SPI_DEVICE
        self.speed = config.WS2812_SPI_SPEED_HZ
        self._grb: List[Color] = [(0, 0, 0)] * self.spec.led_count

    def setup(self) -> None:
        self.spi.open(self.bus, self.dev)
        self.spi.max_speed_hz = self.speed
        self.spi.mode = 0
        print(f"🔧 WS2812 (SPI emu) on /dev/spidev{self.bus}.{self.dev} @{self.speed}Hz: {self.spec}")

    @staticmethod
    def _encode_byte(b: int) -> List[int]:
        # 8 bits -> 8 * 3 bits packed into bytes
        # We'll map bit 1 -> 110, bit 0 -> 100
        out_bits = []
        for i in range(8)[::-1]:
            bit = (b >> i) & 1
            if bit:
                out_bits += [1, 1, 0]
            else:
                out_bits += [1, 0, 0]
        # pack bits into bytes MSB first
        out = []
        acc = 0
        for i, bit in enumerate(out_bits):
            acc = (acc << 1) | bit
            if (i % 8) == 7:
                out.append(acc)
                acc = 0
        if len(out_bits) % 8 != 0:
            acc <<= (8 - (len(out_bits) % 8))
            out.append(acc)
        return out

    def set_pixel(self, index: int, color: Color) -> None:
        if 0 <= index < self.spec.led_count:
            g, r, b = color
            # brightness scaling (software)
            scale = max(0, min(255, self.spec.brightness)) / 255.0
            g = int(g * scale) & 0xFF
            r = int(r * scale) & 0xFF
            b = int(b * scale) & 0xFF
            self._grb[index] = (g, r, b)

    def show(self) -> None:
        payload: List[int] = []
        for (g, r, b) in self._grb:
            payload += self._encode_byte(g)
            payload += self._encode_byte(r)
            payload += self._encode_byte(b)
        # Latch: low for >50us, achieved with SPI idle; sending zeros helps
        payload += [0x00] * 64
        try:
            self.spi.xfer2(payload)
        except Exception as e:
            print("SPI write failed:", e)


def make_controller() -> BaseLightController:
    spec = BoardSpec(led_count=config.LED_COUNT, brightness=config.LED_BRIGHTNESS)
    if config.ENVIRONMENT == "hardware":
        led_type = (config.LED_TYPE or "").upper()
        if led_type == "WS2812":
            try:
                return WS2812SPIController(spec)
            except Exception as e:
                print("⚠️  WS2812 init error, falling back to mock:", e)
                return MockLightController(spec)
        elif led_type == "APA102":
            # Placeholder: could implement APA102 later if you switch
            print("⚠️  APA102 not enabled; using mock.")
            return MockLightController(spec)
        else:
            print("⚠️  Unsupported LED_TYPE; using mock.")
            return MockLightController(spec)
    return MockLightController(spec)


# Utilities for mapping flight categories to colors
FLIGHT_COLORS = {
    "VFR": (255, 0, 0),   # Green (GRB)
    "MVFR": (0, 0, 255),  # Blue
    "IFR": (0, 255, 0),   # Red
    "LIFR": (0, 255, 255), # Pink
}

def color_for_flight_category(cat: str) -> Color:
    return FLIGHT_COLORS.get(cat.upper(), (0, 0, 0))
