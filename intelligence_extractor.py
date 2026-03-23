"""
Threat Intelligence Extraction Module.
Parses ransom notes and artifacts to extract IOCs, contact information, and malware signatures.
"""

import re
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

from config import DB_PATH


class IntelligenceExtractor:
    """Extract actionable threat intelligence from honeypot artifacts."""

    def __init__(self):
        self.bitcoin_pattern = re.compile(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.url_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+|tor://[^\s<>"{}|\\^`\[\]]+')
        self.ipv4_pattern = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
        self.phone_pattern = re.compile(r'[\+]?[(]?[0-9]{3}[)\-]?[(]?[0-9]{0,3}[)\-]?[0-9]{3}[-]?[0-9]{4,6}\b')
        self.file_hash_pattern = re.compile(r'\b[a-fA-F0-9]{32}\b|\b[a-fA-F0-9]{40}\b|\b[a-fA-F0-9]{64}\b')
        self.tor_link_pattern = re.compile(r'(?:https?://)?[a-z0-9]{16,56}\.onion[^\s]*')

    def extract_from_ransom_note(self, ransom_note_path: Path) -> Dict[str, Any]:
        """Extract intelligence from ransom note."""
        if not ransom_note_path.exists():
            return {"error": "file_not_found"}

        content = ransom_note_path.read_text(encoding='utf-8', errors='ignore')
        return self._extract_iocs(content, "ransom_note")

    def extract_from_directory(self, directory: Path) -> Dict[str, Any]:
        """Extract intelligence from all files in directory."""
        intelligence = {
            "bitcoins": set(),
            "emails": set(),
            "urls": set(),
            "ipv4_addresses": set(),
            "phone_numbers": set(),
            "file_hashes": set(),
            "tor_links": set(),
            "files_scanned": 0,
            "files_with_iocs": 0,
            "ioc_count": 0,
        }

        for filepath in directory.rglob("*"):
            if not filepath.is_file():
                continue

            intelligence["files_scanned"] += 1

            # Try to read as text
            try:
                content = filepath.read_text(encoding='utf-8', errors='ignore')
                iocs = self._extract_iocs(content, str(filepath))

                if iocs.get("found_iocs"):
                    intelligence["files_with_iocs"] += 1
                    intelligence["bitcoins"].update(iocs.get("bitcoins", []))
                    intelligence["emails"].update(iocs.get("emails", []))
                    intelligence["urls"].update(iocs.get("urls", []))
                    intelligence["ipv4_addresses"].update(iocs.get("ipv4_addresses", []))
                    intelligence["phone_numbers"].update(iocs.get("phone_numbers", []))
                    intelligence["file_hashes"].update(iocs.get("file_hashes", []))
                    intelligence["tor_links"].update(iocs.get("tor_links", []))
                    intelligence["ioc_count"] += len(iocs.get("all_iocs", []))
            except (UnicodeDecodeError, PermissionError, OSError):
                continue

        # Convert sets to lists for JSON serialization
        return {
            "bitcoins": sorted(list(intelligence["bitcoins"])),
            "emails": sorted(list(intelligence["emails"])),
            "urls": sorted(list(intelligence["urls"])),
            "ipv4_addresses": sorted(list(intelligence["ipv4_addresses"])),
            "phone_numbers": sorted(list(intelligence["phone_numbers"])),
            "file_hashes": sorted(list(intelligence["file_hashes"])),
            "tor_links": sorted(list(intelligence["tor_links"])),
            "files_scanned": intelligence["files_scanned"],
            "files_with_iocs": intelligence["files_with_iocs"],
            "total_iocs_found": intelligence["ioc_count"],
            "timestamp": datetime.now().isoformat(),
        }

    def _extract_iocs(self, content: str, source: str) -> Dict[str, Any]:
        """Extract indicators of compromise from content."""
        bitcoins = set()
        emails = set()
        urls = set()
        ipv4s = set()
        phones = set()
        hashes = set()
        tor_links = set()

        # Extract each IOC type
        for match in self.bitcoin_pattern.finditer(content):
            candidate = match.group()
            # Basic bitcoin address validation (starts with 1, 3, or bc1)
            if candidate[0] in '13' or candidate.startswith('bc1'):
                bitcoins.add(candidate)

        emails.update(set(self.email_pattern.findall(content)))
        urls.update(set(self.url_pattern.findall(content)))
        ipv4s.update(set(self.ipv4_pattern.findall(content)))
        phones.update(set(self.phone_pattern.findall(content)))
        hashes.update(set(self.file_hash_pattern.findall(content)))
        
        # Extract TOR links with higher specificity
        for match in self.tor_link_pattern.finditer(content):
            tor_link = match.group()
            if len(tor_link) > 15:  # Basic validation
                tor_links.add(tor_link)

        all_iocs = list(bitcoins | emails | urls | ipv4s | phones | hashes | tor_links)

        return {
            "source": source,
            "bitcoins": list(bitcoins),
            "emails": list(emails),
            "urls": list(urls),
            "ipv4_addresses": list(ipv4s),
            "phone_numbers": list(phones),
            "file_hashes": list(hashes),
            "tor_links": list(tor_links),
            "all_iocs": all_iocs,
            "found_iocs": len(all_iocs) > 0,
        }

    def analyze_ransomware_family(self, ransom_notes: List[Path]) -> Dict[str, Any]:
        """Analyze ransom notes to identify likely ransomware family."""
        family_indicators = {
            "REvil/Sodinokibi": [
                "REvil",
                "Sodinokibi",
                "Pay attention to decryption recommendations",
                "is encrypted by REvil ransomware",
            ],
            "LockBit": [
                "LockBit",
                "LockBit 2.0",
                "Your files are encrypted",
                "8yvhxf6agay3jkyp",
            ],
            "Conti": [
                "Conti",
                "CONTI",
                "Your company's network was compromised",
            ],
            "Darkside": [
                "DarkSide",
                "Darkside",
                "is encrypted with DarkSide Ransomware",
            ],
            "Ryuk": [
                "Ryuk",
                "RYUK",
                "Your network has been penetrated",
            ],
            "Alphv/BlackCat": [
                "ALPHV",
                "BlackCat",
                "Black Cat",
                "Alpha Team",
            ],
            "Cl0p": [
                "Cl0p",
                "C10p",
                "We have also taken responsibility for copying your data",
            ],
        }

        families_found = {}
        combined_content = ""

        for note_path in ransom_notes:
            if note_path.exists():
                combined_content += note_path.read_text(encoding='utf-8', errors='ignore')
                combined_content += "\n"

        combined_lower = combined_content.lower()

        for family, indicators in family_indicators.items():
            matches = sum(1 for indicator in indicators if indicator.lower() in combined_lower)
            if matches > 0:
                families_found[family] = {"matches": matches, "confidence": min(100, matches * 33)}

        return {
            "likely_families": sorted(families_found.items(), key=lambda x: x[1]["matches"], reverse=True),
            "combined_size": len(combined_content),
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def generate_threat_report(self, exp_id: int, honeypot_dir: Path) -> Dict[str, Any]:
        """Generate comprehensive threat intelligence report."""
        # Extract intelligence from honeypot
        intelligence = self.extract_from_directory(honeypot_dir)

        # Find ransom notes
        ransom_note_patterns = ["README", "DECRYPT", "RANSOM", "NOTICE", "NOTE"]
        ransom_notes = []
        for pattern in ransom_note_patterns:
            ransom_notes.extend(honeypot_dir.rglob(f"*{pattern}*"))

        family_analysis = self.analyze_ransomware_family(ransom_notes)

        # Build comprehensive report
        report = {
            "experiment_id": exp_id,
            "report_generated": datetime.now().isoformat(),
            "indicators_of_compromise": {
                "bitcoin_wallets": intelligence["bitcoins"],
                "email_addresses": intelligence["emails"],
                "command_control_urls": intelligence["urls"],
                "ip_addresses": intelligence["ipv4_addresses"],
                "phone_numbers": intelligence["phone_numbers"],
                "file_hashes": intelligence["file_hashes"],
                "tor_links": intelligence["tor_links"],
                "total_unique_iocs": intelligence["total_iocs_found"],
            },
            "analysis_statistics": {
                "files_scanned": intelligence["files_scanned"],
                "files_containing_iocs": intelligence["files_with_iocs"],
                "ioc_extraction_rate": round(
                    (intelligence["files_with_iocs"] / intelligence["files_scanned"] * 100)
                    if intelligence["files_scanned"] > 0 else 0, 2
                ),
            },
            "ransomware_family_analysis": family_analysis["likely_families"],
            "ransom_notes_found": len(ransom_notes),
            "threat_level": self._calculate_threat_level(intelligence),
        }

        return report

    @staticmethod
    def _calculate_threat_level(intelligence: Dict) -> str:
        """Calculate threat level based on IOCs found."""
        ioc_count = intelligence["total_iocs_found"]
        if ioc_count == 0:
            return "LOW"
        elif ioc_count < 5:
            return "MEDIUM"
        elif ioc_count < 15:
            return "HIGH"
        else:
            return "CRITICAL"

    def save_intelligence_to_db(self, exp_id: int, intelligence: Dict[str, Any]) -> bool:
        """Save extracted intelligence to database."""
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS threat_intelligence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id INTEGER,
                    ioc_type TEXT,
                    ioc_value TEXT,
                    confidence_score REAL,
                    extracted_timestamp TEXT,
                    FOREIGN KEY(experiment_id) REFERENCES experiments(id),
                    UNIQUE(experiment_id, ioc_type, ioc_value)
                )
            """)

            # Insert IOCs
            timestamp = datetime.now().isoformat()
            for ioc_list, ioc_type in [
                (intelligence["bitcoins"], "bitcoin_address"),
                (intelligence["emails"], "email_address"),
                (intelligence["urls"], "command_control_url"),
                (intelligence["ipv4_addresses"], "ip_address"),
                (intelligence["phone_numbers"], "phone_number"),
                (intelligence["file_hashes"], "file_hash"),
                (intelligence["tor_links"], "tor_link"),
            ]:
                for ioc_value in ioc_list:
                    try:
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO threat_intelligence
                            (experiment_id, ioc_type, ioc_value, confidence_score, extracted_timestamp)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (exp_id, ioc_type, ioc_value, 85.0, timestamp),
                        )
                    except sqlite3.IntegrityError:
                        pass

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save intelligence to DB: {e}")
            return False


if __name__ == "__main__":
    extractor = IntelligenceExtractor()
    import sys

    if len(sys.argv) > 1:
        test_dir = Path(sys.argv[1])
        if test_dir.exists():
            results = extractor.extract_from_directory(test_dir)
            print(json.dumps(results, indent=2))
