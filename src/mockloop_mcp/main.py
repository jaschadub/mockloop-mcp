import argparse
import logging
import sys
from typing import Any, TypedDict

# Configure logger for this module
logger = logging.getLogger(__name__)

# Handle imports for different execution contexts
# This allows the script to be run directly (e.g., by 'mcp dev')
# or imported as part of a package.
if __package__ is None or __package__ == "":
    # Likely executed by 'mcp dev' or as a standalone script.
    # Assumes 'src/mockloop_mcp/' is in sys.path.
    from generator import APIGenerationError, generate_mock_api
    from log_analyzer import LogAnalyzer
    from mock_server_manager import MockServerManager
    from parser import APIParsingError, load_api_specification
else:
    # Imported as part of the 'src.mockloop_mcp' package.
    from .generator import APIGenerationError, generate_mock_api
    from .log_analyzer import LogAnalyzer
    from .mock_server_manager import MockServerManager
    from .parser import APIParsingError, load_api_specification

# Import FastMCP and Context from the MCP SDK
from mcp.server.fastmcp import (
    FastMCP,
)


# Define input and output structures for the tool
# These can be Pydantic models for more robust validation if the SDK supports it,
# or TypedDicts as used here.
class GenerateMockApiInput(TypedDict):
    spec_url_or_path: str
    output_dir_name: str | None
    # Example: Add more parameters like target_port: Optional[int]


class GenerateMockApiOutput(TypedDict):
    generated_mock_path: str
    message: str
    status: str  # "success" or "error"


# New TypedDict definitions for enhanced tools
class QueryMockLogsInput(TypedDict):
    server_url: str
    limit: int | None
    offset: int | None
    method: str | None
    path_pattern: str | None
    time_from: str | None
    time_to: str | None
    include_admin: bool | None
    analyze: bool | None


class QueryMockLogsOutput(TypedDict):
    status: str
    logs: list[dict[str, Any]]
    total_count: int
    analysis: dict[str, Any] | None
    message: str


class DiscoverMockServersInput(TypedDict):
    ports: list[int] | None
    check_health: bool | None
    include_generated: bool | None


class DiscoverMockServersOutput(TypedDict):
    status: str
    discovered_servers: list[dict[str, Any]]
    generated_mocks: list[dict[str, Any]]
    total_running: int
    total_generated: int
    message: str


class ManageMockDataInput(TypedDict):
    server_url: str
    operation: (
        str  # "update_response", "create_scenario", "switch_scenario", "list_scenarios"
    )
    endpoint_path: str | None
    response_data: dict[str, Any] | None
    scenario_name: str | None
    scenario_config: dict[str, Any] | None


class ManageMockDataOutput(TypedDict):
    status: str
    operation: str
    result: dict[str, Any]
    server_url: str
    message: str
    performance_metrics: dict[str, Any] | None


# Create an MCP server instance
# The name "MockLoop" will be visible in MCP clients like Claude Desktop.
server = FastMCP(
    name="MockLoop",
    description="Generates and manages mock API servers from specifications.",
    # dependencies=["fastapi", "uvicorn", "Jinja2", "PyYAML", "requests"] # Dependencies of the MCP server itself
)


@server.tool(
    name="generate_mock_api",
    description="Generates a FastAPI mock server from an API specification (e.g., OpenAPI). "
    "The mock server includes request/response logging and Docker support.",
    # input_schema=GenerateMockApiInput, # FastMCP infers from type hints
    # output_schema=GenerateMockApiOutput, # FastMCP infers from return type hint
)
async def generate_mock_api_tool(
    spec_url_or_path: str,
    output_dir_name: str | None = None,
    auth_enabled: bool = True,
    webhooks_enabled: bool = True,
    admin_ui_enabled: bool = True,
    storage_enabled: bool = True,
    # ctx: Context # MCP Context, can be added if tool needs to report progress, etc.
) -> GenerateMockApiOutput:
    """
    MCP Tool to generate a mock API server.

    Args:
        spec_url_or_path: URL or local file path to the API specification.
        output_dir_name: Optional name for the generated mock server directory.
                         If None, a name is derived from the API title and version.
        # ctx: The MCP Context object, automatically injected if type-hinted.
    """
    try:
        # Helper to robustly convert to boolean
        def _tool_to_bool(value: Any) -> bool:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ("true", "yes", "1", "on")
            if isinstance(value, int):
                return value != 0
            return bool(value)

        # Explicitly convert boolean flags at the tool entry point
        # auth_enabled_bool = _tool_to_bool(auth_enabled)
        # webhooks_enabled_bool = _tool_to_bool(webhooks_enabled)
        # admin_ui_enabled_bool = _tool_to_bool(admin_ui_enabled)
        # storage_enabled_bool = _tool_to_bool(storage_enabled)

        # DEBUG: Hardcode to True to test propagation to generator.py
        auth_enabled_debug = True
        webhooks_enabled_debug = True
        admin_ui_enabled_debug = True
        storage_enabled_debug = True

        # If using ctx for logging to MCP client:
        # await ctx.info(f"Loading API specification from: {spec_url_or_path}")

        # Print received boolean flags for debugging

        parsed_spec = load_api_specification(spec_url_or_path)

        # await ctx.info(f"Generating mock API server...")
        if output_dir_name:
            # await ctx.info(f"Using custom output directory name: {output_dir_name}")
            pass

        generated_path = generate_mock_api(
            spec_data=parsed_spec,
            mock_server_name=output_dir_name,
            auth_enabled=auth_enabled_debug,  # Pass debug hardcoded True
            webhooks_enabled=webhooks_enabled_debug,  # Pass debug hardcoded True
            admin_ui_enabled=admin_ui_enabled_debug,  # Pass debug hardcoded True
            storage_enabled=storage_enabled_debug,  # Pass debug hardcoded True
            # output_base_dir can be configured if needed, defaults to "generated_mocks"
        )

        resolved_path = str(generated_path.resolve())
        # await ctx.info(f"Mock API server generated successfully at: {resolved_path}")

        return {
            "generated_mock_path": resolved_path,
            "message": f"Mock API server generated successfully at {resolved_path}. "
            f"Navigate to this directory and use 'docker-compose up --build' to run it.",
            "status": "success",
        }

    except APIParsingError as e:
        # await ctx.error(f"Error parsing API specification: {e}")
        return {
            "generated_mock_path": "",
            "message": f"Error parsing API specification: {e}",
            "status": "error",
        }
    except APIGenerationError as e:
        # await ctx.error(f"Error generating mock API: {e}")
        return {
            "generated_mock_path": "",
            "message": f"Error generating mock API: {e}",
            "status": "error",
        }
    except Exception as e:
        import traceback

        traceback.format_exc()
        # await ctx.error(f"An unexpected error occurred: {e}\n{error_details}")
        return {
            "generated_mock_path": "",
            "message": f"An unexpected error occurred: {e}",
            "status": "error",
        }


@server.tool(
    name="query_mock_logs",
    description="Query and analyze request logs from a running MockLoop server. "
    "Supports filtering by method, path, time range, and provides optional analysis.",
)
async def query_mock_logs_tool(
    server_url: str,
    limit: int = 100,
    offset: int = 0,
    method: str | None = None,
    path_pattern: str | None = None,
    time_from: str | None = None,
    time_to: str | None = None,
    include_admin: bool = False,
    analyze: bool = True,
) -> QueryMockLogsOutput:
    """
    Query request logs from a MockLoop server with optional analysis.

    Args:
        server_url: URL of the mock server (e.g., "http://localhost:8000")
        limit: Maximum number of logs to return (default: 100)
        offset: Number of logs to skip for pagination (default: 0)
        method: Filter by HTTP method (e.g., "GET", "POST")
        path_pattern: Regex pattern to filter paths
        time_from: Start time filter (ISO format)
        time_to: End time filter (ISO format)
        include_admin: Include admin requests in results
        analyze: Perform analysis on the logs
    """
    try:
        # Initialize the mock server manager
        manager = MockServerManager()

        # Query logs from the server
        log_result = await manager.query_server_logs(
            server_url=server_url,
            limit=limit,
            offset=offset,
            method=method,
            path=path_pattern,
            include_admin=include_admin,
        )

        if log_result.get("status") != "success":
            return {
                "status": "error",
                "logs": [],
                "total_count": 0,
                "analysis": None,
                "message": f"Failed to query logs: {log_result.get('error', 'Unknown error')}",
            }

        logs = log_result.get("logs", [])

        # Apply additional filtering if needed
        if time_from or time_to or path_pattern:
            analyzer = LogAnalyzer()
            logs = analyzer.filter_logs(
                logs,
                method=method,
                path_pattern=path_pattern,
                time_from=time_from,
                time_to=time_to,
                include_admin=include_admin,
            )

        analysis = None
        if analyze and logs:
            analyzer = LogAnalyzer()
            analysis = analyzer.analyze_logs(logs)

        return {
            "status": "success",
            "logs": logs,
            "total_count": len(logs),
            "analysis": analysis,
            "message": f"Successfully retrieved {len(logs)} log entries from {server_url}",
        }

    except Exception as e:
        import traceback

        traceback.format_exc()
        return {
            "status": "error",
            "logs": [],
            "total_count": 0,
            "analysis": None,
            "message": f"Error querying logs: {e!s}",
        }


@server.tool(
    name="discover_mock_servers",
    description="Discover running MockLoop servers and generated mock configurations. "
    "Scans common ports and matches with generated mocks.",
)
async def discover_mock_servers_tool(
    ports: list[int] | None = None,
    check_health: bool = True,
    include_generated: bool = True,
) -> DiscoverMockServersOutput:
    """
    Discover running mock servers and generated mock configurations.

    Args:
        ports: List of ports to scan (default: common ports 8000-8005, 3000-3001, 5000-5001)
        check_health: Perform health checks on discovered servers
        include_generated: Include information about generated but not running mocks
    """
    try:
        # Initialize the mock server manager
        manager = MockServerManager()

        if include_generated:
            # Perform comprehensive discovery
            discovery_result = await manager.comprehensive_discovery()

            return {
                "status": "success",
                "discovered_servers": discovery_result.get("matched_servers", [])
                + discovery_result.get("unmatched_running_servers", []),
                "generated_mocks": discovery_result.get("not_running_mocks", []),
                "total_running": discovery_result.get("total_running", 0),
                "total_generated": discovery_result.get("total_generated", 0),
                "message": f"Discovered {discovery_result.get('total_running', 0)} running servers "
                f"and {discovery_result.get('total_generated', 0)} generated mocks",
            }
        else:
            # Just discover running servers
            running_servers = await manager.discover_running_servers(
                ports, check_health
            )

            return {
                "status": "success",
                "discovered_servers": running_servers,
                "generated_mocks": [],
                "total_running": len(running_servers),
                "total_generated": 0,
                "message": f"Discovered {len(running_servers)} running servers",
            }

    except Exception as e:
        import traceback

        traceback.format_exc()
        return {
            "status": "error",
            "discovered_servers": [],
            "generated_mocks": [],
            "total_running": 0,
            "total_generated": 0,
            "message": f"Error discovering servers: {e!s}",
        }


@server.tool(
    name="manage_mock_data",
    description="Manage dynamic response data and scenarios for MockLoop servers. "
    "Supports updating responses, creating scenarios, switching scenarios, and listing scenarios.",
)
async def manage_mock_data_tool(
    server_url: str,
    operation: str,
    endpoint_path: str | None = None,
    response_data: dict[str, Any] | None = None,
    scenario_name: str | None = None,
    scenario_config: dict[str, Any] | None = None,
) -> ManageMockDataOutput:
    """
    Manage mock data and scenarios for dynamic response management.

    Args:
        server_url: URL of the mock server (e.g., "http://localhost:8000")
        operation: Operation to perform ("update_response", "create_scenario", "switch_scenario", "list_scenarios")
        endpoint_path: Specific endpoint to modify (required for update_response)
        response_data: New response data for updates (required for update_response)
        scenario_name: Scenario identifier (required for create_scenario, switch_scenario)
        scenario_config: Complete scenario configuration (required for create_scenario)
    """
    import time

    # Handle imports for different execution contexts
    if __package__ is None or __package__ == "":
        from utils.http_client import MockServerClient, check_server_connectivity
    else:
        from .utils.http_client import MockServerClient, check_server_connectivity

    start_time = time.time()

    try:
        # Validate server accessibility first
        connectivity_result = await check_server_connectivity(server_url)
        if connectivity_result.get("status") != "healthy":
            return {
                "status": "error",
                "operation": operation,
                "result": {},
                "server_url": server_url,
                "message": f"Server not accessible: {connectivity_result.get('error', 'Unknown error')}",
                "performance_metrics": None,
            }

        # Initialize the mock server manager for server validation
        manager = MockServerManager()

        # Validate that this is a MockLoop server
        server_status = await manager.get_server_status(server_url)
        if not server_status.get("is_mockloop_server", False):
            return {
                "status": "error",
                "operation": operation,
                "result": {},
                "server_url": server_url,
                "message": "Target server is not a MockLoop server or does not support admin operations",
                "performance_metrics": None,
            }

        # Initialize HTTP client
        client = MockServerClient(server_url)

        # Perform the requested operation
        if operation == "update_response":
            if not endpoint_path or response_data is None:
                return {
                    "status": "error",
                    "operation": operation,
                    "result": {},
                    "server_url": server_url,
                    "message": "update_response operation requires endpoint_path and response_data parameters",
                    "performance_metrics": None,
                }

            # Get current response for before/after comparison
            before_state = {}
            try:
                # Try to get current endpoint info (this would need to be implemented in the server)
                debug_info = await client.get_debug_info()
                if debug_info.get("status") == "success":
                    before_state = (
                        debug_info.get("debug_info", {})
                        .get("endpoints", {})
                        .get(endpoint_path, {})
                    )
            except Exception as e:
                logger.debug(
                    f"Failed to get before state for endpoint {endpoint_path}: {e}"
                )
                # Continue without before state if not available

            result = await client.update_response(endpoint_path, response_data)

            if result.get("status") == "success":
                # Get after state
                after_state = {}
                try:
                    debug_info = await client.get_debug_info()
                    if debug_info.get("status") == "success":
                        after_state = (
                            debug_info.get("debug_info", {})
                            .get("endpoints", {})
                            .get(endpoint_path, {})
                        )
                except Exception as e:
                    logger.debug(
                        f"Failed to get after state for endpoint {endpoint_path}: {e}"
                    )

                result["before_state"] = before_state
                result["after_state"] = after_state

                message = f"Successfully updated response for {endpoint_path}"
            else:
                message = f"Failed to update response for {endpoint_path}: {result.get('error', 'Unknown error')}"

        elif operation == "create_scenario":
            if not scenario_name or not scenario_config:
                return {
                    "status": "error",
                    "operation": operation,
                    "result": {},
                    "server_url": server_url,
                    "message": "create_scenario operation requires scenario_name and scenario_config parameters",
                    "performance_metrics": None,
                }

            result = await client.create_scenario(scenario_name, scenario_config)

            if result.get("status") == "success":
                message = f"Successfully created scenario '{scenario_name}'"
            else:
                message = f"Failed to create scenario '{scenario_name}': {result.get('error', 'Unknown error')}"

        elif operation == "switch_scenario":
            if not scenario_name:
                return {
                    "status": "error",
                    "operation": operation,
                    "result": {},
                    "server_url": server_url,
                    "message": "switch_scenario operation requires scenario_name parameter",
                    "performance_metrics": None,
                }

            # Get current scenario before switching
            current_result = await client.get_current_scenario()
            before_scenario = (
                current_result.get("current_scenario", {})
                if current_result.get("status") == "success"
                else {}
            )

            result = await client.switch_scenario(scenario_name)

            if result.get("status") == "success":
                result["before_scenario"] = before_scenario
                message = f"Successfully switched to scenario '{scenario_name}'"
                if result.get("previous_scenario"):
                    message += f" (from '{result['previous_scenario']}')"
            else:
                message = f"Failed to switch to scenario '{scenario_name}': {result.get('error', 'Unknown error')}"

        elif operation == "list_scenarios":
            result = await client.list_scenarios()

            if result.get("status") == "success":
                scenarios = result.get("scenarios", [])
                # Get current scenario info
                current_result = await client.get_current_scenario()
                if current_result.get("status") == "success":
                    result["current_scenario"] = current_result.get("current_scenario")

                message = f"Successfully retrieved {len(scenarios)} scenarios"
            else:
                message = (
                    f"Failed to list scenarios: {result.get('error', 'Unknown error')}"
                )

        else:
            return {
                "status": "error",
                "operation": operation,
                "result": {},
                "server_url": server_url,
                "message": f"Unknown operation '{operation}'. Supported operations: update_response, create_scenario, switch_scenario, list_scenarios",
                "performance_metrics": None,
            }

        # Calculate performance metrics
        end_time = time.time()
        performance_metrics = {
            "operation_time_ms": round((end_time - start_time) * 1000, 2),
            "server_response_time": connectivity_result.get(
                "response_time_ms", "unknown"
            ),
            "timestamp": time.time(),
        }

        return {
            "status": result.get("status", "unknown"),
            "operation": operation,
            "result": result,
            "server_url": server_url,
            "message": message,
            "performance_metrics": performance_metrics,
        }

    except Exception as e:
        import traceback

        traceback.format_exc()

        end_time = time.time()
        performance_metrics = {
            "operation_time_ms": round((end_time - start_time) * 1000, 2),
            "error": True,
            "timestamp": time.time(),
        }

        return {
            "status": "error",
            "operation": operation,
            "result": {},
            "server_url": server_url,
            "message": f"Error managing mock data: {e!s}",
            "performance_metrics": performance_metrics,
        }


# --- CLI for local testing of the tool logic ---
async def run_tool_from_cli(args):
    """Helper to call the tool logic for CLI testing."""
    # This simulates how the MCP server would call the tool.
    # The actual MCP server handles the async nature and context injection.

    # Create a dummy context if your tool expects one and you want to test that part.
    # class DummyContext:
    #     async def info(self, msg): print(f"CTX.INFO: {msg}")
    #     async def error(self, msg): print(f"CTX.ERROR: {msg}")
    # dummy_ctx = DummyContext()

    result = await generate_mock_api_tool(
        spec_url_or_path=args.spec_source,
        output_dir_name=args.output_name,
        # ctx=dummy_ctx # if tool expects context
    )
    if result["generated_mock_path"]:
        pass

    if result["status"] == "error":
        sys.exit(1)


def main_cli():
    parser = argparse.ArgumentParser(
        description="MockLoop API Mock Generator (CLI Test Utility for Tool Logic)"
    )
    parser.add_argument(
        "spec_source", help="URL or local file path to the API specification."
    )
    parser.add_argument(
        "-o",
        "--output-name",
        help="Optional name for the generated mock server directory.",
        default=None,
    )
    # output_base_dir is handled by the generator.py, not passed to tool directly
    args = parser.parse_args()

    import asyncio

    asyncio.run(run_tool_from_cli(args))


# To run the MCP server:
# Use `mcp dev src/mockloop_mcp/main.py` or `mcp run src/mockloop_mcp/main.py`
# Or, if this file is intended to be run directly as `python src/mockloop_mcp/main.py`:
if __name__ == "__main__":
    # Check if --cli flag is passed, otherwise assume MCP server run
    if "--cli" in sys.argv:
        # Remove --cli from sys.argv so argparse doesn't see it
        sys.argv.remove("--cli")
        main_cli()
    else:
        # Start the MCP server
        server.run()


# To make `python src/mockloop_mcp/main.py` start the server as per SDK docs:
# (Comment out the main_cli() call above if you uncomment this)
#
# if __name__ == "__main__":
#     print("Starting MockLoop MCP Server...")
#     mcp_server.run()
