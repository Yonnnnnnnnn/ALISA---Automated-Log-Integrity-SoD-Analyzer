# ALISA: Automated Log Integrity & SoD Analyzer

ALISA is a Proof-of-Concept (POC) system designed to transform raw system logs into deterministic, audit-ready evidence artifacts. It combines a Small Language Model (Phi-3) for semantic parsing with a deterministic Rule Engine for compliance checks.

## Key Features

1.  **Integrity Baseline**: SHA-256 hashing of every log line to detect tampering.
2.  **Semantic Parsing**: Uses `Ollama` + `Phi-3` to extract structured data (User, Action, Timestamp).
3.  **SoD Detection**: Identifies Segregation of Duties violations (e.g., _Create Invoice_ + _Approve Payment_) based on NIST AC-5.
4.  **Audit Artifacts**: Generates JSON evidence files for every detected violation coverage.

## Installation

### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.com/) installed and running (`ollama serve`).

### Installation Setup

It is recommended to run all commands from the **project root directory** (where this `README.md`, `.gitignore`, and the `Implementation/` folder are located).

1.  **Get the repository**:
    - **Option 1: Using Git (Recommended)**:
      ```bash
      git clone https://github.com/Yonnnnnnnnn/ALISA---Automated-Log-Integrity-SoD-Analyzer.git
      cd ALISA---Automated-Log-Integrity-SoD-Analyzer
      ```
    - **Option 2: Direct Download**: Download the repository as a **ZIP file** from GitHub and extract it to your desired folder.

2.  **Install dependencies**:

    ```bash
    # Option A: Automated installation (Highly Recommended)
    pip install -r requirements.txt

    # Option B: Manual installation
    pip install requests pydantic pyyaml python-dotenv
    ```

### Dependency Breakdown

| Library         | Purpose in ALISA                                                             |
| :-------------- | :--------------------------------------------------------------------------- |
| `requests`      | Facilitates communication with the **Ollama API** (SLM Inference Engine).    |
| `pydantic`      | Enforces **Data Contracts** to ensure AI-parsed logs follow a strict schema. |
| `pyyaml`        | Enables **Policy Externalization** (NIST compliance rules in `config.yaml`). |
| `python-dotenv` | Manages environment variables and system configurations securely.            |
| `pytest`        | Used for automated logic verification across the pipeline modules.           |

3.  Pull the SLM model:
    ```bash
    ollama run phi3
    ```

## Usage

Navigate to the implementation directory and run the main pipeline script. This will execute the **Mock Simulation** covering Normal flow, SoD Violations, and Tampering checks.

```bash
cd "Implementation"
python src/main.py
```

## Audit Implementation Phases

The `main.py` script executes three distinct audit capabilities:

1.  **Phase 1: Real-Time Log Sealing**
    - Processes standard authentication logs.
    - Demonstrates instant integrity hashing.

2.  **Phase 2: SoD Violation Detection**
    - Detects a user (`u_finance_01`) creating an invoice and then approving a payment.
    - **Expected Result**: A "CRITICAL AUDIT FINDING" alert and a JSON evidence artifact.

3.  **Phase 3: Tampering Detection**
    - Demonstrates detection of record modification by comparing current vs. baseline hashes.
    - **Expected Result**: An "INTEGRITY VIOLATION DETECTED" alert and forensic artifact.

## Project Structure

```
Implementation/
├── config/
│   └── config.yaml          # NIST Rules and SLM settings
├── data/
│   ├── alisa_audit.db       # SQLite Database
│   └── artifacts/           # JSON Evidence Output
├── src/
│   ├── core/
│   │   ├── database.py      # Persistence Layer
│   │   └── hasher.py        # SHA-256 Integrity
│   ├── modules/
│   │   ├── parser.py        # Ollama/Phi-3 Client
│   │   ├── reporter.py      # Artifact Generator
│   │   └── rule_engine.py   # SoD Logic
│   ├── utils/
│   │   └── mock_generator.py # Synthetic Data Factory
│   └── main.py              # Orchestration Entry Point
└── requirements.txt
```
