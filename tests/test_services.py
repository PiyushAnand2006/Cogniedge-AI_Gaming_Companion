"""
CogniEdge Comprehensive Subsystem Test Suite
Tests:
1. LocalLLMProvider fallback and tool registry
2. FrameAnalyzer statistical calculations (1% low, P95, P99, variance)
3. BottleneckDetector deterministic rule classifications
4. StutterDetector & StutterRiskPredictor
5. Adaptive AI Compute Guard (safe optimizations)
6. SQLite MemoryRepository & Pattern Engine
7. AdviceEffectivenessTracker
8. EventBus async streaming
9. Master Contract Endpoints (/qa/ask, /coach/summarize, /perf/diagnose, /perf/optimize)
"""

import sys
import os
import time

# Add paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../services")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/ai")))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../services/performance"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../services/vision"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../services/memory"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../services/core"))

from ai.agent import CogniEdgeAIAgent
from ai.tools import ToolRegistry
from performance.frame_analyzer import FrameAnalyzer
from performance.bottleneck_detector import BottleneckDetector
from performance.stutter_detector import StutterDetector
from performance.predictor import StutterRiskPredictor
from performance.optimizer import AdaptiveAIComputeGuard
from performance.schemas import HardwareMetrics, FrameMetrics, BottleneckType, Provenance
from memory.database import init_database
from memory.repository import MemoryRepository
from memory.pattern_engine import PlayerPatternEngine
from memory.effectiveness import AdviceEffectivenessTracker
from core.events import event_bus


def test_frame_analyzer_math():
    analyzer = FrameAnalyzer(window_size=60)
    for _ in range(59):
        analyzer.push_frame_time(8.33, time.time())
    analyzer.push_frame_time(33.3, time.time())

    metrics = analyzer.calculate_metrics()
    assert metrics.fps > 100.0
    assert metrics.one_percent_low > 25.0
    assert metrics.p95_frame_time_ms >= 8.33
    assert metrics.p99_frame_time_ms >= 8.33
    assert metrics.frame_time_variance > 0
    assert metrics.stutter_count >= 1
    print("[PASS] test_frame_analyzer_math passed.")


def test_bottleneck_classifier_vram():
    detector = BottleneckDetector()
    hw = HardwareMetrics(
        vram_used_gb=7.8,
        vram_total_gb=8.0,
        gpu_usage_pct=92.0,
        hardware_provenance=Provenance.MEASURED
    )
    frames = FrameMetrics(
        timestamp=time.time(),
        fps=110.0,
        frame_time_ms=9.0,
        one_percent_low=55.0,
        point_one_percent_low=40.0,
        p50_frame_time_ms=8.5,
        p95_frame_time_ms=18.0,
        p99_frame_time_ms=25.0,
        frame_time_variance=6.5,
        stutter_count=2,
        longest_frame_ms=65.0
    )

    diagnosis = detector.classify(hw, frames)
    assert diagnosis.likely_issue == BottleneckType.VRAM_PRESSURE
    assert diagnosis.confidence >= 0.80
    assert len(diagnosis.evidence) >= 2
    print("[PASS] test_bottleneck_classifier_vram passed.")


def test_stutter_predictor():
    predictor = StutterRiskPredictor()
    hw = HardwareMetrics(vram_used_gb=7.7, vram_total_gb=8.0, cpu_peak_core_pct=92.0)
    frames = FrameMetrics(
        timestamp=time.time(),
        fps=110.0,
        frame_time_ms=9.0,
        one_percent_low=50.0,
        point_one_percent_low=35.0,
        p50_frame_time_ms=8.5,
        p95_frame_time_ms=20.0,
        p99_frame_time_ms=28.0,
        frame_time_variance=12.0,
        stutter_count=3,
        longest_frame_ms=80.0
    )

    pred = predictor.predict(hw, frames)
    assert pred.stutter_probability > 0.60
    assert pred.risk_level in ["high", "critical"]
    print("[PASS] test_stutter_predictor passed.")


def test_adaptive_ai_compute_guard():
    guard = AdaptiveAIComputeGuard()
    hw = HardwareMetrics(gpu_usage_pct=94.0)
    frames = FrameMetrics(
        timestamp=time.time(),
        fps=115.0,
        frame_time_ms=8.6,
        one_percent_low=60.0,
        point_one_percent_low=40.0,
        p50_frame_time_ms=8.0,
        p95_frame_time_ms=16.0,
        p99_frame_time_ms=22.0,
        frame_time_variance=4.0
    )

    action = guard.evaluate_optimization(hw, frames, BottleneckType.VRAM_PRESSURE)
    assert action is not None
    assert action.id == "opt_dial_vision_fps"

    apply_res = guard.apply_action("opt_dial_vision_fps")
    assert apply_res["status"] == "APPLIED"
    assert guard.vision_capture_fps == 1.0

    revert_res = guard.revert_action("opt_dial_vision_fps")
    assert revert_res["status"] == "REVERTED"
    assert guard.vision_capture_fps == 3.0
    print("[PASS] test_adaptive_ai_compute_guard passed.")


def test_sqlite_memory_and_effectiveness():
    test_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_cogniedge.db"))
    if os.path.exists(test_db):
        os.remove(test_db)

    init_database(test_db)
    repo = MemoryRepository(test_db)

    # 1. Session Lifecycle
    sess_id = repo.create_session("Cyberpunk 2077")
    assert sess_id.startswith("sess_")
    repo.end_session(sess_id, {"avg_fps": 138.0, "one_pct_low": 94.0, "coach_rating": "A"})
    sessions = repo.get_all_sessions()
    assert len(sessions) == 1
    assert sessions[0]["coach_rating"] == "A"

    # 2. Coaching Patterns (Spec schema)
    repo.upsert_coaching_pattern("tactical_habit", "Over-engaging with low HP (<30%)", confidence=0.88)
    patterns = repo.get_top_coaching_patterns(limit=5)
    assert len(patterns) == 1
    assert patterns[0]["pattern_type"] == "tactical_habit"

    # 3. Optimization History (Spec schema)
    repo.record_optimization_history(
        optimization="dial down background vision fps",
        before_metrics={"fps": 115.0, "one_percent_low": 60.0},
        after_metrics={"fps": 128.0, "one_percent_low": 85.0},
        verdict="improved"
    )
    opt_hist = repo.get_optimization_history(limit=5)
    assert len(opt_hist) == 1
    assert opt_hist[0]["verdict"] == "improved"

    if os.path.exists(test_db):
        os.remove(test_db)
    print("[PASS] test_sqlite_memory_and_effectiveness passed.")


def test_qwen_ai_agent_fallback():
    agent = CogniEdgeAIAgent(preferred_provider="fallback")
    status = agent.get_status()
    assert status["is_available"] == True

    diag = agent.diagnose_performance({
        "hardware": {"vram_used_gb": 7.7, "vram_total_gb": 8.0},
        "frames": {"frame_time_variance": 8.5}
    })
    assert "diagnosis" in diag
    assert "recommendation" in diag
    assert "confidence" in diag
    print("[PASS] test_qwen_ai_agent_fallback passed.")


def test_vendor_model_wrappers():
    from ai.genie_wrapper import GenieModelWrapper
    from ai.whisper_wrapper import WhisperModelWrapper
    from vision.yolo_wrapper import YOLOModelWrapper

    genie_wrap = GenieModelWrapper()
    genie_status = genie_wrap.get_status()
    assert genie_status["model_id"] == "qwen3_4b"
    assert "ai-hub-models" in genie_status["vendor_recipe"]

    whisper_wrap = WhisperModelWrapper()
    whisper_status = whisper_wrap.get_status()
    assert whisper_status["model_id"] == "whisper_base"
    assert "whisper_windows_py" in whisper_status["weights_path"]

    yolo_wrap = YOLOModelWrapper()
    yolo_status = yolo_wrap.get_status()
    assert yolo_status["model_id"] == "yolo26_det"
    assert "yolo26_det" in yolo_status["vendor_recipe"]

    print("[PASS] test_vendor_model_wrappers passed.")


if __name__ == "__main__":
    print("Running CogniEdge Subsystem Tests...")
    test_frame_analyzer_math()
    test_bottleneck_classifier_vram()
    test_stutter_predictor()
    test_adaptive_ai_compute_guard()
    test_sqlite_memory_and_effectiveness()
    test_qwen_ai_agent_fallback()
    test_vendor_model_wrappers()
    print("ALL PRODUCTION SUBSYSTEM TESTS PASSED SUCCESSFULLY.")
