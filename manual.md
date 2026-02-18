# Intelligent Ransomware Honeypot Manual

## 1) What your project is doing right now

Your tool is an **academic ransomware honeypot prototype** that does 4 core things:

1. **Creates a fake target filesystem**
- On start, it generates realistic decoy files/folders inside `fake_data/`.
- It uses user profiles from `config.py` (finance, HR, IT) to make file patterns look real.

2. **Monitors file activity in real time**
- It watches `fake_data/` recursively for file events (create/modify/delete/move).
- Every event is logged to SQLite with metadata like file size, entropy, hash, and encryption suspicion.

3. **Monitors suspicious process names**
- It scans running processes.
- If process names contain keywords like `ransom`, `encrypt`, `crypto`, it logs process details.

4. **Triggers adaptive deception**
- Based on suspicious patterns (extensions/ransom-note names/depth/mass behavior), it creates deeper decoy layers.
- This simulates attacker engagement and records when deception was triggered.

## 2) Data it stores for analysis

The database (usually `honeypot.db`, sometimes fallback `honeypot_YYYYMMDD_HHMMSS.db`) stores:
- `experiments`: run start/end/status
- `file_events`: file path, event type, size, entropy, hash, encrypted flag
- `process_events`: suspicious process info
- `deception_events`: deception layer trigger details

This helps explain:
- Which files were touched first
- Which files looked encrypted
- Whether suspicious process behavior appeared
- How many deception triggers happened during a run

## 3) Commands and purpose

### Start honeypot
```powershell
python main.py
```
Purpose:
- Deploy decoy files
- Start monitoring + logging
- Start deception engine

Expected console:
- Experiment ID
- Active DB path
- Monitoring folder path

Stop:
- Press `Ctrl+C` to end experiment and print summary.

### Reset lab state (clean run)
```powershell
python main.py --reset
```
Purpose:
- Remove generated honeypot data for a fresh test:
  - `fake_data/`
  - `logs/`
  - `honeypot*.db`

If DB is locked:
- It prints locked DB names and PIDs.
- Stop those processes, then run `--reset` again.

### Show experiment report
```powershell
python main.py --report <experiment_id>
```
Example:
```powershell
python main.py --report 1
```
Purpose:
- Print JSON summary for one experiment:
  - encrypted files count
  - file event count
  - deception trigger count

## 4) Typical evaluation demo flow

1. Reset environment:
```powershell
python main.py --reset
```
2. Start honeypot:
```powershell
python main.py
```
3. Perform controlled test actions in `fake_data/` (or run safe simulator in lab).
4. Stop with `Ctrl+C`.
5. Read summary and run:
```powershell
python main.py --report <id>
```

## 5) Important notes for evaluation

- Use only in isolated VM/lab.
- This is detection/observation tooling, not full ransomware prevention.
- If `honeypot.db` is locked/read-only, the app can use a fallback DB file automatically.
