"""
CogniEdge Dual Audio Capture & Voice Activity Detection (VAD)
Captures:
1. Microphone input: Player voice queries and tactical questions.
2. System Loopback: In-game comms / game sound output via Windows WASAPI Loopback.

Equipped with Energy/RMS Voice Activity Detection (VAD) to filter idle background silence.
"""

import threading
import time
import struct
import queue
import io
import math
import wave
from typing import Optional, Dict, Any, List

# Attempt to import soundcard for real-time WASAPI capture
try:
    import soundcard as sc
    SOUNDCARD_AVAILABLE = True
except ImportError:
    SOUNDCARD_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class AudioCaptureManager:
    """
    Manages dual-channel on-device audio capture (Microphone + WASAPI Loopback)
    with integrated Voice Activity Detection (VAD) and ring-buffering.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_duration_s: float = 1.0,
        vad_threshold_rms: float = 0.015,
    ):
        self.sample_rate = sample_rate
        self.chunk_duration_s = chunk_duration_s
        self.chunk_samples = int(sample_rate * chunk_duration_s)
        self.vad_threshold_rms = vad_threshold_rms

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._chunk_queue: queue.Queue = queue.Queue(maxsize=30)
        self._source_mode: str = "microphone"  # "microphone", "system_loopback", "simulated"
        self._device_name: str = "Unknown"
        self._last_rms: float = 0.0

    @property
    def is_available(self) -> bool:
        """Check if hardware audio capture is available on this machine."""
        return SOUNDCARD_AVAILABLE and NUMPY_AVAILABLE

    @property
    def device_name(self) -> str:
        return self._device_name

    @property
    def is_running(self) -> bool:
        return self._running

    def list_devices(self) -> Dict[str, Any]:
        """List all available input and output devices."""
        if not SOUNDCARD_AVAILABLE:
            return {
                "microphones": ["Simulated Microphone (Dev Mode)"],
                "speakers": ["Simulated Speaker (Dev Mode)"],
                "soundcard_available": False,
                "provenance": "ESTIMATED"
            }
        try:
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except Exception:
                pass
            mics = [str(m.name) for m in sc.all_microphones()]
            spks = [str(s.name) for s in sc.all_speakers()]
            return {
                "microphones": mics,
                "speakers": spks,
                "soundcard_available": True,
                "provenance": "MEASURED"
            }
        except Exception as e:
            return {
                "microphones": ["Microphone Array (Default)"],
                "speakers": ["Speakers (Default)"],
                "error": str(e),
                "soundcard_available": True,
                "provenance": "ESTIMATED"
            }

    def compute_energy_rms(self, pcm_bytes: bytes) -> float:
        """
        Calculate Root Mean Square (RMS) signal energy of 16-bit PCM audio.
        Returns a normalized float between 0.0 and 1.0.
        """
        if not pcm_bytes:
            return 0.0

        if NUMPY_AVAILABLE:
            try:
                samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                if len(samples) == 0:
                    return 0.0
                rms = float(np.sqrt(np.mean(samples ** 2)))
                self._last_rms = rms
                return rms
            except Exception:
                pass

        # Pure python fallback
        num_samples = len(pcm_bytes) // 2
        if num_samples == 0:
            return 0.0
        sum_squares = 0.0
        for i in range(0, len(pcm_bytes), 2):
            sample = struct.unpack("<h", pcm_bytes[i:i+2])[0] / 32768.0
            sum_squares += sample * sample
        rms = math.sqrt(sum_squares / num_samples)
        self._last_rms = rms
        return rms

    def is_voice_active(self, pcm_bytes: bytes) -> bool:
        """Determines if the audio chunk contains voice activity above threshold."""
        rms = self.compute_energy_rms(pcm_bytes)
        return rms >= self.vad_threshold_rms

    def start(self, source: str = "microphone") -> Dict[str, Any]:
        """
        Start live continuous audio capture loop.
        :param source: 'microphone', 'system_loopback', or 'simulated'
        """
        if self._running:
            return {"status": "already_running", "device": self._device_name, "source": self._source_mode}

        self._source_mode = source

        if self.is_available:
            try:
                try:
                    import pythoncom
                    pythoncom.CoInitialize()
                except Exception:
                    pass
                if source == "system_loopback":
                    speaker = sc.default_speaker()
                    self._device_name = f"WASAPI Loopback: {speaker.name}"
                    self._running = True
                    self._thread = threading.Thread(
                        target=self._capture_loop_loopback,
                        args=(speaker,),
                        daemon=True
                    )
                    self._thread.start()
                    return {"status": "started", "device": self._device_name, "source": source, "mode": "wasapi_loopback"}
                else:
                    # Default to microphone
                    mic = sc.default_microphone()
                    self._device_name = f"Microphone: {mic.name}"
                    self._running = True
                    self._thread = threading.Thread(
                        target=self._capture_loop_microphone,
                        args=(mic,),
                        daemon=True
                    )
                    self._thread.start()
                    return {"status": "started", "device": self._device_name, "source": source, "mode": "microphone"}
            except Exception as e:
                print(f"[CogniEdge AudioCapture] Hardware capture failed ({e}), using simulated stream")
                return self._start_simulated(source)
        else:
            return self._start_simulated(source)

    def _start_simulated(self, source: str) -> Dict[str, Any]:
        self._device_name = f"Simulated Audio ({source})"
        self._source_mode = "simulated"
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop_simulated, daemon=True)
        self._thread.start()
        return {"status": "started", "device": self._device_name, "source": "simulated", "mode": "simulated"}

    def stop(self) -> Dict[str, Any]:
        """Stop capturing audio and drain internal queue."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        while not self._chunk_queue.empty():
            try:
                self._chunk_queue.get_nowait()
            except queue.Empty:
                break
        return {"status": "stopped", "device": self._device_name}

    def get_chunk(self, timeout: float = 2.0) -> Optional[bytes]:
        """Retrieve next captured audio chunk."""
        try:
            return self._chunk_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def record_seconds(self, duration_s: float = 3.0, source: str = "microphone") -> bytes:
        """
        Record a discrete sample directly from microphone or loopback and return as WAV bytes.
        """
        num_samples = int(self.sample_rate * duration_s)

        if self.is_available:
            try:
                try:
                    import pythoncom
                    pythoncom.CoInitialize()
                except Exception:
                    pass
                if source == "system_loopback":
                    speaker = sc.default_speaker()
                    mic = sc.get_microphone(id=str(speaker.name), include_loopback=True)
                else:
                    mic = sc.default_microphone()

                with mic.recorder(samplerate=self.sample_rate, channels=1) as recorder:
                    data = recorder.record(numframes=num_samples)
                    pcm_int16 = (data[:, 0] * 32767).astype(np.int16)
                    pcm_bytes = pcm_int16.tobytes()
                    return self.pcm_to_wav_bytes(pcm_bytes, self.sample_rate)
            except Exception as e:
                print(f"[CogniEdge AudioCapture] Direct record failed ({e}), generating synthetic wave")

        # Simulated recorded wave
        silence_pcm = b"\x00\x00" * num_samples
        return self.pcm_to_wav_bytes(silence_pcm, self.sample_rate)

    def _capture_loop_microphone(self, mic) -> None:
        try:
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except Exception:
                pass
            with mic.recorder(samplerate=self.sample_rate, channels=1) as recorder:
                while self._running:
                    data = recorder.record(numframes=self.chunk_samples)
                    pcm_int16 = (data[:, 0] * 32767).astype(np.int16)
                    pcm_bytes = pcm_int16.tobytes()
                    self._enqueue_chunk(pcm_bytes)
        except Exception as e:
            print(f"[CogniEdge AudioCapture] Mic capture loop error: {e}")
            self._running = False

    def _capture_loop_loopback(self, speaker) -> None:
        try:
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except Exception:
                pass
            mic = sc.get_microphone(id=str(speaker.name), include_loopback=True)
            with mic.recorder(samplerate=self.sample_rate, channels=1) as recorder:
                while self._running:
                    data = recorder.record(numframes=self.chunk_samples)
                    pcm_int16 = (data[:, 0] * 32767).astype(np.int16)
                    pcm_bytes = pcm_int16.tobytes()
                    self._enqueue_chunk(pcm_bytes)
        except Exception as e:
            print(f"[CogniEdge AudioCapture] Loopback capture loop error: {e}")
            self._running = False

    def _capture_loop_simulated(self) -> None:
        while self._running:
            silence = b"\x00\x00" * self.chunk_samples
            self._enqueue_chunk(silence)
            time.sleep(self.chunk_duration_s)

    def _enqueue_chunk(self, pcm_bytes: bytes) -> None:
        try:
            self._chunk_queue.put_nowait(pcm_bytes)
        except queue.Full:
            try:
                self._chunk_queue.get_nowait()
            except queue.Empty:
                pass
            self._chunk_queue.put_nowait(pcm_bytes)

    @staticmethod
    def pcm_to_wav_bytes(pcm_bytes: bytes, sample_rate: int = 16000, channels: int = 1, sample_width: int = 2) -> bytes:
        """Convert raw PCM bytes to in-memory WAV bytes."""
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(sample_rate)
            wf.writeframes(pcm_bytes)
        return buf.getvalue()


# Subclass for 100% backward compatibility with existing code
class SystemAudioCapture(AudioCaptureManager):
    """Alias for backwards compatibility with meeting/loopback workflows."""
    def __init__(self, sample_rate: int = 16000, chunk_duration_s: float = 2.0):
        super().__init__(sample_rate=sample_rate, chunk_duration_s=chunk_duration_s)

    def start(self) -> Dict[str, Any]:
        return super().start(source="system_loopback")
