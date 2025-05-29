import sys
import json
import requests
from pathlib import Path
from src.mockloop_mcp.generator import generate_mock_api

# Function to load API spec from URL or file
def load_api_specification(spec_url_or_path):
    if spec_url_or_path.startswith(('http://', 'https://')):
        print(f"Loading specification from URL: {spec_url_or_path}")
        response = requests.get(spec_url_or_path)
        response.raise_for_status()
        return response.json()
    else:
        print(f"Loading specification from file: {spec_url_or_path}")
        with open(spec_url_or_path, 'r') as f:
            return json.load(f)

# Main function
def main():
    spec_url = "https://petstore3.swagger.io/api/v3/openapi.json"
    output_name = "petstore_new_test"
    
    try:
        # Load the API specification
        spec_data = load_api_specification(spec_url)
        
        # Generate the mock API
        output_path = generate_mock_api(
            spec_data=spec_data,
            mock_server_name=output_name,
            auth_enabled=True,
            webhooks_enabled=True,
            admin_ui_enabled=True,
            storage_enabled=True
        )
        
        print(f"Mock API generated successfully at: {output_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
