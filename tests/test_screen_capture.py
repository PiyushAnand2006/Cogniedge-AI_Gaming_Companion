"""
Unit Tests for Screen Capture Worker
Tests hardware tier adaptive FPS rate scaling, JPEG encoding, and frame buffer access.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

SERVICES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../services"))
sys.path.insert(0, SERVICES_DIR)

from screen_capture import ScreenCaptureWorker, TIER_FPS_MAPPING


class TestScreenCaptureWorker(unittest.TestCase):

    def test_tier_adaptive_fps(self):
        """Verify capture FPS matches hardware tier assignment."""
        worker_floor = ScreenCaptureWorker(hardware_tier="floor")
        self.assertEqual(worker_floor.capture_fps, 1.0)
        self.assertEqual(worker_floor.capture_interval, 1.0)

        worker_mid = ScreenCaptureWorker(hardware_tier="mid")
        self.assertEqual(worker_mid.capture_fps, 2.5)

        worker_high = ScreenCaptureWorker(hardware_tier="high")
        self.assertEqual(worker_high.capture_fps, 5.0)

    def test_dynamic_tier_adaptation(self):
        """Verify dynamic adjustment of tier updates FPS and interval."""
        worker = ScreenCaptureWorker(hardware_tier="floor")
        self.assertEqual(worker.capture_fps, 1.0)

        worker.adapt_to_hardware_tier("high")
        self.assertEqual(worker.capture_fps, 5.0)
        self.assertEqual(worker.capture_interval, 0.2)

    def test_status_reporting(self):
        """Verify get_status returns expected structure."""
        worker = ScreenCaptureWorker(hardware_tier="mid")
        status = worker.get_status()
        self.assertIn("is_running", status)
        self.assertIn("capture_fps", status)
        self.assertIn("hardware_tier", status)
        self.assertEqual(status["hardware_tier"], "mid")
        self.assertEqual(status["provenance"], "MEASURED")

    def test_jpeg_encoding_with_synthetic_frame(self):
        """Verify get_latest_jpeg_frame compresses raw RGB bytes to valid JPEG."""
        worker = ScreenCaptureWorker()
        width, height = 320, 240
        # Synthetic RGB frame (320x240x3)
        raw_rgb = b"\x80" * (width * height * 3)

        with worker._frame_lock:
            worker._latest_frame = raw_rgb
            worker._latest_frame_size = (width, height)

        jpeg_bytes = worker.get_latest_jpeg_frame(quality=60)
        self.assertIsNotNone(jpeg_bytes)
        # JPEG header starts with 0xFF 0xD8
        self.assertTrue(jpeg_bytes.startswith(b"\xff\xd8"))


if __name__ == "__main__":
    unittest.main()
