![MockLoop](logo.png "MockLoop")
# MCP Server (`mockloop-mcp`)

`mockloop-mcp` is a Model Context Protocol (MCP) server designed to generate and run mock API servers from API documentation (e.g., OpenAPI/Swagger specifications). This allows developers to quickly spin up mock backends for development, testing, and integration purposes.

## Features

*   **API Mock Generation:** Takes an API specification (URL or local file) and generates a runnable FastAPI mock server.
*   **Request/Response Logging:** Generated mock servers include middleware for comprehensive logging of requests and responses to `stdout`.
*   **Dockerized Mocks:** Generates a `Dockerfile` and `docker-compose.yml` for each mock API, allowing them to be easily run as Docker containers.
*   **Initial Support:** OpenAPI v2 (Swagger) and v3 (JSON, YAML).

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

### Using the `generate_mock_api` Tool

Once `mockloop-mcp` is running, you can use an MCP client to call its `generate_mock_api` tool.

**Tool Parameters (Example):**
*   `spec_url_or_path`: (string, required) URL or local file path to the API specification (e.g., `https://petstore3.swagger.io/api/v3/openapi.json` or `./my_api.yaml`).
*   `output_dir_name`: (string, optional) Name for the directory where the mock server code will be generated (e.g., `my_petstore_mock`). Defaults to a name derived from the API spec.

**Output:**
The tool will generate a new directory (e.g., `generated_mocks/my_petstore_mock/`) containing:
*   `main.py`: The FastAPI application.
*   `requirements_mock.txt`: Dependencies for the mock server.
*   `Dockerfile`: For building the mock server Docker image.
*   `docker-compose.yml`: For running the mock server with Docker Compose.

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

## Future Ideas & Roadmap

*   **Enhanced Response Mocking:**
    *   Use `examples` or `example` fields from the OpenAPI spec for more realistic mock responses.
    *   Allow users to provide custom response mappings or scripts.
    *   Support for dynamic data generation (e.g., using Faker).
*   **More API Specification Formats:**
    *   Postman Collections
    *   GraphQL SDL
    *   RAML
    *   API Blueprint
    *   gRPC Protobufs (may require conversion for FastAPI)
*   **Interactive Mock Configuration:**
    *   An MCP tool or UI to configure mock responses, delays, error rates per endpoint.
*   **Stateful Mocks:** Allow some mock endpoints to maintain a simple state.
*   **CLI Tool:** A command-line interface for `mockloop-mcp` (e.g., `mockgen myapi.yaml --run`).
*   **Web UI:** A simple web interface for generating and managing mocks.
*   **Advanced Validation:** More robust validation of input API specifications.
*   **Security Considerations:** If exposing generated mocks, ensure proper security practices.
*   **Integration with Testing Frameworks:** Provide helpers or libraries to easily integrate generated mocks into test suites.
*   **Health Check Endpoint:** Automatically include a `/health` endpoint in generated mocks.

### Prioritized Support Roadmap for API Formats
1.  **OpenAPI (Swagger)** - *Current Focus*
2.  **Postman Collections**
3.  **GraphQL SDL**
4.  **RAML**
5.  **API Blueprint**
6.  **gRPC Protobufs**

## Contributing

(Details to be added later)

## License

This project is licensed under the [MIT License](LICENSE).
