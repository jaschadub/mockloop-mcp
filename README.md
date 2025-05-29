![MockLoop](logo.png "MockLoop")
# MCP Server (`mockloop-mcp`)

`mockloop-mcp` is a Model Context Protocol (MCP) server designed to generate and run mock API servers from API documentation (e.g., OpenAPI/Swagger specifications). This allows developers and AI assistants to quickly spin up mock backends for development, testing, and integration purposes with advanced logging and analysis capabilities.

## Features

### Core Features
*   **API Mock Generation:** Takes an API specification (URL or local file) and generates a runnable FastAPI mock server.
*   **Request/Response Logging:** Generated mock servers include middleware for comprehensive logging of requests and responses with SQLite storage.
*   **Dockerized Mocks:** Generates a `Dockerfile` and `docker-compose.yml` for each mock API, allowing them to be easily run as Docker containers.
*   **Initial Support:** OpenAPI v2 (Swagger) and v3 (JSON, YAML).

### Enhanced Features (v2.0)
*   **🔍 Advanced Log Analysis:** Query and analyze request logs with filtering, performance metrics, and intelligent insights.
*   **🖥️ Server Discovery:** Automatically discover running mock servers and match them with generated configurations.
*   **📊 Performance Monitoring:** Real-time performance metrics, error rate analysis, and traffic pattern detection.
*   **🤖 AI Assistant Integration:** Optimized for AI-assisted development workflows with structured data output and comprehensive analysis.
*   **🎯 Smart Filtering:** Advanced log filtering by method, path patterns, time ranges, and custom criteria.
*   **📈 Insights Generation:** Automated analysis with actionable recommendations for debugging and optimization.

## Getting Started

### Prerequisites

*   Python 3.9+
*   Pip
*   Docker and Docker Compose (for running generated mocks in containers)
*   An MCP client capable of interacting with this server.

### Installation & Setup (for `mockloop-mcp` server)

1.  **Clone the repository (if applicable):**
    ```bash
    # git clone <repository-url>
    # cd mockloop-mcp
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    
    **Dependencies include:**
    - Core: `fastapi`, `uvicorn`, `Jinja2`, `PyYAML`, `requests`
    - Enhanced: `aiohttp` (for async HTTP client functionality)
    - MCP: `mcp[cli]` (Model Context Protocol SDK)

4.  **Run the MCP Server (Development Mode):**
    The recommended way to run the server during development is using the `mcp` CLI:
    ```bash
    # Ensure your virtual environment is active
    # source .venv/bin/activate
    mcp dev src/mockloop_mcp/main.py
    ```
    This will start the MockLoop MCP server, and you can interact with it using tools like the MCP Inspector or Claude Desktop.

5.  **Run the MCP Server (Standalone/Production):**
    For direct execution or custom deployments:
    ```bash
    # Ensure your virtual environment is active
    mcp run src/mockloop_mcp/main.py
    # Or, if you've structured main.py to call mcp_server.run() in __main__:
    # python src/mockloop_mcp/main.py 
    ```

### Configuring MCP Clients

To use MockLoop MCP with your MCP client, you'll need to add it to your client's configuration.

#### Cline (VS Code Extension)

Add the following to your Cline MCP settings file (typically located at `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`):

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

**Important:** Replace `/path/to/your/mockloop-mcp/` with the actual path to your MockLoop MCP installation.

#### Claude Desktop

Add the following to your Claude Desktop configuration file:

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

## Available MCP Tools

Once `mockloop-mcp` is configured and running in your MCP client, you can use the following tools:

### 1. `generate_mock_api`
Generate a FastAPI mock server from an API specification.

**Parameters:**
*   `spec_url_or_path`: (string, required) URL or local file path to the API specification (e.g., `https://petstore3.swagger.io/api/v3/openapi.json` or `./my_api.yaml`).
*   `output_dir_name`: (string, optional) Name for the directory where the mock server code will be generated (e.g., `my_petstore_mock`). Defaults to a name derived from the API spec.
*   `auth_enabled`: (boolean, optional) Enable authentication middleware (default: true).
*   `webhooks_enabled`: (boolean, optional) Enable webhook support (default: true).
*   `admin_ui_enabled`: (boolean, optional) Enable admin UI (default: true).
*   `storage_enabled`: (boolean, optional) Enable storage functionality (default: true).

**Output:**
The tool will generate a new directory (e.g., `generated_mocks/my_petstore_mock/`) containing:
*   `main.py`: The FastAPI application with admin endpoints.
*   `requirements_mock.txt`: Dependencies for the mock server.
*   `Dockerfile`: For building the mock server Docker image.
*   `docker-compose.yml`: For running the mock server with Docker Compose.
*   `logging_middleware.py`: Request/response logging with SQLite storage.
*   `templates/admin.html`: Admin UI for monitoring and management.

### 2. `query_mock_logs` ✨ NEW
Query and analyze request logs from running mock servers with advanced filtering and analysis.

**Parameters:**
*   `server_url`: (string, required) URL of the mock server (e.g., "http://localhost:8000").
*   `limit`: (integer, optional) Maximum number of logs to return (default: 100).
*   `offset`: (integer, optional) Number of logs to skip for pagination (default: 0).
*   `method`: (string, optional) Filter by HTTP method (e.g., "GET", "POST").
*   `path_pattern`: (string, optional) Regex pattern to filter paths.
*   `time_from`: (string, optional) Start time filter (ISO format).
*   `time_to`: (string, optional) End time filter (ISO format).
*   `include_admin`: (boolean, optional) Include admin requests in results (default: false).
*   `analyze`: (boolean, optional) Perform analysis on the logs (default: true).

**Output:**
*   Filtered log entries with metadata
*   Performance metrics (response times, percentiles)
*   Error rate analysis and categorization
*   Traffic patterns and insights
*   Automated recommendations for debugging

### 3. `discover_mock_servers` ✨ NEW
Discover running MockLoop servers and generated mock configurations.

**Parameters:**
*   `ports`: (array, optional) List of ports to scan (default: common ports 8000-8005, 3000-3001, 5000-5001).
*   `check_health`: (boolean, optional) Perform health checks on discovered servers (default: true).
*   `include_generated`: (boolean, optional) Include information about generated but not running mocks (default: true).

**Output:**
*   List of running mock servers with health status
*   Generated mock configurations and metadata
*   Server matching and correlation
*   Port usage and availability information

### Running a Generated Mock Server

1.  **Navigate to the generated mock directory:**
    ```bash
    cd generated_mocks/your_generated_mock_api_name
    ```

2.  **Using Docker Compose (Recommended):**
    ```bash
    docker-compose up --build
    ```
    The mock API will typically be available at `http://localhost:8000` (or the port specified during generation/in `docker-compose.yml`). Logs will be streamed to your console.

3.  **Using Uvicorn directly (Requires Python and pip install in that environment):**
    ```bash
    # (Activate a virtual environment if desired for the mock)
    # pip install -r requirements_mock.txt 
    # uvicorn main:app --reload --port 8000 
    ```

## Dockerfile Snippet (Example for a generated mock)

This is an example of what the generated `Dockerfile` might look like:

```dockerfile
FROM python:3.9-slim

ARG APP_PORT=8000

WORKDIR /app

COPY ./requirements_mock.txt .
RUN pip install --no-cache-dir -r requirements_mock.txt

COPY ./main.py .
# COPY ./logging_middleware.py . # If logging middleware is in a separate file

EXPOSE ${APP_PORT}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${APP_PORT}"]
```

## AI Assistant Integration

MockLoop MCP is specifically designed to enhance AI-assisted development workflows:

### Typical AI Workflow
1. **Generate Mock Server**: AI creates an OpenAPI spec and generates a mock server using `generate_mock_api`
2. **Start Testing**: AI runs the mock server and begins making test requests
3. **Monitor & Analyze**: AI uses `query_mock_logs` to analyze request patterns, performance, and errors
4. **Iterate & Improve**: Based on insights, AI modifies code and repeats the cycle
5. **Discover & Manage**: AI uses `discover_mock_servers` to manage multiple mock environments

### Key Benefits for AI Development
- **Rapid Feedback Loop**: Get immediate insights about API behavior and performance
- **Intelligent Debugging**: Automated analysis helps identify issues and patterns
- **Data-Driven Decisions**: Performance metrics and error analysis guide optimization
- **Seamless Integration**: Structured data output optimized for AI consumption
- **Comprehensive Monitoring**: Track everything from response times to traffic patterns

### Example AI Assistant Usage
```
AI: "Let me generate a mock API for user management and test it"
1. Uses generate_mock_api with OpenAPI spec
2. Starts the mock server
3. Makes test requests to various endpoints
4. Uses query_mock_logs to analyze performance
5. Gets insights: "Average response time: 45ms, 0% error rate, most accessed: GET /users"
6. Continues development with confidence
```

## Future Ideas & Roadmap

### Phase 2 (In Development)
*   **Dynamic Mock Data Management:** Real-time response updates without server restart
*   **Server Lifecycle Management:** Start/stop mock servers programmatically via MCP tools
*   **Scenario Management:** Save and switch between different mock configurations
*   **Enhanced Admin API:** Advanced log search, mock data updates, server control

### Phase 3 (Planned)
*   **Enhanced Response Mocking:**
    *   Use `examples` or `example` fields from the OpenAPI spec for more realistic mock responses
    *   Support for dynamic data generation (e.g., using Faker)
    *   Custom response mappings and scripts
*   **More API Specification Formats:**
    *   Postman Collections
    *   GraphQL SDL
    *   RAML
    *   API Blueprint
    *   gRPC Protobufs (may require conversion for FastAPI)
*   **Advanced Features:**
    *   Stateful mocks with persistent data
    *   Load testing and performance simulation
    *   Advanced validation and schema enforcement
    *   Integration with testing frameworks
    *   CLI tool for standalone usage

### Prioritized Support Roadmap for API Formats
1.  **OpenAPI (Swagger)** - *Current Focus*
2.  **Postman Collections**
3.  **GraphQL SDL**
4.  **RAML**
5.  **API Blueprint**
6.  **gRPC Protobufs**

## Changelog

### Version 2.0.0 - Enhanced AI Assistant Integration
**Released: January 2025**

#### 🆕 New Features
- **Advanced Log Analysis**: Query and analyze request logs with filtering, performance metrics, and intelligent insights
- **Server Discovery**: Automatically discover running mock servers and match them with generated configurations
- **Performance Monitoring**: Real-time performance metrics, error rate analysis, and traffic pattern detection
- **AI Assistant Integration**: Optimized for AI-assisted development workflows with structured data output

#### 🔧 New MCP Tools
- `query_mock_logs`: Advanced log querying with filtering and analysis capabilities
- `discover_mock_servers`: Comprehensive server discovery and health monitoring

#### 📦 New Components
- **HTTP Client**: Async HTTP client for mock server communication (`utils/http_client.py`)
- **Server Manager**: Mock server discovery and management (`mock_server_manager.py`)
- **Log Analyzer**: Advanced log analysis with insights generation (`log_analyzer.py`)

#### 🚀 Enhancements
- Enhanced admin UI with auto-refresh and advanced filtering
- SQLite-based request logging with comprehensive metadata
- Performance metrics calculation (response times, percentiles, error rates)
- Traffic pattern detection (bot detection, high-volume clients)
- Automated insights and recommendations for debugging

#### 🔧 Technical Improvements
- Added `aiohttp` dependency for async HTTP operations
- Improved error handling and logging throughout the system
- Enhanced database schema with admin request filtering
- Better Docker integration and port management

### Version 1.0.0 - Initial Release
**Released: 2024**

#### 🆕 Initial Features
- API mock generation from OpenAPI specifications
- FastAPI-based mock servers with Docker support
- Basic request/response logging
- Admin UI for monitoring
- Authentication and webhook support

## Contributing

We welcome contributions! Please see our [Enhancement Plan](ENHANCEMENT_PLAN.md) for current development priorities and planned features.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install dependencies: `pip install -r requirements.txt`
4. Make your changes
5. Test with existing mock servers
6. Submit a pull request

## License

This project is licensed under the [MIT License](LICENSE).
