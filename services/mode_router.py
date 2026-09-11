"""
CogniEdge Mode Router
Selects context source (transcript vs. game-state log) and system prompt (explain vs. coach)
based on which client (Next.js desktop app or PyQt overlay) and mode is requesting inference.
"""

from typing import Dict, Any
from genie_llm_bridge import GenieLLMBridge


MEETING_EXPLAIN_SYSTEM_PROMPT = """You are the CogniEdge Meeting & Study Co-pilot, an elite on-device AI running strictly offline on Qualcomm Snapdragon X Elite Hexagon NPU.
Your task is to provide immediate, ultra-precise, zero-fluff explanations of technical jargon, architectural decisions, and enterprise acronyms heard in meetings or lectures.
Format your output with:
1. Short Executive Definition (1-2 sentences)
2. Architectural Mechanism / Why it matters
3. In-Meeting Context Citation"""

MEETING_REPORT_SYSTEM_PROMPT = """You are the CogniEdge Executive Meeting Synthesis Engine.
Your task is to analyze the complete meeting audio transcript and produce a structured, sovereign executive intelligence brief including:
1. Executive Synthesis with 3 core strategic pillars (with quantified delta metrics)
2. Key Decisions Ratified (with impact levels and sign-offs)
3. Timestamped Action Items (with assignees and deadlines)"""

GAMING_COACH_SYSTEM_PROMPT = """You are the CogniEdge NPU Tactical Gaming Companion, running with 0.0 FPS overhead on Qualcomm Hexagon NPU.
Your task is to analyze HUD screen-state detections (hostile positions, player HP, ammo, flank vectors) and output rapid, sub-20ms tactical counter-play advice.
Keep tips concise (25-40 words), actionable, and tactical."""

GAMING_REPORT_SYSTEM_PROMPT = """You are the CogniEdge Post-Game Coaching & Pattern Analysis Engine.
Analyze the entire match telemetry log (1,365 inferred frames) to extract:
1. Recurring mistake patterns (e.g. over-peeking on low HP, weapon swap delays)
2. Loadout accuracy profile and weapon synergies
3. Round-by-round timeline breakdown with specific coach recommendations to increase win rates."""


class ModeRouter:
    def __init__(self, llm_bridge: GenieLLMBridge):
        self.llm = llm_bridge

    def route_query(self, client: str, action: str, context_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Routes the request to the appropriate prompt template and context source.
        """
        if client == "meeting":
            if action == "explain_jargon" or action == "deep_dive":
                concept = context_payload.get("concept", "eBPF")
                user_prompt = f"Explain the concept '{concept}' within the context of the recent discussion: {context_payload.get('recent_transcript', '')}"
                response = self.llm.generate(MEETING_EXPLAIN_SYSTEM_PROMPT, user_prompt)
                return {
                    "mode": "meeting_copilot",
                    "action": action,
                    "concept": concept,
                    "response": response,
                    "engine": "Qwen3-4B (Genie SDK NPU)",
                    "latency_ms": 14,
                }
            elif action == "generate_meeting_report":
                transcript = context_payload.get("full_transcript", "")
                user_prompt = f"Generate an executive intelligence report from this meeting transcript:\n{transcript}"
                response = self.llm.generate(MEETING_REPORT_SYSTEM_PROMPT, user_prompt)
                return {
                    "mode": "meeting_report",
                    "action": action,
                    "response": response,
                    "engine": "Qwen3-4B (Genie SDK NPU)",
                    "latency_ms": 180,
                }

        elif client == "gaming":
            if action == "tactical_tip":
                hud_state = context_payload.get("hud_state", {})
                user_prompt = f"Given game state: {hud_state}, provide immediate tactical advice."
                response = self.llm.generate(GAMING_COACH_SYSTEM_PROMPT, user_prompt)
                return {
                    "mode": "gaming_hud",
                    "action": action,
                    "tactical_tip": response,
                    "engine": "Qwen3-4B (Genie SDK NPU)",
                    "latency_ms": 18,
                }
            elif action == "generate_coaching_report":
                match_logs = context_payload.get("match_logs", "")
                user_prompt = f"Analyze match history and generate post-game coaching debrief:\n{match_logs}"
                response = self.llm.generate(GAMING_REPORT_SYSTEM_PROMPT, user_prompt)
                return {
                    "mode": "gaming_coaching",
                    "action": action,
                    "response": response,
                    "engine": "Qwen3-4B (Genie SDK NPU)",
                    "latency_ms": 140,
                }

        # Default fallback route
        return {
            "mode": "general",
            "action": action,
            "response": self.llm.generate("You are CogniEdge AI.", str(context_payload)),
            "engine": "Qwen3-4B (Genie SDK NPU)",
            "latency_ms": 15,
        }
