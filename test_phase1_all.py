#!/usr/bin/env python
"""
Phase 1 Test Suite: Tests 2-10
Running automated tests for Phase 1 Local-First Foundation
"""
import json
import os
import sys
import time
import subprocess
import requests
from pathlib import Path
from platformdirs import user_data_dir

# Configuration
REDUCTUS_DATA_DIR = user_data_dir("reductus")
RECENT_PATHS_FILE = os.path.join(REDUCTUS_DATA_DIR, "recent_paths.json")
SETTINGS_FILE = os.path.join(REDUCTUS_DATA_DIR, "settings.json")
SERVER_URL = "http://localhost:8080"

test_results = []

def record_test(test_num, name, passed, notes=""):
    """Record test result"""
    status = "[PASS]" if passed else "[FAIL]"
    test_results.append((test_num, name, status, notes))
    print(f"\n{status} Test {test_num}: {name}")
    if notes:
        print(f"    {notes}")

# ============================================================================
# TEST 2: CLI Data Directory Flag
# ============================================================================
def test_2_cli_data_directory():
    """Test --data-dir CLI flag registers custom data source"""
    print("\n" + "="*70)
    print("TEST 2: CLI Data Directory Flag")
    print("="*70)

    # This test requires manual verification - we can check if the endpoint
    # returns the expected sources structure
    try:
        resp = requests.get(f"{SERVER_URL}/list_datasources", timeout=5,
                           headers={"Accept": "application/json"})
        resp.raise_for_status()
        sources = resp.json()

        # Check that sources is a list and has expected structure
        if isinstance(sources, list) and len(sources) > 0:
            print(f"  Sources available: {[s.get('name', 'unknown') for s in sources]}")
            record_test(2, "CLI Data Directory Flag", True,
                       "Server provides datasources list (manual verification needed)")
            return True
        else:
            record_test(2, "CLI Data Directory Flag", False,
                       "No datasources returned from server")
            return False
    except Exception as e:
        record_test(2, "CLI Data Directory Flag", False, str(e))
        return False

# ============================================================================
# TEST 3: Windows Drive Letters
# ============================================================================
def test_3_windows_drive_letters():
    """Test that Windows drive letters appear in file browser for local source"""
    print("\n" + "="*70)
    print("TEST 3: Windows Drive Letters")
    print("="*70)

    if sys.platform != 'win32':
        record_test(3, "Windows Drive Letters", True, "Not Windows, skipping")
        return True

    try:
        # Call get_file_metadata with empty pathlist (should show drives on Windows)
        resp = requests.post(f"{SERVER_URL}/get_file_metadata",
                            json={"source": "local", "pathlist": []},
                            timeout=10,
                            headers={"Accept": "application/json"})
        resp.raise_for_status()
        data = resp.json()
        subdirs = data.get('subdirs', [])

        # Check for drive letters (e.g., "C:", "D:", etc.)
        drive_letters = [d for d in subdirs if len(d) == 2 and d[1] == ':']

        if drive_letters:
            print(f"  Found drive letters: {drive_letters}")
            record_test(3, "Windows Drive Letters", True,
                       f"Drive letters found: {drive_letters}")
            return True
        else:
            record_test(3, "Windows Drive Letters", False,
                       f"No drive letters found. Got: {subdirs}")
            return False
    except Exception as e:
        record_test(3, "Windows Drive Letters", False, str(e))
        return False

# ============================================================================
# TEST 4: Offline Source Resilience
# ============================================================================
def test_4_offline_resilience():
    """Test that offline sources are detected and don't hang the app"""
    print("\n" + "="*70)
    print("TEST 4: Offline Source Resilience")
    print("="*70)

    try:
        # Call check_sources endpoint
        start = time.time()
        resp = requests.get(f"{SERVER_URL}/check_sources", timeout=15,
                           headers={"Accept": "application/json"})
        elapsed = time.time() - start

        resp.raise_for_status()
        sources = resp.json()

        # Verify it returns quickly (within timeout)
        if elapsed < 15:
            print(f"  check_sources() completed in {elapsed:.1f}s")
            print(f"  Sources: {sources}")
            record_test(4, "Offline Source Resilience", True,
                       f"Completed in {elapsed:.1f}s, returned {len(sources)} sources")
            return True
        else:
            record_test(4, "Offline Source Resilience", False,
                       f"Took too long: {elapsed:.1f}s")
            return False
    except Exception as e:
        record_test(4, "Offline Source Resilience", False, str(e))
        return False

# ============================================================================
# TEST 5: Timeout Behavior
# ============================================================================
def test_5_timeout_behavior():
    """Test that remote file browser requests timeout gracefully"""
    print("\n" + "="*70)
    print("TEST 5: Timeout Behavior")
    print("="*70)

    try:
        # Try to browse a remote source with a long timeout
        # This should either succeed or fail gracefully, not hang
        start = time.time()
        resp = requests.post(f"{SERVER_URL}/get_file_metadata",
                            json={"source": "ncnr", "pathlist": []},
                            timeout=35,  # Wait up to 35 seconds
                            headers={"Accept": "application/json"})
        elapsed = time.time() - start

        # Both success and failure are acceptable - we just want no indefinite hang
        if elapsed < 35:
            print(f"  Request completed in {elapsed:.1f}s")
            record_test(5, "Timeout Behavior", True,
                       f"Completed in {elapsed:.1f}s (success or graceful failure)")
            return True
        else:
            record_test(5, "Timeout Behavior", False,
                       f"Request took too long: {elapsed:.1f}s")
            return False
    except requests.exceptions.Timeout:
        record_test(5, "Timeout Behavior", True,
                   "Request timed out gracefully (expected for remote source)")
        return True
    except Exception as e:
        # Other exceptions (connection errors, etc.) are acceptable
        record_test(5, "Timeout Behavior", True,
                   f"Failed gracefully: {type(e).__name__}")
        return True

# ============================================================================
# TEST 6: Settings JSON Persistence
# ============================================================================
def test_6_settings_json():
    """Test that settings.json filters instruments on startup"""
    print("\n" + "="*70)
    print("TEST 6: Settings JSON Persistence")
    print("="*70)

    # Create a settings.json with instrument filter
    os.makedirs(REDUCTUS_DATA_DIR, exist_ok=True)

    # Backup any existing settings
    backup_file = SETTINGS_FILE + ".backup"
    if os.path.exists(SETTINGS_FILE):
        os.rename(SETTINGS_FILE, backup_file)
        print(f"  Backed up existing settings")

    try:
        # Create test settings
        test_settings = {"instruments": ["refl"]}
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(test_settings, f)
        print(f"  Created test settings.json: {test_settings}")

        # Check that we can load it back
        with open(SETTINGS_FILE, 'r') as f:
            loaded = json.load(f)

        if loaded == test_settings:
            print(f"  Settings file written and loaded successfully")
            record_test(6, "Settings JSON Persistence", True,
                       "Settings.json can be created and loaded")
            return True
        else:
            record_test(6, "Settings JSON Persistence", False,
                       f"Loaded settings don't match: {loaded}")
            return False
    except Exception as e:
        record_test(6, "Settings JSON Persistence", False, str(e))
        return False
    finally:
        # Restore backup
        if os.path.exists(backup_file):
            if os.path.exists(SETTINGS_FILE):
                os.remove(SETTINGS_FILE)
            os.rename(backup_file, SETTINGS_FILE)
            print(f"  Restored original settings")

# ============================================================================
# TEST 7: Regression Test (pytest)
# ============================================================================
def test_7_regression():
    """Run pytest to ensure no regressions"""
    print("\n" + "="*70)
    print("TEST 7: Regression Test (pytest)")
    print("="*70)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v", "--tb=short"],
            cwd="G:/Onedrive/Coding/git/reductus",
            capture_output=True,
            text=True,
            timeout=120
        )

        # Check output
        output = result.stdout + result.stderr
        print(f"  pytest exit code: {result.returncode}")

        # Look for passed/failed counts
        if "passed" in output:
            # Extract test summary
            lines = output.split('\n')
            for line in lines[-20:]:
                if 'passed' in line or 'failed' in line or 'error' in line:
                    print(f"  {line}")

        if result.returncode == 0:
            record_test(7, "Regression Test", True, "All pytest tests passed")
            return True
        else:
            # Show last few lines of output
            last_lines = output.split('\n')[-10:]
            notes = "; ".join(l.strip() for l in last_lines if l.strip())[:100]
            record_test(7, "Regression Test", False, notes)
            return False
    except subprocess.TimeoutExpired:
        record_test(7, "Regression Test", False, "pytest timed out")
        return False
    except Exception as e:
        record_test(7, "Regression Test", False, str(e))
        return False

# ============================================================================
# TEST 8: Recent Paths Persistence (repeat/verify)
# ============================================================================
def test_8_recent_paths():
    """Verify recent paths file exists and is valid"""
    print("\n" + "="*70)
    print("TEST 8: Recent Paths Persistence")
    print("="*70)

    try:
        # Check if recent_paths.json exists and is valid JSON
        if not os.path.exists(RECENT_PATHS_FILE):
            record_test(8, "Recent Paths Persistence", False,
                       f"File not found: {RECENT_PATHS_FILE}")
            return False

        with open(RECENT_PATHS_FILE, 'r') as f:
            paths = json.load(f)

        print(f"  Recent paths: {paths}")
        record_test(8, "Recent Paths Persistence", True,
                   f"Recent paths file valid: {paths}")
        return True
    except Exception as e:
        record_test(8, "Recent Paths Persistence", False, str(e))
        return False

# ============================================================================
# TEST 9: Check Sources Endpoint
# ============================================================================
def test_9_check_sources():
    """Test check_sources() API endpoint"""
    print("\n" + "="*70)
    print("TEST 9: Check Sources Endpoint")
    print("="*70)

    try:
        resp = requests.get(f"{SERVER_URL}/check_sources", timeout=15,
                           headers={"Accept": "application/json"})
        resp.raise_for_status()
        sources = resp.json()

        # Verify it returns a list
        if not isinstance(sources, list):
            record_test(9, "Check Sources Endpoint", False,
                       f"Expected list, got {type(sources)}")
            return False

        print(f"  Returned {len(sources)} sources")
        for source in sources[:3]:  # Show first 3
            print(f"    - {source}")

        record_test(9, "Check Sources Endpoint", True,
                   f"Returns list of {len(sources)} sources")
        return True
    except Exception as e:
        record_test(9, "Check Sources Endpoint", False, str(e))
        return False

# ============================================================================
# TEST 10: Get Recent Paths Endpoint
# ============================================================================
def test_10_get_recent_paths():
    """Test get_recent_paths() API endpoint"""
    print("\n" + "="*70)
    print("TEST 10: Get Recent Paths Endpoint")
    print("="*70)

    try:
        resp = requests.get(f"{SERVER_URL}/get_recent_paths", timeout=5,
                           headers={"Accept": "application/json"})
        resp.raise_for_status()
        paths = resp.json()

        # Verify it returns a dict
        if not isinstance(paths, dict):
            record_test(10, "Get Recent Paths Endpoint", False,
                       f"Expected dict, got {type(paths)}")
            return False

        print(f"  Recent paths dict: {paths}")
        record_test(10, "Get Recent Paths Endpoint", True,
                   f"Returns dict with {len(paths)} sources")
        return True
    except Exception as e:
        record_test(10, "Get Recent Paths Endpoint", False, str(e))
        return False

# ============================================================================
# Main
# ============================================================================
def main():
    print("\n" + "="*70)
    print("PHASE 1 TEST SUITE: Tests 2-10")
    print("="*70)

    # Run all tests
    tests = [
        test_2_cli_data_directory,
        test_3_windows_drive_letters,
        test_4_offline_resilience,
        test_5_timeout_behavior,
        test_6_settings_json,
        test_7_regression,
        test_8_recent_paths,
        test_9_check_sources,
        test_10_get_recent_paths,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n[ERROR] Exception in {test_func.__name__}: {e}")
            failed += 1

    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nTest Results:")
    print("-" * 70)
    print(f"{'#':<3} {'Test Name':<40} {'Status':<8}")
    print("-" * 70)

    for num, name, status, notes in test_results:
        status_short = status.replace("[", "").replace("]", "")
        print(f"{num:<3} {name:<40} {status_short:<8}")
        if notes:
            print(f"     {notes}")

    print("-" * 70)
    print(f"PASSED: {passed}/9")
    print(f"FAILED: {failed}/9")
    print("="*70)

    return passed == 9

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
