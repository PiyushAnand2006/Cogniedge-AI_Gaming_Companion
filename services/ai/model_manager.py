"""
CogniEdge Model Manager
Handles auto-download and caching of GGUF LLM models and whisper.cpp models.
Downloads from HuggingFace Hub to services/models/ on first use.
"""

import os
import sys
import threading
import hashlib
from typing import Optional, Callable, Dict, Any

# Default model directory
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))

# ─── Model Definitions ───

LLM_MODEL_CONFIG = {
    "repo_id": "Qwen/Qwen2.5-3B-Instruct-GGUF",
    "filename": "qwen2.5-3b-instruct-q4_k_m.gguf",
    "expected_size_mb": 2048,  # Approximate, for progress display
    "description": "Qwen2.5-3B-Instruct Q4_K_M quantization",
}

WHISPER_MODEL_CONFIG = {
    "repo_id": "ggerganov/whisper.cpp",
    "filename": "ggml-base.en.bin",
    "expected_size_mb": 142,
    "description": "Whisper base.en for English STT",
}

VISION_MODEL_CONFIG = {
    "repo_id": "Xenova/yolov8n",
    "filename": "yolov8n.onnx",
    "expected_size_mb": 6.2,
    "description": "YOLOv8 Nano ONNX Game HUD & Object Detector",
}


class ModelManager:
    """Thread-safe model download manager with progress callbacks."""

    def __init__(self, models_dir: Optional[str] = None):
        self.models_dir = models_dir or MODELS_DIR
        self.whisper_dir = os.path.join(self.models_dir, "whisper")
        self.vision_dir = os.path.join(self.models_dir, "vision")
        self._download_lock = threading.Lock()
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Create model directories if they don't exist."""
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.whisper_dir, exist_ok=True)
        os.makedirs(self.vision_dir, exist_ok=True)

    @property
    def llm_model_path(self) -> str:
        return os.path.join(self.models_dir, LLM_MODEL_CONFIG["filename"])

    @property
    def whisper_model_path(self) -> str:
        return os.path.join(self.whisper_dir, WHISPER_MODEL_CONFIG["filename"])

    @property
    def vision_model_path(self) -> str:
        return os.path.join(self.vision_dir, VISION_MODEL_CONFIG["filename"])

    def is_llm_downloaded(self) -> bool:
        path = self.llm_model_path
        if not os.path.exists(path):
            return False
        # Basic size check (at least 500MB for a real GGUF)
        size_mb = os.path.getsize(path) / (1024 * 1024)
        return size_mb > 500

    def is_whisper_downloaded(self) -> bool:
        path = self.whisper_model_path
        if not os.path.exists(path):
            return False
        size_mb = os.path.getsize(path) / (1024 * 1024)
        return size_mb > 50

    def is_vision_downloaded(self) -> bool:
        path = self.vision_model_path
        if not os.path.exists(path):
            return False
        size_mb = os.path.getsize(path) / (1024 * 1024)
        return size_mb > 3.0

    def download_llm_model(
        self,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> str:
        """Download LLM GGUF model from HuggingFace. Returns local path."""
        if self.is_llm_downloaded():
            if progress_callback:
                progress_callback("LLM model already downloaded", 1.0)
            return self.llm_model_path

        with self._download_lock:
            # Double-check after acquiring lock
            if self.is_llm_downloaded():
                return self.llm_model_path

            if progress_callback:
                progress_callback(
                    f"Downloading {LLM_MODEL_CONFIG['description']} (~{LLM_MODEL_CONFIG['expected_size_mb']}MB)...",
                    0.0
                )

            try:
                from huggingface_hub import hf_hub_download
                local_path = hf_hub_download(
                    repo_id=LLM_MODEL_CONFIG["repo_id"],
                    filename=LLM_MODEL_CONFIG["filename"],
                    local_dir=self.models_dir,
                    local_dir_use_symlinks=False,
                )
                if progress_callback:
                    progress_callback("LLM model download complete", 1.0)
                print(f"[ModelManager] LLM model downloaded to: {local_path}")
                return local_path

            except ImportError:
                print("[ModelManager] huggingface_hub not installed. Install with: pip install huggingface-hub")
                raise
            except Exception as e:
                print(f"[ModelManager] LLM model download failed: {e}")
                raise

    def download_whisper_model(
        self,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> str:
        """Download Whisper GGML model. Returns local path."""
        if self.is_whisper_downloaded():
            if progress_callback:
                progress_callback("Whisper model already downloaded", 1.0)
            return self.whisper_model_path

        with self._download_lock:
            if self.is_whisper_downloaded():
                return self.whisper_model_path

            if progress_callback:
                progress_callback(
                    f"Downloading {WHISPER_MODEL_CONFIG['description']} (~{WHISPER_MODEL_CONFIG['expected_size_mb']}MB)...",
                    0.0
                )

            try:
                from huggingface_hub import hf_hub_download
                local_path = hf_hub_download(
                    repo_id=WHISPER_MODEL_CONFIG["repo_id"],
                    filename=WHISPER_MODEL_CONFIG["filename"],
                    local_dir=self.whisper_dir,
                    local_dir_use_symlinks=False,
                )
                if progress_callback:
                    progress_callback("Whisper model download complete", 1.0)
                print(f"[ModelManager] Whisper model downloaded to: {local_path}")
                return local_path

            except ImportError:
                print("[ModelManager] huggingface_hub not installed.")
                raise
            except Exception as e:
                print(f"[ModelManager] Whisper model download failed: {e}")
                raise

    def download_vision_model(
        self,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> str:
        """Download or export YOLO ONNX vision model. Returns local path."""
        if self.is_vision_downloaded():
            if progress_callback:
                progress_callback("Vision model already downloaded", 1.0)
            return self.vision_model_path

        with self._download_lock:
            if self.is_vision_downloaded():
                return self.vision_model_path

            if progress_callback:
                progress_callback(
                    f"Downloading / Exporting {VISION_MODEL_CONFIG['description']}...",
                    0.0
                )

            # Strategy 1: Export via ultralytics if available
            try:
                from ultralytics import YOLO
                import shutil
                print("[ModelManager] Exporting YOLOv8n to ONNX via ultralytics...")
                yolo = YOLO("yolov8n.pt")
                exported = yolo.export(format="onnx")
                if os.path.exists(exported):
                    shutil.move(exported, self.vision_model_path)
                    if progress_callback:
                        progress_callback("Vision model export complete", 1.0)
                    print(f"[ModelManager] Vision model exported to: {self.vision_model_path}")
                    return self.vision_model_path
            except Exception as e:
                print(f"[ModelManager] Ultralytics export unavailable/failed: {e}")

            # Strategy 2: HuggingFace Hub download
            try:
                from huggingface_hub import hf_hub_download
                local_path = hf_hub_download(
                    repo_id=VISION_MODEL_CONFIG["repo_id"],
                    filename=VISION_MODEL_CONFIG["filename"],
                    local_dir=self.vision_dir,
                    local_dir_use_symlinks=False,
                )
                if progress_callback:
                    progress_callback("Vision model download complete", 1.0)
                print(f"[ModelManager] Vision model downloaded to: {local_path}")
                return local_path

            except Exception as e:
                print(f"[ModelManager] Vision model download failed: {e}")
                raise

    def get_status(self) -> Dict[str, Any]:
        """Return download status for all models."""
        llm_downloaded = self.is_llm_downloaded()
        whisper_downloaded = self.is_whisper_downloaded()
        vision_downloaded = self.is_vision_downloaded()

        llm_size_mb = 0
        if llm_downloaded:
            llm_size_mb = round(os.path.getsize(self.llm_model_path) / (1024 * 1024), 1)

        whisper_size_mb = 0
        if whisper_downloaded:
            whisper_size_mb = round(os.path.getsize(self.whisper_model_path) / (1024 * 1024), 1)

        vision_size_mb = 0
        if vision_downloaded:
            vision_size_mb = round(os.path.getsize(self.vision_model_path) / (1024 * 1024), 1)

        return {
            "models_dir": self.models_dir,
            "llm": {
                "model_id": LLM_MODEL_CONFIG["repo_id"],
                "filename": LLM_MODEL_CONFIG["filename"],
                "description": LLM_MODEL_CONFIG["description"],
                "downloaded": llm_downloaded,
                "path": self.llm_model_path if llm_downloaded else None,
                "size_mb": llm_size_mb,
            },
            "whisper": {
                "model_id": WHISPER_MODEL_CONFIG["repo_id"],
                "filename": WHISPER_MODEL_CONFIG["filename"],
                "description": WHISPER_MODEL_CONFIG["description"],
                "downloaded": whisper_downloaded,
                "path": self.whisper_model_path if whisper_downloaded else None,
                "size_mb": whisper_size_mb,
            },
            "vision": {
                "model_id": VISION_MODEL_CONFIG["repo_id"],
                "filename": VISION_MODEL_CONFIG["filename"],
                "description": VISION_MODEL_CONFIG["description"],
                "downloaded": vision_downloaded,
                "path": self.vision_model_path if vision_downloaded else None,
                "size_mb": vision_size_mb,
            }
        }


# Singleton instance
model_manager = ModelManager()
