"""
Unit Tests for CogniEdge Local TTS Engine
"""

import unittest
import os
import sys
import wave
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../services")))

from audio.tts_engine import TTSEngine


class TestTTSEngine(unittest.TestCase):
    def setUp(self):
        self.tts = TTSEngine(rate=1, volume=100)

    def test_tts_status(self):
        status = self.tts.get_status()
        self.assertIn("engine", status)
        self.assertIn("voices", status)
        self.assertIn("provenance", status)
        self.assertTrue(status["offline_only"])
        self.assertIsInstance(status["voices"], list)

    def test_synthesize_to_wav_bytes(self):
        text = "Tactical caution: two enemies spotted behind cover."
        wav_bytes = self.tts.synthesize_to_wav_bytes(text)
        self.assertIsInstance(wav_bytes, bytes)
        self.assertGreater(len(wav_bytes), 44)
        self.assertTrue(wav_bytes.startswith(b"RIFF"))

        # Verify valid WAV container
        with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
            self.assertGreater(wf.getnframes(), 0)
            self.assertIn(wf.getframerate(), [16000, 22050, 44100, 48000])

    def test_synthesize_empty_string(self):
        wav_bytes = self.tts.synthesize_to_wav_bytes("")
        self.assertGreater(len(wav_bytes), 44)
        self.assertTrue(wav_bytes.startswith(b"RIFF"))

    def test_speak_invocation(self):
        # Async speak should return True without throwing
        result = self.tts.speak("Tactical ping.", async_mode=True)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
