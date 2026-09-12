"""
Genie LLM Wrapper & Adapter
Bridges CogniEdge's local AI reasoning engine to the Qualcomm Genie SDK / Qwen3-4B
defined in the sibling ai-hub-models and ai-hub-apps repositories.
"""

import os
import sys
import json
import subprocess
import time
from typing import Dict, Any, Optional

# Load vendor path configuration
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


class GenieModelWrapper:
    """Wrapper that references and executes Qualcomm Genie SDK / Qwen3-4B without copying vendor weights."""

    def __init__(self):
        self.config = load_model_config()
        self.llm_cfg = self.config.get("models", {}).get("llm", {})
        
        # Resolve vendor paths
        base_dir = os.path.dirname(CONFIG_PATH)
        self.vendor_recipe_dir = os.path.abspath(
            os.path.join(base_dir, self.llm_cfg.get("vendor_recipe_dir", "../../ai-hub-models/src/qai_hub_models/models/qwen3_4b"))
        )
        self.genie_tutorial_dir = os.path.abspath(
            os.path.join(base_dir, self.llm_cfg.get("genie_tutorial_dir", "../../ai-hub-apps/tutorials/llm_on_genie"))
        )
        self.bundle_dir = os.path.abspath(
            os.path.join(base_dir, self.llm_cfg.get("default_weights_path", "../../ai-hub-models/build/models/qwen3_4b/genie_bundle"))
        )
        self.genie_exe = os.path.join(self.bundle_dir, "genie-t2t-run.exe")

    def is_available(self) -> bool:
        """Checks if compiled Genie bundle exists in vendor or custom path."""
        return os.path.exists(self.genie_exe)

    def get_status(self) -> Dict[str, Any]:
        return {
            "model_id": self.llm_cfg.get("model_id", "qwen3_4b"),
            "model_name": self.llm_cfg.get("model_name", "Qwen3-4B-Instruct-W4A16"),
            "vendor_recipe": self.vendor_recipe_dir,
            "bundle_path": self.bundle_dir,
            "runtime": self.llm_cfg.get("runtime", "GENIE_HEXAGON_NPU"),
            "is_ready": self.is_available()
        }

    def run_inference(self, prompt: str, max_tokens: int = 512) -> Optional[str]:
        if not self.is_available():
            return None
        
        config_json = os.path.join(self.bundle_dir, "genie_config.json")
        cmd = [self.genie_exe, "-c", config_json, "-p", prompt]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if res.returncode == 0:
                return res.stdout.strip()
        except Exception as e:
            print(f"[GenieModelWrapper] Inference error: {e}")
        return None
