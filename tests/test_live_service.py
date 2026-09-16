"""
CogniEdge End-to-End Local AI Service Integration Test
"""

import sys
import os
import pytest

# Ensure repository root is on sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from fastapi.testclient import TestClient
from services.ai_service import app


def test_api():
    print("[TEST] Testing AI Service endpoints via TestClient...")
    client = TestClient(app)

    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200
    health_data = res.json()
    assert health_data["status"] == "online"
    print("[PASS] /health endpoint:", health_data)

    # 2. Telemetry check
    res = client.get("/telemetry")
    assert res.status_code == 200
    telem = res.json()
    assert telem["npu_tops"] in [45.2, 24.0]
    assert "genie_status" in telem
    print("[PASS] /telemetry endpoint:", telem)

    # 3. Tactical Q&A Query
    res = client.post("/qa/ask", json={
        "query": "What is my optimal positioning right now?",
        "include_habits": True
    })
    assert res.status_code == 200
    qa_res = res.json()
    assert "response" in qa_res
    print("[PASS] /qa/ask endpoint:", qa_res["response"][:60], "...")

    # 4. Game Active Profile Endpoint
    res = client.get("/game/active")
    assert res.status_code == 200
    game_res = res.json()
    assert "title" in game_res
    assert "genre" in game_res
    print("[PASS] /game/active endpoint:", game_res["title"], f"({game_res['genre']})")

    # 5. Vision Detection Endpoint
    res = client.post("/vision/detect")
    assert res.status_code == 200
    vision_res = res.json()
    assert "player" in vision_res
    assert vision_res["hostiles_count"] >= 0
    print("[PASS] /vision/detect:", "detected", vision_res["hostiles_count"], "hostiles, vector:", vision_res.get("threat_vector"))

    # 6. Live Performance & Stutter Doctor Endpoint
    res = client.get("/performance/live")
    assert res.status_code == 200
    perf_live = res.json()
    assert "hardware" in perf_live
    assert "frames" in perf_live
    print("[PASS] /performance/live:", f"FPS: {perf_live['frames']['fps']}, NPU: {perf_live['hardware']['npu_available']}")

    # 7. Benchmark Suite Endpoint
    res = client.post("/benchmark/run")
    assert res.status_code == 200
    bench_res = res.json()
    assert "cogniedge" in bench_res
    assert bench_res["cogniedge"]["fps_drop_avg"] == 0.0
    print("[PASS] /benchmark/run:", bench_res["cogniedge"]["name"])

    print("\n>>> ALL API ENDPOINTS VERIFIED AND OPERATIONAL. <<<")


if __name__ == "__main__":
    test_api()

