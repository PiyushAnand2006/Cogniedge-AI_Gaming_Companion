"""
CogniEdge whisper.cpp Local Speech-to-Text Provider
Direct C++ Whisper inference using pywhispercpp.
Supports real-time WAV file and raw PCM chunk transcription with zero cloud dependency.
"""

import os
import io
import wave
import time
import tempfile
from typing import Dict, Any, Optional, List

from model_manager import model_manager, WHISPER_MODEL_CONFIG


class WhisperCppProvider:
    """
    On-device Speech-to-Text provider backed by whisper.cpp via pywhispercpp.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        n_threads: Optional[int] = None,
        language: str = "en"
    ):
        self.model_path = model_path or model_manager.whisper_model_path
        self.n_threads = n_threads or max(2, (os.cpu_count() or 4) // 2)
        self.language = language
        self._model = None
        self._has_binding = False
        self._is_available = False
        self._check_and_init()

    def _check_and_init(self):
        """Check if pywhispercpp is available."""
        try:
            import pywhispercpp
            self._has_binding = True
        except ImportError:
            self._has_binding = False

        if self._has_binding and os.path.exists(self.model_path):
            self._is_available = True
        else:
            self._is_available = False

    def _ensure_loaded(self):
        """Lazy load whisper.cpp model into memory."""
        if self._model is not None:
            return

        if not self._has_binding:
            raise RuntimeError(
                "pywhispercpp is not installed. Install with: pip install pywhispercpp"
            )

        if not os.path.exists(self.model_path):
            print("[WhisperCppProvider] Model not found locally. Initiating download...")
            self.model_path = model_manager.download_whisper_model()

        try:
            from pywhispercpp.model import Model
            print(f"[WhisperCppProvider] Loading whisper model: {self.model_path} (threads={self.n_threads})")
            # Model accepts model name or model path (model path if ends with .bin)
            self._model = Model(
                self.model_path,
                n_threads=self.n_threads,
                language=self.language,
                print_realtime=False,
                print_progress=False
            )
            self._is_available = True
            print(f"[WhisperCppProvider] Whisper model loaded successfully.")
        except Exception as e:
            print(f"[WhisperCppProvider] Failed to load model: {e}")
            self._is_available = False
            raise

    def is_available(self) -> bool:
        return self._has_binding and (os.path.exists(self.model_path) or self._model is not None)

    def health(self) -> Dict[str, Any]:
        return {
            "provider": "whisper.cpp",
            "binding_installed": self._has_binding,
            "model_path": self.model_path,
            "model_exists": os.path.exists(self.model_path),
            "model_loaded": self._model is not None,
            "is_available": self.is_available(),
            "threads": self.n_threads,
            "provenance": "MEASURED"
        }

    def transcribe_audio_file(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe an audio file (WAV format, 16kHz mono recommended)."""
        self._ensure_loaded()
        start_time = time.time()

        try:
            segments = self._model.transcribe(audio_path)
            full_text = " ".join([seg.text.strip() for seg in segments if seg.text.strip()])
            latency_ms = (time.time() - start_time) * 1000.0

            return {
                "text": full_text,
                "model": f"whisper.cpp ({WHISPER_MODEL_CONFIG['filename']})",
                "latency_ms": round(latency_ms, 2),
                "language": self.language,
                "real_hardware": True,
                "provenance": "MEASURED"
            }
        except Exception as e:
            print(f"[WhisperCppProvider] Transcription failed: {e}")
            raise

    def transcribe_pcm_chunk(self, pcm_bytes: bytes, sample_rate: int = 16000) -> Dict[str, Any]:
        """Transcribe raw PCM 16-bit mono audio bytes by saving to a temp WAV."""
        if not pcm_bytes:
            return {
                "text": "",
                "model": "whisper.cpp",
                "latency_ms": 0.0,
                "provenance": "MEASURED"
            }

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
                with wave.open(tmp, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(sample_rate)
                    wf.writeframes(pcm_bytes)

            result = self.transcribe_audio_file(tmp_path)
            result["source"] = "pcm_chunk"
            return result
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
