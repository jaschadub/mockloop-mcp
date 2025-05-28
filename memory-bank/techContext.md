# Tech Context

**Programming Language:**
*   Python (Version 3.9 or higher recommended for FastAPI and modern type hinting).

**Core Frameworks & Libraries:**
*   **`fastapi`**: For building the generated mock API servers. Chosen for its high performance, ease of use, and automatic data validation and serialization with Pydantic.
*   **`uvicorn`**: ASGI server to run the generated FastAPI applications. `uvicorn[standard]` is recommended for performance benefits.
*   **`pydantic`**: Used implicitly by FastAPI for data validation and settings management.
*   **`Jinja2`**: Templating engine for generating Python code (`main.py` for mocks), `Dockerfile`, `docker-compose.yml`, and `requirements_mock.txt`.
*   **`PyYAML`**: For parsing API specifications provided in YAML format.
*   **`requests`**: For fetching API specifications from URLs.
*   **Python Standard Library**: Modules like `json` (for JSON specs), `os`, `pathlib`, `logging`, `time`.

**MCP Integration:**
*   The project will use the relevant Python SDK for creating Model Context Protocol (MCP) servers and defining tools.
*   The MCP server itself will likely be a FastAPI application or a simple Python script utilizing the MCP SDK.

**Development Environment & Setup:**
*   **Virtual Environment:** A Python virtual environment (e.g., created with `python3 -m venv .venv`) is strongly recommended to manage project dependencies and avoid conflicts with system-wide packages.
*   **Dependency Management:** Project dependencies for `mockloop-mcp` itself will be listed in `requirements.txt`. Generated mock servers will have their own minimal `requirements_mock.txt`.
*   **Packaging**: `pyproject.toml` will be used for modern Python packaging and build system configuration (e.g., with `build` and `hatchling` or `setuptools`).
*   **IDE/Editor:** Any Python-supporting IDE (VS Code, PyCharm, etc.).
*   **Version Control:** Git.

**Tooling:**
*   **`pip`**: For installing Python packages.
*   **`Docker`**: For containerizing the generated mock API servers.
*   **`Docker Compose`**: For defining and running multi-container Docker applications, primarily to run the generated mock server.
*   **Linters/Formatters (Recommended for future):** `Black` for code formatting, `Flake8` or `Ruff` for linting, `Mypy` for static type checking.
*   **Testing Framework (Recommended for future):** `pytest` for writing and running tests for `mockloop-mcp` itself.

**Supported API Specification Formats (Initial Focus):**
*   OpenAPI v2 (Swagger) and v3 (JSON, YAML).
*   Future support planned for Postman Collections, GraphQL SDL, etc., as per user feedback.
