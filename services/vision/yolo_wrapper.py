"""
YOLO Vision Wrapper & Adapter
Bridges CogniEdge's game HUD vision detection pipeline to YOLO26 / YOLOv8
defined in the sibling ai-hub-models repository without duplicating vendor code.
"""

import os
import sys
import json
from typing import Dict, Any, Optional, List

CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../config/model_paths.json")
)


def load_model_config() -> Dict[str, Any]:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


class YOLOModelWrapper:
    """Wrapper that references YOLO recipes from the sibling ai-hub-models repository."""

    def __init__(self):
        self.config = load_model_config()
        self.vision_cfg = self.config.get("models", {}).get("vision", {})
        
        base_dir = os.path.dirname(CONFIG_PATH)
        self.vendor_recipe_dir = os.path.abspath(
            os.path.join(base_dir, self.vision_cfg.get("vendor_recipe_dir", "../../ai-hub-models/src/qai_hub_models/models/yolo26_det"))
        )
        self.weights_path = os.path.abspath(
            os.path.join(base_dir, self.vision_cfg.get("default_weights_path", "../../ai-hub-models/build/models/yolo26_det/yolo26n.onnx"))
        )
        
        # Link python path dynamically if available
        vendor_src = os.path.abspath(os.path.join(base_dir, "../../ai-hub-models/src"))
        if os.path.exists(vendor_src) and vendor_src not in sys.path:
            sys.path.insert(0, vendor_src)

    def is_available(self) -> bool:
        return os.path.exists(self.weights_path) or os.path.exists(self.vendor_recipe_dir)

    def get_status(self) -> Dict[str, Any]:
        return {
            "model_id": self.vision_cfg.get("model_id", "yolo26_det"),
            "model_name": self.vision_cfg.get("model_name", "YOLO26-N INT8"),
            "vendor_recipe": self.vendor_recipe_dir,
            "weights_path": self.weights_path,
            "runtime": self.vision_cfg.get("runtime", "QNN_ONNX_NPU"),
            "is_ready": os.path.exists(self.weights_path)
        }
