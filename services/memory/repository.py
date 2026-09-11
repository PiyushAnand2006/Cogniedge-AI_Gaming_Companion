"""
CogniEdge SQLite Repository
Data access layer for sessions, player patterns, recommendations, and timeline events.
"""

import time
import json
import uuid
from typing import List, Dict, Any, Optional
from database import get_db_connection


class MemoryRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def _get_conn(self):
        return get_db_connection(self.db_path)

    # ── Sessions ──────────────────────────────────────────────────
    def create_session(self, game_title: str = "Cyberpunk 2077") -> str:
        session_id = f"sess_{str(uuid.uuid4())[:8]}"
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sessions (id, game_title, start_time, status)
            VALUES (?, ?, ?, 'ACTIVE')
        """, (session_id, game_title, time.time()))
        conn.commit()
        conn.close()
        return session_id

    def end_session(self, session_id: str, summary_data: Dict[str, Any]):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("""
            UPDATE sessions
            SET end_time = ?, duration_s = ?, avg_fps = ?, one_pct_low = ?,
                stutter_count = ?, kills = ?, deaths = ?, coach_rating = ?,
                summary = ?, status = 'COMPLETED'
            WHERE id = ?
        """, (
            time.time(),
            summary_data.get("duration_s", 0),
            summary_data.get("avg_fps", 0),
            summary_data.get("one_pct_low", 0),
            summary_data.get("stutter_count", 0),
            summary_data.get("kills", 0),
            summary_data.get("deaths", 0),
            summary_data.get("coach_rating", "A"),
            summary_data.get("summary", ""),
            session_id
        ))
        conn.commit()
        conn.close()

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM sessions ORDER BY start_time DESC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    # ── Coaching Patterns (Feature 3 Spec) ─────────────────────────
    def get_top_coaching_patterns(self, limit: int = 5, game_context: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        cur = conn.cursor()
        if game_context:
            cur.execute("""
                SELECT * FROM coaching_patterns
                WHERE game_context = ? OR game_context IS NULL
                ORDER BY confidence DESC, last_seen DESC
                LIMIT ?
            """, (game_context, limit))
        else:
            cur.execute("""
                SELECT * FROM coaching_patterns
                ORDER BY confidence DESC, last_seen DESC
                LIMIT ?
            """, (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def upsert_coaching_pattern(
        self,
        pattern_type: str,
        description: str,
        confidence: float = 0.8,
        game_context: Optional[str] = None
    ):
        conn = self._get_conn()
        cur = conn.cursor()
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("""
            SELECT id, occurrence_count, confidence FROM coaching_patterns
            WHERE pattern_type = ? AND (description LIKE ? OR ? LIKE description)
        """, (pattern_type, f"%{description[:30]}%", description))
        row = cur.fetchone()

        if row:
            new_count = row["occurrence_count"] + 1
            new_conf = min(1.0, row["confidence"] + 0.05)
            cur.execute("""
                UPDATE coaching_patterns
                SET occurrence_count = ?, last_seen = ?, confidence = ?, description = ?
                WHERE id = ?
            """, (new_count, now, new_conf, description, row["id"]))
        else:
            cur.execute("""
                INSERT INTO coaching_patterns (pattern_type, description, occurrence_count, first_seen, last_seen, confidence, game_context)
                VALUES (?, ?, 1, ?, ?, ?, ?)
            """, (pattern_type, description, now, now, confidence, game_context))

        conn.commit()
        conn.close()

    # ── Player Patterns (Compatible Schema) ────────────────────────
    def get_player_patterns(self, game_title: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        cur = conn.cursor()
        if game_title:
            cur.execute("SELECT * FROM player_patterns WHERE game_title = ? ORDER BY occurrences DESC", (game_title,))
        else:
            cur.execute("SELECT * FROM player_patterns ORDER BY occurrences DESC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def upsert_player_pattern(
        self,
        game_title: str,
        pattern_name: str,
        category: str,
        description: str,
        corrected: bool = False
    ):
        conn = self._get_conn()
        cur = conn.cursor()
        now = time.time()
        cur.execute("""
            SELECT id, occurrences, successful_corrections FROM player_patterns
            WHERE game_title = ? AND pattern_name = ?
        """, (game_title, pattern_name))
        row = cur.fetchone()

        if row:
            occ = row["occurrences"] + 1
            corr = row["successful_corrections"] + (1 if corrected else 0)
            conf = min(0.5 + (occ * 0.05), 0.98)
            cur.execute("""
                UPDATE player_patterns
                SET occurrences = ?, successful_corrections = ?, current_confidence = ?, last_observed = ?
                WHERE id = ?
            """, (occ, corr, conf, now, row["id"]))
        else:
            cur.execute("""
                INSERT INTO player_patterns (
                    id, game_title, pattern_name, category, description,
                    occurrences, successful_corrections, current_confidence,
                    first_observed, last_observed
                ) VALUES (?, ?, ?, ?, ?, 1, 0, 0.65, ?, ?)
            """, (str(uuid.uuid4())[:8], game_title, pattern_name, category, description, now, now))

        conn.commit()
        conn.close()

    # ── Optimization History (Feature 6 Spec) ──────────────────────
    def record_optimization_history(
        self,
        optimization: str,
        before_metrics: Dict[str, Any],
        after_metrics: Dict[str, Any],
        verdict: str
    ):
        conn = self._get_conn()
        cur = conn.cursor()
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT INTO optimization_history (optimization, applied_at, before_metrics, after_metrics, verdict)
            VALUES (?, ?, ?, ?, ?)
        """, (
            optimization,
            now,
            json.dumps(before_metrics),
            json.dumps(after_metrics),
            verdict
        ))
        conn.commit()
        conn.close()

    def get_optimization_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM optimization_history ORDER BY id DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    # ── Recommendations & Advice ──────────────────────────────────
    def record_advice_feedback(
        self,
        advice_text: str,
        category: str,
        followed: bool,
        success: bool,
        session_id: Optional[str] = None
    ):
        conn = self._get_conn()
        cur = conn.cursor()
        now = time.time()
        cur.execute("SELECT id, suggested_count, followed_count, success_outcomes FROM recommendations WHERE advice_text = ?", (advice_text,))
        row = cur.fetchone()

        if row:
            s_count = row["suggested_count"] + 1
            f_count = row["followed_count"] + (1 if followed else 0)
            o_count = row["success_outcomes"] + (1 if (followed and success) else 0)
            rate = (o_count / f_count * 100.0) if f_count > 0 else 0.0

            cur.execute("""
                UPDATE recommendations
                SET suggested_count = ?, followed_count = ?, success_outcomes = ?, success_rate_pct = ?, last_suggested = ?
                WHERE id = ?
            """, (s_count, f_count, o_count, rate, now, row["id"]))
        else:
            f_count = 1 if followed else 0
            o_count = 1 if (followed and success) else 0
            rate = 100.0 if o_count > 0 else 0.0
            cur.execute("""
                INSERT INTO recommendations (
                    id, session_id, advice_text, category, suggested_count,
                    followed_count, success_outcomes, success_rate_pct, last_suggested
                ) VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?)
            """, (str(uuid.uuid4())[:8], session_id, advice_text, category, f_count, o_count, rate, now))

        conn.commit()
        conn.close()

    def get_all_recommendations(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM recommendations ORDER BY last_suggested DESC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def get_recommendations(self) -> List[Dict[str, Any]]:
        return self.get_all_recommendations()
