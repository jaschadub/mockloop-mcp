# Basic Usage

This guide covers the fundamental features and workflows of MockLoop MCP, helping you master the core functionality for generating and managing mock API servers.

## Core MCP Tools

MockLoop MCP provides four primary tools for managing mock servers:

### 1. `generate_mock_api`

Generate a complete mock server from an API specification.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `spec_url_or_path` | string | ✅ | - | URL or local path to API specification |
| `output_dir_name` | string | ❌ | Auto-generated | Custom directory name |
| `auth_enabled` | boolean | ❌ | `true` | Enable authentication middleware |
| `webhooks_enabled` | boolean | ❌ | `true` | Enable webhook support |
| `admin_ui_enabled` | boolean | ❌ | `true` | Enable admin interface |
| `storage_enabled` | boolean | ❌ | `true` | Enable storage functionality |

#### Examples

**Basic Generation:**
```
Generate a mock server from https://petstore3.swagger.io/api/v3/openapi.json
```

**Custom Configuration:**
```
Generate a mock server with these settings:
- Specification: https://api.github.com/
- Directory name: github_api_mock
- Disable authentication
- Enable all other features
```

**Local File:**
```
Generate a mock server from the local file ./my-api.yaml with directory name "my_custom_api"
```

### 2. `query_mock_logs`

Analyze request logs from running mock servers with advanced filtering and insights.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `server_url` | string | ✅ | - | URL of the mock server |
| `limit` | integer | ❌ | 100 | Maximum logs to return |
| `offset` | integer | ❌ | 0 | Pagination offset |
| `method` | string | ❌ | - | Filter by HTTP method |
| `path_pattern` | string | ❌ | - | Regex pattern for paths |
| `time_from` | string | ❌ | - | Start time (ISO format) |
| `time_to` | string | ❌ | - | End time (ISO format) |
| `include_admin` | boolean | ❌ | `false` | Include admin requests |
| `analyze` | boolean | ❌ | `true` | Perform analysis |

#### Examples

**Basic Analysis:**
```
Analyze the logs for my mock server at http://localhost:8000
```

**Filtered Analysis:**
```
Show me the last 50 GET requests to /pet/* endpoints from my server at http://localhost:8000 in the last hour
```

**Performance Focus:**
```
Analyze performance metrics for http://localhost:8000 including response times and error rates
```

### 3. `discover_mock_servers`

Find running MockLoop servers and generated configurations.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ports` | array | ❌ | [8000-8005, 3000-3001, 5000-5001] | Ports to scan |
| `check_health` | boolean | ❌ | `true` | Perform health checks |
| `include_generated` | boolean | ❌ | `true` | Include generated configs |

#### Examples

**Discover All Servers:**
```
Find all running MockLoop servers on my system
```

**Custom Port Range:**
```
Check for mock servers on ports 8000-8010 and 9000-9005
```

### 4. `manage_mock_data`

Manage dynamic responses and scenarios without server restart.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `server_url` | string | ✅ | - | URL of the mock server |
| `operation` | string | ✅ | - | Operation type |
| `endpoint_path` | string | ❌ | - | API endpoint path |
| `response_data` | object | ❌ | - | New response data |
| `scenario_name` | string | ❌ | - | Scenario name |
| `scenario_config` | object | ❌ | - | Scenario configuration |

#### Operations

- `update_response`: Update response for specific endpoint
- `create_scenario`: Create new test scenario
- `switch_scenario`: Switch to different scenario
- `list_scenarios`: List available scenarios

#### Examples

**Update Response:**
```
Update the response for GET /pet/1 on http://localhost:8000 to return:
{
  "id": 1,
  "name": "Fluffy Cat",
  "status": "available"
}
```

**Create Scenario:**
```
Create a scenario called "error_testing" for http://localhost:8000 where:
- GET /pet/1 returns 404
- POST /pet returns 500
- Other endpoints work normally
```

## Common Workflows

### Workflow 1: API Development

When developing a new API, use MockLoop to create a working backend:

1. **Create OpenAPI Specification**
   ```yaml
   # my-api.yaml
   openapi: 3.0.0
   info:
     title: My API
     version: 1.0.0
   paths:
     /users:
       get:
         responses:
           '200':
             description: List of users
   ```

2. **Generate Mock Server**
   ```
   Generate a mock server from ./my-api.yaml
   ```

3. **Start Development**
   ```bash
   cd generated_mocks/my_api/
   docker-compose up -d
   ```

4. **Iterate and Test**
   - Update your API specification
   - Regenerate the mock server
   - Test with your frontend/client

### Workflow 2: Frontend Development

Use MockLoop to provide realistic backend responses:

1. **Use Existing API Spec**
   ```
   Generate a mock server from https://api.example.com/openapi.json
   ```

2. **Customize Responses**
   ```
   Update the response for GET /users to return realistic test data with 10 users
   ```

3. **Create Test Scenarios**
   ```
   Create scenarios for:
   - Normal operation
   - Error conditions
   - Edge cases
   ```

4. **Develop Frontend**
   - Point your frontend to `http://localhost:8000`
   - Test different scenarios
   - Handle error conditions

### Workflow 3: API Testing

Create comprehensive test environments:

1. **Generate Test Server**
   ```
   Generate a mock server for testing from ./api-spec.yaml with name "test_api"
   ```

2. **Create Test Scenarios**
   ```
   Create test scenarios:
   - "happy_path": All endpoints return success
   - "error_conditions": Various error responses
   - "performance_test": Delayed responses
   ```

3. **Run Test Suite**
   ```bash
   # Switch to error scenario
   curl -X POST http://localhost:8000/admin/api/scenarios/switch \
     -d '{"scenario": "error_conditions"}'
   
   # Run tests
   pytest tests/error_tests.py
   ```

4. **Analyze Results**
   ```
   Analyze test results from http://localhost:8000 focusing on error rates and response times
   ```

### Workflow 4: Integration Testing

Test service integrations:

1. **Mock External Dependencies**
   ```
   Generate mock servers for:
   - Payment service API
   - User authentication API
   - Notification service API
   ```

2. **Configure Service URLs**
   ```bash
   export PAYMENT_API_URL=http://localhost:8001
   export AUTH_API_URL=http://localhost:8002
   export NOTIFICATION_API_URL=http://localhost:8003
   ```

3. **Create Integration Scenarios**
   ```
   Create scenarios for different integration states:
   - All services healthy
   - Payment service down
   - Authentication failures
   ```

4. **Run Integration Tests**
   ```bash
   # Test with all services up
   npm test integration

   # Test with payment service errors
   # Switch payment mock to error scenario
   npm test integration:payment-errors
   ```

## Working with Different API Formats

### OpenAPI 3.0 (JSON)

```
Generate a mock server from https://petstore3.swagger.io/api/v3/openapi.json
```

### OpenAPI 3.0 (YAML)

```
Generate a mock server from ./my-api.yaml
```

### Swagger 2.0

```
Generate a mock server from https://petstore.swagger.io/v2/swagger.json
```

### Local Files

```
Generate a mock server from /path/to/my/api-specification.json
```

## Response Customization

### Static Response Updates

Update responses for specific endpoints:

```
Update the GET /users response to return:
[
  {"id": 1, "name": "Alice", "email": "alice@example.com"},
  {"id": 2, "name": "Bob", "email": "bob@example.com"}
]
```

### Dynamic Response Logic

Create responses with dynamic data:

```
Update GET /users/{id} to return user data where:
- id 1-10: Return valid user data
- id > 10: Return 404 error
- id < 1: Return 400 error
```

### Response Headers

Customize response headers:

```
Update GET /api/data to include these headers:
- X-Rate-Limit: 1000
- X-Rate-Remaining: 999
- Cache-Control: max-age=3600
```

## Monitoring and Analytics

### Real-time Monitoring

Monitor your mock servers in real-time:

1. **Admin Dashboard**: `http://localhost:8000/admin`
2. **Health Endpoint**: `http://localhost:8000/health`
3. **Metrics API**: `http://localhost:8000/admin/api/metrics`

### Performance Analysis

```
Analyze performance for http://localhost:8000 over the last 24 hours
```

Expected output:
- Request volume trends
- Response time percentiles
- Error rate analysis
- Popular endpoints
- Client patterns

### Log Analysis

```
Show me all failed requests (4xx/5xx) from http://localhost:8000 in the last hour
```

### Custom Analytics

```bash
# Get raw log data
curl "http://localhost:8000/admin/api/logs/search?limit=1000" | jq '.'

# Filter specific patterns
curl "http://localhost:8000/admin/api/logs/search?path_pattern=/api/v1/*&method=POST"
```

## Error Handling

### Common Error Scenarios

Create realistic error responses:

```
Create an error scenario where:
- 10% of requests return 500 errors
- 5% of requests return 429 rate limit errors
- 2% of requests timeout after 30 seconds
```

### Debugging Failed Requests

When requests fail:

1. **Check Admin Logs**: View detailed request/response data
2. **Analyze Patterns**: Look for common failure points
3. **Review Configuration**: Verify server settings
4. **Test Scenarios**: Switch to different test scenarios

### Error Response Customization

```
Update error responses to include:
- Detailed error messages
- Error codes
- Suggested actions
- Request correlation IDs
```

## Best Practices

### 1. Organize Your Mocks

```bash
# Use descriptive directory names
generated_mocks/
├── user_service_v1/
├── payment_api_prod/
├── notification_service_test/
└── external_partner_api/
```

### 2. Version Your Specifications

```bash
# Keep API specs in version control
api-specs/
├── user-service/
│   ├── v1.0.yaml
│   ├── v1.1.yaml
│   └── v2.0.yaml
└── payment-service/
    └── v1.0.json
```

### 3. Use Scenarios Effectively

```
Create scenarios for:
- Development: Fast, successful responses
- Testing: Various error conditions
- Performance: Realistic delays
- Demo: Polished, consistent data
```

### 4. Monitor Resource Usage

```bash
# Check Docker resource usage
docker stats

# Monitor disk space
du -sh generated_mocks/*/db/

# Check log file sizes
ls -lh generated_mocks/*/logs/
```

### 5. Regular Cleanup

```bash
# Clean old log files
find generated_mocks/*/logs/ -name "*.log" -mtime +7 -delete

# Remove unused mock servers
rm -rf generated_mocks/old_unused_mock/
```

## Troubleshooting

### Server Won't Start

1. **Check Port Availability**
   ```bash
   lsof -i :8000
   ```

2. **Verify Dependencies**
   ```bash
   pip list | grep fastapi
   ```

3. **Check Logs**
   ```bash
   tail -f generated_mocks/my_mock/logs/server.log
   ```

### Requests Failing

1. **Verify Server Status**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check Admin Interface**
   Visit `http://localhost:8000/admin`

3. **Review Request Logs**
   ```
   Show me the last 10 failed requests from http://localhost:8000
   ```

### Performance Issues

1. **Analyze Performance**
   ```
   Analyze performance bottlenecks for http://localhost:8000
   ```

2. **Check Resource Usage**
   ```bash
   docker stats
   htop
   ```

3. **Optimize Configuration**
   - Reduce logging verbosity
   - Increase worker processes
   - Enable response caching

## Next Steps

Now that you understand the basic usage, explore:

- **[Advanced Features](advanced-features.md)**: Dynamic responses, scenarios, and automation
- **[Performance Monitoring](performance-monitoring.md)**: Deep dive into analytics
- **[AI Integration](../ai-integration/overview.md)**: Connect with AI frameworks
- **[API Reference](../api/mcp-tools.md)**: Complete tool documentation

For specific use cases, see:
- **[Docker Integration](docker-integration.md)**: Container deployment strategies
- **[Scenario Management](scenario-management.md)**: Advanced testing workflows
- **[Request/Response Logging](logging.md)**: Comprehensive logging strategies