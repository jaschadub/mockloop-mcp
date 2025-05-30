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

### Method 1: From PyPI (Recommended)

The easiest way to install MockLoop MCP is from PyPI:

```bash
# Install the latest stable version
pip install mockloop-mcp

# Or install with specific version
pip install mockloop-mcp==2.1.0

# Install with optional dependencies
pip install mockloop-mcp[dev]  # Development tools
pip install mockloop-mcp[docs]  # Documentation tools
pip install mockloop-mcp[all]  # All optional dependencies
```

#### Virtual Environment (Recommended)

For better dependency management, use a virtual environment:

```bash
# Create virtual environment
python3 -m venv mockloop-env
source mockloop-env/bin/activate  # On Windows: mockloop-env\Scripts\activate

# Install MockLoop MCP
pip install mockloop-mcp

# Verify installation
mockloop-mcp --version
```

### Method 2: Development Installation

For contributors or advanced users who want the latest development version:

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

3. **Install in Development Mode**
   ```bash
   pip install -e ".[dev,test,docs]"
   ```

### Method 3: Using pipx (Isolated Installation)

For system-wide installation without affecting other Python packages:

```bash
# Install pipx if not already installed
pip install pipx

# Install MockLoop MCP with pipx
pipx install mockloop-mcp

# Run directly
mockloop-mcp --version
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

2. **Verify MockLoop MCP Installation**
   ```bash
   # Check if MockLoop MCP is installed
   pip show mockloop-mcp
   
   # Check version
   mockloop-mcp --version
   ```

3. **Verify Dependencies**
   ```bash
   pip list | grep -E "(fastapi|uvicorn|mcp|mockloop)"
   ```

4. **Test MCP Server**
   ```bash
   # For PyPI installation
   mockloop-mcp --help
   
   # For development installation
   mcp dev src/mockloop_mcp/main.py
   ```

5. **Test Python Import**
   ```bash
   python -c "import mockloop_mcp; print('MockLoop MCP imported successfully')"
   ```

   You should see output indicating successful import and MCP server availability.

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

### PyPI Installation Issues

#### Package Not Found
If you get "No matching distribution found":
```bash
# Update pip to latest version
pip install --upgrade pip

# Check if package exists
pip search mockloop-mcp

# Try with explicit index
pip install --index-url https://pypi.org/simple/ mockloop-mcp
```

#### Version Conflicts
If you encounter dependency conflicts:
```bash
# Check installed packages
pip list | grep mockloop

# Uninstall and reinstall
pip uninstall mockloop-mcp
pip install mockloop-mcp

# Use dependency resolver
pip install --upgrade --force-reinstall mockloop-mcp
```

#### SSL Certificate Issues
If you encounter SSL errors:
```bash
# Upgrade certificates (macOS)
/Applications/Python\ 3.x/Install\ Certificates.command

# Use trusted hosts (temporary fix)
pip install --trusted-host pypi.org --trusted-host pypi.python.org mockloop-mcp

# Update pip and certificates
pip install --upgrade pip certifi
```

#### Network/Proxy Issues
If installation fails due to network issues:
```bash
# Use proxy
pip install --proxy http://user:password@proxy.server:port mockloop-mcp

# Use different index
pip install -i https://pypi.python.org/simple/ mockloop-mcp

# Increase timeout
pip install --timeout 60 mockloop-mcp
```

#### Import Errors After Installation
If you can install but can't import:
```bash
# Check installation location
pip show mockloop-mcp

# Verify Python path
python -c "import sys; print('\n'.join(sys.path))"

# Reinstall in current environment
pip uninstall mockloop-mcp
pip install mockloop-mcp

# Check for conflicting installations
pip list | grep mockloop
```

### Installation Verification

After PyPI installation, verify everything works:

```bash
# Check MockLoop MCP version
mockloop-mcp --version

# Test MCP server startup
mockloop-mcp --help

# Verify Python can import the package
python -c "import mockloop_mcp; print('Installation successful!')"

# Check available tools
python -c "from mockloop_mcp.main import main; print('MCP tools available')"
```

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