import random
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import psutil
from config import HONEYPOT_CONFIG
from fake_files import FakeFileGenerator


class DeceptionRules:
    """Advanced adaptive deception engine with behavioral analysis."""

    def __init__(self, logger, fake_data_dir: Path):
        self.logger = logger
        self.fake_data_dir = fake_data_dir
        self.last_trigger = {}
        self.attack_metrics = {
            "encryption_events": 0,
            "files_accessed": 0,
            "suspicious_extensions": 0,
            "mass_encryption_detected": False,
        }
        self.adaptive_state = {
            "current_layer": 1,
            "engagement_time": 0,
            "trigger_count": 0,
        }

    def should_trigger_deception(self, event_type: str, filepath: Path, layer: int = 1) -> bool:
        """Determine if deception should be triggered based on adaptive rules."""
        layer_key = f"layer{layer}"
        cooldown = HONEYPOT_CONFIG["deception_layers"][layer_key]["regen_rate"]
        key = f"{layer_key}:{event_type}"
        now = time.time()

        # Check cooldown
        if key in self.last_trigger and (now - self.last_trigger[key]) < cooldown:
            return False

        # Analyze the event for indicators
        lower_name = filepath.name.lower()
        
        # Check for suspicious indicators
        encrypted_ext = self._check_suspicious_extension(lower_name)
        ransom_note = self._check_ransom_note(lower_name)
        deep_access = len(filepath.parts) >= layer + 3
        mass_encryption = self._check_mass_encryption()
        rapid_file_access = self._check_rapid_file_access()
        
        # Update metrics
        if encrypted_ext:
            self.attack_metrics["suspicious_extensions"] += 1
        if encrypted_ext or ransom_note:
            self.attack_metrics["encryption_events"] += 1
        self.attack_metrics["files_accessed"] += 1

        # Adaptive deception logic based on attack intensity
        triggered = False
        
        if layer == 1:
            # Layer 1: Basic encryption detection
            triggered = encrypted_ext or ransom_note
        elif layer == 2:
            # Layer 2: Intense activity detection
            triggered = (encrypted_ext or ransom_note or mass_encryption) and rapid_file_access
        elif layer >= 3:
            # Layer 3: Deep engagement with nested breadcrumbs
            triggered = (encrypted_ext or ransom_note or mass_encryption or deep_access) and rapid_file_access
        
        # Escalate if attack is detected
        if triggered and self.attack_metrics["encryption_events"] >= 5:
            self.attack_metrics["mass_encryption_detected"] = True
            self.adaptive_state["current_layer"] = min(3, max(self.adaptive_state["current_layer"], layer + 1))

        if triggered:
            self.last_trigger[key] = now
            self.adaptive_state["trigger_count"] += 1
        
        return triggered

    def execute_layered_deception(self, exp_id: int, layer: int):
        """Execute multi-layered deception strategy."""
        layer_config = HONEYPOT_CONFIG["deception_layers"][f"layer{layer}"]
        depth = layer_config["depth"]
        target_dir = self._create_nested_breadcrumbs(depth)

        profile = random.choice(HONEYPOT_CONFIG["user_profiles"])
        generator = FakeFileGenerator(target_dir, profile)
        files_generated = random.randint(20, 50)
        
        # Generate files
        generator.generate_realistic_files(files_generated)

        # Create high-value lure file
        high_value = target_dir / f"board_strategy_layer{layer}.txt"
        generator.generate_high_value_target(high_value)

        # Layer-specific enhancements
        self._add_layer_specific_artifacts(target_dir, layer)

        self.logger.log_deception_trigger(
            exp_id,
            "layered_deception",
            layer,
            files_generated + 1,
            str(target_dir),
        )
        print(f"[DECEPTION] Layer {layer} deployed {files_generated + 1} files at {target_dir.name}")

    def _create_nested_breadcrumbs(self, depth: int) -> Path:
        """Create nested directories that appear to contain important data."""
        current = self.fake_data_dir
        seeds = ["Confidential", "Backups", "Financials", "Database", "Executive", "Secure", "Private"]

        for i in range(depth):
            dir_name = f"{random.choice(seeds)}_{random.randint(1, 99)}"
            current = current / dir_name
            current.mkdir(exist_ok=True)

            # Add breadcrumb file that indicates importance/value
            breadcrumb = current / f"IMPORTANT_{dir_name}.txt"
            breadcrumb_content = (
                f"CRITICAL FILES - DO NOT DELETE\n"
                f"Path: {current}\n"
                f"Value: HIGH\n"
                f"Last Modified: {datetime.now().isoformat()}\n"
                f"Backup Location: \\\\internal-backup-server\\{{dir_name}}\n"
            )
            breadcrumb.write_text(breadcrumb_content, encoding="utf-8")
        
        return current

    def _add_layer_specific_artifacts(self, target_dir: Path, layer: int):
        """Add layer-specific deceptive artifacts."""
        if layer == 1:
            # Layer 1: Immediate value files
            artifacts = {
                "BACKUPS_ACTIVE.txt": "Active backups in progress. Do not interrupt.",
                "ENCRYPTION_KEY.txt": "Encryption scheme: AES-256\nKey storage: /secure/keys/backup_2026.key",
                "DATABASE_SYNC.log": "2026-03-23 14:52:01 - Database sync in progress\nEstimated completion: 2 hours",
            }
        elif layer == 2:
            # Layer 2: Database/system files
            artifacts = {
                "PRODUCTION_DB_BACKUP.sql": "-- Production database backup\n-- Critical business data\n-- Size: ~5GB",
                "SYSTEM_CREDENTIALS.conf": "[database]\nhost=prod-db-01\nuser=admin\npassword=REDACTED",
                "CUSTOMER_DATA.csv": "customer_id,name,email,credit_card\n1,John Doe,john@example.com,****",
            }
        else:
            # Layer 3: Executive/strategic files
            artifacts = {
                "STRATEGIC_PLAN_2026_2030.docx": "Confidential Strategic Planning Document",
                "ACQUISITION_TARGETS.xlsx": "Potential acquisition targets and valuations",
                "BOARD_MINUTES_SECRET.txt": "Q1 2026 Board Meeting - Confidential...",
                "M&A_PIPELINE.pdf": "Mergers and Acquisitions Pipeline",
            }

        for filename, content in artifacts.items():
            (target_dir / filename).write_text(content, encoding="utf-8")

    def _check_suspicious_extension(self, filename: str) -> bool:
        """Check if file has suspicious encryption-related extension."""
        return any(
            filename.endswith(ext)
            for ext in HONEYPOT_CONFIG["encryption_patterns"]["suspicious_extensions"]
        )

    def _check_ransom_note(self, filename: str) -> bool:
        """Check if file looks like ransom note."""
        return any(
            note in filename.lower()
            for note in HONEYPOT_CONFIG["encryption_patterns"]["ransom_notes"]
        )

    def _check_mass_encryption(self) -> bool:
        """Detect if many files have been encrypted."""
        encrypted_files = [
            path
            for path in self.fake_data_dir.rglob("*")
            if path.is_file()
            and any(
                str(path).lower().endswith(ext)
                for ext in HONEYPOT_CONFIG["encryption_patterns"]["suspicious_extensions"]
            )
        ]
        return len(encrypted_files) >= 5

    def _check_rapid_file_access(self) -> bool:
        """Detect rapid file access patterns indicating active encryption."""
        # This would normally check timestamps from monitoring events
        # For now, return True if we've seen significant activity
        return self.attack_metrics["files_accessed"] > 10

    def get_adaptive_metrics(self) -> dict:
        """Get current adaptive deception metrics."""
        return {
            "attack_metrics": self.attack_metrics,
            "adaptive_state": self.adaptive_state,
            "threat_level": self._calculate_threat_level(),
        }

    def _calculate_threat_level(self) -> str:
        """Calculate current threat level."""
        encryption_count = self.attack_metrics["encryption_events"]
        if encryption_count == 0:
            return "LOW"
        elif encryption_count < 5:
            return "MEDIUM"
        elif encryption_count < 20:
            return "HIGH"
        else:
            return "CRITICAL"
