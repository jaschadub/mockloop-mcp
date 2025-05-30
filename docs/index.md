<div class="hero-section">
  <img src="logo.png" alt="MockLoop Logo" style="height: 64px; margin-bottom: 1rem;">

  <p>A powerful Model Context Protocol server for generating sophisticated mock API servers from API documentation. Streamline your development workflow with AI-powered mock generation and intelligent testing capabilities.</p>
  <a href="getting-started/installation/" class="cta-button">Get Started →</a>
</div>

## What is MockLoop MCP?

MockLoop MCP is a comprehensive MCP server that automates the generation and execution of feature-rich mock API servers directly from API documentation (initially focusing on OpenAPI/Swagger specifications). This enables developers to quickly obtain a functional mock environment for development and testing purposes, reducing dependencies on live backend systems and facilitating parallel workflows.

## Key Features

### 🚀 Core Capabilities
- **API Mock Generation**: Takes an API specification (URL or local file) and generates a runnable FastAPI mock server
- **Request/Response Logging**: Generated mock servers include middleware for comprehensive logging with SQLite storage
- **Dockerized Mocks**: Generates `Dockerfile` and `docker-compose.yml` for each mock API
- **OpenAPI Support**: Initial support for OpenAPI v2 (Swagger) and v3 (JSON, YAML)

### 🔍 Enhanced Features (v2.0+)
- **Advanced Log Analysis**: Query and analyze request logs with filtering, performance metrics, and intelligent insights
- **Server Discovery**: Automatically discover running mock servers and match them with generated configurations
- **Performance Monitoring**: Real-time performance metrics, error rate analysis, and traffic pattern detection
- **AI Assistant Integration**: Optimized for AI-assisted development workflows with structured data output
- **Smart Filtering**: Advanced log filtering by method, path patterns, time ranges, and custom criteria
- **Insights Generation**: Automated analysis with actionable recommendations for debugging and optimization

### 🤖 AI Framework Integration
- **LangGraph Integration**: Native support for LangGraph workflows
- **CrewAI Integration**: Seamless integration with CrewAI multi-agent systems
- **LangChain Integration**: Built-in tools for LangChain applications
- **Dynamic Response Management**: Real-time response updates without server restart
- **Scenario Management**: Create and switch between different test scenarios instantly

## Quick Start

Get started with MockLoop MCP in just a few steps:

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the MCP Server**
   ```bash
   mcp dev src/mockloop_mcp/main.py
   ```

3. **Generate Your First Mock**
   Use the `generate_mock_api` tool with your OpenAPI specification

4. **Start Testing**
   Access your mock server at `http://localhost:8000`

## Documentation Structure

This documentation is organized into several sections:

- **[Getting Started](getting-started/installation.md)**: Installation, configuration, and your first mock server
- **[User Guides](guides/basic-usage.md)**: Comprehensive guides for using all features
- **[AI Integration](ai-integration/overview.md)**: Integration with popular AI frameworks
- **[API Reference](api/mcp-tools.md)**: Complete API documentation and reference
- **[Advanced Topics](advanced/architecture.md)**: Architecture, performance, and troubleshooting
- **[Contributing](contributing/development-setup.md)**: How to contribute to the project

## Latest Version: 2.1.0

The latest version includes major enhancements:

- ✅ **Dynamic Response Management**: Real-time response updates without server restart
- ✅ **Advanced Scenario Management**: Create, switch, and manage test scenarios with persistent storage
- ✅ **Enhanced Performance Monitoring**: Comprehensive performance metrics with session tracking
- ✅ **Database Migration System**: Robust schema versioning and migration framework
- ✅ **Framework Integration**: Native support for LangGraph, CrewAI, and LangChain workflows

## Community and Support

- **GitHub Repository**: [mockloop/mockloop-mcp](https://github.com/mockloop/mockloop-mcp)
- **Issues and Bug Reports**: [GitHub Issues](https://github.com/mockloop/mockloop-mcp/issues)

## License

MockLoop MCP is licensed under the [MIT License](https://github.com/mockloop/mockloop-mcp/blob/main/LICENSE).

---

Ready to get started? Head over to the [Installation Guide](getting-started/installation.md) to begin your journey with MockLoop MCP!