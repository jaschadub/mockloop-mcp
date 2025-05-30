# Testing Guide

This comprehensive guide covers testing practices, strategies, and tools for MockLoop MCP. Our testing approach ensures reliability, maintainability, and confidence in the codebase through multiple layers of testing.

## Overview

MockLoop MCP uses a multi-layered testing strategy:

- **Unit Tests**: Test individual functions and classes in isolation
- **Integration Tests**: Test component interactions and workflows
- **End-to-End Tests**: Test complete user scenarios
- **Performance Tests**: Validate performance characteristics
- **Security Tests**: Verify security controls and data protection
- **Contract Tests**: Ensure API compatibility

## Testing Framework and Tools

### Core Testing Stack

```python
# pytest - Primary testing framework
import pytest
import pytest_asyncio
import pytest_mock

# Testing utilities
from unittest.mock import Mock, patch, AsyncMock
from faker import Faker
from factory_boy import Factory, Sequence

# HTTP testing
import httpx
from fastapi.testclient import TestClient

# Database testing
import pytest_postgresql
from sqlalchemy import create_engine
from alembic import command
from alembic.config import Config

# Performance testing
import pytest_benchmark
import locust

# Security testing
import bandit
import safety
```

### Test Configuration

```python
# conftest.py - Global test configuration
import pytest
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator

from mockloop_mcp.core import create_app
from mockloop_mcp.database import Database, get_database
from mockloop_mcp.config import Settings, get_settings

# Test settings
@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Provide test-specific settings."""
    return Settings(
        database_url="sqlite:///test.db",
        environment="test",
        log_level="DEBUG",
        auth_enabled=False,
        storage_enabled=True,
        webhook_enabled=False
    )

# Database fixtures
@pytest.fixture(scope="session")
async def database(test_settings: Settings) -> AsyncGenerator[Database, None]:
    """Provide test database connection."""
    db = Database(test_settings.database_url)
    await db.connect()
    
    # Run migrations
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", test_settings.database_url)
    command.upgrade(alembic_cfg, "head")
    
    yield db
    
    await db.disconnect()

@pytest.fixture
async def clean_database(database: Database) -> AsyncGenerator[Database, None]:
    """Provide clean database for each test."""
    # Start transaction
    async with database.transaction():
        yield database
        # Rollback transaction after test

# Application fixtures
@pytest.fixture
def app(test_settings: Settings, clean_database: Database):
    """Provide FastAPI test application."""
    app = create_app(test_settings)
    
    # Override dependencies
    app.dependency_overrides[get_settings] = lambda: test_settings
    app.dependency_overrides[get_database] = lambda: clean_database
    
    return app

@pytest.fixture
def client(app) -> TestClient:
    """Provide HTTP test client."""
    return TestClient(app)

@pytest.fixture
async def async_client(app) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide async HTTP test client."""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

## Unit Testing

### Testing Core Classes

```python
# test_mock_generator.py
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from mockloop_mcp.generator import MockServerGenerator
from mockloop_mcp.models import GenerationOptions, GenerationResult
from mockloop_mcp.exceptions import SpecificationError, GenerationError

class TestMockServerGenerator:
    """Test mock server generation functionality."""
    
    @pytest.fixture
    def generator(self):
        """Provide generator instance."""
        return MockServerGenerator()
    
    @pytest.fixture
    def valid_openapi_spec(self, tmp_path):
        """Provide valid OpenAPI specification."""
        spec_content = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/User"}
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
                            "email": {"type": "string", "format": "email"}
                        }
                    }
                }
            }
        }
        
        spec_file = tmp_path / "openapi.json"
        spec_file.write_text(json.dumps(spec_content))
        return str(spec_file)
    
    def test_generate_with_valid_spec(self, generator, valid_openapi_spec, tmp_path):
        """Test successful generation with valid specification."""
        options = GenerationOptions(
            output_dir=str(tmp_path / "output"),
            auth_enabled=True,
            storage_enabled=True
        )
        
        result = generator.generate(valid_openapi_spec, options)
        
        assert isinstance(result, GenerationResult)
        assert result.success is True
        assert result.server_info is not None
        assert result.server_info.name == "test-api"
        assert len(result.generated_files) > 0
        
        # Verify generated files exist
        output_dir = Path(options.output_dir)
        assert (output_dir / "main.py").exists()
        assert (output_dir / "requirements.txt").exists()
        assert (output_dir / "Dockerfile").exists()
    
    def test_generate_with_invalid_spec_raises_error(self, generator, tmp_path):
        """Test that invalid specification raises SpecificationError."""
        invalid_spec = tmp_path / "invalid.json"
        invalid_spec.write_text('{"invalid": "spec"}')
        
        options = GenerationOptions(output_dir=str(tmp_path / "output"))
        
        with pytest.raises(SpecificationError) as exc_info:
            generator.generate(str(invalid_spec), options)
        
        assert "Invalid OpenAPI specification" in str(exc_info.value)
        assert exc_info.value.spec_path == str(invalid_spec)
    
    def test_generate_with_nonexistent_spec_raises_error(self, generator, tmp_path):
        """Test that nonexistent specification file raises error."""
        nonexistent_spec = str(tmp_path / "nonexistent.json")
        options = GenerationOptions(output_dir=str(tmp_path / "output"))
        
        with pytest.raises(SpecificationError):
            generator.generate(nonexistent_spec, options)
    
    @patch('mockloop_mcp.generator.template_engine')
    def test_generate_with_template_error_raises_generation_error(
        self, mock_template_engine, generator, valid_openapi_spec, tmp_path
    ):
        """Test that template errors raise GenerationError."""
        mock_template_engine.render.side_effect = Exception("Template error")
        
        options = GenerationOptions(output_dir=str(tmp_path / "output"))
        
        with pytest.raises(GenerationError) as exc_info:
            generator.generate(valid_openapi_spec, options)
        
        assert exc_info.value.stage == "template_rendering"
    
    def test_validate_specification_with_valid_spec(self, generator, valid_openapi_spec):
        """Test specification validation with valid spec."""
        result = generator.validate_specification(valid_openapi_spec)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.spec_type == "openapi"
        assert result.version == "3.0.0"
    
    def test_validate_specification_with_invalid_spec(self, generator, tmp_path):
        """Test specification validation with invalid spec."""
        invalid_spec = tmp_path / "invalid.json"
        invalid_spec.write_text('{"openapi": "3.0.0"}')  # Missing required fields
        
        result = generator.validate_specification(str(invalid_spec))
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("info" in error for error in result.errors)
```

### Testing Database Operations

```python
# test_database.py
import pytest
from datetime import datetime, timedelta

from mockloop_mcp.database import Database
from mockloop_mcp.models import RequestLog, ServerConfig

class TestDatabase:
    """Test database operations."""
    
    @pytest.mark.asyncio
    async def test_insert_request_log(self, clean_database: Database):
        """Test inserting request log."""
        log_data = {
            "method": "GET",
            "path": "/users",
            "query_params": {"limit": "10"},
            "headers": {"Accept": "application/json"},
            "body": None,
            "status_code": 200,
            "response_body": {"users": []},
            "response_time": 0.123,
            "timestamp": datetime.utcnow()
        }
        
        log_id = await clean_database.insert_request_log(log_data)
        
        assert log_id is not None
        
        # Verify log was inserted
        log = await clean_database.get_request_log(log_id)
        assert log is not None
        assert log.method == "GET"
        assert log.path == "/users"
        assert log.status_code == 200
    
    @pytest.mark.asyncio
    async def test_query_request_logs_with_filters(self, clean_database: Database):
        """Test querying request logs with filters."""
        # Insert test data
        base_time = datetime.utcnow()
        
        logs = [
            {
                "method": "GET",
                "path": "/users",
                "status_code": 200,
                "timestamp": base_time
            },
            {
                "method": "POST",
                "path": "/users",
                "status_code": 201,
                "timestamp": base_time + timedelta(minutes=1)
            },
            {
                "method": "GET",
                "path": "/posts",
                "status_code": 200,
                "timestamp": base_time + timedelta(minutes=2)
            }
        ]
        
        for log_data in logs:
            await clean_database.insert_request_log(log_data)
        
        # Test method filter
        get_logs = await clean_database.query_request_logs(method="GET")
        assert len(get_logs) == 2
        assert all(log.method == "GET" for log in get_logs)
        
        # Test path filter
        user_logs = await clean_database.query_request_logs(path_pattern="/users")
        assert len(user_logs) == 2
        assert all("/users" in log.path for log in user_logs)
        
        # Test time range filter
        recent_logs = await clean_database.query_request_logs(
            time_from=base_time + timedelta(minutes=0.5),
            time_to=base_time + timedelta(minutes=1.5)
        )
        assert len(recent_logs) == 1
        assert recent_logs[0].method == "POST"
    
    @pytest.mark.asyncio
    async def test_transaction_rollback(self, clean_database: Database):
        """Test transaction rollback on error."""
        initial_count = await clean_database.count_request_logs()
        
        try:
            async with clean_database.transaction():
                # Insert valid log
                await clean_database.insert_request_log({
                    "method": "GET",
                    "path": "/test",
                    "status_code": 200,
                    "timestamp": datetime.utcnow()
                })
                
                # Raise error to trigger rollback
                raise ValueError("Test error")
                
        except ValueError:
            pass
        
        # Verify rollback occurred
        final_count = await clean_database.count_request_logs()
        assert final_count == initial_count
```

### Testing API Endpoints

```python
# test_api.py
import pytest
from fastapi.testclient import TestClient

class TestMockServerAPI:
    """Test mock server API endpoints."""
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {
            "status": "healthy",
            "timestamp": pytest.approx(datetime.utcnow().timestamp(), abs=1)
        }
    
    def test_get_server_info(self, client: TestClient):
        """Test server info endpoint."""
        response = client.get("/admin/info")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "uptime" in data
        assert "request_count" in data
    
    def test_list_request_logs(self, client: TestClient):
        """Test listing request logs."""
        # Make some requests to generate logs
        client.get("/users")
        client.post("/users", json={"name": "Test User"})
        
        response = client.get("/admin/logs")
        
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total" in data
        assert len(data["logs"]) >= 2
    
    def test_list_request_logs_with_filters(self, client: TestClient):
        """Test listing request logs with filters."""
        # Generate test requests
        client.get("/users")
        client.post("/users", json={"name": "Test"})
        client.get("/posts")
        
        # Filter by method
        response = client.get("/admin/logs?method=GET")
        assert response.status_code == 200
        data = response.json()
        assert all(log["method"] == "GET" for log in data["logs"])
        
        # Filter by path
        response = client.get("/admin/logs?path_pattern=/users")
        assert response.status_code == 200
        data = response.json()
        assert all("/users" in log["path"] for log in data["logs"])
    
    def test_update_response_data(self, client: TestClient):
        """Test updating response data."""
        new_data = {"users": [{"id": 1, "name": "Updated User"}]}
        
        response = client.put(
            "/admin/responses/users",
            json=new_data
        )
        
        assert response.status_code == 200
        
        # Verify updated data is returned
        response = client.get("/users")
        assert response.status_code == 200
        assert response.json() == new_data
    
    def test_create_scenario(self, client: TestClient):
        """Test creating a new scenario."""
        scenario_config = {
            "name": "test_scenario",
            "description": "Test scenario",
            "responses": {
                "/users": {"users": [{"id": 1, "name": "Test User"}]},
                "/posts": {"posts": []}
            }
        }
        
        response = client.post("/admin/scenarios", json=scenario_config)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test_scenario"
        assert "id" in data
    
    def test_switch_scenario(self, client: TestClient):
        """Test switching to a different scenario."""
        # Create scenario first
        scenario_config = {
            "name": "test_scenario",
            "responses": {
                "/users": {"users": [{"id": 999, "name": "Scenario User"}]}
            }
        }
        
        create_response = client.post("/admin/scenarios", json=scenario_config)
        scenario_id = create_response.json()["id"]
        
        # Switch to scenario
        response = client.post(f"/admin/scenarios/{scenario_id}/activate")
        assert response.status_code == 200
        
        # Verify scenario is active
        response = client.get("/users")
        assert response.status_code == 200
        data = response.json()
        assert data["users"][0]["id"] == 999
```

## Integration Testing

### Testing Component Interactions

```python
# test_integration.py
import pytest
import asyncio
from pathlib import Path

from mockloop_mcp.generator import MockServerGenerator
from mockloop_mcp.server import MockServer
from mockloop_mcp.database import Database

class TestMockServerIntegration:
    """Test integration between components."""
    
    @pytest.mark.asyncio
    async def test_full_generation_and_startup_workflow(self, tmp_path, test_settings):
        """Test complete workflow from generation to server startup."""
        # 1. Generate mock server
        generator = MockServerGenerator()
        spec_path = self.create_test_spec(tmp_path)
        output_dir = tmp_path / "generated_server"
        
        options = GenerationOptions(
            output_dir=str(output_dir),
            auth_enabled=True,
            storage_enabled=True
        )
        
        result = generator.generate(spec_path, options)
        assert result.success is True
        
        # 2. Start generated server
        server = MockServer.from_directory(output_dir)
        await server.start()
        
        try:
            # 3. Test server functionality
            async with httpx.AsyncClient(base_url=server.base_url) as client:
                # Test health endpoint
                response = await client.get("/health")
                assert response.status_code == 200
                
                # Test generated API endpoint
                response = await client.get("/users")
                assert response.status_code == 200
                
                # Test admin endpoints
                response = await client.get("/admin/info")
                assert response.status_code == 200
                
                # Test request logging
                response = await client.get("/admin/logs")
                assert response.status_code == 200
                logs = response.json()["logs"]
                assert len(logs) >= 3  # health, users, admin/info
                
        finally:
            await server.stop()
    
    @pytest.mark.asyncio
    async def test_database_integration_with_server(self, tmp_path, test_settings):
        """Test database integration with running server."""
        # Setup server with database
        server = MockServer(
            config=ServerConfig(
                name="test_server",
                port=8080,
                storage_enabled=True,
                database_url="sqlite:///test_integration.db"
            )
        )
        
        await server.start()
        
        try:
            # Make requests to generate logs
            async with httpx.AsyncClient(base_url=server.base_url) as client:
                await client.get("/users")
                await client.post("/users", json={"name": "Test User"})
                await client.get("/users/1")
            
            # Verify logs in database
            db = server.database
            logs = await db.query_request_logs(limit=10)
            
            assert len(logs) == 3
            assert logs[0].method in ["GET", "POST"]
            assert all(log.path.startswith("/users") for log in logs)
            
            # Test log filtering
            get_logs = await db.query_request_logs(method="GET")
            assert len(get_logs) == 2
            
            post_logs = await db.query_request_logs(method="POST")
            assert len(post_logs) == 1
            
        finally:
            await server.stop()
    
    def create_test_spec(self, tmp_path: Path) -> str:
        """Create test OpenAPI specification."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "List users",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "users": {
                                                    "type": "array",
                                                    "items": {"$ref": "#/components/schemas/User"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": "User created",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                }
                            }
                        }
                    }
                },
                "/users/{id}": {
                    "get": {
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"}
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Get user",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
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
                            "email": {"type": "string", "format": "email"}
                        }
                    }
                }
            }
        }
        
        spec_file = tmp_path / "test_spec.json"
        spec_file.write_text(json.dumps(spec))
        return str(spec_file)
```

## End-to-End Testing

### User Workflow Testing

```python
# test_e2e.py
import pytest
import subprocess
import time
import requests
from pathlib import Path

class TestEndToEndWorkflows:
    """Test complete user workflows."""
    
    @pytest.mark.e2e
    def test_cli_generate_and_run_workflow(self, tmp_path):
        """Test CLI workflow: generate server and run it."""
        spec_file = self.create_openapi_spec(tmp_path)
        output_dir = tmp_path / "generated_server"
        
        # 1. Generate server using CLI
        result = subprocess.run([
            "python", "-m", "mockloop_mcp.cli",
            "generate",
            "--spec", str(spec_file),
            "--output", str(output_dir),
            "--auth-enabled",
            "--storage-enabled"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "Server generated successfully" in result.stdout
        
        # 2. Verify generated files
        assert (output_dir / "main.py").exists()
        assert (output_dir / "requirements.txt").exists()
        assert (output_dir / "Dockerfile").exists()
        assert (output_dir / "docker-compose.yml").exists()
        
        # 3. Start server using Docker Compose
        compose_process = subprocess.Popen([
            "docker-compose", "up", "-d"
        ], cwd=output_dir)
        
        try:
            # Wait for server to start
            time.sleep(10)
            
            # 4. Test server endpoints
            base_url = "http://localhost:8080"
            
            # Health check
            response = requests.get(f"{base_url}/health")
            assert response.status_code == 200
            
            # API endpoints
            response = requests.get(f"{base_url}/users")
            assert response.status_code == 200
            
            # Admin endpoints
            response = requests.get(f"{base_url}/admin/info")
            assert response.status_code == 200
            
            # Test request logging
            response = requests.get(f"{base_url}/admin/logs")
            assert response.status_code == 200
            logs = response.json()["logs"]
            assert len(logs) >= 3
            
        finally:
            # 5. Stop server
            subprocess.run([
                "docker-compose", "down"
            ], cwd=output_dir)
    
    @pytest.mark.e2e
    def test_mcp_tool_integration(self, tmp_path):
        """Test MCP tool integration workflow."""
        # This would test the actual MCP tool usage
        # in a real MCP client environment
        pass
    
    def create_openapi_spec(self, tmp_path: Path) -> Path:
        """Create test OpenAPI specification file."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "E2E Test API",
                "version": "1.0.0",
                "description": "API for end-to-end testing"
            },
            "servers": [
                {"url": "http://localhost:8080", "description": "Local server"}
            ],
            "paths": {
                "/users": {
                    "get": {
                        "summary": "List users",
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "users": {
                                                    "type": "array",
                                                    "items": {"$ref": "#/components/schemas/User"}
                                                }
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
                            "email": {"type": "string", "format": "email"}
                        }
                    }
                }
            }
        }
        
        spec_file = tmp_path / "e2e_spec.json"
        spec_file.write_text(json.dumps(spec, indent=2))
        return spec_file
```

## Performance Testing

### Load Testing

```python
# test_performance.py
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
import httpx

class TestPerformance:
    """Test performance characteristics."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, running_server):
        """Test server performance under concurrent load."""
        base_url = running_server.base_url
        num_requests = 100
        concurrent_clients = 10
        
        async def make_requests(client_id: int) -> list:
            """Make requests from a single client."""
            results = []
            async with httpx.AsyncClient(base_url=base_url) as client:
                for i in range(num_requests // concurrent_clients):
                    start_time = time.time()
                    response = await client.get("/users")
                    end_time = time.time()
                    
                    results.append({
                        "client_id": client_id,
                        "request_id": i,
                        "status_code": response.status_code,
                        "response_time": end_time - start_time
                    })
            
            return results
        
        # Run concurrent clients
        start_time = time.time()
        tasks = [
            make_requests(client_id) 
            for client_id in range(concurrent_clients)
        ]
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Analyze results
        all_results = [result for client_results in results for result in client_results]
        
        # Verify all requests succeeded
        assert all(r["status_code"] == 200 for r in all_results)
        assert len(all_results) == num_requests
        
        # Performance assertions
        total_time = end_time - start_time
        requests_per_second = num_requests / total_time
        
        assert requests_per_second > 50  # Minimum throughput
        
        response_times = [r["response_time"] for r in all_results]
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 0.1  # Average response time under 100ms
        assert max_response_time < 1.0  # Max response time under 1s
    
    @pytest.mark.performance
    def test_memory_usage_under_load(self, running_server):
        """Test memory usage during sustained load."""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Generate sustained load
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for _ in range(1000):
                future = executor.submit(
                    requests.get, 
                    f"{running_server.base_url}/users"
                )
                futures.append(future)
            
            # Wait for completion
            for future in futures:
                response = future.result()
                assert response.status_code == 200
        
        # Force garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_request_processing_benchmark(self, benchmark, client):
        """Benchmark request processing performance."""
        def process_request():
            response = client.get("/users")
            assert response.status_code == 200
            return response
        
        result = benchmark(process_request)
        
        # Benchmark assertions
        assert benchmark.stats.mean < 0.01  # Mean time under 10ms
        assert benchmark.stats.max < 0.1    # Max time under 100ms
```
