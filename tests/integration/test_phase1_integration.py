#!/usr/bin/env python3
"""
Test script to validate Phase 1 MockLoop MCP enhancements.
This script tests the new admin API endpoints and database schema migration.
"""
import json
import sys
import time
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mockloop_mcp.generator import generate_mock_api
from mockloop_mcp.database_migration import DatabaseMigrator, get_database_status


def test_mock_generation():
    """Test generating a mock server with Phase 1 enhancements."""
    print("🧪 Testing mock server generation with Phase 1 enhancements...")
    
    # Simple test API spec
    test_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Phase 1 Test API",
            "version": "1.0.0",
            "description": "Test API for Phase 1 enhancements"
        },
        "paths": {
            "/users": {
                "get": {
                    "summary": "Get all users",
                    "responses": {
                        "200": {
                            "description": "List of users",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "name": {"type": "string"},
                                                "email": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/users/{user_id}": {
                "get": {
                    "summary": "Get user by ID",
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "User details",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "name": {"type": "string"},
                                            "email": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    try:
        # Generate the mock server
        output_dir = generate_mock_api(
            test_spec,
            mock_server_name="phase1_test_api",
            auth_enabled=True,
            webhooks_enabled=True,
            admin_ui_enabled=True,
            storage_enabled=True
        )
        
        print(f"✅ Mock server generated successfully at: {output_dir}")
        
        # Verify key files exist
        expected_files = [
            "main.py",
            "logging_middleware.py",
            "templates/admin.html",
            "requirements_mock.txt",
            "Dockerfile",
            "docker-compose.yml"
        ]
        
        for file_path in expected_files:
            full_path = output_dir / file_path
            if full_path.exists():
                print(f"✅ {file_path} exists")
            else:
                print(f"❌ {file_path} missing")
                return False
        
        # Check if the new admin endpoints are in main.py
        main_py_content = (output_dir / "main.py").read_text()
        
        required_endpoints = [
            "/admin/api/logs/search",
            "/admin/api/logs/analyze",
            "LogAnalyzer"
        ]
        
        for endpoint in required_endpoints:
            if endpoint in main_py_content:
                print(f"✅ {endpoint} found in main.py")
            else:
                print(f"❌ {endpoint} missing from main.py")
                return False
        
        # Check if the admin UI has the new analytics tab
        admin_html_content = (output_dir / "templates" / "admin.html").read_text()
        
        required_ui_elements = [
            'data-tab="analytics"',
            "Log Analytics",
            "Advanced Log Search",
            "performLogSearch",
            "analyzeAllLogs"
        ]
        
        for element in required_ui_elements:
            if element in admin_html_content:
                print(f"✅ {element} found in admin UI")
            else:
                print(f"❌ {element} missing from admin UI")
                return False
        
        # Check middleware enhancements
        middleware_content = (output_dir / "logging_middleware.py").read_text()
        
        required_middleware_features = [
            "session_id",
            "test_scenario", 
            "correlation_id",
            "user_agent",
            "response_size",
            "extract_session_info",
            "migrate_database"
        ]
        
        for feature in required_middleware_features:
            if feature in middleware_content:
                print(f"✅ {feature} found in middleware")
            else:
                print(f"❌ {feature} missing from middleware")
                return False
        
        return output_dir
        
    except Exception as e:
        print(f"❌ Error generating mock server: {e}")
        return False


def test_database_migration(mock_dir):
    """Test database migration functionality."""
    print("\n🧪 Testing database migration functionality...")
    
    if not mock_dir:
        print("❌ No mock directory provided")
        return False
    
    # Simulate database path
    db_path = mock_dir / "db" / "request_logs.db"
    db_path.parent.mkdir(exist_ok=True)
    
    try:
        # Test migration status
        migrator = DatabaseMigrator(str(db_path))
        
        # Get initial status
        status = migrator.get_migration_status()
        print(f"✅ Initial database version: {status['current_version']}")
        print(f"✅ Latest available version: {status['latest_available']}")
        print(f"✅ Needs migration: {status['needs_migration']}")
        
        # Apply migrations
        if status['needs_migration']:
            print("🔄 Applying migrations...")
            success = migrator.apply_migrations()
            if success:
                print("✅ Migrations applied successfully")
            else:
                print("❌ Migration failed")
                return False
        
        # Check final status
        final_status = migrator.get_migration_status()
        print(f"✅ Final database version: {final_status['current_version']}")
        
        # Test backup functionality
        print("🔄 Testing database backup...")
        backup_path = migrator.backup_database()
        if Path(backup_path).exists():
            print(f"✅ Backup created: {backup_path}")
        else:
            print("❌ Backup creation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing database migration: {e}")
        return False


def test_log_analyzer_integration():
    """Test LogAnalyzer integration."""
    print("\n🧪 Testing LogAnalyzer integration...")
    
    try:
        from mockloop_mcp.log_analyzer import LogAnalyzer, quick_analyze
        
        # Test with sample log data
        sample_logs = [
            {
                "id": 1,
                "timestamp": "2024-01-01T10:00:00",
                "method": "GET",
                "path": "/users",
                "status_code": 200,
                "process_time_ms": 45,
                "client_host": "127.0.0.1",
                "headers": {"user-agent": "test-client"},
                "session_id": "test-session-1",
                "test_scenario": "user_list_test"
            },
            {
                "id": 2,
                "timestamp": "2024-01-01T10:01:00",
                "method": "GET",
                "path": "/users/123",
                "status_code": 200,
                "process_time_ms": 32,
                "client_host": "127.0.0.1",
                "headers": {"user-agent": "test-client"},
                "session_id": "test-session-1",
                "test_scenario": "user_detail_test"
            },
            {
                "id": 3,
                "timestamp": "2024-01-01T10:02:00",
                "method": "POST",
                "path": "/users",
                "status_code": 400,
                "process_time_ms": 15,
                "client_host": "127.0.0.1",
                "headers": {"user-agent": "test-client"},
                "session_id": "test-session-2",
                "test_scenario": "user_create_error_test"
            }
        ]
        
        # Test analysis
        analyzer = LogAnalyzer()
        analysis = analyzer.analyze_logs(sample_logs)
        
        # Verify analysis results
        expected_keys = [
            "total_requests",
            "time_range", 
            "methods",
            "status_codes",
            "endpoints",
            "performance",
            "errors",
            "patterns",
            "insights"
        ]
        
        for key in expected_keys:
            if key in analysis:
                print(f"✅ Analysis contains {key}")
            else:
                print(f"❌ Analysis missing {key}")
                return False
        
        # Test filtering
        filtered_logs = analyzer.filter_logs(
            sample_logs,
            method="GET",
            include_admin=False
        )
        
        if len(filtered_logs) == 2:  # Should filter to only GET requests
            print("✅ Log filtering works correctly")
        else:
            print(f"❌ Log filtering failed: expected 2, got {len(filtered_logs)}")
            return False
        
        # Test quick analysis function
        quick_result = quick_analyze(sample_logs)
        if "total_requests" in quick_result:
            print("✅ Quick analysis function works")
        else:
            print("❌ Quick analysis function failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing LogAnalyzer: {e}")
        return False


def main():
    """Run all Phase 1 integration tests."""
    print("🚀 Starting Phase 1 MockLoop MCP Integration Tests")
    print("=" * 60)
    
    # Test 1: Mock generation with new features
    mock_dir = test_mock_generation()
    if not mock_dir:
        print("\n❌ Mock generation test failed")
        return False
    
    # Test 2: Database migration
    if not test_database_migration(mock_dir):
        print("\n❌ Database migration test failed")
        return False
    
    # Test 3: LogAnalyzer integration
    if not test_log_analyzer_integration():
        print("\n❌ LogAnalyzer integration test failed")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All Phase 1 integration tests passed!")
    print("\n📋 Phase 1 Implementation Summary:")
    print("✅ Enhanced admin UI with Log Analytics tab")
    print("✅ New admin API endpoints: /admin/api/logs/search and /admin/api/logs/analyze")
    print("✅ Database schema migration system with versioning")
    print("✅ Enhanced logging middleware with session tracking")
    print("✅ LogAnalyzer integration for advanced log analysis")
    print("✅ Backward compatibility with existing mock servers")
    
    print(f"\n📁 Test mock server generated at: {mock_dir}")
    print("\n🔧 To test the mock server:")
    print(f"   cd {mock_dir}")
    print("   pip install -r requirements_mock.txt")
    print("   python main.py")
    print("   # Then visit http://localhost:8000/admin for the enhanced admin UI")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)