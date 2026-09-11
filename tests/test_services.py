"""
CogniEdge Integration Tests
Verifies local AI service, mode router, telemetry, audio capture, benchmark harness,
screen capture, and fallback pipelines.
"""

import sys
import os

# Add services directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../services")))

from genie_llm_bridge import GenieLLMBridge
from whisper_bridge import WhisperSTTBridge
from vision_detector import HUDVisionDetector
from mode_router import ModeRouter
from audio_capture import SystemAudioCapture
from screen_capture import ScreenCaptureWorker
from benchmark_harness import BenchmarkHarness


def test_genie_llm_bridge():
    bridge = GenieLLMBridge()
    prompt = bridge.format_qwen3_prompt("You are a helpful assistant.", "What is eBPF?")
    assert "<|im_start|>system" in prompt
    assert "<|im_start|>user" in prompt
    assert "<|im_start|>assistant" in prompt

    response = bridge.generate("Explain concept", "eBPF")
    assert len(response) > 20
    print("[PASS] test_genie_llm_bridge passed.")


def test_mode_router():
    bridge = GenieLLMBridge()
    router = ModeRouter(bridge)

    # Test meeting jargon route
    res_meeting = router.route_query("meeting", "explain_jargon", {"concept": "eBPF", "recent_transcript": "ambient mesh"})
    assert res_meeting["mode"] == "meeting_copilot"
    assert "response" in res_meeting

    # Test gaming tactical tip route
    res_gaming = router.route_query("gaming", "tactical_tip", {"hud_state": {"hostiles_count": 3}})
    assert res_gaming["mode"] == "gaming_hud"
    assert "tactical_tip" in res_gaming

    print("[PASS] test_mode_router passed.")


def test_vision_detector():
    detector = HUDVisionDetector()
    assert detector.active_model in ["YOLO26-N", "YOLO11-N (Fallback)"]
    hud_state = detector.detect_hud_state()
    assert hud_state["hostiles_count"] == 3
    assert hud_state["gpu_overhead_pct"] == 0.00
    print("[PASS] test_vision_detector passed.")


def test_whisper_bridge():
    bridge = WhisperSTTBridge()
    res = bridge.transcribe_audio_file("sample.wav")
    assert "text" in res
    assert res["latency_ms"] > 0
    print("[PASS] test_whisper_bridge passed.")


def test_whisper_pcm_chunk_transcription():
    """Test the new PCM chunk transcription method with simulated fallback."""
    bridge = WhisperSTTBridge()

    # Generate a fake PCM chunk (2 seconds of silence at 16kHz, 16-bit mono)
    fake_pcm = b'\x00\x00' * 32000  # 2 seconds * 16000 samples/sec

    result = bridge.transcribe_pcm_chunk(fake_pcm, sample_rate=16000)
    assert "text" in result
    assert len(result["text"]) > 0
    assert result["latency_ms"] > 0
    assert "speaker" in result
    assert "role" in result

    # Verify rotation: second call should return a different phrase
    result2 = bridge.transcribe_pcm_chunk(fake_pcm, sample_rate=16000)
    assert result2["text"] != result["text"] or result2["speaker"] != result["speaker"]

    print("[PASS] test_whisper_pcm_chunk_transcription passed.")


def test_system_audio_capture_fallback():
    """Test SystemAudioCapture simulated fallback mode."""
    capture = SystemAudioCapture(sample_rate=16000, chunk_duration_s=0.5)

    # Start in simulated mode (will fall back if soundcard not available)
    start_result = capture.start()
    assert start_result["status"] in ["started", "already_running"]

    # Get a chunk (should work even in simulated mode)
    chunk = capture.get_chunk(timeout=2.0)
    assert chunk is not None
    assert len(chunk) > 0

    # Stop
    stop_result = capture.stop()
    assert stop_result["status"] == "stopped"

    print("[PASS] test_system_audio_capture_fallback passed.")


def test_benchmark_harness():
    """Test the FPS benchmark harness returns correct structure."""
    harness = BenchmarkHarness(baseline_fps=144.0, duration_seconds=5)

    result = harness.run_benchmark()
    assert result["baseline_fps"] == 144.0
    assert result["cogniedge"]["avg_fps_drop"] == 0.0
    assert result["cogniedge"]["gpu_contention_pct"] == 0.00
    assert result["cogniedge"]["vram_mb"] == 0.0
    assert result["cogniedge"]["measured_fps"] == 144.0

    # GPU overlays should all have non-zero FPS drops
    for overlay in result["gpu_overlays"]:
        assert overlay["avg_fps_drop"] > 0
        assert overlay["measured_fps"] < 144.0
        assert overlay["gpu_contention_pct"] > 0

    # Test streaming generator (just get first 3 data points)
    stream_points = []
    for point in harness.stream_fps_data(duration_s=2, interval_ms=200):
        stream_points.append(point)
        if len(stream_points) >= 3:
            harness.stop()
            break

    assert len(stream_points) >= 3
    assert stream_points[0]["cogniedge_fps"] > 143  # Should be ~144 with tiny jitter
    assert stream_points[0]["discord_fps"] < 144  # Should have some drop

    print("[PASS] test_benchmark_harness passed.")


def test_screen_capture_worker():
    """Test ScreenCaptureWorker initialization and state."""
    worker = ScreenCaptureWorker(capture_fps=3.0)

    # Should not be running initially
    assert worker.frame_count == 0
    assert worker.get_latest_frame() is None

    # If mss is available, test start/stop
    if worker.is_available:
        start_result = worker.start()
        assert start_result["status"] == "started"
        import time
        time.sleep(0.5)
        stop_result = worker.stop()
        assert stop_result["status"] == "stopped"
        assert stop_result["total_frames_captured"] >= 0
    else:
        start_result = worker.start()
        assert start_result["status"] == "mss_not_available"

    print("[PASS] test_screen_capture_worker passed.")


if __name__ == "__main__":
    print("Running CogniEdge Integration Tests...")
    test_genie_llm_bridge()
    test_mode_router()
    test_vision_detector()
    test_whisper_bridge()
    test_whisper_pcm_chunk_transcription()
    test_system_audio_capture_fallback()
    test_benchmark_harness()
    test_screen_capture_worker()
    print("ALL TESTS PASSED SUCCESSFULLY.")
