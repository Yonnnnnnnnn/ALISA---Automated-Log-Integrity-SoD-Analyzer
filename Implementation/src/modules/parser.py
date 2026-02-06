"""
SLM Parser Module for ALISA

Integrates with Ollama (Phi-3) to transform unstructured logs into structured JSON.

CFG Structure:
═══════════════════════════════════════════════════════════════════════════════
Start Symbol    : ParserModule (this file)

Non-Terminals   :
  ┌─ INTERNAL ────────────────────────────────────────────────────────────────┐
  │  <Phi3Parse>   → Function to call Ollama API                              │
  │  <PromptGen>   → Function to generate system/user prompts                 │
  └───────────────────────────────────────────────────────────────────────────┘

  ┌─ EXTERNAL ────────────────────────────────────────────────────────────────┐
  │  <requests>    ← from library (API calls)                                 │
  │  <json>        ← from standard library (Data parsing)                     │
  └───────────────────────────────────────────────────────────────────────────┘

Terminals       : str, dict, "http://localhost:11434/api/generate"

Production Rules:
  ParserModule    → imports + <Phi3Parse> + <PromptGen>
═══════════════════════════════════════════════════════════════════════════════
"""

import requests
import json

# Pattern: Proxy
# Purpose: Acts as a gateway to the local Ollama SLM instance.

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"


def generate_prompt(log_line: str) -> str:
    """
    Constructs a prompt for log structuring per LogHub schema.
    Rule: Strict JSON output requirement.
    """
    return f"""
    Parse following log line into JSON: "{log_line}"
    JSON Schema:
    {{
      "Month": string,
      "Date": number,
      "Time": string,
      "Level": string,
      "Component": string,
      "PID": number,
      "Content": string
    }}
    Output ONLY THE JSON.
    """


def parse_log_with_phi3(log_line: str) -> dict:
    """
    Sends log line to Ollama and returns structured JSON.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": generate_prompt(log_line),
        "stream": False,
        "format": "json",
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        return json.loads(response.json().get("response", "{}"))
    except Exception as e:
        print(f"Error parsing log with Phi-3: {e}")
        return {}


if __name__ == "__main__":
    # Test with a mock LogHub Linux line
    test_line = "Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEV host=  user=root"
    print(parse_log_with_phi3(test_line))
