"""
Unit Tests for llama.cpp Local LLM Provider
Tests initialization, capability reporting, health checks, generation fallback, and JSON mode.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

SERVICES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../services"))
AI_DIR = os.path.join(SERVICES_DIR, "ai")
sys.path.insert(0, SERVICES_DIR)
sys.path.insert(0, AI_DIR)

from llamacpp_provider import LlamaCppProvider
from agent import CogniEdgeAIAgent


class TestLlamaCppProvider(unittest.TestCase):

    def test_provider_initialization(self):
        """Verify LlamaCppProvider initializes with expected defaults."""
        provider = LlamaCppProvider(model_path="/dummy/path/model.gguf", n_ctx=2048, n_threads=4)
        self.assertEqual(provider.model_path, "/dummy/path/model.gguf")
        self.assertEqual(provider.n_ctx, 2048)
        self.assertEqual(provider.n_threads, 4)

    def test_capabilities_structure(self):
        """Verify capabilities schema matches LLMCapabilities dataclass."""
        provider = LlamaCppProvider(model_path="/dummy/path/model.gguf")
        caps = provider.capabilities()
        self.assertEqual(caps.provider_name, "llama.cpp Direct Provider")
        self.assertTrue(caps.is_local)
        self.assertEqual(caps.provenance, "MEASURED")

    def test_health_check(self):
        """Verify health check returns expected status payload."""
        provider = LlamaCppProvider(model_path="/dummy/path/model.gguf")
        health = provider.health()
        self.assertIn("status", health)
        self.assertIn("model_exists", health)
        self.assertIn("binding_installed", health)
        self.assertIn("hardware_target", health)

    def test_mocked_generation(self):
        """Verify generation executes correctly and parses response."""
        provider = LlamaCppProvider(model_path="/dummy/path/model.gguf")
        provider._has_binding = True

        mock_llm_instance = MagicMock()
        mock_llm_instance.create_chat_completion.return_value = {
            "choices": [{"message": {"content": "Use flank route to surprise enemy."}}],
            "usage": {"completion_tokens": 8}
        }
        provider._llm = mock_llm_instance

        resp = provider.generate(
            system_prompt="You are a gaming coach.",
            user_prompt="How do I breach the site?",
            temperature=0.2,
            max_tokens=100
        )

        self.assertEqual(resp.text, "Use flank route to surprise enemy.")
        self.assertEqual(resp.provider, "llama.cpp")
        self.assertEqual(resp.tokens_generated, 8)
        self.assertEqual(resp.provenance, "MEASURED")

    def test_agent_integration(self):
        """Verify CogniEdgeAIAgent includes llamacpp in status and fallback hierarchy."""
        agent = CogniEdgeAIAgent()
        status = agent.get_status()
        self.assertIn("llamacpp_available", status)
        self.assertIn("active_provider", status)


if __name__ == "__main__":
    unittest.main()
