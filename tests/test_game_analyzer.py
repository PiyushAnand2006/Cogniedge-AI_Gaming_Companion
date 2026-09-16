"""
CogniEdge Game Analyzer & Dynamic Game-Type Classification Test Suite
Tests foreground window tracking, multi-tier genre classification,
heuristic keyword analysis, AI zero-shot reasoning, and cache persistence.
"""

import sys
import os
import unittest
import json
import sqlite3

# Add services to path
SERVICES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../services"))
sys.path.insert(0, SERVICES_DIR)
sys.path.insert(0, os.path.join(SERVICES_DIR, "ai"))
sys.path.insert(0, os.path.join(SERVICES_DIR, "memory"))
sys.path.insert(0, os.path.join(SERVICES_DIR, "core"))

from game_analyzer import GameAnalyzer, GameGenre, GameProfile
from ai.agent import CogniEdgeAIAgent
from memory.database import init_database
from memory.repository import MemoryRepository


class TestGameAnalyzer(unittest.TestCase):

    def setUp(self):
        self.test_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_game_catalog.db"))
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except Exception:
                pass
        self.ai_agent = CogniEdgeAIAgent(preferred_provider="fallback")
        self.analyzer = GameAnalyzer(db_path=self.test_db, ai_agent=self.ai_agent)

    def tearDown(self):
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except Exception:
                pass

    def test_battle_royale_detection(self):
        """Test detection and catalog classification of Battle Royale games (Free Fire, PUBG)."""
        # Free Fire MAX
        ff_profile = self.analyzer.classify_game("Free Fire MAX", "FreeFire.exe")
        self.assertEqual(ff_profile.genre, GameGenre.BATTLE_ROYALE)
        self.assertEqual(ff_profile.title, "Free Fire MAX")
        self.assertEqual(ff_profile.hud_schema["analysis_mode"], "TACTICAL_COMBAT")
        self.assertTrue(any("Gloo wall" in f or "Zone rotation" in f for f in ff_profile.coaching_focus))

        # PUBG
        pubg_profile = self.analyzer.classify_game("PUBG: BATTLEGROUNDS - Direct3D 12", "TslGame.exe")
        self.assertEqual(pubg_profile.genre, GameGenre.BATTLE_ROYALE)
        self.assertEqual(pubg_profile.title, "PUBG: BATTLEGROUNDS")

    def test_puzzle_logic_detection(self):
        """Test detection and catalog classification of Puzzle / Problem Solving games."""
        # Portal 2
        portal_profile = self.analyzer.classify_game("Portal 2", "portal2.exe")
        self.assertEqual(portal_profile.genre, GameGenre.PUZZLE_LOGIC)
        self.assertEqual(portal_profile.hud_schema["analysis_mode"], "PROBLEM_SOLVING")
        self.assertFalse(portal_profile.hud_schema["threat_tracking"])
        self.assertTrue(any("trajectory" in f or "hints" in f for f in portal_profile.coaching_focus))

        # The Witness
        witness_profile = self.analyzer.classify_game("The Witness (x64)", "witness64_d3d11.exe")
        self.assertEqual(witness_profile.genre, GameGenre.PUZZLE_LOGIC)

        # Baba Is You
        baba_profile = self.analyzer.classify_game("Baba Is You", "Baba Is You.exe")
        self.assertEqual(baba_profile.genre, GameGenre.PUZZLE_LOGIC)

        # Sudoku
        sudoku_profile = self.analyzer.classify_game("Sudoku Master v1.4", "sudoku.exe")
        self.assertEqual(sudoku_profile.genre, GameGenre.PUZZLE_LOGIC)

    def test_tactical_fps_detection(self):
        """Test Counter-Strike 2 & Valorant."""
        cs2_profile = self.analyzer.classify_game("Counter-Strike 2", "cs2.exe")
        self.assertEqual(cs2_profile.genre, GameGenre.FPS_TACTICAL)
        self.assertEqual(cs2_profile.hud_schema["analysis_mode"], "TACTICAL_COMBAT")

    def test_heuristic_keyword_classification(self):
        """Test arbitrary unknown game titles classified via heuristic keywords."""
        # Unknown puzzle game
        mystery_puzzle = self.analyzer.classify_game("Chamber Escape: Mind Riddles", "mind_riddles.exe")
        self.assertEqual(mystery_puzzle.genre, GameGenre.PUZZLE_LOGIC)
        self.assertEqual(mystery_puzzle.hud_schema["analysis_mode"], "PROBLEM_SOLVING")

        # Unknown battle royale
        mystery_br = self.analyzer.classify_game("Neon Island Royale v2.0", "island_royale.exe")
        self.assertEqual(mystery_br.genre, GameGenre.BATTLE_ROYALE)

    def test_title_normalization(self):
        """Test cleaning of window titles."""
        raw_1 = "Cyberpunk 2077 - Direct3D 12 (Win64) - Steam"
        clean_1 = self.analyzer.normalize_title(raw_1, "Cyberpunk2077.exe")
        self.assertEqual(clean_1, "Cyberpunk 2077")

        raw_2 = "Apex Legends (64-bit, DX11) - Epic Games"
        clean_2 = self.analyzer.normalize_title(raw_2, "r5apex.exe")
        self.assertEqual(clean_2, "Apex Legends")

    def test_manual_override_and_clear(self):
        """Test setting manual override and clearing."""
        profile = self.analyzer.set_manual_override("Portal 2")
        self.assertEqual(profile.title, "Portal 2")
        self.assertEqual(profile.provenance, "MANUAL")
        self.assertEqual(self.analyzer.detect_active_game().title, "Portal 2")

        self.analyzer.clear_manual_override()

    def test_sqlite_catalog_persistence(self):
        """Test that classified games are cached in SQLite for sub-millisecond retrieval."""
        custom_game = self.analyzer.classify_game("Quantum Logic Physics Puzzles", "quantum_logic.exe")
        self.assertEqual(custom_game.genre, GameGenre.PUZZLE_LOGIC)

        # Check DB directly
        conn = sqlite3.connect(self.test_db)
        cur = conn.cursor()
        cur.execute("SELECT genre, category FROM game_catalog WHERE title = ?", ("Quantum Logic Physics Puzzles",))
        row = cur.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], GameGenre.PUZZLE_LOGIC)


if __name__ == "__main__":
    unittest.main()
