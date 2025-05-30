# Mock Server Management

MockLoop provides comprehensive tools for managing mock servers throughout their lifecycle, from creation and configuration to monitoring and maintenance.

## Overview

Mock server management in MockLoop includes:

- **Server Lifecycle Management**: Create, start, stop, and destroy servers
- **Configuration Management**: Update server settings and behavior
- **Health Monitoring**: Monitor server status and performance
- **Resource Management**: Manage server resources and scaling
- **Multi-Server Coordination**: Manage multiple mock servers

## Server Discovery

### Finding Running Servers

Discover active MockLoop servers in your environment:

```python
from mockloop_mcp import discover_mock_servers

# Discover all running servers
servers = discover_mock_servers(
    check_health=True,
    include_generated=True
)

print("Running servers:")
for server in servers['running_servers']:
    print(f"  {server['url']} - {server['status']} - {server['spec_name']}")

print("\nGenerated servers:")
for server in servers['generated_servers']:
    print(f"  {server['path']} - {server['spec_file']}")
```

### Server Status Monitoring

Check the health and status of specific servers:

```python
# Check server health
health = check_server_health("http://localhost:8000")
print(f"Server status: {health['status']}")
print(f"Uptime: {health['uptime']}")
print(f"Request count: {health['request_count']}")
print(f"Memory usage: {health['memory_usage']}")

# Get detailed server info
info = get_server_info("http://localhost:8000")
print(f"Server version: {info['version']}")
print(f"OpenAPI spec: {info['spec_info']['title']} v{info['spec_info']['version']}")
print(f"Endpoints: {len(info['endpoints'])}")
```

## Server Configuration

### Runtime Configuration

Update server configuration without restarting:

```python
from mockloop_mcp import manage_mock_data

# Update server configuration
manage_mock_data(
    server_url="http://localhost:8000",
    operation="update_config",
    config={
        "cors_enabled": True,
        "cors_origins": ["http://localhost:3000", "https://myapp.com"],
        "rate_limiting": {
            "enabled": True,
            "requests_per_minute": 100
        },
        "authentication": {
            "enabled": True,
            "type": "bearer",
            "validate_tokens": False
        }
    }
)
```

### Environment-Specific Settings

Configure servers for different environments:

```python
# Development configuration
dev_config = {
    "debug": True,
    "log_level": "DEBUG",
    "cors_enabled": True,
    "cors_origins": ["*"],
    "response_delays": False,
    "detailed_logging": True
}

# Production configuration
prod_config = {
    "debug": False,
    "log_level": "INFO",
    "cors_enabled": True,
    "cors_origins": ["https://myapp.com"],
    "response_delays": True,
    "detailed_logging": False,
    "rate_limiting": {
        "enabled": True,
        "requests_per_minute": 1000
    }
}

# Apply configuration based on environment
import os
config = dev_config if os.getenv("ENV") == "development" else prod_config

manage_mock_data(
    server_url="http://localhost:8000",
    operation="update_config",
    config=config
)
```

### Feature Toggles

Enable or disable server features dynamically:

```python
# Toggle features
manage_mock_data(
    server_url="http://localhost:8000",
    operation="toggle_features",
    features={
        "admin_ui": True,
        "webhooks": True,
        "storage": True,
        "auth": False,
        "metrics": True,
        "request_logging": True
    }
)
```

## Multi-Server Management

### Server Groups

Manage multiple servers as a group:

```python
# Define server group
server_group = [
    "http://localhost:8000",  # User service
    "http://localhost:8001",  # Order service
    "http://localhost:8002",  # Payment service
]

# Apply configuration to all servers
for server_url in server_group:
    manage_mock_data(
        server_url=server_url,
        operation="update_config",
        config={
            "cors_enabled": True,
            "log_level": "INFO"
        }
    )

# Switch all servers to the same scenario
for server_url in server_group:
    manage_mock_data(
        server_url=server_url,
        operation="switch_scenario",
        scenario_name="integration_testing"
    )
```

### Service Mesh Integration

Integrate with service mesh environments:

```python
# Configure for service mesh
mesh_config = {
    "service_mesh": {
        "enabled": True,
        "mesh_type": "istio",
        "sidecar_injection": True,
        "mtls_enabled": True
    },
    "networking": {
        "service_name": "user-service-mock",
        "namespace": "testing",
        "port": 8080
    }
}

manage_mock_data(
    server_url="http://localhost:8000",
    operation="configure_service_mesh",
    config=mesh_config
)
```

### Load Balancing

Configure load balancing across multiple server instances:

```python
# Set up load balancing
lb_config = {
    "load_balancer": {
        "enabled": True,
        "algorithm": "round_robin",  # round_robin, least_connections, weighted
        "health_check": {
            "enabled": True,
            "interval": 30,
            "timeout": 5,
            "path": "/health"
        }
    },
    "instances": [
        {"url": "http://localhost:8000", "weight": 1},
        {"url": "http://localhost:8001", "weight": 1},
        {"url": "http://localhost:8002", "weight": 2}
    ]
}

configure_load_balancer(lb_config)
```

## Resource Management

### Memory Management

Monitor and manage server memory usage:

```python
# Check memory usage
memory_stats = get_server_stats("http://localhost:8000")
print(f"Memory usage: {memory_stats['memory']['used_mb']}MB")
print(f"Memory limit: {memory_stats['memory']['limit_mb']}MB")

# Configure memory limits
manage_mock_data(
    server_url="http://localhost:8000",
    operation="set_resource_limits",
    limits={
        "memory_mb": 512,
        "cpu_percent": 50,
        "disk_mb": 1024
    }
)

# Enable memory optimization
manage_mock_data(
    server_url="http://localhost:8000",
    operation="optimize_memory",
    config={
        "cache_responses": True,
        "compress_logs": True,
        "cleanup_interval": 3600  # seconds
    }
)
```

### Performance Tuning

Optimize server performance:

```python
# Performance tuning configuration
perf_config = {
    "performance": {
        "worker_processes": 4,
        "max_connections": 1000,
        "keep_alive_timeout": 30,
        "request_timeout": 60
    },
    "caching": {
        "enabled": True,
        "ttl_seconds": 300,
        "max_entries": 10000
    },
    "compression": {
        "enabled": True,
        "algorithms": ["gzip", "deflate"],
        "min_size": 1024
    }
}

manage_mock_data(
    server_url="http://localhost:8000",
    operation="configure_performance",
    config=perf_config
)
```

### Auto-Scaling

Configure automatic scaling based on load:

```python
# Auto-scaling configuration
scaling_config = {
    "auto_scaling": {
        "enabled": True,
        "min_instances": 1,
        "max_instances": 5,
        "target_cpu_percent": 70,
        "target_memory_percent": 80,
        "scale_up_threshold": 2,    # minutes
        "scale_down_threshold": 5   # minutes
    },
    "metrics": {
        "collection_interval": 30,
        "evaluation_interval": 60
    }
}

configure_auto_scaling("http://localhost:8000", scaling_config)
```

## Server Lifecycle

### Programmatic Server Creation

Create servers programmatically:

```python
from mockloop_mcp import generate_mock_api
import subprocess
import time

# Generate new mock server
server_path = generate_mock_api(
    spec_url_or_path="https://api.example.com/openapi.json",
    output_dir_name="example_api_mock"
)

# Start the server
process = subprocess.Popen(
    ["python", "main.py"],
    cwd=server_path,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server to start
time.sleep(5)

# Verify server is running
health = check_server_health("http://localhost:8000")
if health['status'] == 'healthy':
    print("Server started successfully")
else:
    print("Server failed to start")
```

### Server Updates

Update running servers with new specifications:

```python
# Update server with new OpenAPI spec
manage_mock_data(
    server_url="http://localhost:8000",
    operation="update_spec",
    spec_url="https://api.example.com/openapi-v2.json",
    reload_server=True
)

# Hot reload configuration
manage_mock_data(
    server_url="http://localhost:8000",
    operation="reload_config",
    preserve_state=True
)
```

### Graceful Shutdown

Implement graceful server shutdown:

```python
# Initiate graceful shutdown
manage_mock_data(
    server_url="http://localhost:8000",
    operation="shutdown",
    config={
        "graceful": True,
        "timeout_seconds": 30,
        "finish_requests": True,
        "save_state": True
    }
)

# Check shutdown status
shutdown_status = get_shutdown_status("http://localhost:8000")
print(f"Shutdown status: {shutdown_status['status']}")
print(f"Remaining requests: {shutdown_status['pending_requests']}")
```

## Monitoring and Alerting

### Health Checks

Implement comprehensive health checks:

```python
# Configure health checks
health_config = {
    "health_checks": {
        "enabled": True,
        "checks": [
            {
                "name": "database",
                "type": "database_connection",
                "timeout": 5
            },
            {
                "name": "memory",
                "type": "memory_usage",
                "threshold": 90
            },
            {
                "name": "disk",
                "type": "disk_space",
                "threshold": 85
            },
            {
                "name": "response_time",
                "type": "avg_response_time",
                "threshold": 1000
            }
        ]
    }
}

manage_mock_data(
    server_url="http://localhost:8000",
    operation="configure_health_checks",
    config=health_config
)
```

### Alerting

Set up alerts for server issues:

```python
# Configure alerting
alert_config = {
    "alerting": {
        "enabled": True,
        "channels": [
            {
                "type": "webhook",
                "url": "https://hooks.slack.com/services/...",
                "events": ["server_down", "high_error_rate", "memory_high"]
            },
            {
                "type": "email",
                "recipients": ["admin@example.com"],
                "events": ["server_down", "critical_error"]
            }
        ],
        "thresholds": {
            "error_rate_percent": 5,
            "response_time_ms": 2000,
            "memory_usage_percent": 90
        }
    }
}

manage_mock_data(
    server_url="http://localhost:8000",
    operation="configure_alerts",
    config=alert_config
)
```

### Metrics Collection

Collect and export metrics:

```python
# Configure metrics collection
metrics_config = {
    "metrics": {
        "enabled": True,
        "collection_interval": 30,
        "exporters": [
            {
                "type": "prometheus",
                "port": 9090,
                "path": "/metrics"
            },
            {
                "type": "statsd",
                "host": "localhost",
                "port": 8125
            }
        ],
        "custom_metrics": [
            "request_count_by_endpoint",
            "response_time_histogram",
            "error_rate_by_status_code"
        ]
    }
}

manage_mock_data(
    server_url="http://localhost:8000",
    operation="configure_metrics",
    config=metrics_config
)
```

## Backup and Recovery

### State Backup

Backup server state and configuration:

```python
# Create backup
backup_config = {
    "backup": {
        "include_logs": True,
        "include_scenarios": True,
        "include_config": True,
        "include_data": True,
        "compression": True
    }
}

backup_result = manage_mock_data(
    server_url="http://localhost:8000",
    operation="create_backup",
    config=backup_config
)

print(f"Backup created: {backup_result['backup_file']}")
print(f"Backup size: {backup_result['size_mb']}MB")
```

### State Restoration

Restore server from backup:

```python
# Restore from backup
restore_config = {
    "restore": {
        "backup_file": "/backups/server_backup_20240101.tar.gz",
        "restore_logs": False,
        "restore_scenarios": True,
        "restore_config": True,
        "restore_data": True
    }
}

restore_result = manage_mock_data(
    server_url="http://localhost:8000",
    operation="restore_backup",
    config=restore_config
)

print(f"Restore status: {restore_result['status']}")
```

### Disaster Recovery

Implement disaster recovery procedures:

```python
# Disaster recovery configuration
dr_config = {
    "disaster_recovery": {
        "enabled": True,
        "backup_interval": 3600,  # hourly
        "backup_retention_days": 30,
        "failover": {
            "enabled": True,
            "backup_servers": [
                "http://backup1.example.com:8000",
                "http://backup2.example.com:8000"
            ],
            "health_check_interval": 60,
            "failover_timeout": 30
        }
    }
}

configure_disaster_recovery("http://localhost:8000", dr_config)
```

## Security Management

### Access Control

Configure access control and authentication:

```python
# Configure access control
security_config = {
    "security": {
        "authentication": {
            "enabled": True,
            "type": "jwt",
            "secret_key": "your-secret-key",
            "token_expiry": 3600
        },
        "authorization": {
            "enabled": True,
            "roles": {
                "admin": ["read", "write", "delete", "configure"],
                "user": ["read"],
                "tester": ["read", "write"]
            }
        },
        "ip_whitelist": [
            "192.168.1.0/24",
            "10.0.0.0/8"
        ]
    }
}

manage_mock_data(
    server_url="http://localhost:8000",
    operation="configure_security",
    config=security_config
)
```

### SSL/TLS Configuration

Configure SSL/TLS for secure communication:

```python
# Configure SSL/TLS
ssl_config = {
    "ssl": {
        "enabled": True,
        "cert_file": "/etc/ssl/certs/server.crt",
        "key_file": "/etc/ssl/private/server.key",
        "ca_file": "/etc/ssl/certs/ca.crt",
        "verify_client": False,
        "protocols": ["TLSv1.2", "TLSv1.3"]
    }
}

manage_mock_data(
    server_url="http://localhost:8000",
    operation="configure_ssl",
    config=ssl_config
)
```

## Best Practices

### Server Management

1. **Use health checks** to monitor server status
2. **Implement graceful shutdown** procedures
3. **Configure appropriate resource limits**
4. **Set up monitoring and alerting**
5. **Regular backup of server state**

### Multi-Server Environments

1. **Use consistent naming conventions**
2. **Centralize configuration management**
3. **Implement service discovery**
4. **Use load balancing for high availability**
5. **Coordinate scenario switches across services**

### Production Deployment

1. **Use container orchestration** (Kubernetes, Docker Swarm)
2. **Implement auto-scaling** based on load
3. **Configure proper logging and monitoring**
4. **Set up disaster recovery procedures**
5. **Regular security audits and updates**

## Troubleshooting

### Common Issues

1. **Server won't start**: Check port availability and configuration
2. **High memory usage**: Review log retention and caching settings
3. **Slow responses**: Check resource limits and performance configuration
4. **Connection issues**: Verify network configuration and firewall rules

### Debugging Tools

```python
# Enable debug mode
manage_mock_data(
    server_url="http://localhost:8000",
    operation="enable_debug",
    config={
        "debug_level": "verbose",
        "trace_requests": True,
        "profile_performance": True
    }
)

# Get diagnostic information
diagnostics = get_server_diagnostics("http://localhost:8000")
print("Server diagnostics:", diagnostics)
```

## Next Steps

- [Performance Monitoring](performance-monitoring.md) - Monitor server performance
- [Scenario Management](scenario-management.md) - Manage test scenarios
- [Docker Integration](docker-integration.md) - Deploy servers in containers
- [Logging](logging.md) - Configure comprehensive logging