#!/usr/bin/env python3
"""
Debug script to test the admin UI toggle functionality for filtering /admin requests.
This script will help validate our diagnosis of the issue.
"""

import sys
import time

import requests


def test_admin_toggle_functionality(base_url="http://localhost:8000"):
    """
    Test the admin toggle functionality by making requests and checking the API responses.

    Args:
        base_url: Base URL of the mock API server
    """

    # Step 1: Make some non-admin requests to create logs
    for _i in range(3):
        response = requests.get(f"{base_url}/health", timeout=10)
        time.sleep(0.1)

    # Step 2: Make some admin requests to create admin logs
    for _i in range(2):
        response = requests.get(f"{base_url}/admin/api/requests?limit=1", timeout=10)
        time.sleep(0.1)

    # Step 3: Test the admin API with include_admin=false (default)
    response = requests.get(f"{base_url}/admin/api/requests?include_admin=false", timeout=10)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    logs = response.json()
    admin_logs = [
        log for log in logs if log.get("path", "").startswith("/admin")
    ]
    # Admin logs should be filtered out when include_admin=false
    assert len(admin_logs) == 0, f"Expected no admin logs, but found {len(admin_logs)}"

    # Step 4: Test the admin API with include_admin=true
    response = requests.get(f"{base_url}/admin/api/requests?include_admin=true", timeout=10)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    logs = response.json()
    admin_logs = [
        log for log in logs if log.get("path", "").startswith("/admin")
    ]
    # Admin logs should be included when include_admin=true
    assert len(admin_logs) > 0, f"Expected admin logs to be included, but found {len(admin_logs)}"

    # Step 5: Test the default behavior (no include_admin parameter)
    response = requests.get(f"{base_url}/admin/api/requests", timeout=10)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    logs = response.json()
    admin_logs = [
        log for log in logs if log.get("path", "").startswith("/admin")
    ]
    # Default behavior should filter out admin logs
    assert len(admin_logs) == 0, f"Expected no admin logs by default, but found {len(admin_logs)}"

    # Step 6: Check database directly if possible
    # Try to get a specific log to see its structure
    response = requests.get(
        f"{base_url}/admin/api/requests?limit=1&include_admin=true", timeout=10
    )
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    logs = response.json()
    if logs:
        sample_log = logs[0]
        # Check if log has expected structure
        assert isinstance(sample_log, dict), "Log should be a dictionary"


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    input("Press Enter to continue...")

    try:
        test_admin_toggle_functionality(base_url)
        print("Admin toggle functionality test passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception:
        sys.exit(1)
