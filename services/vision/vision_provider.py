"""
CogniEdge Game Vision Provider Interface
Zero-DLL-injection screen-only computer vision interface.
Extracts structured JSON game state (Player HP, Shields, Ammo, Minimap, Threat Direction).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class DetectedObject(BaseModel):
    label: str
    bbox: List[int]
    confidence: float


class StructuredPlayerVitals(BaseModel):
    health: int = 100
    shield: int = 100
    ammo: int = 30
    reloading: bool = False


class StructuredGameState(BaseModel):
    timestamp: float
    player: StructuredPlayerVitals
    hostiles_count: int = 0
    threat_vector: str = "Clear"
    detected_objects: List[DetectedObject] = []
    confidence: float = 0.0
    model_name: str = "YOLO26-N"
    provenance: str = "MEASURED"


class GameVisionProvider(ABC):
    @abstractmethod
    def capture_frame(self) -> Optional[bytes]:
        pass

    @abstractmethod
    def detect(self, frame_bytes: Optional[bytes]) -> List[DetectedObject]:
        pass

    @abstractmethod
    def extract_game_state(self, detections: List[DetectedObject], frame_bytes: Optional[bytes] = None) -> StructuredGameState:
        pass
