# Contributing Guidelines

This document outlines the guidelines and best practices for contributing to MockLoop MCP. Following these guidelines helps maintain code quality, consistency, and ensures a smooth collaboration process.

## Overview

We welcome contributions from the community! Whether you're fixing bugs, adding features, improving documentation, or helping with testing, your contributions are valuable. This guide covers:

- **Code Standards**: Formatting, style, and quality requirements
- **Development Process**: Workflow for contributing changes
- **Pull Request Guidelines**: How to submit and review changes
- **Issue Management**: Reporting bugs and requesting features
- **PyPI Distribution**: Guidelines for package distribution
- **Community Standards**: Code of conduct and communication

## PyPI Distribution Guidelines

MockLoop MCP is distributed via PyPI, which requires special attention to certain aspects:

### Package Quality Standards

- **Version Compatibility**: Ensure compatibility with supported Python versions (3.9+)
- **Dependency Management**: Keep dependencies minimal and well-tested
- **Documentation**: Maintain comprehensive documentation for PyPI users
- **Testing**: Ensure all tests pass across supported environments
- **Security**: Follow security best practices for package distribution

### PyPI-Related Issues

When reporting issues related to PyPI installation or distribution:

1. **Installation Issues**: Use the PyPI Installation Issue template (available in GitHub issue templates)
2. **Version Problems**: Include specific version numbers and Python environment details
3. **Dependency Conflicts**: Provide complete pip freeze output
4. **Distribution Issues**: Tag issues with `pypi` and `distribution` labels

### Testing PyPI Changes

Before submitting changes that affect PyPI distribution:

```bash
# Test local installation
pip install -e .

# Test package building
python -m build

# Test with different Python versions
tox

# Verify package metadata
python setup.py check --metadata --strict
```

### Release Process Contributions

Contributors can help with the release process by:

- **Testing Release Candidates**: Install and test pre-release versions
- **Documentation Updates**: Ensure documentation reflects latest changes
- **Changelog Maintenance**: Help maintain accurate changelog entries
- **Version Testing**: Test across different Python versions and platforms

## Code Standards

### Python Code Style

We follow [PEP 8](https://pep8.org/) with some modifications and use automated tools to enforce consistency.

#### Formatting Tools

```bash
# Black for code formatting
black src/ tests/ scripts/

# isort for import sorting
isort src/ tests/ scripts/ --profile black

# flake8 for linting
flake8 src/ tests/ scripts/

# mypy for type checking
mypy src/
```

#### Code Style Rules

```python
# Use type hints for all function signatures
def generate_mock_server(
    spec_path: str, 
    output_dir: str, 
    options: GenerationOptions
) -> GenerationResult:
    """Generate a mock server from API specification.
    
    Args:
        spec_path: Path to the API specification file
        output_dir: Directory for generated files
        options: Generation configuration options
        
    Returns:
        Result containing server information and status
        
    Raises:
        SpecificationError: If specification is invalid
        GenerationError: If generation fails
    """
    pass

# Use dataclasses for structured data
@dataclass
class ServerConfig:
    """Configuration for mock server."""
    
    name: str
    port: int
    auth_enabled: bool = True
    storage_enabled: bool = True
    
    def validate(self) -> None:
        """Validate configuration values."""
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port: {self.port}")

# Use enums for constants
class ServerStatus(Enum):
    """Mock server status values."""
    
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

# Use context managers for resource management
async def process_request(request: Request) -> Response:
    """Process HTTP request."""
    
    async with database.transaction():
        # Database operations
        log_entry = await database.insert_log(request)
        
        # Process request
        response = await handle_request(request)
        
        # Update log with response
        await database.update_log(log_entry.id, response)
        
        return response
```

#### Documentation Standards

```python
# Use Google-style docstrings
def calculate_response_time(start_time: float, end_time: float) -> float:
    """Calculate response time in milliseconds.
    
    Args:
        start_time: Request start timestamp in seconds
        end_time: Request end timestamp in seconds
        
    Returns:
        Response time in milliseconds
        
    Example:
        >>> start = time.time()
        >>> time.sleep(0.1)
        >>> end = time.time()
        >>> response_time = calculate_response_time(start, end)
        >>> assert 90 <= response_time <= 110
    """
    return (end_time - start_time) * 1000

# Document complex algorithms
def generate_cache_key(request: Request) -> str:
    """Generate cache key for request.
    
    The cache key is generated by combining:
    1. HTTP method (GET, POST, etc.)
    2. URL path (without query parameters)
    3. Sorted query parameters
    4. Content-Type header
    5. Accept header
    
    The combined string is then hashed using SHA-256 to ensure
    consistent key length and avoid special characters.
    
    Args:
        request: HTTP request object
        
    Returns:
        32-character hexadecimal cache key
    """
    # Implementation details...
```

### Testing Standards

#### Test Structure

```python
# Use descriptive test names
def test_generate_mock_server_with_valid_openapi_spec():
    """Test mock server generation with valid OpenAPI specification."""
    pass

def test_generate_mock_server_raises_error_with_invalid_spec():
    """Test that invalid specification raises SpecificationError."""
    pass

# Use pytest fixtures for setup
@pytest.fixture
def mock_server_config():
    """Provide test configuration for mock server."""
    return ServerConfig(
        name="test_server",
        port=8080,
        auth_enabled=False,
        storage_enabled=False
    )

@pytest.fixture
async def database_connection():
    """Provide test database connection."""
    conn = await create_test_database()
    yield conn
    await cleanup_test_database(conn)

# Use parametrized tests for multiple scenarios
@pytest.mark.parametrize("spec_type,expected_routes", [
    ("openapi", 5),
    ("swagger", 3),
    ("postman", 7),
])
def test_route_generation_by_spec_type(spec_type, expected_routes):
    """Test route generation for different specification types."""
    pass

# Use async tests for async code
@pytest.mark.asyncio
async def test_async_request_processing():
    """Test asynchronous request processing."""
    request = create_test_request()
    response = await process_request(request)
    assert response.status_code == 200
```

#### Test Coverage

- **Minimum Coverage**: 80% overall, 90% for core modules
- **Critical Paths**: 100% coverage for security and data integrity code
- **Integration Tests**: Cover main user workflows
- **Unit Tests**: Cover individual functions and classes

```bash
# Run tests with coverage
pytest --cov=mockloop_mcp --cov-report=html --cov-report=term

# Check coverage thresholds
pytest --cov=mockloop_mcp --cov-fail-under=80
```

### Error Handling

#### Exception Hierarchy

```python
# Base exception class
class MockLoopError(Exception):
    """Base exception for MockLoop MCP errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code
        self.timestamp = datetime.utcnow()

# Specific exception types
class SpecificationError(MockLoopError):
    """Exception for API specification errors."""
    
    def __init__(self, message: str, spec_path: Optional[str] = None):
        super().__init__(message, "SPEC_ERROR")
        self.spec_path = spec_path

class GenerationError(MockLoopError):
    """Exception for mock server generation errors."""
    
    def __init__(self, message: str, stage: Optional[str] = None):
        super().__init__(message, "GEN_ERROR")
        self.stage = stage

# Error handling patterns
async def safe_operation() -> Result[T, Error]:
    """Perform operation with proper error handling."""
    
    try:
        result = await risky_operation()
        return Success(result)
        
    except SpecificationError as e:
        logger.error(f"Specification error: {e}", exc_info=True)
        return Failure(e)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return Failure(MockLoopError(f"Operation failed: {str(e)}"))
```

### Logging Standards

```python
# Use structured logging
import structlog

logger = structlog.get_logger(__name__)

async def process_request(request: Request) -> Response:
    """Process HTTP request with proper logging."""
    
    request_id = generate_request_id()
    
    logger.info(
        "Processing request",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host
    )
    
    try:
        response = await handle_request(request)
        
        logger.info(
            "Request processed successfully",
            request_id=request_id,
            status_code=response.status_code,
            response_time_ms=response.processing_time
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "Request processing failed",
            request_id=request_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        raise
```

## Development Process

### Git Workflow

We use a modified Git Flow workflow:

#### Branch Types

- **`main`**: Production-ready code
- **`develop`**: Integration branch for features
- **`feature/*`**: New features and enhancements
- **`bugfix/*`**: Bug fixes for develop branch
- **`hotfix/*`**: Critical fixes for production
- **`release/*`**: Release preparation

#### Branch Naming

```bash
# Feature branches
feature/add-webhook-support
feature/improve-performance
feature/user-authentication

# Bug fix branches
bugfix/fix-memory-leak
bugfix/correct-validation-error
bugfix/resolve-race-condition

# Hotfix branches
hotfix/security-vulnerability
hotfix/critical-data-loss

# Release branches
release/v1.2.0
release/v1.2.1
```

#### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: <type>[optional scope]: <description>

# Types:
feat: add new feature
fix: bug fix
docs: documentation changes
style: formatting, missing semicolons, etc.
refactor: code refactoring
test: adding or updating tests
chore: maintenance tasks

# Examples:
feat(auth): add JWT authentication support
fix(database): resolve connection pool exhaustion
docs(api): update API reference documentation
test(generator): add integration tests for mock generation
refactor(core): simplify request processing logic
chore(deps): update dependencies to latest versions

# Breaking changes:
feat!: change API response format
feat(api)!: remove deprecated endpoints
```

### Development Workflow

#### 1. Setup Development Environment

```bash
# Fork repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/mockloop-mcp.git
cd mockloop-mcp

# Add upstream remote
git remote add upstream https://github.com/mockloop/mockloop-mcp.git

# Setup development environment
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,test,docs]"
```

#### 2. Create Feature Branch

```bash
# Update develop branch
git checkout develop
git pull upstream develop

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
# ... edit files ...

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Commit changes
git add .
git commit -m "feat: add your feature description"
```

#### 3. Keep Branch Updated

```bash
# Regularly sync with upstream
git fetch upstream
git rebase upstream/develop

# Resolve conflicts if any
# ... resolve conflicts ...
git add .
git rebase --continue
```

#### 4. Submit Pull Request

```bash
# Push branch to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
# Fill out pull request template
# Request review from maintainers
```

## Pull Request Guidelines

### Pull Request Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Documentation updated (if applicable)
- [ ] No new warnings introduced
- [ ] Changes are backward compatible (or breaking changes documented)

## Related Issues
Closes #123
Fixes #456
Related to #789
```

### Review Process

#### For Contributors

1. **Self-Review**: Review your own code before submitting
2. **Tests**: Ensure all tests pass and add new tests for new functionality
3. **Documentation**: Update documentation for user-facing changes
4. **Small PRs**: Keep pull requests focused and reasonably sized
5. **Responsive**: Respond to review feedback promptly

#### For Reviewers

1. **Timely Reviews**: Review PRs within 2-3 business days
2. **Constructive Feedback**: Provide specific, actionable feedback
3. **Code Quality**: Check for code style, performance, and security issues
4. **Testing**: Verify adequate test coverage
5. **Documentation**: Ensure documentation is updated appropriately

### Review Criteria

#### Code Quality
- [ ] Code follows established patterns and conventions
- [ ] Functions and classes have clear, single responsibilities
- [ ] Error handling is appropriate and consistent
- [ ] Performance considerations are addressed
- [ ] Security best practices are followed

#### Testing
- [ ] New functionality has appropriate test coverage
- [ ] Tests are well-structured and maintainable
- [ ] Edge cases are covered
- [ ] Integration points are tested

#### Documentation
- [ ] Public APIs are documented
- [ ] Complex algorithms are explained
- [ ] User-facing changes are documented
- [ ] Breaking changes are clearly marked

## Issue Management

### Bug Reports

Use the bug report template:

```markdown
**Bug Description**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Python Version: [e.g. 3.11.0]
- MockLoop MCP Version: [e.g. 1.2.0]
- Database: [e.g. PostgreSQL 15]

**Additional Context**
Add any other context about the problem here.
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.

**Implementation Ideas**
If you have ideas about how this could be implemented, please share them.
```

### Issue Labels

- **Type**: `bug`, `enhancement`, `documentation`, `question`
- **Priority**: `critical`, `high`, `medium`, `low`
- **Status**: `needs-triage`, `in-progress`, `blocked`, `ready-for-review`
- **Component**: `core`, `api`, `database`, `auth`, `docs`
- **Difficulty**: `good-first-issue`, `help-wanted`, `expert-needed`

## Community Standards

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read and follow our [Code of Conduct](https://github.com/mockloop/mockloop-mcp/blob/main/CODE_OF_CONDUCT.md).

### Communication Guidelines

#### GitHub Discussions
- Use for questions, ideas, and general discussion
- Search existing discussions before creating new ones
- Use clear, descriptive titles
- Provide context and examples

#### Issues
- Use for bug reports and feature requests
- Follow issue templates
- Provide detailed information
- Stay on topic

#### Pull Requests
- Use for code contributions
- Follow PR template
- Respond to feedback constructively
- Keep discussions focused on the code

### Recognition

We recognize contributors in several ways:

- **Contributors File**: All contributors are listed in CONTRIBUTORS.md
- **Release Notes**: Significant contributions are mentioned in release notes
- **GitHub Recognition**: We use GitHub's contributor recognition features
- **Community Highlights**: Outstanding contributions are highlighted in community updates

## Getting Help

### Resources

- **Documentation**: Comprehensive guides and API reference
- **GitHub Discussions**: Community Q&A and discussions
- **Issues**: Bug reports and feature requests
- **Discord**: Real-time chat with maintainers and community

### Mentorship

New contributors can request mentorship:

1. Comment on a `good-first-issue` asking for guidance
2. Join our Discord and ask in the #contributors channel
3. Attend community office hours (schedule in Discord)

### Office Hours

Maintainers hold regular office hours for:
- Answering questions about contributing
- Discussing feature ideas
- Providing guidance on implementation
- Code review sessions

Check Discord for current schedule.

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in a backward compatible manner
- **PATCH**: Backward compatible bug fixes

### Release Schedule

- **Major Releases**: Every 6-12 months
- **Minor Releases**: Every 1-2 months
- **Patch Releases**: As needed for critical fixes

### Release Criteria

#### Major Release
- [ ] All planned features implemented
- [ ] Breaking changes documented
- [ ] Migration guide provided
- [ ] Full test suite passes
- [ ] Performance benchmarks meet targets
- [ ] Security review completed

#### Minor Release
- [ ] New features tested and documented
- [ ] Backward compatibility maintained
- [ ] No known critical bugs
- [ ] Documentation updated

#### Patch Release
- [ ] Critical bugs fixed
- [ ] No new features
- [ ] Minimal risk of regression
- [ ] Emergency fixes only

## Conclusion

Thank you for contributing to MockLoop MCP! Your contributions help make the project better for everyone. If you have questions about these guidelines or need help getting started, please don't hesitate to reach out through our community channels.

Remember:
- Start small with good first issues
- Ask questions when you're unsure
- Follow the established patterns
- Write tests for your code
- Update documentation
- Be patient and respectful

Happy coding! 🚀

## See Also

- **[Development Setup](development-setup.md)**: Setting up your development environment
- **[Testing Guide](testing.md)**: Comprehensive testing practices
- **[Release Process](release-process.md)**: Detailed release procedures