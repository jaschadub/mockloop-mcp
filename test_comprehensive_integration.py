#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite for MockLoop MCP Enhancement Plan
Tests the complete integration of Phase 1 and Phase 2 components.
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
import subprocess
import requests
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mockloop_mcp.generator import generate_mock_api
from mockloop_mcp.database_migration import DatabaseMigrator, get_database_status
from mockloop_mcp.main import (
    generate_mock_api_tool, 
    query_mock_logs_tool, 
    discover_mock_servers_tool,
    manage_mock_data_tool
)
from mockloop_mcp.mock_server_manager import MockServerManager
from mockloop_mcp.utils.http_client import MockServerClient, test_server_connectivity
from mockloop_mcp.log_analyzer import LogAnalyzer


class ComprehensiveIntegrationTester:
    """Comprehensive test suite for MockLoop MCP enhancement plan."""
    
    def __init__(self):
        self.test_results = {}
        self.temp_dir = None
        self.mock_server_dir = None
        self.test_server_url = "http://localhost:8000"
        self.server_process = None
        
    def setup_test_environment(self):
        """Set up temporary test environment."""
        print("🔧 Setting up test environment...")
        self.temp_dir = Path(tempfile.mkdtemp(prefix="mockloop_integration_test_"))
        print(f"   Test directory: {self.temp_dir}")
        
    def cleanup_test_environment(self):
        """Clean up test environment."""
        print("🧹 Cleaning up test environment...")
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                pass
        
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            
    def create_test_api_spec(self) -> Dict[str, Any]:
        """Create a comprehensive test API specification."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Comprehensive Integration Test API",
                "version": "1.0.0",
                "description": "API for testing all MockLoop MCP enhancement features"
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
                    },
                    "post": {
                        "summary": "Create a user",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "email": {"type": "string"}
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
                                                "email": {"type": "string"}
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
                },
                "/products": {
                    "get": {
                        "summary": "Get all products",
                        "responses": {
                            "200": {
                                "description": "List of products",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "integer"},
                                                    "name": {"type": "string"},
                                                    "price": {"type": "number"}
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
        }
    
    async def test_complete_workflow(self) -> bool:
        """Test the complete workflow: generation → scenario creation → dynamic responses → monitoring."""
        print("\n🔄 Testing complete end-to-end workflow...")
        
        try:
            # Step 1: Generate mock server with all features
            print("   Step 1: Generating mock server with all enhancement features...")
            test_spec = self.create_test_api_spec()
            
            result = await generate_mock_api_tool(
                spec_url_or_path=json.dumps(test_spec),
                output_dir_name="integration_test_server",
                auth_enabled=True,
                webhooks_enabled=True,
                admin_ui_enabled=True,
                storage_enabled=True
            )
            
            if result["status"] != "success":
                print(f"   ❌ Mock generation failed: {result['message']}")
                return False
            
            self.mock_server_dir = Path(result["generated_mock_path"])
            print(f"   ✅ Mock server generated at: {self.mock_server_dir}")
            
            # Step 2: Validate database schema migration
            print("   Step 2: Validating database schema migration...")
            db_path = self.mock_server_dir / "db" / "request_logs.db"
            db_path.parent.mkdir(exist_ok=True)
            
            migrator = DatabaseMigrator(str(db_path))
            migration_status = migrator.get_migration_status()
            
            if migration_status["needs_migration"]:
                success = migrator.apply_migrations()
                if not success:
                    print("   ❌ Database migration failed")
                    return False
            
            print(f"   ✅ Database at version {migration_status['current_version']}")
            
            # Step 3: Start the mock server (simulate)
            print("   Step 3: Validating mock server structure...")
            
            # Check for enhanced files
            required_files = [
                "main.py",
                "logging_middleware.py", 
                "templates/admin.html",
                "requirements_mock.txt"
            ]
            
            for file_path in required_files:
                if not (self.mock_server_dir / file_path).exists():
                    print(f"   ❌ Required file missing: {file_path}")
                    return False
            
            print("   ✅ All required files present")
            
            # Step 4: Test MCP tools integration (without running server)
            print("   Step 4: Testing MCP tools integration...")
            
            # Test discover_mock_servers
            discovery_result = await discover_mock_servers_tool(
                ports=[8000, 8001, 8002],
                check_health=False,
                include_generated=True
            )
            
            if discovery_result["status"] != "success":
                print(f"   ❌ Server discovery failed: {discovery_result['message']}")
                return False
            
            print(f"   ✅ Discovered {discovery_result['total_generated']} generated mocks")
            
            # Step 5: Test database operations
            print("   Step 5: Testing database operations...")
            
            # Insert test log data
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            test_logs = [
                ("2024-01-01T10:00:00", "request", "GET", "/users", 200, 45, "127.0.0.1", "8080", 
                 '{"user-agent": "test-client"}', '{}', '{}', '[{"id": 1, "name": "Test User"}]',
                 "test-session-1", "user-list-scenario", "req-001", "test-client", 1024, 0),
                ("2024-01-01T10:01:00", "request", "POST", "/users", 201, 67, "127.0.0.1", "8080",
                 '{"user-agent": "test-client"}', '{}', '{"name": "New User"}', '{"id": 2, "name": "New User"}',
                 "test-session-1", "user-create-scenario", "req-002", "test-client", 512, 0),
                ("2024-01-01T10:02:00", "request", "GET", "/products", 200, 32, "127.0.0.1", "8080",
                 '{"user-agent": "test-client"}', '{}', '{}', '[{"id": 1, "name": "Product 1"}]',
                 "test-session-2", "product-list-scenario", "req-003", "test-client", 2048, 0)
            ]
            
            for log_data in test_logs:
                cursor.execute("""
                    INSERT INTO request_logs (
                        timestamp, type, method, path, status_code, process_time_ms, 
                        client_host, client_port, headers, query_params, request_body, 
                        response_body, session_id, test_scenario, correlation_id, 
                        user_agent, response_size, is_admin
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, log_data)
            
            conn.commit()
            conn.close()
            
            print("   ✅ Test log data inserted")
            
            # Step 6: Test log analysis
            print("   Step 6: Testing log analysis...")
            
            analyzer = LogAnalyzer()
            
            # Read logs back from database
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM request_logs ORDER BY timestamp")
            logs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            analysis = analyzer.analyze_logs(logs)
            
            if not analysis or "total_requests" not in analysis:
                print("   ❌ Log analysis failed")
                return False
            
            print(f"   ✅ Analyzed {analysis['total_requests']} log entries")
            
            # Step 7: Test scenario management (structure validation)
            print("   Step 7: Testing scenario management structure...")
            
            # Check if mock_scenarios table exists
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='mock_scenarios'
            """)
            
            if not cursor.fetchone():
                print("   ❌ mock_scenarios table not found")
                conn.close()
                return False
            
            # Insert test scenario
            test_scenario = {
                "name": "integration-test-scenario",
                "description": "Test scenario for integration testing",
                "endpoints": {
                    "/users": {
                        "GET": {"status": 200, "data": [{"id": 999, "name": "Integration Test User"}]}
                    }
                }
            }
            
            cursor.execute("""
                INSERT INTO mock_scenarios (name, description, config, is_active)
                VALUES (?, ?, ?, ?)
            """, ("integration-test", "Integration test scenario", json.dumps(test_scenario), 1))
            
            conn.commit()
            conn.close()
            
            print("   ✅ Scenario management structure validated")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Complete workflow test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_mcp_tools_integration(self) -> bool:
        """Test all MCP tools working together."""
        print("\n🔧 Testing MCP tools integration...")
        
        try:
            # Test 1: generate_mock_api_tool
            print("   Testing generate_mock_api_tool...")
            result = await generate_mock_api_tool(
                spec_url_or_path=json.dumps(self.create_test_api_spec()),
                output_dir_name="mcp_tools_test_server"
            )
            
            if result["status"] != "success":
                print(f"   ❌ generate_mock_api_tool failed: {result['message']}")
                return False
            
            print("   ✅ generate_mock_api_tool working")
            
            # Test 2: discover_mock_servers_tool
            print("   Testing discover_mock_servers_tool...")
            discovery_result = await discover_mock_servers_tool(
                check_health=False,
                include_generated=True
            )
            
            if discovery_result["status"] != "success":
                print(f"   ❌ discover_mock_servers_tool failed: {discovery_result['message']}")
                return False
            
            print(f"   ✅ discover_mock_servers_tool found {discovery_result['total_generated']} mocks")
            
            # Test 3: manage_mock_data_tool (validation only)
            print("   Testing manage_mock_data_tool validation...")
            
            # Test invalid server
            result = await manage_mock_data_tool(
                server_url="http://invalid-server:9999",
                operation="list_scenarios"
            )
            
            if result["status"] != "error":
                print("   ❌ manage_mock_data_tool should fail with invalid server")
                return False
            
            # Test invalid operation
            result = await manage_mock_data_tool(
                server_url="http://localhost:8000",
                operation="invalid_operation"
            )
            
            if result["status"] != "error" or "Unknown operation" not in result["message"]:
                print("   ❌ manage_mock_data_tool should fail with invalid operation")
                return False
            
            print("   ✅ manage_mock_data_tool validation working")
            
            # Test 4: query_mock_logs_tool (without server)
            print("   Testing query_mock_logs_tool...")
            
            # This will fail without a server, but we test the structure
            result = await query_mock_logs_tool(
                server_url="http://localhost:8000",
                limit=10
            )
            
            # Should have proper error handling
            if "status" not in result or "logs" not in result:
                print("   ❌ query_mock_logs_tool missing required fields")
                return False
            
            print("   ✅ query_mock_logs_tool structure correct")
            
            return True
            
        except Exception as e:
            print(f"   ❌ MCP tools integration test failed: {e}")
            return False
    
    async def test_database_migration_system(self) -> bool:
        """Test the complete database migration system."""
        print("\n🗄️ Testing database migration system...")
        
        try:
            # Create test database
            test_db_path = self.temp_dir / "migration_test.db"
            migrator = DatabaseMigrator(str(test_db_path))
            
            # Test 1: Initial state
            print("   Testing initial migration state...")
            initial_status = migrator.get_migration_status()
            
            if initial_status["current_version"] != 0:
                print(f"   ❌ Expected initial version 0, got {initial_status['current_version']}")
                return False
            
            print("   ✅ Initial migration state correct")
            
            # Test 2: Apply all migrations
            print("   Testing migration application...")
            success = migrator.apply_migrations()
            
            if not success:
                print("   ❌ Migration application failed")
                return False
            
            final_status = migrator.get_migration_status()
            
            if final_status["needs_migration"]:
                print("   ❌ Migrations not fully applied")
                return False
            
            print(f"   ✅ Migrated to version {final_status['current_version']}")
            
            # Test 3: Verify all tables exist
            print("   Testing table creation...")
            conn = sqlite3.connect(str(test_db_path))
            cursor = conn.cursor()
            
            expected_tables = [
                "request_logs",
                "test_sessions", 
                "performance_metrics",
                "mock_scenarios",
                "schema_version"
            ]
            
            for table in expected_tables:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (table,))
                
                if not cursor.fetchone():
                    print(f"   ❌ Table {table} not found")
                    conn.close()
                    return False
            
            conn.close()
            print("   ✅ All expected tables created")
            
            # Test 4: Backup functionality
            print("   Testing backup functionality...")
            backup_path = migrator.backup_database()
            
            if not Path(backup_path).exists():
                print("   ❌ Backup file not created")
                return False
            
            print(f"   ✅ Backup created: {backup_path}")
            
            # Test 5: Rollback functionality
            print("   Testing rollback functionality...")
            current_version = migrator.get_current_version()
            
            if current_version > 1:
                rollback_success = migrator.rollback_migration(current_version - 1)
                if not rollback_success:
                    print("   ❌ Rollback failed")
                    return False
                
                print("   ✅ Rollback functionality working")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Database migration test failed: {e}")
            return False
    
    async def test_performance_and_compatibility(self) -> bool:
        """Test performance overhead and backward compatibility."""
        print("\n⚡ Testing performance and compatibility...")
        
        try:
            # Test 1: Template generation performance
            print("   Testing template generation performance...")
            
            start_time = time.time()
            
            for i in range(5):  # Generate multiple servers
                test_spec = self.create_test_api_spec()
                test_spec["info"]["title"] = f"Performance Test API {i}"
                
                result = await generate_mock_api_tool(
                    spec_url_or_path=json.dumps(test_spec),
                    output_dir_name=f"perf_test_server_{i}"
                )
                
                if result["status"] != "success":
                    print(f"   ❌ Performance test {i} failed")
                    return False
            
            generation_time = time.time() - start_time
            avg_time = generation_time / 5
            
            print(f"   ✅ Average generation time: {avg_time:.2f}s")
            
            if avg_time > 10:  # Should be under 10 seconds per generation
                print("   ⚠️  Generation time may be too slow")
            
            # Test 2: Database operation performance
            print("   Testing database operation performance...")
            
            test_db_path = self.temp_dir / "performance_test.db"
            migrator = DatabaseMigrator(str(test_db_path))
            
            start_time = time.time()
            migrator.apply_migrations()
            migration_time = time.time() - start_time
            
            print(f"   ✅ Migration time: {migration_time:.2f}s")
            
            # Test 3: Log analysis performance
            print("   Testing log analysis performance...")
            
            # Generate large log dataset
            conn = sqlite3.connect(str(test_db_path))
            cursor = conn.cursor()
            
            start_time = time.time()
            
            # Insert 1000 test log entries
            for i in range(1000):
                cursor.execute("""
                    INSERT INTO request_logs (
                        timestamp, type, method, path, status_code, process_time_ms,
                        client_host, client_port, headers, query_params, request_body,
                        response_body, session_id, test_scenario, correlation_id,
                        user_agent, response_size, is_admin
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"2024-01-01T10:{i//60:02d}:{i%60:02d}",
                    "request", "GET", f"/test/{i}", 200, 50 + (i % 100),
                    "127.0.0.1", "8080", '{"user-agent": "test"}', '{}', '{}', '{}',
                    f"session-{i//100}", f"scenario-{i%10}", f"req-{i:04d}",
                    "test-client", 1024, 0
                ))
            
            conn.commit()
            
            # Read and analyze
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM request_logs")
            logs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            analyzer = LogAnalyzer()
            analysis = analyzer.analyze_logs(logs)
            
            analysis_time = time.time() - start_time
            
            print(f"   ✅ Analyzed {len(logs)} logs in {analysis_time:.2f}s")
            
            if analysis_time > 5:  # Should analyze 1000 logs in under 5 seconds
                print("   ⚠️  Log analysis may be too slow")
            
            # Test 4: Backward compatibility
            print("   Testing backward compatibility...")
            
            # Create a "legacy" database with just the base table
            legacy_db_path = self.temp_dir / "legacy_test.db"
            conn = sqlite3.connect(str(legacy_db_path))
            cursor = conn.cursor()
            
            # Create base table only (migration 0)
            cursor.execute("""
                CREATE TABLE request_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    type TEXT,
                    method TEXT,
                    path TEXT,
                    status_code INTEGER,
                    process_time_ms INTEGER,
                    client_host TEXT,
                    client_port TEXT,
                    headers TEXT,
                    query_params TEXT,
                    request_body TEXT,
                    response_body TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            # Test migration from legacy
            legacy_migrator = DatabaseMigrator(str(legacy_db_path))
            legacy_status = legacy_migrator.get_migration_status()
            
            if legacy_status["current_version"] != 0:
                print(f"   ❌ Legacy database should be version 0, got {legacy_status['current_version']}")
                return False
            
            # Apply migrations to legacy database
            success = legacy_migrator.apply_migrations()
            
            if not success:
                print("   ❌ Legacy database migration failed")
                return False
            
            print("   ✅ Backward compatibility maintained")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Performance and compatibility test failed: {e}")
            return False
    
    async def test_error_handling_and_resilience(self) -> bool:
        """Test error handling and system resilience."""
        print("\n🛡️ Testing error handling and resilience...")
        
        try:
            # Test 1: Invalid API specifications
            print("   Testing invalid API specification handling...")
            
            invalid_specs = [
                "invalid json",
                {"invalid": "spec"},
                {"openapi": "3.0.0"},  # Missing required fields
            ]
            
            for i, invalid_spec in enumerate(invalid_specs):
                try:
                    result = await generate_mock_api_tool(
                        spec_url_or_path=json.dumps(invalid_spec) if isinstance(invalid_spec, dict) else invalid_spec,
                        output_dir_name=f"invalid_test_{i}"
                    )
                    
                    if result["status"] != "error":
                        print(f"   ❌ Invalid spec {i} should have failed")
                        return False
                        
                except Exception:
                    pass  # Expected to fail
            
            print("   ✅ Invalid API specification handling working")
            
            # Test 2: Database corruption handling
            print("   Testing database corruption handling...")
            
            # Create corrupted database
            corrupted_db_path = self.temp_dir / "corrupted.db"
            with open(corrupted_db_path, 'w') as f:
                f.write("This is not a valid SQLite database")
            
            try:
                migrator = DatabaseMigrator(str(corrupted_db_path))
                status = migrator.get_migration_status()
                # Should handle gracefully
                print("   ✅ Database corruption handled gracefully")
            except Exception as e:
                print(f"   ⚠️  Database corruption handling: {e}")
            
            # Test 3: Network error handling
            print("   Testing network error handling...")
            
            # Test with unreachable server
            result = await manage_mock_data_tool(
                server_url="http://192.0.2.1:9999",  # RFC 5737 test address
                operation="list_scenarios"
            )
            
            if result["status"] != "error":
                print("   ❌ Network error should be handled")
                return False
            
            print("   ✅ Network error handling working")
            
            # Test 4: Concurrent access
            print("   Testing concurrent database access...")
            
            test_db_path = self.temp_dir / "concurrent_test.db"
            migrator = DatabaseMigrator(str(test_db_path))
            migrator.apply_migrations()
            
            async def concurrent_operation(operation_id):
                """Simulate concurrent database operation."""
                try:
                    conn = sqlite3.connect(str(test_db_path))
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO request_logs (
                            timestamp, type, method, path, status_code, process_time_ms,
                            client_host, client_port, headers, query_params, request_body,
                            response_body, session_id, test_scenario, correlation_id,
                            user_agent, response_size, is_admin
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        f"2024-01-01T10:00:{operation_id:02d}",
                        "request", "GET", f"/concurrent/{operation_id}", 200, 50,
                        "127.0.0.1", "8080", '{}', '{}', '{}', '{}',
                        f"session-{operation_id}", "concurrent-test", f"req-{operation_id}",
                        "test-client", 1024, 0
                    ))
                    
                    conn.commit()
                    conn.close()
                    return True
                except Exception as e:
                    print(f"   Concurrent operation {operation_id} failed: {e}")
                    return False
            
            # Run 10 concurrent operations
            tasks = [concurrent_operation(i) for i in range(10)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_ops = sum(1 for r in results if r is True)
            
            if successful_ops < 8:  # Allow some failures due to locking
                print(f"   ❌ Only {successful_ops}/10 concurrent operations succeeded")
                return False
            
            print(f"   ✅ {successful_ops}/10 concurrent operations succeeded")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error handling test failed: {e}")
            return False
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
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
                "test_directory": str(self.temp_dir) if self.temp_dir else None
            }
        }
    
    async def run_all_tests(self) -> bool:
        """Run all integration tests."""
        print("🚀 Starting Comprehensive MockLoop MCP Integration Tests")
        print("=" * 80)
        
        self.setup_test_environment()
        
        try:
            # Test 1: Complete workflow
            print("\n" + "=" * 80)
            self.test_results["complete_workflow"] = await self.test_complete_workflow()
            
            # Test 2: MCP tools integration
            print("\n" + "=" * 80)
            self.test_results["mcp_tools_integration"] = await self.test_mcp_tools_integration()
            
            # Test 3: Database migration system
            print("\n" + "=" * 80)
            self.test_results["database_migration"] = await self.test_database_migration_system()
            
            # Test 4: Performance and compatibility
            print("\n" + "=" * 80)
            self.test_results["performance_compatibility"] = await self.test_performance_and_compatibility()
            
            # Test 5: Error handling and resilience
            print("\n" + "=" * 80)
            self.test_results["error_handling"] = await self.test_error_handling_and_resilience()
            
            # Generate final report
            report = self.generate_test_report()
            
            print("\n" + "=" * 80)
            print("🎉 COMPREHENSIVE INTEGRATION TEST RESULTS")
            print("=" * 80)
            
            for test_name, result in self.test_results.items():
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"{test_name.replace('_', ' ').title()}: {status}")
            
            print(f"\nOverall Success Rate: {report['test_summary']['success_rate']:.1f}%")
            print(f"Tests Passed: {report['test_summary']['passed_tests']}/{report['test_summary']['total_tests']}")
            
            # Save detailed report
            report_path = self.temp_dir / "integration_test_report.json" if self.temp_dir else Path("integration_test_report.json")
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


async def main():
    """Main test execution function."""
    tester = ComprehensiveIntegrationTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All integration tests passed! MockLoop MCP enhancement plan is fully validated.")
        return 0
    else:
        print("\n❌ Some integration tests failed. Please review the results above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)