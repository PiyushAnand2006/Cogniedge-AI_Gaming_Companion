"""
CogniEdge Screen Capture Worker
Background thread using mss (Monitor Screenshot) to grab game screen frames.
Zero GPU overhead — uses Windows Desktop Duplication API under the hood.
Adapts capture rate dynamically to the system's hardware tier (floor=1fps, mid=2.5fps, high=5fps).
"""

import io
import threading
import time
from typing import Optional, Dict, Any
from PIL import Image

# Attempt to import mss for screen capture
try:
    import mss
    import mss.tools
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False


TIER_FPS_MAPPING = {
    "floor": 1.0,
    "mid": 2.5,
    "high": 5.0,
}


class ScreenCaptureWorker:
    """
    Background screen capture with adaptive hardware-tier frame rate.
    Uses mss (Windows Desktop Duplication API) for zero GPU contention.
    """

    def __init__(self, capture_fps: float = 2.5, monitor_index: int = 1, hardware_tier: str = "mid"):
        """
        Args:
            capture_fps: Baseline frames per second to capture.
            monitor_index: Which monitor to capture (1 = primary).
            hardware_tier: Current hardware tier ('floor', 'mid', 'high').
        """
        self.hardware_tier = hardware_tier
        self.capture_fps = TIER_FPS_MAPPING.get(hardware_tier, capture_fps)
        self.capture_interval = 1.0 / self.capture_fps
        self.monitor_index = monitor_index
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._latest_frame: Optional[bytes] = None
        self._latest_frame_size: tuple = (0, 0)
        self._latest_jpeg: Optional[bytes] = None
        self._frame_lock = threading.Lock()
        self._frame_count = 0

    @property
    def is_available(self) -> bool:
        return MSS_AVAILABLE

    @property
    def frame_count(self) -> int:
        return self._frame_count

    def adapt_to_hardware_tier(self, tier: str):
        """Dynamically adjusts capture FPS based on hardware tier."""
        self.hardware_tier = tier
        new_fps = TIER_FPS_MAPPING.get(tier, 2.5)
        self.capture_fps = new_fps
        self.capture_interval = 1.0 / new_fps
        print(f"[ScreenCaptureWorker] Adapted to tier '{tier}': capture FPS = {self.capture_fps}")

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self._running,
            "is_available": self.is_available,
            "capture_fps": self.capture_fps,
            "hardware_tier": self.hardware_tier,
            "frame_count": self._frame_count,
            "frame_size": self._latest_frame_size,
            "provenance": "MEASURED"
        }

    def start(self) -> dict:
        """Start the background screen capture thread."""
        if self._running:
            return {"status": "already_running", "fps": self.capture_fps}

        if not self.is_available:
            return {"status": "mss_not_available", "message": "Install mss: pip install mss"}

        self._running = True
        self._frame_count = 0
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        return {"status": "started", "fps": self.capture_fps, "monitor": self.monitor_index, "tier": self.hardware_tier}

    def stop(self) -> dict:
        """Stop the screen capture thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=3.0)
            self._thread = None
        captured = self._frame_count
        self._frame_count = 0
        with self._frame_lock:
            self._latest_frame = None
            self._latest_jpeg = None
        return {"status": "stopped", "total_frames_captured": captured}

    def get_latest_frame(self) -> Optional[bytes]:
        """Get the most recently captured frame as raw RGB pixel bytes."""
        with self._frame_lock:
            return self._latest_frame

    def get_latest_frame_size(self) -> tuple:
        """Get (width, height) of the latest captured frame."""
        return self._latest_frame_size

    def get_latest_jpeg_frame(self, quality: int = 70) -> Optional[bytes]:
        """Get the latest frame compressed as JPEG bytes for MJPEG streaming."""
        with self._frame_lock:
            if self._latest_frame is None or self._latest_frame_size[0] == 0:
                return None
            
            try:
                w, h = self._latest_frame_size
                img = Image.frombytes("RGB", (w, h), self._latest_frame)
                
                # Downscale for fast web streaming (max 1280px wide)
                if w > 1280:
                    scale = 1280.0 / w
                    img = img.resize((1280, int(h * scale)), Image.Resampling.BILINEAR)
                
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=quality)
                return buf.getvalue()
            except Exception as e:
                print(f"[ScreenCaptureWorker] JPEG encoding error: {e}")
                return None

    def _capture_loop(self) -> None:
        """Main capture loop running in background thread."""
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[self.monitor_index] if self.monitor_index < len(sct.monitors) else sct.monitors[1]

                while self._running:
                    start_time = time.perf_counter()

                    # Capture the screen
                    screenshot = sct.grab(monitor)
                    raw_bytes = screenshot.rgb  # Raw RGB bytes
                    size = (screenshot.width, screenshot.height)

                    with self._frame_lock:
                        self._latest_frame = raw_bytes
                        self._latest_frame_size = size
                    self._frame_count += 1

                    # Maintain target FPS
                    elapsed = time.perf_counter() - start_time
                    sleep_time = self.capture_interval - elapsed
                    if sleep_time > 0:
                        time.sleep(sleep_time)

        except Exception as e:
            print(f"[CogniEdge ScreenCapture] Error: {e}")
            self._running = False
