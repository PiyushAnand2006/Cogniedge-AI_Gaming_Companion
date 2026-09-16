"""
Unit Tests for CogniEdge Dual Audio Capture & VAD
"""

import unittest
import os
import sys
import wave
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../services")))

from audio_capture import AudioCaptureManager, SystemAudioCapture


class TestAudioCaptureManager(unittest.TestCase):
    def setUp(self):
        self.mgr = AudioCaptureManager(sample_rate=16000, chunk_duration_s=0.5, vad_threshold_rms=0.02)

    def test_list_devices(self):
        devices = self.mgr.list_devices()
        self.assertIn("microphones", devices)
        self.assertIn("speakers", devices)
        self.assertIn("provenance", devices)
        self.assertIsInstance(devices["microphones"], list)

    def test_compute_energy_rms_silence(self):
        silence = b"\x00\x00" * 8000
        rms = self.mgr.compute_energy_rms(silence)
        self.assertEqual(rms, 0.0)
        self.assertFalse(self.mgr.is_voice_active(silence))

    def test_compute_energy_rms_active_signal(self):
        import struct
        # Synthetic loud tone
        loud_pcm = bytearray()
        for i in range(8000):
            sample = 20000 if (i % 2 == 0) else -20000
            loud_pcm.extend(struct.pack("<h", sample))
        
        rms = self.mgr.compute_energy_rms(bytes(loud_pcm))
        self.assertGreater(rms, 0.05)
        self.assertTrue(self.mgr.is_voice_active(bytes(loud_pcm)))

    def test_pcm_to_wav_conversion(self):
        silence_pcm = b"\x00\x00" * 16000
        wav_bytes = self.mgr.pcm_to_wav_bytes(silence_pcm, sample_rate=16000)
        self.assertTrue(wav_bytes.startswith(b"RIFF"))
        
        with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
            self.assertEqual(wf.getnchannels(), 1)
            self.assertEqual(wf.getframerate(), 16000)
            self.assertEqual(wf.getsampwidth(), 2)
            self.assertEqual(wf.getnframes(), 16000)

    def test_simulated_capture_lifecycle(self):
        res = self.mgr._start_simulated("microphone")
        self.assertEqual(res["status"], "started")
        self.assertTrue(self.mgr.is_running)

        chunk = self.mgr.get_chunk(timeout=1.5)
        self.assertIsNotNone(chunk)
        self.assertIsInstance(chunk, bytes)

        stop_res = self.mgr.stop()
        self.assertEqual(stop_res["status"], "stopped")
        self.assertFalse(self.mgr.is_running)

    def test_backwards_compatibility_system_audio_capture(self):
        sys_ac = SystemAudioCapture(sample_rate=16000, chunk_duration_s=1.0)
        self.assertIsInstance(sys_ac, AudioCaptureManager)


if __name__ == "__main__":
    unittest.main()
