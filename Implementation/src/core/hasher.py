"""
Hasher Module for ALISA

Provides SHA-256 integrity verification for log lines.

CFG Structure:
═══════════════════════════════════════════════════════════════════════════════
Start Symbol    : HasherModule (this file)

Non-Terminals   :
  ┌─ INTERNAL ────────────────────────────────────────────────────────────────┐
  │  <GenerateHash> → Function to compute SHA-256 string                      │
  │  <VerifyHash>   → Function to compare current vs baseline                  │
  └───────────────────────────────────────────────────────────────────────────┘

  ┌─ EXTERNAL ────────────────────────────────────────────────────────────────┐
  │  <hashlib>      ← from standard library (Crypto)                          │
  └───────────────────────────────────────────────────────────────────────────┘

Terminals       : str, bytes, bool

Production Rules:
  HasherModule    → imports + <GenerateHash> + <VerifyHash>
═══════════════════════════════════════════════════════════════════════════════
"""

import hashlib

# Pattern: Simple implementation, no pattern needed

def generate_sha256(content: str) -> str:
    """
    Generates a SHA-256 hash for a given string.
    Rule: deterministic hashing for integrity baseline.
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def verify_integrity(content: str, baseline_hash: str) -> bool:
    """
    Verifies if the current content matches the baseline hash.
    """
    current_hash = generate_sha256(content)
    return current_hash == baseline_hash
