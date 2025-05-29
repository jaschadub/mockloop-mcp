import argparse
import sys
from pathlib import Path
from typing import Optional, TypedDict, Any # Added Any back

# Handle imports for different execution contexts
# This allows the script to be run directly (e.g., by 'mcp dev')
# or imported as part of a package.
if __package__ is None or __package__ == '':
    # Likely executed by 'mcp dev' or as a standalone script.
    # Assumes 'src/mockloop_mcp/' is in sys.path.
    from parser import load_api_specification, APIParsingError
    from generator import generate_mock_api, APIGenerationError
else:
    # Imported as part of the 'src.mockloop_mcp' package.
    from .parser import load_api_specification, APIParsingError
    from .generator import generate_mock_api, APIGenerationError

# Import FastMCP and Context from the MCP SDK
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context # For type hinting if needed in tools

# Define input and output structures for the tool
# These can be Pydantic models for more robust validation if the SDK supports it,
# or TypedDicts as used here.
class GenerateMockApiInput(TypedDict):
    spec_url_or_path: str
    output_dir_name: Optional[str]
    # Example: Add more parameters like target_port: Optional[int]

class GenerateMockApiOutput(TypedDict):
    generated_mock_path: str
    message: str
    status: str # "success" or "error"

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
    output_dir_name: Optional[str] = None,
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
                return value.lower() in ('true', 'yes', '1', 'on')
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
        print(f"Tool: Loading API specification from: {spec_url_or_path}") # Server-side log
        
        # Print received boolean flags for debugging
        print(f"Tool: Hardcoded auth_enabled: {auth_enabled_debug} (type: {type(auth_enabled_debug)}) (original was: {auth_enabled})")
        print(f"Tool: Hardcoded webhooks_enabled: {webhooks_enabled_debug} (type: {type(webhooks_enabled_debug)}) (original was: {webhooks_enabled})")
        print(f"Tool: Hardcoded admin_ui_enabled: {admin_ui_enabled_debug} (type: {type(admin_ui_enabled_debug)}) (original was: {admin_ui_enabled})")
        print(f"Tool: Hardcoded storage_enabled: {storage_enabled_debug} (type: {type(storage_enabled_debug)}) (original was: {storage_enabled})")
        
        parsed_spec = load_api_specification(spec_url_or_path)
        
        # await ctx.info(f"Generating mock API server...")
        print(f"Tool: Generating mock API server...")
        if output_dir_name:
            # await ctx.info(f"Using custom output directory name: {output_dir_name}")
            print(f"Tool: Using custom output directory name: {output_dir_name}")
        
        generated_path = generate_mock_api(
            spec_data=parsed_spec,
            mock_server_name=output_dir_name,
            auth_enabled=auth_enabled_debug, # Pass debug hardcoded True
            webhooks_enabled=webhooks_enabled_debug, # Pass debug hardcoded True
            admin_ui_enabled=admin_ui_enabled_debug, # Pass debug hardcoded True
            storage_enabled=storage_enabled_debug # Pass debug hardcoded True
            # output_base_dir can be configured if needed, defaults to "generated_mocks"
        )
        
        resolved_path = str(generated_path.resolve())
        # await ctx.info(f"Mock API server generated successfully at: {resolved_path}")
        print(f"Tool: Mock API server generated successfully at: {resolved_path}")
        
        return {
            "generated_mock_path": resolved_path,
            "message": f"Mock API server generated successfully at {resolved_path}. "
                       f"Navigate to this directory and use 'docker-compose up --build' to run it.",
            "status": "success"
        }

    except APIParsingError as e:
        print(f"Tool Error: Error parsing API specification: {e}")
        # await ctx.error(f"Error parsing API specification: {e}")
        return {
            "generated_mock_path": "",
            "message": f"Error parsing API specification: {e}",
            "status": "error"
        }
    except APIGenerationError as e:
        print(f"Tool Error: Error generating mock API: {e}")
        # await ctx.error(f"Error generating mock API: {e}")
        return {
            "generated_mock_path": "",
            "message": f"Error generating mock API: {e}",
            "status": "error"
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Tool Error: An unexpected error occurred: {error_details}")
        # await ctx.error(f"An unexpected error occurred: {e}\n{error_details}")
        return {
            "generated_mock_path": "",
            "message": f"An unexpected error occurred: {e}",
            "status": "error"
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
    print("\n--- CLI Tool Execution Result ---")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    if result['generated_mock_path']:
        print(f"Generated Path: {result['generated_mock_path']}")
    
    if result['status'] == "error":
        sys.exit(1)

def main_cli():
    parser = argparse.ArgumentParser(description="MockLoop API Mock Generator (CLI Test Utility for Tool Logic)")
    parser.add_argument("spec_source", help="URL or local file path to the API specification.")
    parser.add_argument("-o", "--output-name", help="Optional name for the generated mock server directory.", default=None)
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
        print("Running in CLI test mode...")
        # Remove --cli from sys.argv so argparse doesn't see it
        sys.argv.remove("--cli")
        main_cli()
    else:
        # Start the MCP server
        print("Starting MockLoop MCP Server...")
        server.run()


# To make `python src/mockloop_mcp/main.py` start the server as per SDK docs:
# (Comment out the main_cli() call above if you uncomment this)
#
# if __name__ == "__main__":
#     print("Starting MockLoop MCP Server...")
#     mcp_server.run()
