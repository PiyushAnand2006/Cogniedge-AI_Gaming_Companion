"""
Player Recurring Pattern Engine
Derives recurring gameplay vulnerabilities and cross-session improvements:
- Sub-30% HP over-engagement
- Late defensive rotations
- Left-flank vulnerability
"""

from typing import List, Dict, Any
from repository import MemoryRepository


class PlayerPatternEngine:
    def __init__(self, repo: MemoryRepository):
        self.repo = repo

    def seed_initial_patterns_if_empty(self, game_title: str = "Cyberpunk 2077"):
        """Seeds realistic initial pattern observations for the hackathon player profile."""
        existing = self.repo.get_player_patterns(game_title)
        if not existing:
            self.repo.upsert_player_pattern(
                game_title=game_title,
                pattern_name="Low HP (<30%) Over-Engagement",
                category="TACTICAL",
                description="Tendency to push duels when health is under 30% rather than securing cover or healing.",
                corrected=True
            )
            # Add occurrence count
            for _ in range(14):
                self.repo.upsert_player_pattern(
                    game_title=game_title,
                    pattern_name="Low HP (<30%) Over-Engagement",
                    category="TACTICAL",
                    description="Tendency to push duels when health is under 30% rather than securing cover or healing.",
                    corrected=True if _ % 2 == 0 else False
                )

            for _ in range(9):
                self.repo.upsert_player_pattern(
                    game_title=game_title,
                    pattern_name="Delayed Defensive Rotation",
                    category="POSITIONING",
                    description="Remaining anchored in exposed choke points >8 seconds after radar flank warnings.",
                    corrected=True if _ > 4 else False
                )

            for _ in range(6):
                self.repo.upsert_player_pattern(
                    game_title=game_title,
                    pattern_name="Left-Flank Sector Blindspot",
                    category="POSITIONING",
                    description="Elevated death rate from blind spot entries on asymmetric left corridors.",
                    corrected=False
                )

    def analyze_session_patterns(self, session_id: str, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifies recurring pattern candidate triggers from live events."""
        insights = []
        low_hp_deaths = sum(1 for e in events if e.get("event_type") == "LOW_HP_DEATH")
        if low_hp_deaths >= 2:
            insights.append({
                "pattern": "Low HP Over-Engagement",
                "evidence": f"{low_hp_deaths} combat deaths occurred while below 30% health.",
                "action": "Reinforce 2-second retreat rule in upcoming session advice."
            })
        return insights
