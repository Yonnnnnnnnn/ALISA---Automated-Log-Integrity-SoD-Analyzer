"""
Main Entry Point for ALISA

Orchestrates the log ingestion, integrity validation, and semantic parsing flow.

CFG Structure:
═══════════════════════════════════════════════════════════════════════════════
Start Symbol    : AlisaMain (this file)

Non-Terminals   :
  ┌─ INTERNAL ────────────────────────────────────────────────────────────────┐
  │  <ProcessLog>  → Main pipeline for a single log line                      │
  └───────────────────────────────────────────────────────────────────────────┘

  ┌─ EXTERNAL ────────────────────────────────────────────────────────────────┐
  │  <database>    ← from core (DB persistence)                               │
  │  <hasher>      ← from core (Integrity)                                    │
  │  <parser>      ← from modules (SLM Parser)                                │
  │  <reporter>    ← from modules (Evidence Generation)                       │
  └───────────────────────────────────────────────────────────────────────────┘

Terminals       : str, "mock_logs.txt"

Production Rules:
  AlisaMain       → imports + <ProcessLog> + main_loop
═══════════════════════════════════════════════════════════════════════════════
"""

from core.database import init_db, save_log_baseline, save_audit_item
from core.hasher import generate_sha256, verify_integrity
from modules.parser import parse_log_with_phi3
from modules.rule_engine import engine as rule_engine
from modules.reporter import generate_evidence_artifact, save_artifact

# Pattern: Facade
# Purpose: Simplifies the complex multi-stage audit process into a single entry point.


def run_pipeline(raw_log: str, expected_hash: str = None) -> bool:
    """
    Executes the full Pipeline: Ingest -> Hash -> Parse -> Persistence -> Rules -> Report.
    Returns True if log is compliant/safe, False if generic error or tampering (for simulation control).
    """
    print(f"Processing: {raw_log[:50]}...")

    # 1. Integrity Baseline (Simplified for POC: always hash)
    # If expected_hash is provided (Tamper Check), we verify against it.
    current_hash = generate_sha256(raw_log)
    integrity_status = True

    if expected_hash:
        integrity_status = verify_integrity(raw_log, expected_hash)
        if not integrity_status:
            print(
                f">>> CRITICAL: Integrity Check Failed! Expected {expected_hash}, Got {current_hash}"
            )
            # Generate special "Tampering" artifact
            artifact = generate_evidence_artifact(
                raw_log,
                {"Event": "Tampering Detected"},
                integrity_status=False,
                violation_msg="Hash Mismatch - Potential Log Tampering",
            )
            save_artifact(artifact)
            print("-" * 20)
            return False

    # 2. Semantic Parsing
    structured_data = parse_log_with_phi3(raw_log)

    # 2b. Fallback parsing for POC
    if not structured_data or "action" not in structured_data:
        if "executed action:" in raw_log:
            try:
                parts = raw_log.split("User ")[1].split(" executed action: ")
                structured_data = {"user": parts[0], "action": parts[1].split(" ")[0]}
            except IndexError:
                structured_data = {}

    # 3. Rule Engine Analysis
    violations = rule_engine.analyze_log(structured_data)

    # 3b. Persistence (Save Baseline)
    log_id = save_log_baseline(raw_log, current_hash)

    # 4. Output (Reporting & Persistence)
    print("Structured Output:", structured_data)
    print("Hash:", current_hash)

    if violations:
        for v in violations:
            print(f">>> CRITICAL AUDIT FINDING: {v}")
            # Generate Evidence Artifact
            artifact = generate_evidence_artifact(
                raw_log, structured_data, integrity_status, violation_msg=v
            )
            save_artifact(artifact)

            # Save to Database
            save_audit_item(
                log_id=log_id,
                user_id=structured_data.get("user", "unknown"),
                action=structured_data.get("action", "unknown"),
                verdict="Violation",
                nist_control="AC-5",
                evidence_json=artifact,
            )
    else:
        # Save compliant item to DB
        save_audit_item(
            log_id=log_id,
            user_id=structured_data.get("user", "unknown"),
            action=structured_data.get("action", "unknown"),
            verdict="Clear",
            nist_control="AC-5",
            evidence_json={},
        )

    print("-" * 20)
    return True


if __name__ == "__main__":
    # Initialize DB
    init_db()

    # Mock data for POC test (Dynamic Generation)
    from utils.mock_generator import (
        generate_normal_log,
        generate_sod_violation_sequence,
        generate_tampered_log_pair,
    )

    print("\n--- Phase 1: Real-Time Log Sealing ---")
    for _ in range(3):
        run_pipeline(generate_normal_log())

    print("\n--- Phase 2: SoD Violation Detection ---")
    sod_logs = generate_sod_violation_sequence()
    for log in sod_logs:
        run_pipeline(log)

    print("\n--- Phase 3: Tampering Detection ---")
    original_log, tampered_log = generate_tampered_log_pair()

    # 1. Establish Baseline
    baseline_hash = generate_sha256(original_log)
    print(f"Original Log: {original_log[:50]}...")
    print(f"Baseline Hash: {baseline_hash}")

    # 2. Simulate Attack (Verify tampered log against baseline)
    # run_pipeline will now handle the check if we pass expected_hash
    run_pipeline(tampered_log, expected_hash=baseline_hash)
