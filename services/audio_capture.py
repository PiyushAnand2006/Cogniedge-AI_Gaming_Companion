"""
CogniEdge System Audio Loopback Capture
Captures meeting speakers' voices from the system audio output via Windows WASAPI Loopback.
Works with Bluetooth headphones, wired headphones, speakers — any output device.

The user is a passive listener; CogniEdge taps what they HEAR (system audio),
not what they SAY (microphone).
"""

import threading
import time
import struct
import queue
import io
import wave
from typing import Optional

# Attempt to import soundcard for WASAPI loopback
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


class SystemAudioCapture:
    """
    Captures system audio output (what the user hears) via WASAPI loopback.
    This is the meeting speakers' voices coming through Zoom/Teams/Meet,
    regardless of whether output goes to Bluetooth, speakers, or headphones.
    """

    def __init__(self, sample_rate: int = 16000, chunk_duration_s: float = 2.0):
        self.sample_rate = sample_rate
        self.chunk_duration_s = chunk_duration_s
        self.chunk_samples = int(sample_rate * chunk_duration_s)
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._chunk_queue: queue.Queue = queue.Queue(maxsize=20)
        self._device_name: str = "Unknown"

    @property
    def is_available(self) -> bool:
        """Check if system audio loopback capture is available on this machine."""
        return SOUNDCARD_AVAILABLE and NUMPY_AVAILABLE

    @property
    def device_name(self) -> str:
        return self._device_name

    def start(self) -> dict:
        """Start capturing system audio output in loopback mode."""
        if self._running:
            return {"status": "already_running", "device": self._device_name}

        if self.is_available:
            try:
                # Get default speaker/output device for loopback capture
                default_speaker = sc.default_speaker()
                self._device_name = default_speaker.name
                self._running = True
                self._thread = threading.Thread(
                    target=self._capture_loop_real,
                    args=(default_speaker,),
                    daemon=True
                )
                self._thread.start()
                return {"status": "started", "device": self._device_name, "mode": "wasapi_loopback"}
            except Exception as e:
                print(f"[CogniEdge Audio] WASAPI loopback failed, falling back to simulation: {e}")
                return self._start_simulated()
        else:
            return self._start_simulated()

    def _start_simulated(self) -> dict:
        """Fallback: Generate simulated audio chunks for demo/dev environments."""
        self._device_name = "Simulated Loopback (Dev Mode)"
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop_simulated, daemon=True)
        self._thread.start()
        return {"status": "started", "device": self._device_name, "mode": "simulated"}

    def stop(self) -> dict:
        """Stop the audio capture loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=3.0)
            self._thread = None
        # Drain the queue
        while not self._chunk_queue.empty():
            try:
                self._chunk_queue.get_nowait()
            except queue.Empty:
                break
        return {"status": "stopped"}

    def get_chunk(self, timeout: float = 3.0) -> Optional[bytes]:
        """
        Get the next captured PCM audio chunk as raw bytes.
        Returns None if no chunk is available within the timeout.
        """
        try:
            return self._chunk_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def _capture_loop_real(self, speaker) -> None:
        """Real WASAPI loopback capture loop."""
        try:
            # Use loopback=True to capture system audio output
            mic = sc.get_microphone(id=str(speaker.name), include_loopback=True)
            with mic.recorder(samplerate=self.sample_rate, channels=1) as recorder:
                while self._running:
                    # Record chunk_duration_s of audio
                    data = recorder.record(numframes=self.chunk_samples)
                    # Convert float32 numpy array to 16-bit PCM bytes
                    pcm_int16 = (data[:, 0] * 32767).astype(np.int16)
                    pcm_bytes = pcm_int16.tobytes()
                    try:
                        self._chunk_queue.put_nowait(pcm_bytes)
                    except queue.Full:
                        # Drop oldest chunk if queue is full
                        try:
                            self._chunk_queue.get_nowait()
                        except queue.Empty:
                            pass
                        self._chunk_queue.put_nowait(pcm_bytes)
        except Exception as e:
            print(f"[CogniEdge Audio] Loopback capture error: {e}")
            self._running = False

    def _capture_loop_simulated(self) -> None:
        """Simulated capture loop: generates silent PCM chunks at real-time pacing."""
        while self._running:
            # Generate ~2 seconds of silence (16-bit PCM, 16kHz mono)
            num_samples = self.chunk_samples
            silence = b'\x00\x00' * num_samples
            try:
                self._chunk_queue.put_nowait(silence)
            except queue.Full:
                try:
                    self._chunk_queue.get_nowait()
                except queue.Empty:
                    pass
                self._chunk_queue.put_nowait(silence)
            time.sleep(self.chunk_duration_s)

    @staticmethod
    def pcm_to_wav_bytes(pcm_bytes: bytes, sample_rate: int = 16000, channels: int = 1, sample_width: int = 2) -> bytes:
        """Convert raw PCM bytes to a WAV file in memory."""
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(sample_rate)
            wf.writeframes(pcm_bytes)
        return buf.getvalue()
