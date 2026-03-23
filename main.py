#!/usr/bin/env python3
"""
Intelligent Ransomware Honeypot with Adaptive Deception Mechanisms.
Academic research tool for ransomware analysis in isolated environments.

SAFETY WARNING: Run only in authorized, isolated virtual machines.
This software is designed to attract and monitor ransomware.
Unauthorized use is illegal.
"""

import argparse
import json
import os
import signal
import sys
import threading
import time
from pathlib import Path
from typing import List

from config import DB_PATH, FAKE_DATA_DIR, HONEYPOT_CONFIG, LOGS_DIR
from fake_files import FakeFileGenerator
from threat_logger import ThreatLogger

# Import advanced modules
try:
    from advanced_fake_generator import AdvancedFakeGenerator
    ADVANCED_GENERATION_AVAILABLE = True
except ImportError:
    ADVANCED_GENERATION_AVAILABLE = False
    print("[WARN] Advanced file generation not available")

try:
    from intelligence_extractor import IntelligenceExtractor
    INTELLIGENCE_EXTRACTION_AVAILABLE = True
except ImportError:
    INTELLIGENCE_EXTRACTION_AVAILABLE = False
    print("[WARN] Intelligence extraction not available")

try:
    from report_generator import ReportGenerator
    REPORT_GENERATION_AVAILABLE = True
except ImportError:
    REPORT_GENERATION_AVAILABLE = False
    print("[WARN] Advanced reporting not available")


class IntelligentHoneypot:
    def __init__(self):
        self.running = False
        self.exp_id = None
        self.logger = ThreatLogger()
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

    def start(self):
        print("INTELLIGENT RANSOMWARE HONEYPOT")
        print("=" * 50)

        self._generate_initial_filesystem()

        self.exp_id = self.logger.start_experiment()
        total_files = len([path for path in FAKE_DATA_DIR.rglob("*") if path.is_file()])
        self.logger.conn.execute(
            "UPDATE experiments SET total_files = ? WHERE id = ?",
            (total_files, self.exp_id),
        )
        self.logger.conn.commit()

        print(f"Experiment {self.exp_id} started with {total_files} files")
        print(f"Database: {self.logger.db_path.resolve()}")
        print(f"Monitoring: {FAKE_DATA_DIR.resolve()}")
        print("Press Ctrl+C to stop and generate summary")

        self.running = True
        from monitoring import start_monitoring

        monitor_thread = threading.Thread(target=start_monitoring, args=(self.exp_id, FAKE_DATA_DIR), daemon=True)
        monitor_thread.start()

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self._shutdown()

    def _generate_initial_filesystem(self):
        FAKE_DATA_DIR.mkdir(exist_ok=True)
        LOGS_DIR.mkdir(exist_ok=True)

        print("[Phase 1] Generating fake filesystem - Enhanced")
        
        # Use advanced generator if available
        if ADVANCED_GENERATION_AVAILABLE:
            print("  Using advanced file generation (PDFs, Excel, Word, logs, configs)")
            advanced_gen = AdvancedFakeGenerator(FAKE_DATA_DIR)
            for profile in HONEYPOT_CONFIG["user_profiles"]:
                files_created = advanced_gen.generate_diverse_environment(
                    profile, profile["file_count"]
                )
                print(f"  Generated {files_created} diverse files for {profile['username']}")
        else:
            # Fallback to basic generation
            print("  Using basic text-file generation")
            for profile in HONEYPOT_CONFIG["user_profiles"]:
                generator = FakeFileGenerator(FAKE_DATA_DIR, profile)
                generator.generate_realistic_files(profile["file_count"])

        # Create critical data breadcrumbs
        valuable_dir = FAKE_DATA_DIR / "Critical_Data"
        valuable_dir.mkdir(exist_ok=True)
        (valuable_dir / "README_BACKUP.txt").write_text(
            "ACTIVE BACKUPS - DO NOT DELETE\nLast backup: 2026-02-18\nEncryption: AES-256\n",
            encoding="utf-8",
        )
        
        # Create additional lure files
        lure_files = [
            ("Board_Strategy_2026.txt", "CONFIDENTIAL\nBoard Meeting Minutes\n2026 Strategic Direction"),
            ("Financial_Forecast_Q2_2026.xlsx", "Q2 Financial Projections"),
            ("Customer_Database.csv", "customer,email,value\nCorporate,contact@corp.com,100000"),
        ]
        
        for filename, content in lure_files:
            (valuable_dir / filename).write_text(content, encoding="utf-8")
        
        print(f"  Critical data lures deployed in {valuable_dir}")
        print("Initial filesystem deployed")

    def _shutdown(self, signum=None, frame=None):
        self.running = False
        if self.exp_id:
            self.logger.end_experiment(self.exp_id)
            report = self.logger.generate_report(self.exp_id)
            
            print("\n" + "=" * 60)
            print("EXPERIMENT SUMMARY")
            print("=" * 60)
            print(f"Experiment ID: {self.exp_id}")
            print(f"Files encrypted: {report.get('files_encrypted', 0)}")
            print(f"Deception triggers: {report.get('deception_triggers', 0)}")
            print(f"Total events: {report.get('total_file_events', 0)}")
            
            # Extract threat intelligence
            if INTELLIGENCE_EXTRACTION_AVAILABLE:
                print("\n[Phase] Extracting Threat Intelligence...")
                try:
                    extractor = IntelligenceExtractor()
                    intelligence = extractor.extract_from_directory(FAKE_DATA_DIR)
                    extractor.save_intelligence_to_db(self.exp_id, intelligence)
                    
                    print(f"  Bitcoin wallets found: {len(intelligence['bitcoins'])}")
                    print(f"  Email addresses found: {len(intelligence['emails'])}")
                    print(f"  C2 URLs found: {len(intelligence['urls'])}")
                    print(f"  TOR links found: {len(intelligence['tor_links'])}")
                    print(f"  Total IOCs extracted: {intelligence['total_iocs_found']}")
                except Exception as e:
                    print(f"  [ERROR] Intelligence extraction failed: {e}")
            
            # Generate comprehensive report
            if REPORT_GENERATION_AVAILABLE:
                print("\n[Phase] Generating Advanced Reports...")
                try:
                    report_gen = ReportGenerator()
                    full_report = report_gen.generate_full_report(self.exp_id)
                    report_gen.export_json_report(self.exp_id)
                    
                    if full_report.get('file_statistics'):
                        stats = full_report['file_statistics']
                        print(f"  Encryption rate: {stats.get('encryption_rate_percent', 0)}%")
                        print(f"  Most targeted type: {stats['file_types_targeted'][0] if stats['file_types_targeted'] else 'N/A'}")
                    
                    print("  JSON report generated")
                    
                    # Try to generate PDF report
                    try:
                        report_gen.generate_pdf_report(self.exp_id)
                        print("  PDF report generated")
                    except Exception:
                        pass
                except Exception as e:
                    print(f"  [ERROR] Report generation failed: {e}")
            
            print("\n" + "=" * 60)
            print("Full data saved in honeypot.db")
            print(f"Location: {self.logger.db_path.resolve()}")
            print("=" * 60)

        try:
            self.logger.conn.close()
        except Exception:
            pass

        print("Honeypot shutdown complete")
        sys.exit(0)


def _find_running_honeypot_pids():
    try:
        import psutil
    except Exception:
        return []

    pids = []
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = " ".join(proc.info.get("cmdline") or []).lower()
            if "python" in (proc.info.get("name") or "").lower() and "main.py" in cmdline:
                if proc.info["pid"] != os.getpid():
                    pids.append(proc.info["pid"])
        except (psutil.Error, OSError):
            continue
    return pids


def main():
    parser = argparse.ArgumentParser(description="Intelligent Ransomware Honeypot")
    parser.add_argument("--reset", action="store_true", help="Reset database and filesystem")
    parser.add_argument("--report", type=int, help="Generate report for experiment ID")
    parser.add_argument("--intelligence", type=int, help="Extract intelligence from experiment ID")
    parser.add_argument("--list-experiments", action="store_true", help="List all experiments")
    parser.add_argument("--compare", nargs='+', type=int, help="Compare multiple experiments")
    parser.add_argument("--vm-check", action="store_true", help="Check if running in VM")
    args = parser.parse_args()

    if args.vm_check:
        _check_vm_environment()
        return

    if args.reset:
        _reset_system()
        return

    if args.list_experiments:
        _list_experiments()
        return

    if args.intelligence:
        if not INTELLIGENCE_EXTRACTION_AVAILABLE:
            print("ERROR: Intelligence extraction module not available")
            return
        _extract_intelligence(args.intelligence)
        return

    if args.compare:
        if not REPORT_GENERATION_AVAILABLE:
            print("ERROR: Report generation module not available")
            return
        _compare_experiments(args.compare)
        return

    if args.report:
        logger = ThreatLogger()
        try:
            report = logger.generate_report(args.report)
            print(json.dumps(report, indent=2))
        finally:
            logger.conn.close()
        return

    # Start honeypot
    print("=" * 70)
    print("INTELLIGENT RANSOMWARE HONEYPOT - ADAPTIVE DECEPTION ENGINE")
    print("=" * 70)
    print("\nWARNING: This honeypot is designed to attract ransomware.")
    print("ONLY RUN in authorized, isolated virtual environments.")
    print("Unauthorized use is ILLEGAL.")
    print("\nPress Ctrl+C to stop and generate analysis reports.")
    print("=" * 70 + "\n")

    honeypot = IntelligentHoneypot()
    honeypot.start()


def _check_vm_environment():
    """Check if running in a virtual machine."""
    print("Checking VM environment...")
    
    vm_indicators = {
        "VirtualBox": ["vboxguest", "VirtualBox", "innotek"],
        "VMware": ["vmware", "VMware Tools"],
        "Hyper-V": ["hyperv"],
        "KVM": ["kvm"],
    }
    
    try:
        # Check for VM files/processes
        vm_found = False
        for vm_type, indicators in vm_indicators.items():
            for indicator in indicators:
                if os.path.exists(f"/proc/modules") if os.name != "nt" else False:
                    # Linux-specific check
                    pass
                if vm_type.lower() in str(os.uname()).lower() if os.name != "nt" else False:
                    print(f"✓ Detected: {vm_type}")
                    vm_found = True
        
        if not vm_found:
            print("⚠ WARNING: Could not confirm VM environment")
            print("  Ensure honeypot is running in isolated VM")
    except Exception:
        print("⚠ Could not determine VM status")


def _reset_system():
    """Reset database and filesystem."""
    import shutil

    print("Resetting honeypot system...")
    print("WARNING: This will delete all honeypot data and experiments.\n")
    
    response = input("Type 'yes' to confirm reset: ").strip()
    if response != "yes":
        print("Reset cancelled")
        return

    db_candidates = list(DB_PATH.parent.glob("honeypot*.db"))
    locked_dbs = []
    for db_file in db_candidates:
        try:
            db_file.unlink(missing_ok=True)
        except PermissionError:
            locked_dbs.append(db_file.name)

    shutil.rmtree(FAKE_DATA_DIR, ignore_errors=True)
    shutil.rmtree(LOGS_DIR, ignore_errors=True)

    if not locked_dbs:
        print("✓ Reset complete")
    else:
        pids = _find_running_honeypot_pids()
        print("⚠ Some databases are locked:")
        for db in locked_dbs:
            print(f"  - {db}")
        if pids:
            print(f"Running honeypot PIDs: {', '.join(str(p) for p in pids)}")
            print("Stop these processes and retry reset.")


def _extract_intelligence(exp_id: int):
    """Extract threat intelligence from experiment."""
    extractor = IntelligenceExtractor()
    
    report = extractor.generate_threat_report(exp_id, FAKE_DATA_DIR)
    print(json.dumps(report, indent=2))
    
    # Save to file
    output_file = LOGS_DIR / f"intelligence_report_exp{exp_id}_{int(time.time())}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n✓ Intelligence report saved to: {output_file}")


def _list_experiments():
    """List all experiments in database."""
    try:
        logger = ThreatLogger()
        cursor = logger.conn.cursor()
        cursor.execute("SELECT id, start_time, end_time, status, total_files, files_encrypted FROM experiments ORDER BY id DESC")
        experiments = cursor.fetchall()
        
        if not experiments:
            print("No experiments found")
            return
        
        print("\nExperiments:")
        print("-" * 100)
        for exp in experiments:
            exp_id, start_time, end_time, status, total_files, encrypted = exp
            print(f"ID: {exp_id:3d} | Status: {status:10s} | Files: {total_files:4} | Encrypted: {encrypted:4} | Start: {start_time}")
        print("-" * 100)
        logger.conn.close()
    except Exception as e:
        print(f"Error listing experiments: {e}")


def _compare_experiments(exp_ids: List[int]):
    """Compare multiple experiments."""
    report_gen = ReportGenerator()
    comparison = report_gen.compare_experiments(exp_ids)
    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
