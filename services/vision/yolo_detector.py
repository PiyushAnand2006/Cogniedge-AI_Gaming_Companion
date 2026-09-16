"""
CogniEdge YOLO Game HUD Vision Detector
Orchestrates ONNX YOLO detector, screen frame processing, and dynamic game HUD analysis.
Supports Qualcomm QNN / DirectML / CPU acceleration with honest provenance tagging.
"""

import time
import os
import sys
from typing import List, Optional, Dict, Any

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai")))

try:
    from vision_provider import GameVisionProvider, DetectedObject, StructuredGameState, StructuredPlayerVitals
    from onnx_yolo_detector import ONNXYOLODetector
    from hud_analyzer import HUDAnalyzer
except ImportError:
    from vision.vision_provider import GameVisionProvider, DetectedObject, StructuredGameState, StructuredPlayerVitals
    from vision.onnx_yolo_detector import ONNXYOLODetector
    from vision.hud_analyzer import HUDAnalyzer


class YOLOHUDVisionDetector(GameVisionProvider):
    """
    Main vision detector façade for CogniEdge.
    """

    def __init__(self, demo_mode: bool = False):
        self.demo_mode = demo_mode
        self.onnx_detector = ONNXYOLODetector()
        self.hud_analyzer = HUDAnalyzer()
        self.active_model = "YOLOv8 Nano ONNX"

    @property
    def is_available(self) -> bool:
        return self.onnx_detector.is_available()

    def get_status(self) -> Dict[str, Any]:
        h = self.onnx_detector.health()
        return {
            "active_model": self.active_model,
            "provider": h.get("provider", "CPUExecutionProvider"),
            "model_exists": h.get("model_exists", False),
            "is_loaded": h.get("is_loaded", False),
            "demo_mode": self.demo_mode,
            "latency_ms": h.get("last_latency_ms", 0.0),
            "provenance": "DEMO" if self.demo_mode else "MEASURED"
        }

    def capture_frame(self) -> Optional[bytes]:
        return None

    def detect(
        self,
        frame_bytes: Optional[bytes],
        width: int = 1920,
        height: int = 1080
    ) -> List[DetectedObject]:
        """
        Runs object detection on real frame bytes if provided, or simulated demo items if in demo mode.
        """
        if frame_bytes and len(frame_bytes) > 0:
            try:
                return self.onnx_detector.detect_frame(frame_bytes, width, height)
            except Exception as e:
                print(f"[YOLOHUDVisionDetector] Detection error: {e}")

        if self.demo_mode:
            return [
                DetectedObject(label="Hostile_Combatant", bbox=[820, 340, 95, 210], confidence=0.92),
                DetectedObject(label="Hostile_Combatant", bbox=[1140, 390, 80, 180], confidence=0.87),
                DetectedObject(label="Minimap_Sector_B9", bbox=[20, 20, 220, 220], confidence=0.98),
                DetectedObject(label="Health_HUD", bbox=[40, 980, 260, 45], confidence=0.95),
            ]

        return []

    def extract_game_state(
        self,
        detections: List[DetectedObject],
        frame_bytes: Optional[bytes] = None,
        screen_size: tuple = (1920, 1080),
        game_category: str = "Tactical FPS",
        game_title: str = "Unknown Game"
    ) -> StructuredGameState:
        """
        Constructs a structured game state from visual detections and genre intelligence.
        """
        return self.hud_analyzer.analyze(
            detections=detections,
            screen_size=screen_size,
            game_category=game_category,
            game_title=game_title,
            model_name=self.active_model,
            is_demo=self.demo_mode
        )
