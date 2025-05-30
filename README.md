![MockLoop](logo.png "MockLoop")

# MockLoop MCP

[![PyPI version](https://img.shields.io/pypi/v/mockloop-mcp.svg)](https://pypi.org/project/mockloop-mcp/)
[![Python versions](https://img.shields.io/pypi/pyversions/mockloop-mcp.svg)](https://pypi.org/project/mockloop-mcp/)
[![Downloads](https://img.shields.io/pypi/dm/mockloop-mcp.svg)](https://pypi.org/project/mockloop-mcp/)
[![License](https://img.shields.io/pypi/l/mockloop-mcp.svg)](https://github.com/mockloop/mockloop-mcp/blob/main/LICENSE)
[![Tests](https://github.com/mockloop/mockloop-mcp/workflows/Tests/badge.svg)](https://github.com/mockloop/mockloop-mcp/actions)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](https://docs.mockloop.com)

`mockloop-mcp` is a comprehensive Model Context Protocol (MCP) server designed to generate and run sophisticated mock API servers from API documentation (e.g., OpenAPI/Swagger specifications). This allows developers and AI assistants to quickly spin up mock backends for development, testing, and integration purposes with advanced logging, dynamic response management, scenario testing, and comprehensive performance analytics.

**📚 Documentation:** https://docs.mockloop.com
**📦 PyPI Package:** https://pypi.org/project/mockloop-mcp/
**🐙 GitHub Repository:** https://github.com/mockloop/mockloop-mcp

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

## Quick Start

Get started with MockLoop MCP in just a few steps:

```bash
# 1. Install from PyPI
pip install mockloop-mcp

# 2. Verify installation
mockloop-mcp --version

# 3. Configure with your MCP client (Cline, Claude Desktop, etc.)
# See configuration examples below
```

That's it! MockLoop MCP is ready to generate mock servers from any OpenAPI specification.

## Getting Started

### Prerequisites

*   Python 3.10+
*   Pip
*   Docker and Docker Compose (for running generated mocks in containers)
*   An MCP client capable of interacting with this server.

### Installation

#### Option 1: Install from PyPI (Recommended)

```bash
# Install the latest stable version
pip install mockloop-mcp

# Or install with optional dependencies
pip install mockloop-mcp[dev]  # Development tools
pip install mockloop-mcp[docs]  # Documentation tools
pip install mockloop-mcp[all]  # All optional dependencies

# Verify installation
mockloop-mcp --version
```

#### Option 2: Development Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/mockloop/mockloop-mcp.git
    cd mockloop-mcp
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    # On Windows: .venv\Scripts\activate
    ```

3.  **Install in development mode:**
    ```bash
    pip install -e ".[dev]"
    ```

### Setup & Configuration

**Dependencies include:**
- Core: `fastapi`, `uvicorn`, `Jinja2`, `PyYAML`, `requests`, `aiohttp`
- MCP: `mcp[cli]` (Model Context Protocol SDK)

#### Running the MCP Server

**Development Mode:**
```bash
# If installed from PyPI
mockloop-mcp

# If using development installation
mcp dev src/mockloop_mcp/main.py
```

**Production Mode:**
```bash
# If installed from PyPI
mockloop-mcp

# If using development installation
mcp run src/mockloop_mcp/main.py
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
      "command": "mockloop-mcp",
      "args": [],
      "transportType": "stdio"
    }
  }
}
```

**For virtual environment installations:**
```json
{
  "mcpServers": {
    "MockLoopLocal": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "command": "/path/to/your/venv/bin/python",
      "args": ["-m", "mockloop_mcp"],
      "transportType": "stdio"
    }
  }
}
```

#### Claude Desktop

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

**For virtual environment installations:**
```json
{
  "mcpServers": {
    "mockloop": {
      "command": "/path/to/your/venv/bin/python",
      "args": ["-m", "mockloop_mcp"]
    }
  }
}
```

#### Other MCP Clients

For other MCP clients, use the command `mockloop-mcp` or `python -m mockloop_mcp` depending on your installation method.

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

4.  **Access Enhanced Features:**
    - **Admin UI**: `http://localhost:8000/admin` - Enhanced interface with Log Analytics tab
    - **API Documentation**: `http://localhost:8000/docs` - Interactive Swagger UI
    - **Health Check**: `http://localhost:8000/health` - Server status and metrics
    - **Log Search API**: `http://localhost:8000/admin/api/logs/search` - Advanced log querying
    - **Performance Analytics**: `http://localhost:8000/admin/api/logs/analyze` - Performance insights
    - **Scenario Management**: `http://localhost:8000/admin/api/mock-data/scenarios` - Dynamic response management

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

MockLoop MCP is specifically designed to enhance AI-assisted development workflows with comprehensive testing and analysis capabilities:

### Enhanced AI Workflow
1. **Generate Mock Server**: AI creates an OpenAPI spec and generates a mock server using `generate_mock_api`
2. **Start Testing**: AI runs the mock server and begins making test requests
3. **Monitor & Analyze**: AI uses `query_mock_logs` to analyze request patterns, performance, and errors
4. **Create Scenarios**: AI uses `manage_mock_data` to create dynamic test scenarios for edge cases
5. **Performance Optimization**: Based on insights, AI modifies configurations and repeats the cycle
6. **Discover & Manage**: AI uses `discover_mock_servers` to manage multiple mock environments

### Key Benefits for AI Development
- **Dynamic Response Management**: Modify API responses in real-time without server restart
- **Scenario-Based Testing**: Create and switch between different test scenarios instantly
- **Advanced Performance Analytics**: P95/P99 response times, error rate analysis, session tracking
- **Intelligent Debugging**: AI-powered insights with actionable recommendations
- **Framework Integration**: Native support for LangGraph, CrewAI, and LangChain workflows
- **Comprehensive Monitoring**: Track everything from response times to traffic patterns with session correlation

### Enhanced AI Assistant Usage
```
AI: "Let me generate a comprehensive API testing environment"
1. Uses generate_mock_api with OpenAPI spec
2. Starts the mock server with enhanced logging
3. Creates multiple test scenarios using manage_mock_data
4. Runs comprehensive test suite across scenarios
5. Uses query_mock_logs for deep performance analysis
6. Gets insights: "P95 response time: 120ms, 2% error rate in error scenario,
   session correlation shows 95% success rate, recommendation: optimize /users endpoint"
7. Dynamically adjusts responses and continues testing
8. Discovers all running servers for environment management
```

### Advanced Scenario Management
```python
# AI can dynamically create test scenarios
await manage_mock_data(
    server_url="http://localhost:8000",
    operation="create_scenario",
    scenario_name="high_load_testing",
    scenario_config={
        "endpoints": {
            "/users": {"GET": {"status": 200, "delay": 500}},
            "/orders": {"POST": {"status": 503, "error": "Service Unavailable"}}
        }
    }
)

# Switch scenarios for different test phases
await manage_mock_data(
    server_url="http://localhost:8000",
    operation="switch_scenario",
    scenario_name="error_testing"
)

# Analyze performance across scenarios
logs = await query_mock_logs(
    server_url="http://localhost:8000",
    analyze=True,
    time_from="2025-01-01T00:00:00Z"
)
```

## Future Ideas & Roadmap

### Phase 2 ✅ COMPLETED
*   ✅ **Dynamic Mock Data Management:** Real-time response updates without server restart
*   ✅ **Server Lifecycle Management:** Comprehensive server discovery and health monitoring
*   ✅ **Scenario Management:** Save and switch between different mock configurations with database persistence
*   ✅ **Enhanced Admin API:** Advanced log search, mock data updates, performance analytics
*   ✅ **Database Migration System:** Robust schema versioning and migration framework
*   ✅ **Performance Monitoring:** Session tracking, correlation IDs, P95/P99 metrics

### Phase 3 (In Development)
*   **Enhanced Response Mocking:**
    *   Use `examples` or `example` fields from the OpenAPI spec for more realistic mock responses
    *   Support for dynamic data generation (e.g., using Faker)
    *   Custom response mappings and scripts
*   **Server Lifecycle Management:**
    *   Start/stop mock servers programmatically via MCP tools
    *   Container orchestration and scaling
    *   Multi-environment management
*   **Advanced Testing Features:**
    *   Load testing and performance simulation
    *   Chaos engineering capabilities
    *   Contract testing integration

### Phase 4 (Planned)
*   **More API Specification Formats:**
    *   Postman Collections
    *   GraphQL SDL
    *   RAML
    *   API Blueprint
    *   gRPC Protobufs (may require conversion for FastAPI)
*   **Advanced Features:**
    *   Stateful mocks with persistent data
    *   Advanced validation and schema enforcement
    *   Integration with testing frameworks
    *   CLI tool for standalone usage
    *   Real-time collaboration features

### Prioritized Support Roadmap for API Formats
1.  **OpenAPI (Swagger)** - *Current Focus*
2.  **Postman Collections**
3.  **GraphQL SDL**
4.  **RAML**
5.  **API Blueprint**
6.  **gRPC Protobufs**

### 4. `manage_mock_data` ✨ NEW
Manage dynamic response data and scenarios for MockLoop servers without server restart.

**Parameters:**
*   `server_url`: (string, required) URL of the mock server (e.g., "http://localhost:8000").
*   `operation`: (string, required) Operation to perform: "update_response", "create_scenario", "switch_scenario", "list_scenarios".
*   `endpoint_path`: (string, optional) API endpoint path for response updates.
*   `response_data`: (object, optional) New response data for endpoint updates.
*   `scenario_name`: (string, optional) Name for scenario operations.
*   `scenario_config`: (object, optional) Scenario configuration for creation.

**Output:**
*   Success confirmation for operations
*   Scenario lists and current active scenario
*   Dynamic response updates without server restart
*   Runtime configuration management

## Framework Integration Examples

MockLoop MCP integrates seamlessly with popular AI frameworks for enhanced development workflows:

### LangGraph Integration

```python
from langgraph.graph import StateGraph, END
from mockloop_mcp import MockLoopClient

# Initialize MockLoop client
mockloop = MockLoopClient()

def setup_mock_api(state):
    """Generate mock API for testing"""
    result = mockloop.generate_mock_api(
        spec_url_or_path="https://api.example.com/openapi.json",
        output_dir_name="langgraph_test_api"
    )
    state["mock_server_url"] = "http://localhost:8000"
    return state

def test_api_endpoints(state):
    """Test API endpoints and analyze logs"""
    # Make test requests to mock server
    # ... your API testing logic ...
    
    # Analyze request logs
    logs = mockloop.query_mock_logs(
        server_url=state["mock_server_url"],
        analyze=True
    )
    state["test_results"] = logs
    return state

def create_test_scenario(state):
    """Create dynamic test scenarios"""
    mockloop.manage_mock_data(
        server_url=state["mock_server_url"],
        operation="create_scenario",
        scenario_name="error_testing",
        scenario_config={
            "endpoints": {
                "/users": {"GET": {"status": 500, "error": "Internal Server Error"}}
            }
        }
    )
    return state

# Build LangGraph workflow
workflow = StateGraph(dict)
workflow.add_node("setup_mock", setup_mock_api)
workflow.add_node("test_endpoints", test_api_endpoints)
workflow.add_node("create_scenario", create_test_scenario)

workflow.set_entry_point("setup_mock")
workflow.add_edge("setup_mock", "test_endpoints")
workflow.add_edge("test_endpoints", "create_scenario")
workflow.add_edge("create_scenario", END)

app = workflow.compile()
```

### CrewAI Integration

```python
from crewai import Agent, Task, Crew
from mockloop_mcp import MockLoopClient

# Initialize MockLoop client
mockloop = MockLoopClient()

# Define API Testing Agent
api_tester = Agent(
    role='API Testing Specialist',
    goal='Generate and test mock APIs for development',
    backstory='Expert in API testing and mock server management',
    tools=[mockloop.generate_mock_api, mockloop.query_mock_logs]
)

# Define Performance Analyst Agent
performance_analyst = Agent(
    role='Performance Analyst',
    goal='Analyze API performance and provide optimization insights',
    backstory='Specialist in API performance monitoring and analysis',
    tools=[mockloop.query_mock_logs, mockloop.discover_mock_servers]
)

# Define Scenario Manager Agent
scenario_manager = Agent(
    role='Test Scenario Manager',
    goal='Create and manage different testing scenarios',
    backstory='Expert in test scenario design and execution',
    tools=[mockloop.manage_mock_data]
)

# Define tasks
setup_task = Task(
    description='Generate a mock API server from the provided OpenAPI specification',
    agent=api_tester,
    expected_output='Mock server running with comprehensive logging'
)

analysis_task = Task(
    description='Analyze request logs and provide performance insights',
    agent=performance_analyst,
    expected_output='Detailed performance analysis with recommendations'
)

scenario_task = Task(
    description='Create test scenarios for edge cases and error conditions',
    agent=scenario_manager,
    expected_output='Multiple test scenarios configured and ready'
)

# Create crew
crew = Crew(
    agents=[api_tester, performance_analyst, scenario_manager],
    tasks=[setup_task, analysis_task, scenario_task],
    verbose=True
)

# Execute workflow
result = crew.kickoff()
```

### LangChain Integration

```python
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from mockloop_mcp import MockLoopClient

# Initialize MockLoop client
mockloop = MockLoopClient()

# Define MockLoop tools for LangChain
def generate_mock_api_tool(spec_path: str) -> str:
    """Generate a mock API server from specification"""
    result = mockloop.generate_mock_api(spec_url_or_path=spec_path)
    return f"Mock API generated successfully: {result}"

def analyze_api_logs_tool(server_url: str) -> str:
    """Analyze API request logs and performance"""
    logs = mockloop.query_mock_logs(server_url=server_url, analyze=True)
    return f"Log analysis complete: {logs['analysis']}"

def manage_test_scenarios_tool(server_url: str, scenario_name: str) -> str:
    """Create and manage test scenarios"""
    result = mockloop.manage_mock_data(
        server_url=server_url,
        operation="create_scenario",
        scenario_name=scenario_name,
        scenario_config={"endpoints": {"/test": {"GET": {"status": 200}}}}
    )
    return f"Scenario '{scenario_name}' created successfully"

# Create LangChain tools
tools = [
    Tool(
        name="GenerateMockAPI",
        func=generate_mock_api_tool,
        description="Generate a mock API server from OpenAPI specification"
    ),
    Tool(
        name="AnalyzeAPILogs",
        func=analyze_api_logs_tool,
        description="Analyze API request logs and get performance insights"
    ),
    Tool(
        name="ManageTestScenarios",
        func=manage_test_scenarios_tool,
        description="Create and manage API test scenarios"
    )
]

# Create agent
llm = ChatOpenAI(temperature=0)
prompt = PromptTemplate.from_template("""
You are an API testing assistant with access to MockLoop tools.
Help users generate mock APIs, analyze performance, and manage test scenarios.

Tools available:
{tools}

Tool names: {tool_names}

Question: {input}
{agent_scratchpad}
""")

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Example usage
response = agent_executor.invoke({
    "input": "Generate a mock API from https://petstore.swagger.io/v2/swagger.json and analyze its performance"
})
```

## Changelog

### Version 2.1.0 - Complete Enhancement Integration
**Released: May 2025**

#### 🆕 Major Features
- **Dynamic Response Management**: Real-time response updates without server restart via `manage_mock_data` tool
- **Advanced Scenario Management**: Create, switch, and manage test scenarios with persistent storage
- **Enhanced Performance Monitoring**: Comprehensive performance metrics with session tracking and analytics
- **Database Migration System**: Robust schema versioning and migration framework
- **Framework Integration**: Native support for LangGraph, CrewAI, and LangChain workflows

#### 🔧 New MCP Tools
- `manage_mock_data`: Dynamic response management and scenario handling
- Enhanced `query_mock_logs`: Advanced filtering with session and performance analytics
- Enhanced `discover_mock_servers`: Comprehensive server discovery with health monitoring

#### 📦 New Components
- **Database Migration System**: Full versioning and migration framework (`database_migration.py`)
- **HTTP Client Extensions**: Enhanced MockServerClient with admin API integration (`utils/http_client.py`)
- **Enhanced Log Analyzer**: AI-powered insights generation with performance metrics (`log_analyzer.py`)
- **Scenario Management**: Complete scenario lifecycle management with database persistence

#### 🚀 Enhanced Features
- **Advanced Admin UI**: Log Analytics tab with search, filtering, and scenario management
- **Session Tracking**: Comprehensive session analytics with correlation IDs
- **Performance Metrics**: P95/P99 response times, error rate analysis, traffic pattern detection
- **Runtime Configuration**: Dynamic endpoint behavior modification without restart
- **Enhanced Database Schema**: 20+ columns including session tracking, performance metrics, and scenario data

#### 🔧 Technical Improvements
- Enhanced database schema with automatic migration (versions 0-6)
- Improved error handling and logging throughout the system
- Advanced SQL query optimization with proper indexing
- Concurrent access protection and transaction safety
- Backup creation before migrations for data safety
- Enhanced Docker integration with better port management

### Version 2.0.0 - Enhanced AI Assistant Integration
**Released: May 2025**

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
**Released: 2025**

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
