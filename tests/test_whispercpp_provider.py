"""
Unit Tests for whisper.cpp Local Speech-to-Text Provider
Tests initialization, availability checks, health status, and bridge integration.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

SERVICES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../services"))
AI_DIR = os.path.join(SERVICES_DIR, "ai")
sys.path.insert(0, SERVICES_DIR)
sys.path.insert(0, AI_DIR)

from whispercpp_provider import WhisperCppProvider
from whisper_bridge import WhisperSTTBridge


class TestWhisperCppProvider(unittest.TestCase):

    def test_provider_initialization(self):
        """Verify WhisperCppProvider initializes with correct config."""
        provider = WhisperCppProvider(model_path="/dummy/path/whisper.bin", n_threads=4)
        self.assertEqual(provider.model_path, "/dummy/path/whisper.bin")
        self.assertEqual(provider.n_threads, 4)
        self.assertEqual(provider.language, "en")

    def test_health_check(self):
        """Verify health check returns expected status keys."""
        provider = WhisperCppProvider(model_path="/dummy/path/whisper.bin")
        health = provider.health()
        self.assertEqual(health["provider"], "whisper.cpp")
        self.assertIn("binding_installed", health)
        self.assertIn("model_exists", health)
        self.assertIn("is_available", health)
        self.assertEqual(health["provenance"], "MEASURED")

    def test_whisper_bridge_integration(self):
        """Verify WhisperSTTBridge initializes whispercpp provider."""
        bridge = WhisperSTTBridge()
        self.assertIsNotNone(bridge.whispercpp)
        self.assertTrue(hasattr(bridge, "is_whispercpp_installed"))

    def test_pcm_chunk_fallback(self):
        """Verify empty PCM returns cleanly."""
        provider = WhisperCppProvider(model_path="/dummy/path/whisper.bin")
        res = provider.transcribe_pcm_chunk(b"")
        self.assertEqual(res["text"], "")


if __name__ == "__main__":
    unittest.main()
