import hashlib
import math
from datetime import datetime
from pathlib import Path

import psutil

from config import HONEYPOT_CONFIG


def calculate_entropy(data: bytes) -> float:
    if not data:
        return 0.0

    entropy = 0.0
    length = len(data)
    for value in range(256):
        probability = data.count(value) / length
        if probability > 0:
            entropy -= probability * math.log(probability, 2)
    return entropy


def file_hash(filepath: Path) -> str:
    try:
        with open(filepath, "rb") as file_obj:
            return hashlib.sha256(file_obj.read()).hexdigest()
    except (FileNotFoundError, PermissionError, OSError):
        return ""


def is_encrypted_suspicious(filepath: Path) -> bool:
    try:
        stat = filepath.stat()
        if stat.st_size == 0:
            return False

        with open(filepath, "rb") as file_obj:
            data = file_obj.read(min(1024 * 1024, stat.st_size))
            entropy = calculate_entropy(data)

        suspicious_ext = any(
            ext in str(filepath).lower()
            for ext in HONEYPOT_CONFIG["encryption_patterns"]["suspicious_extensions"]
        )
        return entropy > HONEYPOT_CONFIG["encryption_patterns"]["high_entropy_threshold"] or suspicious_ext
    except (FileNotFoundError, PermissionError, OSError):
        return False


def log_process_info(pid: int) -> dict:
    try:
        proc = psutil.Process(pid)
        return {
            "pid": pid,
            "name": proc.name(),
            "exe": proc.exe(),
            "cwd": proc.cwd(),
            "create_time": datetime.fromtimestamp(proc.create_time()).isoformat(),
        }
    except (psutil.Error, OSError):
        return {"pid": pid}
