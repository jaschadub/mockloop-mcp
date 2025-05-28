# Active Context

**Current Focus:**
*   Initial project setup and implementation of the core `mockloop-mcp` server.
*   Establishing the directory structure as planned.
*   Creating the foundational Python modules: `parser.py`, `generator.py`, and the main MCP server entry point (`src/mockloop_mcp/main.py`).
*   Developing the initial set of Jinja2 templates: `route_template.j2`, `middleware_log_template.j2`, `dockerfile_template.j2`, `docker_compose_template.j2`.

**Recent Changes:**
*   Finalized the initial plan for `mockloop-mcp` based on user input and ChatGPT suggestions.
*   Updated core memory bank documents (`projectbrief.md`, `productContext.md`, `systemPatterns.md`, `techContext.md`) to reflect the project's scope, architecture, and technology choices.

**Next Steps (Immediate):**
1.  Create the main project directories: `src/mockloop_mcp/templates`, `generated_mocks`, `tests`, `src/scripts`.
2.  Create placeholder `__init__.py` files where necessary.
3.  Create the initial `requirements.txt` file with core dependencies.
4.  Create the initial `.gitignore` file.
5.  Create the initial `README.md` file, incorporating future ideas and API doc priorities.
6.  Create the `pyproject.toml` file for Python packaging.
7.  Begin implementation of `parser.py` to load and parse OpenAPI specifications.
8.  Begin implementation of `generator.py` and the Jinja2 templates.
9.  Develop the MCP tool definition in `src/mockloop_mcp/main.py`.

**Important Decisions & Considerations:**
*   **Python Version:** Target Python 3.9+ for compatibility with FastAPI and modern type hinting.
*   **Virtual Environment:** All development and execution will assume a Python virtual environment is active.
*   **Initial Mock Response:** Generated mock endpoints will initially return a static, generic JSON response (e.g., `{"message": "mock response"}`). Dynamic response generation based on API schemas is a future enhancement.
*   **Logging:** Focus on comprehensive request/response logging to `stdout` for easy debugging, especially when using Docker.
*   **Error Handling:** Implement basic error handling for file operations and API spec parsing. More sophisticated validation will be added iteratively.
*   **Output Directory:** Generated mock server files will be placed in the `generated_mocks/` directory, which will be added to `.gitignore`.
