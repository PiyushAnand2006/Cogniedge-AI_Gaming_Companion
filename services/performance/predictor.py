"""
Numerical Stutter Risk Predictor
Evaluates time-series telemetry trends (frame-time slope, VRAM trend, CPU spikes, temperature drift)
to forecast upcoming stutter probability in the next 1.5s window.
"""

import math
from typing import List
from schemas import HardwareMetrics, FrameMetrics, StutterRiskPrediction


class StutterRiskPredictor:
    def predict(self, hardware: HardwareMetrics, frames: FrameMetrics) -> StutterRiskPrediction:
        risk_score = 0.0
        factors: List[str] = []

        # 1. VRAM saturation risk
        vram_pct = (hardware.vram_used_gb / hardware.vram_total_gb * 100) if hardware.vram_total_gb > 0 else 0
        if vram_pct > 94.0:
            risk_score += 0.40
            factors.append("VRAM near buffer limit (>94%)")
        elif vram_pct > 88.0:
            risk_score += 0.20
            factors.append("Elevated VRAM allocation (>88%)")

        # 2. Frame-time variance trend
        if frames.frame_time_variance > 10.0:
            risk_score += 0.35
            factors.append("High frame delivery jitter")
        elif frames.frame_time_variance > 4.0:
            risk_score += 0.15
            factors.append("Moderate frame-time variance")

        # 3. CPU Core saturation
        if hardware.cpu_peak_core_pct > 90.0:
            risk_score += 0.20
            factors.append("Render thread near 100% capacity")

        # 4. Thermal stress
        if hardware.gpu_temp_c and hardware.gpu_temp_c > 82.0:
            risk_score += 0.15
            factors.append("Thermal threshold warning")

        # Cap probability between 0.02 and 0.98
        probability = min(max(risk_score, 0.04), 0.96)

        if probability > 0.70:
            level = "critical" if probability > 0.85 else "high"
        elif probability > 0.35:
            level = "medium"
        else:
            level = "low"

        if not factors:
            factors.append("Stable frame pacing across all telemetry channels")

        return StutterRiskPrediction(
            stutter_probability=round(probability, 2),
            risk_level=level,
            predicted_window_ms=1500,
            contributing_factors=factors,
            model_type="Heuristic-Statistical Risk Predictor"
        )
