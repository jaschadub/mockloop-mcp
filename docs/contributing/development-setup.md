# Development Setup

This document provides comprehensive guidance for setting up a development environment for MockLoop MCP, including prerequisites, installation steps, configuration, and development workflows.

## Overview

MockLoop MCP development requires a Python environment with specific dependencies, database setup, and development tools. This guide covers:

- **Environment Setup**: Python, dependencies, and virtual environments
- **Database Configuration**: Local database setup for development
- **Development Tools**: Code formatting, linting, testing, and debugging
- **IDE Configuration**: VS Code, PyCharm, and other editor setups
- **Docker Development**: Containerized development environment

## Prerequisites

### System Requirements

- **Python**: 3.9 or higher (3.11+ recommended)
- **Node.js**: 16+ (for documentation and frontend tools)
- **Git**: Latest version
- **Database**: SQLite (included), PostgreSQL, or MySQL (optional)
- **Redis**: For caching and rate limiting (optional)

### Operating System Support

MockLoop MCP development is supported on:

- **Linux**: Ubuntu 20.04+, CentOS 8+, Arch Linux
- **macOS**: 10.15+ (Catalina or later)
- **Windows**: 10/11 with WSL2 recommended

## Environment Setup

### 1. Clone the Repository

```bash
# Clone the main repository
git clone https://github.com/mockloop/mockloop-mcp.git
cd mockloop-mcp

# Clone with all submodules
git clone --recursive https://github.com/mockloop/mockloop-mcp.git
cd mockloop-mcp
```

### 2. Python Environment Setup

#### Using uv (Recommended)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
uv pip install -e ".[dev,test,docs]"
```

#### Using pip and venv

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install development dependencies
pip install -e ".[dev,test,docs]"
```

#### Using conda

```bash
# Create conda environment
conda create -n mockloop-mcp python=3.11
conda activate mockloop-mcp

# Install dependencies
pip install -e ".[dev,test,docs]"
```

### 3. Verify Installation

```bash
# Check MockLoop MCP installation
python -c "import mockloop_mcp; print(mockloop_mcp.__version__)"

# Run basic tests
python -m pytest tests/unit/ -v

# Check CLI availability
mockloop --help
```

## Database Setup

### SQLite (Default)

SQLite requires no additional setup and is used by default:

```bash
# Initialize database
mockloop db init

# Run migrations
mockloop db migrate

# Verify setup
mockloop db status
```

### PostgreSQL Setup

#### Installation

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS with Homebrew
brew install postgresql
brew services start postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE mockloop_dev;
CREATE USER mockloop_dev WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE mockloop_dev TO mockloop_dev;
\q
```

#### Configuration

```bash
# Set environment variables
export MOCKLOOP_DATABASE_TYPE=postgresql
export MOCKLOOP_DATABASE_HOST=localhost
export MOCKLOOP_DATABASE_PORT=5432
export MOCKLOOP_DATABASE_NAME=mockloop_dev
export MOCKLOOP_DATABASE_USER=mockloop_dev
export MOCKLOOP_DATABASE_PASSWORD=dev_password

# Or create .env file
cat > .env << EOF
MOCKLOOP_DATABASE_TYPE=postgresql
MOCKLOOP_DATABASE_HOST=localhost
MOCKLOOP_DATABASE_PORT=5432
MOCKLOOP_DATABASE_NAME=mockloop_dev
MOCKLOOP_DATABASE_USER=mockloop_dev
MOCKLOOP_DATABASE_PASSWORD=dev_password
EOF
```

### MySQL Setup

#### Installation

```bash
# Ubuntu/Debian
sudo apt-get install mysql-server

# macOS with Homebrew
brew install mysql
brew services start mysql

# Create database and user
mysql -u root -p
CREATE DATABASE mockloop_dev;
CREATE USER 'mockloop_dev'@'localhost' IDENTIFIED BY 'dev_password';
GRANT ALL PRIVILEGES ON mockloop_dev.* TO 'mockloop_dev'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### Configuration

```bash
# Set environment variables
export MOCKLOOP_DATABASE_TYPE=mysql
export MOCKLOOP_DATABASE_HOST=localhost
export MOCKLOOP_DATABASE_PORT=3306
export MOCKLOOP_DATABASE_NAME=mockloop_dev
export MOCKLOOP_DATABASE_USER=mockloop_dev
export MOCKLOOP_DATABASE_PASSWORD=dev_password
```

## Development Tools

### Code Formatting and Linting

#### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

#### Manual Tools

```bash
# Format code with black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Lint with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/

# Security scanning with bandit
bandit -r src/
```

### Testing Setup

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mockloop_mcp --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/e2e/          # End-to-end tests

# Run tests with specific markers
pytest -m "not slow"       # Skip slow tests
pytest -m "database"       # Only database tests
```

#### Test Configuration

Create `pytest.ini`:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=mockloop_mcp
    --cov-branch
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    database: marks tests that require database
    redis: marks tests that require Redis
    network: marks tests that require network access
```

### Documentation Development

#### MkDocs Setup

```bash
# Install documentation dependencies
pip install -r docs-requirements.txt

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build

# Check for issues and broken links
mkdocs build --strict
```

#### Documentation Writing

```bash
# Watch for changes and auto-reload
mkdocs serve --dev-addr=0.0.0.0:8000

# Check for issues
mkdocs build --strict

# Generate API documentation
python scripts/generate_api_docs.py
```

#### GitHub Pages Deployment

The documentation is automatically deployed to GitHub Pages using GitHub Actions. The workflow is triggered on:

- **Push to main/master**: Automatically builds and deploys documentation
- **Pull requests**: Builds documentation to check for errors (no deployment)
- **Manual trigger**: Can be triggered manually from GitHub Actions tab

##### Setting Up GitHub Pages

1. **Enable GitHub Pages** in repository settings:
   - Go to Settings → Pages
   - Source: "GitHub Actions"
   - No need to select a branch when using GitHub Actions

2. **Workflow Configuration**: The workflow is defined in `.github/workflows/docs.yml`

3. **Automatic Deployment**:
   ```bash
   # Documentation is automatically deployed when you:
   git push origin main  # Push to main branch
   
   # Or when a PR is merged that changes documentation files
   ```

4. **Manual Deployment** (if needed):
   - Go to GitHub → Actions → "Build and Deploy Documentation"
   - Click "Run workflow" → "Run workflow"

##### Local Testing Before Deployment

```bash
# Test the exact build process used in CI
pip install -r docs-requirements.txt
mkdocs build --clean --strict

# Serve the built site locally
cd site && python -m http.server 8080
```

##### Troubleshooting Deployment

- **Check GitHub Actions**: Go to Actions tab to see build logs
- **Verify dependencies**: Ensure `docs-requirements.txt` includes all needed packages
- **Test locally**: Always test `mkdocs build --strict` before pushing
- **Check permissions**: Ensure repository has Pages and Actions enabled

## IDE Configuration

### VS Code Setup

#### Recommended Extensions

Create `.vscode/extensions.json`:

```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.black-formatter",
        "ms-python.isort",
        "ms-python.flake8",
        "ms-python.mypy-type-checker",
        "ms-python.pylint",
        "charliermarsh.ruff",
        "ms-vscode.test-adapter-converter",
        "littlefoxteam.vscode-python-test-adapter",
        "ms-vscode.vscode-json",
        "redhat.vscode-yaml",
        "yzhang.markdown-all-in-one",
        "davidanson.vscode-markdownlint"
    ]
}
```

#### Workspace Settings

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.unittestEnabled": false,
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": [
        "--profile",
        "black"
    ],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".coverage": true,
        "htmlcov": true,
        ".mypy_cache": true
    }
}
```

#### Launch Configuration

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: MockLoop MCP",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/mockloop_mcp/main.py",
            "args": ["serve"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "MOCKLOOP_LOG_LEVEL": "debug"
            }
        },
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: Pytest",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["${workspaceFolder}/tests"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

### PyCharm Setup

#### Project Configuration

1. **Open Project**: File → Open → Select mockloop-mcp directory
2. **Python Interpreter**: File → Settings → Project → Python Interpreter → Add → Existing environment → Select `.venv/bin/python`
3. **Code Style**: File → Settings → Editor → Code Style → Python → Set to Black
4. **Inspections**: File → Settings → Editor → Inspections → Enable Python inspections

#### Run Configurations

Create run configurations for:

- **MockLoop Server**: Script path: `src/mockloop_mcp/main.py`, Parameters: `serve`
- **Tests**: Test runner: pytest, Target: `tests/`
- **Specific Test**: Test runner: pytest, Target: specific test file

### Vim/Neovim Setup

#### Plugin Configuration

For Neovim with LSP support:

```lua
-- init.lua
require('lspconfig').pylsp.setup{
    settings = {
        pylsp = {
            plugins = {
                pycodestyle = {enabled = false},
                mccabe = {enabled = false},
                pyflakes = {enabled = false},
                flake8 = {enabled = true},
                black = {enabled = true},
                isort = {enabled = true},
                mypy = {enabled = true}
            }
        }
    }
}
```

## Docker Development

### Development Container

Create `docker-compose.dev.yml`:

```yaml
version: '3.8'

services:
  mockloop-dev:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/workspace
      - /workspace/.venv  # Exclude venv from mount
    ports:
      - "8000:8000"
      - "5678:5678"  # Debug port
    environment:
      - MOCKLOOP_LOG_LEVEL=debug
      - MOCKLOOP_DATABASE_TYPE=postgresql
      - MOCKLOOP_DATABASE_HOST=postgres
    depends_on:
      - postgres
      - redis
    command: python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m mockloop_mcp.main serve

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: mockloop_dev
      POSTGRES_USER: mockloop_dev
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

Create `Dockerfile.dev`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Install Python dependencies
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Install debugpy for remote debugging
RUN pip install debugpy

# Copy source code
COPY . .

# Install in development mode
RUN pip install -e ".[dev,test]"

# Expose ports
EXPOSE 8000 5678

# Default command
CMD ["python", "-m", "mockloop_mcp.main", "serve"]
```

### Development Commands

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f mockloop-dev

# Run tests in container
docker-compose -f docker-compose.dev.yml exec mockloop-dev pytest

# Access container shell
docker-compose -f docker-compose.dev.yml exec mockloop-dev bash

# Stop environment
docker-compose -f docker-compose.dev.yml down
```

## Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# ... edit files ...

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Commit changes
git add .
git commit -m "feat: add new feature"

# Push branch
git push origin feature/new-feature
```

### 2. Testing Workflow

```bash
# Run quick tests during development
pytest tests/unit/ -x  # Stop on first failure

# Run full test suite before commit
pytest

# Run tests with coverage
pytest --cov=mockloop_mcp --cov-report=html

# Run specific test
pytest tests/unit/test_generator.py::test_generate_mock_server -v

# Run tests matching pattern
pytest -k "test_auth" -v
```

### 3. Documentation Workflow

```bash
# Start documentation server
mkdocs serve

# Edit documentation files
# ... edit docs/*.md ...

# Check for issues
mkdocs build --strict

# Generate API docs
python scripts/generate_api_docs.py

# Commit documentation changes
git add docs/
git commit -m "docs: update API documentation"
```

### 4. Database Development

```bash
# Create new migration
python scripts/create_migration.py "Add new table"

# Apply migrations
mockloop db migrate

# Rollback migration
mockloop db rollback --version 2

# Reset database (development only)
mockloop db reset --confirm
```

## Debugging

### Local Debugging

#### Python Debugger

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use built-in breakpoint() (Python 3.7+)
breakpoint()
```

#### VS Code Debugging

1. Set breakpoints in code
2. Press F5 or use Run → Start Debugging
3. Select "Python: MockLoop MCP" configuration

#### PyCharm Debugging

1. Set breakpoints in code
2. Right-click → Debug 'MockLoop Server'
3. Use debugger controls to step through code

### Remote Debugging

#### Docker Remote Debugging

```python
# In your code
import debugpy
debugpy.listen(("0.0.0.0", 5678))
debugpy.wait_for_client()  # Optional: wait for debugger to attach
```

Connect from VS Code:

```json
{
    "name": "Python: Remote Attach",
    "type": "python",
    "request": "attach",
    "connect": {
        "host": "localhost",
        "port": 5678
    },
    "pathMappings": [
        {
            "localRoot": "${workspaceFolder}",
            "remoteRoot": "/workspace"
        }
    ]
}
```

### Performance Profiling

```bash
# Profile with cProfile
python -m cProfile -o profile.stats -m mockloop_mcp.main serve

# Analyze profile
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
"

# Profile with py-spy
pip install py-spy
py-spy record -o profile.svg -- python -m mockloop_mcp.main serve
```

## Environment Variables

### Development Environment Variables

Create `.env` file:

```bash
# Database
MOCKLOOP_DATABASE_TYPE=sqlite
MOCKLOOP_DATABASE_PATH=./dev.db

# Logging
MOCKLOOP_LOG_LEVEL=debug
MOCKLOOP_LOG_FORMAT=text

# Development
MOCKLOOP_DEBUG=true
MOCKLOOP_RELOAD=true

# Testing
MOCKLOOP_TEST_DATABASE_URL=sqlite:///test.db
MOCKLOOP_TEST_REDIS_URL=redis://localhost:6379/1

# API Keys (for testing)
MOCKLOOP_TEST_API_KEY=test-key-12345
```

### Loading Environment Variables

```python
# In development scripts
from dotenv import load_dotenv
load_dotenv()

# Or use python-dotenv in code
import os
from pathlib import Path

env_path = Path('.') / '.env'
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)
```

## Troubleshooting

### Common Issues

#### Import Errors

```bash
# Ensure package is installed in development mode
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"

# Verify installation
python -c "import mockloop_mcp; print(mockloop_mcp.__file__)"
```

#### Database Issues

```bash
# Reset database
rm -f dev.db
mockloop db init
mockloop db migrate

# Check database connection
python -c "
from mockloop_mcp.database import get_database_connection
conn = get_database_connection()
print('Database connection successful')
"
```

#### Port Conflicts

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Use different port
export MOCKLOOP_PORT=8001
```

#### Permission Issues

```bash
# Fix file permissions
chmod +x scripts/*.py

# Fix directory permissions
chmod -R 755 src/
```

### Getting Help

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Discord**: Real-time chat with developers
- **Documentation**: Check the full documentation

## Next Steps

After setting up your development environment:

1. **Read the [Contributing Guidelines](guidelines.md)** for code standards
2. **Review the [Testing Guide](testing.md)** for testing practices
3. **Check the [Release Process](release-process.md)** for deployment procedures
4. **Explore the codebase** and start contributing!

---

Welcome to MockLoop MCP development! We're excited to have you contribute to the project.