# MCP Tools Reference

This comprehensive reference documents all Model Context Protocol (MCP) tools provided by MockLoop MCP, including parameters, examples, and response formats.

## Overview

MockLoop MCP provides four primary tools for managing mock API servers:

| Tool | Purpose | Category |
|------|---------|----------|
| [`generate_mock_api`](#generate_mock_api) | Generate mock servers from API specifications | Generation |
| [`query_mock_logs`](#query_mock_logs) | Analyze request logs with filtering and insights | Analytics |
| [`discover_mock_servers`](#discover_mock_servers) | Find running servers and configurations | Discovery |
| [`manage_mock_data`](#manage_mock_data) | Manage dynamic responses and scenarios | Management |

## `generate_mock_api`

Generate a FastAPI mock server from an API specification with comprehensive logging, Docker support, and admin interface.

### Parameters

```json
{
  "spec_url_or_path": "string (required)",
  "output_dir_name": "string (optional)",
  "auth_enabled": "boolean (optional, default: true)",
  "webhooks_enabled": "boolean (optional, default: true)",
  "admin_ui_enabled": "boolean (optional, default: true)",
  "storage_enabled": "boolean (optional, default: true)"
}
```

#### Parameter Details

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `spec_url_or_path` | string | ✅ | - | URL or local file path to API specification (OpenAPI/Swagger) |
| `output_dir_name` | string | ❌ | Auto-generated | Custom name for the output directory |
| `auth_enabled` | boolean | ❌ | `true` | Enable authentication middleware |
| `webhooks_enabled` | boolean | ❌ | `true` | Enable webhook support |
| `admin_ui_enabled` | boolean | ❌ | `true` | Enable admin UI |
| `storage_enabled` | boolean | ❌ | `true` | Enable storage functionality |

### Examples

#### Basic Usage

```json
{
  "spec_url_or_path": "https://petstore3.swagger.io/api/v3/openapi.json"
}
```

#### Custom Configuration

```json
{
  "spec_url_or_path": "https://api.github.com/",
  "output_dir_name": "github_api_mock",
  "auth_enabled": false,
  "webhooks_enabled": true,
  "admin_ui_enabled": true,
  "storage_enabled": true
}
```

#### Local File

```json
{
  "spec_url_or_path": "./my-api.yaml",
  "output_dir_name": "my_custom_api",
  "auth_enabled": true
}
```

### Response Format

```json
{
  "success": true,
  "message": "Mock server generated successfully",
  "output_directory": "generated_mocks/petstore_api/",
  "server_info": {
    "name": "Swagger Petstore - OpenAPI 3.0",
    "version": "1.0.17",
    "endpoints": 19,
    "tags": ["pet", "store", "user"],
    "features": {
      "auth_enabled": true,
      "webhooks_enabled": true,
      "admin_ui_enabled": true,
      "storage_enabled": true
    }
  },
  "generated_files": [
    "main.py",
    "requirements_mock.txt",
    "Dockerfile",
    "docker-compose.yml",
    "logging_middleware.py",
    "templates/admin.html"
  ],
  "next_steps": [
    "cd generated_mocks/petstore_api/",
    "docker-compose up --build"
  ]
}
```

### Error Responses

```json
{
  "success": false,
  "error": "Failed to download specification",
  "details": "HTTP 404: Not Found",
  "suggestion": "Verify the URL is correct and accessible"
}
```

## `query_mock_logs`

Query and analyze request logs from running mock servers with advanced filtering, performance metrics, and AI-powered insights.

### Parameters

```json
{
  "server_url": "string (required)",
  "limit": "integer (optional, default: 100)",
  "offset": "integer (optional, default: 0)",
  "method": "string (optional)",
  "path_pattern": "string (optional)",
  "time_from": "string (optional)",
  "time_to": "string (optional)",
  "include_admin": "boolean (optional, default: false)",
  "analyze": "boolean (optional, default: true)"
}
```

#### Parameter Details

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `server_url` | string | ✅ | - | URL of the mock server (e.g., "http://localhost:8000") |
| `limit` | integer | ❌ | 100 | Maximum number of logs to return |
| `offset` | integer | ❌ | 0 | Number of logs to skip for pagination |
| `method` | string | ❌ | - | Filter by HTTP method (GET, POST, PUT, DELETE, etc.) |
| `path_pattern` | string | ❌ | - | Regex pattern to filter request paths |
| `time_from` | string | ❌ | - | Start time filter (ISO 8601 format) |
| `time_to` | string | ❌ | - | End time filter (ISO 8601 format) |
| `include_admin` | boolean | ❌ | `false` | Include admin requests in results |
| `analyze` | boolean | ❌ | `true` | Perform analysis on the logs |

### Examples

#### Basic Analysis

```json
{
  "server_url": "http://localhost:8000"
}
```

#### Filtered Query

```json
{
  "server_url": "http://localhost:8000",
  "method": "GET",
  "path_pattern": "/pet/.*",
  "limit": 50,
  "time_from": "2025-01-01T00:00:00Z",
  "time_to": "2025-01-01T23:59:59Z"
}
```

#### Performance Focus

```json
{
  "server_url": "http://localhost:8000",
  "analyze": true,
  "include_admin": false,
  "limit": 1000
}
```

### Response Format

```json
{
  "success": true,
  "server_url": "http://localhost:8000",
  "query_info": {
    "total_logs": 1250,
    "returned_logs": 100,
    "filters_applied": ["method: GET", "path_pattern: /pet/.*"],
    "time_range": "2025-01-01T00:00:00Z to 2025-01-01T23:59:59Z"
  },
  "logs": [
    {
      "id": 1,
      "timestamp": "2025-01-01T12:00:00Z",
      "method": "GET",
      "path": "/pet/1",
      "status_code": 200,
      "response_time_ms": 15,
      "client_ip": "127.0.0.1",
      "user_agent": "curl/7.68.0",
      "request_headers": {...},
      "response_headers": {...},
      "request_body": null,
      "response_body": {...}
    }
  ],
  "analysis": {
    "performance_metrics": {
      "total_requests": 1250,
      "avg_response_time_ms": 25,
      "p50_response_time_ms": 18,
      "p95_response_time_ms": 45,
      "p99_response_time_ms": 78,
      "error_rate_percent": 2.4
    },
    "traffic_patterns": {
      "requests_per_hour": 52,
      "peak_hour": "14:00-15:00 UTC",
      "most_popular_endpoint": "/pet/findByStatus",
      "unique_clients": 15
    },
    "error_analysis": {
      "total_errors": 30,
      "error_breakdown": {
        "404": 20,
        "500": 8,
        "429": 2
      },
      "common_error_paths": ["/pet/999", "/store/order/invalid"]
    },
    "insights": [
      "Response times are excellent (P95 < 50ms)",
      "Low error rate indicates stable operation",
      "Consider adding rate limiting for /pet/findByStatus",
      "404 errors suggest missing test data for high pet IDs"
    ]
  }
}
```

## `discover_mock_servers`

Discover running MockLoop servers and generated mock configurations on the local system.

### Parameters

```json
{
  "ports": "array (optional)",
  "check_health": "boolean (optional, default: true)",
  "include_generated": "boolean (optional, default: true)"
}
```

#### Parameter Details

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ports` | array | ❌ | [8000-8005, 3000-3001, 5000-5001] | List of ports to scan |
| `check_health` | boolean | ❌ | `true` | Perform health checks on discovered servers |
| `include_generated` | boolean | ❌ | `true` | Include generated but not running mocks |

### Examples

#### Default Discovery

```json
{
  "check_health": true,
  "include_generated": true
}
```

#### Custom Port Range

```json
{
  "ports": [8000, 8001, 8002, 9000, 9001],
  "check_health": true,
  "include_generated": false
}
```

### Response Format

```json
{
  "success": true,
  "discovery_info": {
    "scanned_ports": [8000, 8001, 8002, 3000, 3001, 5000, 5001],
    "scan_duration_ms": 1250,
    "timestamp": "2025-01-01T12:00:00Z"
  },
  "running_servers": [
    {
      "url": "http://localhost:8000",
      "status": "healthy",
      "server_info": {
        "name": "Swagger Petstore - OpenAPI 3.0",
        "version": "1.0.17",
        "uptime_seconds": 3600,
        "total_requests": 1250
      },
      "features": {
        "admin_ui": true,
        "webhooks": true,
        "auth": true,
        "storage": true
      },
      "health_check": {
        "status": "healthy",
        "response_time_ms": 5,
        "last_check": "2025-01-01T12:00:00Z"
      }
    }
  ],
  "generated_mocks": [
    {
      "directory": "generated_mocks/petstore_api/",
      "name": "Swagger Petstore - OpenAPI 3.0",
      "created": "2025-01-01T10:00:00Z",
      "status": "running",
      "port": 8000,
      "docker_compose": true
    },
    {
      "directory": "generated_mocks/github_api_mock/",
      "name": "GitHub API",
      "created": "2025-01-01T09:00:00Z",
      "status": "stopped",
      "port": null,
      "docker_compose": true
    }
  ],
  "summary": {
    "total_running": 1,
    "total_generated": 2,
    "healthy_servers": 1,
    "available_ports": [8001, 8002, 3000, 3001, 5000, 5001]
  }
}
```

## `manage_mock_data`

Manage dynamic response data and scenarios for MockLoop servers without requiring server restart.

### Parameters

```json
{
  "server_url": "string (required)",
  "operation": "string (required)",
  "endpoint_path": "string (optional)",
  "response_data": "object (optional)",
  "scenario_name": "string (optional)",
  "scenario_config": "object (optional)"
}
```

#### Parameter Details

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `server_url` | string | ✅ | - | URL of the mock server |
| `operation` | string | ✅ | - | Operation type (see operations below) |
| `endpoint_path` | string | ❌ | - | API endpoint path for response updates |
| `response_data` | object | ❌ | - | New response data for endpoint updates |
| `scenario_name` | string | ❌ | - | Name for scenario operations |
| `scenario_config` | object | ❌ | - | Scenario configuration for creation |

#### Operations

| Operation | Description | Required Parameters |
|-----------|-------------|-------------------|
| `update_response` | Update response for specific endpoint | `endpoint_path`, `response_data` |
| `create_scenario` | Create new test scenario | `scenario_name`, `scenario_config` |
| `switch_scenario` | Switch to different scenario | `scenario_name` |
| `list_scenarios` | List available scenarios | None |

### Examples

#### Update Response

```json
{
  "server_url": "http://localhost:8000",
  "operation": "update_response",
  "endpoint_path": "/pet/1",
  "response_data": {
    "id": 1,
    "name": "Fluffy Cat",
    "category": {"id": 2, "name": "Cats"},
    "status": "available"
  }
}
```

#### Create Scenario

```json
{
  "server_url": "http://localhost:8000",
  "operation": "create_scenario",
  "scenario_name": "error_testing",
  "scenario_config": {
    "description": "Test error conditions",
    "endpoints": {
      "/pet/1": {
        "GET": {"status": 404, "error": "Pet not found"}
      },
      "/pet": {
        "POST": {"status": 500, "error": "Internal server error"}
      }
    }
  }
}
```

#### Switch Scenario

```json
{
  "server_url": "http://localhost:8000",
  "operation": "switch_scenario",
  "scenario_name": "error_testing"
}
```

#### List Scenarios

```json
{
  "server_url": "http://localhost:8000",
  "operation": "list_scenarios"
}
```

### Response Formats

#### Update Response Success

```json
{
  "success": true,
  "operation": "update_response",
  "endpoint_path": "/pet/1",
  "message": "Response updated successfully",
  "previous_response": {...},
  "new_response": {...}
}
```

#### Create Scenario Success

```json
{
  "success": true,
  "operation": "create_scenario",
  "scenario_name": "error_testing",
  "message": "Scenario created successfully",
  "scenario_config": {...},
  "endpoints_affected": ["/pet/1", "/pet"]
}
```

#### List Scenarios Response

```json
{
  "success": true,
  "operation": "list_scenarios",
  "current_scenario": "default",
  "scenarios": [
    {
      "name": "default",
      "description": "Default responses",
      "active": true,
      "created": "2025-01-01T10:00:00Z",
      "endpoints": 19
    },
    {
      "name": "error_testing",
      "description": "Test error conditions",
      "active": false,
      "created": "2025-01-01T12:00:00Z",
      "endpoints": 2
    }
  ]
}
```

## Error Handling

All tools return consistent error responses:

```json
{
  "success": false,
  "error": "Error type",
  "message": "Human-readable error message",
  "details": "Technical details about the error",
  "suggestion": "Suggested action to resolve the issue",
  "error_code": "MOCKLOOP_ERROR_001"
}
```

### Common Error Codes

| Code | Description | Common Causes |
|------|-------------|---------------|
| `MOCKLOOP_ERROR_001` | Invalid specification URL | URL not accessible, invalid format |
| `MOCKLOOP_ERROR_002` | Server not reachable | Server not running, wrong port |
| `MOCKLOOP_ERROR_003` | Invalid operation | Unsupported operation type |
| `MOCKLOOP_ERROR_004` | Scenario not found | Scenario doesn't exist |
| `MOCKLOOP_ERROR_005` | Permission denied | File system permissions |

## Rate Limiting

MCP tools respect rate limiting to prevent overwhelming mock servers:

- **Default Rate**: 10 requests per second per server
- **Burst Limit**: 50 requests in 10 seconds
- **Backoff Strategy**: Exponential backoff on rate limit errors

## Best Practices

### 1. Server URL Format

Always use complete URLs with protocol:
```
✅ http://localhost:8000
✅ https://my-mock-server.com
❌ localhost:8000
❌ my-mock-server.com
```

### 2. Time Filtering

Use ISO 8601 format for time parameters:
```
✅ 2025-01-01T12:00:00Z
✅ 2025-01-01T12:00:00+00:00
❌ 2025-01-01 12:00:00
❌ Jan 1, 2025 12:00 PM
```

### 3. Path Patterns

Use proper regex syntax for path filtering:
```
✅ /pet/.*          # All pet endpoints
✅ /api/v[12]/.*     # API v1 or v2
✅ .*\\.json$        # JSON endpoints
❌ /pet/*           # Shell glob (not regex)
```

### 4. Response Data

Ensure response data matches the API schema:
```json
{
  "endpoint_path": "/pet/1",
  "response_data": {
    "id": 1,
    "name": "string",
    "status": "available"  // Must match enum values
  }
}
```

### 5. Scenario Management

Use descriptive scenario names and configurations:
```json
{
  "scenario_name": "high_load_simulation",
  "scenario_config": {
    "description": "Simulate high load with delays",
    "endpoints": {
      "/pet/findByStatus": {
        "GET": {
          "status": 200,
          "delay_ms": 1000,
          "response": {...}
        }
      }
    }
  }
}
```

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/api-tests.yml
- name: Start Mock Server
  run: |
    mockloop generate_mock_api \
      --spec ./api-spec.yaml \
      --output test_api
    cd generated_mocks/test_api
    docker-compose up -d

- name: Run Tests
  run: pytest tests/

- name: Analyze Results
  run: |
    mockloop query_mock_logs \
      --server-url http://localhost:8000 \
      --analyze
```

### Development Workflow

```bash
# Generate mock for development
mockloop generate_mock_api \
  --spec https://api.example.com/openapi.json \
  --output dev_api

# Start development server
cd generated_mocks/dev_api
docker-compose up -d

# Update responses during development
mockloop manage_mock_data \
  --server-url http://localhost:8000 \
  --operation update_response \
  --endpoint-path "/users" \
  --response-data '{"users": [...]}'
```

## Next Steps

- **[Core Classes](core-classes.md)**: Understand the underlying implementation
- **[Configuration Options](configuration.md)**: Detailed configuration reference
- **[Database Schema](database-schema.md)**: Database structure and queries
- **[Admin API](admin-api.md)**: Direct API access for automation