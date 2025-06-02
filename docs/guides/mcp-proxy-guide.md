# MCP Proxy Guide

## Overview

The MockLoop MCP Proxy functionality enables seamless switching between development (mock) and production (proxy) testing environments. This powerful feature allows you to:

- **Start with mocks** during early development when APIs aren't ready
- **Switch to live APIs** for integration testing and validation
- **Use hybrid mode** to combine mock and live responses for comprehensive testing
- **Compare responses** between mock and live APIs to ensure consistency

## Core Concepts

### Proxy Modes

The MCP proxy supports three distinct operational modes:

#### Mock Mode (`MOCK`)
- All requests are handled by generated mock responses
- No external API calls are made
- Ideal for early development and isolated testing
- Consistent, predictable responses

#### Proxy Mode (`PROXY`)
- All requests are forwarded to the live API
- Real-time data and responses
- Requires valid authentication credentials
- Network-dependent operation

#### Hybrid Mode (`HYBRID`)
- Intelligent routing between mock and proxy based on rules
- Conditional switching based on request patterns
- Allows gradual migration from mock to live
- Enables A/B testing scenarios

### Authentication Support

The proxy system supports multiple authentication schemes:

- **API Key**: Header, query parameter, or cookie-based
- **Bearer Token**: OAuth2 and JWT tokens
- **Basic Auth**: Username/password combinations
- **OAuth2**: Full OAuth2 flow support
- **Custom**: Extensible authentication handlers

## Quick Start

### 1. Create an MCP Plugin

```python
from mockloop_mcp.mcp_tools import create_mcp_plugin

# Create a plugin for the Shodan API
plugin_result = await create_mcp_plugin(
    spec_url_or_path="https://api.shodan.io/openapi.json",
    mode="mock",  # Start with mock mode
    plugin_name="shodan_api",
    target_url="https://api.shodan.io",
    auth_config={
        "auth_type": "api_key",
        "credentials": {"api_key": "your-api-key"},
        "location": "query",
        "name": "key"
    }
)
```

### 2. Operating in Different Modes

The proxy mode (mock, proxy, or hybrid) is typically set when creating the MCP plugin using the `mode` parameter in the [`create_mcp_plugin()`](https://github.com/MockLoop/mockloop-mcp/blob/main/src/mockloop_mcp/mcp_tools.py#L1080) tool.

**Example: Creating a plugin directly in Proxy Mode**
```python
# Create a plugin configured for Proxy Mode
proxy_plugin_result = await create_mcp_plugin(
    spec_url_or_path="https://api.shodan.io/openapi.json",
    mode="proxy",  # Set mode to proxy
    plugin_name="shodan_api_proxy_instance", # Consider a distinct name for clarity
    target_url="https://api.shodan.io", # Required for proxy/hybrid modes
    auth_config={ # Ensure authentication is correctly configured for the live API
        "auth_type": "api_key",
        "credentials": {"api_key": "YOUR_ACTUAL_SHODAN_API_KEY"}, # Use your live API key
        "location": "query",
        "name": "key"
    }
)
# The plugin 'shodan_api_proxy_instance' will now operate by forwarding requests to 'https://api.shodan.io'.
```

If you need to change the operational mode for an API after its initial plugin configuration, you would typically re-configure by calling [`create_mcp_plugin()`](https://github.com/MockLoop/mockloop-mcp/blob/main/src/mockloop_mcp/mcp_tools.py#L1080) again with the new desired `mode` and potentially other updated configurations.

While the underlying [`ProxyHandler`](https://github.com/MockLoop/mockloop-mcp/blob/main/src/mockloop_mcp/proxy/proxy_handler.py#L24) class (see API Reference below) contains a [`switch_mode()`](https://github.com/MockLoop/mockloop-mcp/blob/main/src/mockloop_mcp/proxy/proxy_handler.py#L87) method, direct manipulation of `ProxyHandler` instances is generally an advanced use case. The recommended approach for managing proxy behavior is through the `create_mcp_plugin` tool.

### 3. Execute Proxy-Aware Tests

```python
from mockloop_mcp.mcp_tools import execute_test_plan

# Run tests with automatic mode detection
test_results = await execute_test_plan(
    openapi_spec=api_spec,
    server_url="http://localhost:8000",
    mode="auto",  # Automatically detect mock/proxy/hybrid
    validation_mode="strict",
    comparison_config={
        "ignore_fields": ["timestamp", "request_id"],
        "tolerance": 0.1
    },
    report_differences=True
)
```

## Configuration

### Proxy Configuration

```python
from mockloop_mcp.proxy.config import ProxyConfig, AuthConfig, EndpointConfig

# Create proxy configuration
proxy_config = ProxyConfig(
    api_name="example_api",
    base_url="https://api.example.com",
    mode=ProxyMode.HYBRID,
    default_auth=AuthConfig(
        auth_type=AuthType.BEARER_TOKEN,
        credentials={"token": "your-bearer-token"}
    ),
    timeout=30,
    retry_count=3
)

# Add endpoint-specific configuration
endpoint_config = EndpointConfig(
    path="/users/{id}",
    method="GET",
    proxy_url="https://api.example.com/users/{id}",
    timeout=15
)
proxy_config.add_endpoint(endpoint_config)
```

### Authentication Configuration

#### API Key Authentication
```python
auth_config = {
    "auth_type": "api_key",
    "credentials": {
        "api_key": "your-api-key"
    },
    "location": "header",  # or "query", "cookie"
    "name": "X-API-Key"
}
```

#### Bearer Token Authentication
```python
auth_config = {
    "auth_type": "bearer_token",
    "credentials": {
        "token": "your-bearer-token"
    }
}
```

#### Basic Authentication
```python
auth_config = {
    "auth_type": "basic_auth",
    "credentials": {
        "username": "your-username",
        "password": "your-password"
    }
}
```

#### OAuth2 Authentication
```python
auth_config = {
    "auth_type": "oauth2",
    "credentials": {
        "access_token": "your-access-token",
        "refresh_token": "your-refresh-token",
        "client_id": "your-client-id",
        "client_secret": "your-client-secret"
    }
}
```

### Hybrid Mode Routing Rules

```python
from mockloop_mcp.proxy.config import RouteRule

# Route critical endpoints to live API
critical_rule = RouteRule(
    pattern="/api/payments/*",
    mode=ProxyMode.PROXY,
    condition="request.method == 'POST'",
    priority=10
)

# Route development endpoints to mock
dev_rule = RouteRule(
    pattern="/api/dev/*",
    mode=ProxyMode.MOCK,
    priority=5
)

proxy_config.add_route_rule(critical_rule)
proxy_config.add_route_rule(dev_rule)
```

## Advanced Features

### Response Comparison

The proxy system can automatically compare responses between mock and live APIs:

```python
comparison_config = {
    "ignore_fields": [
        "timestamp",
        "request_id", 
        "server_time",
        "response_time"
    ],
    "tolerance": 0.1,  # 10% tolerance for numeric values
    "strict_arrays": False,  # Allow array order differences
    "compare_headers": True
}

test_results = await execute_test_plan(
    openapi_spec=spec,
    server_url="http://localhost:8000",
    mode="hybrid",
    comparison_config=comparison_config,
    report_differences=True
)
```

### Conditional Routing

Use Python expressions for dynamic routing decisions:

```python
# Route based on request headers
header_rule = RouteRule(
    pattern="/api/*",
    mode=ProxyMode.PROXY,
    condition="'X-Test-Mode' not in request.headers",
    priority=8
)

# Route based on request parameters
param_rule = RouteRule(
    pattern="/api/search",
    mode=ProxyMode.MOCK,
    condition="request.params.get('mock') == 'true'",
    priority=9
)
```

### Performance Monitoring

Monitor proxy performance and response times:

```python
# Enable performance monitoring
test_results = await execute_test_plan(
    openapi_spec=spec,
    server_url="http://localhost:8000",
    mode="proxy",
    monitor_performance=True,
    collect_logs=True
)

# Analyze performance metrics
metrics = get_performance_metrics(
    test_results,
    metric_types=["response_time", "throughput", "error_rate"]
)
```

## Best Practices

### 1. Start with Mock Mode
- Begin development with mock responses
- Ensure your application works with predictable data
- Test edge cases and error scenarios

### 2. Gradual Migration to Proxy
- Use hybrid mode to gradually introduce live API calls
- Start with read-only endpoints
- Monitor for differences between mock and live responses

### 3. Authentication Management
- Store credentials securely
- Use environment variables for sensitive data
- Implement credential rotation strategies

### 4. Error Handling
- Configure appropriate timeouts and retry policies
- Handle network failures gracefully
- Implement fallback mechanisms

### 5. Testing Strategy
- Compare mock and live responses regularly
- Use validation modes appropriate for your testing phase
- Monitor performance impact of proxy calls

## Troubleshooting

### Common Issues

#### Authentication Failures
```python
# Check authentication status
from mockloop_mcp.proxy.auth_handler import AuthHandler

auth_handler = AuthHandler()
status = auth_handler.get_auth_status("your_api")
print(f"Authentication status: {status}")
```

#### Network Timeouts
```python
# Increase timeout values
endpoint_config = EndpointConfig(
    path="/slow-endpoint",
    timeout=60,  # Increase to 60 seconds
    retry_count=5
)
```

#### Response Differences
```python
# Use more lenient comparison settings
comparison_config = {
    "ignore_fields": ["timestamp", "server_info"],
    "tolerance": 0.2,  # Increase tolerance
    "strict_arrays": False
}
```

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
logging.getLogger("mockloop_mcp.proxy").setLevel(logging.DEBUG)
```

## Integration Examples

### CI/CD Pipeline Integration

```yaml
# .github/workflows/api-tests.yml
name: API Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install mockloop-mcp
      
      - name: Run mock tests
        run: |
          python -c "
          import asyncio
          from mockloop_mcp.mcp_tools import execute_test_plan
          
          async def run_tests():
              results = await execute_test_plan(
                  openapi_spec='api-spec.json',
                  server_url='http://localhost:8000',
                  mode='mock'
              )
              print(f'Tests completed: {results}')
          
          asyncio.run(run_tests())
          "
      
      - name: Run proxy validation (if API key available)
        if: env.API_KEY
        run: |
          python -c "
          import asyncio
          from mockloop_mcp.mcp_tools import execute_test_plan
          
          async def run_proxy_tests():
              results = await execute_test_plan(
                  openapi_spec='api-spec.json',
                  server_url='http://localhost:8000',
                  mode='proxy',
                  validation_mode='soft'
              )
              print(f'Proxy validation: {results}')
          
          asyncio.run(run_proxy_tests())
          "
        env:
          API_KEY: ${{ secrets.API_KEY }}
```

### Docker Integration

```dockerfile
# Dockerfile for proxy-enabled testing
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set environment variables for proxy configuration
ENV PROXY_MODE=hybrid
ENV API_BASE_URL=https://api.example.com
ENV AUTH_TYPE=bearer_token

CMD ["python", "run_proxy_tests.py"]
```

## API Reference

### Core Classes

- [`ProxyConfig`](https://github.com/MockLoop/mockloop-mcp/blob/main/src/mockloop_mcp/proxy/config.py#L133): Main configuration class
- [`ProxyHandler`](https://github.com/MockLoop/mockloop-mcp/blob/main/src/mockloop_mcp/proxy/proxy_handler.py#L24): Request handling and routing. Note: The detailed implementation for specific request handling methods may be under development. Users typically interact with proxy capabilities through higher-level tools like [`create_mcp_plugin()`](https://github.com/MockLoop/mockloop-mcp/blob/main/src/mockloop_mcp/mcp_tools.py#L1080).
- [`AuthHandler`](https://github.com/MockLoop/mockloop-mcp/blob/main/src/mockloop_mcp/proxy/auth_handler.py): Authentication management
- [`PluginManager`](https://github.com/MockLoop/mockloop-mcp/blob/main/src/mockloop_mcp/proxy/plugin_manager.py): Plugin lifecycle management

### MCP Tools

- [`create_mcp_plugin()`](https://github.com/MockLoop/mockloop-mcp/blob/main/src/mockloop_mcp/mcp_tools.py#L1080): Create dynamic MCP plugins
- [`execute_test_plan()`](https://github.com/MockLoop/mockloop-mcp/blob/main/src/mockloop_mcp/mcp_tools.py#L577): Execute proxy-aware test plans

For detailed API documentation, see the [API Reference](../api/).