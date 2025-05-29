#!/usr/bin/env python3
import sys
from pathlib import Path

# Add the current directory to path to find the modules
sys.path.append('.')

# Import the necessary functions directly
from src.mockloop_mcp.parser import load_api_specification
from src.mockloop_mcp.generator import generate_mock_api

def main():
    spec_url_or_path = "https://petstore3.swagger.io/api/v3/openapi.json"
    output_dir_name = "petstore_fixed_final_v3"
    
    # Load the API specification
    print(f"Loading API specification from: {spec_url_or_path}")
    parsed_spec = load_api_specification(spec_url_or_path)
    
    # Generate the mock API
    print(f"Generating mock API server with output name: {output_dir_name}")
    generated_path = generate_mock_api(
        spec_data=parsed_spec,
        mock_server_name=output_dir_name,
        auth_enabled=True,
        webhooks_enabled=True,
        admin_ui_enabled=True,
        storage_enabled=True
    )
    
    resolved_path = str(generated_path.resolve())
    print(f"Mock API server generated successfully at: {resolved_path}")
    print(f"Navigate to this directory and use 'docker-compose up --build' to run it.")

if __name__ == "__main__":
    main()
