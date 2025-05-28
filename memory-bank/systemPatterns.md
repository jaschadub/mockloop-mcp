# System Patterns

**Core Architecture:**
The `mockloop-mcp` server follows a modular architecture centered around parsing API specifications and generating runnable mock servers.

1.  **MCP Tool Interface:**
    *   The primary interaction point is an MCP tool (e.g., `generate_mock_api`).
    *   Input: API specification source (URL or local file path), output directory for generated code (optional).
    *   Output: Path to the generated mock server, status message.

2.  **API Specification Parser (`parser.py`):**
    *   Responsible for loading API documentation from a given URL or file path.
    *   Supports OpenAPI (JSON/YAML) specifications initially.
    *   Validates the specification format (basic validation).
    *   Transforms the raw specification into a structured Python dictionary/object that the generator can easily consume.

3.  **FastAPI Code Generator (`generator.py`):**
    *   Takes the parsed API specification data as input.
    *   Uses Jinja2 templates to generate Python code for a FastAPI application.
    *   Generates the following components for each mock API:
        *   `main.py`: The FastAPI application, including:
            *   Router instantiations.
            *   Mock endpoint definitions for each path and method in the API spec.
            *   Integration of the logging middleware.
        *   `requirements_mock.txt`: A minimal list of dependencies for the mock server (e.g., `fastapi`, `uvicorn`).
        *   `Dockerfile`: To containerize the generated FastAPI application.
        *   `docker-compose.yml`: To easily run the mock server using Docker Compose.
    *   Places generated files into a dedicated output directory (e.g., `generated_mocks/my_api_mock/`).

4.  **Jinja2 Templates (`src/mockloop_mcp/templates/`):**
    *   `route_template.j2`: Defines the structure for individual FastAPI route handlers.
        *   Variables: HTTP method, path, summary, basic mock response.
    *   `middleware_log_template.j2`: Defines a FastAPI middleware class for comprehensive request/response logging.
        *   Logs details like timestamp, method, path, headers, query params, request body, response status, response body, and processing time to `stdout`.
    *   `dockerfile_template.j2`: A template for the `Dockerfile` to build the mock server image.
        *   Variables: Python version, port.
    *   `docker_compose_template.j2`: A template for the `docker-compose.yml` file.
        *   Variables: Service name, host port, container port.

5.  **Generated Mock Server:**
    *   A self-contained FastAPI application.
    *   Each endpoint returns a static, predefined mock response (e.g., `{"message": "mock response"}`).
    *   Includes the logging middleware for detailed request/response tracing.
    *   Can be run directly using Uvicorn or via the generated Docker Compose setup.

**Key Design Patterns:**

*   **Template-Based Code Generation:** Jinja2 is used to separate the structure of the generated code from the generation logic, allowing for easier maintenance and modification of the output format.
*   **Modular Design:** The system is broken down into distinct components (parser, generator, MCP tool interface), promoting separation of concerns.
*   **Convention over Configuration (for generated mocks):** The generated mocks follow a standard structure, making them predictable and easy to understand.
*   **Middleware for Cross-Cutting Concerns:** Logging is implemented as FastAPI middleware, keeping the route handler logic clean.

**Error Handling:**
*   The parser will handle basic errors like invalid file paths or unfetchable URLs.
*   The generator will assume a valid parsed specification. More robust error handling for malformed specs can be added later.
*   The MCP tool will return clear error messages to the user if any step fails.
