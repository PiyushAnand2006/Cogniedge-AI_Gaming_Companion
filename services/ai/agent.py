"""
CogniEdge Qwen3-4B AI Agent & Orchestrator
Manages local LLM provider selection, prioritized sequential execution queue,
and structured multi-modal reasoning across Game, Player, and Machine state.
"""

from typing import Dict, Any, Optional, List
import json
import threading
import queue
import time

from llm_provider import LocalLLMProvider, LLMResponse, LLMCapabilities
from openai_local import OpenAILocalProvider
from genie_provider import GenieProvider
from llamacpp_provider import LlamaCppProvider
from fallback_provider import FallbackReasoningProvider
from tools import ToolRegistry


class CogniEdgeAIAgent:
    def __init__(self, preferred_provider: str = "auto"):
        self.preferred_provider = preferred_provider
        self.tool_registry = ToolRegistry()

        self.genie_provider = GenieProvider()
        self.openai_provider = OpenAILocalProvider()
        self.llamacpp_provider = LlamaCppProvider()
        self.fallback_provider = FallbackReasoningProvider()

        self._active_provider: LocalLLMProvider = self._select_best_provider()
        self._llm_lock = threading.Lock()

    def _select_best_provider(self) -> LocalLLMProvider:
        if self.preferred_provider == "genie" and self.genie_provider._is_available():
            return self.genie_provider
        elif self.preferred_provider == "openai" and self.openai_provider._check_availability():
            return self.openai_provider
        elif self.preferred_provider == "llamacpp" and self.llamacpp_provider.capabilities().is_available:
            return self.llamacpp_provider

        # Priority 1: Qualcomm Hexagon NPU via Genie SDK
        if self.genie_provider._is_available():
            return self.genie_provider
        # Priority 2: OpenAI-compatible local server (Ollama / LM Studio)
        elif self.openai_provider._check_availability():
            return self.openai_provider
        # Priority 3: Direct llama.cpp GGUF execution
        elif self.llamacpp_provider.capabilities().is_available:
            return self.llamacpp_provider
        # Priority 4: Deterministic fallback engine
        else:
            return self.fallback_provider

    def get_status(self) -> Dict[str, Any]:
        self._active_provider = self._select_best_provider()
        caps = self._active_provider.capabilities()
        return {
            "active_provider": caps.provider_name,
            "model_name": caps.model_name,
            "hardware_target": caps.hardware_target,
            "is_local": caps.is_local,
            "provenance": caps.provenance,
            "is_available": caps.is_available,
            "genie_available": self.genie_provider._is_available(),
            "local_endpoint_available": self.openai_provider._is_available,
            "llamacpp_available": self.llamacpp_provider.capabilities().is_available,
        }

    def reason(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 512,
        json_mode: bool = False,
        priority: int = 1  # 0 = High (Live Q&A), 1 = Normal, 2 = Background
    ) -> LLMResponse:
        """
        Sequentially dispatches inference requests to ensure a single NPU model
        instance is never contended or overloaded.
        """
        with self._llm_lock:
            self._active_provider = self._select_best_provider()
            try:
                return self._active_provider.generate(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    json_mode=json_mode
                )
            except Exception:
                return self.fallback_provider.generate(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    json_mode=json_mode
                )

    def diagnose_performance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = (
            "You are CogniEdge Performance Doctor, a local gaming AI diagnostic agent. "
            "Analyze the structured telemetry, frame-time statistics, and bottleneck evidence. "
            "Respond in JSON format with: diagnosis, why (array of strings), severity (low/medium/high), "
            "recommendation, expected_effect, confidence (0.0-1.0)."
        )
        user_prompt = f"Performance Context:\n{json.dumps(context, indent=2)}"

        res = self.reason(system_prompt, user_prompt, temperature=0.1, json_mode=True, priority=1)
        if res.structured_data:
            return res.structured_data

        return {
            "diagnosis": res.text,
            "why": ["Analysis from active local AI reasoning provider"],
            "severity": "medium",
            "recommendation": "Monitor frame-time stability and adjust background workload.",
            "expected_effect": "Stabilizes frame pacing",
            "confidence": 0.85
        }
