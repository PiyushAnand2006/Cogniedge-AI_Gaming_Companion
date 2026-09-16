"""
Unit Tests for CogniEdge Context-Aware Voice Assistant
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../services")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/ai")))

from ai.voice_assistant import VoiceAssistant


class TestVoiceAssistant(unittest.TestCase):
    def setUp(self):
        self.assistant = VoiceAssistant()

    def test_voice_assistant_status(self):
        status = self.assistant.get_status()
        self.assertEqual(status["status"], "ready")
        self.assertTrue(status["voice_assistant_ready"])
        self.assertIn("stt", status)
        self.assertIn("llm", status)
        self.assertIn("tts", status)

    def test_intent_classification(self):
        self.assertEqual(self.assistant.classify_intent("Why are my frame rates dropping?"), "diagnostic")
        self.assertEqual(self.assistant.classify_intent("Is the enemy pushing from behind?"), "tactical")
        self.assertEqual(self.assistant.classify_intent("What is the best build and strategy for this hero?"), "coaching")
        self.assertEqual(self.assistant.classify_intent("What time is the tournament?"), "general")

    def test_process_text_query_with_context(self):
        context = {
            "vision_hud": {
                "threat_level": "HIGH",
                "enemies_visible": 3,
                "health_pct": 24,
                "ammo_pct": 12
            },
            "telemetry": {
                "fps": 58,
                "gpu_load_pct": 98,
                "cpu_bottleneck_pct": 5
            },
            "game_info": {
                "title": "Valorant",
                "genre": "Tactical FPS"
            }
        }
        res = self.assistant.process_text_query("Should I push site now?", context=context, speak_output=False)
        self.assertIn("response_text", res)
        self.assertIn("intent", res)
        self.assertEqual(res["intent"], "tactical")
        self.assertTrue(res["context_injected"])
        self.assertGreater(res["audio_size_bytes"], 0)
        self.assertIsNotNone(res["audio_base64"])
        self.assertTrue(res["offline_only"])

    def test_process_audio_query(self):
        # Create silent WAV audio bytes
        import wave
        import io
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(b"\x00\x00" * 16000)
        audio_bytes = buf.getvalue()

        res = self.assistant.process_audio_query(audio_bytes, speak_output=False)
        self.assertIn("transcript", res)
        self.assertIn("response_text", res)
        self.assertIn("audio_base64", res)
        self.assertIn("total_latency_ms", res)


if __name__ == "__main__":
    unittest.main()
