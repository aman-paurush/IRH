# Intelligent Ransomware Honeypot Viva Manual

## 1) Library-wise responsibility (what does what)

### A) File monitoring
- `watchdog`:
  - Used in `monitoring.py`
  - `Observer` watches `fake_data/` recursively in real time.
  - `FileSystemEventHandler` captures file create/modify/delete/move events.
  - This is the core library for file activity monitoring.

### B) Process monitoring
- `psutil`:
  - Used in `monitoring.py` and `utils.py`
  - Scans running processes (`pid`, `name`) and flags suspicious names like `ransom`, `encrypt`, `crypto`.
  - Collects process details for logging.

### C) Trap/fake file creation
- `pathlib` (standard library):
  - Used across modules for safe folder/file path handling.
- `random` (standard library):
  - Used to generate realistic random folder/file names and deception layers.
- `datetime` (standard library):
  - Adds realistic timestamps in decoy files.
- Project module `fake_files.py` (`FakeFileGenerator`):
  - Creates decoy user files and high-value lure files.

### D) Deception logic (adaptive behavior)
- Project module `deception_rules.py` (`DeceptionRules`):
  - Decides when to trigger deception layers.
  - Conditions include suspicious extension, ransom-note-like names, mass encryption pattern, and deep path access.
  - Generates additional nested decoy files to keep attacker/ransomware engaged.

### E) Detection support (encryption suspicion)
- `hashlib` and `math` (standard library), used in `utils.py`:
  - Hashing and entropy calculations are used to mark files as suspiciously encrypted.

### F) Logging and storage
- `sqlite3` (standard library), used in `threat_logger.py`:
  - Stores all experiment/file/process/deception events in `honeypot.db`.
- `json` (standard library):
  - Used for structured report output and event data formatting.

### G) Runtime/control libraries
- `argparse`, `threading`, `time`, `signal`, `os`, `sys`:
  - Used in `main.py` for CLI commands, worker threads, timing, shutdown handling, and runtime control.

### H) Libraries listed in requirements but not currently used in code
- `faker`, `reportlab`, `openpyxl` are installed but not actively imported in the current implementation.
  - Intended future use:
    - `faker`: richer fake identities/content
    - `reportlab`: decoy PDF generation
    - `openpyxl`: decoy Excel generation

## 2) Which component is used for deception?
- Primary deception component: `deception_rules.py`
- Support component for deception content creation: `fake_files.py`
- Trigger source: file events from `watchdog` + rule checks in `DeceptionRules`

## 3) How the system works (end-to-end flow)

1. Start command (`python main.py`) initializes a new experiment.
2. Fake environment setup: decoy files/folders are generated in `fake_data/`.
3. Monitoring starts:
   - File events are watched by `watchdog`.
   - Running processes are scanned using `psutil`.
4. For each suspicious file/process action:
   - Event metadata is captured.
   - Data is stored by `ThreatLogger` into SQLite.
5. Deception engine evaluates event patterns:
   - If trigger conditions are met, layer-based deception is deployed.
   - New nested decoy directories/files are created dynamically.
6. On stop (`Ctrl+C`):
   - Monitoring threads shut down safely.
   - Experiment summary/report can be generated.

## 4) How system analyzes encrypted vs modified files

### A) What ransomware usually does
- It modifies file content using an encryption key (symmetric or asymmetric flow).
- It often renames files and adds new extensions like `.locked`, `.encrypted`, `.enc`.
- It may drop ransom-note files like `readme_decrypt.txt`.

### B) How this project checks a file
- Every file event (create/modify/move/delete) is captured.
- On each event, the logger stores:
  - file size
  - SHA-256 hash
  - entropy score
  - `is_encrypted` flag
- `is_encrypted` comes from `is_encrypted_suspicious(filepath)` in `utils.py`.

### C) Exact encrypted-suspicion logic in current code
- A file is marked suspicious if either condition is true:
  1. Entropy is greater than configured threshold (`high_entropy_threshold = 7.2`).
  2. File path/name contains suspicious extension from config (`.locked`, `.encrypted`, `.crypt`, `.enc`, `.ryk`, `.ransom`).
- Entropy is computed from up to first 1 MB of bytes.
- Higher entropy indicates random-looking ciphertext, which is common after encryption.

### D) How it distinguishes normal modification vs ransomware-like change
- Normal modification can change size/hash, but usually does not push entropy very high and does not add ransomware-style extension.
- Ransomware-like modification often causes:
  - sudden extension change to suspicious pattern,
  - very high-entropy content,
  - repeated events across many files (mass behavior),
  - ransom-note-like filenames.
- The system combines these signals to flag suspicious events and trigger deception layers.

### E) Important limitation (viva point)
- This is heuristic detection, not cryptographic proof.
- High entropy can also appear in some legitimate compressed/binary files.
- So the project labels files as `suspiciously encrypted`, then correlates with behavior (process + event patterns).

## 5) Short viva-ready one-liners
- File monitoring library: `watchdog`
- Process monitoring library: `psutil`
- Database/logging library: `sqlite3`
- Deception decision module: `deception_rules.py`
- Trap file generation module: `fake_files.py`
- Encryption-suspicion helpers: `utils.py` (entropy + hash logic)

## 6) Final implementation libraries and purpose (current code)
### Core modules
- `main.py`: entry point, argument parser, experiment lifecycle, integrates all components.
- `config.py`: project constants, directories, deception and encryption pattern config.
- `monitoring.py`: real-time watchdog file events, process scanning, ties one-shot detection with deception.
- `deception_rules.py`: layered adaptive deception strategy and breadcrumb generation.
- `threat_logger.py`: SQLite schema, event log APIs, experiment reporting.
- `utils.py`: file hashing, entropy, process info extraction.

### Advanced content generation
- `advanced_fake_generator.py`: realistic document generation (PDF, Excel, Word, logs, config, source code), used for high-fidelity fake environment when available.
  - `reportlab` for PDF, `openpyxl` for Excel, `python-docx` for Word, `faker` for dynamic text.

### Intelligence + reporting
- `intelligence_extractor.py`: IOC extraction from file contents, ransom note analysis, ransomware family mapping, DB IOC persistence.
- `report_generator.py`: full experiment analytics JSON/PDF reports, cross-experiment comparison.

### Deployment/test tooling
- `setup_honeypot.py`: automated virtual environment and dependency installation, directory setup, VM-safe config file creation.
- `test_honeypot.py`: all-around verification test suite for environment, dependencies, DB, fake file generation, CLI.

### Why each non-std library is used
- `watchdog`: event-driven filesystem observation requires efficient cross-platform file system events.
- `psutil`: process enumeration + local process metadata retrieval for suspicious process tracking.
- `faker`: realistic fake data values to avoid trivially synthetic honeypot artifacts.
- `reportlab`: PDF generation for user-friendly forensic reports.
- `openpyxl`: create Excel decoy data to lure ransomware targeting productivity files.
- `python-docx`: generate Word documents with sections/tables for realism.

## 7) Isolated (virtual environment) workflow
1. Clone project and go to repository.
2. Run `python3 setup_honeypot.py` (creates `honeypot_venv/`, installs packages from `requirements.txt`).
3. Activate venv:
   - Linux/macOS: `source honeypot_venv/bin/activate`
   - Windows: `honeypot_venv\\Scripts\\activate`
4. Confirm setup with `python3 test_honeypot.py`.
5. Snap VM state (critical!).
6. Start honeypot: `python3 main.py`.
7. Optionally, run ransomware sample in same isolated VM.
8. Stop with Ctrl+C, review `honeypot.db`, generated report(s) and extracted IOCs.
9. Restore VM from snapshot after each experiment.

### Why use VM isolation
- Contains possible real malware effects.
- Prevents spread to host/production network.
- Offers disposable forensic state and repeatable experiments.
- Ensures ethical and safe analysis required for ransomware research.

## 8) Notes for viva answers
- Mention that this is a proof-of-concept academic malware analysis system.
- Explain the difference between static honeypot (one-shot decoy set) and adaptive honeypot (runtime environment mutation triggered by attacker behavior).
- Explain that intelligence extraction is performed automatically via pattern matching and persistence in DB for later analysis.

