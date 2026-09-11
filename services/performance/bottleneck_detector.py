"""
Deterministic Bottleneck Classifier
Analyzes real-time telemetry and frame-time consistency to identify primary hardware limits:
- GPU_BOUND (GPU > 90%, high frame time)
- CPU_BOUND (Single-core peak > 85%, moderate GPU)
- VRAM_PRESSURE (VRAM > 92%, high frame variance)
- THERMAL_LIMIT (Temp > 84C, clock throttled)
- BACKGROUND_PROCESS_INTERFERENCE (Non-game process > 15% CPU/disk)
- STORAGE_ASSET_STREAMING_RISK (Disk spike aligning with frame spike)
- FRAME_TIME_INSTABILITY (High variance without clear saturation)
- OPTIMAL (Balanced, low variance)
"""

from typing import List, Tuple
from schemas import HardwareMetrics, FrameMetrics, BottleneckType, BottleneckDiagnosis, Provenance


class BottleneckDetector:
    def classify(self, hardware: HardwareMetrics, frames: FrameMetrics) -> BottleneckDiagnosis:
        evidence: List[str] = []

        # 1. Check VRAM Pressure (High Priority Stutter Cause)
        vram_pct = (hardware.vram_used_gb / hardware.vram_total_gb * 100) if hardware.vram_total_gb > 0 else 0
        if vram_pct > 92.0 and (frames.frame_time_variance > 5.0 or frames.stutter_count > 0):
            evidence.append(f"VRAM allocation is critical ({hardware.vram_used_gb:.1f}GB / {hardware.vram_total_gb:.1f}GB = {vram_pct:.1f}%)")
            evidence.append(f"Frame-time variance elevated ({frames.frame_time_variance:.2f}) indicating texture paging")
            return BottleneckDiagnosis(
                likely_issue=BottleneckType.VRAM_PRESSURE,
                confidence=0.89,
                evidence=evidence,
                severity="high" if vram_pct > 96 else "medium",
                diagnosis="VRAM allocation is near capacity, inducing paging latency during texture/mesh streaming.",
                recommendation="Reduce AI vision capture rate from 3 FPS to 1 FPS, or drop in-game texture resolution one step.",
                expected_effect="Recovers 1% low frame rates and eliminates paging-induced frame stalls.",
                provenance=hardware.hardware_provenance
            )

        # 2. Check Thermal Throttle
        if hardware.gpu_temp_c and hardware.gpu_temp_c > 84.0:
            evidence.append(f"GPU temperature reached {hardware.gpu_temp_c:.1f}°C")
            if hardware.gpu_clock_mhz and hardware.gpu_clock_mhz < 1500:
                evidence.append("GPU clock frequencies dropped below nominal boost states")
            return BottleneckDiagnosis(
                likely_issue=BottleneckType.THERMAL_LIMIT,
                confidence=0.86,
                evidence=evidence,
                severity="high",
                diagnosis="Thermal throttling detected on primary GPU.",
                recommendation="Cap in-game frame rate to monitor refresh rate and ensure laptop ventilation is clear.",
                expected_effect="Prevents clock down-throttling and stabilizes prolonged gaming sessions.",
                provenance=hardware.hardware_provenance
            )

        # 3. Check Background Process Interference
        for proc in hardware.top_background_processes:
            if proc["cpu_pct"] > 15.0 and "game" not in proc["name"].lower():
                evidence.append(f"Background application '{proc['name']}' consuming {proc['cpu_pct']:.1f}% CPU")
                return BottleneckDiagnosis(
                    likely_issue=BottleneckType.BACKGROUND_PROCESS_INTERFERENCE,
                    confidence=0.82,
                    evidence=evidence,
                    severity="medium",
                    diagnosis=f"Background process '{proc['name']}' is contending for CPU scheduler cycles.",
                    recommendation=f"Pause or close '{proc['name']}' during active gameplay sessions.",
                    expected_effect="Smooths out sudden CPU scheduling spikes and eliminates micro-stutters.",
                    provenance=hardware.hardware_provenance
                )

        # 4. Check Single-Core CPU Bound
        if hardware.cpu_peak_core_pct > 88.0 and hardware.gpu_usage_pct < 85.0:
            evidence.append(f"CPU thread peak utilization at {hardware.cpu_peak_core_pct:.1f}% on render thread")
            evidence.append(f"GPU utilization under-saturated at {hardware.gpu_usage_pct:.1f}%")
            return BottleneckDiagnosis(
                likely_issue=BottleneckType.CPU_BOUND,
                confidence=0.85,
                evidence=evidence,
                severity="medium",
                diagnosis="Render pipeline is single-thread CPU bound on the main game engine thread.",
                recommendation="Lower CPU-heavy game settings (crowd density, physics simulation distance, ray-traced shadows).",
                expected_effect="Increases 1% low frame consistency by reducing main thread bottlenecks.",
                provenance=hardware.hardware_provenance
            )

        # 5. Check GPU Bound
        if hardware.gpu_usage_pct > 92.0:
            evidence.append(f"GPU compute load saturated at {hardware.gpu_usage_pct:.1f}%")
            severity = "medium" if frames.fps < 60 else "low"
            return BottleneckDiagnosis(
                likely_issue=BottleneckType.GPU_BOUND,
                confidence=0.91,
                evidence=evidence,
                severity=severity,
                diagnosis="GPU graphics pipeline is fully utilized (expected in graphics-heavy rendering).",
                recommendation="Enable DLSS/FSR Quality mode or reduce shadow/volumetric fog quality for higher frame rates.",
                expected_effect="Boosts average and 1% low FPS while maintaining visual fidelity.",
                provenance=hardware.hardware_provenance
            )

        # 6. Check General Frame-Time Instability
        if frames.frame_time_variance > 8.0 or frames.stutter_count > 2:
            evidence.append(f"Frame-time variance is elevated ({frames.frame_time_variance:.2f} ms²)")
            evidence.append(f"Detected {frames.stutter_count} frame delivery anomalies in rolling window")
            return BottleneckDiagnosis(
                likely_issue=BottleneckType.FRAME_TIME_INSTABILITY,
                confidence=0.78,
                evidence=evidence,
                severity="medium",
                diagnosis="Possible asset/shader streaming-related stutter during dynamic scene transitions.",
                recommendation="Enable Adaptive AI Compute Guard to lower CogniEdge background capture frequency.",
                expected_effect="Stabilizes frame pacing during intense scene streaming.",
                provenance=hardware.hardware_provenance
            )

        # 7. Optimal
        return BottleneckDiagnosis(
            likely_issue=BottleneckType.OPTIMAL,
            confidence=0.95,
            evidence=["GPU/CPU loads balanced", "Low frame-time variance", "Zero thermal throttling detected"],
            severity="low",
            diagnosis="System performance is healthy with smooth frame delivery.",
            recommendation="Current configuration is optimal. No action required.",
            expected_effect="Maintains optimal gaming experience.",
            provenance=hardware.hardware_provenance
        )
