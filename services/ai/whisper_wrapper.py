"""
Whisper Audio Wrapper & Adapter
Bridges CogniEdge's push-to-talk voice pipeline to Whisper ONNX / QAIRT
defined in the sibling ai-hub-apps/whisper_windows_py and ai-hub-models repos.
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, Optional

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


class WhisperModelWrapper:
    """Wrapper that references and executes Whisper from sibling vendor directories."""

    def __init__(self):
        self.config = load_model_config()
        self.whisper_cfg = self.config.get("models", {}).get("whisper", {})
        
        base_dir = os.path.dirname(CONFIG_PATH)
        self.vendor_recipe_dir = os.path.abspath(
            os.path.join(base_dir, self.whisper_cfg.get("vendor_recipe_dir", "../../ai-hub-models/src/qai_hub_models/models/whisper_base"))
        )
        self.app_demo_dir = os.path.abspath(
            os.path.join(base_dir, self.whisper_cfg.get("app_demo_dir", "../../ai-hub-apps/whisper_windows_py"))
        )
        self.weights_path = os.path.abspath(
            os.path.join(base_dir, self.whisper_cfg.get("default_weights_path", "../../ai-hub-apps/whisper_windows_py/models/whisper_base.onnx"))
        )

    def is_available(self) -> bool:
        return os.path.exists(self.weights_path) or os.path.exists(self.app_demo_dir)

    def get_status(self) -> Dict[str, Any]:
        return {
            "model_id": self.whisper_cfg.get("model_id", "whisper_base"),
            "model_name": self.whisper_cfg.get("model_name", "Whisper Base Quantized"),
            "vendor_recipe": self.vendor_recipe_dir,
            "weights_path": self.weights_path,
            "runtime": self.whisper_cfg.get("runtime", "ONNX_NPU"),
            "is_ready": os.path.exists(self.weights_path)
        }

    def transcribe_audio(self, audio_wav_path: str) -> Optional[str]:
        """Transcribes audio file by calling into vendor script or runtime."""
        if not os.path.exists(audio_wav_path):
            return None
        
        demo_script = os.path.join(self.app_demo_dir, "demo.py")
        if os.path.exists(demo_script):
            try:
                cmd = [sys.executable, demo_script, "--audio_file", audio_wav_path]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                if res.returncode == 0:
                    return res.stdout.strip()
            except Exception as e:
                print(f"[WhisperModelWrapper] Transcription error: {e}")
        return None
