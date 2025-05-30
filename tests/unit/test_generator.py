import json
from src.mockloop_mcp.parser import load_api_specification
from src.mockloop_mcp.generator import generate_mock_api

def test_mock_api_generation():
    print("Loading API specification from test_spec.json...")
    spec_data = load_api_specification("tests/fixtures/test_spec.json")
    
    print("Generating mock API server...")
    output_dir = generate_mock_api(
        spec_data=spec_data,
        mock_server_name="test_api_mock"
    )
    
    print(f"Successfully generated mock API at: {output_dir.resolve()}")
    print("Files created:")
    for item in output_dir.iterdir():
        print(f"  - {item.name}")
    
    print("\nTo run the mock server (example):")
    print(f"cd {output_dir.resolve()}")
    print("docker-compose up --build")

if __name__ == "__main__":
    test_mock_api_generation()
