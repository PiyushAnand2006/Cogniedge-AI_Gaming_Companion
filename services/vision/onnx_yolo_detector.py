"""
CogniEdge ONNX YOLO Vision Detector
Hardware-accelerated screen & HUD object detection using onnxruntime.
Supports YOLOv8 / YOLO11 models with letterbox pre-processing, vectorized NMS, and QNN/CPU providers.
"""

import os
import sys
import time
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from model_manager import model_manager, VISION_MODEL_CONFIG
except ImportError:
    from ai.model_manager import model_manager, VISION_MODEL_CONFIG

try:
    from vision_provider import DetectedObject
except ImportError:
    from vision.vision_provider import DetectedObject

# Standard 80 COCO Classes + Game Entities mapping
COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
    "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
    "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
    "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote",
    "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book",
    "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
]


class ONNXYOLODetector:
    """
    On-device ONNX vision detector for game frames and HUD objects.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        conf_threshold: float = 0.35,
        iou_threshold: float = 0.45,
        input_size: int = 640
    ):
        self._model_path = model_path
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.input_size = input_size
        self._session = None
        self._input_name = None
        self._output_names = []
        self._provider = "CPUExecutionProvider"
        self._is_loaded = False
        self._last_latency_ms = 0.0

    @property
    def model_path(self) -> str:
        return self._model_path or model_manager.vision_model_path

    def _ensure_loaded(self):
        """Lazy load ONNX session on first inference request."""
        if self._session is not None:
            return

        if not os.path.exists(self.model_path):
            print(f"[ONNXYOLODetector] Vision model not found. Downloading...")
            self.model_path = model_manager.download_vision_model()

        import onnxruntime as ort

        # Available execution providers in priority order
        available = ort.get_available_providers()
        preferred_providers = []
        for p in ["QNNExecutionProvider", "DmlExecutionProvider", "CUDAExecutionProvider", "CPUExecutionProvider"]:
            if p in available:
                preferred_providers.append(p)

        print(f"[ONNXYOLODetector] Initializing ONNX session with providers: {preferred_providers}")
        self._session = ort.InferenceSession(self.model_path, providers=preferred_providers)
        self._input_name = self._session.get_inputs()[0].name
        self._output_names = [o.name for o in self._session.get_outputs()]
        self._provider = self._session.get_providers()[0]
        self._is_loaded = True
        print(f"[ONNXYOLODetector] Model loaded successfully on {self._provider}")

    def is_available(self) -> bool:
        """Check if model weights exist locally."""
        return os.path.exists(self.model_path) or self._session is not None

    def health(self) -> Dict[str, Any]:
        return {
            "model_name": VISION_MODEL_CONFIG.get("description", "YOLOv8 Nano ONNX"),
            "model_path": self.model_path,
            "model_exists": os.path.exists(self.model_path),
            "is_loaded": self._is_loaded,
            "provider": self._provider,
            "conf_threshold": self.conf_threshold,
            "last_latency_ms": self._last_latency_ms,
            "provenance": "MEASURED"
        }

    def _preprocess(self, image_np: np.ndarray) -> Tuple[np.ndarray, float, Tuple[int, int]]:
        """
        Letterbox resize image to square input_size x input_size with aspect ratio preserved.
        """
        orig_h, orig_w = image_np.shape[:2]
        scale = min(self.input_size / orig_w, self.input_size / orig_h)
        new_w, new_h = int(orig_w * scale), int(orig_h * scale)

        # Fast PIL resize for high quality interpolation
        img_pil = Image.fromarray(image_np).resize((new_w, new_h), Image.Resampling.BILINEAR)
        resized = np.array(img_pil)

        # Pad canvas with neutral gray (114)
        canvas = np.full((self.input_size, self.input_size, 3), 114, dtype=np.uint8)
        pad_x = (self.input_size - new_w) // 2
        pad_y = (self.input_size - new_h) // 2
        canvas[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = resized

        # Normalize and layout: HWC -> CHW -> NCHW float32
        tensor = canvas.astype(np.float32) / 255.0
        tensor = np.transpose(tensor, (2, 0, 1))
        tensor = np.expand_dims(tensor, axis=0)

        return tensor, scale, (pad_x, pad_y)

    def _nms(self, boxes: np.ndarray, scores: np.ndarray) -> List[int]:
        """Vectorized Non-Maximum Suppression."""
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        areas = (x2 - x1) * (y2 - y1)
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)

            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1)
            h = np.maximum(0.0, yy2 - yy1)
            inter = w * h

            ovr = inter / (areas[i] + areas[order[1:]] - inter + 1e-6)
            inds = np.where(ovr <= self.iou_threshold)[0]
            order = order[inds + 1]

        return keep

    def detect_frame(
        self,
        frame_bytes: bytes,
        width: int,
        height: int
    ) -> List[DetectedObject]:
        """
        Run object detection on raw RGB frame bytes (e.g. from screen_capture.py).
        """
        if not frame_bytes or width <= 0 or height <= 0:
            return []

        self._ensure_loaded()
        start_time = time.perf_counter()

        # Convert raw RGB bytes to numpy array
        try:
            image_np = np.frombuffer(frame_bytes, dtype=np.uint8).reshape((height, width, 3))
        except Exception:
            return []

        # Preprocess
        tensor, scale, (pad_x, pad_y) = self._preprocess(image_np)

        # Run ONNX inference
        outputs = self._session.run(self._output_names, {self._input_name: tensor})
        out = outputs[0]  # Shape: (1, 84, 8400) for YOLOv8

        # Post-process
        # Transpose to (8400, 84): [cx, cy, w, h, class0_score, class1_score, ...]
        preds = np.transpose(out[0], (1, 0))

        boxes = preds[:, :4]
        class_scores = preds[:, 4:]

        max_scores = np.max(class_scores, axis=1)
        class_ids = np.argmax(class_scores, axis=1)

        # Filter by confidence threshold
        mask = max_scores >= self.conf_threshold
        if not np.any(mask):
            self._last_latency_ms = (time.perf_counter() - start_time) * 1000.0
            return []

        filt_boxes = boxes[mask]
        filt_scores = max_scores[mask]
        filt_classes = class_ids[mask]

        # Convert [cx, cy, w, h] in letterbox space to [x1, y1, x2, y2] in original image space
        cx = filt_boxes[:, 0]
        cy = filt_boxes[:, 1]
        bw = filt_boxes[:, 2]
        bh = filt_boxes[:, 3]

        # Remove letterbox offset and rescale
        x1 = np.clip((cx - bw / 2 - pad_x) / scale, 0, width)
        y1 = np.clip((cy - bh / 2 - pad_y) / scale, 0, height)
        x2 = np.clip((cx + bw / 2 - pad_x) / scale, 0, width)
        y2 = np.clip((cy + bh / 2 - pad_y) / scale, 0, height)

        coords_xyxy = np.column_stack([x1, y1, x2, y2])

        # Apply NMS
        keep_indices = self._nms(coords_xyxy, filt_scores)

        results: List[DetectedObject] = []
        for idx in keep_indices[:30]:  # Limit top 30 detections
            c_id = int(filt_classes[idx])
            label = COCO_CLASSES[c_id] if c_id < len(COCO_CLASSES) else f"class_{c_id}"
            
            # Label enhancement for gaming context
            if label == "person":
                label = "Hostile_Combatant"
            elif label in ["knife", "scissors"]:
                label = "Melee_Weapon"

            bx = int(coords_xyxy[idx, 0])
            by = int(coords_xyxy[idx, 1])
            bw_val = int(coords_xyxy[idx, 2] - coords_xyxy[idx, 0])
            bh_val = int(coords_xyxy[idx, 3] - coords_xyxy[idx, 1])

            results.append(
                DetectedObject(
                    label=label,
                    bbox=[bx, by, bw_val, bh_val],
                    confidence=round(float(filt_scores[idx]), 3)
                )
            )

        self._last_latency_ms = (time.perf_counter() - start_time) * 1000.0
        return results
