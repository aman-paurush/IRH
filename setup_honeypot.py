#!/usr/bin/env python3
"""
Virtual Environment Setup Script for Ransomware Honeypot.
Prepares the environment for safe execution in an isolated VM.
"""

import os
import sys
import subprocess
from pathlib import Path
import json


def check_python_version():
    """Verify Python 3.8+ is available."""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8+ required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")


def create_venv():
    """Create virtual environment."""
    venv_path = Path("honeypot_venv")
    if venv_path.exists():
        print(f"✓ Virtual environment already exists at {venv_path}")
        return venv_path

    print(f"Creating virtual environment at {venv_path}...")
    subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
    print(f"✓ Virtual environment created")
    return venv_path


def get_pip_executable(venv_path: Path) -> str:
    """Get the pip executable path for the venv."""
    if os.name == "nt":  # Windows
        return str(venv_path / "Scripts" / "pip")
    else:  # Linux/Mac
        return str(venv_path / "bin" / "pip")


def install_requirements(venv_path: Path):
    """Install required packages."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        print(f"ERROR: requirements.txt not found")
        return False

    pip_exe = get_pip_executable(venv_path)

    print(f"\nInstalling requirements from {requirements_file}...")
    try:
        subprocess.check_call([pip_exe, "install", "-r", str(requirements_file)])
        print("✓ All requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR installing requirements: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    directories = [
        Path("fake_data"),
        Path("logs"),
        Path("reports"),
        Path("backups"),
    ]

    for directory in directories:
        directory.mkdir(exist_ok=True)
        print(f"✓ Directory created/verified: {directory}")


def initialize_database():
    """Initialize the SQLite database with schema."""
    from threat_logger import ThreatLogger

    print("\nInitializing database...")
    try:
        logger = ThreatLogger()
        logger.conn.close()
        print("✓ Database initialized")
        return True
    except Exception as e:
        print(f"ERROR initializing database: {e}")
        return False


def create_deployment_config():
    """Create VM deployment configuration."""
    config = {
        "deployment": {
            "isolation_level": "CRITICAL",
            "network": {
                "isolated_network": True,
                "internet_access": False,
                "external_connections": False,
            },
            "resource_limits": {
                "max_cpu_percent": 25,
                "max_memory_gb": 2,
                "disk_quota_gb": 50,
            },
        },
        "honeypot": {
            "run_mode": "full",
            "adaptive_deception": True,
            "monitoring_enabled": True,
            "auto_report_generation": True,
        },
        "safety_checks": {
            "vm_isolation_required": True,
            "no_production_data": True,
            "snapshot_before_run": True,
        },
        "created": "2026-03-23",
        "last_modified": "2026-03-23",
    }

    config_path = Path("deployment_config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✓ Deployment config created: {config_path}")


def print_summary():
    """Print setup summary."""
    print("\n" + "=" * 60)
    print("RANSOMWARE HONEYPOT SETUP COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. IMPORTANT: Deploy this in an ISOLATED virtual machine")
    print("2. Take a VM snapshot BEFORE running")
    print("3. Run the honeypot with: python main.py")
    print("4. Generate reports: python main.py --report <exp_id>")
    print("5. Reset system: python main.py --reset")
    print("\nSafety Notes:")
    print("  - NO production data in fake_data/")
    print("  - NEVER connect VM to production network")
    print("  - ALWAYS restore from snapshot after analysis")
    print("  - Authorized use only (academic/security research)")
    print("\nFiles and directories created:")
    print("  - honeypot_venv/          (Python environment)")
    print("  - fake_data/              (Decoy files)")
    print("  - logs/                   (Activity logs)")
    print("  - reports/                (Generated reports)")
    print("  - honeypot.db             (SQLite database)")
    print("  - deployment_config.json  (VM configuration)")
    print("\n" + "=" * 60)


def main():
    """Run complete setup."""
    print("=" * 60)
    print("RANSOMWARE HONEYPOT VIRTUAL ENVIRONMENT SETUP")
    print("=" * 60)

    check_python_version()
    venv_path = create_venv()
    create_directories()

    if not install_requirements(venv_path):
        print("\nWARNING: Some packages failed to install")
        print("Continue? (y/n): ", end="")
        if input().lower() != "y":
            sys.exit(1)

    try:
        initialize_database()
    except ImportError:
        print("Database initialization will work after running in the venv")

    create_deployment_config()
    print_summary()

    # Print activation command
    if os.name == "nt":
        activate_cmd = str(venv_path / "Scripts" / "activate")
    else:
        activate_cmd = f"source {venv_path}/bin/activate"

    print(f"\nTo activate the virtual environment, run:")
    print(f"  {activate_cmd}")
    print("\nThen run the honeypot:")
    print(f"  python main.py")


if __name__ == "__main__":
    main()
