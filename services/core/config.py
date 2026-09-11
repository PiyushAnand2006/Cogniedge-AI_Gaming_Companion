"""
CogniEdge Settings & Configuration Manager
"""

import os
import json
from typing import Dict, Any


CONFIG_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../settings.json")
)

DEFAULT_CONFIG = {
    "preferred_llm_provider": "auto",  # "auto" | "openai" | "genie" | "fallback"
    "local_endpoint_url": "http://127.0.0.1:11434/v1",
    "local_model_name": "qwen2.5:3b",
    "vision_capture_fps": 3.0,
    "demo_mode": False,
    "ptt_hotkey": "V",
    "overlay_hotkey": "Ctrl+Shift+O",
    "overlay_opacity": 0.85,
    "overlay_mode": "minimal",  # "minimal" | "compact" | "standard"
    "overlay_position": "top_right",
    "ai_compute_guard_enabled": True,
    "predictive_stutter_enabled": True,
    "session_retention_days": 30,
    "screenshot_retention": "events_only"  # "never" | "events_only" | "full"
}


class ConfigManager:
    def __init__(self, config_path: str = CONFIG_FILE):
        self.config_path = config_path
        self._config = dict(DEFAULT_CONFIG)
        self.load()

    def load(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._config.update(data)
            except Exception as e:
                print(f"[ConfigManager] Error reading settings: {e}")
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        self._config[key] = value
        self.save()

    def update_all(self, new_settings: Dict[str, Any]):
        self._config.update(new_settings)
        self.save()

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"[ConfigManager] Error saving settings: {e}")

    def get_all(self) -> Dict[str, Any]:
        return dict(self._config)


config_manager = ConfigManager()
