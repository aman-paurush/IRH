import time
from pathlib import Path

import psutil
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from deception_rules import DeceptionRules
from threat_logger import ThreatLogger
from utils import log_process_info


class RansomwareMonitor(FileSystemEventHandler):
    def __init__(self, exp_id: int, logger: ThreatLogger, rules: DeceptionRules, monitor_dir: Path):
        self.exp_id = exp_id
        self.logger = logger
        self.rules = rules
        self.monitor_dir = monitor_dir

    def on_any_event(self, event):
        if event.is_directory:
            return

        filepath = Path(event.src_path)
        if self.monitor_dir not in filepath.parents and filepath != self.monitor_dir:
            return

        event_type = event.event_type
        self.logger.log_file_event(self.exp_id, filepath, event_type)

        size = filepath.stat().st_size if filepath.exists() else 0
        print(f"[FILE] {event_type.upper()}: {filepath.name} (size: {size}B)")

        for layer in range(1, 4):
            if self.rules.should_trigger_deception(event_type, filepath, layer):
                self.rules.execute_layered_deception(self.exp_id, layer)

    def monitor_processes(self):
        for proc in psutil.process_iter(["pid", "name"]):
            name = (proc.info.get("name") or "").lower()
            if any(token in name for token in ["ransom", "encrypt", "crypto"]):
                info = log_process_info(proc.info["pid"])
                self.logger.log_process_event(self.exp_id, info)
                print(f"[WARN] Suspicious process: {info}")


def start_monitoring(exp_id: int, monitor_dir: Path):
    logger = ThreatLogger()
    rules = DeceptionRules(logger, monitor_dir)
    monitor = RansomwareMonitor(exp_id, logger, rules, monitor_dir)

    observer = Observer()
    observer.schedule(monitor, str(monitor_dir), recursive=True)
    observer.start()

    try:
        while True:
            monitor.monitor_processes()
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
