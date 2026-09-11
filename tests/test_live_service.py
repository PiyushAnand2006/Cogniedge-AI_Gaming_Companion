"""
CogniEdge End-to-End Local AI Service Integration Test
"""

import sys
import os
import time
import subprocess
import requests

def test_api():
    print("[TEST] Starting AI Service on http://127.0.0.1:8088...")
    service_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/ai_service.py"))
    
    proc = subprocess.Popen([sys.executable, service_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2.5)

    try:
        # 1. Health check
        res = requests.get("http://127.0.0.1:8088/health", timeout=3)
        assert res.status_code == 200
        health_data = res.json()
        assert health_data["status"] == "online"
        print("[PASS] /health endpoint:", health_data)

        # 2. Telemetry check
        res = requests.get("http://127.0.0.1:8088/telemetry", timeout=3)
        assert res.status_code == 200
        telem = res.json()
        assert telem["npu_tops"] == 45.2
        assert telem["gpu_contention_pct"] == 0.00
        print("[PASS] /telemetry endpoint:", telem)

        # 3. Router Query for Meeting Jargon
        res = requests.post("http://127.0.0.1:8088/router/query", json={
            "client": "meeting",
            "action": "explain_jargon",
            "context": {"concept": "eBPF", "recent_transcript": "ambient mesh filtering"}
        }, timeout=3)
        assert res.status_code == 200
        router_res = res.json()
        assert "response" in router_res
        assert router_res["mode"] == "meeting_copilot"
        print("[PASS] /router/query (meeting):", router_res["concept"], "->", router_res["response"][:60], "...")

        # 4. Router Query for Gaming Tactical Tip
        res = requests.post("http://127.0.0.1:8088/router/query", json={
            "client": "gaming",
            "action": "tactical_tip",
            "context": {"hud_state": {"hostiles_count": 3, "threat_vector": "East Corridor"}}
        }, timeout=3)
        assert res.status_code == 200
        game_res = res.json()
        assert "tactical_tip" in game_res
        assert game_res["mode"] == "gaming_hud"
        print("[PASS] /router/query (gaming):", game_res["tactical_tip"][:60], "...")

        # 5. Vision Detection Endpoint
        res = requests.post("http://127.0.0.1:8088/vision/detect", timeout=3)
        assert res.status_code == 200
        vision_res = res.json()
        assert vision_res["hostiles_count"] == 3
        print("[PASS] /vision/detect:", vision_res["model_used"], "detected", vision_res["hostiles_count"], "hostiles")

        # 6. Overlay State Endpoint
        res = requests.get("http://127.0.0.1:8088/overlay/state", timeout=3)
        assert res.status_code == 200
        overlay_state = res.json()
        assert overlay_state["game_fps"] == 144.0
        assert overlay_state["gpu_overhead"] == 0.00
        print("[PASS] /overlay/state:", overlay_state)

        print("\n>>> ALL API ENDPOINTS VERIFIED AND OPERATIONAL. <<<")

    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    test_api()
