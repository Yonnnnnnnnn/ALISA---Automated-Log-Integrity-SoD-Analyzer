"""
Database Seeder for ALISA POC

Populates the database with historical dummy data to demonstrate
audit capabilities without waiting for real-time log ingestion.

Pattern: Simple implementation, no pattern needed
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Fix path to allow importing from parent directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.database import init_db, save_log_baseline, save_audit_item
from core.hasher import generate_sha256
from utils.mock_generator import (
    generate_normal_log,
    generate_sod_violation_sequence,
    generate_tampered_log_pair,
)


def run_seeder(count=50):
    print(f"--- ALISA Data Seeder Started ---")
    init_db()

    # 1. Normal Logs (Bulk)
    print(f"Seeding {count} normal logs...")
    for i in range(count):
        log = generate_normal_log()
        h = generate_sha256(log)
        log_id = save_log_baseline(log, h)

        # Randomly decide if it's a success or generic info
        save_audit_item(
            log_id=log_id,
            user_id=f"user_{random.randint(100, 999)}",
            action="SYSTEM_INFO" if i % 5 == 0 else "LOGIN_SUCCESS",
            verdict="Clear",
            nist_control="AC-6 (Least Privilege)",
            evidence_json={},
        )

    # 2. Historical SoD Violations
    print("Seeding historical SoD violations...")
    for _ in range(3):
        logs = generate_sod_violation_sequence()
        for log in logs:
            h = generate_sha256(log)
            log_id = save_log_baseline(log, h)

            # Simple manual parse for seeding
            user = log.split("User ")[1].split(" executed")[0]
            action = log.split("action: ")[1].split(" ")[0]

            verdict = "Clear"
            if "Approve" in action:
                verdict = "Violation"

            save_audit_item(
                log_id=log_id,
                user_id=user,
                action=action,
                verdict=verdict,
                nist_control="AC-5 (Separation of Duties)",
                evidence_json=(
                    {"note": "Historical SoD record"} if verdict == "Violation" else {}
                ),
            )

    print(f"--- Seeding Completed Successfully! ---")
    print(f"You can now refresh your SQLite Viewer to see the data.")


if __name__ == "__main__":
    run_seeder()
