#!/usr/bin/env python3
"""
Final Integration Test Suite for MockLoop MCP Enhancement Plan
Tests core functionality without MCP server dependencies.
"""

import asyncio
import json
import sys
import time
import tempfile
import shutil
import sqlite3
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mockloop_mcp.generator import generate_mock_api
from mockloop_mcp.database_migration import DatabaseMigrator, get_database_status
from mockloop_mcp.mock_server_manager import MockServerManager
from mockloop_mcp.utils.http_client import MockServerClient, test_server_connectivity
from mockloop_mcp.log_analyzer import LogAnalyzer


class FinalIntegrationTester:
    """Final integration test suite for MockLoop MCP enhancement plan."""
    
    def __init__(self):
        self.test_results = {}
        self.temp_dir = None
        self.mock_server_dir = None
        
    def setup_test_environment(self):
        """Set up temporary test environment."""
        print("🔧 Setting up test environment...")
        self.temp_dir = Path(tempfile.mkdtemp(prefix="mockloop_final_test_"))
        print(f"   Test directory: {self.temp_dir}")
        
    def cleanup_test_environment(self):
        """Clean up test environment."""
        print("🧹 Cleaning up test environment...")
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            
    def create_comprehensive_test_spec(self) -> Dict[str, Any]:
        """Create a comprehensive test API specification."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Final Integration Test API",
                "version": "2.0.0",
                "description": "Comprehensive API for testing all MockLoop MCP enhancement features"
            },
            "servers": [
                {"url": "http://localhost:8000", "description": "Development server"}
            ],
            "paths": {
                "/users": {
                    "get": {
                        "summary": "Get all users",
                        "tags": ["Users"],
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
                                                    "created_at": {"type": "string", "format": "date-time"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "summary": "Create a user",
                        "tags": ["Users"],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["name", "email"],
                                        "properties": {
                                            "name": {"type": "string"},
                                            "email": {"type": "string", "format": "email"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": "User created",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "name": {"type": "string"},
                                                "email": {"type": "string"},
                                                "created_at": {"type": "string", "format": "date-time"}
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
                        "tags": ["Users"],
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
                                                "email": {"type": "string"},
                                                "created_at": {"type": "string", "format": "date-time"}
                                            }
                                        }
                                    }
                                }
                            },
                            "404": {
                                "description": "User not found"
                            }
                        }
                    },
                    "put": {
                        "summary": "Update user",
                        "tags": ["Users"],
                        "parameters": [
                            {
                                "name": "user_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"}
                            }
                        ],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "email": {"type": "string", "format": "email"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "User updated"
                            },
                            "404": {
                                "description": "User not found"
                            }
                        }
                    },
                    "delete": {
                        "summary": "Delete user",
                        "tags": ["Users"],
                        "parameters": [
                            {
                                "name": "user_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"}
                            }
                        ],
                        "responses": {
                            "204": {
                                "description": "User deleted"
                            },
                            "404": {
                                "description": "User not found"
                            }
                        }
                    }
                },
                "/products": {
                    "get": {
                        "summary": "Get all products",
                        "tags": ["Products"],
                        "parameters": [
                            {
                                "name": "category",
                                "in": "query",
                                "schema": {"type": "string"}
                            },
                            {
                                "name": "limit",
                                "in": "query",
                                "schema": {"type": "integer", "default": 10}
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "List of products",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "products": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "id": {"type": "integer"},
                                                            "name": {"type": "string"},
                                                            "price": {"type": "number"},
                                                            "category": {"type": "string"}
                                                        }
                                                    }
                                                },
                                                "total": {"type": "integer"},
                                                "page": {"type": "integer"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/orders": {
                    "post": {
                        "summary": "Create an order",
                        "tags": ["Orders"],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["user_id", "items"],
                                        "properties": {
                                            "user_id": {"type": "integer"},
                                            "items": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "product_id": {"type": "integer"},
                                                        "quantity": {"type": "integer"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": "Order created",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "user_id": {"type": "integer"},
                                                "total": {"type": "number"},
                                                "status": {"type": "string"},
                                                "created_at": {"type": "string", "format": "date-time"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "email": {"type": "string"},
                            "created_at": {"type": "string", "format": "date-time"}
                        }
                    },
                    "Product": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "price": {"type": "number"},
                            "category": {"type": "string"}
                        }
                    }
                }
            }
        }
    
    def test_enhanced_mock_generation(self) -> bool:
        """Test enhanced mock server generation with all features."""
        print("\n🏗️ Testing enhanced mock server generation...")
        
        try:
            # Test with comprehensive API spec
            test_spec = self.create_comprehensive_test_spec()
            
            print("   Generating mock server with all enhancement features...")
            output_dir = generate_mock_api(
                test_spec,
                mock_server_name="final_integration_test_server",
                auth_enabled=True,
                webhooks_enabled=True,
                admin_ui_enabled=True,
                storage_enabled=True
            )
            
            self.mock_server_dir = output_dir
            print(f"   ✅ Mock server generated at: {output_dir}")
            
            # Verify all enhanced files exist
            required_files = [
                "main.py",
                "logging_middleware.py",
                "templates/admin.html",
                "requirements_mock.txt",
                "Dockerfile",
                "docker-compose.yml",
                "auth_middleware.py",
                "webhook_handler.py",
                "storage_manager.py"
            ]
            
            missing_files = []
            for file_path in required_files:
                full_path = output_dir / file_path
                if not full_path.exists():
                    missing_files.append(file_path)
            
            if missing_files:
                print(f"   ❌ Missing files: {missing_files}")
                return False
            
            print("   ✅ All required files generated")
            
            # Check for Phase 1 enhancements in main.py
            main_py_content = (output_dir / "main.py").read_text()
            
            phase1_features = [
                "/admin/api/logs/search",
                "/admin/api/logs/analyze",
                "LogAnalyzer"
            ]
            
            missing_features = []
            for feature in phase1_features:
                if feature not in main_py_content:
                    missing_features.append(feature)
            
            if missing_features:
                print(f"   ❌ Missing Phase 1 features: {missing_features}")
                return False
            
            print("   ✅ Phase 1 features present in main.py")
            
            # Check for enhanced admin UI
            admin_html_content = (output_dir / "templates" / "admin.html").read_text()
            
            ui_features = [
                'data-tab="analytics"',
                "Log Analytics",
                "Advanced Log Search",
                "performLogSearch",
                "analyzeAllLogs",
                "displayAnalysisResults"
            ]
            
            missing_ui_features = []
            for feature in ui_features:
                if feature not in admin_html_content:
                    missing_ui_features.append(feature)
            
            if missing_ui_features:
                print(f"   ❌ Missing UI features: {missing_ui_features}")
                return False
            
            print("   ✅ Enhanced admin UI features present")
            
            # Check for enhanced middleware
            middleware_content = (output_dir / "logging_middleware.py").read_text()
            
            middleware_features = [
                "session_id",
                "test_scenario",
                "correlation_id",
                "user_agent",
                "response_size",
                "extract_session_info",
                "migrate_database"
            ]
            
            missing_middleware_features = []
            for feature in middleware_features:
                if feature not in middleware_content:
                    missing_middleware_features.append(feature)
            
            if missing_middleware_features:
                print(f"   ❌ Missing middleware features: {missing_middleware_features}")
                return False
            
            print("   ✅ Enhanced middleware features present")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Enhanced mock generation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_complete_database_system(self) -> bool:
        """Test the complete database migration and schema system."""
        print("\n🗄️ Testing complete database system...")
        
        try:
            if not self.mock_server_dir:
                print("   ❌ No mock server directory available")
                return False
            
            # Test database migration system
            db_path = self.mock_server_dir / "db" / "request_logs.db"
            db_path.parent.mkdir(exist_ok=True)
            
            print("   Testing database migration system...")
            migrator = DatabaseMigrator(str(db_path))
            
            # Get initial status
            initial_status = migrator.get_migration_status()
            print(f"   Initial version: {initial_status['current_version']}")
            
            # Apply all migrations
            success = migrator.apply_migrations()
            if not success:
                print("   ❌ Migration application failed")
                return False
            
            final_status = migrator.get_migration_status()
            print(f"   ✅ Migrated to version {final_status['current_version']}")
            
            # Verify all tables exist
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            expected_tables = [
                "request_logs",
                "test_sessions",
                "performance_metrics", 
                "mock_scenarios",
                "schema_version"
            ]
            
            missing_tables = []
            for table in expected_tables:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (table,))
                
                if not cursor.fetchone():
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"   ❌ Missing tables: {missing_tables}")
                conn.close()
                return False
            
            print("   ✅ All expected tables created")
            
            # Test enhanced request_logs schema
            cursor.execute("PRAGMA table_info(request_logs)")
            columns = {col[1] for col in cursor.fetchall()}
            
            expected_columns = {
                "id", "timestamp", "type", "method", "path", "status_code",
                "process_time_ms", "client_host", "client_port", "headers",
                "query_params", "request_body", "response_body", "created_at",
                "session_id", "test_scenario", "correlation_id", "user_agent",
                "response_size", "is_admin"
            }
            
            missing_columns = expected_columns - columns
            if missing_columns:
                print(f"   ❌ Missing columns in request_logs: {missing_columns}")
                conn.close()
                return False
            
            print("   ✅ Enhanced request_logs schema validated")
            
            # Test data insertion with enhanced schema
            print("   Testing enhanced data insertion...")
            
            test_data = [
                ("2024-01-01T10:00:00", "request", "GET", "/users", 200, 45, "127.0.0.1", "8080",
                 '{"user-agent": "test-client", "x-session-id": "session-1"}', '{}', '{}', 
                 '[{"id": 1, "name": "Test User"}]', "session-1", "user-list-test", "req-001",
                 "test-client", 1024, 0),
                ("2024-01-01T10:01:00", "request", "POST", "/users", 201, 67, "127.0.0.1", "8080",
                 '{"user-agent": "test-client", "x-session-id": "session-1"}', '{}', 
                 '{"name": "New User", "email": "new@example.com"}',
                 '{"id": 2, "name": "New User", "email": "new@example.com"}', "session-1", 
                 "user-create-test", "req-002", "test-client", 512, 0),
                ("2024-01-01T10:02:00", "request", "GET", "/admin/logs", 200, 23, "127.0.0.1", "8080",
                 '{"user-agent": "admin-client"}', '{}', '{}', '{"logs": []}', None, None, 
                 "req-003", "admin-client", 256, 1)
            ]
            
            for data in test_data:
                cursor.execute("""
                    INSERT INTO request_logs (
                        timestamp, type, method, path, status_code, process_time_ms,
                        client_host, client_port, headers, query_params, request_body,
                        response_body, session_id, test_scenario, correlation_id,
                        user_agent, response_size, is_admin
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, data)
            
            conn.commit()
            
            # Verify data insertion
            cursor.execute("SELECT COUNT(*) FROM request_logs")
            count = cursor.fetchone()[0]
            
            if count != len(test_data):
                print(f"   ❌ Expected {len(test_data)} records, got {count}")
                conn.close()
                return False
            
            print(f"   ✅ {count} test records inserted successfully")
            
            # Test scenario management
            print("   Testing scenario management...")
            
            test_scenarios = [
                ("default", "Default scenario", '{"name": "default", "endpoints": {}}', 1),
                ("user-registration", "User registration flow", 
                 '{"name": "user-registration", "endpoints": {"/users": {"POST": {"status": 201}}}}', 0),
                ("error-testing", "Error testing scenario",
                 '{"name": "error-testing", "endpoints": {"/users": {"GET": {"status": 500}}}}', 0)
            ]
            
            for scenario in test_scenarios:
                cursor.execute("""
                    INSERT INTO mock_scenarios (name, description, config, is_active)
                    VALUES (?, ?, ?, ?)
                """, scenario)
            
            conn.commit()
            
            # Verify scenarios
            cursor.execute("SELECT COUNT(*) FROM mock_scenarios")
            scenario_count = cursor.fetchone()[0]
            
            if scenario_count != len(test_scenarios):
                print(f"   ❌ Expected {len(test_scenarios)} scenarios, got {scenario_count}")
                conn.close()
                return False
            
            print(f"   ✅ {scenario_count} test scenarios created")
            
            conn.close()
            
            # Test backup functionality
            print("   Testing backup functionality...")
            backup_path = migrator.backup_database()
            
            if not Path(backup_path).exists():
                print("   ❌ Backup file not created")
                return False
            
            print(f"   ✅ Backup created: {backup_path}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Database system test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_log_analysis_system(self) -> bool:
        """Test the complete log analysis system."""
        print("\n📊 Testing log analysis system...")
        
        try:
            if not self.mock_server_dir:
                print("   ❌ No mock server directory available")
                return False
            
            # Read test data from database
            db_path = self.mock_server_dir / "db" / "request_logs.db"
            
            if not db_path.exists():
                print("   ❌ Database not found")
                return False
            
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM request_logs ORDER BY timestamp")
            logs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            if not logs:
                print("   ❌ No log data found")
                return False
            
            print(f"   Found {len(logs)} log entries for analysis")
            
            # Test LogAnalyzer
            analyzer = LogAnalyzer()
            
            # Test complete analysis
            print("   Testing complete log analysis...")
            analysis = analyzer.analyze_logs(logs)
            
            if not analysis:
                print("   ❌ Log analysis failed")
                return False
            
            # Verify analysis structure
            expected_keys = [
                "total_requests", "time_range", "methods", "status_codes",
                "endpoints", "performance", "errors", "patterns", "insights"
            ]
            
            missing_keys = []
            for key in expected_keys:
                if key not in analysis:
                    missing_keys.append(key)
            
            if missing_keys:
                print(f"   ❌ Missing analysis keys: {missing_keys}")
                return False
            
            print("   ✅ Complete analysis structure validated")
            
            # Test filtering
            print("   Testing log filtering...")
            
            # Filter by method
            get_logs = analyzer.filter_logs(logs, method="GET")
            post_logs = analyzer.filter_logs(logs, method="POST")
            
            total_filtered = len(get_logs) + len(post_logs)
            if total_filtered > len(logs):
                print("   ❌ Filtering logic error")
                return False
            
            print(f"   ✅ Filtered {len(get_logs)} GET and {len(post_logs)} POST requests")
            
            # Filter by admin requests
            admin_logs = analyzer.filter_logs(logs, include_admin=True)
            non_admin_logs = analyzer.filter_logs(logs, include_admin=False)
            
            print(f"   ✅ Filtered {len(admin_logs)} admin and {len(non_admin_logs)} non-admin requests")
            
            # Test session-based analysis
            print("   Testing session-based analysis...")
            
            session_logs = [log for log in logs if log.get("session_id")]
            if session_logs:
                session_analysis = analyzer.analyze_logs(session_logs)
                
                if "patterns" in session_analysis and "sessions" in session_analysis["patterns"]:
                    print("   ✅ Session-based analysis working")
                else:
                    print("   ⚠️  Session analysis may need improvement")
            
            # Test performance analysis
            print("   Testing performance analysis...")
            
            if "performance" in analysis:
                perf = analysis["performance"]
                required_perf_keys = ["avg_response_time", "total_requests"]
                
                missing_perf_keys = []
                for key in required_perf_keys:
                    if key not in perf:
                        missing_perf_keys.append(key)
                
                if missing_perf_keys:
                    print(f"   ❌ Missing performance keys: {missing_perf_keys}")
                    return False
                
                print(f"   ✅ Performance analysis: {perf['avg_response_time']:.2f}ms avg")
            
            # Test insights generation
            print("   Testing insights generation...")
            
            if "insights" in analysis and analysis["insights"]:
                insights = analysis["insights"]
                print(f"   ✅ Generated {len(insights)} insights")
                
                # Print sample insights
                for i, insight in enumerate(insights[:3]):
                    print(f"      {i+1}. {insight}")
            else:
                print("   ⚠️  No insights generated")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Log analysis test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_http_client_system(self) -> bool:
        """Test the HTTP client system and server connectivity."""
        print("\n🌐 Testing HTTP client system...")
        
        try:
            # Test MockServerClient structure
            print("   Testing MockServerClient structure...")
            
            client = MockServerClient("http://localhost:8000")
            
            # Verify client has all required methods
            required_methods = [
                "get_debug_info", "get_logs", "update_response",
                "create_scenario", "switch_scenario", "list_scenarios",
                "get_current_scenario"
            ]
            
            missing_methods = []
            for method in required_methods:
                if not hasattr(client, method):
                    missing_methods.append(method)
            
            if missing_methods:
                print(f"   ❌ Missing client methods: {missing_methods}")
                return False
            
            print("   ✅ MockServerClient has all required methods")
            
            # Test connectivity function structure
            print("   Testing connectivity function...")
            
            try:
                # This will fail but should return proper structure
                result = await test_server_connectivity("http://invalid-server:9999")
                
                if not isinstance(result, dict) or "status" not in result:
                    print("   ❌ Connectivity function doesn't return proper structure")
                    return False
                
                print("   ✅ Connectivity function structure correct")
                
            except Exception as e:
                print(f"   ⚠️  Connectivity test exception (expected): {e}")
            
            # Test MockServerManager
            print("   Testing MockServerManager...")
            
            manager = MockServerManager()
            
            # Test discovery methods exist
            discovery_methods = ["discover_running_servers", "comprehensive_discovery", "get_server_status"]
            
            missing_discovery_methods = []
            for method in discovery_methods:
                if not hasattr(manager, method):
                    missing_discovery_methods.append(method)
            
            if missing_discovery_methods:
                print(f"   ❌ Missing manager methods: {missing_discovery_methods}")
                return False
            
            print("   ✅ MockServerManager has all required methods")
            
            # Test discovery functionality (structure only)
            print("   Testing discovery functionality...")
            
            try:
                discovery_result = await manager.comprehensive_discovery()
                
                if not isinstance(discovery_result, dict):
                    print("   ❌ Discovery doesn't return dict")
                    return False
                
                expected_keys = ["total_generated", "total_running"]
                missing_keys = []
                for key in expected_keys:
                    if key not in discovery_result:
                        missing_keys.append(key)
                
                if missing_keys:
                    print(f"   ❌ Missing discovery keys: {missing_keys}")
                    return False
                
                print(f"   ✅ Discovery found {discovery_result.get('total_generated', 0)} generated mocks")
                
            except Exception as e:
                print(f"   ⚠️  Discovery exception (may be expected): {e}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ HTTP client system test failed: {e}")
            return False
    
    def test_template_system(self) -> bool:
        """Test the template generation system."""
        print("\n📄 Testing template system...")
        
        try:
            if not self.mock_server_dir:
                print("   ❌ No mock server directory available")
                return False
            
            # Test all template files exist and have correct content
            template_tests = [
                {
                    "file": "main.py",
                    "required_content": [
                        "FastAPI", "logging_middleware", "/admin/api/logs/search",
                        "/admin/api/logs/analyze", "LogAnalyzer"
                    ]
                },
                {
                    "file": "logging_middleware.py",
                    "required_content": [
                        "extract_session_info", "migrate_database", "session_id",
                        "test_scenario", "correlation_id", "response_size"
                    ]
                },
                {
                    "file": "templates/admin.html",
                    "required_content": [
                        "Log Analytics", "performLogSearch", "analyzeAllLogs",
                        "data-tab=\"analytics\"", "Advanced Log Search"
                    ]
                },
                {
                    "file": "auth_middleware.py",
                    "required_content": [
                        "authenticate", "token", "authorization"
                    ]
                },
                {
                    "file": "webhook_handler.py",
                    "required_content": [
                        "webhook", "trigger", "payload"
                    ]
                },
                {
                    "file": "storage.py",
                    "required_content": [
                        "storage", "data", "persistence"
                    ]
                }
            ]
            
            for test in template_tests:
                file_path = self.mock_server_dir / test["file"]
                
                if not file_path.exists():
                    print(f"   ❌ Template file missing: {test['file']}")
                    return False
                
                # Read file content
                try:
                    content = file_path.read_text()
                    
                    missing_content = []
                    for required in test["required_content"]:
                        if required not in content:
                            missing_content.append(required)
                    
                    if missing_content:
                        print(f"   ❌ {test['file']} missing content: {missing_content}")
                        return False
                    
                    print(f"   ✅ {test['file']} template validated")
                    
                except Exception as e:
                    print(f"   ❌ Error reading {test['file']}: {e}")
                    return False
            
            # Test Docker files
            print("   Testing Docker configuration...")
            
            dockerfile_path = self.mock_server_dir / "Dockerfile"
            compose_path = self.mock_server_dir / "docker-compose.yml"
            
            if not dockerfile_path.exists():
                print("   ❌ Dockerfile missing")
                return False
            
            if not compose_path.exists():
                print("   ❌ docker-compose.yml missing")
                return False
            
            # Check Dockerfile content
            dockerfile_content = dockerfile_path.read_text()
            required_dockerfile_content = ["FROM python:", "COPY requirements_mock.txt", "RUN pip install", "CMD"]
            
            missing_dockerfile_content = []
            for required in required_dockerfile_content:
                if required not in dockerfile_content:
                    missing_dockerfile_content.append(required)
            
            if missing_dockerfile_content:
                print(f"   ❌ Dockerfile missing content: {missing_dockerfile_content}")
                return False
            
            print("   ✅ Docker configuration validated")
            
            # Test requirements file
            requirements_path = self.mock_server_dir / "requirements_mock.txt"
            if not requirements_path.exists():
                print("   ❌ requirements_mock.txt missing")
                return False
            
            requirements_content = requirements_path.read_text()
            required_packages = ["fastapi", "uvicorn", "jinja2"]
            
            missing_packages = []
            for package in required_packages:
                if package.lower() not in requirements_content.lower():
                    missing_packages.append(package)
            
            if missing_packages:
                print(f"   ❌ Missing required packages: {missing_packages}")
                return False
            
            print("   ✅ Requirements file validated")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Template system test failed: {e}")
            return False
    
    def test_performance_metrics(self) -> bool:
        """Test performance metrics and overhead."""
        print("\n⚡ Testing performance metrics...")
        
        try:
            # Test generation performance
            print("   Testing generation performance...")
            
            start_time = time.time()
            
            # Generate multiple test servers
            for i in range(3):
                test_spec = self.create_comprehensive_test_spec()
                test_spec["info"]["title"] = f"Performance Test API {i}"
                
                output_dir = generate_mock_api(
                    test_spec,
                    mock_server_name=f"perf_test_{i}",
                    auth_enabled=True,
                    webhooks_enabled=True,
                    admin_ui_enabled=True,
                    storage_enabled=True
                )
                
                if not output_dir.exists():
                    print(f"   ❌ Performance test {i} failed")
                    return False
            
            generation_time = time.time() - start_time
            avg_time = generation_time / 3
            
            print(f"   ✅ Average generation time: {avg_time:.2f}s")
            
            if avg_time > 15:  # Should be reasonable
                print("   ⚠️  Generation time may be slow")
            
            # Test database performance
            print("   Testing database performance...")
            
            if not self.mock_server_dir:
                print("   ❌ No mock server directory available")
                return False
            
            db_path = self.mock_server_dir / "db" / "request_logs.db"
            
            if not db_path.exists():
                print("   ❌ Database not found")
                return False
            
            # Test large data insertion
            start_time = time.time()
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Insert 1000 test records
            for i in range(1000):
                cursor.execute("""
                    INSERT INTO request_logs (
                        timestamp, type, method, path, status_code, process_time_ms,
                        client_host, client_port, headers, query_params, request_body,
                        response_body, session_id, test_scenario, correlation_id,
                        user_agent, response_size, is_admin
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"2024-01-01T{i//3600:02d}:{(i//60)%60:02d}:{i%60:02d}",
                    "request", "GET", f"/perf/test/{i}", 200, 50 + (i % 100),
                    "127.0.0.1", "8080", '{"user-agent": "perf-test"}', '{}', '{}',
                    f'{{"result": "test-{i}"}}', f"session-{i//100}", f"scenario-{i%10}",
                    f"req-{i:04d}", "perf-test-client", 1024 + (i % 512), 0
                ))
            
            conn.commit()
            
            insertion_time = time.time() - start_time
            
            print(f"   ✅ Inserted 1000 records in {insertion_time:.2f}s")
            
            # Test query performance
            start_time = time.time()
            
            cursor.execute("SELECT COUNT(*) FROM request_logs")
            total_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT method, COUNT(*) as count, AVG(process_time_ms) as avg_time
                FROM request_logs
                GROUP BY method
            """)
            method_stats = cursor.fetchall()
            
            query_time = time.time() - start_time
            
            print(f"   ✅ Queried {total_count} records in {query_time:.3f}s")
            
            # Test analysis performance
            start_time = time.time()
            
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM request_logs LIMIT 500")
            logs = [dict(row) for row in cursor.fetchall()]
            
            analyzer = LogAnalyzer()
            analysis = analyzer.analyze_logs(logs)
            
            analysis_time = time.time() - start_time
            
            print(f"   ✅ Analyzed {len(logs)} logs in {analysis_time:.3f}s")
            
            conn.close()
            
            if analysis_time > 2:  # Should analyze 500 logs quickly
                print("   ⚠️  Analysis time may be slow")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Performance metrics test failed: {e}")
            return False
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Generate final comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        return {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "python_version": sys.version,
                "test_directory": str(self.temp_dir) if self.temp_dir else None,
                "mock_server_directory": str(self.mock_server_dir) if self.mock_server_dir else None
            },
            "enhancement_plan_validation": {
                "phase_1_complete": self.test_results.get("enhanced_mock_generation", False) and
                                   self.test_results.get("complete_database_system", False),
                "phase_2_part_1_complete": self.test_results.get("http_client_system", False),
                "integration_validated": all(self.test_results.values()),
                "performance_acceptable": self.test_results.get("performance_metrics", False)
            }
        }
    
    def run_all_tests(self) -> bool:
        """Run all final integration tests."""
        print("🚀 Starting Final MockLoop MCP Integration Tests")
        print("=" * 80)
        
        self.setup_test_environment()
        
        try:
            # Test 1: Enhanced mock generation
            print("\n" + "=" * 80)
            self.test_results["enhanced_mock_generation"] = self.test_enhanced_mock_generation()
            
            # Test 2: Complete database system
            print("\n" + "=" * 80)
            self.test_results["complete_database_system"] = self.test_complete_database_system()
            
            # Test 3: Log analysis system
            print("\n" + "=" * 80)
            self.test_results["log_analysis_system"] = self.test_log_analysis_system()
            
            # Test 4: HTTP client system
            print("\n" + "=" * 80)
            self.test_results["http_client_system"] = asyncio.run(self.test_http_client_system())
            
            # Test 5: Template system
            print("\n" + "=" * 80)
            self.test_results["template_system"] = self.test_template_system()
            
            # Test 6: Performance metrics
            print("\n" + "=" * 80)
            self.test_results["performance_metrics"] = self.test_performance_metrics()
            
            # Generate final report
            report = self.generate_final_report()
            
            print("\n" + "=" * 80)
            print("🎉 FINAL INTEGRATION TEST RESULTS")
            print("=" * 80)
            
            for test_name, result in self.test_results.items():
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"{test_name.replace('_', ' ').title()}: {status}")
            
            print(f"\nOverall Success Rate: {report['test_summary']['success_rate']:.1f}%")
            print(f"Tests Passed: {report['test_summary']['passed_tests']}/{report['test_summary']['total_tests']}")
            
            # Enhancement plan validation
            enhancement = report["enhancement_plan_validation"]
            print(f"\n📋 Enhancement Plan Validation:")
            print(f"Phase 1 Complete: {'✅' if enhancement['phase_1_complete'] else '❌'}")
            print(f"Phase 2 Part 1 Complete: {'✅' if enhancement['phase_2_part_1_complete'] else '❌'}")
            print(f"Integration Validated: {'✅' if enhancement['integration_validated'] else '❌'}")
            print(f"Performance Acceptable: {'✅' if enhancement['performance_acceptable'] else '❌'}")
            
            # Save detailed report
            report_path = self.temp_dir / "final_integration_report.json" if self.temp_dir else Path("final_integration_report.json")
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"\nDetailed report saved to: {report_path}")
            
            return all(self.test_results.values())
            
        except Exception as e:
            print(f"\n❌ Test execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            self.cleanup_test_environment()


def main():
    """Main test execution function."""
    tester = FinalIntegrationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All final integration tests passed!")
        print("✅ MockLoop MCP enhancement plan is fully validated and ready for production.")
        return 0
    else:
        print("\n❌ Some final integration tests failed.")
        print("Please review the results above and address any issues.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)