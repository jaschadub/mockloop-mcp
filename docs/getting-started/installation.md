# Installation

This guide will walk you through installing MockLoop MCP and setting up your development environment.

## Prerequisites

Before installing MockLoop MCP, ensure you have the following prerequisites:

### System Requirements
- **Python 3.9+** (Python 3.10+ recommended)
- **pip** (Python package installer)
- **Docker and Docker Compose** (for running generated mocks in containers)
- **Git** (for cloning the repository)

### MCP Client
You'll need an MCP client to interact with MockLoop MCP. Supported clients include:
- **Cline (VS Code Extension)**: Recommended for development
- **Claude Desktop**: For desktop usage
- **Custom MCP clients**: Any client supporting the MCP protocol

## Installation Methods

### Method 1: From Source (Recommended)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/mockloop/mockloop-mcp.git
   cd mockloop-mcp
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Method 2: Using pip (Future Release)

!!! note "Coming Soon"
    MockLoop MCP will be available on PyPI in future releases:
    ```bash
    pip install mockloop-mcp
    ```

## Dependencies

MockLoop MCP includes the following key dependencies:

### Core Dependencies
- **FastAPI**: Web framework for generated mock servers
- **Uvicorn**: ASGI server for running FastAPI applications
- **Jinja2**: Template engine for code generation
- **PyYAML**: YAML parsing for OpenAPI specifications
- **Requests**: HTTP library for fetching remote specifications

### Enhanced Features
- **aiohttp**: Async HTTP client functionality
- **SQLite3**: Database for request logging (built into Python)

### MCP Framework
- **mcp[cli]**: Model Context Protocol SDK

## Verification

After installation, verify that MockLoop MCP is working correctly:

1. **Check Python Version**
   ```bash
   python --version
   # Should show Python 3.9 or higher
   ```

2. **Verify Dependencies**
   ```bash
   pip list | grep -E "(fastapi|uvicorn|mcp)"
   ```

3. **Test MCP Server**
   ```bash
   mcp dev src/mockloop_mcp/main.py
   ```

   You should see output indicating the MCP server is running.

## Docker Setup (Optional)

If you plan to use Docker for running generated mock servers:

1. **Install Docker**
   - **Linux**: Follow the [official Docker installation guide](https://docs.docker.com/engine/install/)
   - **macOS**: Install [Docker Desktop for Mac](https://docs.docker.com/desktop/mac/install/)
   - **Windows**: Install [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/install/)

2. **Install Docker Compose**
   ```bash
   # Usually included with Docker Desktop
   docker-compose --version
   ```

3. **Verify Docker Installation**
   ```bash
   docker --version
   docker run hello-world
   ```

## Development Tools (Optional)

For development and advanced usage, consider installing:

### Code Quality Tools
```bash
pip install black flake8 mypy pytest
```

### Documentation Tools
```bash
pip install mkdocs mkdocs-material mkdocstrings[python]
```

## Troubleshooting

### Common Issues

#### Python Version Issues
If you encounter Python version issues:
```bash
# Check available Python versions
python3 --version
python3.10 --version
python3.11 --version

# Use specific version for virtual environment
python3.10 -m venv .venv
```

#### Permission Issues (Linux/macOS)
If you encounter permission issues:
```bash
# Use user installation
pip install --user -r requirements.txt

# Or fix permissions
sudo chown -R $USER:$USER ~/.local
```

#### Windows Path Issues
On Windows, ensure Python is in your PATH:
1. Open System Properties → Advanced → Environment Variables
2. Add Python installation directory to PATH
3. Restart command prompt

#### Docker Issues
If Docker commands fail:
```bash
# Check Docker service status (Linux)
sudo systemctl status docker

# Start Docker service (Linux)
sudo systemctl start docker

# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in
```

### Getting Help

If you encounter issues during installation:

1. **Check the [Troubleshooting Guide](../advanced/troubleshooting.md)**
2. **Search [GitHub Issues](https://github.com/mockloop/mockloop-mcp/issues)**
3. **Create a new issue** with:
   - Your operating system and version
   - Python version
   - Complete error message
   - Steps to reproduce

## Next Steps

Once installation is complete, proceed to:

- **[Configuration](configuration.md)**: Configure MockLoop MCP for your environment
- **[Quick Start](quick-start.md)**: Generate your first mock server
- **[First Mock Server](first-mock-server.md)**: Detailed walkthrough of creating a mock server

## Environment Variables

MockLoop MCP supports several environment variables for configuration:

```bash
# Optional: Set custom port for generated mocks
export MOCKLOOP_DEFAULT_PORT=8000

# Optional: Set default output directory
export MOCKLOOP_OUTPUT_DIR=./generated_mocks

# Optional: Enable debug logging
export MOCKLOOP_DEBUG=true
```

Add these to your shell profile (`.bashrc`, `.zshrc`, etc.) for persistence.