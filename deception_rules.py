import random
import time
from pathlib import Path

from config import HONEYPOT_CONFIG
from fake_files import FakeFileGenerator


class DeceptionRules:
    def __init__(self, logger, fake_data_dir: Path):
        self.logger = logger
        self.fake_data_dir = fake_data_dir
        self.last_trigger = {}

    def should_trigger_deception(self, event_type: str, filepath: Path, layer: int = 1) -> bool:
        layer_key = f"layer{layer}"
        cooldown = HONEYPOT_CONFIG["deception_layers"][layer_key]["regen_rate"]
        key = f"{layer_key}:{event_type}"
        now = time.time()

        if key in self.last_trigger and (now - self.last_trigger[key]) < cooldown:
            return False

        lower_name = filepath.name.lower()
        encrypted_ext = any(
            lower_name.endswith(ext)
            for ext in HONEYPOT_CONFIG["encryption_patterns"]["suspicious_extensions"]
        )
        ransom_note = any(
            note in lower_name for note in HONEYPOT_CONFIG["encryption_patterns"]["ransom_notes"]
        )
        deep_access = len(filepath.parts) >= layer + 3
        mass_encryption = self._check_mass_encryption()

        triggered = False
        if layer == 1:
            triggered = encrypted_ext or ransom_note
        elif layer == 2:
            triggered = encrypted_ext or ransom_note or mass_encryption
        elif layer >= 3:
            triggered = encrypted_ext or ransom_note or mass_encryption or deep_access

        if triggered:
            self.last_trigger[key] = now
        return triggered

    def _check_mass_encryption(self) -> bool:
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

    def execute_layered_deception(self, exp_id: int, layer: int):
        layer_config = HONEYPOT_CONFIG["deception_layers"][f"layer{layer}"]
        depth = layer_config["depth"]
        target_dir = self._create_nested_breadcrumbs(depth)

        profile = random.choice(HONEYPOT_CONFIG["user_profiles"])
        generator = FakeFileGenerator(target_dir, profile)
        files_generated = random.randint(20, 50)
        generator.generate_realistic_files(files_generated)

        high_value = target_dir / f"board_strategy_layer{layer}.txt"
        generator.generate_high_value_target(high_value)

        self.logger.log_deception_trigger(
            exp_id,
            "layered_deception",
            layer,
            files_generated + 1,
            str(target_dir),
        )
        print(f"[DECEPTION] Layer {layer} deployed {files_generated + 1} files")

    def _create_nested_breadcrumbs(self, depth: int) -> Path:
        current = self.fake_data_dir
        seeds = ["Confidential", "Backups", "Financials", "Database", "Executive"]

        for _ in range(depth):
            dir_name = f"{random.choice(seeds)}_{random.randint(1, 99)}"
            current = current / dir_name
            current.mkdir(exist_ok=True)

            breadcrumb = current / f"IMPORTANT_{dir_name}.txt"
            breadcrumb.write_text(f"CRITICAL FILES - DO NOT DELETE\nPath: {current}", encoding="utf-8")
        return current
