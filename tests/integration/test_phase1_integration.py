#!/usr/bin/env python3
"""
Test script to validate Phase 1 MockLoop MCP enhancements.
This script tests the new admin API endpoints and database schema migration.
"""

from pathlib import Path
import sys

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mockloop_mcp.database_migration import DatabaseMigrator
from mockloop_mcp.generator import generate_mock_api


def test_mock_generation():
    """Test generating a mock server with Phase 1 enhancements."""

    # Simple test API spec
    test_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Phase 1 Test API",
            "version": "1.0.0",
            "description": "Test API for Phase 1 enhancements",
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
                                                "email": {"type": "string"},
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    },
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
                            "schema": {"type": "integer"},
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
                                            "email": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
        },
    }

    try:
        # Generate the mock server
        output_dir = generate_mock_api(
            test_spec,
            mock_server_name="phase1_test_api",
            auth_enabled=True,
            webhooks_enabled=True,
            admin_ui_enabled=True,
            storage_enabled=True,
        )

        # Verify key files exist
        expected_files = [
            "main.py",
            "logging_middleware.py",
            "templates/admin.html",
            "requirements_mock.txt",
            "Dockerfile",
            "docker-compose.yml",
        ]

        for file_path in expected_files:
            full_path = output_dir / file_path
            if full_path.exists():
                pass
            else:
                return False

        # Check if the new admin endpoints are in main.py
        main_py_content = (output_dir / "main.py").read_text()

        required_endpoints = [
            "/admin/api/logs/search",
            "/admin/api/logs/analyze",
            "LogAnalyzer",
        ]

        for endpoint in required_endpoints:
            if endpoint in main_py_content:
                pass
            else:
                return False

        # Check if the admin UI has the new analytics tab
        admin_html_content = (output_dir / "templates" / "admin.html").read_text()

        required_ui_elements = [
            'data-tab="analytics"',
            "Log Analytics",
            "Advanced Log Search",
            "performLogSearch",
            "analyzeAllLogs",
        ]

        for element in required_ui_elements:
            if element in admin_html_content:
                pass
            else:
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
            "migrate_database",
        ]

        for feature in required_middleware_features:
            if feature in middleware_content:
                pass
            else:
                return False

        return output_dir

    except Exception:
        return False


def test_database_migration():
    """Test database migration functionality."""

    # First generate a mock server to get the directory
    mock_dir = test_mock_generation()
    if not mock_dir:
        return False

    # Simulate database path
    db_path = mock_dir / "db" / "request_logs.db"
    db_path.parent.mkdir(exist_ok=True)

    try:
        # Test migration status
        migrator = DatabaseMigrator(str(db_path))

        # Get initial status
        status = migrator.get_migration_status()

        # Apply migrations
        if status["needs_migration"]:
            success = migrator.apply_migrations()
            if success:
                pass
            else:
                return False

        # Check final status
        migrator.get_migration_status()

        # Test backup functionality
        backup_path = migrator.backup_database()
        if Path(backup_path).exists():
            pass
        else:
            return False

        return True

    except Exception:
        return False


def test_log_analyzer_integration():
    """Test LogAnalyzer integration."""

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
                "test_scenario": "user_list_test",
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
                "test_scenario": "user_detail_test",
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
                "test_scenario": "user_create_error_test",
            },
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
            "insights",
        ]

        for key in expected_keys:
            if key in analysis:
                pass
            else:
                return False

        # Test filtering
        filtered_logs = analyzer.filter_logs(
            sample_logs, method="GET", include_admin=False
        )

        if len(filtered_logs) == 2:  # Should filter to only GET requests
            pass
        else:
            return False

        # Test quick analysis function
        quick_result = quick_analyze(sample_logs)
        if "total_requests" in quick_result:
            pass
        else:
            return False

        return True

    except Exception:
        return False


def main():
    """Run all Phase 1 integration tests."""

    # Test 1: Mock generation with new features
    mock_dir = test_mock_generation()
    if not mock_dir:
        return False

    # Test 2: Database migration
    if not test_database_migration(mock_dir):
        return False

    # Test 3: LogAnalyzer integration
    return test_log_analyzer_integration()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
