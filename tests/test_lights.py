import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.light_controller import MockLightController, WS2812SPIController, BoardSpec

class TestMockController(unittest.TestCase):
    def setUp(self):
        self.spec = BoardSpec(led_count=10)
        self.ctrl = MockLightController(self.spec)

    def test_set_pixel(self):
        self.ctrl.set_pixel(0, (10, 20, 30))
        self.assertEqual(self.ctrl._state[0], (10, 20, 30))
        # Verify others are still black
        self.assertEqual(self.ctrl._state[1], (0, 0, 0))

    def test_clear(self):
        self.ctrl.set_pixel(0, (255, 255, 255))
        self.ctrl.clear()
        self.assertEqual(self.ctrl._state[0], (0, 0, 0))

    def test_stop_is_authoritative_over_repaint(self):
        # Reproduces the "LED stays lit after Stop" bug: an update that lands
        # after the board is stopped must NOT relight the strip.
        self.ctrl.set_pixel(1, (0, 255, 0))
        self.ctrl.show()
        self.assertEqual(self.ctrl._displayed[1], (0, 255, 0))

        # Stop, as the /api/control/stop handler does it.
        self.ctrl.set_enabled(False)
        self.ctrl.clear()
        self.assertTrue(all(c == (0, 0, 0) for c in self.ctrl._displayed),
                        "clear() must turn every LED off")

        # A late / in-flight weather repaint arrives after Stop.
        self.ctrl.set_pixel(1, (0, 255, 0))
        self.ctrl.show()
        self.assertEqual(self.ctrl._displayed[1], (0, 0, 0),
                         "A stopped board must not relight LEDs")

    def test_start_re_enables_output(self):
        self.ctrl.set_enabled(False)
        self.ctrl.set_enabled(True)
        self.ctrl.set_pixel(2, (1, 2, 3))
        self.ctrl.show()
        self.assertEqual(self.ctrl._displayed[2], (1, 2, 3))

class TestWS2812Encoding(unittest.TestCase):
    def test_encode_byte(self):
        # 1 -> 110 (binary 6), 0 -> 100 (binary 4)
        # Test pattern 0b10000000 (128) -> should be 110 then seven 100s
        # 110 100 100 -> 11010010 (0xD2)
        # 100 100 100 -> 10010010 (0x92)
        # 100 100 ...
        
        # Let's test a simple known byte: 0xFF (all 1s)
        # 8 bits * 3 spi-bits = 24 spi-bits = 3 bytes
        # Each bit is 1 -> 110
        # 110 110 110 110 110 110 110 110
        # Byte 1: 110 110 11 -> 0b11011011 -> 0xDB
        # Byte 2: 0 110 110 1 -> 0b01101101 -> 0x6D
        # Byte 3: 10 110 110 -> 0b10110110 -> 0xB6
        
        encoded = WS2812SPIController._encode_byte(0xFF)
        self.assertEqual(encoded, [0xDB, 0x6D, 0xB6])

    def test_encode_zero(self):
        # 0x00 (all 0s)
        # Each bit is 0 -> 100
        # 100 100 100 100 100 100 100 100
        # Byte 1: 100 100 10 -> 0b10010010 -> 0x92
        # Byte 2: 0 100 100 1 -> 0b01001001 -> 0x49
        # Byte 3: 00 100 100 -> 0b00100100 -> 0x24
        
        encoded = WS2812SPIController._encode_byte(0x00)
        self.assertEqual(encoded, [0x92, 0x49, 0x24])

class TestWS2812Framing(unittest.TestCase):
    # Fastest clock the app supports; the reset must be long enough there too.
    MAX_SPI_HZ = 3_200_000

    @staticmethod
    def _leading_zero_bytes(payload):
        count = 0
        for byte in payload:
            if byte != 0x00:
                break
            count += 1
        return count

    def test_frame_begins_with_reset_pulse(self):
        # Reproduces the "first LED keeps its old colour" bug. Without a reset
        # before the data, pixel 0's first bits land on the SPI controller's
        # startup edge and get mis-read, so LED 0 latches garbage while every
        # downstream pixel is fine.
        payload = WS2812SPIController._build_payload([(0, 255, 0)])
        lead_us = self._leading_zero_bytes(payload) * 8 / self.MAX_SPI_HZ * 1e6
        self.assertGreaterEqual(
            lead_us, 50.0,
            "WS2812 needs >=50us low before data or pixel 0 mis-reads the frame")

    def test_frame_ends_with_latch(self):
        payload = WS2812SPIController._build_payload([(0, 255, 0)])
        trail_us = self._leading_zero_bytes(payload[::-1]) * 8 / self.MAX_SPI_HZ * 1e6
        self.assertGreaterEqual(trail_us, 50.0, "frame must latch after the data")

    def test_pixel_data_follows_the_reset(self):
        payload = WS2812SPIController._build_payload([(0x00, 0xFF, 0x00)])
        start = self._leading_zero_bytes(payload)
        expected = (WS2812SPIController._encode_byte(0x00)
                    + WS2812SPIController._encode_byte(0xFF)
                    + WS2812SPIController._encode_byte(0x00))
        self.assertEqual(payload[start:start + len(expected)], expected,
                         "GRB data must be transmitted intact after the reset")

if __name__ == '__main__':
    unittest.main()
