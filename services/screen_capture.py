"""
CogniEdge Screen Capture Worker
Background thread using mss (Monitor Screenshot) to grab game screen frames at 2-5 Hz.
Zero GPU overhead — uses Windows Desktop Duplication API under the hood.
Feeds frames to YOLO26-N / YOLO11-N vision detector for HUD state detection.
"""

import threading
import time
from typing import Optional

# Attempt to import mss for screen capture
try:
    import mss
    import mss.tools
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False


class ScreenCaptureWorker:
    """
    Background screen capture at 2-5 Hz for game HUD vision detection.
    Uses mss (Windows Desktop Duplication API) for zero GPU contention.
    """

    def __init__(self, capture_fps: float = 3.0, monitor_index: int = 1):
        """
        Args:
            capture_fps: Frames per second to capture (2-5 Hz recommended for NPU budget).
            monitor_index: Which monitor to capture (1 = primary, 2 = secondary, etc.).
        """
        self.capture_fps = min(max(capture_fps, 1.0), 10.0)  # Clamp 1-10 FPS
        self.capture_interval = 1.0 / self.capture_fps
        self.monitor_index = monitor_index
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._latest_frame: Optional[bytes] = None
        self._latest_frame_size: tuple = (0, 0)
        self._frame_lock = threading.Lock()
        self._frame_count = 0

    @property
    def is_available(self) -> bool:
        return MSS_AVAILABLE

    @property
    def frame_count(self) -> int:
        return self._frame_count

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
        return {"status": "started", "fps": self.capture_fps, "monitor": self.monitor_index}

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
        return {"status": "stopped", "total_frames_captured": captured}

    def get_latest_frame(self) -> Optional[bytes]:
        """Get the most recently captured frame as raw pixel bytes."""
        with self._frame_lock:
            return self._latest_frame

    def get_latest_frame_size(self) -> tuple:
        """Get (width, height) of the latest captured frame."""
        return self._latest_frame_size

    def _capture_loop(self) -> None:
        """Main capture loop running in background thread."""
        try:
            with mss.MSS() as sct:
                # Select monitor
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
