import json
from src.mockloop_mcp.parser import load_api_specification
from src.mockloop_mcp.generator import generate_mock_api

def test_auth_mock_api_generation():
    print("Loading API specification from test_spec.json...")
    spec_data = load_api_specification("test_spec.json")
    
    print("Generating mock API server with authentication...")
    output_dir = generate_mock_api(
        spec_data=spec_data,
        mock_server_name="test_api_auth_mock",
        auth_enabled=True
    )
    
    print(f"Successfully generated mock API with authentication at: {output_dir.resolve()}")
    print("Files created:")
    for item in output_dir.iterdir():
        print(f"  - {item.name}")
    
    print("\nTo run the mock server (example):")
    print(f"cd {output_dir.resolve()}")
    print("docker-compose up --build")
    
    print("\nAuthentication information:")
    print("  - API Key: Check the auth_middleware.py file for MOCK_API_KEY")
    print("  - JWT Token URL: /token")
    print("  - Available users: admin, user, guest (any password works)")

if __name__ == "__main__":
    test_auth_mock_api_generation()
