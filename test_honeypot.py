#!/usr/bin/env python3
"""
Test and Validation Suite for Intelligent Ransomware Honeypot.
Verifies all components are working correctly before deployment.
"""

import sys
import json
from pathlib import Path
from datetime import datetime


def test_python_version():
    """Test Python version."""
    print("\n[TEST] Python Version")
    required = (3, 8)
    if sys.version_info >= required:
        print(f"  ✓ Python {sys.version.split()[0]} (required: 3.8+)")
        return True
    else:
        print(f"  ✗ Python {sys.version.split()[0]} (required: 3.8+)")
        return False


def test_imports():
    """Test critical imports."""
    print("\n[TEST] Module Imports")
    modules = {
        "config": "Configuration module",
        "fake_files": "Basic fake file generator",
        "threat_logger": "Threat logging system",
        "monitoring": "File system monitoring",
        "deception_rules": "Deception engine",
        "utils": "Utility functions",
    }
    
    optional_modules = {
        "advanced_fake_generator": "Advanced file generation",
        "intelligence_extractor": "Intelligence extraction",
        "report_generator": "Report generation",
    }
    
    all_ok = True
    
    # Test required modules
    print("  Required modules:")
    for module, description in modules.items():
        try:
            __import__(module)
            print(f"    ✓ {module}: {description}")
        except ImportError as e:
            print(f"    ✗ {module}: {description} - {e}")
            all_ok = False
    
    # Test optional modules
    print("  Optional modules (for enhanced features):")
    for module, description in optional_modules.items():
        try:
            __import__(module)
            print(f"    ✓ {module}: {description}")
        except ImportError:
            print(f"    ~ {module}: {description} (not available)")
    
    return all_ok


def test_dependencies():
    """Test external dependencies."""
    print("\n[TEST] External Dependencies")
    dependencies = {
        "watchdog": "File system monitoring",
        "psutil": "Process monitoring",
        "faker": "Fake data generation",
        "reportlab": "PDF generation",
        "openpyxl": "Excel file creation",
    }
    
    all_installed = True
    for package, description in dependencies.items():
        try:
            __import__(package)
            print(f"  ✓ {package}: {description}")
        except ImportError:
            print(f"  ✗ {package}: {description} - NOT INSTALLED")
            all_installed = False
    
    return all_installed


def test_file_structure():
    """Test required file structure."""
    print("\n[TEST] File Structure")
    base_dir = Path(__file__).parent
    required_files = [
        "main.py",
        "config.py",
        "fake_files.py",
        "threat_logger.py",
        "monitoring.py",
        "deception_rules.py",
        "utils.py",
        "requirements.txt",
    ]
    
    all_present = True
    for filename in required_files:
        filepath = base_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"  ✓ {filename} ({size} bytes)")
        else:
            print(f"  ✗ {filename} - MISSING")
            all_present = False
    
    return all_present


def test_config():
    """Test configuration loading."""
    print("\n[TEST] Configuration")
    try:
        from config import HONEYPOT_CONFIG, FAKE_DATA_DIR, LOGS_DIR, DB_PATH
        
        print(f"  ✓ Configuration loaded")
        print(f"  ✓ Fake data directory: {FAKE_DATA_DIR}")
        print(f"  ✓ Logs directory: {LOGS_DIR}")
        print(f"  ✓ Database path: {DB_PATH}")
        
        # Verify config structure
        required_keys = ["user_profiles", "encryption_patterns", "deception_layers"]
        for key in required_keys:
            if key in HONEYPOT_CONFIG:
                print(f"  ✓ Config section: {key}")
            else:
                print(f"  ✗ Config section missing: {key}")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False


def test_database():
    """Test database initialization."""
    print("\n[TEST] Database System")
    try:
        from threat_logger import ThreatLogger
        
        logger = ThreatLogger()
        print(f"  ✓ Database initialized: {logger.db_path}")
        
        # Check tables
        cursor = logger.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        required_tables = {
            "experiments": "Experiment metadata",
            "file_events": "File access events",
            "process_events": "Process monitoring",
            "deception_events": "Deception triggers",
        }
        
        found_tables = {row[0] for row in tables}
        all_present = True
        for table_name, description in required_tables.items():
            if table_name in found_tables:
                print(f"  ✓ Table: {table_name} ({description})")
            else:
                print(f"  ✗ Table missing: {table_name}")
                all_present = False
        
        logger.conn.close()
        return all_present
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False


def test_fake_file_generator():
    """Test fake file generation."""
    print("\n[TEST] Fake File Generator")
    try:
        from fake_files import FakeFileGenerator
        from config import FAKE_DATA_DIR
        
        test_dir = FAKE_DATA_DIR / "TEST_validation"
        test_dir.mkdir(exist_ok=True)
        
        profile = {"username": "test_user", "department": "test"}
        generator = FakeFileGenerator(test_dir, profile)
        
        # Generate a few test files
        generator.generate_realistic_files(5)
        
        # Count files
        files = list(test_dir.rglob("*.txt"))
        if len(files) >= 5:
            print(f"  ✓ Generated {len(files)} test files")
            # Cleanup
            import shutil
            shutil.rmtree(test_dir)
            return True
        else:
            print(f"  ✗ Failed to generate files (got {len(files)})")
            return False
    except Exception as e:
        print(f"  ✗ Fake file generation error: {e}")
        return False


def test_advanced_features():
    """Test optional advanced features."""
    print("\n[TEST] Advanced Features (Optional)")
    
    features = {
        "advanced_fake_generator": "Advanced file generation",
        "intelligence_extractor": "Intelligence extraction",
        "report_generator": "Report generation",
    }
    
    features_available = 0
    for module_name, description in features.items():
        try:
            __import__(module_name)
            print(f"  ✓ {description}: Available")
            features_available += 1
        except ImportError:
            print(f"  ~ {description}: Not available (install optional dependencies)")
    
    return features_available > 0


def test_permissions():
    """Test file system permissions."""
    print("\n[TEST] File System Permissions")
    from config import FAKE_DATA_DIR, LOGS_DIR
    
    all_ok = True
    for directory in [FAKE_DATA_DIR, LOGS_DIR]:
        directory.mkdir(exist_ok=True)
        try:
            # Try to create a test file
            test_file = directory / ".test_write"
            test_file.write_text("test")
            test_file.unlink()
            print(f"  ✓ Write permission: {directory}")
        except PermissionError:
            print(f"  ✗ No write permission: {directory}")
            all_ok = False
    
    return all_ok


def test_command_line():
    """Test command-line interface."""
    print("\n[TEST] Command-Line Interface")
    try:
        from main import IntelligentHoneypot
        
        print("  ✓ Main module imports successfully")
        
        # Check for expected functions
        import inspect
        from main import main, _find_running_honeypot_pids
        
        print("  ✓ Main entry point available")
        print("  ✓ Process finder available")
        return True
    except Exception as e:
        print(f"  ✗ Command-line error: {e}")
        return False


def run_all_tests():
    """Run all tests andgenerate report."""
    print("=" * 70)
    print("RANSOMWARE HONEYPOT - VALIDATION TEST SUITE")
    print("=" * 70)

    tests = [
        ("Python Version", test_python_version),
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("External Dependencies", test_dependencies),
        ("Configuration", test_config),
        ("Database System", test_database),
        ("Fake File Generator", test_fake_file_generator),
        ("File System Permissions", test_permissions),
        ("Command-Line Interface", test_command_line),
        ("Advanced Features", test_advanced_features),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = "PASS" if result else "FAIL"
        except Exception as e:
            results[test_name] = f"ERROR: {e}"
            print(f"  [ERROR] {e}")

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    pass_count = sum(1 for r in results.values() if r == "PASS")
    fail_count = sum(1 for r in results.values() if r == "FAIL")
    error_count = len(results) - pass_count - fail_count

    for test_name, result in results.items():
        status_icon = "✓" if result == "PASS" else "✗"
        print(f"{status_icon} {test_name}: {result}")

    print("\n" + "=" * 70)
    print(f"Results: {pass_count} passed, {fail_count} failed, {error_count} errors")
    print("=" * 70)

    if fail_count == 0 and error_count == 0:
        print("\n✓ ALL TESTS PASSED - System is ready for deployment")
        print("\nNext steps:")
        print("  1. Take a VM snapshot")
        print("  2. Run: python3 main.py")
        print("  3. Deploy ransomware sample to test system")
        return True
    else:
        print(f"\n✗ {fail_count + error_count} tests failed - Please fix issues before deployment")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
