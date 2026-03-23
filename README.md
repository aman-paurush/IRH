# Intelligent Ransomware Honeypot with Adaptive Deception Mechanisms

## Project Overview
This project aims to design and implement a **host-based ransomware honeypot software** that safely attracts ransomware samples into a controlled environment, observes their behavior, and automatically extracts threat intelligence using **adaptive deception mechanisms**.

Unlike traditional static honeypots, this system dynamically modifies its fake environment based on ransomware actions, increasing engagement time and improving behavioral visibility. The project is designed strictly for **academic research and malware analysis** in isolated virtual machines.

---

## Quick Start (5 Minutes)

```bash
# 1. Prepare isolated VM and take snapshot
# 2. Run setup
python3 setup_honeypot.py

# 3. Start honeypot
source honeypot_venv/bin/activate  # Windows: honeypot_venv\Scripts\activate
python3 main.py

# 4. Press Ctrl+C after attack completes
# Reports auto-generate

# 5. Analyze results
python3 main.py --report 1
python3 main.py --intelligence 1
```

For detailed instructions, see [QUICKSTART.md](QUICKSTART.md)

---

## Area of Work
- Cybersecurity
- Malware Analysis
- Ransomware Behavior Analysis
- Deception Technology
- Threat Intelligence Extraction

---

## Problem Statement
Current ransomware detection approaches rely heavily on signature-based detection and post-infection analysis. Existing honeypots often use **static file systems**, which are predictable and easily detected by modern ransomware. Additionally, threat intelligence extraction is largely manual and time-consuming.

There is a need for a **ransomware-specific honeypot** that:
- Uses realistic fake environments
- Adapts dynamically to ransomware behavior
- Automatically extracts actionable threat intelligence

---

## Objectives
- To design a honeypot-based framework that safely attracts and analyzes ransomware in a controlled environment
- To implement **adaptive deception techniques** that increase ransomware interaction time
- To analyze ransomware behavior such as file selection, encryption patterns, and execution logic
- To automatically extract threat intelligence such as ransom notes, IOCs, and TTPs
- To compare adaptive honeypots with static honeypots for effectiveness

---

## System Architecture (Complete Implementation)

### 1. **Honeypot Controller** (`main.py`)
- Orchestrates entire honeypot system
- Manages experiment lifecycle
- Integrates all components
- Command-line interface for operations

### 2. **Fake File System Generator** (`fake_files.py` & `advanced_fake_generator.py`)
- **Basic Generator**: Simple text files organized by user/department
- **Advanced Generator**: 
  - PDF documents with realistic content
  - Excel spreadsheets with financial data
  - Word documents with business content
  - System logs, configuration files
  - Source code (Python, SQL, JSON)
  - All files contain believable metadata

### 3. **Adaptive Deception Engine** (`deception_rules.py`)
- **Layer 1**: Basic deception (suspicious file detection)
- **Layer 2**: Triggered deception (mass encryption detection)
- **Layer 3**: Deep engagement (nested breadcrumbs with critical files)
- **Behavioral Analysis**: Monitors attack patterns
- **Dynamic Response**: Escalates deception based on threat level

### 4. **Real-Time Monitoring** (`monitoring.py`)
- File system monitoring with Watchdog
- Process monitoring with psutil
- Event classification and logging
- Encryption pattern detection
- Adaptive trigger evaluation

### 5. **Threat Logger** (`threat_logger.py`)
- SQLite database for persistent storage
- Experiment metadata tracking
- File event logging with entropy analysis
- Process monitoring records
- Deception trigger history

### 6. **Intelligence Extractor** (`intelligence_extractor.py`)
- **IOC Extraction**:
  - Bitcoin wallet addresses
  - Email addresses
  - C2 URLs and TOR links
  - IP addresses
  - File hashes
  - Phone numbers
- **Ransomware Family Identification**:
  - Pattern matching against known families
  - Confidence scoring
- **Database Storage**: All IOCs indexed by experiment

### 7. **Advanced Reporting** (`report_generator.py`)
- **JSON Reports**: Complete experiment data
- **PDF Reports**: Formatted analysis document
- **Comparative Analysis**: Multi-experiment comparison
- **Statistics**: Encryption rates, timeline, file types
- **Deception Effectiveness**: Layer-by-layer analysis

### 8. **Configuration & Utils** (`config.py`, `utils.py`)
- Centralized configuration management
- High-entropy detection for encrypted files
- Process information gathering
- File hashing and analysis

---

## Features Implemented

### ✅ Core Functionality
- [x] Fake file system generation (200+ files per experiment)
- [x] Real-time file system monitoring
- [x] Process activity monitoring
- [x] Encryption pattern detection
- [x] Multi-layered adaptive deception
- [x] SQLite event logging

### ✅ Advanced Features
- [x] Advanced file generation (PDFs, Excel, Word, logs, configs)
- [x] Automatic threat intelligence extraction
- [x] Ransom note parsing and IOC extraction
- [x] Ransomware family identification
- [x] Comprehensive report generation (JSON & PDF)
- [x] Multi-experiment comparison

### ✅ Deployment Features
- [x] Virtual environment setup script
- [x] Command-line interface with multiple modes
- [x] VM environment checking
- [x] Database reset functionality
- [x] Test and validation suite
- [x] Comprehensive documentation

### ✅ Safety & Isolation
- [x] VM isolation checklist
- [x] Snapshot management guidelines
- [x] Network isolation verification
- [x] Safe reset procedures

---

## Unique Contributions of This Project

- **Dynamic fake file generation** - Environment adapts during attack
- **Multi-layer adaptive deception** - Escalating lure strategy
- **Automated threat intelligence extraction** - IOC identification
- **Ransomware family fingerprinting** - Pattern-based classification
- **Comprehensive behavioral analysis** - File access patterns, encryption rates
- **Rule-based, explainable approach** - No black-box ML models

---

## Technology Stack

### Core Technologies
- **Python 3.8+** - Primary language
- **Watchdog 4.0+** - File system monitoring
- **psutil 6.0+** - Process monitoring
- **SQLite3** - Event database
- **Ubuntu 22.04 LTS** - Recommended OS

### Data Generation
- **Faker** - Fake data generation
- **ReportLab** - PDF generation
- **openpyxl** - Excel file creation
- **python-docx** - Word document creation

### Analysis & Reporting
- **JSON** - Data export format
- **ReportLab** - PDF report generation

---

## File Structure

```
honeypot-project/
├── main.py                      # Main controller & CLI
├── config.py                    # Configuration (paths, patterns)
├── fake_files.py                # Basic fake file generator
├── advanced_fake_generator.py   # Advanced file generation
├── monitoring.py                # File system monitoring
├── deception_rules.py           # Adaptive deception engine
├── threat_logger.py             # Event logging & database
├── intelligence_extractor.py    # IOC extraction & analysis
├── report_generator.py          # Report generation
├── utils.py                     # Utility functions
├── setup_honeypot.py            # Virtual environment setup
├── test_honeypot.py             # Validation test suite
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── QUICKSTART.md                # Quick start guide
├── DEPLOYMENT_GUIDE.md          # Detailed deployment
├── fake_data/                   # Generated honeypot files
├── logs/                        # Activity logs
└── honeypot.db                  # SQLite event database
```

---

## Safety & Ethical Considerations

### CRITICAL REQUIREMENTS
- All ransomware samples are executed **only in isolated virtual machines**
- No connection to production networks
- VM snapshots restored after every experiment
- Project is strictly for authorized security research

### Compliance
- [ ] Only run in authorized environment
- [ ] Obtain institutional review/approval
- [ ] Document all testing and analysis
- [ ] Follow responsible disclosure practices

---

## Getting Started

### Installation
```bash
# Automatic (recommended)
python3 setup_honeypot.py

# Manual
python3 -m venv honeypot_venv
source honeypot_venv/bin/activate
pip install -r requirements.txt
```

### Validation
```bash
python3 test_honeypot.py  # Run test suite
```

### Running Honeypot
```bash
python3 main.py                    # Start honeypot
python3 main.py --list-experiments # View past tests
python3 main.py --report 1         # Generate report
python3 main.py --intelligence 1   # Extract IOCs
```

### Advanced Operations
```bash
python3 main.py --compare 1 2 3    # Compare multiple experiments
python3 main.py --vm-check         # Verify VM isolation
python3 main.py --reset            # Reset system
```

---

## Expected Outcomes

From running the honeypot with actual ransomware samples, you will obtain:

1. **Behavioral Logs**
   - File access patterns
   - Encryption timelines
   - Process activity records

2. **Threat Intelligence**
   - Bitcoin wallets
   - Email addresses
   - C2 infrastructure
   - Ransom note analysis

3. **Attack Metrics**
   - Encryption rate (%)
   - Engagement time
   - File targeting patterns
   - Deception effectiveness

4. **Comparative Analysis**
   - Static vs. adaptive honeypot
   - Different ransomware families
   - Evolution of techniques

---

## Future Work

- Integration with YARA rules for file classification
- Machine learning for behavior clustering
- Integration with threat intelligence feeds
- Multi-VM distributed honeypot
- Live dashboard with real-time metrics
- Automated behavior reports

---

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup guide
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Comprehensive deployment guide
- [test_honeypot.py](test_honeypot.py) - Validation test suite

---

## Author
**Aman Paurush**  
Cybersecurity | Malware Analysis  
PBL-4 Project

---

## License and Authorization

This tool is provided for **authorized security research only**. 

Before using this honeypot, ensure:
- [ ] You have explicit authorization
- [ ] Your institution approved this research
- [ ] You understand legal implications
- [ ] You will use findings responsibly
- [ ] You follow responsible disclosure

**Unauthorized access to computer systems is illegal.**

---

## Support

For issues or questions:
1. Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) troubleshooting section
2. Run test suite: `python3 test_honeypot.py`
3. Review database: `sqlite3 honeypot.db`
4. Check logs: `tail -f logs/honeypot.log`

---

**Status: COMPLETE AND READY FOR DEPLOYMENT**
**Last Updated: March 23, 2026**
**Version: 1.0**
