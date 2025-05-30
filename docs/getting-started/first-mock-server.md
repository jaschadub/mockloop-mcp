# Your First Mock Server

This comprehensive guide walks you through creating your first mock server with MockLoop MCP, from specification to running server, with detailed explanations of each step.

## Overview

In this tutorial, you'll:
1. Choose an API specification
2. Generate a complete mock server
3. Explore the generated files
4. Run and test the server
5. Use the admin interface
6. Analyze request logs

## Step 1: Choose Your API Specification

For this tutorial, we'll use the popular Petstore API, but you can use any OpenAPI specification.

### Option A: Petstore API (Recommended for beginners)
```
https://petstore3.swagger.io/api/v3/openapi.json
```

### Option B: Your Own API Specification
If you have your own OpenAPI specification, you can use:
- A URL to a remote specification
- A local file path (JSON or YAML)

### Option C: Other Popular APIs
- **JSONPlaceholder**: `https://jsonplaceholder.typicode.com/`
- **GitHub API**: `https://api.github.com/`
- **Stripe API**: `https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json`

## Step 2: Generate the Mock Server

### Using Your MCP Client

In your MCP client (Cline or Claude Desktop), request mock server generation:

```
Please generate a mock API server using the Petstore OpenAPI specification at:
https://petstore3.swagger.io/api/v3/openapi.json

Name the output directory "my_first_petstore_mock"
```

### What Happens During Generation

MockLoop MCP will:

1. **Download the specification** from the provided URL
2. **Parse the OpenAPI document** to understand the API structure
3. **Generate FastAPI routes** for each endpoint
4. **Create mock responses** based on the schema definitions
5. **Set up logging middleware** for request/response tracking
6. **Generate Docker configuration** for containerized deployment
7. **Create an admin interface** for monitoring and management

### Expected Output

You should see output similar to:

```
✅ Downloaded OpenAPI specification from https://petstore3.swagger.io/api/v3/openapi.json
✅ Parsed API specification: Swagger Petstore - OpenAPI 3.0
✅ Found 19 endpoints across 3 tags
✅ Generated FastAPI application with authentication middleware
✅ Created admin UI with logging capabilities
✅ Generated Docker configuration
✅ Mock server created successfully in: generated_mocks/my_first_petstore_mock/

Your mock server is ready! To start it:
1. cd generated_mocks/my_first_petstore_mock/
2. docker-compose up --build
   OR
   pip install -r requirements_mock.txt && uvicorn main:app --reload
```

## Step 3: Explore the Generated Files

Navigate to your generated mock server directory:

```bash
cd generated_mocks/my_first_petstore_mock/
```

### File Structure

```
my_first_petstore_mock/
├── main.py                    # Main FastAPI application
├── requirements_mock.txt      # Python dependencies
├── Dockerfile                # Docker image configuration
├── docker-compose.yml        # Docker Compose setup
├── logging_middleware.py     # Request/response logging
├── auth_middleware.py        # Authentication middleware
├── webhook_handler.py        # Webhook functionality
├── storage_manager.py        # Data storage management
├── templates/
│   └── admin.html            # Admin UI template
├── db/                       # Database directory (created on first run)
└── logs/                     # Log files directory
```

### Key Files Explained

#### `main.py` - The Heart of Your Mock Server

```python
# Generated FastAPI application
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(
    title="Swagger Petstore - OpenAPI 3.0",
    version="1.0.17",
    description="This is a sample Pet Store Server..."
)

# Example generated endpoint
@app.get("/pet/{petId}")
async def get_pet_by_id(petId: int):
    """Find pet by ID"""
    # Mock response based on OpenAPI schema
    return {
        "id": petId,
        "name": "doggie",
        "category": {"id": 1, "name": "Dogs"},
        "photoUrls": ["string"],
        "tags": [{"id": 0, "name": "string"}],
        "status": "available"
    }
```

#### `requirements_mock.txt` - Dependencies

```
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
jinja2>=3.1.2
aiofiles>=23.2.1
python-multipart>=0.0.6
```

#### `docker-compose.yml` - Container Setup

```yaml
version: '3.8'
services:
  petstore-mock:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./db:/app/db
      - ./logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
```

## Step 4: Run Your Mock Server

### Method 1: Using Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### Method 2: Using Python Directly

```bash
# Install dependencies
pip install -r requirements_mock.txt

# Start the server
uvicorn main:app --reload --port 8000
```

### Verify Server is Running

You should see output like:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1234] using StatReload
INFO:     Started server process [5678]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Step 5: Test Your Mock Server

### Access Points

Once running, your mock server provides several access points:

| URL | Description |
|-----|-------------|
| `http://localhost:8000` | API base URL |
| `http://localhost:8000/docs` | Interactive API documentation (Swagger UI) |
| `http://localhost:8000/redoc` | Alternative API documentation (ReDoc) |
| `http://localhost:8000/admin` | Admin interface |
| `http://localhost:8000/health` | Health check endpoint |

### Test API Endpoints

#### Using curl

```bash
# Get all pets by status
curl "http://localhost:8000/pet/findByStatus?status=available"

# Get a specific pet
curl "http://localhost:8000/pet/1"

# Create a new pet
curl -X POST "http://localhost:8000/pet" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fluffy",
    "category": {"id": 1, "name": "Cats"},
    "photoUrls": ["https://example.com/fluffy.jpg"],
    "status": "available"
  }'

# Update a pet
curl -X PUT "http://localhost:8000/pet" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "name": "Updated Fluffy",
    "status": "sold"
  }'

# Delete a pet
curl -X DELETE "http://localhost:8000/pet/1"
```

#### Using the Interactive Documentation

1. **Open Swagger UI**: Navigate to `http://localhost:8000/docs`
2. **Explore endpoints**: Browse available API operations
3. **Try it out**: Click "Try it out" on any endpoint
4. **Execute requests**: Fill in parameters and click "Execute"
5. **View responses**: See the mock response data

### Expected Responses

All endpoints return realistic mock data based on the OpenAPI schema:

```json
{
  "id": 1,
  "name": "doggie",
  "category": {
    "id": 1,
    "name": "Dogs"
  },
  "photoUrls": ["string"],
  "tags": [
    {
      "id": 0,
      "name": "string"
    }
  ],
  "status": "available"
}
```

## Step 6: Explore the Admin Interface

### Access the Admin UI

Navigate to `http://localhost:8000/admin` to access the comprehensive admin interface.

### Admin Features

#### Dashboard Tab
- **Server Status**: Uptime, version, and health information
- **Quick Stats**: Total requests, error rate, average response time
- **Recent Activity**: Latest API requests

#### Request Logs Tab
- **Real-time Logs**: Live view of incoming requests
- **Filtering**: Filter by method, path, status code, time range
- **Details**: Full request/response data for each entry
- **Export**: Download logs in various formats

#### Log Analytics Tab
- **Performance Metrics**: Response time percentiles (P50, P95, P99)
- **Error Analysis**: Error rates and common failure patterns
- **Traffic Patterns**: Request volume over time
- **Insights**: AI-powered recommendations

#### Webhooks Tab
- **Webhook Management**: Configure webhook endpoints
- **Event Types**: Set up webhooks for different events
- **Testing**: Test webhook delivery
- **History**: View webhook delivery logs

#### API Documentation Tab
- **Swagger UI**: Link to interactive API documentation
- **ReDoc**: Alternative documentation view
- **OpenAPI Spec**: Download the original specification

#### Settings Tab
- **Server Configuration**: Runtime settings
- **Feature Toggles**: Enable/disable features
- **Debug Mode**: Toggle debug logging

## Step 7: Analyze Request Logs

### Using MCP Tools

You can analyze your mock server's logs using MockLoop MCP tools:

```
Please analyze the request logs for my mock server at http://localhost:8000
```

### Expected Analysis Output

```
📊 Mock Server Log Analysis (http://localhost:8000)

📈 Performance Metrics:
- Total Requests: 25
- Average Response Time: 12ms
- P95 Response Time: 45ms
- P99 Response Time: 78ms
- Error Rate: 0%

🔍 Traffic Patterns:
- Most Popular Endpoint: GET /pet/findByStatus (40% of requests)
- Peak Activity: 14:30-15:00 UTC
- Unique Clients: 3

💡 Insights:
- All requests completed successfully
- Response times are excellent (<100ms)
- No error patterns detected
- Consider adding more test scenarios
```

### Manual Log Analysis

You can also query logs directly using the admin API:

```bash
# Get recent logs
curl "http://localhost:8000/admin/api/logs/search?limit=10"

# Filter by endpoint
curl "http://localhost:8000/admin/api/logs/search?path_pattern=/pet/*"

# Get performance analytics
curl "http://localhost:8000/admin/api/logs/analyze"
```

## Step 8: Advanced Features

### Dynamic Response Management

You can modify responses without restarting the server:

```
Please update the response for GET /pet/1 to return a cat instead of a dog
```

### Scenario Management

Create different test scenarios:

```
Please create a test scenario called "error_testing" where:
- GET /pet/1 returns a 404 error
- POST /pet returns a 500 error
- All other endpoints work normally
```

### Performance Testing

Generate load to test performance:

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 http://localhost:8000/pet/1
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Use a different port
uvicorn main:app --port 8001
```

#### Docker Issues
```bash
# Check Docker status
docker --version
docker-compose --version

# View container logs
docker-compose logs

# Restart containers
docker-compose down && docker-compose up --build
```

#### Permission Issues
```bash
# Fix database permissions
chmod 755 db/
chmod 644 db/*.db

# Fix log permissions
chmod 755 logs/
chmod 644 logs/*.log
```

### Getting Help

If you encounter issues:
1. Check the server logs in the terminal
2. Visit the admin interface for diagnostics
3. Review the [Troubleshooting Guide](../advanced/troubleshooting.md)
4. Search [GitHub Issues](https://github.com/mockloop/mockloop-mcp/issues)

## Next Steps

Congratulations! You've successfully created, run, and tested your first mock server. Here's what to explore next:

### Learn More Features
- **[Basic Usage Guide](../guides/basic-usage.md)**: Master the core features
- **[Advanced Features](../guides/advanced-features.md)**: Explore dynamic responses and scenarios
- **[Performance Monitoring](../guides/performance-monitoring.md)**: Deep dive into analytics

### Explore AI Integration
- **[AI Integration Overview](../ai-integration/overview.md)**: Connect with AI frameworks
- **[LangGraph Integration](../ai-integration/langgraph.md)**: Build AI workflows
- **[Custom AI Workflows](../ai-integration/custom-workflows.md)**: Create custom integrations

### API Reference
- **[MCP Tools](../api/mcp-tools.md)**: Complete tool documentation
- **[Admin API](../api/admin-api.md)**: Programmatic server management
- **[Database Schema](../api/database-schema.md)**: Understanding the data model

## Summary

You've learned how to:
- ✅ Generate a mock server from an OpenAPI specification
- ✅ Run the server using Docker or Python
- ✅ Test API endpoints using various methods
- ✅ Use the admin interface for monitoring
- ✅ Analyze request logs and performance
- ✅ Troubleshoot common issues

Your mock server is now ready for development, testing, and integration with your applications!