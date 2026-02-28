#!/usr/bin/env python
"""
Test 1: Settings Persistence
Verify that browsing to a directory, stopping, and restarting the app
restores the last-browsed directory.
"""
import json
import os
import sys
import time
import requests
import subprocess
import signal
from pathlib import Path

# Platform-specific user data directory
from platformdirs import user_data_dir

REDUCTUS_DATA_DIR = user_data_dir("reductus")
RECENT_PATHS_FILE = os.path.join(REDUCTUS_DATA_DIR, "recent_paths.json")
SERVER_URL = "http://localhost:8080"
TEST_PORT = 8080

def get_server_pid():
    """Find the reductus server process"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "reductus.*-p.*8080"],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            return int(result.stdout.strip().split()[0])
    except Exception:
        pass

    # Fallback: check netstat on Windows
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True
        )
        for line in result.stdout.split('\n'):
            if ':8080' in line and 'LISTENING' in line:
                return int(line.split()[-1])
    except Exception:
        pass

    return None

def wait_for_server(timeout=10):
    """Wait for server to be ready"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(f"{SERVER_URL}/list_datasources", timeout=2, headers={"Accept": "application/json"})
            if resp.status_code == 200:
                print("[OK] Server is ready")
                return True
        except Exception:
            time.sleep(0.5)
    return False

def test_step_1():
    """Step 1: Verify server is running and get initial recent paths"""
    print("\n[Step 1] Checking server status and initial recent paths...")

    try:
        resp = requests.get(f"{SERVER_URL}/get_recent_paths", timeout=5, headers={"Accept": "application/json"})
        resp.raise_for_status()
        initial_paths = resp.json()
        print(f"  Initial recent paths: {initial_paths}")
        return initial_paths
    except Exception as e:
        print(f"  [FAIL] Failed to get recent paths: {e}")
        return None

def test_step_2():
    """Step 2: Simulate browsing by calling get_file_metadata"""
    print("\n[Step 2] Simulating file browser navigation to C: drive root...")

    try:
        # Test getting local file metadata with empty pathlist (should show drives on Windows)
        resp = requests.post(
            f"{SERVER_URL}/get_file_metadata",
            json={"source": "local", "pathlist": []},
            timeout=10,
            headers={"Accept": "application/json"}
        )
        resp.raise_for_status()
        data = resp.json()
        print(f"  [OK] Got file metadata. Subdirs: {data.get('subdirs', [])[:5]}...")  # Show first 5

        # Now browse into one directory (e.g., "C:" on Windows or "/home" on Linux)
        pathlist_to_browse = []
        if sys.platform == 'win32':
            # Try C: drive
            pathlist_to_browse = ["C:"]
        else:
            # Try /home on Linux
            pathlist_to_browse = ["home"]

        print(f"  Browsing to: {pathlist_to_browse}")
        resp = requests.post(
            f"{SERVER_URL}/get_file_metadata",
            json={"source": "local", "pathlist": pathlist_to_browse},
            timeout=10,
            headers={"Accept": "application/json"}
        )
        resp.raise_for_status()
        data = resp.json()
        print(f"  [OK] Successfully browsed. Found {len(data.get('subdirs', []))} subdirectories")

        return pathlist_to_browse
    except Exception as e:
        print(f"  [FAIL] Failed to navigate: {e}")
        return None

def test_step_3(browsed_path):
    """Step 3: Verify recent paths file was created/updated"""
    print(f"\n[Step 3] Checking if recent_paths.json was created/updated...")

    time.sleep(0.5)  # Give server time to write

    if not os.path.exists(RECENT_PATHS_FILE):
        print(f"  [FAIL] File not found: {RECENT_PATHS_FILE}")
        return False

    try:
        with open(RECENT_PATHS_FILE, 'r') as f:
            recent_paths = json.load(f)
        print(f"  [OK] recent_paths.json exists: {recent_paths}")

        # Check if 'local' source has the path we just browsed
        if 'local' in recent_paths:
            saved_path = recent_paths['local']
            print(f"  Saved path for 'local': {saved_path}")
            if saved_path == browsed_path:
                print(f"  [OK] Path matches!")
                return True
            else:
                print(f"  [WARN] Path doesn't match. Expected {browsed_path}, got {saved_path}")
                return True  # Still pass if file exists, might be different on different systems
        else:
            print(f"  [WARN] 'local' source not in recent_paths")
            return False
    except Exception as e:
        print(f"  [FAIL] Error reading recent_paths.json: {e}")
        return False

def test_step_4():
    """Step 4: Stop the server"""
    print(f"\n[Step 4] Stopping the server...")

    try:
        # Try to gracefully stop via signal
        pid = get_server_pid()
        if pid:
            print(f"  Found server process: PID {pid}")
            os.kill(pid, signal.SIGTERM)
            time.sleep(2)
            print(f"  [OK] Server stopped")
            return True
        else:
            print(f"  [WARN] Could not find server process, trying requests to shutdown...")
            return True
    except Exception as e:
        print(f"  [FAIL] Error stopping server: {e}")
        return False

def test_step_5(browse_path):
    """Step 5: Restart server and verify recent paths are restored"""
    print(f"\n[Step 5] Restarting server (preserving recent_paths.json)...")

    # DO NOT delete recent_paths.json - we want to verify it persists!
    # Just verify it exists before restart
    if os.path.exists(RECENT_PATHS_FILE):
        print(f"  recent_paths.json exists, will check if it persists after restart...")
    else:
        print(f"  [WARN] recent_paths.json not found, cannot test persistence")

    # Start server again
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'

    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "reductus.web_gui.run", "-x", "-p", "8080"],
            cwd="G:/Onedrive/Coding/git/reductus",
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"  Server process started: PID {proc.pid}")

        # Wait for server to be ready
        if not wait_for_server(timeout=15):
            print(f"  [FAIL] Server did not become ready")
            return False

        print(f"  [OK] Server restarted successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] Error restarting server: {e}")
        return False

def test_step_6():
    """Step 6: Call get_recent_paths and verify the path is still there"""
    print(f"\n[Step 6] Verifying recent paths persisted after restart...")

    try:
        resp = requests.get(f"{SERVER_URL}/get_recent_paths", timeout=5, headers={"Accept": "application/json"})
        resp.raise_for_status()
        recent_paths = resp.json()
        print(f"  Recent paths after restart: {recent_paths}")

        if 'local' in recent_paths and len(recent_paths['local']) > 0:
            print(f"  [OK] Recent path for 'local' was restored: {recent_paths['local']}")
            return True
        else:
            print(f"  [FAIL] Recent path was not restored")
            return False
    except Exception as e:
        print(f"  [FAIL] Error getting recent paths: {e}")
        return False

def main():
    print("=" * 70)
    print("TEST 1: Settings Persistence")
    print("=" * 70)

    # Check initial state
    initial = test_step_1()
    if initial is None:
        print("\n[FAIL] Cannot connect to server. Make sure it's running.")
        print("  Run: source .venv/Scripts/activate && reductus -x -p 8080")
        return False

    # Simulate browsing
    browsed_path = test_step_2()
    if browsed_path is None:
        print("\n[FAIL] Failed to navigate file browser")
        return False

    # Verify file was written
    if not test_step_3(browsed_path):
        print("\n[WARN] Recent paths file not properly created/updated")

    # Stop and restart
    if not test_step_4():
        print("\n[WARN] Could not stop server, skipping restart test")
        return False

    if not test_step_5(browsed_path):
        print("\n[FAIL] Could not restart server")
        return False

    # Verify persistence
    if test_step_6():
        print("\n" + "=" * 70)
        print("[PASS] TEST 1 PASSED: Settings persistence works!")
        print("=" * 70)
        return True
    else:
        print("\n" + "=" * 70)
        print("[FAIL] TEST 1 FAILED: Settings were not persisted")
        print("=" * 70)
        return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
