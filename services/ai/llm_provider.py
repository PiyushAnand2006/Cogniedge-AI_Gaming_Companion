"""
CogniEdge Local LLM Provider Interface
Generic abstraction supporting:
1. Local OpenAI-compatible endpoints (Ollama, LM Studio, vLLM, llama.cpp on localhost)
2. Qualcomm Snapdragon Genie SDK runtime (Hexagon NPU)
3. High-fidelity deterministic local fallback provider with explicit provenance
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class LLMCapabilities(BaseModel):
    provider_name: str
    model_name: str
    is_local: bool = True
    hardware_target: str = "CPU/GPU"
    context_length: int = 8192
    supports_tools: bool = True
    is_available: bool = False
    provenance: str = "MEASURED"


class LLMResponse(BaseModel):
    text: str
    structured_data: Optional[Dict[str, Any]] = None
    latency_ms: float = 0.0
    tokens_generated: int = 0
    provider: str = "unknown"
    hardware_target: str = "unknown"
    provenance: str = "MEASURED"


class LocalLLMProvider(ABC):
    """Abstract base class for all CogniEdge local reasoning LLM backends."""

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def capabilities(self) -> LLMCapabilities:
        pass

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 512,
        json_mode: bool = False
    ) -> LLMResponse:
        pass
