# Logging

MockLoop provides comprehensive logging capabilities to help you monitor, debug, and analyze your mock servers and the interactions they handle.

## Overview

MockLoop's logging system includes:

- **Request/Response Logging**: Detailed logging of all API interactions
- **Application Logging**: Server events, errors, and operational information
- **Performance Logging**: Timing and performance metrics
- **Custom Logging**: Application-specific log entries
- **Structured Logging**: JSON-formatted logs for easy parsing

## Log Types

### Request Logs

Every API request is automatically logged with comprehensive details:

```python
from mockloop_mcp import query_mock_logs

# Query recent request logs
logs = query_mock_logs(
    server_url="http://localhost:8000",
    limit=50
)

for log in logs['logs']:
    print(f"{log['timestamp']} {log['method']} {log['path']} - {log['status_code']}")
```

Request log structure:
```json
{
    "id": "req_123456789",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "method": "POST",
    "path": "/api/users",
    "query_params": {"page": "1", "limit": "10"},
    "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer token123"
    },
    "request_body": {"name": "John", "email": "john@example.com"},
    "response_body": {"id": 1, "name": "John", "email": "john@example.com"},
    "status_code": 201,
    "response_time_ms": 45,
    "scenario": "default",
    "client_ip": "192.168.1.100",
    "user_agent": "curl/7.68.0"
}
```

### Application Logs

Server events and operational information:

```python
# Access application logs
app_logs = query_mock_logs(
    server_url="http://localhost:8000",
    include_admin=True,
    path_pattern="/admin/logs"
)
```

Application log levels:
- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error conditions that don't stop the server
- **CRITICAL**: Serious errors that may cause server shutdown

### Performance Logs

Timing and performance metrics:

```python
# Query performance logs
perf_logs = query_mock_logs(
    server_url="http://localhost:8000",
    analyze=True
)

print(f"Average response time: {perf_logs['analysis']['avg_response_time']}ms")
print(f"Slowest endpoint: {perf_logs['analysis']['slowest_endpoint']}")
```

## Log Configuration

### Basic Configuration

Configure logging levels and output:

```python
from mockloop_mcp import manage_mock_data

# Configure logging
manage_mock_data(
    server_url="http://localhost:8000",
    operation="configure_logging",
    config={
        "log_level": "INFO",
        "log_format": "json",
        "log_requests": True,
        "log_responses": True,
        "log_headers": True,
        "log_body": True
    }
)
```

### Environment Variables

Configure logging via environment variables:

```bash
# Set log level
export MOCKLOOP_LOG_LEVEL=DEBUG

# Configure log format
export MOCKLOOP_LOG_FORMAT=json

# Enable/disable request logging
export MOCKLOOP_LOG_REQUESTS=true
export MOCKLOOP_LOG_RESPONSES=true

# Configure log file
export MOCKLOOP_LOG_FILE=/var/log/mockloop/server.log
```

### Configuration File

Use a configuration file for complex setups:

```yaml
# logging.yaml
logging:
  version: 1
  disable_existing_loggers: false
  
  formatters:
    json:
      format: '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
    simple:
      format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  
  handlers:
    console:
      class: logging.StreamHandler
      level: INFO
      formatter: json
      stream: ext://sys.stdout
    
    file:
      class: logging.handlers.RotatingFileHandler
      level: DEBUG
      formatter: json
      filename: /var/log/mockloop/server.log
      maxBytes: 10485760  # 10MB
      backupCount: 5
    
    requests:
      class: logging.handlers.RotatingFileHandler
      level: INFO
      formatter: json
      filename: /var/log/mockloop/requests.log
      maxBytes: 52428800  # 50MB
      backupCount: 10
  
  loggers:
    mockloop:
      level: DEBUG
      handlers: [console, file]
      propagate: false
    
    mockloop.requests:
      level: INFO
      handlers: [requests]
      propagate: false
  
  root:
    level: WARNING
    handlers: [console]
```

## Log Filtering and Querying

### Basic Filtering

Filter logs by various criteria:

```python
# Filter by HTTP method
get_logs = query_mock_logs(
    server_url="http://localhost:8000",
    method="GET"
)

# Filter by path pattern
api_logs = query_mock_logs(
    server_url="http://localhost:8000",
    path_pattern="/api/*"
)

# Filter by time range
recent_logs = query_mock_logs(
    server_url="http://localhost:8000",
    time_from="2024-01-01T00:00:00Z",
    time_to="2024-01-01T23:59:59Z"
)

# Filter by status code
error_logs = query_mock_logs(
    server_url="http://localhost:8000",
    status_code_range=[400, 599]
)
```

### Advanced Querying

Use advanced query capabilities:

```python
# Complex filtering
logs = query_mock_logs(
    server_url="http://localhost:8000",
    filters={
        "method": ["GET", "POST"],
        "status_code": {"gte": 200, "lt": 300},
        "response_time": {"gte": 100},  # Slow requests
        "scenario": "performance_test",
        "client_ip": "192.168.1.*"
    }
)

# Search in request/response bodies
search_logs = query_mock_logs(
    server_url="http://localhost:8000",
    search={
        "request_body": "email",
        "response_body": "error"
    }
)
```

### SQL-like Queries

For complex analysis, use SQL-like queries:

```python
# Direct database query
import sqlite3

conn = sqlite3.connect('mock_server/logs/requests.db')
cursor = conn.cursor()

# Find slow requests by endpoint
cursor.execute("""
    SELECT path, AVG(response_time_ms) as avg_time, COUNT(*) as count
    FROM request_logs 
    WHERE timestamp > datetime('now', '-1 hour')
    GROUP BY path 
    HAVING avg_time > 100
    ORDER BY avg_time DESC
""")

slow_endpoints = cursor.fetchall()
for endpoint, avg_time, count in slow_endpoints:
    print(f"{endpoint}: {avg_time:.2f}ms average ({count} requests)")
```

## Log Analysis

### Performance Analysis

Analyze performance patterns:

```python
# Get performance insights
analysis = query_mock_logs(
    server_url="http://localhost:8000",
    analyze=True,
    time_range="24h"
)

print("Performance Summary:")
print(f"  Total requests: {analysis['total_requests']}")
print(f"  Average response time: {analysis['avg_response_time']}ms")
print(f"  95th percentile: {analysis['p95_response_time']}ms")
print(f"  Error rate: {analysis['error_rate']}%")

print("\nTop Endpoints:")
for endpoint in analysis['top_endpoints']:
    print(f"  {endpoint['path']}: {endpoint['count']} requests")

print("\nSlowest Endpoints:")
for endpoint in analysis['slowest_endpoints']:
    print(f"  {endpoint['path']}: {endpoint['avg_time']}ms")
```

### Error Analysis

Analyze error patterns:

```python
# Analyze errors
error_analysis = query_mock_logs(
    server_url="http://localhost:8000",
    status_code_range=[400, 599],
    analyze=True
)

print("Error Summary:")
print(f"  Total errors: {error_analysis['total_errors']}")
print(f"  Error rate: {error_analysis['error_rate']}%")

print("\nError Breakdown:")
for status_code, count in error_analysis['status_codes'].items():
    print(f"  {status_code}: {count} occurrences")

print("\nError Patterns:")
for pattern in error_analysis['patterns']:
    print(f"  {pattern['path']}: {pattern['error_count']} errors")
```

### Usage Patterns

Analyze usage patterns:

```python
# Analyze usage patterns
usage = query_mock_logs(
    server_url="http://localhost:8000",
    analyze=True,
    group_by="hour"
)

print("Hourly Usage:")
for hour, stats in usage['hourly_stats'].items():
    print(f"  {hour}:00 - {stats['requests']} requests, {stats['avg_time']}ms avg")

print("\nClient Analysis:")
for client in usage['top_clients']:
    print(f"  {client['ip']}: {client['requests']} requests")
```

## Log Export and Integration

### Export Formats

Export logs in various formats:

```python
# Export to CSV
export_logs(
    server_url="http://localhost:8000",
    format="csv",
    output_file="requests.csv",
    time_range="24h"
)

# Export to JSON
export_logs(
    server_url="http://localhost:8000",
    format="json",
    output_file="requests.json",
    filters={"status_code": {"gte": 400}}
)

# Export to ELK format
export_logs(
    server_url="http://localhost:8000",
    format="elk",
    output_file="requests.jsonl"
)
```

### Integration with Log Aggregators

#### ELK Stack Integration

Configure for Elasticsearch, Logstash, and Kibana:

```yaml
# logstash.conf
input {
  file {
    path => "/var/log/mockloop/requests.log"
    start_position => "beginning"
    codec => "json"
  }
}

filter {
  if [logger] == "mockloop.requests" {
    mutate {
      add_tag => ["mockloop", "api_request"]
    }
    
    date {
      match => ["timestamp", "ISO8601"]
    }
    
    if [response_time_ms] {
      mutate {
        convert => { "response_time_ms" => "integer" }
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "mockloop-requests-%{+YYYY.MM.dd}"
  }
}
```

#### Splunk Integration

Configure for Splunk ingestion:

```conf
# inputs.conf
[monitor:///var/log/mockloop/requests.log]
disabled = false
index = mockloop
sourcetype = mockloop_requests

# props.conf
[mockloop_requests]
SHOULD_LINEMERGE = false
KV_MODE = json
TIME_PREFIX = "timestamp":"
TIME_FORMAT = %Y-%m-%dT%H:%M:%S.%3N%Z
```

#### Fluentd Integration

Configure for Fluentd log collection:

```ruby
# fluent.conf
<source>
  @type tail
  path /var/log/mockloop/requests.log
  pos_file /var/log/fluentd/mockloop.log.pos
  tag mockloop.requests
  format json
  time_key timestamp
  time_format %Y-%m-%dT%H:%M:%S.%L%z
</source>

<match mockloop.**>
  @type elasticsearch
  host localhost
  port 9200
  index_name mockloop
  type_name requests
</match>
```

## Real-time Log Monitoring

### WebSocket Streaming

Stream logs in real-time:

```javascript
// Connect to log stream
const ws = new WebSocket('ws://localhost:8000/admin/logs/stream');

ws.onmessage = function(event) {
    const logEntry = JSON.parse(event.data);
    console.log('New log entry:', logEntry);
    
    // Update dashboard
    updateLogDashboard(logEntry);
};

// Filter stream
ws.send(JSON.stringify({
    filter: {
        level: ['ERROR', 'WARNING'],
        logger: 'mockloop.requests'
    }
}));
```

### Server-Sent Events

Use SSE for log streaming:

```javascript
// Connect to SSE endpoint
const eventSource = new EventSource('http://localhost:8000/admin/logs/events');

eventSource.onmessage = function(event) {
    const logEntry = JSON.parse(event.data);
    displayLogEntry(logEntry);
};

eventSource.addEventListener('error', function(event) {
    console.error('Log stream error:', event);
});
```

## Log Retention and Cleanup

### Automatic Cleanup

Configure automatic log cleanup:

```python
# Configure log retention
manage_mock_data(
    server_url="http://localhost:8000",
    operation="configure_retention",
    config={
        "request_logs_days": 30,
        "application_logs_days": 7,
        "performance_logs_days": 90,
        "cleanup_interval_hours": 24
    }
)
```

### Manual Cleanup

Manually clean up old logs:

```python
# Clean up logs older than 30 days
cleanup_logs(
    server_url="http://localhost:8000",
    older_than_days=30,
    log_types=["requests", "application"]
)

# Archive logs before cleanup
archive_logs(
    server_url="http://localhost:8000",
    older_than_days=30,
    archive_path="/backup/logs/"
)
```

## Security and Privacy

### Sensitive Data Filtering

Filter sensitive information from logs:

```python
# Configure sensitive data filtering
manage_mock_data(
    server_url="http://localhost:8000",
    operation="configure_privacy",
    config={
        "filter_headers": ["Authorization", "Cookie", "X-API-Key"],
        "filter_body_fields": ["password", "ssn", "credit_card"],
        "mask_ip_addresses": True,
        "hash_user_agents": True
    }
)
```

### Log Encryption

Enable log encryption for sensitive environments:

```python
# Enable log encryption
manage_mock_data(
    server_url="http://localhost:8000",
    operation="configure_encryption",
    config={
        "encrypt_logs": True,
        "encryption_key_file": "/etc/mockloop/encryption.key",
        "encryption_algorithm": "AES-256-GCM"
    }
)
```

## Troubleshooting

### Common Logging Issues

1. **Logs not appearing**: Check log level configuration
2. **High disk usage**: Configure log rotation and retention
3. **Performance impact**: Reduce log verbosity in production
4. **Missing request logs**: Verify request logging is enabled

### Debug Logging

Enable debug logging for troubleshooting:

```python
# Enable debug logging
manage_mock_data(
    server_url="http://localhost:8000",
    operation="set_log_level",
    level="DEBUG"
)

# Check logging configuration
config = manage_mock_data(
    server_url="http://localhost:8000",
    operation="get_logging_config"
)
print("Current logging config:", config)
```

### Log Validation

Validate log integrity:

```python
# Validate log files
validation = validate_logs(
    server_url="http://localhost:8000",
    check_integrity=True,
    check_format=True
)

if validation['errors']:
    print("Log validation errors:", validation['errors'])
else:
    print("All logs are valid")
```

## Best Practices

### Production Logging

1. **Use structured logging** (JSON format) for easier parsing
2. **Set appropriate log levels** (INFO or WARNING in production)
3. **Configure log rotation** to prevent disk space issues
4. **Filter sensitive data** to protect privacy
5. **Monitor log volume** and performance impact

### Development Logging

1. **Use DEBUG level** for detailed troubleshooting
2. **Enable request/response body logging** for debugging
3. **Use real-time log streaming** for immediate feedback
4. **Correlate logs with test scenarios**

### Log Analysis

1. **Regular performance reviews** using log analysis
2. **Set up alerts** for error rate thresholds
3. **Monitor trends** over time
4. **Use log aggregation tools** for complex analysis

## Next Steps

- [Performance Monitoring](performance-monitoring.md) - Monitor performance using logs
- [Scenario Management](scenario-management.md) - Correlate logs with test scenarios
- [Docker Integration](docker-integration.md) - Configure logging in containers