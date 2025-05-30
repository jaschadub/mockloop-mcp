# Advanced Features

Explore the powerful advanced capabilities of MockLoop MCP for sophisticated testing and development scenarios.

## Dynamic Response Management

Update API responses in real-time without restarting servers.

### Real-Time Response Updates

```python
# Update specific endpoint response
await mockloop.manage_mock_data(
    server_url="http://localhost:8000",
    operation="update_response",
    endpoint_path="/users/1",
    response_data={
        "id": 1,
        "name": "Updated User",
        "email": "updated@example.com"
    }
)
```

### Conditional Responses

Create responses that change based on request parameters:

```python
# Different responses based on query parameters
responses = {
    "status=active": {"users": [...]},
    "status=inactive": {"users": []},
    "status=pending": {"error": "Access denied"}
}
```

## Scenario Management

Create and manage comprehensive test scenarios.

### Creating Scenarios

```python
# Create error testing scenario
await mockloop.manage_mock_data(
    server_url="http://localhost:8000",
    operation="create_scenario",
    scenario_name="error_testing",
    scenario_config={
        "description": "Test error conditions",
        "endpoints": {
            "/users": {"GET": {"status": 500, "error": "Internal server error"}},
            "/orders": {"POST": {"status": 429, "error": "Rate limit exceeded"}}
        }
    }
)
```

### Switching Scenarios

```python
# Switch to different scenario
await mockloop.manage_mock_data(
    server_url="http://localhost:8000",
    operation="switch_scenario",
    scenario_name="error_testing"
)
```

## Performance Testing

Simulate various performance conditions.

### Response Delays

```python
# Add realistic delays
scenario_config = {
    "endpoints": {
        "/slow-endpoint": {
            "GET": {
                "status": 200,
                "delay_ms": 2000,
                "response": {"data": "..."}
            }
        }
    }
}
```

### Load Testing

```bash
# Use Apache Bench for load testing
ab -n 1000 -c 10 http://localhost:8000/api/endpoint

# Use wrk for advanced load testing
wrk -t12 -c400 -d30s http://localhost:8000/api/endpoint
```

## Advanced Analytics

Deep dive into request patterns and performance metrics.

### Custom Analytics Queries

```python
# Analyze specific patterns
logs = await mockloop.query_mock_logs(
    server_url="http://localhost:8000",
    path_pattern="/api/v1/.*",
    time_from="2025-01-01T00:00:00Z",
    analyze=True
)

# Extract insights
performance = logs["analysis"]["performance_metrics"]
print(f"P95 response time: {performance['p95_response_time_ms']}ms")
```

### Real-Time Monitoring

```python
# Continuous monitoring
async def monitor_performance():
    while True:
        logs = await mockloop.query_mock_logs(
            server_url="http://localhost:8000",
            limit=100,
            analyze=True
        )
        
        if logs["analysis"]["error_rate_percent"] > 5:
            # Alert or take action
            await handle_high_error_rate()
        
        await asyncio.sleep(60)  # Check every minute
```

## Webhook Integration

Set up webhooks for real-time notifications.

### Webhook Configuration

```python
# Configure webhook endpoints
webhook_config = {
    "url": "https://your-app.com/webhooks/mockloop",
    "events": ["request.completed", "error.occurred"],
    "headers": {
        "Authorization": "Bearer your-token"
    }
}
```

### Event Types

- `request.completed`: Fired after each API request
- `error.occurred`: Fired when errors happen
- `scenario.switched`: Fired when scenarios change
- `performance.threshold`: Fired when performance thresholds are exceeded

## Custom Response Logic

Implement sophisticated response logic.

### Stateful Responses

```python
# Responses that change based on previous requests
class StatefulResponder:
    def __init__(self):
        self.request_count = 0
        self.user_sessions = {}
    
    def get_response(self, request):
        self.request_count += 1
        
        if self.request_count > 100:
            return {"error": "Rate limit exceeded", "status": 429}
        
        return {"data": "...", "request_number": self.request_count}
```

### Data Persistence

```python
# Persist data between requests
class PersistentMock:
    def __init__(self):
        self.data_store = {}
    
    def handle_post(self, data):
        # Store data
        item_id = len(self.data_store) + 1
        self.data_store[item_id] = data
        return {"id": item_id, **data}
    
    def handle_get(self, item_id):
        # Retrieve data
        return self.data_store.get(item_id, {"error": "Not found"})
```

## Integration Patterns

Advanced integration with development workflows.

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Setup Mock Environment
  run: |
    mockloop generate_mock_api --spec ./api-spec.yaml
    cd generated_mocks/api_mock
    docker-compose up -d
    
- name: Run Integration Tests
  run: |
    # Run tests against mock
    pytest tests/integration/
    
- name: Analyze Test Results
  run: |
    mockloop query_mock_logs \
      --server-url http://localhost:8000 \
      --analyze > test-analysis.json
```

### Development Automation

```python
# Auto-update mocks based on API changes
class MockAutoUpdater:
    def __init__(self, spec_url, mock_server_url):
        self.spec_url = spec_url
        self.mock_server_url = mock_server_url
        self.last_spec_hash = None
    
    async def check_for_updates(self):
        current_spec = await fetch_spec(self.spec_url)
        current_hash = hash(current_spec)
        
        if current_hash != self.last_spec_hash:
            await self.update_mock_server(current_spec)
            self.last_spec_hash = current_hash
    
    async def update_mock_server(self, spec):
        # Regenerate mock with new spec
        await mockloop.generate_mock_api(
            spec_url_or_path=self.spec_url,
            output_dir_name="auto_updated_mock"
        )
```

## Security Features

Advanced security testing capabilities.

### Authentication Testing

```python
# Test different authentication states
auth_scenarios = {
    "valid_token": {
        "headers": {"Authorization": "Bearer valid-token"},
        "response": {"data": "..."}
    },
    "invalid_token": {
        "headers": {"Authorization": "Bearer invalid-token"},
        "response": {"error": "Unauthorized", "status": 401}
    },
    "expired_token": {
        "headers": {"Authorization": "Bearer expired-token"},
        "response": {"error": "Token expired", "status": 401}
    }
}
```

### Rate Limiting Simulation

```python
# Simulate rate limiting
class RateLimiter:
    def __init__(self, requests_per_minute=60):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
    
    def check_rate_limit(self):
        now = time.time()
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        if len(self.request_times) >= self.requests_per_minute:
            return {"error": "Rate limit exceeded", "status": 429}
        
        self.request_times.append(now)
        return None  # Allow request
```

## Best Practices

### 1. Scenario Organization

```python
# Organize scenarios by purpose
scenarios = {
    "development": {
        "description": "Fast responses for development",
        "default_delay_ms": 10
    },
    "testing": {
        "description": "Realistic delays and errors",
        "default_delay_ms": 100,
        "error_rate": 0.05
    },
    "demo": {
        "description": "Polished responses for demos",
        "default_delay_ms": 50,
        "error_rate": 0
    }
}
```

### 2. Performance Monitoring

```python
# Set up performance alerts
performance_thresholds = {
    "max_response_time_ms": 1000,
    "max_error_rate_percent": 5,
    "max_requests_per_second": 100
}

async def check_performance_thresholds():
    logs = await mockloop.query_mock_logs(analyze=True)
    metrics = logs["analysis"]["performance_metrics"]
    
    for threshold, limit in performance_thresholds.items():
        if metrics.get(threshold, 0) > limit:
            await send_alert(f"Threshold exceeded: {threshold}")
```

### 3. Data Management

```python
# Clean up old data regularly
async def cleanup_old_data():
    # Remove logs older than 30 days
    cutoff_date = datetime.now() - timedelta(days=30)
    
    await mockloop.query_mock_logs(
        time_to=cutoff_date.isoformat(),
        operation="delete"
    )
```

## Next Steps

- **[Performance Monitoring](performance-monitoring.md)**: Deep dive into analytics
- **[Scenario Management](scenario-management.md)**: Advanced scenario techniques
- **[Docker Integration](docker-integration.md)**: Container deployment strategies
- **[AI Integration](../ai-integration/overview.md)**: Connect with AI frameworks