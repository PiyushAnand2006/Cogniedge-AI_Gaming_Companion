"""
CogniEdge llama.cpp Local LLM Provider
Direct GGUF inference backend using llama-cpp-python or llama.cpp binary interface.
Runs on-device quantized models (Qwen, Llama, Phi) with zero cloud dependency.
"""

import os
import sys
import json
import time
import subprocess
from typing import Dict, Any, Optional

from llm_provider import LocalLLMProvider, LLMResponse, LLMCapabilities
from model_manager import model_manager, LLM_MODEL_CONFIG


class LlamaCppProvider(LocalLLMProvider):
    """
    Direct in-process LLM inference provider backed by llama.cpp.
    Prioritizes Python bindings (llama-cpp-python), with binary fallback.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        n_ctx: int = 4096,
        n_threads: Optional[int] = None,
        n_gpu_layers: int = 0
    ):
        self.model_path = model_path or model_manager.llm_model_path
        self.n_ctx = n_ctx
        self.n_threads = n_threads or max(4, (os.cpu_count() or 8) // 2)
        self.n_gpu_layers = n_gpu_layers
        self._llm = None
        self._is_available = False
        self._hardware_target = "CPU"
        self._check_and_init()

    def _check_and_init(self):
        """Check if llama.cpp bindings and model file are available."""
        try:
            import llama_cpp
            self._has_binding = True
        except ImportError:
            self._has_binding = False

        if self._has_binding and os.path.exists(self.model_path):
            self._is_available = True
        else:
            self._is_available = False

    def _ensure_loaded(self):
        """Lazy-load the model into memory on first request."""
        if self._llm is not None:
            return

        if not self._has_binding:
            raise RuntimeError(
                "llama-cpp-python is not installed. Install with: pip install llama-cpp-python"
            )

        if not os.path.exists(self.model_path):
            # Attempt auto-download via model manager
            print(f"[LlamaCppProvider] Model not found locally. Initiating download...")
            self.model_path = model_manager.download_llm_model()

        import llama_cpp
        print(f"[LlamaCppProvider] Loading GGUF model: {self.model_path} (threads={self.n_threads}, ctx={self.n_ctx})")
        
        # Check GPU offload capability
        try:
            self._llm = llama_cpp.Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                n_gpu_layers=self.n_gpu_layers,
                verbose=False
            )
            self._hardware_target = f"CPU ({self.n_threads} threads)" if self.n_gpu_layers == 0 else f"GPU/CPU ({self.n_gpu_layers} layers offloaded)"
            self._is_available = True
            print(f"[LlamaCppProvider] Model loaded successfully on {self._hardware_target}")
        except Exception as e:
            print(f"[LlamaCppProvider] Failed to load model: {e}")
            self._is_available = False
            raise

    def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if self._is_available else "standby",
            "model_path": self.model_path,
            "model_exists": os.path.exists(self.model_path),
            "binding_installed": self._has_binding,
            "model_loaded": self._llm is not None,
            "hardware_target": self._hardware_target,
            "provenance": "MEASURED"
        }

    def capabilities(self) -> LLMCapabilities:
        return LLMCapabilities(
            provider_name="llama.cpp Direct Provider",
            model_name=LLM_MODEL_CONFIG.get("description", "Qwen2.5-3B-Instruct GGUF"),
            is_local=True,
            hardware_target=self._hardware_target,
            context_length=self.n_ctx,
            supports_tools=True,
            is_available=self._is_available or os.path.exists(self.model_path),
            provenance="MEASURED"
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 512,
        json_mode: bool = False
    ) -> LLMResponse:
        self._ensure_loaded()

        start_time = time.time()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response_format = {"type": "json_object"} if json_mode else None

        try:
            output = self._llm.create_chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format
            )

            latency_ms = (time.time() - start_time) * 1000.0
            content = output["choices"][0]["message"]["content"].strip()
            tokens_generated = output.get("usage", {}).get("completion_tokens", len(content.split()))

            structured_data = None
            if json_mode:
                try:
                    structured_data = json.loads(content)
                except Exception:
                    # Strip possible markdown code fence
                    clean = content.strip()
                    if clean.startswith("```json"):
                        clean = clean[7:]
                    if clean.startswith("```"):
                        clean = clean[3:]
                    if clean.endswith("```"):
                        clean = clean[:-3]
                    try:
                        structured_data = json.loads(clean.strip())
                    except Exception:
                        pass

            return LLMResponse(
                text=content,
                structured_data=structured_data,
                latency_ms=round(latency_ms, 2),
                tokens_generated=tokens_generated,
                provider="llama.cpp",
                hardware_target=self._hardware_target,
                provenance="MEASURED"
            )

        except Exception as e:
            print(f"[LlamaCppProvider] Generation failed: {e}")
            raise
