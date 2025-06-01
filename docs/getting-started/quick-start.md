# Quick Start

Get up and running with MockLoop MCP in just a few minutes! This guide will walk you through generating your first mock API server.

## Prerequisites

Before starting, ensure you have:  
- ✅ [Installed MockLoop MCP from PyPI](installation.md)  
- ✅ An MCP client configured (Cline or Claude Desktop)  
- ✅ A sample OpenAPI specification (we'll provide one)  

## Step 1: Install MockLoop MCP

If you haven't already, install MockLoop MCP from PyPI:

```bash
# Create and activate virtual environment (recommended)
python3 -m venv mockloop-env
source mockloop-env/bin/activate  # On Windows: mockloop-env\Scripts\activate

# Install MockLoop MCP
pip install mockloop-mcp

# Verify installation
mockloop-mcp --version
```

## Step 2: Configure Your MCP Client

The MockLoop MCP server runs automatically when configured with your MCP client. No manual server startup is required.

### Using Cline (VS Code Extension)

1. **Open VS Code** with the Cline extension installed
2. **Configure MCP Settings** by adding MockLoop to your Cline MCP settings file:

```json
{
  "mcpServers": {
    "MockLoopLocal": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "command": "mockloop-mcp",
      "args": [],
      "transportType": "stdio"
    }
  }
}
```

**Alternative for virtual environment:**
```json
{
  "mcpServers": {
    "MockLoopLocal": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "command": "/path/to/your/mockloop-env/bin/python",
      "args": ["-m", "mockloop_mcp"],
      "transportType": "stdio"
    }
  }
}
```

3. **Restart Cline** to load the new configuration

### Using Claude Desktop

Add the following to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "mockloop": {
      "command": "mockloop-mcp",
      "args": []
    }
  }
}
```

**Alternative for virtual environment:**
```json
{
  "mcpServers": {
    "mockloop": {
      "command": "/path/to/your/mockloop-env/bin/python",
      "args": ["-m", "mockloop_mcp"]
    }
  }
}
```

## Step 3: Generate Your First Mock Server

Now let's generate a mock server using the Petstore API as an example:

### Using the MCP Tool

In your MCP client, use the `generate_mock_api` tool:

```
Please generate a mock API server using the Petstore OpenAPI specification:
https://petstore3.swagger.io/api/v3/openapi.json
```

### Expected Output

MockLoop MCP will:

1. **Download** the OpenAPI specification
2. **Parse** the API definition
3. **Generate** a complete FastAPI mock server
4. **Create** Docker configuration files
5. **Set up** request/response logging

You'll see a new directory created: `generated_mocks/petstore_api/`

## Step 4: Explore the Generated Files

Navigate to your generated mock server:

```bash
cd generated_mocks/petstore_api/
ls -la
```

You should see:

```
├── main.py                 # FastAPI application
├── requirements_mock.txt   # Dependencies
├── Dockerfile             # Docker image configuration
├── docker-compose.yml     # Docker Compose setup
├── logging_middleware.py  # Request/response logging
├── templates/
│   └── admin.html         # Admin UI
└── db/                    # SQLite database directory
```

## Step 5: Run Your Mock Server

### Option A: Using Docker Compose (Recommended)

```bash
docker-compose up --build
```

### Option B: Using Python Directly

```bash
# Install dependencies
pip install -r requirements_mock.txt

# Run the server
uvicorn main:app --reload --port 8000
```

## Step 6: Test Your Mock Server

Once running, your mock server will be available at `http://localhost:8000`.

### Access Points

- **API Documentation**: `http://localhost:8000/docs`
- **Admin UI**: `http://localhost:8000/admin`
- **Health Check**: `http://localhost:8000/health`
- **API Endpoints**: `http://localhost:8000/pet`, `http://localhost:8000/store/order`, etc.

### Test API Endpoints

Try making some requests:

```bash
# Get all pets
curl http://localhost:8000/pet/findByStatus?status=available

# Get a specific pet
curl http://localhost:8000/pet/1

# Create a new pet (POST)
curl -X POST http://localhost:8000/pet \
  -H "Content-Type: application/json" \
  -d '{"name": "Fluffy", "status": "available"}'
```

## Step 7: Explore Advanced Features

### Admin UI

Visit `http://localhost:8000/admin` to access the admin interface:

- **Dashboard**: Overview of server status and metrics
- **Request Logs**: View all incoming requests and responses
- **Log Analytics**: Performance metrics and insights
- **Webhooks**: Configure webhook endpoints
- **API Documentation**: Links to Swagger UI and ReDoc

### Request Logging

All requests are automatically logged to a SQLite database. You can query logs using the MCP tools:

```
Please analyze the request logs for my mock server at http://localhost:8000
```

### Performance Monitoring

MockLoop automatically tracks:
- Response times (P95, P99 percentiles)
- Error rates
- Traffic patterns
- Session correlation

## Next Steps

Congratulations! You've successfully created and run your first mock server. Here's what to explore next:

### Learn More Features
- **[Configuration](configuration.md)**: Customize your mock servers
- **[Advanced Features](../guides/advanced-features.md)**: Explore dynamic responses and scenarios
- **[AI Integration](../ai-integration/overview.md)**: Integrate with AI frameworks

### Explore MCP Tools
- **`query_mock_logs`**: Analyze request patterns and performance
- **`discover_mock_servers`**: Find and manage running servers
- **`manage_mock_data`**: Update responses and create scenarios

### Common Use Cases
- **API Development**: Mock dependencies while building your API
- **Frontend Development**: Create realistic backend responses
- **Testing**: Generate test scenarios and edge cases
- **Documentation**: Provide interactive API examples

## Troubleshooting

### Server Won't Start
```bash
# Check if port is already in use
lsof -i :8000

# Use a different port
uvicorn main:app --port 8001
```

### Docker Issues
```bash
# Check Docker status
docker --version
docker-compose --version

# View logs
docker-compose logs
```

### MCP Connection Issues
1. Verify the MCP server is running
2. Check file paths in your MCP client configuration
3. Ensure Python virtual environment is activated
4. Check for any error messages in the MCP client

### Getting Help

If you encounter issues:  
1. Check the [Troubleshooting Guide](../advanced/troubleshooting.md)  
2. Review [GitHub Issues](https://github.com/mockloop/mockloop-mcp/issues)  

## Example Specifications

Here are some popular OpenAPI specifications you can try:

- **Petstore**: `https://petstore3.swagger.io/api/v3/openapi.json`
- **JSONPlaceholder**: `https://jsonplaceholder.typicode.com/`
- **GitHub API**: `https://api.github.com/`
- **Stripe API**: `https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json`

Ready to dive deeper? Continue to the [Configuration Guide](configuration.md) to learn how to customize your mock servers!