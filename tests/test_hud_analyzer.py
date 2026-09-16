"""
Unit Tests for Game HUD Analyzer
Tests threat vector calculation and structured game state extraction across categories.
"""

import unittest
import os
import sys

SERVICES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../services"))
VISION_DIR = os.path.join(SERVICES_DIR, "vision")
sys.path.insert(0, SERVICES_DIR)
sys.path.insert(0, VISION_DIR)

from hud_analyzer import HUDAnalyzer
from vision_provider import DetectedObject, StructuredGameState


class TestHUDAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = HUDAnalyzer()

    def test_threat_vector_calculation_flanks(self):
        """Verify left flank, right flank, and center threats are properly categorized."""
        # Left side threat (x=200 on 1920px screen)
        left_threat = [DetectedObject(label="Hostile_Combatant", bbox=[200, 400, 60, 120], confidence=0.88)]
        self.assertEqual(
            self.analyzer.compute_threat_vector(left_threat, 1920),
            "Left Flank / West Corridor"
        )

        # Right side threat (x=1600 on 1920px screen)
        right_threat = [DetectedObject(label="Hostile_Combatant", bbox=[1600, 400, 60, 120], confidence=0.88)]
        self.assertEqual(
            self.analyzer.compute_threat_vector(right_threat, 1920),
            "Right Flank / East Corridor"
        )

        # Center threat (x=900 on 1920px screen)
        center_threat = [DetectedObject(label="Hostile_Combatant", bbox=[900, 400, 60, 120], confidence=0.88)]
        self.assertEqual(
            self.analyzer.compute_threat_vector(center_threat, 1920),
            "Direct Center / Frontal Threat"
        )

        # No threats
        self.assertEqual(self.analyzer.compute_threat_vector([], 1920), "Clear")

    def test_battle_royale_vitals_extraction(self):
        """Verify battle royale vitals and hostiles extraction."""
        detections = [
            DetectedObject(label="Hostile_Combatant", bbox=[500, 400, 50, 100], confidence=0.92),
            DetectedObject(label="Hostile_Combatant", bbox=[950, 400, 50, 100], confidence=0.89),
        ]

        state = self.analyzer.analyze(
            detections=detections,
            screen_size=(1920, 1080),
            game_category="Battle Royale",
            game_title="PUBG: BATTLEGROUNDS"
        )

        self.assertEqual(state.hostiles_count, 2)
        self.assertEqual(state.player.health, 65)
        self.assertTrue(state.confidence > 80.0)
        self.assertEqual(state.provenance, "MEASURED")

    def test_puzzle_game_state_extraction(self):
        """Verify puzzle game category state extraction."""
        state = self.analyzer.analyze(
            detections=[],
            screen_size=(1920, 1080),
            game_category="Puzzle / Problem Solving",
            game_title="Portal 2"
        )

        self.assertEqual(state.hostiles_count, 0)
        self.assertEqual(state.player.health, 100)
        self.assertEqual(state.threat_vector, "Puzzle Grid Active")


if __name__ == "__main__":
    unittest.main()
