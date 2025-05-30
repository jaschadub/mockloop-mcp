# Configuration

This guide covers how to configure MockLoop MCP for your specific needs, including MCP client setup, server options, and customization settings.

## MCP Client Configuration

### Cline (VS Code Extension)

Cline is the recommended MCP client for development workflows. Here's how to configure it:

#### 1. Locate Configuration File

The Cline MCP settings file is typically located at:
- **Linux/macOS**: `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- **Windows**: `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

#### 2. Add MockLoop Configuration

```json
{
  "mcpServers": {
    "MockLoopLocal": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "command": "/path/to/your/mockloop-mcp/.venv/bin/python",
      "args": [
        "/path/to/your/mockloop-mcp/src/mockloop_mcp/main.py"
      ],
      "transportType": "stdio"
    }
  }
}
```

#### 3. Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `autoApprove` | Tools to auto-approve without user confirmation | `[]` |
| `disabled` | Whether the server is disabled | `false` |
| `timeout` | Connection timeout in seconds | `60` |
| `command` | Path to Python executable | Required |
| `args` | Arguments to pass to the MCP server | Required |
| `transportType` | Communication protocol | `"stdio"` |

#### 4. Auto-Approval Configuration

For development convenience, you can auto-approve certain tools:

```json
{
  "mcpServers": {
    "MockLoopLocal": {
      "autoApprove": [
        "generate_mock_api",
        "query_mock_logs",
        "discover_mock_servers"
      ],
      "disabled": false,
      "timeout": 60,
      "command": "/path/to/your/mockloop-mcp/.venv/bin/python",
      "args": [
        "/path/to/your/mockloop-mcp/src/mockloop_mcp/main.py"
      ],
      "transportType": "stdio"
    }
  }
}
```

### Claude Desktop

For Claude Desktop, add the configuration to your Claude Desktop settings:

#### 1. Locate Configuration File

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

#### 2. Add Configuration

```json
{
  "mcpServers": {
    "mockloop": {
      "command": "/path/to/your/mockloop-mcp/.venv/bin/python",
      "args": ["/path/to/your/mockloop-mcp/src/mockloop_mcp/main.py"]
    }
  }
}
```

## Environment Variables

MockLoop MCP supports several environment variables for configuration:

### Core Settings

```bash
# Default port for generated mock servers
export MOCKLOOP_DEFAULT_PORT=8000

# Default output directory for generated mocks
export MOCKLOOP_OUTPUT_DIR=./generated_mocks

# Enable debug logging
export MOCKLOOP_DEBUG=true

# Default host for generated servers
export MOCKLOOP_DEFAULT_HOST=0.0.0.0
```

### Advanced Settings

```bash
# Custom template directory
export MOCKLOOP_TEMPLATE_DIR=./custom_templates

# Database configuration
export MOCKLOOP_DB_PATH=./mockloop.db

# Log level (DEBUG, INFO, WARNING, ERROR)
export MOCKLOOP_LOG_LEVEL=INFO

# Maximum request body size (in bytes)
export MOCKLOOP_MAX_REQUEST_SIZE=10485760

# Request timeout (in seconds)
export MOCKLOOP_REQUEST_TIMEOUT=30
```

### Setting Environment Variables

#### Linux/macOS (Bash/Zsh)

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
# MockLoop MCP Configuration
export MOCKLOOP_DEFAULT_PORT=8000
export MOCKLOOP_OUTPUT_DIR=./generated_mocks
export MOCKLOOP_DEBUG=false
```

#### Windows (PowerShell)

```powershell
# Set environment variables
$env:MOCKLOOP_DEFAULT_PORT = "8000"
$env:MOCKLOOP_OUTPUT_DIR = "./generated_mocks"
$env:MOCKLOOP_DEBUG = "false"
```

#### Windows (Command Prompt)

```cmd
set MOCKLOOP_DEFAULT_PORT=8000
set MOCKLOOP_OUTPUT_DIR=./generated_mocks
set MOCKLOOP_DEBUG=false
```

## Mock Server Configuration

### Default Generation Options

When generating mock servers, you can customize various options:

```python
# Example tool usage with all options
{
  "spec_url_or_path": "https://petstore3.swagger.io/api/v3/openapi.json",
  "output_dir_name": "my_custom_petstore",
  "auth_enabled": true,
  "webhooks_enabled": true,
  "admin_ui_enabled": true,
  "storage_enabled": true
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `spec_url_or_path` | string | Required | URL or local path to API specification |
| `output_dir_name` | string | Auto-generated | Custom name for output directory |
| `auth_enabled` | boolean | `true` | Enable authentication middleware |
| `webhooks_enabled` | boolean | `true` | Enable webhook support |
| `admin_ui_enabled` | boolean | `true` | Enable admin UI |
| `storage_enabled` | boolean | `true` | Enable storage functionality |

### Template Customization

MockLoop uses Jinja2 templates for code generation. You can customize these templates:

#### 1. Copy Default Templates

```bash
cp -r src/mockloop_mcp/templates ./custom_templates
```

#### 2. Modify Templates

Edit the templates in `./custom_templates/`:
- `route_template.j2`: API route generation
- `admin_ui_template.j2`: Admin interface
- `dockerfile_template.j2`: Docker configuration
- `docker_compose_template.j2`: Docker Compose setup
- `middleware_log_template.j2`: Logging middleware

#### 3. Use Custom Templates

```bash
export MOCKLOOP_TEMPLATE_DIR=./custom_templates
```

## Database Configuration

MockLoop uses SQLite for request logging and data storage. You can configure database settings:

### Database Location

```bash
# Custom database directory
export MOCKLOOP_DB_DIR=./data

# Custom database filename pattern
export MOCKLOOP_DB_FILENAME_PATTERN="{server_name}_logs.db"
```

### Database Schema

The database schema is automatically managed through migrations. Current schema includes:

- **request_logs**: HTTP request/response data
- **schema_version**: Database version tracking
- **webhooks**: Webhook configurations
- **scenarios**: Test scenario definitions
- **mock_data**: Dynamic response data

### Migration Settings

```bash
# Enable automatic migrations
export MOCKLOOP_AUTO_MIGRATE=true

# Backup before migrations
export MOCKLOOP_BACKUP_BEFORE_MIGRATE=true

# Migration timeout (seconds)
export MOCKLOOP_MIGRATION_TIMEOUT=300
```

## Logging Configuration

### Log Levels

Configure logging verbosity:

```bash
# Available levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
export MOCKLOOP_LOG_LEVEL=INFO
```

### Log Formats

```bash
# Enable structured JSON logging
export MOCKLOOP_JSON_LOGGING=true

# Custom log format
export MOCKLOOP_LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Log file location
export MOCKLOOP_LOG_FILE=./mockloop.log
```

### Request Logging

Configure request/response logging:

```bash
# Enable request body logging
export MOCKLOOP_LOG_REQUEST_BODY=true

# Enable response body logging
export MOCKLOOP_LOG_RESPONSE_BODY=true

# Maximum body size to log (bytes)
export MOCKLOOP_MAX_LOG_BODY_SIZE=1048576

# Exclude admin requests from logs
export MOCKLOOP_EXCLUDE_ADMIN_LOGS=true
```

## Performance Configuration

### Resource Limits

```bash
# Maximum concurrent requests
export MOCKLOOP_MAX_CONCURRENT_REQUESTS=100

# Request queue size
export MOCKLOOP_REQUEST_QUEUE_SIZE=1000

# Worker thread pool size
export MOCKLOOP_WORKER_THREADS=4
```

### Caching

```bash
# Enable response caching
export MOCKLOOP_ENABLE_CACHING=true

# Cache TTL (seconds)
export MOCKLOOP_CACHE_TTL=300

# Maximum cache size (MB)
export MOCKLOOP_MAX_CACHE_SIZE=100
```

## Security Configuration

### Authentication

```bash
# Default admin password
export MOCKLOOP_ADMIN_PASSWORD=admin123

# JWT secret key
export MOCKLOOP_JWT_SECRET=your-secret-key-here

# Token expiration (seconds)
export MOCKLOOP_TOKEN_EXPIRATION=3600
```

### CORS Settings

```bash
# Enable CORS
export MOCKLOOP_ENABLE_CORS=true

# Allowed origins (comma-separated)
export MOCKLOOP_CORS_ORIGINS="http://localhost:3000,http://localhost:8080"

# Allowed methods
export MOCKLOOP_CORS_METHODS="GET,POST,PUT,DELETE,OPTIONS"
```

## Docker Configuration

### Default Docker Settings

When generating Docker configurations, MockLoop uses these defaults:

```bash
# Base Docker image
export MOCKLOOP_DOCKER_BASE_IMAGE=python:3.9-slim

# Default port mapping
export MOCKLOOP_DOCKER_PORT=8000

# Docker network name
export MOCKLOOP_DOCKER_NETWORK=mockloop-network
```

### Custom Dockerfile Template

You can customize the generated Dockerfile by modifying the template:

```dockerfile
# Custom base image
FROM python:3.11-slim

# Custom working directory
WORKDIR /app

# Custom port
ARG APP_PORT=8000
EXPOSE ${APP_PORT}

# Custom startup command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${APP_PORT}"]
```

## Configuration Validation

MockLoop validates configuration on startup. Common validation errors:

### Invalid Paths
```
Error: MOCKLOOP_OUTPUT_DIR path does not exist: /invalid/path
Solution: Create the directory or use a valid path
```

### Port Conflicts
```
Error: Port 8000 is already in use
Solution: Use MOCKLOOP_DEFAULT_PORT to specify a different port
```

### Permission Issues
```
Error: Permission denied writing to output directory
Solution: Check directory permissions or use a different location
```

## Configuration Examples

### Development Environment

```bash
# .env.development
MOCKLOOP_DEBUG=true
MOCKLOOP_LOG_LEVEL=DEBUG
MOCKLOOP_DEFAULT_PORT=8000
MOCKLOOP_OUTPUT_DIR=./dev_mocks
MOCKLOOP_AUTO_MIGRATE=true
MOCKLOOP_ENABLE_CORS=true
MOCKLOOP_CORS_ORIGINS=http://localhost:3000
```

### Production Environment

```bash
# .env.production
MOCKLOOP_DEBUG=false
MOCKLOOP_LOG_LEVEL=INFO
MOCKLOOP_DEFAULT_PORT=80
MOCKLOOP_OUTPUT_DIR=/var/mockloop/mocks
MOCKLOOP_AUTO_MIGRATE=false
MOCKLOOP_ENABLE_CORS=false
MOCKLOOP_LOG_FILE=/var/log/mockloop.log
```

### Testing Environment

```bash
# .env.testing
MOCKLOOP_DEBUG=true
MOCKLOOP_LOG_LEVEL=DEBUG
MOCKLOOP_DEFAULT_PORT=9000
MOCKLOOP_OUTPUT_DIR=./test_mocks
MOCKLOOP_AUTO_MIGRATE=true
MOCKLOOP_EXCLUDE_ADMIN_LOGS=false
```

## Next Steps

Now that you have MockLoop MCP configured, you're ready to:

1. **[Create Your First Mock Server](first-mock-server.md)**: Detailed walkthrough
2. **[Explore Basic Usage](../guides/basic-usage.md)**: Learn core features
3. **[Advanced Features](../guides/advanced-features.md)**: Discover powerful capabilities

For troubleshooting configuration issues, see the [Troubleshooting Guide](../advanced/troubleshooting.md).