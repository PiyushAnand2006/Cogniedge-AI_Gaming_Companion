"""
Unit Tests for ONNX YOLO Vision Detector
Tests preprocessing (letterboxing), NMS algorithm, output schema, and health reporting.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import numpy as np

SERVICES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../services"))
VISION_DIR = os.path.join(SERVICES_DIR, "vision")
sys.path.insert(0, SERVICES_DIR)
sys.path.insert(0, VISION_DIR)

from onnx_yolo_detector import ONNXYOLODetector
from vision_provider import DetectedObject


class TestONNXYOLODetector(unittest.TestCase):

    def setUp(self):
        self.detector = ONNXYOLODetector(model_path="/dummy/path/yolov8n.onnx")

    def test_detector_initialization(self):
        """Verify detector initializes with expected defaults."""
        self.assertEqual(self.detector.conf_threshold, 0.35)
        self.assertEqual(self.detector.iou_threshold, 0.45)
        self.assertEqual(self.detector.input_size, 640)

    def test_letterbox_preprocessing(self):
        """Verify letterbox scales 1920x1080 image to (1, 3, 640, 640) tensor."""
        dummy_img = np.zeros((1080, 1920, 3), dtype=np.uint8)
        tensor, scale, (pad_x, pad_y) = self.detector._preprocess(dummy_img)

        self.assertEqual(tensor.shape, (1, 3, 640, 640))
        self.assertEqual(tensor.dtype, np.float32)
        self.assertTrue(scale > 0)
        self.assertEqual(pad_x, 0)
        self.assertTrue(pad_y > 0)

    def test_vectorized_nms(self):
        """Verify Non-Maximum Suppression eliminates overlapping bounding boxes."""
        # Box 1 and Box 2 are heavily overlapping with high IoU
        boxes = np.array([
            [100, 100, 200, 200],  # Box 0, score 0.9
            [105, 102, 198, 205],  # Box 1 (duplicate), score 0.85
            [400, 400, 500, 500],  # Box 2 (distinct), score 0.75
        ], dtype=np.float32)
        scores = np.array([0.90, 0.85, 0.75], dtype=np.float32)

        keep = self.detector._nms(boxes, scores)
        self.assertIn(0, keep)  # Highest score kept
        self.assertNotIn(1, keep)  # Overlapping duplicate suppressed
        self.assertIn(2, keep)  # Independent box kept

    def test_empty_frame_handling(self):
        """Verify empty or zero-sized frames return empty list safely without exception."""
        res = self.detector.detect_frame(b"", 0, 0)
        self.assertEqual(res, [])

    def test_health_reporting(self):
        """Verify health check dictionary format."""
        health = self.detector.health()
        self.assertIn("model_name", health)
        self.assertIn("provider", health)
        self.assertIn("conf_threshold", health)
        self.assertEqual(health["provenance"], "MEASURED")


if __name__ == "__main__":
    unittest.main()
