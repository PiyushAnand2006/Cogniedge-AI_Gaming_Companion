"""
Qualcomm Snapdragon Genie SDK LLM Provider
Bridges to Hexagon NPU compiled Qwen3-4B bundle (genie-t2t-run.exe).
"""

import os
import re
import time
import json
import subprocess
from typing import Dict, Any, Optional
from llm_provider import LocalLLMProvider, LLMCapabilities, LLMResponse


class GenieProvider(LocalLLMProvider):
    def __init__(self, bundle_root: Optional[str] = None):
        self.bundle_root = bundle_root or os.environ.get("GENIE_BUNDLE_ROOT", "genie_bundle")
        self.genie_executable = os.path.join(self.bundle_root, "genie-t2t-run.exe")
        self.config_path = os.path.join(self.bundle_root, "genie_config.json")

    def _is_available(self) -> bool:
        return os.path.exists(self.genie_executable) and os.path.exists(self.config_path)

    def health(self) -> Dict[str, Any]:
        avail = self._is_available()
        return {
            "status": "online" if avail else "offline",
            "provider": "Qualcomm Genie SDK (Hexagon NPU)",
            "bundle_root": self.bundle_root,
            "available": avail
        }

    def capabilities(self) -> LLMCapabilities:
        avail = self._is_available()
        return LLMCapabilities(
            provider_name="Qualcomm Genie SDK",
            model_name="Qwen3-4B-Instruct-W4A16",
            is_local=True,
            hardware_target="Snapdragon Hexagon NPU",
            context_length=4096,
            supports_tools=True,
            is_available=avail,
            provenance="MEASURED" if avail else "UNAVAILABLE"
        )

    def format_qwen3_prompt(self, system_prompt: str, user_prompt: str) -> str:
        return (
            f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 512,
        json_mode: bool = False
    ) -> LLMResponse:
        if not self._is_available():
            raise RuntimeError("Genie SDK hardware binary or model bundle not found on host.")

        raw_prompt = self.format_qwen3_prompt(system_prompt, user_prompt)
        start_t = time.perf_counter()

        cmd = [
            self.genie_executable,
            "-c", self.config_path,
            "-p", raw_prompt
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        latency_ms = (time.perf_counter() - start_t) * 1000.0

        if result.returncode != 0:
            raise RuntimeError(f"Genie execution failed with code {result.returncode}: {result.stderr}")

        output = result.stdout
        cleaned = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL).strip()

        structured = None
        if json_mode:
            try:
                match = re.search(r"\{.*\}", cleaned, re.DOTALL)
                if match:
                    structured = json.loads(match.group(0))
            except Exception:
                pass

        return LLMResponse(
            text=cleaned,
            structured_data=structured,
            latency_ms=round(latency_ms, 1),
            tokens_generated=len(cleaned.split()),
            provider="Qualcomm Genie SDK",
            hardware_target="Hexagon NPU",
            provenance="MEASURED"
        )
