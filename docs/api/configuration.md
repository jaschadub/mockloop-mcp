# Configuration Options

This document provides comprehensive reference for all configuration options available in MockLoop MCP. Configuration can be set through environment variables, configuration files, or programmatically through the API.

## Overview

MockLoop MCP supports multiple configuration methods:

- **Environment Variables**: Set configuration through environment variables
- **Configuration Files**: Use YAML or JSON configuration files
- **Programmatic Configuration**: Set options through the API
- **Command Line Arguments**: Override settings via CLI arguments

## Core Configuration

### Server Configuration

#### Basic Server Settings

```yaml
# mockloop.yaml
server:
  host: "0.0.0.0"                    # Server host (default: localhost)
  port: 8000                         # Server port (default: auto-assigned)
  workers: 1                         # Number of worker processes
  reload: false                      # Enable auto-reload in development
  log_level: "info"                  # Logging level (debug, info, warning, error)
  access_log: true                   # Enable access logging
  
# Environment variables
MOCKLOOP_HOST=0.0.0.0
MOCKLOOP_PORT=8000
MOCKLOOP_WORKERS=1
MOCKLOOP_LOG_LEVEL=info
```

#### SSL/TLS Configuration

```yaml
server:
  ssl:
    enabled: false                   # Enable SSL/TLS
    cert_file: "/path/to/cert.pem"   # SSL certificate file
    key_file: "/path/to/key.pem"     # SSL private key file
    ca_file: "/path/to/ca.pem"       # Certificate authority file (optional)
    verify_mode: "none"              # SSL verification mode (none, optional, required)

# Environment variables
MOCKLOOP_SSL_ENABLED=false
MOCKLOOP_SSL_CERT_FILE=/path/to/cert.pem
MOCKLOOP_SSL_KEY_FILE=/path/to/key.pem
```

### Generation Configuration

#### Mock Server Generation Options

```yaml
generation:
  auth_enabled: true                 # Enable authentication middleware
  webhooks_enabled: true             # Enable webhook support
  admin_ui_enabled: true             # Enable admin UI interface
  storage_enabled: true              # Enable persistent storage
  cors_enabled: true                 # Enable CORS support
  rate_limiting_enabled: false       # Enable rate limiting
  
  # Response behavior
  response_delay_ms: 0               # Default response delay in milliseconds
  error_rate_percent: 0.0            # Default error rate percentage
  
  # File generation
  output_directory: "./generated_mocks"  # Base directory for generated files
  template_directory: "./templates"      # Custom template directory
  overwrite_existing: false              # Overwrite existing files
  
# Environment variables
MOCKLOOP_AUTH_ENABLED=true
MOCKLOOP_WEBHOOKS_ENABLED=true
MOCKLOOP_ADMIN_UI_ENABLED=true
MOCKLOOP_STORAGE_ENABLED=true
```

#### Code Generation Settings

```yaml
generation:
  code:
    language: "python"               # Target language (python, typescript, go)
    framework: "fastapi"             # Target framework
    style: "async"                   # Code style (async, sync)
    type_hints: true                 # Include type hints
    docstrings: true                 # Generate docstrings
    validation: true                 # Include request/response validation
    
  templates:
    route_template: "route.j2"       # Custom route template
    model_template: "model.j2"       # Custom model template
    middleware_template: "middleware.j2"  # Custom middleware template
```

### Database Configuration

#### SQLite Configuration (Default)

```yaml
database:
  type: "sqlite"                     # Database type
  path: "./db/mockloop.db"           # Database file path
  pool_size: 5                       # Connection pool size
  pool_timeout: 30                   # Pool timeout in seconds
  echo: false                        # Echo SQL queries (debug)
  
# Environment variables
MOCKLOOP_DB_TYPE=sqlite
MOCKLOOP_DB_PATH=./db/mockloop.db
```

#### PostgreSQL Configuration

```yaml
database:
  type: "postgresql"
  host: "localhost"                  # Database host
  port: 5432                         # Database port
  database: "mockloop"               # Database name
  username: "mockloop_user"          # Database username
  password: "secure_password"        # Database password
  pool_size: 10                      # Connection pool size
  pool_timeout: 30                   # Pool timeout in seconds
  ssl_mode: "prefer"                 # SSL mode (disable, allow, prefer, require)
  
# Environment variables
MOCKLOOP_DB_TYPE=postgresql
MOCKLOOP_DB_HOST=localhost
MOCKLOOP_DB_PORT=5432
MOCKLOOP_DB_NAME=mockloop
MOCKLOOP_DB_USER=mockloop_user
MOCKLOOP_DB_PASSWORD=secure_password
```

#### MySQL Configuration

```yaml
database:
  type: "mysql"
  host: "localhost"
  port: 3306
  database: "mockloop"
  username: "mockloop_user"
  password: "secure_password"
  charset: "utf8mb4"                 # Character set
  pool_size: 10
  pool_timeout: 30
```

### Authentication Configuration

#### API Key Authentication

```yaml
auth:
  enabled: true
  type: "api_key"                    # Authentication type
  api_key_header: "X-API-Key"        # API key header name
  api_keys:                          # Valid API keys
    - "dev-key-12345"
    - "test-key-67890"
  
# Environment variables
MOCKLOOP_AUTH_ENABLED=true
MOCKLOOP_AUTH_TYPE=api_key
MOCKLOOP_API_KEYS=dev-key-12345,test-key-67890
```

#### JWT Authentication

```yaml
auth:
  enabled: true
  type: "jwt"
  jwt:
    secret_key: "your-secret-key"     # JWT secret key
    algorithm: "HS256"                # JWT algorithm
    expiration_hours: 24              # Token expiration time
    issuer: "mockloop"                # Token issuer
    audience: "mockloop-api"          # Token audience
    
# Environment variables
MOCKLOOP_AUTH_TYPE=jwt
MOCKLOOP_JWT_SECRET=your-secret-key
MOCKLOOP_JWT_ALGORITHM=HS256
```

#### OAuth2 Configuration

```yaml
auth:
  enabled: true
  type: "oauth2"
  oauth2:
    provider: "custom"                # OAuth2 provider
    client_id: "your-client-id"       # OAuth2 client ID
    client_secret: "your-secret"      # OAuth2 client secret
    authorization_url: "https://auth.example.com/oauth/authorize"
    token_url: "https://auth.example.com/oauth/token"
    userinfo_url: "https://auth.example.com/oauth/userinfo"
    scopes: ["read", "write"]         # Required scopes
```

### Logging Configuration

#### Basic Logging

```yaml
logging:
  level: "info"                      # Log level (debug, info, warning, error, critical)
  format: "json"                     # Log format (json, text)
  output: "stdout"                   # Output destination (stdout, stderr, file)
  file_path: "./logs/mockloop.log"   # Log file path (if output is file)
  max_file_size: "10MB"              # Maximum log file size
  backup_count: 5                    # Number of backup files to keep
  
# Environment variables
MOCKLOOP_LOG_LEVEL=info
MOCKLOOP_LOG_FORMAT=json
MOCKLOOP_LOG_OUTPUT=stdout
```

#### Request Logging

```yaml
logging:
  requests:
    enabled: true                    # Enable request logging
    include_headers: true            # Include request headers
    include_body: true               # Include request body
    include_response: true           # Include response data
    max_body_size: 1024              # Maximum body size to log (bytes)
    exclude_paths:                   # Paths to exclude from logging
      - "/health"
      - "/metrics"
    exclude_methods:                 # Methods to exclude from logging
      - "OPTIONS"
```

### Storage Configuration

#### File Storage

```yaml
storage:
  type: "file"                       # Storage type
  base_path: "./storage"             # Base storage path
  max_file_size: "100MB"             # Maximum file size
  allowed_extensions:                # Allowed file extensions
    - ".json"
    - ".yaml"
    - ".xml"
    - ".csv"
```

#### S3 Storage

```yaml
storage:
  type: "s3"
  s3:
    bucket: "mockloop-storage"       # S3 bucket name
    region: "us-west-2"              # AWS region
    access_key_id: "your-access-key" # AWS access key ID
    secret_access_key: "your-secret" # AWS secret access key
    endpoint_url: null               # Custom S3 endpoint (for S3-compatible services)
    
# Environment variables
MOCKLOOP_STORAGE_TYPE=s3
MOCKLOOP_S3_BUCKET=mockloop-storage
MOCKLOOP_S3_REGION=us-west-2
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret
```

### Webhook Configuration

#### Basic Webhook Settings

```yaml
webhooks:
  enabled: true                      # Enable webhook support
  base_url: "http://localhost:8000"  # Base URL for webhook endpoints
  timeout: 30                        # Webhook timeout in seconds
  retry_attempts: 3                  # Number of retry attempts
  retry_delay: 5                     # Delay between retries in seconds
  
# Environment variables
MOCKLOOP_WEBHOOKS_ENABLED=true
MOCKLOOP_WEBHOOK_TIMEOUT=30
```

#### Webhook Security

```yaml
webhooks:
  security:
    verify_ssl: true                 # Verify SSL certificates
    signature_header: "X-Signature"  # Signature header name
    secret_key: "webhook-secret"     # Secret key for signature verification
    allowed_ips:                     # Allowed IP addresses
      - "192.168.1.0/24"
      - "10.0.0.0/8"
```

### Performance Configuration

#### Rate Limiting

```yaml
rate_limiting:
  enabled: false                     # Enable rate limiting
  requests_per_minute: 60            # Requests per minute per IP
  burst_size: 10                     # Burst size for rate limiting
  storage: "memory"                  # Storage backend (memory, redis)
  
  # Redis configuration (if storage is redis)
  redis:
    host: "localhost"
    port: 6379
    db: 0
    password: null
```

#### Caching

```yaml
caching:
  enabled: true                      # Enable response caching
  backend: "memory"                  # Cache backend (memory, redis, file)
  ttl: 300                          # Default TTL in seconds
  max_size: 1000                    # Maximum cache entries
  
  # Redis configuration
  redis:
    host: "localhost"
    port: 6379
    db: 1
    password: null
```

#### Connection Pooling

```yaml
performance:
  connection_pool:
    max_connections: 100             # Maximum connections
    max_keepalive_connections: 20    # Maximum keep-alive connections
    keepalive_expiry: 5              # Keep-alive expiry in seconds
    timeout: 30                      # Connection timeout
```

### Monitoring Configuration

#### Health Checks

```yaml
monitoring:
  health_checks:
    enabled: true                    # Enable health check endpoint
    endpoint: "/health"              # Health check endpoint path
    include_database: true           # Include database health check
    include_external: false          # Include external service checks
    timeout: 5                       # Health check timeout
```

#### Metrics

```yaml
monitoring:
  metrics:
    enabled: true                    # Enable metrics collection
    endpoint: "/metrics"             # Metrics endpoint path
    format: "prometheus"             # Metrics format (prometheus, json)
    include_request_metrics: true    # Include request metrics
    include_system_metrics: false    # Include system metrics
```

## Environment-Specific Configuration

### Development Configuration

```yaml
# development.yaml
server:
  host: "localhost"
  port: 8000
  reload: true
  log_level: "debug"

generation:
  auth_enabled: false
  storage_enabled: false
  response_delay_ms: 100

logging:
  level: "debug"
  format: "text"
  requests:
    include_body: true
    include_headers: true
```

### Production Configuration

```yaml
# production.yaml
server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  reload: false
  log_level: "info"

generation:
  auth_enabled: true
  storage_enabled: true
  response_delay_ms: 0

database:
  type: "postgresql"
  host: "${DB_HOST}"
  port: 5432
  database: "${DB_NAME}"
  username: "${DB_USER}"
  password: "${DB_PASSWORD}"
  pool_size: 20

logging:
  level: "info"
  format: "json"
  output: "file"
  file_path: "/var/log/mockloop/app.log"

rate_limiting:
  enabled: true
  requests_per_minute: 1000
```

### Testing Configuration

```yaml
# testing.yaml
server:
  host: "localhost"
  port: 0  # Auto-assign port
  log_level: "warning"

generation:
  auth_enabled: false
  webhooks_enabled: false
  admin_ui_enabled: false
  storage_enabled: false

database:
  type: "sqlite"
  path: ":memory:"  # In-memory database

logging:
  level: "warning"
  requests:
    enabled: false
```

## Configuration Loading

### Configuration File Priority

MockLoop MCP loads configuration files in the following order (later files override earlier ones):

1. Default configuration (built-in)
2. `/etc/mockloop/config.yaml` (system-wide)
3. `~/.mockloop/config.yaml` (user-specific)
4. `./mockloop.yaml` (project-specific)
5. Environment-specific file (e.g., `production.yaml`)
6. Environment variables
7. Command line arguments

### Environment Variable Mapping

Environment variables use the `MOCKLOOP_` prefix and follow this pattern:

```bash
# Nested configuration
server.host -> MOCKLOOP_SERVER_HOST
database.type -> MOCKLOOP_DATABASE_TYPE
auth.jwt.secret_key -> MOCKLOOP_AUTH_JWT_SECRET_KEY

# Array values (comma-separated)
auth.api_keys -> MOCKLOOP_AUTH_API_KEYS=key1,key2,key3

# Boolean values
generation.auth_enabled -> MOCKLOOP_GENERATION_AUTH_ENABLED=true
```

### Programmatic Configuration

```python
from mockloop_mcp import MockLoopClient, Configuration

# Create configuration object
config = Configuration(
    server=ServerConfig(
        host="localhost",
        port=8000,
        log_level="debug"
    ),
    generation=GenerationConfig(
        auth_enabled=False,
        storage_enabled=True
    ),
    database=DatabaseConfig(
        type="sqlite",
        path="./test.db"
    )
)

# Initialize client with configuration
client = MockLoopClient(config=config)
```

### Configuration Validation

MockLoop MCP validates configuration on startup:

```python
from mockloop_mcp import Configuration, ConfigurationError

try:
    config = Configuration.load_from_file("config.yaml")
    config.validate()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    print(f"Invalid field: {e.field}")
    print(f"Invalid value: {e.value}")
```

## Advanced Configuration

### Custom Middleware Configuration

```yaml
middleware:
  custom:
    - name: "request_id"
      module: "mockloop.middleware.request_id"
      config:
        header_name: "X-Request-ID"
        
    - name: "cors_custom"
      module: "my_app.middleware.cors"
      config:
        allowed_origins: ["https://app.example.com"]
        allowed_methods: ["GET", "POST"]
```

### Plugin Configuration

```yaml
plugins:
  enabled:
    - "mockloop.plugins.openapi_validator"
    - "mockloop.plugins.response_transformer"
    - "my_app.plugins.custom_plugin"
    
  config:
    openapi_validator:
      strict_mode: true
      validate_responses: true
      
    response_transformer:
      transformations:
        - path: "/api/users"
          method: "GET"
          transform: "add_metadata"
```

### Template Configuration

```yaml
templates:
  directories:
    - "./custom_templates"
    - "./shared_templates"
    
  globals:
    company_name: "Acme Corp"
    api_version: "v1"
    
  filters:
    - name: "snake_case"
      module: "my_app.filters.case_conversion"
```

## Configuration Examples

### Microservices Setup

```yaml
# microservice.yaml
server:
  host: "0.0.0.0"
  port: "${SERVICE_PORT}"

generation:
  auth_enabled: true
  webhooks_enabled: true
  
auth:
  type: "jwt"
  jwt:
    secret_key: "${JWT_SECRET}"
    
database:
  type: "postgresql"
  host: "${DB_HOST}"
  database: "${SERVICE_NAME}_db"
  
monitoring:
  metrics:
    enabled: true
    endpoint: "/metrics"
  health_checks:
    enabled: true
    endpoint: "/health"
```

### High-Performance Setup

```yaml
# high-performance.yaml
server:
  workers: 8
  
performance:
  connection_pool:
    max_connections: 200
    max_keepalive_connections: 50
    
caching:
  enabled: true
  backend: "redis"
  ttl: 600
  max_size: 10000
  
rate_limiting:
  enabled: true
  requests_per_minute: 10000
  storage: "redis"
```

### Development with Hot Reload

```yaml
# dev-hot-reload.yaml
server:
  reload: true
  log_level: "debug"
  
generation:
  overwrite_existing: true
  
logging:
  level: "debug"
  format: "text"
  requests:
    enabled: true
    include_body: true
    
monitoring:
  health_checks:
    enabled: true
  metrics:
    enabled: true
```

## Configuration Best Practices

### Security

1. **Never commit secrets**: Use environment variables for sensitive data
2. **Use strong authentication**: Enable authentication in production
3. **Validate SSL certificates**: Always verify SSL in production
4. **Limit access**: Use IP whitelisting and rate limiting

### Performance

1. **Tune connection pools**: Adjust pool sizes based on load
2. **Enable caching**: Use Redis for high-performance caching
3. **Configure workers**: Use multiple workers for CPU-bound tasks
4. **Monitor metrics**: Enable metrics collection for optimization

### Maintainability

1. **Environment-specific configs**: Use separate configs for each environment
2. **Document custom settings**: Comment complex configuration options
3. **Validate configuration**: Use configuration validation in CI/CD
4. **Version control**: Track configuration changes in version control

## Troubleshooting Configuration

### Common Issues

#### Configuration Not Loading

```bash
# Check configuration file syntax
mockloop config validate ./config.yaml

# Check environment variables
mockloop config show-env

# Debug configuration loading
MOCKLOOP_LOG_LEVEL=debug mockloop serve
```

#### Database Connection Issues

```yaml
# Add connection debugging
database:
  echo: true  # Log all SQL queries
  pool_timeout: 60  # Increase timeout
  
logging:
  level: "debug"  # Enable debug logging
```

#### Performance Issues

```yaml
# Monitor and tune performance
monitoring:
  metrics:
    enabled: true
    include_system_metrics: true
    
performance:
  connection_pool:
    max_connections: 50  # Reduce if memory constrained
    timeout: 10  # Reduce timeout
```

## See Also

- **[Core Classes](core-classes.md)**: Core class documentation
- **[Database Schema](database-schema.md)**: Database structure reference
- **[Admin API](admin-api.md)**: Admin API configuration
- **[Performance Optimization](../advanced/performance-optimization.md)**: Performance tuning guide