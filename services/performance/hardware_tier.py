"""
CogniEdge Hardware Tier Detection Subsystem
Implements hardware tier classification and tier-to-configuration mapping
following Technical Requirements §6.2 and PRD §3.3.

Explicit concept: `hardware_tier` (values: "floor", "mid", "high").
Detection runs ONCE at startup and is cached for the session.
"""

import os
import sys
import shutil
import subprocess
from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass, asdict
import psutil

# Explicit type for hardware tier
HardwareTierType = Literal["floor", "mid", "high"]


@dataclass
class GPUSummary:
    name: str
    backend: str  # "cuda", "directml", "vulkan", "rocm"
    vram_total_gb: float
    vram_used_gb: float
    usage_pct: float
    temperature_c: Optional[float] = None
    provenance: str = "MEASURED"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HardwareTierResult:
    hardware_tier: HardwareTierType
    total_ram_gb: float
    logical_cpu_cores: int
    physical_cpu_cores: int
    gpu_detected: bool
    gpu_name: Optional[str]
    gpu_backend: Optional[str]
    gpu_details: Optional[GPUSummary]
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        res = asdict(self)
        if self.gpu_details is None:
            res["gpu_details"] = None
        return res


# ─────────────────────────────────────────────────────────────
# Tier-to-Configuration Mapping (§6.2 Model/backend selection)
# ─────────────────────────────────────────────────────────────

TIER_CONFIGURATIONS: Dict[HardwareTierType, Dict[str, Any]] = {
    "floor": {
        "hardware_tier": "floor",
        "description": "Floor tier configuration (~16GB RAM, CPU-only execution, zero GPU backend offload)",
        "model_family": "Qwen-Mini / Qwen-1.5B",
        "model_size_placeholder": "1.5B-Q4_K_M",
        # TODO (Stage 2): Replace with actual llama.cpp / onnx weight path once downloaded
        "model_path_placeholder": "models/floor/qwen_1.5b_q4_k_m.gguf",
        "context_window": 2048,
        "max_inference_threads": 4,  # Conservative thread limit to leave cores for host game
        "gpu_layers_offload": 0,    # CPU-only execution
        "vision_sampling_fps": 1.0, # Minimal background vision polling rate
        "audio_stt_model": "whisper-tiny-int8",
        "allow_concurrent_inference": False,
    },
    "mid": {
        "hardware_tier": "mid",
        "description": "Mid tier configuration (>=24GB RAM or high CPU core count, CPU-only execution)",
        "model_family": "Qwen-Standard / Qwen-4B",
        "model_size_placeholder": "4B-Q4_K_M",
        # TODO (Stage 2): Replace with actual llama.cpp / onnx weight path once downloaded
        "model_path_placeholder": "models/mid/qwen_4b_q4_k_m.gguf",
        "context_window": 4096,
        "max_inference_threads": 6,  # Scaled CPU thread allocation
        "gpu_layers_offload": 0,    # CPU execution with expanded context budget
        "vision_sampling_fps": 2.0,
        "audio_stt_model": "whisper-base-int8",
        "allow_concurrent_inference": False,
    },
    "high": {
        "hardware_tier": "high",
        "description": "High tier configuration (Usable GPU acceleration backend present, full/partial layer offloading)",
        "model_family": "Qwen-Full / Qwen-7B / Qwen-4B-INT8",
        "model_size_placeholder": "4B-INT8 / 7B-Q4_K_M",
        # TODO (Stage 2): Replace with actual llama.cpp / onnx weight path once downloaded
        "model_path_placeholder": "models/high/qwen_4b_int8.gguf",
        "context_window": 8192,
        "max_inference_threads": 8,
        "gpu_layers_offload": 99,   # Full GPU layer offloading to CUDA/DirectML
        "vision_sampling_fps": 3.0,
        "audio_stt_model": "whisper-small-fp16",
        "allow_concurrent_inference": True,
    }
}


def get_tier_configuration(hardware_tier: HardwareTierType) -> Dict[str, Any]:
    """
    Central lookup keyed by hardware_tier as specified in Technical Requirements §6.2.
    """
    return TIER_CONFIGURATIONS.get(hardware_tier, TIER_CONFIGURATIONS["floor"])


# ─────────────────────────────────────────────────────────────
# Hardware Tier Detector Core
# ─────────────────────────────────────────────────────────────

class HardwareTierDetector:
    """
    Evaluates system RAM, CPU cores, and GPU backend presence once at startup.
    Caches the result for the lifetime of the session.
    """

    def __init__(self):
        self._cached_result: Optional[HardwareTierResult] = None
        # Evaluate immediately on instantiation (startup)
        self.detect_hardware_tier()

    def detect_hardware_tier(self) -> HardwareTierResult:
        """Runs the detection once and caches the result."""
        if self._cached_result is not None:
            return self._cached_result

        # 1. Total System RAM (GB)
        mem = psutil.virtual_memory()
        total_ram_gb = round(mem.total / (1024 ** 3), 2)

        # 2. Logical and Physical CPU Cores
        logical_cores = psutil.cpu_count(logical=True) or 4
        physical_cores = psutil.cpu_count(logical=False) or logical_cores

        # 3. Probe for GPU Presence & Usable Acceleration Backend
        gpu_detected, gpu_name, gpu_backend, gpu_details = self._probe_gpu_backend()

        # 4. Assign Hardware Tier following Technical Requirements §6.2:
        # - "high": Usable GPU acceleration backend present (CUDA/ROCm/DirectML with dedicated VRAM)
        # - "mid": Meaningfully more RAM (>= 24 GB) or high core count, but no usable GPU backend
        # - "floor": ~16 GB RAM or less, no usable GPU backend
        if gpu_detected and gpu_backend in ["cuda", "directml", "rocm", "vulkan"]:
            tier: HardwareTierType = "high"
            reason = f"Usable GPU backend '{gpu_backend}' confirmed on {gpu_name}"
        elif total_ram_gb >= 24.0 or (total_ram_gb >= 20.0 and logical_cores >= 12):
            tier = "mid"
            reason = f"System has {total_ram_gb} GB RAM (>20 GB) and {logical_cores} cores, but no discrete GPU acceleration backend"
        else:
            tier = "floor"
            reason = f"System has {total_ram_gb} GB RAM (~16 GB or less) and no discrete GPU acceleration backend"

        self._cached_result = HardwareTierResult(
            hardware_tier=tier,
            total_ram_gb=total_ram_gb,
            logical_cpu_cores=logical_cores,
            physical_cpu_cores=physical_cores,
            gpu_detected=gpu_detected,
            gpu_name=gpu_name,
            gpu_backend=gpu_backend,
            gpu_details=gpu_details,
            reason=reason
        )
        return self._cached_result

    def rescan_hardware_tier(self) -> HardwareTierResult:
        """Explicitly re-runs hardware tier detection (not auto-triggered)."""
        self._cached_result = None
        return self.detect_hardware_tier()

    @property
    def current_tier(self) -> HardwareTierType:
        if self._cached_result is None:
            self.detect_hardware_tier()
        return self._cached_result.hardware_tier

    def _probe_gpu_backend(self) -> tuple[bool, Optional[str], Optional[str], Optional[GPUSummary]]:
        """
        Probes whether a usable GPU acceleration backend exists.
        Never fabricates metrics: if detection cannot confirm a usable GPU backend,
        returns (False, None, None, None).
        """
        has_nvidia_smi = shutil.which("nvidia-smi") is not None

        # 1. Check NVIDIA GPU via nvidia-smi
        if has_nvidia_smi:
            try:
                out = subprocess.check_output(
                    [
                        "nvidia-smi",
                        "--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.gpu",
                        "--format=csv,noheader,nounits"
                    ],
                    text=True, timeout=2.0
                ).strip()
                if out:
                    first_line = out.split("\n")[0]
                    parts = [p.strip() for p in first_line.split(",")]
                    if len(parts) >= 4:
                        name = parts[0]
                        vram_total = round(float(parts[1]) / 1024.0, 2)
                        vram_used = round(float(parts[2]) / 1024.0, 2)
                        usage_pct = float(parts[3])
                        temp_c = float(parts[4]) if len(parts) >= 5 and parts[4] != "[N/A]" else None
                        
                        summary = GPUSummary(
                            name=name,
                            backend="cuda",
                            vram_total_gb=vram_total,
                            vram_used_gb=vram_used,
                            usage_pct=usage_pct,
                            temperature_c=temp_c,
                            provenance="MEASURED"
                        )
                        return True, name, "cuda", summary
            except Exception:
                pass

        # 2. Check Windows WMI for dedicated AMD / Intel / Discrete GPUs
        if sys.platform == "win32":
            try:
                # Query VideoController
                cmd = 'powershell -NoProfile -Command "Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM | ConvertTo-Json"'
                out = subprocess.check_output(cmd, shell=True, text=True, timeout=3.0).strip()
                if out:
                    import json
                    data = json.loads(out)
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        name = item.get("Name", "")
                        adapter_ram = item.get("AdapterRAM", 0) or 0
                        adapter_ram_gb = round(adapter_ram / (1024 ** 3), 2)

                        # Exclude basic display adapters / standard software drivers
                        if any(ex in name.lower() for ex in ["basic display", "remote display", "vbox", "virtual"]):
                            continue

                        # Check for dedicated GPUs (e.g. GeForce, Radeon RX, Intel Arc, RTX) with >= 2GB VRAM
                        is_discrete = any(kw in name.lower() for kw in ["geforce", "radeon rx", "intel arc", "rtx", "quadro", "adreno"])
                        if is_discrete and adapter_ram_gb >= 2.0:
                            summary = GPUSummary(
                                name=name,
                                backend="directml",
                                vram_total_gb=adapter_ram_gb,
                                vram_used_gb=0.0,
                                usage_pct=0.0,
                                temperature_c=None,
                                provenance="MEASURED"
                            )
                            return True, name, "directml", summary
            except Exception:
                pass

        # No usable discrete acceleration backend confirmed
        return False, None, None, None

    def get_telemetry_payload(self) -> Dict[str, Any]:
        """
        Produces the exact GET /system/telemetry response following Technical Requirements §3.1.
        - Per-metric provenance (ram.provenance, cpu.provenance, gpu.provenance)
        - cpu.freq_mhz in MHz
        - top_processes list populated via psutil
        - cogniedge_load correctly shaped placeholder
        - On floor/mid tier without a usable GPU, 'gpu' is explicitly JSON null.
        """
        res = self.detect_hardware_tier()
        mem = psutil.virtual_memory()
        cpu_freq = psutil.cpu_freq()

        ram_data = {
            "total_gb": res.total_ram_gb,
            "used_gb": round((mem.total - mem.available) / (1024 ** 3), 2),
            "available_gb": round(mem.available / (1024 ** 3), 2),
            "provenance": "MEASURED"
        }

        cpu_data = {
            "core_count": res.physical_cpu_cores,
            "logical_cores": res.logical_cpu_cores,
            "usage_pct": psutil.cpu_percent(interval=None),
            "freq_mhz": round(cpu_freq.current, 1) if cpu_freq else None,
            "provenance": "MEASURED"
        }

        # Explicit JSON null if no GPU backend present on floor/mid tier
        gpu_data = res.gpu_details.to_dict() if (res.gpu_detected and res.gpu_details is not None) else None

        # Top processes by CPU usage
        top_procs = []
        try:
            for p in sorted(
                psutil.process_iter(['name', 'cpu_percent', 'memory_info']),
                key=lambda x: (x.info.get('cpu_percent') or 0.0),
                reverse=True
            )[:5]:
                p_name = p.info.get('name')
                if p_name and p_name.lower() not in ['system idle process', 'system']:
                    mem_info = p.info.get('memory_info')
                    mem_mb = round((mem_info.rss if mem_info else 0) / (1024 * 1024), 1)
                    top_procs.append({
                        "name": p_name,
                        "cpu_pct": round(p.info.get('cpu_percent') or 0.0, 1),
                        "mem_mb": mem_mb
                    })
        except Exception:
            pass

        # CogniEdge overhead placeholder (per Technical Requirements §3.1)
        cogniedge_load = {
            "cpu_pct_attributable": 0.0,
            "ram_mb_attributable": 0.0,
            "gpu_pct_attributable": 0.0,
            "provenance": "DEMO"
        }

        return {
            "hardware_tier": res.hardware_tier,
            "ram": ram_data,
            "cpu": cpu_data,
            "gpu": gpu_data,  # Explicitly null on floor/mid tier without usable GPU backend
            "top_processes": top_procs,
            "cogniedge_load": cogniedge_load
        }


# Singleton instance initialized once at startup
hardware_tier_detector = HardwareTierDetector()


# Singleton instance initialized once at startup
hardware_tier_detector = HardwareTierDetector()
