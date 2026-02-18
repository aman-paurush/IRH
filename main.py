#!/usr/bin/env python3
"""
Intelligent ransomware honeypot (academic prototype).
Run only in an isolated and authorized lab environment.
"""

import argparse
import json
import signal
import sys
import threading
import time

from config import DB_PATH, FAKE_DATA_DIR, HONEYPOT_CONFIG, LOGS_DIR
from fake_files import FakeFileGenerator
from threat_logger import ThreatLogger


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

        print("[Phase 1] Generating fake filesystem")
        for profile in HONEYPOT_CONFIG["user_profiles"]:
            generator = FakeFileGenerator(FAKE_DATA_DIR, profile)
            generator.generate_realistic_files(profile["file_count"])

        valuable_dir = FAKE_DATA_DIR / "Critical_Data"
        valuable_dir.mkdir(exist_ok=True)
        (valuable_dir / "README_BACKUP.txt").write_text(
            "ACTIVE BACKUPS - DO NOT DELETE\nLast backup: 2026-02-18\n",
            encoding="utf-8",
        )
        print("Initial filesystem deployed")

    def _shutdown(self, signum=None, frame=None):
        self.running = False
        if self.exp_id:
            self.logger.end_experiment(self.exp_id)
            report = self.logger.generate_report(self.exp_id)
            print("\nEXPERIMENT SUMMARY")
            print(f"Files encrypted: {report.get('files_encrypted', 0)}")
            print(f"Deception triggers: {report.get('deception_triggers', 0)}")
            print(f"Total events: {report.get('total_file_events', 0)}")
            print("Full data saved in honeypot.db")

        print("Honeypot shutdown complete")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Intelligent Ransomware Honeypot")
    parser.add_argument("--reset", action="store_true", help="Reset database and filesystem")
    parser.add_argument("--report", type=int, help="Generate report for experiment ID")
    args = parser.parse_args()

    if args.reset:
        import shutil

        DB_PATH.unlink(missing_ok=True)
        shutil.rmtree(FAKE_DATA_DIR, ignore_errors=True)
        shutil.rmtree(LOGS_DIR, ignore_errors=True)
        print("Reset complete")
        return

    if args.report:
        logger = ThreatLogger()
        report = logger.generate_report(args.report)
        print(json.dumps(report, indent=2))
        return

    honeypot = IntelligentHoneypot()
    honeypot.start()


if __name__ == "__main__":
    main()
