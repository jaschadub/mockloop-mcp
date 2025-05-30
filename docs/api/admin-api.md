# Admin API

The MockLoop MCP Admin API provides comprehensive management capabilities for mock servers, scenarios, logs, and system configuration. This REST API enables programmatic control over all aspects of MockLoop MCP.

## Overview

The Admin API is automatically enabled when `admin_ui_enabled` is set to `true` during mock server generation. It provides endpoints for:

- **Server Management**: Start, stop, and configure mock servers
- **Scenario Management**: Create, update, and switch between scenarios
- **Log Management**: Query, analyze, and export request logs
- **Configuration Management**: Update server and system settings
- **Health Monitoring**: Check server health and performance metrics

## Base URL and Authentication

### Base URL

```
http://localhost:{port}/admin/api/v1
```

Where `{port}` is the mock server port (default: 8000).

### Authentication

The Admin API supports multiple authentication methods:

#### API Key Authentication

```bash
curl -H "X-API-Key: your-api-key" \
     http://localhost:8000/admin/api/v1/servers
```

#### JWT Authentication

```bash
# Get JWT token
curl -X POST http://localhost:8000/admin/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password"}'

# Use JWT token
curl -H "Authorization: Bearer your-jwt-token" \
     http://localhost:8000/admin/api/v1/servers
```

## Server Management

### List Servers

Get a list of all mock servers.

```http
GET /admin/api/v1/servers
```

**Response:**

```json
{
  "servers": [
    {
      "id": "server_123",
      "name": "Petstore API Mock",
      "status": "running",
      "port": 8000,
      "spec_path": "./petstore-api.yaml",
      "created_at": "2024-01-01T10:00:00Z",
      "started_at": "2024-01-01T10:05:00Z",
      "config": {
        "auth_enabled": true,
        "webhooks_enabled": true,
        "storage_enabled": true
      }
    }
  ],
  "total": 1
}
```

### Get Server Details

Get detailed information about a specific server.

```http
GET /admin/api/v1/servers/{server_id}
```

**Response:**

```json
{
  "id": "server_123",
  "name": "Petstore API Mock",
  "status": "running",
  "port": 8000,
  "pid": 12345,
  "spec_path": "./petstore-api.yaml",
  "spec_content": "openapi: 3.0.0...",
  "output_directory": "./generated_mocks/petstore",
  "created_at": "2024-01-01T10:00:00Z",
  "started_at": "2024-01-01T10:05:00Z",
  "config": {
    "auth_enabled": true,
    "webhooks_enabled": true,
    "admin_ui_enabled": true,
    "storage_enabled": true,
    "cors_enabled": true,
    "response_delay_ms": 0,
    "error_rate_percent": 0.0
  },
  "statistics": {
    "total_requests": 1250,
    "error_requests": 15,
    "avg_response_time_ms": 45,
    "unique_clients": 8,
    "last_request_time": "2024-01-01T15:30:00Z"
  }
}
```

### Create Server

Create a new mock server from an API specification.

```http
POST /admin/api/v1/servers
```

**Request Body:**

```json
{
  "name": "New API Mock",
  "spec_url_or_path": "./new-api.yaml",
  "output_dir_name": "new_api_mock",
  "config": {
    "auth_enabled": false,
    "webhooks_enabled": true,
    "admin_ui_enabled": true,
    "storage_enabled": true,
    "port": 8001
  }
}
```

**Response:**

```json
{
  "id": "server_456",
  "name": "New API Mock",
  "status": "starting",
  "port": 8001,
  "output_directory": "./generated_mocks/new_api_mock",
  "created_at": "2024-01-01T16:00:00Z",
  "message": "Server creation initiated"
}
```

### Update Server Configuration

Update server configuration settings.

```http
PUT /admin/api/v1/servers/{server_id}/config
```

**Request Body:**

```json
{
  "response_delay_ms": 100,
  "error_rate_percent": 5.0,
  "cors_enabled": true
}
```

### Start Server

Start a stopped mock server.

```http
POST /admin/api/v1/servers/{server_id}/start
```

**Response:**

```json
{
  "id": "server_123",
  "status": "starting",
  "message": "Server start initiated"
}
```

### Stop Server

Stop a running mock server.

```http
POST /admin/api/v1/servers/{server_id}/stop
```

**Response:**

```json
{
  "id": "server_123",
  "status": "stopping",
  "message": "Server stop initiated"
}
```

### Delete Server

Delete a mock server and its generated files.

```http
DELETE /admin/api/v1/servers/{server_id}
```

**Query Parameters:**

- `delete_files` (boolean): Whether to delete generated files (default: false)

**Response:**

```json
{
  "message": "Server deleted successfully",
  "files_deleted": true
}
```

## Scenario Management

### List Scenarios

Get all scenarios for a server.

```http
GET /admin/api/v1/servers/{server_id}/scenarios
```

**Response:**

```json
{
  "scenarios": [
    {
      "id": 1,
      "name": "happy_path",
      "description": "All services working normally",
      "is_active": true,
      "created_at": "2024-01-01T10:00:00Z",
      "created_by": "admin"
    },
    {
      "id": 2,
      "name": "error_scenario",
      "description": "Simulate service errors",
      "is_active": false,
      "created_at": "2024-01-01T11:00:00Z",
      "created_by": "admin"
    }
  ],
  "total": 2,
  "active_scenario": "happy_path"
}
```

### Get Scenario Details

Get detailed scenario configuration.

```http
GET /admin/api/v1/servers/{server_id}/scenarios/{scenario_id}
```

**Response:**

```json
{
  "id": 1,
  "name": "happy_path",
  "description": "All services working normally",
  "is_active": true,
  "config": {
    "/pets": {
      "GET": {
        "status": 200,
        "body": {
          "pets": [
            {"id": 1, "name": "Fluffy", "status": "available"},
            {"id": 2, "name": "Buddy", "status": "pending"}
          ]
        }
      }
    },
    "/pets/{id}": {
      "GET": {
        "status": 200,
        "body": {
          "id": 1,
          "name": "Fluffy",
          "status": "available"
        }
      }
    }
  },
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "created_by": "admin"
}
```

### Create Scenario

Create a new scenario.

```http
POST /admin/api/v1/servers/{server_id}/scenarios
```

**Request Body:**

```json
{
  "name": "testing_scenario",
  "description": "Scenario for automated testing",
  "config": {
    "/pets": {
      "GET": {
        "status": 200,
        "body": {
          "pets": [
            {"id": 1, "name": "Test Pet", "status": "available"}
          ]
        },
        "delay_ms": 100
      }
    }
  }
}
```

**Response:**

```json
{
  "id": 3,
  "name": "testing_scenario",
  "description": "Scenario for automated testing",
  "is_active": false,
  "created_at": "2024-01-01T16:00:00Z",
  "message": "Scenario created successfully"
}
```

### Update Scenario

Update an existing scenario.

```http
PUT /admin/api/v1/servers/{server_id}/scenarios/{scenario_id}
```

**Request Body:**

```json
{
  "description": "Updated scenario description",
  "config": {
    "/pets": {
      "GET": {
        "status": 200,
        "body": {
          "pets": [
            {"id": 1, "name": "Updated Pet", "status": "available"}
          ]
        }
      }
    }
  }
}
```

### Switch Scenario

Activate a specific scenario.

```http
POST /admin/api/v1/servers/{server_id}/scenarios/{scenario_id}/activate
```

**Response:**

```json
{
  "message": "Scenario activated successfully",
  "active_scenario": "testing_scenario",
  "previous_scenario": "happy_path"
}
```

### Delete Scenario

Delete a scenario.

```http
DELETE /admin/api/v1/servers/{server_id}/scenarios/{scenario_id}
```

**Response:**

```json
{
  "message": "Scenario deleted successfully"
}
```

## Mock Response Management

### List Mock Responses

Get all mock responses for a server.

```http
GET /admin/api/v1/servers/{server_id}/responses
```

**Query Parameters:**

- `endpoint` (string): Filter by endpoint path
- `method` (string): Filter by HTTP method
- `scenario_id` (integer): Filter by scenario ID

**Response:**

```json
{
  "responses": [
    {
      "id": 1,
      "endpoint_path": "/pets",
      "method": "GET",
      "response_status": 200,
      "response_body": "{\"pets\": [...]}",
      "delay_ms": 0,
      "scenario_id": 1,
      "is_default": true,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

### Update Mock Response

Update a specific mock response.

```http
PUT /admin/api/v1/servers/{server_id}/responses/{response_id}
```

**Request Body:**

```json
{
  "response_status": 200,
  "response_headers": {
    "Content-Type": "application/json",
    "X-Custom-Header": "value"
  },
  "response_body": {
    "pets": [
      {"id": 1, "name": "Updated Pet", "status": "available"}
    ]
  },
  "delay_ms": 50
}
```

### Create Mock Response

Create a new mock response.

```http
POST /admin/api/v1/servers/{server_id}/responses
```

**Request Body:**

```json
{
  "endpoint_path": "/pets/{id}",
  "method": "DELETE",
  "response_status": 204,
  "response_headers": {},
  "response_body": "",
  "delay_ms": 0,
  "scenario_id": 1
}
```

## Log Management

### Query Request Logs

Query request logs with filtering and analysis.

```http
GET /admin/api/v1/servers/{server_id}/logs
```

**Query Parameters:**

- `limit` (integer): Maximum number of logs (default: 100)
- `offset` (integer): Number of logs to skip (default: 0)
- `method` (string): Filter by HTTP method
- `path` (string): Filter by path pattern (regex)
- `status` (integer): Filter by response status
- `time_from` (string): Start time filter (ISO format)
- `time_to` (string): End time filter (ISO format)
- `client_ip` (string): Filter by client IP
- `scenario` (string): Filter by scenario name
- `analyze` (boolean): Include analysis (default: false)

**Response:**

```json
{
  "logs": [
    {
      "id": 1,
      "timestamp": "2024-01-01T15:30:00Z",
      "method": "GET",
      "path": "/pets",
      "query_params": {"limit": "10"},
      "headers": {
        "User-Agent": "curl/7.68.0",
        "Accept": "*/*"
      },
      "request_body": null,
      "response_status": 200,
      "response_headers": {
        "Content-Type": "application/json"
      },
      "response_body": "{\"pets\": [...]}",
      "response_time_ms": 45,
      "client_ip": "192.168.1.100",
      "user_agent": "curl/7.68.0",
      "request_id": "req_123",
      "scenario_name": "happy_path"
    }
  ],
  "total": 1250,
  "analysis": {
    "total_requests": 1250,
    "unique_clients": 8,
    "avg_response_time_ms": 45,
    "min_response_time_ms": 12,
    "max_response_time_ms": 234,
    "error_rate_percent": 1.2,
    "status_distribution": {
      "200": 1235,
      "404": 10,
      "500": 5
    },
    "method_distribution": {
      "GET": 1000,
      "POST": 150,
      "PUT": 75,
      "DELETE": 25
    },
    "top_endpoints": [
      {
        "path": "/pets",
        "count": 800,
        "avg_response_time_ms": 42
      },
      {
        "path": "/pets/{id}",
        "count": 300,
        "avg_response_time_ms": 38
      }
    ]
  }
}
```

### Export Logs

Export request logs in various formats.

```http
GET /admin/api/v1/servers/{server_id}/logs/export
```

**Query Parameters:**

- `format` (string): Export format (json, csv, xlsx) (default: json)
- `time_from` (string): Start time filter
- `time_to` (string): End time filter
- `include_analysis` (boolean): Include analysis in export

**Response:**

Returns file download with appropriate Content-Type header.

### Clear Logs

Clear request logs for a server.

```http
DELETE /admin/api/v1/servers/{server_id}/logs
```

**Query Parameters:**

- `older_than_days` (integer): Only delete logs older than specified days
- `keep_count` (integer): Keep the most recent N logs

**Response:**

```json
{
  "message": "Logs cleared successfully",
  "deleted_count": 1000,
  "remaining_count": 250
}
```

## Webhook Management

### List Webhooks

Get all webhooks for a server.

```http
GET /admin/api/v1/servers/{server_id}/webhooks
```

**Response:**

```json
{
  "webhooks": [
    {
      "id": 1,
      "name": "notification_webhook",
      "url": "https://api.example.com/webhooks/mockloop",
      "method": "POST",
      "events": ["request.received", "response.sent"],
      "is_active": true,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

### Create Webhook

Create a new webhook.

```http
POST /admin/api/v1/servers/{server_id}/webhooks
```

**Request Body:**

```json
{
  "name": "test_webhook",
  "url": "https://webhook.site/unique-id",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer token",
    "Content-Type": "application/json"
  },
  "events": ["request.received", "scenario.changed"],
  "secret_key": "webhook_secret"
}
```

### Update Webhook

Update webhook configuration.

```http
PUT /admin/api/v1/servers/{server_id}/webhooks/{webhook_id}
```

### Test Webhook

Test webhook delivery.

```http
POST /admin/api/v1/servers/{server_id}/webhooks/{webhook_id}/test
```

**Response:**

```json
{
  "success": true,
  "response_status": 200,
  "response_body": "OK",
  "delivery_time_ms": 150
}
```

### Webhook Delivery Logs

Get webhook delivery history.

```http
GET /admin/api/v1/servers/{server_id}/webhooks/{webhook_id}/deliveries
```

**Response:**

```json
{
  "deliveries": [
    {
      "id": 1,
      "event_type": "request.received",
      "payload": "{\"event\": \"request.received\", ...}",
      "response_status": 200,
      "response_body": "OK",
      "delivery_time_ms": 150,
      "success": true,
      "delivered_at": "2024-01-01T15:30:00Z"
    }
  ],
  "total": 50
}
```

## System Management

### Health Check

Check system health and status.

```http
GET /admin/api/v1/health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T15:30:00Z",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 5
    },
    "storage": {
      "status": "healthy",
      "free_space_gb": 50.5
    },
    "memory": {
      "status": "healthy",
      "usage_percent": 45.2
    }
  }
}
```

### System Metrics

Get system performance metrics.

```http
GET /admin/api/v1/metrics
```

**Response:**

```json
{
  "timestamp": "2024-01-01T15:30:00Z",
  "system": {
    "cpu_usage_percent": 25.5,
    "memory_usage_percent": 45.2,
    "disk_usage_percent": 60.1,
    "uptime_seconds": 3600
  },
  "application": {
    "active_servers": 3,
    "total_requests": 5000,
    "requests_per_second": 10.5,
    "avg_response_time_ms": 42,
    "error_rate_percent": 1.2
  },
  "database": {
    "connection_pool_size": 10,
    "active_connections": 3,
    "query_count": 1500,
    "avg_query_time_ms": 8
  }
}
```

### System Configuration

Get system configuration.

```http
GET /admin/api/v1/config
```

**Response:**

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 4,
    "log_level": "info"
  },
  "database": {
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "mockloop"
  },
  "auth": {
    "enabled": true,
    "type": "jwt"
  },
  "logging": {
    "level": "info",
    "format": "json",
    "requests": {
      "enabled": true,
      "include_body": true
    }
  }
}
```

### Update System Configuration

Update system configuration (requires admin privileges).

```http
PUT /admin/api/v1/config
```

**Request Body:**

```json
{
  "logging": {
    "level": "debug",
    "requests": {
      "include_body": false
    }
  }
}
```

## Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "spec_url_or_path",
      "reason": "File not found"
    },
    "timestamp": "2024-01-01T15:30:00Z",
    "request_id": "req_123"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `AUTHENTICATION_ERROR` | 401 | Authentication required or failed |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict (e.g., duplicate name) |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

## Rate Limiting

The Admin API implements rate limiting to prevent abuse:

- **Default Limit**: 1000 requests per hour per API key
- **Burst Limit**: 100 requests per minute
- **Headers**: Rate limit information is included in response headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1640995200
X-RateLimit-Retry-After: 60
```

## SDK Examples

### Python SDK

```python
from mockloop_mcp import AdminAPIClient

# Initialize client
client = AdminAPIClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# List servers
servers = await client.list_servers()

# Create scenario
scenario = await client.create_scenario(
    server_id="server_123",
    name="test_scenario",
    config={
        "/pets": {
            "GET": {
                "status": 200,
                "body": {"pets": []}
            }
        }
    }
)

# Query logs with analysis
logs = await client.query_logs(
    server_id="server_123",
    analyze=True,
    time_from="2024-01-01T00:00:00Z"
)
```

### JavaScript SDK

```javascript
import { AdminAPIClient } from '@mockloop/mcp-client';

// Initialize client
const client = new AdminAPIClient({
  baseURL: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

// List servers
const servers = await client.listServers();

// Create scenario
const scenario = await client.createScenario('server_123', {
  name: 'test_scenario',
  config: {
    '/pets': {
      'GET': {
        status: 200,
        body: { pets: [] }
      }
    }
  }
});

// Query logs
const logs = await client.queryLogs('server_123', {
  analyze: true,
  timeFrom: '2024-01-01T00:00:00Z'
});
```

### cURL Examples

```bash
# List servers
curl -H "X-API-Key: your-api-key" \
     http://localhost:8000/admin/api/v1/servers

# Create scenario
curl -X POST \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"name": "test", "config": {...}}' \
     http://localhost:8000/admin/api/v1/servers/server_123/scenarios

# Query logs with analysis
curl -H "X-API-Key: your-api-key" \
     "http://localhost:8000/admin/api/v1/servers/server_123/logs?analyze=true&limit=50"
```

## OpenAPI Specification

The complete Admin API is documented with OpenAPI 3.0 specification available at:

```
http://localhost:8000/admin/api/v1/openapi.json
```

Interactive API documentation is available at:

```
http://localhost:8000/admin/docs
```

## See Also

- **[Core Classes](core-classes.md)**: Core API classes and methods
- **[Configuration Options](configuration.md)**: Admin API configuration
- **[Database Schema](database-schema.md)**: Database structure for API data
- **[MCP Tools](mcp-tools.md)**: MCP tool integration with Admin API