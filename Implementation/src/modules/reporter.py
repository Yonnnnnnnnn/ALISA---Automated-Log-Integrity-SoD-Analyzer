"""
Reporter Module for ALISA

Generates audit-ready evidence artifacts in JSON format.
Inspiration: AuditBuddy/AutoPilot-Audit evidence schemas.

CFG Structure:
═══════════════════════════════════════════════════════════════════════════════
Start Symbol    : ReporterModule (this file)

Non-Terminals   :
  ┌─ INTERNAL ────────────────────────────────────────────────────────────────┐
  │  <GenerateArtifact> → Creates the JSON evidence object                    │
  │  <SaveArtifact>     → Writes to disk (or DB)                              │
  └───────────────────────────────────────────────────────────────────────────┘

  ┌─ EXTERNAL ────────────────────────────────────────────────────────────────┐
  │  <uuid>        ← Standard lib                                             │
  │  <datetime>    ← Standard lib                                             │
  │  <json>        ← Standard lib                                             │
  └───────────────────────────────────────────────────────────────────────────┘

Terminals       : dict, str, "Violations"

Production Rules:
  ReporterModule  → imports + <GenerateArtifact> + <SaveArtifact>
═══════════════════════════════════════════════════════════════════════════════
"""

import uuid
import json
import os
from datetime import datetime

# Pattern: Builder
# Purpose: Constructs a complex audit evidence object step-by-step.

ARTIFACTS_DIR = "data/artifacts"


def generate_evidence_artifact(
    log_line: str,
    structured_data: dict,
    integrity_status: bool,
    violation_msg: str = None,
) -> dict:
    """
    Constructs a JSON Evidence Artifact compliant with the project design.
    """

    artifact = {
        "EvidenceID": str(uuid.uuid4()),
        "Timestamp": datetime.now().isoformat(),
        "NIST_Control": "AC-5 (Separation of Duties)",
        "Status": "VIOLATION" if violation_msg else "COMPLIANT",
        "SourceLog": {"Raw": log_line, "IntegrityVerified": integrity_status},
        "Details": structured_data,
    }

    if violation_msg:
        artifact["ViolationReason"] = violation_msg

    return artifact


def save_artifact(artifact: dict):
    """
    Saves the evidence artifact to the local file system (simulating storage).
    """
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    filename = f"{ARTIFACTS_DIR}/{artifact['EvidenceID']}.json"

    with open(filename, "w") as f:
        json.dump(artifact, f, indent=2)

    print(f"Evidence Artifact saved: {filename}")
