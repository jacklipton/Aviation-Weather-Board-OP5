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

if __name__ == '__main__':
    unittest.main()
