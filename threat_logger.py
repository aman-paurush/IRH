import json
import sqlite3
from datetime import datetime
from pathlib import Path

from config import DB_PATH
from utils import calculate_entropy, file_hash, is_encrypted_suspicious


class ThreatLogger:
    def __init__(self):
        self.db_path = DB_PATH
        self.conn = self._connect_with_fallback()
        self._init_schema()

    def _connect_with_fallback(self):
        try:
            return sqlite3.connect(self.db_path, check_same_thread=False)
        except sqlite3.Error:
            fallback = DB_PATH.with_name(f"honeypot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            self.db_path = fallback
            print(f"[WARN] Primary DB unavailable. Using fallback DB: {fallback.name}")
            return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_schema(self):
        cursor = self.conn.cursor()
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT,
                end_time TEXT,
                status TEXT,
                total_files INTEGER DEFAULT 0,
                engagement_time INTEGER,
                files_encrypted INTEGER DEFAULT 0,
                deception_triggers INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS file_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER,
                timestamp TEXT,
                filepath TEXT,
                event_type TEXT,
                size_bytes INTEGER,
                entropy REAL,
                hash TEXT,
                is_encrypted BOOLEAN,
                FOREIGN KEY(experiment_id) REFERENCES experiments(id)
            );

            CREATE TABLE IF NOT EXISTS process_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER,
                timestamp TEXT,
                pid INTEGER,
                process_info TEXT,
                FOREIGN KEY(experiment_id) REFERENCES experiments(id)
            );

            CREATE TABLE IF NOT EXISTS deception_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER,
                timestamp TEXT,
                trigger_type TEXT,
                layer INTEGER,
                files_generated INTEGER,
                target_dir TEXT
            );
        """
        )
        self.conn.commit()

    def start_experiment(self) -> int:
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO experiments (start_time, status) VALUES (?, ?)",
                (datetime.now().isoformat(), "running"),
            )
        except sqlite3.OperationalError as exc:
            if "readonly" not in str(exc).lower():
                raise

            self.conn.close()
            fallback = DB_PATH.with_name(f"honeypot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            self.db_path = fallback
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._init_schema()
            cursor = self.conn.cursor()
            print(f"[WARN] {DB_PATH.name} is read-only/locked. Using {fallback.name} for this run.")
            cursor.execute(
                "INSERT INTO experiments (start_time, status) VALUES (?, ?)",
                (datetime.now().isoformat(), "running"),
            )
        exp_id = cursor.lastrowid
        self.conn.commit()
        return exp_id

    def log_file_event(self, exp_id: int, filepath: Path, event_type: str):
        exists = filepath.exists()
        size_bytes = filepath.stat().st_size if exists else 0
        blob = filepath.read_bytes() if exists else b""

        payload = {
            "timestamp": datetime.now().isoformat(),
            "size_bytes": size_bytes,
            "hash": file_hash(filepath) if exists else "",
            "entropy": calculate_entropy(blob) if exists else 0.0,
            "is_encrypted": is_encrypted_suspicious(filepath) if exists else False,
        }

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO file_events (
                experiment_id, timestamp, filepath, event_type, size_bytes, entropy, hash, is_encrypted
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                exp_id,
                payload["timestamp"],
                str(filepath),
                event_type,
                payload["size_bytes"],
                payload["entropy"],
                payload["hash"],
                payload["is_encrypted"],
            ),
        )
        self.conn.commit()

    def log_process_event(self, exp_id: int, process_info: dict):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO process_events (experiment_id, timestamp, pid, process_info)
            VALUES (?, ?, ?, ?)
        """,
            (
                exp_id,
                datetime.now().isoformat(),
                process_info.get("pid", -1),
                json.dumps(process_info),
            ),
        )
        self.conn.commit()

    def log_deception_trigger(
        self,
        exp_id: int,
        trigger_type: str,
        layer: int,
        files_generated: int,
        target_dir: str,
    ):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO deception_events (
                experiment_id, timestamp, trigger_type, layer, files_generated, target_dir
            ) VALUES (?, ?, ?, ?, ?, ?)
        """,
            (exp_id, datetime.now().isoformat(), trigger_type, layer, files_generated, target_dir),
        )
        self.conn.commit()

    def end_experiment(self, exp_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE experiments SET end_time = ?, status = 'completed' WHERE id = ?",
            (datetime.now().isoformat(), exp_id),
        )
        self.conn.commit()

    def generate_report(self, exp_id: int) -> dict:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM experiments WHERE id = ?", (exp_id,))
        if cursor.fetchone() is None:
            return {"experiment_id": exp_id, "error": "experiment_not_found"}

        total_file_events = cursor.execute(
            "SELECT COUNT(*) FROM file_events WHERE experiment_id = ?",
            (exp_id,),
        ).fetchone()[0]
        files_encrypted = cursor.execute(
            "SELECT COUNT(*) FROM file_events WHERE experiment_id = ? AND is_encrypted = 1",
            (exp_id,),
        ).fetchone()[0]
        deception_triggers = cursor.execute(
            "SELECT COUNT(*) FROM deception_events WHERE experiment_id = ?",
            (exp_id,),
        ).fetchone()[0]

        return {
            "experiment_id": exp_id,
            "files_encrypted": files_encrypted,
            "total_file_events": total_file_events,
            "deception_triggers": deception_triggers,
        }
