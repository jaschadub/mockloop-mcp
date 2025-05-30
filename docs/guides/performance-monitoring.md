# Performance Monitoring

MockLoop provides comprehensive performance monitoring capabilities to help you track and analyze the behavior of your mock servers and the applications that interact with them.

## Overview

Performance monitoring in MockLoop includes:

- **Request/Response Logging**: Detailed logging of all API interactions
- **Performance Metrics**: Response times, throughput, and error rates
- **Real-time Analytics**: Live monitoring of server performance
- **Historical Analysis**: Trend analysis and performance over time

## Request Logging

### Automatic Logging

All requests to your mock servers are automatically logged with detailed information:

```python
# Query recent requests
from mockloop_mcp import query_mock_logs

logs = query_mock_logs(
    server_url="http://localhost:8000",
    limit=100,
    analyze=True
)

print(f"Total requests: {logs['total_count']}")
print(f"Average response time: {logs['analysis']['avg_response_time']}ms")
```

### Log Data Structure

Each log entry contains:

- **Timestamp**: When the request was made
- **Method**: HTTP method (GET, POST, etc.)
- **Path**: Request path and query parameters
- **Headers**: Request and response headers
- **Body**: Request and response bodies
- **Response Time**: Time taken to process the request
- **Status Code**: HTTP response status

### Filtering Logs

You can filter logs by various criteria:

```python
# Filter by method
get_requests = query_mock_logs(
    server_url="http://localhost:8000",
    method="GET"
)

# Filter by path pattern
api_requests = query_mock_logs(
    server_url="http://localhost:8000",
    path_pattern="/api/*"
)

# Filter by time range
recent_requests = query_mock_logs(
    server_url="http://localhost:8000",
    time_from="2024-01-01T00:00:00Z",
    time_to="2024-01-02T00:00:00Z"
)
```

## Performance Metrics

### Response Time Analysis

MockLoop tracks response times for all requests:

```python
# Get performance analysis
analysis = query_mock_logs(
    server_url="http://localhost:8000",
    analyze=True
)

print(f"Average response time: {analysis['analysis']['avg_response_time']}ms")
print(f"95th percentile: {analysis['analysis']['p95_response_time']}ms")
print(f"Slowest request: {analysis['analysis']['max_response_time']}ms")
```

### Throughput Monitoring

Track request volume and patterns:

```python
# Analyze request patterns
patterns = analysis['analysis']['request_patterns']
print(f"Most common endpoint: {patterns['top_endpoints'][0]}")
print(f"Peak hour: {patterns['peak_hour']}")
print(f"Requests per minute: {patterns['avg_rpm']}")
```

### Error Rate Tracking

Monitor error rates and patterns:

```python
# Error analysis
errors = analysis['analysis']['error_analysis']
print(f"Error rate: {errors['error_rate']}%")
print(f"Most common errors: {errors['common_status_codes']}")
```

## Real-time Monitoring

### Live Dashboard

MockLoop provides a web-based dashboard for real-time monitoring:

```bash
# Access the admin dashboard
curl http://localhost:8000/admin/dashboard
```

The dashboard includes:

- Live request feed
- Performance graphs
- Error rate charts
- Endpoint usage statistics

### WebSocket Monitoring

For real-time updates in your applications:

```javascript
// Connect to monitoring WebSocket
const ws = new WebSocket('ws://localhost:8000/admin/monitor');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('New request:', data);
    updateDashboard(data);
};
```

## Performance Testing Integration

### Load Testing Support

MockLoop is designed to handle high-load scenarios:

```python
# Configure for high-load testing
from mockloop_mcp import manage_mock_data

# Enable performance mode
manage_mock_data(
    server_url="http://localhost:8000",
    operation="configure_performance",
    config={
        "enable_detailed_logging": False,  # Reduce overhead
        "batch_log_writes": True,
        "response_delay": 0  # Remove artificial delays
    }
)
```

### Stress Testing

Monitor performance under stress:

```bash
# Run load test with monitoring
ab -n 10000 -c 100 http://localhost:8000/api/users

# Analyze results
python -c "
from mockloop_mcp import query_mock_logs
logs = query_mock_logs('http://localhost:8000', analyze=True)
print('Performance under load:', logs['analysis'])
"
```

## Custom Metrics

### Adding Custom Metrics

You can add custom performance metrics:

```python
# Add custom timing metrics
import time
from mockloop_mcp import log_custom_metric

start_time = time.time()
# Your application logic here
end_time = time.time()

log_custom_metric(
    server_url="http://localhost:8000",
    metric_name="custom_operation_time",
    value=end_time - start_time,
    tags={"operation": "data_processing"}
)
```

### Metric Aggregation

Aggregate custom metrics over time:

```python
# Query custom metrics
metrics = query_custom_metrics(
    server_url="http://localhost:8000",
    metric_name="custom_operation_time",
    time_range="1h"
)

print(f"Average operation time: {metrics['avg']}s")
print(f"Max operation time: {metrics['max']}s")
```

## Alerting and Notifications

### Performance Alerts

Set up alerts for performance thresholds:

```python
# Configure performance alerts
manage_mock_data(
    server_url="http://localhost:8000",
    operation="configure_alerts",
    config={
        "response_time_threshold": 1000,  # ms
        "error_rate_threshold": 5,  # percent
        "alert_webhook": "https://your-webhook.com/alerts"
    }
)
```

### Webhook Notifications

Receive notifications when thresholds are exceeded:

```json
{
    "alert_type": "performance_threshold",
    "metric": "response_time",
    "value": 1500,
    "threshold": 1000,
    "timestamp": "2024-01-01T12:00:00Z",
    "server_url": "http://localhost:8000"
}
```

## Export and Analysis

### Data Export

Export performance data for external analysis:

```python
# Export logs to CSV
export_logs(
    server_url="http://localhost:8000",
    format="csv",
    output_file="performance_data.csv",
    time_range="24h"
)

# Export to JSON for programmatic analysis
export_logs(
    server_url="http://localhost:8000",
    format="json",
    output_file="performance_data.json"
)
```

### Integration with Monitoring Tools

MockLoop can integrate with popular monitoring tools:

```yaml
# Prometheus integration
prometheus:
  enabled: true
  port: 9090
  metrics:
    - request_duration
    - request_count
    - error_rate

# Grafana dashboard
grafana:
  dashboard_url: "http://localhost:3000/d/mockloop"
```

## Best Practices

### Performance Optimization

1. **Disable detailed logging** in production for better performance
2. **Use batch logging** for high-throughput scenarios
3. **Set appropriate log retention** policies
4. **Monitor resource usage** of the mock server itself

### Monitoring Strategy

1. **Set up baseline metrics** before load testing
2. **Monitor both mock server and client performance**
3. **Use alerts for proactive issue detection**
4. **Regular performance reviews** and optimization

### Troubleshooting Performance Issues

Common performance issues and solutions:

- **High response times**: Check for complex response generation logic
- **Memory usage**: Review log retention settings
- **CPU usage**: Consider disabling detailed request logging
- **Disk I/O**: Use in-memory storage for temporary testing

## Next Steps

- [Scenario Management](scenario-management.md) - Learn about managing test scenarios
- [Docker Integration](docker-integration.md) - Deploy with performance monitoring
- [Advanced Features](advanced-features.md) - Explore advanced monitoring capabilities