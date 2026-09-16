"""
CogniEdge Game Analyzer & Dynamic Classifier
Automatically detects the currently focused game application on Windows,
extracts the clean title, classifies the game genre, and determines the
adaptive coaching profile and HUD schema.
"""

import sys
import os
import time
import re
import json
import threading
import sqlite3
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict

# Windows API imports
try:
    import ctypes
    from ctypes import wintypes
    USER32_AVAILABLE = True
except ImportError:
    USER32_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


# ─────────────────────────────────────────────────────────────
# Game Categories & Genres Taxonomy
# ─────────────────────────────────────────────────────────────

class GameGenre:
    BATTLE_ROYALE = "Battle Royale"
    FPS_TACTICAL = "Tactical FPS"
    PUZZLE_LOGIC = "Puzzle / Problem Solving"
    ACTION_RPG = "Action RPG"
    STRATEGY_RTS = "Strategy / RTS"
    SPORTS_RACING = "Sports / Racing"
    PLATFORMER_INDIE = "Platformer / Action"
    SIMULATION_SURVIVAL = "Simulation / Survival"
    FIGHTING = "Fighting / Combat"
    GENERAL = "General Gaming"


@dataclass
class GameProfile:
    title: str
    genre: str
    category: str
    gameplay_loop: str
    coaching_focus: List[str]
    hud_schema: Dict[str, Any]
    process_name: Optional[str] = None
    confidence: float = 1.0
    provenance: str = "CATALOG"  # CATALOG, HEURISTIC, AI_NPU, MANUAL, STANDBY

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ─────────────────────────────────────────────────────────────
# Tier-1 Fast Catalog (Pre-compiled popular games)
# ─────────────────────────────────────────────────────────────

KNOWN_GAME_CATALOG: Dict[str, Dict[str, Any]] = {
    # Battle Royale
    "freefire": {
        "title": "Free Fire MAX",
        "genre": GameGenre.BATTLE_ROYALE,
        "category": "Fast-Paced Battle Royale",
        "gameplay_loop": "Looting, zone positioning, close-quarters gunplay, squad survival",
        "coaching_focus": [
            "Zone rotation timing & blue wall pacing",
            "Gloo wall deployment speed & cover mechanics",
            "Close-range headshot tracking & crosshair placement",
            "High-risk engagement vs defensive positioning"
        ],
        "hud_schema": {
            "primary_metric": "Hostiles in Range",
            "threat_tracking": True,
            "vitals_monitoring": ["HP", "EP", "Armor", "Ammo"],
            "analysis_mode": "TACTICAL_COMBAT"
        }
    },
    "pubg": {
        "title": "PUBG: BATTLEGROUNDS",
        "genre": GameGenre.BATTLE_ROYALE,
        "category": "Tactical Battle Royale",
        "gameplay_loop": "Long-range ballistics, vehicle traversal, compound defense, tactical positioning",
        "coaching_focus": [
            "Recoil compensation & tap-fire spray patterns",
            "Compound holding & peripheral threat awareness",
            "Vehicle hard-cover usage in open circles",
            "Utility & smoke grenade deployment pacing"
        ],
        "hud_schema": {
            "primary_metric": "Threat Vector",
            "threat_tracking": True,
            "vitals_monitoring": ["Health", "Boost", "Helmet", "Vest"],
            "analysis_mode": "TACTICAL_COMBAT"
        }
    },
    "apex": {
        "title": "Apex Legends",
        "genre": GameGenre.BATTLE_ROYALE,
        "category": "Hero Movement Shooter",
        "gameplay_loop": "High-mobility combat, ability synergies, shield swapping, vertical repositioning",
        "coaching_focus": [
            "Slide-jump momentum & vertical cover usage",
            "Tactical ability cooldown timing",
            "Shield swap speed during third-party engagements",
            "Frametime variance control during 3-squad clashes"
        ],
        "hud_schema": {
            "primary_metric": "Enemy Squad Proximity",
            "threat_tracking": True,
            "vitals_monitoring": ["HP", "Shield", "Ultimate Charge"],
            "analysis_mode": "TACTICAL_COMBAT"
        }
    },
    "fortnite": {
        "title": "Fortnite",
        "genre": GameGenre.BATTLE_ROYALE,
        "category": "Building Battle Royale",
        "gameplay_loop": "High ground retakes, piece control, storm surge pacing, spatial building",
        "coaching_focus": [
            "Piece control & edit speed under pressure",
            "Material conservation for endgame rotations",
            "Height advantage maintenance",
            "Input latency & micro-stutter tracking"
        ],
        "hud_schema": {
            "primary_metric": "Opponent Distance",
            "threat_tracking": True,
            "vitals_monitoring": ["HP", "Shield", "Materials"],
            "analysis_mode": "TACTICAL_COMBAT"
        }
    },

    # Tactical FPS
    "cs2": {
        "title": "Counter-Strike 2",
        "genre": GameGenre.FPS_TACTICAL,
        "category": "Round-Based Tactical Shooter",
        "gameplay_loop": "Angle holding, execute utility lineups, economy management, crosshair placement",
        "coaching_focus": [
            "Head-level pre-aiming & corner clearing",
            "Counter-strafing velocity synchronization",
            "Round economy & buy-phase decision tracking",
            "Frametime consistency & 1% low latency"
        ],
        "hud_schema": {
            "primary_metric": "Crosshair Alignment",
            "threat_tracking": True,
            "vitals_monitoring": ["HP", "Armor", "Money", "Utility"],
            "analysis_mode": "TACTICAL_COMBAT"
        }
    },
    "valorant": {
        "title": "Valorant",
        "genre": GameGenre.FPS_TACTICAL,
        "category": "Tactical Hero Shooter",
        "gameplay_loop": "Site executes, agent utility combos, crosshair placement, retake coordination",
        "coaching_focus": [
            "First-bullet accuracy & movement deadzoning",
            "Ultimate economy tracking across rounds",
            "Post-plant positioning & defusal timing",
            "NPU zero-latency voice callout assistance"
        ],
        "hud_schema": {
            "primary_metric": "Site Threat Level",
            "threat_tracking": True,
            "vitals_monitoring": ["HP", "Shield", "Abilities", "Credits"],
            "analysis_mode": "TACTICAL_COMBAT"
        }
    },

    # Puzzle & Problem Solving
    "portal": {
        "title": "Portal 2",
        "genre": GameGenre.PUZZLE_LOGIC,
        "category": "Spatial Physics Puzzle",
        "gameplay_loop": "Momentum preservation, portal trajectory planning, laser routing, test chamber problem solving",
        "coaching_focus": [
            "Spatial trajectory & velocity conservation analysis",
            "Laser routing & weighted button sequence deduction",
            "Step-by-step logic hints when decision time stalls",
            "Chamber solve time efficiency & pattern recognition"
        ],
        "hud_schema": {
            "primary_metric": "Chamber Solve Efficiency",
            "threat_tracking": False,
            "vitals_monitoring": ["Step Efficiency", "Solve Time", "Portal Placements"],
            "analysis_mode": "PROBLEM_SOLVING"
        }
    },
    "witness": {
        "title": "The Witness",
        "genre": GameGenre.PUZZLE_LOGIC,
        "category": "Environmental Line Puzzle",
        "gameplay_loop": "Grid rule deduction, environmental perspective alignment, visual logic deduction",
        "coaching_focus": [
            "Grid rule deduction (polyominoes, color isolation, symmetry)",
            "Environmental line perspective hints",
            "Logical constraint verification before execution",
            "Puzzle cluster completion tracking"
        ],
        "hud_schema": {
            "primary_metric": "Constraint Validation",
            "threat_tracking": False,
            "vitals_monitoring": ["Panel Complexity", "Rule Set", "Deduction Phase"],
            "analysis_mode": "PROBLEM_SOLVING"
        }
    },
    "baba": {
        "title": "Baba Is You",
        "genre": GameGenre.PUZZLE_LOGIC,
        "category": "Rule-Manipulation Logic Puzzle",
        "gameplay_loop": "Grammar syntax modification, word block movement, condition-action inversion",
        "coaching_focus": [
            "Syntactic rule chain analysis (Noun Is Property/Noun)",
            "Win condition path verification",
            "Infinite loop / soft-lock prevention hints",
            "Transformation sequence planning"
        ],
        "hud_schema": {
            "primary_metric": "Active Rule Syntaxes",
            "threat_tracking": False,
            "vitals_monitoring": ["Rule Count", "Transformation State", "Moves"],
            "analysis_mode": "PROBLEM_SOLVING"
        }
    },
    "talos": {
        "title": "The Talos Principle",
        "genre": GameGenre.PUZZLE_LOGIC,
        "category": "Philosophical Spatial Puzzle",
        "gameplay_loop": "Connector beam redirection, jammer placement, time recording clone coordination",
        "coaching_focus": [
            "Beam connector line-of-sight analysis",
            "Time recording timeline synchronization",
            "Sigil gate unlocking requirements",
            "Logical trial-and-error reduction hints"
        ],
        "hud_schema": {
            "primary_metric": "Sigil Progress",
            "threat_tracking": False,
            "vitals_monitoring": ["Active Beams", "Recorded Timeline", "Sigils"],
            "analysis_mode": "PROBLEM_SOLVING"
        }
    },
    "sudoku": {
        "title": "Sudoku Master",
        "genre": GameGenre.PUZZLE_LOGIC,
        "category": "Combinatorial Number Puzzle",
        "gameplay_loop": "Row/column/box candidate elimination, naked pairs, X-wing logic deduction",
        "coaching_focus": [
            "Candidate elimination & single possibility hints",
            "Row, column, and 3x3 box constraint verification",
            "Advanced solving techniques (Naked Triples, Hidden Pairs)",
            "Error detection without spoiling solutions"
        ],
        "hud_schema": {
            "primary_metric": "Grid Completion Rate",
            "threat_tracking": False,
            "vitals_monitoring": ["Empty Cells", "Mistakes", "Elapsed Time"],
            "analysis_mode": "PROBLEM_SOLVING"
        }
    },
    "tetris": {
        "title": "Tetris Effect",
        "genre": GameGenre.PUZZLE_LOGIC,
        "category": "Falling Block Spatial Puzzle",
        "gameplay_loop": "Matrix stacking, T-spin setups, line clears, speed management",
        "coaching_focus": [
            "Flat matrix maintenance & hole prevention",
            "T-Spin and 4-wide setup recognition",
            "Piece preview queue management",
            "Input responsiveness & drop speed pacing"
        ],
        "hud_schema": {
            "primary_metric": "Stack Height",
            "threat_tracking": False,
            "vitals_monitoring": ["Lines Cleared", "PPS (Pieces/Sec)", "Score"],
            "analysis_mode": "PROBLEM_SOLVING"
        }
    },

    # Action RPG
    "cyberpunk": {
        "title": "Cyberpunk 2077",
        "genre": GameGenre.ACTION_RPG,
        "category": "Open-World Sci-Fi RPG",
        "gameplay_loop": "Cyberware builds, perk optimization, quickhacking, boss combat tactics",
        "coaching_focus": [
            "RAM allocation & quickhack queue synergy",
            "Cyberware armor threshold vs stamina consumption",
            "Boss attack telegraph dodge timing",
            "Ray tracing performance & GPU VRAM stability"
        ],
        "hud_schema": {
            "primary_metric": "Combat Alert Status",
            "threat_tracking": True,
            "vitals_monitoring": ["HP", "Cyberware RAM", "Stamina", "Ammo"],
            "analysis_mode": "TACTICAL_COMBAT"
        }
    },
    "eldenring": {
        "title": "Elden Ring",
        "genre": GameGenre.ACTION_RPG,
        "category": "Souls-like Action RPG",
        "gameplay_loop": "Boss pattern recognition, stamina management, poise breaking, build optimization",
        "coaching_focus": [
            "Boss telegraph timing & attack delay tracking",
            "Stamina recovery pacing & rolling window discipline",
            "Poise damage buildup & critical riposte timing",
            "Flask and mana allocation efficiency"
        ],
        "hud_schema": {
            "primary_metric": "Boss Poise Gauge",
            "threat_tracking": True,
            "vitals_monitoring": ["HP", "FP", "Stamina", "Flasks"],
            "analysis_mode": "TACTICAL_COMBAT"
        }
    }
}

# System processes to ignore
IGNORED_PROCESS_NAMES = {
    "explorer.exe", "chrome.exe", "firefox.exe", "msedge.exe", "brave.exe",
    "code.exe", "antigravity.exe", "devenv.exe", "taskmgr.exe", "cmd.exe",
    "powershell.exe", "pwsh.exe", "conhost.exe", "windowsterminal.exe",
    "searchhost.exe", "shellexperiencehost.exe", "startmenuexperiencehost.exe",
    "python.exe", "pythonw.exe", "node.exe", "systemsettings.exe",
    "applicationframehost.exe", "lockapp.exe", "discord.exe", "spotify.exe",
    "steam.exe", "steamservice.exe", "epicgameslauncher.exe", "obs64.exe"
}


# ─────────────────────────────────────────────────────────────
# Game Analyzer Core
# ─────────────────────────────────────────────────────────────

class GameAnalyzer:
    """
    On-device game detection and dynamic classification engine.
    Probes Windows foreground window & active process, matching against
    local catalog, heuristic normalizers, and local AI reasoning.
    """

    def __init__(self, db_path: Optional[str] = None, ai_agent=None):
        self.db_path = db_path or os.path.abspath(os.path.join(os.path.dirname(__file__), "cogniedge.db"))
        self.ai_agent = ai_agent
        self._lock = threading.Lock()
        self._last_detected_profile: Optional[GameProfile] = None
        self._manual_override_profile: Optional[GameProfile] = None
        self._init_db()

    def _init_db(self):
        """Create game_catalog caching table in SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS game_catalog (
                    process_or_key TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    category TEXT NOT NULL,
                    gameplay_loop TEXT,
                    coaching_focus TEXT,
                    hud_schema TEXT,
                    confidence REAL,
                    provenance TEXT,
                    updated_at REAL
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[GameAnalyzer DB Init] Warning: {e}")

    def _get_cached_profile(self, key: str) -> Optional[GameProfile]:
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT * FROM game_catalog WHERE process_or_key = ?", (key.lower(),))
            row = cur.fetchone()
            conn.close()
            if row:
                return GameProfile(
                    process_name=row[0],
                    title=row[1],
                    genre=row[2],
                    category=row[3],
                    gameplay_loop=row[4] or "",
                    coaching_focus=json.loads(row[5]) if row[5] else [],
                    hud_schema=json.loads(row[6]) if row[6] else {},
                    confidence=row[7] or 0.9,
                    provenance=row[8] or "DATABASE"
                )
        except Exception:
            pass
        return None

    def _save_profile_to_cache(self, key: str, profile: GameProfile):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO game_catalog
                (process_or_key, title, genre, category, gameplay_loop, coaching_focus, hud_schema, confidence, provenance, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                key.lower(),
                profile.title,
                profile.genre,
                profile.category,
                profile.gameplay_loop,
                json.dumps(profile.coaching_focus),
                json.dumps(profile.hud_schema),
                profile.confidence,
                profile.provenance,
                time.time()
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[GameAnalyzer Cache Save] Error: {e}")

    def get_foreground_window_info(self) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        """
        Retrieves (window_title, process_name, pid) of the current foreground window on Windows.
        """
        if not USER32_AVAILABLE:
            return None, None, None

        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return None, None, None

            # Get Window Title
            length = user32.GetWindowTextLengthW(hwnd)
            title = ""
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value.strip()

            # Get Process ID
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            process_id = pid.value

            # Get Process Name via psutil
            process_name = None
            if PSUTIL_AVAILABLE and process_id > 0:
                try:
                    proc = psutil.Process(process_id)
                    process_name = proc.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            return title, process_name, process_id

        except Exception as e:
            print(f"[GameAnalyzer Foreground Win32] Warning: {e}")
            return None, None, None

    def normalize_title(self, raw_title: str, process_name: Optional[str] = None) -> str:
        """Cleans up raw window titles removing engine/window suffixes."""
        if not raw_title:
            if process_name:
                name_clean = re.sub(r'\.exe$', '', process_name, flags=re.IGNORECASE)
                name_clean = re.sub(r'[-_](shipping|win64|x64|steam|dx11|dx12)', '', name_clean, flags=re.IGNORECASE)
                return name_clean.replace('_', ' ').title()
            return "Active Game"

        title = raw_title
        # Strip common game launcher/storefront artifacts
        title = re.sub(r'\s*-\s*(Steam|Epic Games|GOG\.com|Ubisoft Connect|Origin|Battle\.net|Riot Client).*$', '', title, flags=re.IGNORECASE)
        # Strip graphics engine / Direct3D / architecture tags
        title = re.sub(r'\s*-\s*(Direct3D\s*1\d|DirectX\s*1\d|Vulkan|OpenGL|Unity|Unreal Engine|64-bit|32-bit).*$', '', title, flags=re.IGNORECASE)
        # Strip parenthetical architecture/build tags (e.g. (64-bit, DX11), (x64), (Shipping))
        title = re.sub(r'\s*\([^)]*(?:64-bit|32-bit|x64|win64|dx\d+|vulkan|shipping|build)[^)]*\).*$', '', title, flags=re.IGNORECASE)
        # Strip version tags
        title = re.sub(r'\s*v\d+(\.\d+)+.*$', '', title, flags=re.IGNORECASE)
        return title.strip() or (process_name or "Active Game")

    def classify_game(
        self,
        raw_title: str,
        process_name: Optional[str] = None
    ) -> GameProfile:
        """
        Multi-tier classifier:
        Tier 1: Fast Catalog Key Match
        Tier 2: Cached DB Lookup
        Tier 3: Heuristic Regex / Keyword Matching
        Tier 4: On-Device AI Zero-Shot Reasoning (Genie / Local Qwen)
        """
        clean_title = self.normalize_title(raw_title, process_name)
        search_key = (process_name or clean_title).lower()
        title_lower = clean_title.lower()

        # ── Tier 1: Fast Catalog Key Match ──
        for key, entry in KNOWN_GAME_CATALOG.items():
            if key in search_key or key in title_lower:
                return GameProfile(
                    title=entry["title"],
                    genre=entry["genre"],
                    category=entry["category"],
                    gameplay_loop=entry["gameplay_loop"],
                    coaching_focus=entry["coaching_focus"],
                    hud_schema=entry["hud_schema"],
                    process_name=process_name,
                    confidence=0.98,
                    provenance="CATALOG"
                )

        # ── Tier 2: Check SQLite Cache ──
        cached = self._get_cached_profile(clean_title)
        if cached:
            return cached

        # ── Tier 3: Heuristic Keyword Analysis ──
        heuristic_profile = self._heuristic_classify(clean_title, process_name)
        if heuristic_profile.confidence >= 0.85:
            self._save_profile_to_cache(clean_title, heuristic_profile)
            return heuristic_profile

        # ── Tier 4: On-Device AI Reasoning ──
        if self.ai_agent:
            ai_profile = self._ai_classify(clean_title, process_name)
            if ai_profile:
                self._save_profile_to_cache(clean_title, ai_profile)
                return ai_profile

        # Fallback to heuristic
        self._save_profile_to_cache(clean_title, heuristic_profile)
        return heuristic_profile

    def _heuristic_classify(self, clean_title: str, process_name: Optional[str]) -> GameProfile:
        """Pattern matching for genres like puzzle, battle royale, shooter, rpg, racing."""
        text = f"{clean_title} {process_name or ''}".lower()

        # Puzzle / Problem Solving
        if any(w in text for w in ["puzzle", "portal", "witness", "baba", "talos", "sudoku", "chess", "tetris", "escape", "logic", "riddle", "solve", "brain", "match3", "physics"]):
            return GameProfile(
                title=clean_title,
                genre=GameGenre.PUZZLE_LOGIC,
                category="Problem Solving & Logic Deduction",
                gameplay_loop="Rule deduction, spatial mechanics, constraint validation, step-by-step solutions",
                coaching_focus=[
                    "Logical rule analysis & decision bottleneck detection",
                    "Step-by-step hints when problem solving stalls",
                    "Pattern recognition across puzzle chambers",
                    "Efficiency and move minimization tracking"
                ],
                hud_schema={
                    "primary_metric": "Problem Solving Pacing",
                    "threat_tracking": False,
                    "vitals_monitoring": ["Solve Time", "Deduction Phase", "Move Efficiency"],
                    "analysis_mode": "PROBLEM_SOLVING"
                },
                process_name=process_name,
                confidence=0.88,
                provenance="HEURISTIC"
            )

        # Battle Royale / Fast-Paced Shooter
        if any(w in text for w in ["royale", "pubg", "freefire", "free fire", "fortnite", "apex", "warzone", "surviv"]):
            return GameProfile(
                title=clean_title,
                genre=GameGenre.BATTLE_ROYALE,
                category="Survival & Combat Shooter",
                gameplay_loop="Zone rotations, compound control, situational awareness, recoil management",
                coaching_focus=[
                    "Zone pacing & blue wall rotation strategy",
                    "Crosshair placement & recoil reset timing",
                    "Peripheral threat awareness & enemy counts",
                    "Cover usage & armor replenishment cadence"
                ],
                hud_schema={
                    "primary_metric": "Hostile Proximity",
                    "threat_tracking": True,
                    "vitals_monitoring": ["HP", "Armor", "Ammo", "Zone Timer"],
                    "analysis_mode": "TACTICAL_COMBAT"
                },
                process_name=process_name,
                confidence=0.90,
                provenance="HEURISTIC"
            )

        # Tactical FPS
        if any(w in text for w in ["fps", "strike", "counter", "cs2", "csgo", "valorant", "siege", "overwatch", "shooter", "tactical"]):
            return GameProfile(
                title=clean_title,
                genre=GameGenre.FPS_TACTICAL,
                category="Tactical First-Person Shooter",
                gameplay_loop="Angle holding, economy pacing, utility placement, headshot tracking",
                coaching_focus=[
                    "Crosshair placement & corner pre-aiming",
                    "First-bullet accuracy & movement counter-strafing",
                    "Round pacing and economy management",
                    "Low latency and 1% low frame consistency"
                ],
                hud_schema={
                    "primary_metric": "Threat Vector",
                    "threat_tracking": True,
                    "vitals_monitoring": ["Health", "Shield", "Ammo", "Utility"],
                    "analysis_mode": "TACTICAL_COMBAT"
                },
                process_name=process_name,
                confidence=0.85,
                provenance="HEURISTIC"
            )

        # RPG / Action
        if any(w in text for w in ["rpg", "souls", "elden", "witcher", "cyberpunk", "fallout", "skyrim", "fantasy", "dragon", "quest"]):
            return GameProfile(
                title=clean_title,
                genre=GameGenre.ACTION_RPG,
                category="Immersive Action Role-Playing",
                gameplay_loop="Character builds, enemy attack telegraphs, resource allocation, boss mechanics",
                coaching_focus=[
                    "Boss attack telegraph timing & dodge windows",
                    "Stamina / Mana / Resource replenishment pacing",
                    "Stat scaling and weapon synergy recommendations",
                    "Frame pacing during dense visual particle effects"
                ],
                hud_schema={
                    "primary_metric": "Combat Readiness",
                    "threat_tracking": True,
                    "vitals_monitoring": ["HP", "Stamina", "Mana / RAM", "Consumables"],
                    "analysis_mode": "TACTICAL_COMBAT"
                },
                process_name=process_name,
                confidence=0.85,
                provenance="HEURISTIC"
            )

        # Strategy / RTS / MOBA
        if any(w in text for w in ["strategy", "rts", "moba", "starcraft", "warcraft", "dota", "league", "civilization", "age of", "chess"]):
            return GameProfile(
                title=clean_title,
                genre=GameGenre.STRATEGY_RTS,
                category="Real-Time / Turn-Based Strategy",
                gameplay_loop="Economy macro, unit micro, map control, strategic timing pushes",
                coaching_focus=[
                    "APM and multitasking efficiency",
                    "Resource income vs expenditure balance",
                    "Map vision and tactical positioning",
                    "Upgrade timing & counter-strategy execution"
                ],
                hud_schema={
                    "primary_metric": "Resource Float Rate",
                    "threat_tracking": False,
                    "vitals_monitoring": ["Economy Rate", "Supply / Population", "Map Control"],
                    "analysis_mode": "PROBLEM_SOLVING"
                },
                process_name=process_name,
                confidence=0.80,
                provenance="HEURISTIC"
            )

        # Default General Game Profile
        return GameProfile(
            title=clean_title,
            genre=GameGenre.GENERAL,
            category="Interactive Gaming Application",
            gameplay_loop="Real-time interaction, frame stability, responsiveness, player control",
            coaching_focus=[
                "Frame pacing and latency optimization",
                "Input response & stutter prevention",
                "Player decision consistency and session pacing"
            ],
            hud_schema={
                "primary_metric": "Frame Pacing Stability",
                "threat_tracking": False,
                "vitals_monitoring": ["FPS", "1% Low", "GPU Utilization"],
                "analysis_mode": "GENERAL_MONITORING"
            },
            process_name=process_name,
            confidence=0.60,
            provenance="HEURISTIC"
        )

    def _ai_classify(self, clean_title: str, process_name: Optional[str]) -> Optional[GameProfile]:
        """On-device AI zero-shot classification using Qwen/Genie."""
        if not self.ai_agent:
            return None

        system_prompt = (
            "You are CogniEdge Game Intelligence Classifier on Snapdragon Copilot+ PC. "
            "Analyze the given game title and process name. Classify into genre, category, "
            "gameplay loop, 4 coaching focus points, and HUD analysis mode (TACTICAL_COMBAT or PROBLEM_SOLVING). "
            "Respond ONLY with a JSON object: {"
            "\"title\": string, \"genre\": string, \"category\": string, \"gameplay_loop\": string, "
            "\"coaching_focus\": [string, string, string, string], "
            "\"analysis_mode\": \"TACTICAL_COMBAT\"|\"PROBLEM_SOLVING\""
            "}"
        )
        user_prompt = f"Game Title: '{clean_title}', Process Name: '{process_name or 'Unknown'}'"

        try:
            res = self.ai_agent.reason(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                max_tokens=300,
                json_mode=True,
                priority=1
            )
            data = res.structured_data
            if data and "genre" in data:
                analysis_mode = data.get("analysis_mode", "TACTICAL_COMBAT")
                return GameProfile(
                    title=data.get("title", clean_title),
                    genre=data.get("genre", GameGenre.GENERAL),
                    category=data.get("category", "Dynamic Game Application"),
                    gameplay_loop=data.get("gameplay_loop", "Interactive gameplay"),
                    coaching_focus=data.get("coaching_focus", ["Frame pacing", "Reflex tracking"]),
                    hud_schema={
                        "primary_metric": "Tactical State" if analysis_mode == "TACTICAL_COMBAT" else "Solve Pacing",
                        "threat_tracking": analysis_mode == "TACTICAL_COMBAT",
                        "vitals_monitoring": ["Health", "Shield"] if analysis_mode == "TACTICAL_COMBAT" else ["Solve Time", "Steps"],
                        "analysis_mode": analysis_mode
                    },
                    process_name=process_name,
                    confidence=0.92,
                    provenance="AI_NPU"
                )
        except Exception as e:
            print(f"[GameAnalyzer AI Classifier] Warning: {e}")
        return None

    def set_manual_override(self, game_title: str) -> GameProfile:
        """Allows user to manually set or test any game title."""
        with self._lock:
            profile = self.classify_game(game_title)
            profile.provenance = "MANUAL"
            self._manual_override_profile = profile
            self._last_detected_profile = profile
            return profile

    def clear_manual_override(self):
        with self._lock:
            self._manual_override_profile = None

    def detect_active_game(self) -> GameProfile:
        """
        Polls the active foreground application. If a valid game is focused, returns its profile.
        Otherwise falls back to manual override or the last detected game.
        """
        with self._lock:
            if self._manual_override_profile:
                return self._manual_override_profile

            title, proc_name, _ = self.get_foreground_window_info()

            # If no active window or system process, keep previous profile or return default
            if proc_name and proc_name.lower() in IGNORED_PROCESS_NAMES:
                if self._last_detected_profile:
                    return self._last_detected_profile
                # Default clean fallback
                return GameProfile(
                    title="System Desktop / Idle",
                    genre=GameGenre.GENERAL,
                    category="System Standby",
                    gameplay_loop="Waiting for game launch...",
                    coaching_focus=["Launch any game (PUBG, Free Fire, Portal, etc.) to begin auto-analysis."],
                    hud_schema={"primary_metric": "NPU Standby", "threat_tracking": False, "vitals_monitoring": [], "analysis_mode": "GENERAL_MONITORING"},
                    confidence=1.0,
                    provenance="STANDBY"
                )

            if title or proc_name:
                profile = self.classify_game(title or proc_name, proc_name)
                self._last_detected_profile = profile
                return profile

            if self._last_detected_profile:
                return self._last_detected_profile

            # Fallback
            return GameProfile(
                title="System Desktop / Idle",
                genre=GameGenre.GENERAL,
                category="System Standby",
                gameplay_loop="Waiting for game launch...",
                coaching_focus=["Launch any game (PUBG, Free Fire, Portal, etc.) to begin auto-analysis."],
                hud_schema={"primary_metric": "NPU Standby", "threat_tracking": False, "vitals_monitoring": [], "analysis_mode": "GENERAL_MONITORING"},
                confidence=1.0,
                provenance="STANDBY"
            )


# ─────────────────────────────────────────────────────────────
# Background Polling Worker
# ─────────────────────────────────────────────────────────────

class GameAnalyzerWorker:
    """
    Background worker that continuously monitors foreground games at 1-2 Hz,
    emitting events when a new game starts or window focus changes.
    """

    def __init__(self, analyzer: GameAnalyzer, poll_interval_s: float = 1.5, on_game_change=None):
        self.analyzer = analyzer
        self.poll_interval = poll_interval_s
        self.on_game_change = on_game_change
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._current_profile: Optional[GameProfile] = None

    @property
    def current_profile(self) -> GameProfile:
        return self._current_profile or self.analyzer.detect_active_game()

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    def _loop(self):
        while self._running:
            try:
                new_profile = self.analyzer.detect_active_game()
                if not self._current_profile or (new_profile.title != self._current_profile.title and new_profile.provenance != "STANDBY"):
                    old_title = self._current_profile.title if self._current_profile else None
                    self._current_profile = new_profile
                    if self.on_game_change and new_profile.provenance != "STANDBY":
                        try:
                            self.on_game_change(new_profile, old_title)
                        except Exception as e:
                            print(f"[GameAnalyzer Callback Error]: {e}")
                else:
                    self._current_profile = new_profile
            except Exception as e:
                print(f"[GameAnalyzer Worker Loop Error]: {e}")
            time.sleep(self.poll_interval)
