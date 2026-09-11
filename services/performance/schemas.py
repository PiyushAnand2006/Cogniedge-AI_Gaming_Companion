"""
Data Schemas for CogniEdge Performance Doctor Subsystem
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class Provenance(str, Enum):
    MEASURED = "MEASURED"
    ESTIMATED = "ESTIMATED"
    REFERENCE = "REFERENCE"
    DEMO = "DEMO"
    UNAVAILABLE = "UNAVAILABLE"


class BottleneckType(str, Enum):
    GPU_BOUND = "GPU_BOUND"
    CPU_BOUND = "CPU_BOUND"
    VRAM_PRESSURE = "VRAM_PRESSURE"
    RAM_PRESSURE = "RAM_PRESSURE"
    THERMAL_LIMIT = "THERMAL_LIMIT"
    BACKGROUND_PROCESS_INTERFERENCE = "BACKGROUND_PROCESS_INTERFERENCE"
    STORAGE_ASSET_STREAMING_RISK = "STORAGE_ASSET_STREAMING_RISK"
    FRAME_TIME_INSTABILITY = "FRAME_TIME_INSTABILITY"
    OPTIMAL = "OPTIMAL"
    UNKNOWN = "UNKNOWN"


class FrameMetrics(BaseModel):
    timestamp: float
    fps: float
    frame_time_ms: float
    one_percent_low: float
    point_one_percent_low: float
    p50_frame_time_ms: float
    p95_frame_time_ms: float
    p99_frame_time_ms: float
    frame_time_variance: float
    stutter_count: int = 0
    longest_frame_ms: float = 0.0
    provenance: Provenance = Provenance.MEASURED


class HardwareMetrics(BaseModel):
    # CPU
    cpu_usage_pct: float = 0.0
    cpu_clock_ghz: Optional[float] = None
    cpu_temp_c: Optional[float] = None
    cpu_core_count: int = 8
    cpu_peak_core_pct: float = 0.0
    # GPU
    gpu_name: str = "Generic GPU"
    gpu_usage_pct: float = 0.0
    gpu_temp_c: Optional[float] = None
    gpu_clock_mhz: Optional[float] = None
    gpu_power_watts: Optional[float] = None
    vram_used_gb: float = 0.0
    vram_total_gb: float = 8.0
    # System Memory & Disk
    ram_used_gb: float = 0.0
    ram_total_gb: float = 16.0
    disk_usage_pct: float = 0.0
    top_background_processes: List[Dict[str, Any]] = Field(default_factory=list)
    # NPU
    npu_name: str = "NPU Provider"
    npu_utilization_pct: Optional[float] = None
    npu_tops_used: Optional[float] = None
    npu_available: bool = False
    npu_status_note: str = "Provider not detected"
    # Provenance
    hardware_provenance: Provenance = Provenance.MEASURED


class StutterEvent(BaseModel):
    id: Optional[str] = None
    timestamp: float
    duration_ms: float
    severity: str  # "minor" | "moderate" | "severe"
    likely_cause: BottleneckType
    game_state_tag: Optional[str] = None
    fps_before: float
    fps_dropped: float


class StutterRiskPrediction(BaseModel):
    stutter_probability: float  # 0.0 to 1.0
    risk_level: str  # "low" | "medium" | "high" | "critical"
    predicted_window_ms: int = 1500
    contributing_factors: List[str] = Field(default_factory=list)
    model_type: str = "Heuristic-Statistical Predictor"


class BottleneckDiagnosis(BaseModel):
    likely_issue: BottleneckType
    confidence: float
    evidence: List[str]
    severity: str  # "low" | "medium" | "high" | "critical"
    diagnosis: str
    recommendation: str
    expected_effect: str
    provenance: Provenance = Provenance.MEASURED


class OptimizerAction(BaseModel):
    id: str
    title: str
    description: str
    category: str  # "AI_COMPUTE_GUARD" | "IN_GAME_SETTING" | "BACKGROUND_PROCESS"
    current_value: Any
    recommended_value: Any
    safety_level: str = "SAFE_LOCAL_WORKLOAD"  # Only safe AI workload tweaks allowed automatically
    expected_improvement: str
    status: str = "PROPOSED"  # "PROPOSED" | "PREVIEWED" | "APPLIED" | "REVERTED"
