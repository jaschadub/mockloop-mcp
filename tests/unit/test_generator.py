from src.mockloop_mcp.generator import generate_mock_api
from src.mockloop_mcp.parser import load_api_specification


def test_mock_api_generation():
    spec_data = load_api_specification("tests/fixtures/test_spec.json")

    output_dir = generate_mock_api(
        spec_data=spec_data,
        mock_server_name="test_api_mock"
    )

    for _item in output_dir.iterdir():
        pass


if __name__ == "__main__":
    test_mock_api_generation()
