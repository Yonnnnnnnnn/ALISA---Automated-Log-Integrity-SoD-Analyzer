# 🚀 Step-by-Step Guide: How to Use ALISA

Welcome! This guide will help you set up and run the **ALISA (Automated Log Integrity & SoD Analyzer)** system on your computer.

---

## Part 1: Setting Up the System

### Step 1: "Unpacking" the Project

1. Locate the **ZIP file** you downloaded from GitHub.
2. **Right-click** the file and select **"Extract All..."**.
3. Open the folder you just extracted. You should see files like `README.md`, `requirements.txt`, and a folder named `Implementation`.

### Step 2: Preparing the AI (Ollama)

1. Make sure the **Ollama** app is open and running on your computer.
2. Open your computer's **Terminal** (or Command Prompt).
3. Type the following command and press Enter:
   ```bash
   ollama run phi3
   ```
   _Note: If it's your first time, it will download the "brain" for the system. Once you see a chat prompt, you can close the window; the AI will stay ready in the background._

### Step 3: Installing the "Helper Tools"

1. In your Terminal, make sure you are inside the folder you extracted in Step 1.
2. Type this command to install the necessary libraries:
   ```bash
   pip install -r requirements.txt
   ```

---

## Part 2: Running the Audit Demo

Now, let's see ALISA in action! Type this command in your terminal:

```bash
python Implementation/src/main.py
```

---

## Part 3: What Just Happened? (Plain-English Analysis)

When you run the script, ALISA goes through three "Phases" of testing. Here is what the computer is actually doing in each phase:

### 🟢 Phase 1: Normal Bookkeeping

- **What it does**: ALISA reads standard logs (like someone logging in successfully).
- **The Result**: The system simply records these events. It creates a "Digital Fingerprint" (Hash) for each log.
- **Plain English**: "Everything looks normal. I've recorded who logged in and made sure the record is sealed so it can't be changed later."

### 🔴 Phase 2: Detecting "Sneaky" Behavior (SoD Violation)

- **What it does**: ALISA watches a specific user (`u_finance_01`) perform two actions: _Creating an Invoice_ and then _Approving a Payment_.
- **The Result**: The system triggers a **CRITICAL ALERT**.
- **Plain English**: "Hold on! The person who created the bill shouldn't be the one approving the payment. This is a conflict of interest, and I've flagged it for the auditors."

### 🛡️ Phase 3: Catching a "Log Hacker" (Tampering Simulation)

- **What it does**: The system creates a log entry, seals it with a fingerprint, and then **simulates a hacker** trying to change the words (e.g., changing "Failed" to "Success").
- **The Result**: ALISA compares the information against its original "Digital Fingerprint."
- **Plain English**: "Someone tried to sneakily change the records! The fingerprint doesn't match the original. I've flagged this record as tampered with and untrustworthy."

---

## How to Verify the Results?

1.  **Look in the Folder**: Go to `Implementation/data/artifacts/`. You will see JSON files. These are the "Digital Evidence" folders that an auditor would use in court.
2.  **Look at the Ledger**: Open `Implementation/data/alisa_audit.db` using a database viewer. This is the "Main Ledger" where every single event is permanently stored and sealed.

**Congratulations! You've just performed an automated intelligent audit.**
