"""
Spike & Stutter Detector
Detects discrete frame spikes, duration, severity, and logs events.
"""

import time
import uuid
from typing import Optional, List
from schemas import StutterEvent, BottleneckType


class StutterDetector:
    def __init__(self, spike_threshold_multiplier: float = 2.2, min_spike_ms: float = 30.0):
        self.spike_threshold_multiplier = spike_threshold_multiplier
        self.min_spike_ms = min_spike_ms

    def detect_spike(
        self,
        current_frame_ms: float,
        rolling_avg_ms: float,
        likely_cause: BottleneckType = BottleneckType.UNKNOWN,
        fps_before: float = 120.0
    ) -> Optional[StutterEvent]:
        threshold = max(rolling_avg_ms * self.spike_threshold_multiplier, self.min_spike_ms)

        if current_frame_ms > threshold:
            duration = current_frame_ms - rolling_avg_ms
            severity = "minor"
            if duration > 50.0:
                severity = "severe"
            elif duration > 25.0:
                severity = "moderate"

            dropped_fps = max(fps_before - (1000.0 / current_frame_ms), 0.0)

            return StutterEvent(
                id=str(uuid.uuid4())[:8],
                timestamp=time.time(),
                duration_ms=round(duration, 1),
                severity=severity,
                likely_cause=likely_cause,
                fps_before=round(fps_before, 1),
                fps_dropped=round(dropped_fps, 1)
            )
        return None
