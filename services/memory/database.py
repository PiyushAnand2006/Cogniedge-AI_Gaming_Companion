"""
CogniEdge SQLite Persistent Database Engine
Stores player patterns, cross-session coaching history, advice effectiveness,
and game performance profiles locally with privacy-first retention policies.
"""

import os
import sqlite3
from typing import Optional


DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../cogniedge.db")
)


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_database(db_path: Optional[str] = None):
    conn = get_db_connection(db_path)
    cur = conn.cursor()

    # 1. Sessions Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        game_title TEXT NOT NULL,
        start_time REAL NOT NULL,
        end_time REAL,
        duration_s REAL DEFAULT 0,
        avg_fps REAL DEFAULT 0,
        one_pct_low REAL DEFAULT 0,
        stutter_count INTEGER DEFAULT 0,
        kills INTEGER DEFAULT 0,
        deaths INTEGER DEFAULT 0,
        coach_rating TEXT DEFAULT 'A',
        summary TEXT,
        status TEXT DEFAULT 'ACTIVE'
    )
    """)

    # 2. Player Recurring Patterns Table (Master spec schema)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS coaching_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern_type TEXT NOT NULL,
        description TEXT NOT NULL,
        occurrence_count INTEGER DEFAULT 1,
        first_seen TIMESTAMP NOT NULL,
        last_seen TIMESTAMP NOT NULL,
        confidence REAL NOT NULL,
        game_context TEXT
    )
    """)

    # 3. Player Recurring Patterns Table (Compatible schema)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS player_patterns (
        id TEXT PRIMARY KEY,
        game_title TEXT NOT NULL,
        pattern_name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        occurrences INTEGER DEFAULT 1,
        successful_corrections INTEGER DEFAULT 0,
        current_confidence REAL DEFAULT 0.5,
        first_observed REAL NOT NULL,
        last_observed REAL NOT NULL
    )
    """)

    # 4. Optimization History Table (Master spec schema)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS optimization_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        optimization TEXT NOT NULL,
        applied_at TIMESTAMP NOT NULL,
        before_metrics TEXT NOT NULL,
        after_metrics TEXT NOT NULL,
        verdict TEXT NOT NULL
    )
    """)

    # 5. AI Recommendations & Advice Effectiveness Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        id TEXT PRIMARY KEY,
        session_id TEXT,
        advice_text TEXT NOT NULL,
        category TEXT NOT NULL,
        suggested_count INTEGER DEFAULT 1,
        followed_count INTEGER DEFAULT 0,
        success_outcomes INTEGER DEFAULT 0,
        success_rate_pct REAL DEFAULT 0.0,
        last_suggested REAL NOT NULL,
        FOREIGN KEY(session_id) REFERENCES sessions(id)
    )
    """)

    # 6. Session Timeline Events Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS session_events (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        timestamp REAL NOT NULL,
        event_type TEXT NOT NULL,
        description TEXT NOT NULL,
        metadata_json TEXT,
        FOREIGN KEY(session_id) REFERENCES sessions(id)
    )
    """)

    # 7. Optimization Experiments Table (A/B Benchmarks)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS optimization_experiments (
        id TEXT PRIMARY KEY,
        timestamp REAL NOT NULL,
        action_name TEXT NOT NULL,
        baseline_fps REAL NOT NULL,
        baseline_one_pct_low REAL NOT NULL,
        baseline_p95_ms REAL NOT NULL,
        optimized_fps REAL NOT NULL,
        optimized_one_pct_low REAL NOT NULL,
        optimized_p95_ms REAL NOT NULL,
        summary_verdict TEXT NOT NULL
    )
    """)

    # 8. Voice Notes & PTT Queries Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS voice_notes (
        id TEXT PRIMARY KEY,
        session_id TEXT,
        timestamp REAL NOT NULL,
        transcript TEXT NOT NULL,
        ai_response TEXT NOT NULL,
        latency_ms REAL DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


init_database()
