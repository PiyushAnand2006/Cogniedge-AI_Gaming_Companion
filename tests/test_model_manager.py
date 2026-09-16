"""
Unit Tests for Model Manager Subsystem
Tests model configuration, status reporting, directory creation, and download mechanics.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile

SERVICES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../services"))
AI_DIR = os.path.join(SERVICES_DIR, "ai")
sys.path.insert(0, SERVICES_DIR)
sys.path.insert(0, AI_DIR)

from model_manager import ModelManager, LLM_MODEL_CONFIG, WHISPER_MODEL_CONFIG


class TestModelManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mgr = ModelManager(models_dir=self.temp_dir)

    def test_directory_structure_created(self):
        """Verify models directory and whisper subdirectory are created."""
        self.assertTrue(os.path.exists(self.temp_dir))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "whisper")))

    def test_model_paths(self):
        """Verify correct paths computed for LLM and Whisper models."""
        expected_llm = os.path.join(self.temp_dir, LLM_MODEL_CONFIG["filename"])
        expected_whisper = os.path.join(self.temp_dir, "whisper", WHISPER_MODEL_CONFIG["filename"])
        self.assertEqual(self.mgr.llm_model_path, expected_llm)
        self.assertEqual(self.mgr.whisper_model_path, expected_whisper)

    def test_status_when_empty(self):
        """Verify status reporting when no models are downloaded."""
        status = self.mgr.get_status()
        self.assertFalse(status["llm"]["downloaded"])
        self.assertIsNone(status["llm"]["path"])
        self.assertFalse(status["whisper"]["downloaded"])
        self.assertIsNone(status["whisper"]["path"])

    def test_is_downloaded_size_validation(self):
        """Verify size checks work accurately."""
        # Create a small dummy file (1MB) - should NOT count as downloaded LLM (needs >500MB)
        llm_path = self.mgr.llm_model_path
        with open(llm_path, "wb") as f:
            f.write(b"0" * 1024 * 1024)

        self.assertFalse(self.mgr.is_llm_downloaded())

    def test_vision_model_paths(self):
        """Verify correct paths and directory computed for vision model."""
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "vision")))
        self.assertTrue(self.mgr.vision_model_path.endswith("yolov8n.onnx"))

    @patch("huggingface_hub.hf_hub_download")
    def test_download_llm_model_mocked(self, mock_hf_download):
        """Verify download invocation uses correct repo and filename."""
        mock_hf_download.return_value = self.mgr.llm_model_path

        # Mock download
        with patch.object(self.mgr, "is_llm_downloaded", return_value=False):
            res_path = self.mgr.download_llm_model()
            mock_hf_download.assert_called_once_with(
                repo_id=LLM_MODEL_CONFIG["repo_id"],
                filename=LLM_MODEL_CONFIG["filename"],
                local_dir=self.temp_dir,
                local_dir_use_symlinks=False,
            )
            self.assertEqual(res_path, self.mgr.llm_model_path)

    @patch("huggingface_hub.hf_hub_download")
    def test_download_vision_model_mocked(self, mock_hf_download):
        """Verify vision download invocation."""
        mock_hf_download.return_value = self.mgr.vision_model_path

        with patch.object(self.mgr, "is_vision_downloaded", return_value=False), \
             patch("sys.modules", {**sys.modules, "ultralytics": None}):
            res_path = self.mgr.download_vision_model()
            self.assertEqual(res_path, self.mgr.vision_model_path)


if __name__ == "__main__":
    unittest.main()
