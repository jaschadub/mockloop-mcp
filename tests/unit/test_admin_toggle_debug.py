#!/usr/bin/env python3
"""
Debug script to test the admin UI toggle functionality for filtering /admin requests.
This script will help validate our diagnosis of the issue.
"""

import requests
import time
import json
import sys
from pathlib import Path

def test_admin_toggle_functionality(base_url="http://localhost:8000"):
    """
    Test the admin toggle functionality by making requests and checking the API responses.
    
    Args:
        base_url: Base URL of the mock API server
    """
    print(f"Testing admin toggle functionality at {base_url}")
    print("=" * 60)
    
    try:
        # Step 1: Make some non-admin requests to create logs
        print("Step 1: Making non-admin requests...")
        for i in range(3):
            response = requests.get(f"{base_url}/health")
            print(f"  Health check {i+1}: {response.status_code}")
            time.sleep(0.1)
        
        # Step 2: Make some admin requests to create admin logs
        print("\nStep 2: Making admin requests...")
        for i in range(2):
            response = requests.get(f"{base_url}/admin/api/requests?limit=1")
            print(f"  Admin API call {i+1}: {response.status_code}")
            time.sleep(0.1)
        
        # Step 3: Test the admin API with include_admin=false (default)
        print("\nStep 3: Testing admin API with include_admin=false (should hide admin requests)...")
        response = requests.get(f"{base_url}/admin/api/requests?include_admin=false")
        if response.status_code == 200:
            logs = response.json()
            admin_logs = [log for log in logs if log.get('path', '').startswith('/admin')]
            non_admin_logs = [log for log in logs if not log.get('path', '').startswith('/admin')]
            print(f"  Total logs returned: {len(logs)}")
            print(f"  Admin logs in response: {len(admin_logs)}")
            print(f"  Non-admin logs in response: {len(non_admin_logs)}")
            
            if admin_logs:
                print("  ❌ ISSUE FOUND: Admin requests are still showing when include_admin=false")
                print("  Sample admin log paths:", [log.get('path') for log in admin_logs[:3]])
            else:
                print("  ✅ GOOD: No admin requests showing when include_admin=false")
        else:
            print(f"  ❌ ERROR: API call failed with status {response.status_code}")
            return False
        
        # Step 4: Test the admin API with include_admin=true
        print("\nStep 4: Testing admin API with include_admin=true (should show admin requests)...")
        response = requests.get(f"{base_url}/admin/api/requests?include_admin=true")
        if response.status_code == 200:
            logs = response.json()
            admin_logs = [log for log in logs if log.get('path', '').startswith('/admin')]
            non_admin_logs = [log for log in logs if not log.get('path', '').startswith('/admin')]
            print(f"  Total logs returned: {len(logs)}")
            print(f"  Admin logs in response: {len(admin_logs)}")
            print(f"  Non-admin logs in response: {len(non_admin_logs)}")
            
            if admin_logs:
                print("  ✅ GOOD: Admin requests are showing when include_admin=true")
            else:
                print("  ⚠️  WARNING: No admin requests showing when include_admin=true (might be expected if none exist)")
        else:
            print(f"  ❌ ERROR: API call failed with status {response.status_code}")
            return False
        
        # Step 5: Test the default behavior (no include_admin parameter)
        print("\nStep 5: Testing default behavior (no include_admin parameter)...")
        response = requests.get(f"{base_url}/admin/api/requests")
        if response.status_code == 200:
            logs = response.json()
            admin_logs = [log for log in logs if log.get('path', '').startswith('/admin')]
            non_admin_logs = [log for log in logs if not log.get('path', '').startswith('/admin')]
            print(f"  Total logs returned: {len(logs)}")
            print(f"  Admin logs in response: {len(admin_logs)}")
            print(f"  Non-admin logs in response: {len(non_admin_logs)}")
            
            if admin_logs:
                print("  ❌ ISSUE FOUND: Admin requests showing by default (should be hidden)")
            else:
                print("  ✅ GOOD: Admin requests hidden by default")
        else:
            print(f"  ❌ ERROR: API call failed with status {response.status_code}")
            return False
        
        # Step 6: Check database directly if possible
        print("\nStep 6: Checking if is_admin column exists and is populated...")
        try:
            # Try to get a specific log to see its structure
            response = requests.get(f"{base_url}/admin/api/requests?limit=1&include_admin=true")
            if response.status_code == 200:
                logs = response.json()
                if logs:
                    sample_log = logs[0]
                    print(f"  Sample log structure: {list(sample_log.keys())}")
                    if 'is_admin' in sample_log:
                        print(f"  ✅ is_admin column exists: {sample_log['is_admin']}")
                    else:
                        print("  ❌ ISSUE FOUND: is_admin column missing from logs")
                else:
                    print("  ⚠️  No logs available to check structure")
        except Exception as e:
            print(f"  ❌ Error checking log structure: {e}")
        
        print("\n" + "=" * 60)
        print("Test completed. Check the output above for any issues found.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    print("Admin Toggle Debug Test")
    print("This script will test the admin UI toggle functionality")
    print("Make sure your mock API server is running before proceeding.")
    print()
    
    input("Press Enter to continue...")
    
    success = test_admin_toggle_functionality(base_url)
    
    if success:
        print("\n✅ Test completed successfully")
        return 0
    else:
        print("\n❌ Test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())