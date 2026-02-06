"""
Mock Log Generator for ALISA

Generates synthetic Linux auth logs with controlled anomalies for testing.
Includes scenarios for Normal checks, Tampering, and SoD violations.

CFG Structure:
═══════════════════════════════════════════════════════════════════════════════
Start Symbol    : MockGenerator (this file)

Non-Terminals   :
  ┌─ INTERNAL ────────────────────────────────────────────────────────────────┐
  │  <GenNormal>   → Generates standard SSH auth logs                         │
  │  <GenSoD>      → Generates conflict sequence (Create + Approve)           │
  │  <GenTamper>   → Generates logs that will be modified post-hashing        │
  └───────────────────────────────────────────────────────────────────────────┘

  ┌─ EXTERNAL ────────────────────────────────────────────────────────────────┐
  │  <random>      ← Standard lib                                             │
  │  <datetime>    ← Standard lib                                             │
  └───────────────────────────────────────────────────────────────────────────┘

Terminals       : str, list, int

Production Rules:
  MockGenerator   → imports + <GenNormal> + <GenSoD> + <GenTamper>
═══════════════════════════════════════════════════════════════════════════════
"""

import random
from datetime import datetime, timedelta

# Pattern: Factory (of logs)
# Purpose: Dynamic generation of test data based on requested scenario.

USERS = ["root", "admin", "process_owner", "u_finance_01", "u_audit_01"]
ACTIONS = ["password check", "authentication failure", "accepted password"]


def get_timestamp():
    """Returns current timestamp in Linux log format."""
    return datetime.now().strftime("%b %d %H:%M:%S")


def generate_normal_log() -> str:
    """
    Generates a generic Linux authentication log.
    Example: Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; user=root
    """
    timestamp = get_timestamp()
    user = random.choice(USERS)
    pid = random.randint(1000, 20000)
    msg = random.choice(ACTIONS)

    return f"{timestamp} combo sshd(pam_unix)[{pid}]: {msg}; user={user}"


def generate_sod_violation_sequence() -> list[str]:
    """
    Generates a sequence of logs simulating a Segregation of Duties violation.
    Scenario: Same user creates an invoice and then approves the payment.
    """
    timestamp_1 = datetime.now()
    timestamp_2 = timestamp_1 + timedelta(seconds=45)
    user = "u_finance_01"  # The violator
    pid = random.randint(3000, 4000)

    t1_str = timestamp_1.strftime("%b %d %H:%M:%S")
    t2_str = timestamp_2.strftime("%b %d %H:%M:%S")

    # Log 1: Create Invoice
    log1 = f"{t1_str} finance_app system[1]: User {user} executed action: Create_Invoice ID=INV-2024-001"

    # Log 2: Approve Payment (Violation!)
    log2 = f"{t2_str} finance_app system[1]: User {user} executed action: Approve_Payment ID=INV-2024-001"

    return [log1, log2]


def generate_tampered_log_pair() -> tuple[str, str]:
    """
    Returns the SAME log twice, meant to be modified externally between calls
    to demonstrate hash mismatch.
    """
    original = generate_normal_log()
    tampered = original.replace("authentication failure", "accepted password")
    return original, tampered
