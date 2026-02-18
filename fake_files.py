from datetime import datetime
from pathlib import Path
import random


class FakeFileGenerator:
    def __init__(self, base_dir: Path, profile: dict):
        self.base_dir = Path(base_dir)
        self.profile = profile

    def generate_realistic_files(self, count: int):
        user_dir = self.base_dir / self.profile["username"]
        folders = ["Documents", "Spreadsheets", "Projects", "Archive", "Backups"]
        stems = [
            "budget_q1",
            "payroll_summary",
            "client_list",
            "contract_notes",
            "infra_plan",
            "meeting_minutes",
            "roadmap",
            "incident_report",
            "onboarding",
            "compliance_audit",
        ]
        exts = [".txt", ".csv", ".md", ".log"]

        for _ in range(count):
            folder = random.choice(folders)
            target_dir = user_dir / folder
            target_dir.mkdir(parents=True, exist_ok=True)

            filename = f"{random.choice(stems)}_{random.randint(1, 9999)}{random.choice(exts)}"
            filepath = target_dir / filename
            filepath.write_text(self._build_file_content(filepath), encoding="utf-8")

    def generate_high_value_target(self, filepath: Path):
        content = (
            "CONFIDENTIAL - DO NOT DELETE\n\n"
            f"FILE: {filepath.name}\n"
            "OWNER: CEO Office\n"
            "VALUE: $2,500,000+\n\n"
            "CRITICAL BUSINESS DATA\n"
            "- Q4 Financial Projections\n"
            "- Acquisition Targets\n"
            "- Customer Database (50K records)\n"
            "- Intellectual Property\n\n"
            "BACKUP STATUS: ACTIVE\n"
            f"Last backup: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding="utf-8")

    def _build_file_content(self, filepath: Path) -> str:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"Owner: {self.profile['username']}\n"
            f"Department: {self.profile['department']}\n"
            f"Generated: {stamp}\n"
            f"Filename: {filepath.name}\n\n"
            "Internal business record.\n"
            "Do not share externally.\n"
        )
