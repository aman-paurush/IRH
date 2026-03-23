# Deployment Guide: Intelligent Ransomware Honeypot

## Overview
This guide provides step-by-step instructions for deploying the Intelligent Ransomware Honeypot in a virtual machine environment for analyzing ransomware behavior through adaptive deception mechanisms.

## CRITICAL SAFETY REQUIREMENTS

> **WARNING:** This honeypot is designed to ATTRACT ransomware. Never deploy in production networks or on systems with critical data.

### Prerequisites
1. **Isolated Virtual Machine** (VirtualBox, VMware, or Hyper-V)
   - No network connection to production systems
   - Isolated network or no network access
   - Snapshot capability enabled
   - Minimum 2GB RAM, 50GB disk space

2. **Operating System**
   - Ubuntu 22.04 LTS (Recommended)
   - Windows 10/11 (with WSL2)
   - CentOS/RHEL compatible

3. **Prerequisites**
   - Python 3.8+
   - pip package manager
   - Git (optional)

### Network Isolation Checklist
- [ ] VM has no internet access
- [ ] VM is on isolated network (internal only)
- [ ] VM cannot access production systems
- [ ] VM has no shared folders with host
- [ ] VM network is restricted to honeypot operations
- [ ] Firewall rules block external connections

## Installation Steps

### 1. Prepare Virtual Machine
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.10 python3.10-venv python3-pip

# Create a dedicated user (optional but recommended)
sudo useradd -m -s /bin/bash honeypot
sudo su - honeypot
```

### 2. Clone/Download Honeypot
```bash
# Clone repository (if using git)
git clone https://github.com/aman-paurush/IRH.git ~/honeypot
cd ~/honeypot

# Or extract from ZIP
unzip honeypot.zip
cd honeypot
```

### 3. Set Up Virtual Environment
```bash
# Automatic setup
python3 setup_honeypot.py

# Or manual setup
python3 -m venv honeypot_venv
source honeypot_venv/bin/activate  # On Windows: honeypot_venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
# Check that all dependencies are installed
pip list | grep -E "faker|watchdog|psutil|reportlab|openpyxl"

# Test basic functionality
python3 main.py --list-experiments

# Check VM environment
python3 main.py --vm-check
```

### 5. Take VM Snapshot
**CRITICAL:** Before running the honeypot with actual ransomware:
```bash
# VirtualBox
VBoxManage snapshot <VM-UUID> take "clean-state-before-honeypot"

# Or use VM GUI to take snapshot
```

## Running the Honeypot

### Basic Operation
```bash
# Activate virtual environment
source honeypot_venv/bin/activate

# Start honeypot
python3 main.py

# Press Ctrl+C to stop (generates reports automatically)
```

### Output During Run
```
======================================================================
INTELLIGENT RANSOMWARE HONEYPOT - ADAPTIVE DECEPTION ENGINE
======================================================================

[Phase 1] Generating fake filesystem - Enhanced
  Using advanced file generation (PDFs, Excel, Word, logs, configs)
  Generated 80 diverse files for finance_analyst
  Generated 60 diverse files for hr_manager
  Generated 70 diverse files for it_admin
  Critical data lures deployed

Experiment 1 started with 210 files
Database: /path/to/honeypot.db
Monitoring: /path/to/fake_data

[FILE] MODIFY: budget_q1_1234.txt (size: 245B)
[ALERT] Suspicious extension detected: file.locked (size: 1024B)
[DECEPTION] Layer 1 deployed 45 files
```

### Advanced Options
```bash
# List all experiments
python3 main.py --list-experiments

# Generate report for specific experiment
python3 main.py --report 1

# Extract threat intelligence
python3 main.py --intelligence 1

# Compare multiple experiments
python3 main.py --compare 1 2 3

# Reset system (WARNING: deletes all data)
python3 main.py --reset

# Check VM environment
python3 main.py --vm-check
```

## Running with Ransomware Samples

### Preparation
1. **Acquire ransomware samples**
   - From verified threat intelligence feeds
   - With proper authorization and documentation
   - Ensure academic/research approval

2. **Prepare execution environment**
   - Ensure VM is isolated
   - Ensure snapshot is taken
   - Ensure monitoring is running

### Execution
```bash
# Terminal 1: Start honeypot
python3 main.py

# Terminal 2: Execute ransomware sample
# (In a controlled manner with proper isolation)
# Example (LINUX):
/path/to/ransomware_sample

# Monitor output in terminal 1:
# [FILE] MODIFY: budget_q1_1234.txt -> budget_q1_1234.locked
# [ALERT] Encrypted-like high-entropy content detected
# [DECEPTION] Layer 2 deployed 65 files
```

### Monitoring During Attack
- Watch for file access patterns
- Observe deception layer triggers
- Monitor encryption patterns
- Track process activity

### After Attack
1. **Generate Reports**
   ```bash
   python3 main.py --report 1
   python3 main.py --intelligence 1
   ```

2. **Preserve Evidence**
   ```bash
   cp honeypot.db honeypot_exp1_backup.db
   tar czf evidence_exp1.tar.gz fake_data/ logs/
   ```

3. **Restore VM from Snapshot**
   ```bash
   # VirtualBox
   VBoxManage snapshot <VM-UUID> restore "clean-state-before-honeypot"
   ```

## Understanding the Output

### File Events
```
[FILE] CREATED: document.pdf (size: 45234B)
[FILE] MODIFIED: spreadsheet.xlsx (size: 123456B)
[FILE] DELETED: backup.sql (size: 89234B)
```

### Alerts
```
[ALERT] Suspicious extension detected: file.locked
[ALERT] Encrypted-like high-entropy content detected: file.txt
[WARN] Suspicious process: ransomware.exe (PID: 1234)
```

### Deception Triggers
```
[DECEPTION] Layer 1 deployed 45 files
  - in fake_data/Confidential_24/Board_Strategy_layer1.txt
[DECEPTION] Layer 2 deployed 65 files
  - creates breadcrumbs to deeper "valuable" data
[DECEPTION] Layer 3 deployed 89 files
  - multilevel nested directories with critical-looking files
```

## Report Analysis

### Experiment Summary After Run
```
============================================================
EXPERIMENT SUMMARY
============================================================
Experiment ID: 1
Files encrypted: 127
Deception triggers: 3
Total events: 2341

Bitcoin wallets found: 2
Email addresses found: 3
C2 URLs found: 5
TOR links found: 1
Total IOCs extracted: 11

Encryption rate: 60.5%
Most targeted type: PDF
JSON report generated
============================================================
```

### Generated Files
- `honeypot.db` - SQLite database with all events
- `honeypot_report_1_TIMESTAMP.json` - Detailed JSON report
- `honeypot_report_1_TIMESTAMP.pdf` - Formatted PDF report
- `intelligence_report_exp1_TIMESTAMP.json` - IOC extraction results

## Database Structure

### Key Tables
- **experiments** - Overall experiment metadata
- **file_events** - Individual file access events
- **deception_events** - Deception trigger records
- **process_events** - Suspicious process detections
- **threat_intelligence** - Extracted IOCs

### Query Examples
```sql
-- Find encrypted files
SELECT filepath, entropy, is_encrypted FROM file_events 
WHERE experiment_id = 1 AND is_encrypted = 1;

-- Timeline of encryption activity
SELECT DATE(timestamp), COUNT(*) as events, 
       SUM(CASE WHEN is_encrypted THEN 1 ELSE 0 END) as encrypted
FROM file_events WHERE experiment_id = 1
GROUP BY DATE(timestamp);

-- Deception effectiveness
SELECT layer, COUNT(*) as triggers, SUM(files_generated) as total_files
FROM deception_events WHERE experiment_id = 1
GROUP BY layer;
```

## Troubleshooting

### Honeypot Won't Start
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check database permissions
ls -la honeypot.db

# Try reset
python3 main.py --reset
```

### No Files Being Monitored
```bash
# Check watch capability
ls -la fake_data/

# Verify watchdog installation
python3 -c "import watchdog; print(watchdog.__version__)"

# Check file system observer
python3 main.py --list-experiments
```

### Memory Issues
```bash
# Check available memory
free -h  # Linux
wmic OS get TotalMemory  # Windows

# Reduce initial file count in config.py
# or increase VM memory allocation
```

### Intelligence Extraction Issues
```bash
# Verify modules installed
python3 -c "from intelligence_extractor import IntelligenceExtractor"

# Check for ransom notes in fake_data
find fake_data -iname "*readme*" -o -iname "*decrypt*"
```

## Performance Optimization

### For Slower Systems
1. Reduce initial file count in `config.py`:
   ```python
   "file_count": 40  # Reduce from 80/60/70
   ```

2. Adjust deception rates:
   ```python
   "regen_rate": 30  # Increase cooldown (fewer triggers)
   ```

3. Disable advanced file generation:
   - Edit `main.py` to only use basic text files

### For Analysis
```bash
# Export specific experiment data
python3 main.py --report 1 > exp1_analysis.json

# Compare attack patterns across experiments
python3 main.py --compare 1 2 3 > comparison.json
```

## Security Best Practices

1. **Always use isolated VM**
   - No shared network segments
   - No shared folders
   - No clipboard sharing

2. **Snapshot management**
   - Take snapshot BEFORE running
   - Restore AFTER analysis
   - Keep multiple snapshots for comparison

3. **Evidence preservation**
   - Backup database files
   - Archive raw outputs
   - Document findings

4. **Access control**
   - Run with least privilege
   - Restrict file permissions
   - Use separate user account

5. **Incident response**
   - Have runbooks prepared
   - Document analysis procedures
   - Train team on processes

## Advanced Features

### Custom File Generation
Edit `config.py` and `fake_files.py` to:
- Add industry-specific files
- Create realistic department structures
- Add custom file types

### Custom Deception Rules
Edit `deception_rules.py` to:
- Adjust trigger conditions
- Create new deception strategies
- Add honeypot tokens/canaries

### Integration with SIEM
Export data to external systems:
```bash
# Copy logs to central location
scp -r logs/ siem-server:/import/

# Or use database APIs
python3 -c "from threat_logger import ThreatLogger; ..."
```

## Support and Reporting Issues

### When reporting issues:
1. Include output from `main.py`
2. Attach `honeypot.db` (anonymized)
3. Include system information:
   ```bash
   python3 --version
   python3 -m pip list
   uname -a  # Linux
   systeminfo  # Windows
   ```

4. Describe honeypot behavior:
   - What files were accessed?
   - What deception was triggered?
   - What IOCs were extracted?

## References

- Watchdog: https://github.com/gorakhargosh/watchdog
- SQLite: https://www.sqlite.org/
- Faker: https://github.com/joke2k/faker
- ReportLab: https://www.reportlab.com/

## License and Authorization

This tool is provided for **authorized security research only**. Ensure:
- [ ] You have explicit authorization to run this
- [ ] You understand the legal implications
- [ ] Your organization approves this activity
- [ ] You will use findings responsibly

---

**Last Updated:** March 23, 2026
**Version:** 1.0 - Complete Implementation
