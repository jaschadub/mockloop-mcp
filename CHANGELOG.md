# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [2.2.1] - 2025-05-30

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [2.2.0] - 2025-05-30

### Added
- GitHub Actions CI/CD pipeline for automated testing and PyPI publishing
- Automated release workflow with PyPI trusted publishing
- Comprehensive test matrix for Python 3.10, 3.11, and 3.12
- Security scanning with ruff and bandit in CI pipeline
- Code coverage reporting with Codecov integration
- Package build validation and distribution checks

### Changed
- Updated project version to 2.2.0 for major release
- Enhanced release automation and deployment process
- Improved development workflow with automated quality checks

### Fixed
- Version consistency across all project files
- Configuration file formatting and validation

## [0.1.0] - 2025-05-30

### Added
- Initial release of MockLoop MCP server
- FastAPI mock server generation from OpenAPI specifications
- Authentication middleware support with configurable auth types
- Webhook functionality for external integrations
- Admin UI for server management and monitoring
- Storage capabilities for persistent mock data
- Docker support with automated containerization
- Comprehensive logging and request/response tracking
- MCP tools for generating, querying, and managing mock servers
- Support for dynamic response scenarios and data management
- Integration with MockLoop ecosystem
- Comprehensive test suite with unit and integration tests
- Security workflows and quality assurance tools
- Pre-commit hooks for code quality enforcement
- GitHub Actions CI/CD pipeline
- Code coverage reporting and analysis
- Dependency vulnerability scanning
- Static security analysis with multiple tools

### Security
- Implemented security policy and vulnerability reporting process
- Added automated dependency vulnerability scanning with Dependabot
- Integrated multiple security analysis tools (Bandit, Safety, Semgrep, pip-audit)
- Configured secure coding practices and validation

[Unreleased]: https://github.com/mockloop/mockloop-mcp/compare/v2.2.1...HEAD
[2.2.1]: https://github.com/mockloop/mockloop-mcp/releases/tag/v2.2.1
v2.2.0...HEAD
[2.2.0]: https://github.com/mockloop/mockloop-mcp/releases/tag/v2.2.0
[0.1.0]: https://github.com/mockloop/mockloop-mcp/releases/tag/v0.1.0
