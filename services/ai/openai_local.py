"""
Local OpenAI-compatible LLM Provider
Connects to local inference servers (Ollama, LM Studio, vLLM, llama.cpp, LocalAI)
at endpoints like http://localhost:11434/v1 or http://localhost:1234/v1.
"""

import time
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from llm_provider import LocalLLMProvider, LLMCapabilities, LLMResponse


class OpenAILocalProvider(LocalLLMProvider):
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434/v1",
        model_name: str = "qwen2.5:3b",
        api_key: str = "local"
    ):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.api_key = api_key
        self._is_available = False
        self._hardware_target = "Local Inference Engine"
        self._check_availability()

    def _check_availability(self) -> bool:
        try:
            req = urllib.request.Request(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    models = [m.get("id", "") for m in data.get("data", [])]
                    self._is_available = True
                    for m in models:
                        if "qwen" in m.lower():
                            self.model_name = m
                            break
                    return True
        except Exception:
            self._is_available = False
        return False

    def health(self) -> Dict[str, Any]:
        available = self._check_availability()
        return {
            "status": "online" if available else "offline",
            "provider": "OpenAI-Compatible Local Endpoint",
            "base_url": self.base_url,
            "model_name": self.model_name,
            "available": available
        }

    def capabilities(self) -> LLMCapabilities:
        return LLMCapabilities(
            provider_name="OpenAI-Compatible Local",
            model_name=self.model_name,
            is_local=True,
            hardware_target="Local CPU/GPU Inference",
            context_length=8192,
            supports_tools=True,
            is_available=self._is_available,
            provenance="MEASURED" if self._is_available else "UNAVAILABLE"
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 512,
        json_mode: bool = False
    ) -> LLMResponse:
        start_t = time.perf_counter()
        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=req_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                content = resp_json["choices"][0]["message"]["content"].strip()
                latency_ms = (time.perf_counter() - start_t) * 1000.0
                tokens = resp_json.get("usage", {}).get("completion_tokens", len(content.split()))

                structured = None
                if json_mode:
                    try:
                        structured = json.loads(content)
                    except Exception:
                        pass

                return LLMResponse(
                    text=content,
                    structured_data=structured,
                    latency_ms=round(latency_ms, 1),
                    tokens_generated=tokens,
                    provider="OpenAI-Compatible Local",
                    hardware_target="Local Endpoint",
                    provenance="MEASURED"
                )
        except Exception as e:
            raise RuntimeError(f"OpenAI Local provider request failed: {e}")
