import os
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).parent
FAKE_DATA_DIR = BASE_DIR / "fake_data"
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = BASE_DIR / "honeypot.db"

for directory in [FAKE_DATA_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

HONEYPOT_CONFIG = {
    "user_profiles": [
        {"name": "John.Doe", "dept": "Finance", "priority": 3, "file_count": 150},
        {"name": "Sarah.Wilson", "dept": "HR", "priority": 2, "file_count": 100},
        {"name": "Mike.Chen", "dept": "Engineering", "priority": 3, "file_count": 200},
        {"name": "Admin", "dept": "IT", "priority": 4, "file_count": 50},
    ],
    "encryption_patterns": {
        "suspicious_extensions": [".encrypted", ".lockbit", ".conti", ".ransom"],
        "ransom_notes": ["README.txt", "DECRYPT.txt", "HOW_TO_DECRYPT.html", "_HOW_TO_RECOVER_FILES_.html"],
        "high_entropy_threshold": 7.5,
    },
    "deception_layers": {
        "layer1": {"depth": 1, "regen_rate": 30},  # Quick regeneration
        "layer2": {"depth": 2, "regen_rate": 60},  # Medium
        "layer3": {"depth": 4, "regen_rate": 120}, # Deep valuable files
    }
}
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FAKE_DATA_DIR = BASE_DIR / "fake_data"
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = BASE_DIR / "honeypot.db"

HONEYPOT_CONFIG = {
    "user_profiles": [
        {"username": "finance_analyst", "department": "finance", "file_count": 80},
        {"username": "hr_manager", "department": "hr", "file_count": 60},
        {"username": "it_admin", "department": "it", "file_count": 70},
    ],
    "encryption_patterns": {
        "suspicious_extensions": [
            ".locked",
            ".encrypted",
            ".crypt",
            ".enc",
            ".ryk",
            ".ransom",
        ],
        "ransom_notes": [
            "readme_decrypt",
            "how_to_decrypt",
            "recover_files",
            "decrypt_instructions",
        ],
        "high_entropy_threshold": 7.2,
    },
    "deception_layers": {
        "layer1": {"depth": 1, "regen_rate": 10},
        "layer2": {"depth": 2, "regen_rate": 20},
        "layer3": {"depth": 4, "regen_rate": 30},
    },
}
