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

    try:
        # Step 1: Make some non-admin requests to create logs
        for _i in range(3):
            response = requests.get(f"{base_url}/health")
            time.sleep(0.1)

        # Step 2: Make some admin requests to create admin logs
        for _i in range(2):
            response = requests.get(f"{base_url}/admin/api/requests?limit=1")
            time.sleep(0.1)

        # Step 3: Test the admin API with include_admin=false (default)
        response = requests.get(f"{base_url}/admin/api/requests?include_admin=false")
        if response.status_code == 200:
            logs = response.json()
            admin_logs = [log for log in logs if log.get('path', '').startswith('/admin')]
            [log for log in logs if not log.get('path', '').startswith('/admin')]

            if admin_logs:
                pass
            else:
                pass
        else:
            return False

        # Step 4: Test the admin API with include_admin=true
        response = requests.get(f"{base_url}/admin/api/requests?include_admin=true")
        if response.status_code == 200:
            logs = response.json()
            admin_logs = [log for log in logs if log.get('path', '').startswith('/admin')]
            [log for log in logs if not log.get('path', '').startswith('/admin')]

            if admin_logs:
                pass
            else:
                pass
        else:
            return False

        # Step 5: Test the default behavior (no include_admin parameter)
        response = requests.get(f"{base_url}/admin/api/requests")
        if response.status_code == 200:
            logs = response.json()
            admin_logs = [log for log in logs if log.get('path', '').startswith('/admin')]
            [log for log in logs if not log.get('path', '').startswith('/admin')]

            if admin_logs:
                pass
            else:
                pass
        else:
            return False

        # Step 6: Check database directly if possible
        try:
            # Try to get a specific log to see its structure
            response = requests.get(f"{base_url}/admin/api/requests?limit=1&include_admin=true")
            if response.status_code == 200:
                logs = response.json()
                if logs:
                    sample_log = logs[0]
                    if 'is_admin' in sample_log:
                        pass
                    else:
                        pass
                else:
                    pass
        except Exception:
            pass

        return True

    except Exception:
        return False

def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"


    input("Press Enter to continue...")

    success = test_admin_toggle_functionality(base_url)

    if success:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
