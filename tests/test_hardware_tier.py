"""
Unit Tests for Hardware Tier Detection Subsystem
Tests tier assignment logic, caching, rescan behavior, and schema compliance.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

SERVICES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../services"))
PERF_DIR = os.path.join(SERVICES_DIR, "performance")
sys.path.insert(0, SERVICES_DIR)
sys.path.insert(0, PERF_DIR)

from hardware_tier import HardwareTierDetector, get_tier_configuration, GPUSummary


class TestHardwareTierDetection(unittest.TestCase):

    def test_floor_tier_assignment(self):
        """Test ~16GB RAM with no GPU assigns 'floor' tier and produces null GPU."""
        detector = HardwareTierDetector()
        
        # Mock 16GB RAM and no GPU
        with patch("psutil.virtual_memory") as mock_mem, \
             patch("psutil.cpu_count", return_value=8), \
             patch.object(detector, "_probe_gpu_backend", return_value=(False, None, None, None)):
            
            mock_mem.return_value = MagicMock(total=16 * (1024 ** 3), available=10 * (1024 ** 3))
            detector._cached_result = None
            res = detector.detect_hardware_tier()

            self.assertEqual(res.hardware_tier, "floor")
            self.assertIsNone(res.gpu_details)

            # Check telemetry payload format
            payload = detector.get_telemetry_payload()
            self.assertEqual(payload["hardware_tier"], "floor")
            self.assertIsNone(payload["gpu"])  # Must be explicit JSON null
            self.assertEqual(payload["ram"]["provenance"], "MEASURED")
            self.assertEqual(payload["cpu"]["provenance"], "MEASURED")
            self.assertIn("freq_mhz", payload["cpu"])
            self.assertIsInstance(payload["top_processes"], list)
            self.assertEqual(payload["cogniedge_load"]["provenance"], "DEMO")
            self.assertEqual(payload["cogniedge_load"]["cpu_pct_attributable"], 0.0)

    def test_mid_tier_assignment(self):
        """Test >=24GB RAM with no GPU assigns 'mid' tier."""
        detector = HardwareTierDetector()

        # Mock 32GB RAM and no GPU
        with patch("psutil.virtual_memory") as mock_mem, \
             patch("psutil.cpu_count", return_value=16), \
             patch.object(detector, "_probe_gpu_backend", return_value=(False, None, None, None)):
            
            mock_mem.return_value = MagicMock(total=32 * (1024 ** 3), available=24 * (1024 ** 3))
            detector._cached_result = None
            res = detector.detect_hardware_tier()

            self.assertEqual(res.hardware_tier, "mid")
            self.assertIsNone(res.gpu_details)

            payload = detector.get_telemetry_payload()
            self.assertEqual(payload["hardware_tier"], "mid")
            self.assertIsNone(payload["gpu"])  # Must be explicit JSON null
            self.assertEqual(payload["ram"]["provenance"], "MEASURED")
            self.assertEqual(payload["cpu"]["provenance"], "MEASURED")
            self.assertIsInstance(payload["top_processes"], list)
            self.assertIn("cogniedge_load", payload)

    def test_high_tier_assignment(self):
        """Test usable GPU backend assigns 'high' tier regardless of RAM."""
        detector = HardwareTierDetector()

        gpu_mock = GPUSummary(
            name="NVIDIA GeForce RTX 4080",
            backend="cuda",
            vram_total_gb=16.0,
            vram_used_gb=2.5,
            usage_pct=15.0,
            temperature_c=55.0,
            provenance="MEASURED"
        )

        # Mock 16GB RAM with NVIDIA GPU
        with patch("psutil.virtual_memory") as mock_mem, \
             patch("psutil.cpu_count", return_value=8), \
             patch.object(detector, "_probe_gpu_backend", return_value=(True, "NVIDIA GeForce RTX 4080", "cuda", gpu_mock)):
            
            mock_mem.return_value = MagicMock(total=16 * (1024 ** 3), available=10 * (1024 ** 3))
            detector._cached_result = None
            res = detector.detect_hardware_tier()

            self.assertEqual(res.hardware_tier, "high")
            self.assertIsNotNone(res.gpu_details)

            payload = detector.get_telemetry_payload()
            self.assertEqual(payload["hardware_tier"], "high")
            self.assertIsNotNone(payload["gpu"])
            self.assertEqual(payload["gpu"]["name"], "NVIDIA GeForce RTX 4080")
            self.assertEqual(payload["gpu"]["backend"], "cuda")
            self.assertEqual(payload["gpu"]["provenance"], "MEASURED")
            self.assertEqual(payload["ram"]["provenance"], "MEASURED")
            self.assertEqual(payload["cpu"]["provenance"], "MEASURED")
            self.assertIn("cogniedge_load", payload)

    def test_caching_and_rescan(self):
        """Test that tier is cached and only re-evaluated on explicit rescan."""
        detector = HardwareTierDetector()
        first_call = detector.detect_hardware_tier()

        # Calling again should return cached instance
        second_call = detector.detect_hardware_tier()
        self.assertIs(first_call, second_call)

        # Rescan creates a fresh detection result
        rescan_call = detector.rescan_hardware_tier()
        self.assertIsNotNone(rescan_call)


if __name__ == "__main__":
    unittest.main()
