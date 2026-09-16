"""
CogniEdge Local Text-to-Speech (TTS) Engine
Uses native Windows SAPI (Speech API) for zero-latency, 100% offline, on-device voice generation.
Provides direct playback and in-memory WAV audio byte synthesis with zero cloud dependency.
"""

import os
import io
import time
import math
import struct
import wave
import tempfile
import threading
from typing import Dict, Any, List, Optional

# Attempt SAPI dispatch via win32com
SAPI_AVAILABLE = False
try:
    import win32com.client
    import pythoncom
    # Verify we can initialize SAPI voice
    try:
        pythoncom.CoInitialize()
        _test_voice = win32com.client.Dispatch("SAPI.SpVoice")
        SAPI_AVAILABLE = True
    except Exception:
        SAPI_AVAILABLE = False
except ImportError:
    SAPI_AVAILABLE = False


class TTSEngine:
    """
    On-device Speech Synthesis Engine for CogniEdge Companion.
    Synthesizes tactical callouts and diagnostic debriefs into audio.
    """

    def __init__(self, rate: int = 1, volume: int = 100, voice_index: int = 0):
        """
        :param rate: Speed adjustment (-10 to 10, default 1 for crisp tactical pace)
        :param volume: Volume level (0 to 100, default 100)
        :param voice_index: Index of the installed system voice
        """
        self.rate = rate
        self.volume = volume
        self.voice_index = voice_index
        self._lock = threading.Lock()
        self._available_voices: List[str] = self._discover_voices()

    def _discover_voices(self) -> List[str]:
        if not SAPI_AVAILABLE:
            return ["CogniEdge Synthetic Voice (Fallback)"]
        try:
            pythoncom.CoInitialize()
            voice = win32com.client.Dispatch("SAPI.SpVoice")
            voices = voice.GetVoices()
            return [voices.Item(i).GetDescription() for i in range(voices.Count)]
        except Exception as e:
            print(f"[CogniEdge TTS] Voice discovery error: {e}")
            return ["CogniEdge Synthetic Voice (Fallback)"]

    @property
    def is_available(self) -> bool:
        return SAPI_AVAILABLE

    def get_status(self) -> Dict[str, Any]:
        return {
            "engine": "Windows SAPI (Native On-Device)" if SAPI_AVAILABLE else "Synthetic Wave Synthesizer",
            "is_available": True,
            "sapi_available": SAPI_AVAILABLE,
            "offline_only": True,
            "provenance": "MEASURED" if SAPI_AVAILABLE else "ESTIMATED",
            "voices": self._available_voices,
            "selected_voice": self._available_voices[min(self.voice_index, len(self._available_voices) - 1)] if self._available_voices else "None",
            "rate": self.rate,
            "volume": self.volume
        }

    def speak(self, text: str, async_mode: bool = True) -> bool:
        """
        Speak text directly to system audio output.
        """
        if not text or not text.strip():
            return False

        if SAPI_AVAILABLE:
            def _speak_worker():
                with self._lock:
                    try:
                        pythoncom.CoInitialize()
                        voice = win32com.client.Dispatch("SAPI.SpVoice")
                        voice.Rate = self.rate
                        voice.Volume = self.volume
                        voices = voice.GetVoices()
                        if 0 <= self.voice_index < voices.Count:
                            voice.Voice = voices.Item(self.voice_index)
                        # SVSFlagsAsync = 1, SVSFDefault = 0
                        flags = 1 if async_mode else 0
                        voice.Speak(text, flags)
                    except Exception as e:
                        print(f"[CogniEdge TTS] Speak error: {e}")

            if async_mode:
                t = threading.Thread(target=_speak_worker, daemon=True)
                t.start()
                return True
            else:
                _speak_worker()
                return True
        else:
            print(f"[CogniEdge TTS Fallback] Speaking: {text}")
            return True

    def synthesize_to_wav_bytes(self, text: str) -> bytes:
        """
        Synthesize text into standard RIFF WAV bytes in memory.
        """
        if not text or not text.strip():
            return self._generate_silence_wav(0.5)

        if SAPI_AVAILABLE:
            tmp_path = None
            try:
                with self._lock:
                    pythoncom.CoInitialize()
                    fs = win32com.client.Dispatch("SAPI.SpFileStream")
                    voice = win32com.client.Dispatch("SAPI.SpVoice")
                    voice.Rate = self.rate
                    voice.Volume = self.volume
                    voices = voice.GetVoices()
                    if 0 <= self.voice_index < voices.Count:
                        voice.Voice = voices.Item(self.voice_index)

                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                        tmp_path = tmp.name

                    # SSFMCreateForWrite = 3
                    fs.Open(tmp_path, 3, False)
                    voice.AudioOutputStream = fs
                    voice.Speak(text, 0)
                    fs.Close()

                if os.path.exists(tmp_path):
                    with open(tmp_path, "rb") as f:
                        wav_data = f.read()
                    return wav_data
            except Exception as e:
                print(f"[CogniEdge TTS] WAV synthesis error, generating synthetic wave: {e}")
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass

        # Fallback synthesizer: generates clean multi-tone synthetic audio signal
        return self._generate_synthetic_speech_wav(text)

    def _generate_silence_wav(self, duration_s: float = 0.5, sample_rate: int = 16000) -> bytes:
        """Generate silent WAV file."""
        buf = io.BytesIO()
        num_samples = int(duration_s * sample_rate)
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(b"\x00\x00" * num_samples)
        return buf.getvalue()

    def _generate_synthetic_speech_wav(self, text: str, sample_rate: int = 16000) -> bytes:
        """
        Deterministic lightweight speech waveform generator for CI / headless testing.
        Modulates frequency based on character rhythm.
        """
        buf = io.BytesIO()
        words = text.split()
        duration_s = max(0.4, len(words) * 0.28)
        num_samples = int(duration_s * sample_rate)

        # Generate harmonic speech-like formant tones
        frames = bytearray()
        for i in range(num_samples):
            t = float(i) / sample_rate
            # Base carrier tone around 220Hz with vibrato & envelope modulation
            envelope = math.sin(math.pi * (i % 3200) / 3200.0) ** 2 if (i % 3200) < 2800 else 0.05
            freq1 = 220.0 + 30.0 * math.sin(2 * math.pi * 3.0 * t)
            freq2 = 440.0 + 20.0 * math.cos(2 * math.pi * 2.0 * t)
            sample = int(32767.0 * 0.3 * envelope * (0.6 * math.sin(2 * math.pi * freq1 * t) + 0.4 * math.sin(2 * math.pi * freq2 * t)))
            sample = max(-32768, min(32767, sample))
            frames.extend(struct.pack("<h", sample))

        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(frames)
        return buf.getvalue()
