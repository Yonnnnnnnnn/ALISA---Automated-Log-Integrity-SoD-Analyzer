"""
Database Module for ALISA

Manages SQLite initialization and table creation for Audit Items and Integrity Baselines.

CFG Structure:
═══════════════════════════════════════════════════════════════════════════════
Start Symbol    : DatabaseModule (this file)

Non-Terminals   :
  ┌─ INTERNAL ────────────────────────────────────────────────────────────────┐
  │  <InitDB>      → Function to create tables                                │
  │  <DBConnection> → Context manager or connection getter                    │
  └───────────────────────────────────────────────────────────────────────────┘

  ┌─ EXTERNAL ────────────────────────────────────────────────────────────────┐
  │  <sqlite3>     ← from standard library (DB engine)                        │
  │  <Path>        ← from pathlib (Path management)                           │
  └───────────────────────────────────────────────────────────────────────────┘

Terminals       : str, bool, "alisa_audit.db"

Production Rules:
  DatabaseModule  → imports + <InitDB> + <DBConnection>
═══════════════════════════════════════════════════════════════════════════════
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

# Pattern: Singleton (Simplified for SQLite Connection management)
# Purpose: Ensures unified access to the audit database.

DB_PATH = Path(__file__).parent.parent.parent / "data" / "alisa_audit.db"


def init_db():
    """
    Initializes the SQLite database with required tables.
    Rule 6.5: Strict schema mapping based on Database_Schema.md.
    """
    os.makedirs(DB_PATH.parent, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # IntegrityBaseline Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS IntegrityBaseline (
                LogID INTEGER PRIMARY KEY AUTOINCREMENT,
                LogLine TEXT NOT NULL,
                HashSHA256 TEXT NOT NULL,
                Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # AuditItems Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS AuditItems (
                AuditID INTEGER PRIMARY KEY AUTOINCREMENT,
                LogID INTEGER,
                Timestamp TEXT,
                UserID TEXT,
                Action TEXT,
                Verdict TEXT, -- Violation | Clear
                NIST_Control TEXT, -- e.g., AC-5
                EvidenceArtifact JSON,
                FOREIGN KEY (LogID) REFERENCES IntegrityBaseline (LogID)
            )
        """
        )

        conn.commit()
    print(f"Database initialized at {DB_PATH}")


def save_log_baseline(raw_log: str, log_hash: str) -> int:
    """
    Saves a log entry and its hash to the IntegrityBaseline table.
    Returns the generated LogID.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO IntegrityBaseline (LogLine, HashSHA256) VALUES (?, ?)",
            (raw_log, log_hash),
        )
        conn.commit()
        return cursor.lastrowid


def save_audit_item(
    log_id: int,
    user_id: str,
    action: str,
    verdict: str,
    nist_control: str,
    evidence_json: dict,
):
    """
    Saves an audit finding to the AuditItems table.
    """
    import json

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO AuditItems 
            (LogID, Timestamp, UserID, Action, Verdict, NIST_Control, EvidenceArtifact)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                log_id,
                datetime.now().isoformat(),
                user_id,
                action,
                verdict,
                nist_control,
                json.dumps(evidence_json),
            ),
        )
        conn.commit()


if __name__ == "__main__":
    init_db()
