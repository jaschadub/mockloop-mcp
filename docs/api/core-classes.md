# Core Classes

This document provides comprehensive documentation for the core Python classes in MockLoop MCP. These classes form the foundation of the mock server generation and management system.

## MockLoopClient

The main client class for interacting with MockLoop MCP services.

### Class Definition

```python
class MockLoopClient:
    """
    Main client for MockLoop MCP operations.
    
    Provides methods for generating mock servers, managing mock data,
    querying logs, and discovering running servers.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize MockLoop client.
        
        Args:
            base_url: Base URL for MockLoop MCP server (optional)
        """
```

### Methods

#### generate_mock_api()

Generate a mock API server from an OpenAPI specification.

```python
async def generate_mock_api(
    self,
    spec_url_or_path: str,
    output_dir_name: Optional[str] = None,
    auth_enabled: bool = True,
    webhooks_enabled: bool = True,
    admin_ui_enabled: bool = True,
    storage_enabled: bool = True
) -> Dict[str, Any]:
    """
    Generate a FastAPI mock server from an API specification.
    
    Args:
        spec_url_or_path: URL or file path to OpenAPI specification
        output_dir_name: Name for output directory (auto-generated if None)
        auth_enabled: Enable authentication middleware
        webhooks_enabled: Enable webhook support
        admin_ui_enabled: Enable admin UI interface
        storage_enabled: Enable persistent storage
        
    Returns:
        Dict containing generation results and server information
        
    Raises:
        ValueError: If specification is invalid
        FileNotFoundError: If specification file not found
        GenerationError: If mock generation fails
    """
```

**Example Usage:**

```python
client = MockLoopClient()

# Generate basic mock server
result = await client.generate_mock_api(
    spec_url_or_path="./api-spec.yaml",
    output_dir_name="my_mock_server"
)

# Generate with custom configuration
result = await client.generate_mock_api(
    spec_url_or_path="https://api.example.com/openapi.json",
    auth_enabled=False,
    webhooks_enabled=True,
    admin_ui_enabled=True,
    storage_enabled=False
)
```

#### manage_mock_data()

Manage dynamic response data and scenarios for mock servers.

```python
async def manage_mock_data(
    self,
    server_url: str,
    operation: str,
    endpoint_path: Optional[str] = None,
    response_data: Optional[Dict[str, Any]] = None,
    scenario_name: Optional[str] = None,
    scenario_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Manage mock server data and scenarios.
    
    Args:
        server_url: URL of the mock server
        operation: Operation to perform (update_response, create_scenario, 
                  switch_scenario, list_scenarios)
        endpoint_path: API endpoint path (for update_response)
        response_data: Response data to set (for update_response)
        scenario_name: Name of scenario (for scenario operations)
        scenario_config: Scenario configuration (for create_scenario)
        
    Returns:
        Dict containing operation results
        
    Raises:
        ValueError: If invalid operation or missing required parameters
        ConnectionError: If unable to connect to mock server
        MockServerError: If mock server returns error
    """
```

**Example Usage:**

```python
# Update endpoint response
await client.manage_mock_data(
    server_url="http://localhost:8000",
    operation="update_response",
    endpoint_path="/users/123",
    response_data={"id": 123, "name": "John Doe", "status": "active"}
)

# Create scenario
await client.manage_mock_data(
    server_url="http://localhost:8000",
    operation="create_scenario",
    scenario_name="user_testing",
    scenario_config={
        "/users/123": {"id": 123, "name": "Test User"},
        "/users/456": {"id": 456, "name": "Another User"}
    }
)

# Switch to scenario
await client.manage_mock_data(
    server_url="http://localhost:8000",
    operation="switch_scenario",
    scenario_name="user_testing"
)

# List available scenarios
scenarios = await client.manage_mock_data(
    server_url="http://localhost:8000",
    operation="list_scenarios"
)
```

#### query_mock_logs()

Query and analyze request logs from mock servers.

```python
async def query_mock_logs(
    self,
    server_url: str,
    limit: int = 100,
    offset: int = 0,
    method: Optional[str] = None,
    path_pattern: Optional[str] = None,
    time_from: Optional[str] = None,
    time_to: Optional[str] = None,
    include_admin: bool = False,
    analyze: bool = True
) -> Dict[str, Any]:
    """
    Query and analyze mock server request logs.
    
    Args:
        server_url: URL of the mock server
        limit: Maximum number of logs to return
        offset: Number of logs to skip
        method: Filter by HTTP method
        path_pattern: Filter by path pattern (regex)
        time_from: Start time filter (ISO format)
        time_to: End time filter (ISO format)
        include_admin: Include admin endpoint requests
        analyze: Include analysis in response
        
    Returns:
        Dict containing logs and optional analysis
        
    Raises:
        ValueError: If invalid parameters
        ConnectionError: If unable to connect to mock server
    """
```

**Example Usage:**

```python
# Get recent logs with analysis
logs = await client.query_mock_logs(
    server_url="http://localhost:8000",
    limit=50,
    analyze=True
)

# Filter logs by method and path
api_logs = await client.query_mock_logs(
    server_url="http://localhost:8000",
    method="POST",
    path_pattern="/api/.*",
    limit=100
)

# Get logs for specific time range
time_filtered_logs = await client.query_mock_logs(
    server_url="http://localhost:8000",
    time_from="2024-01-01T00:00:00Z",
    time_to="2024-01-02T00:00:00Z"
)
```

#### discover_mock_servers()

Discover running MockLoop servers and generated configurations.

```python
async def discover_mock_servers(
    self,
    ports: Optional[List[int]] = None,
    check_health: bool = True,
    include_generated: bool = True
) -> Dict[str, Any]:
    """
    Discover running MockLoop servers.
    
    Args:
        ports: List of ports to check (default: common ports)
        check_health: Verify server health
        include_generated: Include generated mock configurations
        
    Returns:
        Dict containing discovered servers and configurations
        
    Raises:
        DiscoveryError: If discovery process fails
    """
```

**Example Usage:**

```python
# Discover all running servers
servers = await client.discover_mock_servers()

# Check specific ports
servers = await client.discover_mock_servers(
    ports=[8000, 8001, 8002],
    check_health=True
)

# Quick discovery without health checks
servers = await client.discover_mock_servers(
    check_health=False,
    include_generated=False
)
```

## MockServerGenerator

Core class for generating mock servers from API specifications.

### Class Definition

```python
class MockServerGenerator:
    """
    Generates FastAPI mock servers from OpenAPI specifications.
    
    Handles parsing of API specifications, code generation,
    and server configuration.
    """
    
    def __init__(self, config: Optional[GeneratorConfig] = None):
        """
        Initialize mock server generator.
        
        Args:
            config: Generator configuration options
        """
```

### Methods

#### generate()

Generate a complete mock server from specification.

```python
async def generate(
    self,
    spec_source: str,
    output_directory: str,
    options: GenerationOptions
) -> GenerationResult:
    """
    Generate mock server from API specification.
    
    Args:
        spec_source: URL or path to API specification
        output_directory: Directory for generated files
        options: Generation options and configuration
        
    Returns:
        GenerationResult with details about generated server
        
    Raises:
        SpecificationError: If specification is invalid
        GenerationError: If generation fails
    """
```

#### parse_specification()

Parse and validate API specification.

```python
def parse_specification(self, spec_source: str) -> ParsedSpecification:
    """
    Parse API specification from source.
    
    Args:
        spec_source: URL or file path to specification
        
    Returns:
        ParsedSpecification object
        
    Raises:
        SpecificationError: If specification is invalid or cannot be parsed
    """
```

#### generate_routes()

Generate FastAPI routes from parsed specification.

```python
def generate_routes(
    self,
    parsed_spec: ParsedSpecification,
    options: GenerationOptions
) -> List[RouteDefinition]:
    """
    Generate route definitions from parsed specification.
    
    Args:
        parsed_spec: Parsed API specification
        options: Generation options
        
    Returns:
        List of route definitions
    """
```

## MockServerManager

Manages running mock servers and their lifecycle.

### Class Definition

```python
class MockServerManager:
    """
    Manages mock server instances and their lifecycle.
    
    Provides methods for starting, stopping, and monitoring
    mock servers.
    """
    
    def __init__(self):
        """Initialize mock server manager."""
```

### Methods

#### start_server()

Start a mock server instance.

```python
async def start_server(
    self,
    server_config: ServerConfig,
    port: Optional[int] = None
) -> ServerInstance:
    """
    Start a mock server instance.
    
    Args:
        server_config: Server configuration
        port: Port to run server on (auto-assigned if None)
        
    Returns:
        ServerInstance representing the running server
        
    Raises:
        ServerStartError: If server fails to start
        PortInUseError: If specified port is already in use
    """
```

#### stop_server()

Stop a running mock server.

```python
async def stop_server(self, server_id: str) -> bool:
    """
    Stop a running mock server.
    
    Args:
        server_id: ID of server to stop
        
    Returns:
        True if server was stopped successfully
        
    Raises:
        ServerNotFoundError: If server ID not found
    """
```

#### list_servers()

List all managed server instances.

```python
def list_servers(self) -> List[ServerInstance]:
    """
    List all managed server instances.
    
    Returns:
        List of ServerInstance objects
    """
```

## Data Models

### GenerationOptions

Configuration options for mock server generation.

```python
@dataclass
class GenerationOptions:
    """Options for mock server generation."""
    
    auth_enabled: bool = True
    webhooks_enabled: bool = True
    admin_ui_enabled: bool = True
    storage_enabled: bool = True
    cors_enabled: bool = True
    rate_limiting_enabled: bool = False
    custom_middleware: List[str] = field(default_factory=list)
    response_delay_ms: int = 0
    error_rate_percent: float = 0.0
```

### ServerConfig

Configuration for a mock server instance.

```python
@dataclass
class ServerConfig:
    """Configuration for mock server instance."""
    
    name: str
    spec_path: str
    port: Optional[int] = None
    host: str = "localhost"
    options: GenerationOptions = field(default_factory=GenerationOptions)
    environment: Dict[str, str] = field(default_factory=dict)
```

### ServerInstance

Represents a running mock server instance.

```python
@dataclass
class ServerInstance:
    """Represents a running mock server instance."""
    
    id: str
    name: str
    config: ServerConfig
    port: int
    pid: Optional[int] = None
    status: ServerStatus = ServerStatus.STARTING
    start_time: Optional[datetime] = None
    health_check_url: Optional[str] = None
```

### ParsedSpecification

Represents a parsed API specification.

```python
@dataclass
class ParsedSpecification:
    """Parsed API specification."""
    
    title: str
    version: str
    description: Optional[str] = None
    servers: List[ServerInfo] = field(default_factory=list)
    paths: Dict[str, PathItem] = field(default_factory=dict)
    components: Optional[Components] = None
    security: List[SecurityRequirement] = field(default_factory=list)
    tags: List[Tag] = field(default_factory=list)
```

### RouteDefinition

Defines a generated API route.

```python
@dataclass
class RouteDefinition:
    """Definition of a generated API route."""
    
    path: str
    method: str
    operation_id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: List[Parameter] = field(default_factory=list)
    request_body: Optional[RequestBody] = None
    responses: Dict[str, Response] = field(default_factory=dict)
    security: List[SecurityRequirement] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
```

## Enumerations

### ServerStatus

Status of a mock server instance.

```python
class ServerStatus(Enum):
    """Mock server status."""
    
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
```

### LogLevel

Logging levels for mock servers.

```python
class LogLevel(Enum):
    """Logging levels."""
    
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
```

## Exception Classes

### MockLoopError

Base exception class for MockLoop errors.

```python
class MockLoopError(Exception):
    """Base exception for MockLoop errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code
```

### SpecificationError

Exception for API specification related errors.

```python
class SpecificationError(MockLoopError):
    """Exception for API specification errors."""
    
    def __init__(self, message: str, spec_path: Optional[str] = None):
        super().__init__(message)
        self.spec_path = spec_path
```

### GenerationError

Exception for mock server generation errors.

```python
class GenerationError(MockLoopError):
    """Exception for mock server generation errors."""
    
    def __init__(self, message: str, stage: Optional[str] = None):
        super().__init__(message)
        self.stage = stage
```

### ServerError

Exception for mock server runtime errors.

```python
class ServerError(MockLoopError):
    """Exception for mock server runtime errors."""
    
    def __init__(self, message: str, server_id: Optional[str] = None):
        super().__init__(message)
        self.server_id = server_id
```

## Usage Examples

### Complete Workflow Example

```python
import asyncio
from mockloop_mcp import MockLoopClient, MockServerGenerator, GenerationOptions

async def complete_workflow_example():
    """Example of complete MockLoop workflow."""
    
    # Initialize client
    client = MockLoopClient()
    
    # Generate mock server
    generation_result = await client.generate_mock_api(
        spec_url_or_path="./petstore-api.yaml",
        output_dir_name="petstore_mock",
        auth_enabled=True,
        webhooks_enabled=True,
        admin_ui_enabled=True,
        storage_enabled=True
    )
    
    print(f"Generated server: {generation_result}")
    
    # Wait for server to start
    await asyncio.sleep(2)
    
    # Configure test scenario
    await client.manage_mock_data(
        server_url="http://localhost:8000",
        operation="create_scenario",
        scenario_name="testing",
        scenario_config={
            "/pets": {
                "pets": [
                    {"id": 1, "name": "Fluffy", "status": "available"},
                    {"id": 2, "name": "Buddy", "status": "pending"}
                ]
            },
            "/pets/1": {
                "id": 1,
                "name": "Fluffy",
                "status": "available",
                "category": {"id": 1, "name": "cats"}
            }
        }
    )
    
    # Switch to test scenario
    await client.manage_mock_data(
        server_url="http://localhost:8000",
        operation="switch_scenario",
        scenario_name="testing"
    )
    
    # Make some test requests (using httpx or requests)
    import httpx
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get("http://localhost:8000/pets")
        print(f"Pets response: {response.json()}")
        
        response = await http_client.get("http://localhost:8000/pets/1")
        print(f"Pet 1 response: {response.json()}")
    
    # Query logs and analyze
    logs = await client.query_mock_logs(
        server_url="http://localhost:8000",
        analyze=True
    )
    
    print(f"Total requests: {logs['analysis']['total_requests']}")
    print(f"Average response time: {logs['analysis']['avg_response_time_ms']}ms")
    
    # Discover all running servers
    servers = await client.discover_mock_servers()
    print(f"Running servers: {servers}")

if __name__ == "__main__":
    asyncio.run(complete_workflow_example())
```

### Custom Generator Example

```python
from mockloop_mcp import MockServerGenerator, GenerationOptions

async def custom_generator_example():
    """Example using MockServerGenerator directly."""
    
    # Create custom generation options
    options = GenerationOptions(
        auth_enabled=False,
        webhooks_enabled=True,
        admin_ui_enabled=True,
        storage_enabled=False,
        cors_enabled=True,
        response_delay_ms=100,  # Add 100ms delay to all responses
        error_rate_percent=5.0  # 5% error rate for testing
    )
    
    # Initialize generator
    generator = MockServerGenerator()
    
    # Generate mock server
    result = await generator.generate(
        spec_source="https://api.example.com/openapi.json",
        output_directory="./custom_mock",
        options=options
    )
    
    print(f"Generated {len(result.routes)} routes")
    print(f"Server files created in: {result.output_directory}")

if __name__ == "__main__":
    asyncio.run(custom_generator_example())
```

## Best Practices

### Error Handling

Always handle exceptions appropriately:

```python
from mockloop_mcp import MockLoopClient, SpecificationError, GenerationError

async def robust_mock_generation():
    client = MockLoopClient()
    
    try:
        result = await client.generate_mock_api(
            spec_url_or_path="./api-spec.yaml"
        )
        print("Mock server generated successfully")
        
    except SpecificationError as e:
        print(f"Invalid API specification: {e}")
        if e.spec_path:
            print(f"Specification path: {e.spec_path}")
            
    except GenerationError as e:
        print(f"Generation failed: {e}")
        if e.stage:
            print(f"Failed at stage: {e.stage}")
            
    except Exception as e:
        print(f"Unexpected error: {e}")
```

### Resource Management

Use context managers for proper resource cleanup:

```python
from mockloop_mcp import MockServerManager

async def managed_server_example():
    manager = MockServerManager()
    
    try:
        # Start server
        server = await manager.start_server(server_config)
        
        # Use server
        await perform_tests(server)
        
    finally:
        # Ensure server is stopped
        if server:
            await manager.stop_server(server.id)
```

### Configuration Management

Use configuration objects for complex setups:

```python
from mockloop_mcp import ServerConfig, GenerationOptions

def create_test_config():
    options = GenerationOptions(
        auth_enabled=False,
        storage_enabled=False,
        response_delay_ms=0
    )
    
    return ServerConfig(
        name="test_server",
        spec_path="./test-api.yaml",
        port=8080,
        options=options,
        environment={"ENV": "test", "DEBUG": "true"}
    )
```

## See Also

- **[Configuration Options](configuration.md)**: Detailed configuration reference
- **[Database Schema](database-schema.md)**: Database structure documentation
- **[Admin API](admin-api.md)**: Admin API endpoints reference
- **[MCP Tools](mcp-tools.md)**: MCP tool integration guide