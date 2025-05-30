#!/usr/bin/env python3
import sys
import os
import sqlite3
from pathlib import Path
import shutil
import argparse
import requests

def update_existing_mock(mock_dir):
    """
    Update an existing mock API with the fixes for request logs.
    
    Args:
        mock_dir: Path to the mock API directory
    """
    try:
        # 1. Update the admin.html template
        templates_dir = Path(mock_dir) / "templates"
        admin_html_path = templates_dir / "admin.html"
        
        if not admin_html_path.exists():
            print(f"Error: Admin UI template not found at {admin_html_path}")
            return False
            
        with open(admin_html_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Find and replace the showRequestDetails function
        old_function = """async function showRequestDetails(requestId) {
            try {
                // Clear previous details first
                document.getElementById('request-headers').textContent = 'Loading...';
                document.getElementById('request-body').textContent = 'Loading...';
                document.getElementById('response-body').textContent = 'Loading...';
                document.getElementById('request-details').style.display = 'block';
                
                const response = await fetch(`/admin/api/requests?limit=1&offset=0&id=${requestId}`);
                if (response.ok) {
                    const requests = await response.json();
                    if (requests && requests.length > 0) {
                        const req = requests[0];
                        document.getElementById('request-headers').textContent = JSON.stringify(req.headers || {}, null, 2);
                        document.getElementById('request-body').textContent = req.request_body || 'No request body';
                        document.getElementById('response-body').textContent = req.response_body || 'No response body';
                    } else {
                        document.getElementById('request-headers').textContent = 'No data available';
                        document.getElementById('request-body').textContent = 'No data available';
                        document.getElementById('response-body').textContent = 'No data available';
                    }"""
                    
        new_function = """async function showRequestDetails(requestId) {
            try {
                // Clear previous details first
                document.getElementById('request-headers').textContent = 'Loading...';
                document.getElementById('request-body').textContent = 'Loading...';
                document.getElementById('response-body').textContent = 'Loading...';
                document.getElementById('request-details').style.display = 'block';
                
                const response = await fetch(`/admin/api/requests?id=${requestId}`);
                if (response.ok) {
                    const data = await response.json();
                    // Handle both array and single object responses
                    const req = Array.isArray(data) ? data[0] : data;
                    
                    if (req && req.id) {
                        document.getElementById('request-headers').textContent = JSON.stringify(req.headers || {}, null, 2);
                        document.getElementById('request-body').textContent = req.request_body || 'No request body';
                        document.getElementById('response-body').textContent = req.response_body || 'No response body';
                    } else {
                        document.getElementById('request-headers').textContent = 'No data available';
                        document.getElementById('request-body').textContent = 'No data available';
                        document.getElementById('response-body').textContent = 'No data available';
                    }"""
                    
        updated_content = content.replace(old_function, new_function)
        
        if content == updated_content:
            print("Warning: Function replacement did not change anything in admin.html")
        
        with open(admin_html_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        # 2. Update the main.py file to handle ID parameter correctly
        main_py_path = Path(mock_dir) / "main.py"
        
        if not main_py_path.exists():
            print(f"Error: main.py not found at {main_py_path}")
            return False
            
        with open(main_py_path, "r", encoding="utf-8") as f:
            main_content = f.read()
            
        # Look for the get_request_logs function
        if "async def get_request_logs" in main_content:
            # Check if it already has the id parameter
            if "id: int = None" not in main_content:
                # Add the id parameter
                main_content = main_content.replace(
                    "async def get_request_logs(limit: int = 100, offset: int = 0, method: str = None, path: str = None, include_admin: bool = False):",
                    "async def get_request_logs(limit: int = 100, offset: int = 0, method: str = None, path: str = None, include_admin: bool = False, id: int = None):"
                )
            
            # Check for the id filter in the query
            if "# Filter by exact ID if provided" not in main_content:
                # Add the ID filter code before the method filter
                old_filter_code = """        # Build query with filters
        query = "SELECT * FROM request_logs"
        params = []
        where_clauses = []
        
        if method:"""
                
                new_filter_code = """        # Build query with filters
        query = "SELECT * FROM request_logs"
        params = []
        where_clauses = []
        
        # Filter by exact ID if provided
        if id is not None:
            where_clauses.append("id = ?")
            params.append(id)
        
        if method:"""
                
                main_content = main_content.replace(old_filter_code, new_filter_code)
            
            # Update the admin requests filter to respect id parameter
            if "if not include_admin:" in main_content and "if not include_admin and id is None:" not in main_content:
                main_content = main_content.replace(
                    "        # Filter out admin requests by default\n        if not include_admin:",
                    "        # Filter out admin requests by default, but only if not querying by specific ID\n        if not include_admin and id is None:"
                )
            
            # Update the limit/offset to be skipped when querying by id
            if "query += \" ORDER BY id DESC LIMIT ? OFFSET ?\"" in main_content and "# Skip limit/offset when querying by exact ID" not in main_content:
                old_limit_code = """        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])"""
                
                new_limit_code = """        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Skip limit/offset when querying by exact ID
        if id is not None:
            query += " ORDER BY id DESC"
        else:
            query += " ORDER BY id DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])"""
                
                main_content = main_content.replace(old_limit_code, new_limit_code)
            
            # Add the return of a single object when querying by ID
            if "return logs" in main_content and "# If we're querying by ID and have a result" not in main_content:
                old_return_code = """        conn.close()
        return logs"""
                
                new_return_code = """        conn.close()
        
        # If we're querying by ID and have a result, return just that single record instead of an array
        if id is not None and logs:
            return logs[0]
        
        return logs"""
                
                main_content = main_content.replace(old_return_code, new_return_code)
        
        with open(main_py_path, "w", encoding="utf-8") as f:
            f.write(main_content)
        
        print(f"Successfully updated mock API at {mock_dir}")
        return True
    
    except Exception as e:
        print(f"Error updating mock API: {e}")
        return False

def test_request_logs(base_url="http://localhost:8001"):
    """
    Test the request logs API to verify the fix.
    
    Args:
        base_url: Base URL of the mock API
    """
    try:
        # Make a test request to create a log
        requests.get(f"{base_url}/health")
        
        # Get all logs
        logs_response = requests.get(f"{base_url}/admin/api/requests")
        if logs_response.status_code != 200:
            print(f"Error getting logs: {logs_response.status_code}")
            return False
        
        logs = logs_response.json()
        if not logs or not isinstance(logs, list):
            print(f"No logs found or invalid response: {logs}")
            return False
        
        print(f"Found {len(logs)} logs")
        
        # Get a specific log by ID
        log_id = logs[0]["id"]
        detail_response = requests.get(f"{base_url}/admin/api/requests?id={log_id}")
        
        if detail_response.status_code != 200:
            print(f"Error getting log details: {detail_response.status_code}")
            return False
        
        log_detail = detail_response.json()
        
        if isinstance(log_detail, list):
            print("WARNING: Log detail still returned as an array, fix may not be working correctly")
            log_detail = log_detail[0] if log_detail else None
        
        if not log_detail or not isinstance(log_detail, dict) or "id" not in log_detail:
            print(f"Invalid log detail response: {log_detail}")
            return False
        
        print(f"Successfully retrieved log detail for ID {log_id}")
        print(f"Method: {log_detail.get('method')}, Path: {log_detail.get('path')}")
        
        return True
    
    except Exception as e:
        print(f"Error testing request logs: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test and fix the request logs in MockLoop mock APIs")
    parser.add_argument("--mock-dir", help="Path to the mock API directory to update")
    parser.add_argument("--base-url", default="http://localhost:8001", help="Base URL of the running mock API to test")
    parser.add_argument("--test-only", action="store_true", help="Only run the test without updating")
    
    args = parser.parse_args()
    
    if not args.test_only and args.mock_dir:
        if update_existing_mock(args.mock_dir):
            print(f"Mock API updated successfully at {args.mock_dir}")
        else:
            print(f"Failed to update mock API at {args.mock_dir}")
            return 1
    
    print(f"Testing request logs API at {args.base_url}...")
    if test_request_logs(args.base_url):
        print("Request logs API is working correctly!")
    else:
        print("Request logs API test failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
