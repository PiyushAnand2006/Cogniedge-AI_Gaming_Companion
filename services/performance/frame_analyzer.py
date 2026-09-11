"""
Rolling Window Frame-Time & Stutter Analyzer
Computes:
- Average FPS
- 1% Low FPS (99th percentile frame time inverted)
- 0.1% Low FPS (99.9th percentile frame time inverted)
- P50, P95, P99 Frame Times
- Frame-time variance and standard deviation
- Longest frame and stutter counts
"""

import math
import numpy as np
from typing import List, Dict, Any, Optional
from schemas import FrameMetrics, Provenance


class FrameAnalyzer:
    def __init__(self, window_size: int = 120):
        self.window_size = window_size
        self._frame_times: List[float] = []
        self._timestamps: List[float] = []

    def push_frame_time(self, frame_time_ms: float, timestamp: float):
        self._frame_times.append(frame_time_ms)
        self._timestamps.append(timestamp)
        if len(self._frame_times) > self.window_size:
            self._frame_times.pop(0)
            self._timestamps.pop(0)

    def calculate_metrics(self, provenance: Provenance = Provenance.MEASURED) -> FrameMetrics:
        if not self._frame_times:
            return FrameMetrics(
                timestamp=0.0,
                fps=0.0,
                frame_time_ms=0.0,
                one_percent_low=0.0,
                point_one_percent_low=0.0,
                p50_frame_time_ms=0.0,
                p95_frame_time_ms=0.0,
                p99_frame_time_ms=0.0,
                frame_time_variance=0.0,
                stutter_count=0,
                longest_frame_ms=0.0,
                provenance=provenance
            )

        arr = np.array(self._frame_times, dtype=np.float64)
        avg_ft = float(np.mean(arr))
        fps = 1000.0 / avg_ft if avg_ft > 0 else 0.0

        p50 = float(np.percentile(arr, 50))
        p95 = float(np.percentile(arr, 95))
        p99 = float(np.percentile(arr, 99))
        p99_9 = float(np.percentile(arr, 99.9))

        one_pct_low = 1000.0 / p99 if p99 > 0 else 0.0
        point_one_pct_low = 1000.0 / p99_9 if p99_9 > 0 else 0.0

        variance = float(np.var(arr))
        longest_frame = float(np.max(arr))

        # Stutter definition: frame time > 2x average frame time (dropped vsync cycle)
        stutter_threshold = avg_ft * 2.0
        stutter_count = int(np.sum(arr > stutter_threshold))

        ts = self._timestamps[-1] if self._timestamps else 0.0

        return FrameMetrics(
            timestamp=ts,
            fps=round(fps, 1),
            frame_time_ms=round(avg_ft, 2),
            one_percent_low=round(one_pct_low, 1),
            point_one_percent_low=round(point_one_pct_low, 1),
            p50_frame_time_ms=round(p50, 2),
            p95_frame_time_ms=round(p95, 2),
            p99_frame_time_ms=round(p99, 2),
            frame_time_variance=round(variance, 3),
            stutter_count=stutter_count,
            longest_frame_ms=round(longest_frame, 2),
            provenance=provenance
        )
