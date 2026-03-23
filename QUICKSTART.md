# Quick Start Guide - Ransomware Honeypot

## 5-Minute Setup

### Step 1: Prepare VM (1 min)
- Start isolated virtual machine
- Ensure no network access
- Take snapshot of clean state

### Step 2: Install (2 min)
```bash
cd honeypot-directory
python3 setup_honeypot.py
source honeypot_venv/bin/activate  # or honeypot_venv\Scripts\activate
```

### Step 3: Run Honeypot (2 min)
```bash
python3 main.py
# Wait for "Monitoring: /path/to/fake_data"
# Honeypot is now active and monitoring
```

### Step 4: Stop and Analyze (Automatic)
```bash
# Press Ctrl+C to stop
# Reports auto-generate
```

---

## What Happens When You Run It?

```
1. Creates 210+ fake files (PDFs, Excel, Word, logs, configs)
2. Starts monitoring for suspicious activity
3. Adapts environment when threats detected
4. Extracts ransomware indicators (IOCs)
5. Generates analysis reports
```

## Key Commands

```bash
# List all tests
python3 main.py --list-experiments

# View specific report
python3 main.py --report 1

# Extract threat intelligence
python3 main.py --intelligence 1

# Reset everything
python3 main.py --reset
```

## Output Explained

| Event | Meaning |
|-------|---------|
| `[FILE] CREATED` | Honeypot file accessed |
| `[ALERT]` | Suspicious activity detected |
| `[DECEPTION] Layer 1` | Adaptive lure deployed |
| `[WARN] Suspicious process` | Ransomware process likely detected |

## Generated Files

After run, check:
- `honeypot.db` - Complete database
- `honeypot_report_*.json` - Detailed analysis
- `intelligence_report_*.json` - IOCs found

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Module not found" | Run `pip install -r requirements.txt` |
| "Permission denied" | Use `chmod +x *.py` on Linux |
| "No monitoring" | Ensure `fake_data/` exists |
| Files not encrypted | Ransomware may have exited early |

## Next Steps

1. Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed setup
2. Run with actual ransomware samples in isolated VM
3. Analyze generated reports
4. Extract threat intelligence
5. Document findings

---

For detailed information, see the full deployment guide.
