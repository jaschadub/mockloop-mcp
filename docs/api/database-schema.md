# Database Schema

This document provides comprehensive documentation for the MockLoop MCP database schema. The database stores request logs, mock configurations, scenarios, and system metadata.

## Overview

MockLoop MCP uses a relational database to store:

- **Request Logs**: HTTP request/response data and metadata
- **Mock Configurations**: Generated mock server configurations
- **Scenarios**: Named sets of mock responses
- **System Metadata**: Schema versions, migrations, and system state
- **User Data**: Authentication and authorization information

## Supported Databases

- **SQLite** (default): Lightweight, file-based database
- **PostgreSQL**: Production-ready relational database
- **MySQL**: Alternative relational database option

## Core Tables

### request_logs

Stores HTTP request and response data for analysis and debugging.

```sql
CREATE TABLE request_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    method VARCHAR(10) NOT NULL,
    path TEXT NOT NULL,
    query_params TEXT,
    headers TEXT,
    request_body TEXT,
    response_status INTEGER NOT NULL,
    response_headers TEXT,
    response_body TEXT,
    response_time_ms INTEGER,
    server_id VARCHAR(255),
    client_ip VARCHAR(45),
    user_agent TEXT,
    request_id VARCHAR(255),
    scenario_name VARCHAR(255),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_request_logs_timestamp ON request_logs(timestamp);
CREATE INDEX idx_request_logs_method ON request_logs(method);
CREATE INDEX idx_request_logs_path ON request_logs(path);
CREATE INDEX idx_request_logs_server_id ON request_logs(server_id);
CREATE INDEX idx_request_logs_scenario_name ON request_logs(scenario_name);
CREATE INDEX idx_request_logs_response_status ON request_logs(response_status);
```

#### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key, auto-incrementing |
| `timestamp` | DATETIME | Request timestamp (UTC) |
| `method` | VARCHAR(10) | HTTP method (GET, POST, etc.) |
| `path` | TEXT | Request path (without query parameters) |
| `query_params` | TEXT | JSON-encoded query parameters |
| `headers` | TEXT | JSON-encoded request headers |
| `request_body` | TEXT | Request body content |
| `response_status` | INTEGER | HTTP response status code |
| `response_headers` | TEXT | JSON-encoded response headers |
| `response_body` | TEXT | Response body content |
| `response_time_ms` | INTEGER | Response time in milliseconds |
| `server_id` | VARCHAR(255) | Mock server identifier |
| `client_ip` | VARCHAR(45) | Client IP address |
| `user_agent` | TEXT | Client user agent string |
| `request_id` | VARCHAR(255) | Unique request identifier |
| `scenario_name` | VARCHAR(255) | Active scenario name |
| `created_at` | DATETIME | Record creation timestamp |
| `updated_at` | DATETIME | Record last update timestamp |

### mock_servers

Stores information about generated mock servers.

```sql
CREATE TABLE mock_servers (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    spec_path TEXT NOT NULL,
    spec_content TEXT,
    output_directory TEXT NOT NULL,
    port INTEGER,
    status VARCHAR(50) NOT NULL DEFAULT 'stopped',
    pid INTEGER,
    config TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    stopped_at DATETIME
);

-- Indexes
CREATE INDEX idx_mock_servers_name ON mock_servers(name);
CREATE INDEX idx_mock_servers_status ON mock_servers(status);
CREATE INDEX idx_mock_servers_port ON mock_servers(port);
```

#### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | VARCHAR(255) | Unique server identifier |
| `name` | VARCHAR(255) | Human-readable server name |
| `spec_path` | TEXT | Path to API specification file |
| `spec_content` | TEXT | API specification content |
| `output_directory` | TEXT | Generated files directory |
| `port` | INTEGER | Server port number |
| `status` | VARCHAR(50) | Server status (stopped, starting, running, error) |
| `pid` | INTEGER | Process ID when running |
| `config` | TEXT | JSON-encoded server configuration |
| `created_at` | DATETIME | Server creation timestamp |
| `updated_at` | DATETIME | Last update timestamp |
| `started_at` | DATETIME | Last start timestamp |
| `stopped_at` | DATETIME | Last stop timestamp |

### scenarios

Stores named scenarios with mock response configurations.

```sql
CREATE TABLE scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    server_id VARCHAR(255) NOT NULL,
    description TEXT,
    config TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    
    FOREIGN KEY (server_id) REFERENCES mock_servers(id) ON DELETE CASCADE,
    UNIQUE(name, server_id)
);

-- Indexes
CREATE INDEX idx_scenarios_name ON scenarios(name);
CREATE INDEX idx_scenarios_server_id ON scenarios(server_id);
CREATE INDEX idx_scenarios_is_active ON scenarios(is_active);
```

#### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key, auto-incrementing |
| `name` | VARCHAR(255) | Scenario name (unique per server) |
| `server_id` | VARCHAR(255) | Associated mock server ID |
| `description` | TEXT | Scenario description |
| `config` | TEXT | JSON-encoded scenario configuration |
| `is_active` | BOOLEAN | Whether scenario is currently active |
| `created_at` | DATETIME | Scenario creation timestamp |
| `updated_at` | DATETIME | Last update timestamp |
| `created_by` | VARCHAR(255) | User who created the scenario |

### mock_responses

Stores individual mock response configurations.

```sql
CREATE TABLE mock_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id VARCHAR(255) NOT NULL,
    endpoint_path TEXT NOT NULL,
    method VARCHAR(10) NOT NULL,
    response_status INTEGER NOT NULL DEFAULT 200,
    response_headers TEXT,
    response_body TEXT,
    delay_ms INTEGER DEFAULT 0,
    scenario_id INTEGER,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (server_id) REFERENCES mock_servers(id) ON DELETE CASCADE,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_mock_responses_server_id ON mock_responses(server_id);
CREATE INDEX idx_mock_responses_endpoint ON mock_responses(endpoint_path);
CREATE INDEX idx_mock_responses_method ON mock_responses(method);
CREATE INDEX idx_mock_responses_scenario_id ON mock_responses(scenario_id);
```

#### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key, auto-incrementing |
| `server_id` | VARCHAR(255) | Associated mock server ID |
| `endpoint_path` | TEXT | API endpoint path |
| `method` | VARCHAR(10) | HTTP method |
| `response_status` | INTEGER | HTTP response status code |
| `response_headers` | TEXT | JSON-encoded response headers |
| `response_body` | TEXT | Response body content |
| `delay_ms` | INTEGER | Response delay in milliseconds |
| `scenario_id` | INTEGER | Associated scenario ID (optional) |
| `is_default` | BOOLEAN | Whether this is the default response |
| `created_at` | DATETIME | Response creation timestamp |
| `updated_at` | DATETIME | Last update timestamp |

### webhooks

Stores webhook configuration and delivery logs.

```sql
CREATE TABLE webhooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    method VARCHAR(10) NOT NULL DEFAULT 'POST',
    headers TEXT,
    events TEXT NOT NULL,
    secret_key VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (server_id) REFERENCES mock_servers(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_webhooks_server_id ON webhooks(server_id);
CREATE INDEX idx_webhooks_is_active ON webhooks(is_active);
```

### webhook_deliveries

Stores webhook delivery attempts and results.

```sql
CREATE TABLE webhook_deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    webhook_id INTEGER NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    payload TEXT NOT NULL,
    response_status INTEGER,
    response_body TEXT,
    delivery_time_ms INTEGER,
    attempt_number INTEGER NOT NULL DEFAULT 1,
    success BOOLEAN NOT NULL DEFAULT FALSE,
    error_message TEXT,
    delivered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (webhook_id) REFERENCES webhooks(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_webhook_deliveries_webhook_id ON webhook_deliveries(webhook_id);
CREATE INDEX idx_webhook_deliveries_event_type ON webhook_deliveries(event_type);
CREATE INDEX idx_webhook_deliveries_success ON webhook_deliveries(success);
CREATE INDEX idx_webhook_deliveries_delivered_at ON webhook_deliveries(delivered_at);
```

## System Tables

### schema_version

Tracks database schema version for migrations.

```sql
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    description TEXT,
    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial version
INSERT INTO schema_version (version, description) VALUES (1, 'Initial schema');
```

### system_config

Stores system-wide configuration settings.

```sql
CREATE TABLE system_config (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Default configuration
INSERT INTO system_config (key, value, description) VALUES
('log_retention_days', '30', 'Number of days to retain request logs'),
('max_log_entries', '100000', 'Maximum number of log entries to keep'),
('default_response_delay', '0', 'Default response delay in milliseconds'),
('webhook_timeout', '30', 'Webhook timeout in seconds');
```

## Authentication Tables

### users

Stores user authentication information (when auth is enabled).

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    api_key VARCHAR(255) UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

-- Indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_api_key ON users(api_key);
CREATE INDEX idx_users_is_active ON users(is_active);
```

### user_sessions

Stores user session information.

```sql
CREATE TABLE user_sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_accessed DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
```

## Views

### request_logs_summary

Provides aggregated request log statistics.

```sql
CREATE VIEW request_logs_summary AS
SELECT 
    server_id,
    DATE(timestamp) as date,
    method,
    COUNT(*) as request_count,
    AVG(response_time_ms) as avg_response_time,
    MIN(response_time_ms) as min_response_time,
    MAX(response_time_ms) as max_response_time,
    COUNT(CASE WHEN response_status >= 400 THEN 1 END) as error_count,
    COUNT(CASE WHEN response_status < 400 THEN 1 END) as success_count
FROM request_logs
GROUP BY server_id, DATE(timestamp), method;
```

### active_scenarios

Shows currently active scenarios for each server.

```sql
CREATE VIEW active_scenarios AS
SELECT 
    s.server_id,
    s.name as scenario_name,
    s.description,
    s.created_at,
    ms.name as server_name
FROM scenarios s
JOIN mock_servers ms ON s.server_id = ms.id
WHERE s.is_active = TRUE;
```

### server_statistics

Provides statistics for each mock server.

```sql
CREATE VIEW server_statistics AS
SELECT 
    ms.id as server_id,
    ms.name as server_name,
    ms.status,
    COUNT(rl.id) as total_requests,
    COUNT(CASE WHEN rl.response_status >= 400 THEN 1 END) as error_requests,
    AVG(rl.response_time_ms) as avg_response_time,
    COUNT(DISTINCT rl.client_ip) as unique_clients,
    MAX(rl.timestamp) as last_request_time
FROM mock_servers ms
LEFT JOIN request_logs rl ON ms.id = rl.server_id
GROUP BY ms.id, ms.name, ms.status;
```

## Database Migrations

### Migration System

MockLoop MCP uses a migration system to manage schema changes:

```python
# Example migration file: migrations/002_add_webhook_tables.py
from mockloop_mcp.database import Migration

class AddWebhookTables(Migration):
    version = 2
    description = "Add webhook tables"
    
    def up(self, connection):
        connection.execute("""
            CREATE TABLE webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                url TEXT NOT NULL,
                method VARCHAR(10) NOT NULL DEFAULT 'POST',
                headers TEXT,
                events TEXT NOT NULL,
                secret_key VARCHAR(255),
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (server_id) REFERENCES mock_servers(id) ON DELETE CASCADE
            )
        """)
        
        connection.execute("""
            CREATE INDEX idx_webhooks_server_id ON webhooks(server_id)
        """)
    
    def down(self, connection):
        connection.execute("DROP TABLE IF EXISTS webhooks")
```

### Running Migrations

```bash
# Run all pending migrations
mockloop db migrate

# Check migration status
mockloop db status

# Rollback to specific version
mockloop db rollback --version 1
```

## Database Configuration Examples

### SQLite Configuration

```yaml
database:
  type: "sqlite"
  path: "./db/mockloop.db"
  pool_size: 5
  pool_timeout: 30
  echo: false
  
  # SQLite-specific options
  sqlite:
    journal_mode: "WAL"
    synchronous: "NORMAL"
    cache_size: 10000
    temp_store: "MEMORY"
```

### PostgreSQL Configuration

```yaml
database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  database: "mockloop"
  username: "mockloop_user"
  password: "secure_password"
  pool_size: 20
  pool_timeout: 30
  ssl_mode: "prefer"
  
  # PostgreSQL-specific options
  postgresql:
    application_name: "mockloop"
    connect_timeout: 10
    command_timeout: 30
    server_settings:
      timezone: "UTC"
      statement_timeout: "30s"
```

### MySQL Configuration

```yaml
database:
  type: "mysql"
  host: "localhost"
  port: 3306
  database: "mockloop"
  username: "mockloop_user"
  password: "secure_password"
  charset: "utf8mb4"
  pool_size: 15
  pool_timeout: 30
  
  # MySQL-specific options
  mysql:
    autocommit: true
    sql_mode: "STRICT_TRANS_TABLES"
    time_zone: "+00:00"
```

## Performance Optimization

### Indexing Strategy

```sql
-- Request logs performance indexes
CREATE INDEX idx_request_logs_composite ON request_logs(server_id, timestamp, method);
CREATE INDEX idx_request_logs_path_method ON request_logs(path, method);
CREATE INDEX idx_request_logs_status_time ON request_logs(response_status, timestamp);

-- Scenarios performance indexes
CREATE INDEX idx_scenarios_server_active ON scenarios(server_id, is_active);

-- Mock responses performance indexes
CREATE INDEX idx_mock_responses_lookup ON mock_responses(server_id, endpoint_path, method);
```

### Partitioning (PostgreSQL)

```sql
-- Partition request_logs by month
CREATE TABLE request_logs_partitioned (
    LIKE request_logs INCLUDING ALL
) PARTITION BY RANGE (timestamp);

-- Create monthly partitions
CREATE TABLE request_logs_2024_01 PARTITION OF request_logs_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE request_logs_2024_02 PARTITION OF request_logs_partitioned
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

### Query Optimization

```sql
-- Efficient log queries with proper indexes
EXPLAIN ANALYZE
SELECT method, COUNT(*) as count
FROM request_logs 
WHERE server_id = 'server123' 
  AND timestamp >= '2024-01-01'
  AND timestamp < '2024-02-01'
GROUP BY method;

-- Use covering indexes for common queries
CREATE INDEX idx_request_logs_covering 
ON request_logs(server_id, timestamp) 
INCLUDE (method, response_status, response_time_ms);
```

## Data Retention

### Automatic Cleanup

```sql
-- Stored procedure for log cleanup (PostgreSQL)
CREATE OR REPLACE FUNCTION cleanup_old_logs()
RETURNS void AS $$
BEGIN
    DELETE FROM request_logs 
    WHERE timestamp < NOW() - INTERVAL '30 days';
    
    DELETE FROM webhook_deliveries 
    WHERE delivered_at < NOW() - INTERVAL '7 days';
    
    -- Update statistics
    ANALYZE request_logs;
    ANALYZE webhook_deliveries;
END;
$$ LANGUAGE plpgsql;

-- Schedule cleanup (requires pg_cron extension)
SELECT cron.schedule('cleanup-logs', '0 2 * * *', 'SELECT cleanup_old_logs();');
```

### Manual Cleanup

```bash
# Clean up old logs via CLI
mockloop db cleanup --days 30

# Clean up specific server logs
mockloop db cleanup --server-id server123 --days 7

# Vacuum database after cleanup
mockloop db vacuum
```

## Backup and Recovery

### SQLite Backup

```bash
# Create backup
sqlite3 mockloop.db ".backup backup_$(date +%Y%m%d).db"

# Restore from backup
cp backup_20240101.db mockloop.db
```

### PostgreSQL Backup

```bash
# Create backup
pg_dump -h localhost -U mockloop_user mockloop > backup_$(date +%Y%m%d).sql

# Restore from backup
psql -h localhost -U mockloop_user mockloop < backup_20240101.sql
```

## Troubleshooting

### Common Issues

#### Database Connection Errors

```sql
-- Check connection limits (PostgreSQL)
SELECT * FROM pg_stat_activity WHERE datname = 'mockloop';

-- Check table locks
SELECT * FROM pg_locks WHERE relation::regclass::text LIKE '%request_logs%';
```

#### Performance Issues

```sql
-- Analyze query performance
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM request_logs 
WHERE timestamp > NOW() - INTERVAL '1 hour';

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE schemaname = 'public';
```

#### Storage Issues

```bash
# Check database size
mockloop db size

# Check table sizes
mockloop db table-sizes

# Analyze storage usage
mockloop db analyze
```

## See Also

- **[Core Classes](core-classes.md)**: Database interaction classes
- **[Configuration Options](configuration.md)**: Database configuration
- **[Admin API](admin-api.md)**: Database management endpoints
- **[Database Migrations](../advanced/database-migrations.md)**: Migration system guide