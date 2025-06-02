<div class="hero-section">
  <img src="logo.png" alt="MockLoop Logo" style="height: 64px; margin-bottom: 1rem;">

  <p>A Model Context Protocol server for generating and managing mock API servers with AI-powered testing capabilities.</p>
  <a href="getting-started/installation/" class="cta-button">Get Started →</a>
</div>

## What is MockLoop MCP?

The world's first AI-native API testing platform powered by the Model Context Protocol. Revolutionary AI-driven scenario generation, automated test execution, and intelligent analysis capabilities. MockLoop MCP is a Model Context Protocol server that generates mock API servers from OpenAPI specifications and provides AI-powered testing tools. It includes 50 MCP capabilities for automated testing, scenario management, and audit logging. 

## Core Components

### MCP Tools (16)
- Mock server generation and management
- Test scenario validation and deployment
- Test execution and monitoring
- Result analysis and reporting

### MCP Prompts (5)
- OpenAPI analysis for testing strategies
- Test scenario configuration generation
- Load testing optimization
- Error scenario generation
- Security test generation

### MCP Resources (15)
- Pre-built scenario packs for common testing patterns
- Error simulation scenarios
- Load testing configurations
- Security testing suites

### MCP Context Management (10)
- Test session state management
- Workflow orchestration
- Cross-session data sharing
- State snapshots and rollback

### Audit Logging (4)
- Request/response logging
- Compliance tracking
- Performance metrics
- Security event monitoring

## Key Features

- **Mock Server Generation**: Creates mock servers from OpenAPI v2/v3 specifications
- **MCP Proxy Functionality**: Seamless switching between mock, proxy, and hybrid modes
- **Dual-Port Architecture**: Separate ports for business API (8000) and admin UI (8001)
- **Request Logging**: SQLite-based logging with query capabilities
- **Docker Support**: Containerized deployment with Docker Compose
- **AI Integration**: Compatible with LangGraph, CrewAI, and LangChain

## Quick Start

1. **Install**
   ```bash
   pip install mockloop-mcp
   ```

2. **Run MCP Server**
   ```bash
   mockloop-mcp
   ```

3. **Generate Mock Server**
   Use the `generate_mock_api` tool with your OpenAPI specification

4. **Access Mock Server**
   Mocked API: `http://localhost:8000`
   Admin UI: `http://localhost:8001`

## Add to Claude Code
**Simply run**
`claude mcp add -t stdio mockloop-mcp mockloop-mcp `

Or if using virtual environment:

`claude mcp add -t stdio mockloop-mcp /path/to/venv/bin/mockloop_mcp`


## MCP Proxy Functionality

MockLoop MCP includes powerful proxy capabilities that enable seamless switching between mock and live API environments:

### Proxy Modes
- **Mock Mode**: All requests handled by generated mock responses
- **Proxy Mode**: All requests forwarded to live API endpoints
- **Hybrid Mode**: Intelligent routing between mock and proxy based on rules

### Key Capabilities
- **Universal Authentication**: API Key, Bearer Token, Basic Auth, OAuth2 support
- **Dynamic Routing**: Configure rules to route requests based on patterns and conditions
- **Response Comparison**: Automated comparison between mock and live responses
- **Zero-Downtime Switching**: Change modes without service interruption

### Quick Example
```python
# Create a proxy-enabled plugin
plugin_result = await create_mcp_plugin(
    spec_url_or_path="https://api.example.com/openapi.json",
    mode="hybrid",
    target_url="https://api.example.com",
    auth_config={"auth_type": "bearer_token", "credentials": {"token": "your-token"}}
)
```

**📚 [Complete MCP Proxy Guide](guides/mcp-proxy-guide.md)** - Detailed configuration, examples, and best practices

## Documentation

- **[Getting Started](getting-started/installation.md)**: Installation and basic setup
- **[MCP Proxy Guide](guides/mcp-proxy-guide.md)**: Proxy functionality and configuration
- **[User Guides](guides/basic-usage.md)**: Using MockLoop features
- **[AI Integration](ai-integration/overview.md)**: Integration with AI frameworks
- **[API Reference](api/mcp-tools.md)**: Complete MCP tool documentation
- **[Advanced Topics](advanced/architecture.md)**: Architecture and troubleshooting
- **[Contributing](contributing/development-setup.md)**: Development and contribution guide

## Architecture

### Dual-Port Design
- **Mocked API Port (8000)**: Serves mock API endpoints
- **Admin Port (8001)**: Management interface and logging
- **No Path Conflicts**: Eliminates `/admin` endpoint conflicts

### Database Schema
- **Request Logs**: Complete request/response audit trail
- **Test Sessions**: Stateful test execution tracking
- **Compliance Events**: Regulatory compliance monitoring
- **Performance Metrics**: Response time and throughput data

## Community and Support

- **GitHub**: [mockloop/mockloop-mcp](https://github.com/mockloop/mockloop-mcp)
- **Issues**: [GitHub Issues](https://github.com/mockloop/mockloop-mcp/issues)
- **License**: [MIT License](https://github.com/mockloop/mockloop-mcp/blob/main/LICENSE)

---

Continue to the [Installation Guide](getting-started/installation.md) to set up MockLoop MCP.