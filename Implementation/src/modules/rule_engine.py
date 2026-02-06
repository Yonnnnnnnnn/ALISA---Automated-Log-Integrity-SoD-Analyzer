"""
Rule Engine Module for ALISA

Implements logic for detecting Segregation of Duties (SoD) violations and other audit rules.
Uses a sliding window approach for stateful analysis of user actions.

CFG Structure:
═══════════════════════════════════════════════════════════════════════════════
Start Symbol    : RuleEngineModule (this file)

Non-Terminals   :
  ┌─ INTERNAL ────────────────────────────────────────────────────────────────┐
  │  <SoDCheck>    → Logic to detect conflict pairs (e.g. Create + Approve)   │
  │  <ConfigLoader>→ Loads YAML rules                                         │
  └───────────────────────────────────────────────────────────────────────────┘

  ┌─ EXTERNAL ────────────────────────────────────────────────────────────────┐
  │  <yaml>        ← from library (Config parsing)                            │
  │  <Path>        ← from pathlib                                             │
  └───────────────────────────────────────────────────────────────────────────┘

Terminals       : dict, list, str

Production Rules:
  RuleEngineModule→ imports + <ConfigLoader> + <SoDCheck>
═══════════════════════════════════════════════════════════════════════════════
"""

import yaml
from pathlib import Path
from typing import List, Dict, Set

# Pattern: Strategy
# Purpose: Decouples the rule logic (SoD, Access Control) from the execution engine.

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "config.yaml"


class RuleEngine:
    def __init__(self):
        self.rules = self._load_rules()
        # State tracking: user_id -> set of actions performed
        self.user_state: Dict[str, Set[str]] = {}

    def _load_rules(self) -> dict:
        """Loads NIST rules from YAML configuration."""
        try:
            with open(CONFIG_PATH, "r") as f:
                config = yaml.safe_load(f)
            return config.get("rules", {})
        except Exception as e:
            print(f"Error loading rules: {e}")
            return {}

    def analyze_log(self, structured_log: dict) -> List[str]:
        """
        Analyzes a structured log against active rules.
        Returns a list of violation messages.
        """
        violations = []

        # Safe extraction of fields (handling potentially incomplete logs)
        user = structured_log.get("user")
        action = structured_log.get("action")

        if not user or not action:
            return []  # Skip logs without clear user/action context

        # Update User State
        if user not in self.user_state:
            self.user_state[user] = set()
        self.user_state[user].add(action)

        # Check SoD Rules (NIST AC-5)
        # Logic: V(u) = exists (a, b) in Actions(u) such that (a, b) in Conflict_Matrix
        sod_rule = self.rules.get("nist_ac2_sod")
        if sod_rule:
            conflict_pairs = sod_rule.get("conflict_actions", [])
            for conflict in conflict_pairs:
                action_a, action_b = conflict

                # Check if user has done BOTH actions
                has_a = action_a in self.user_state[user]
                has_b = action_b in self.user_state[user]

                if has_a and has_b:
                    violation_msg = (
                        f"SoD VIOLATION DETECTED ({sod_rule['id']}): "
                        f"User '{user}' performed conflicting actions: {action_a} + {action_b}"
                    )
                    violations.append(violation_msg)

        return violations


# Shared Singleton
engine = RuleEngine()
