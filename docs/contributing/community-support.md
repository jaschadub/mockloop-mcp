# Community Support

This document outlines the various ways to get help, report issues, and engage with the MockLoop MCP community.

## Getting Help

### 📚 Documentation

Start with our comprehensive documentation:

- **[Installation Guide](../getting-started/installation.md)**: Step-by-step installation instructions
- **[Quick Start](../getting-started/quick-start.md)**: Get up and running quickly
- **[API Reference](../api/mcp-tools.md)**: Detailed API documentation
- **[Troubleshooting](../advanced/troubleshooting.md)**: Common issues and solutions

### 💬 Community Channels

#### GitHub Issues
- **Purpose**: Bug reports and specific feature requests
- **Link**: [GitHub Issues](https://github.com/mockloop/mockloop-mcp/issues)
- **Best for**:
  - Bug reports with reproducible steps
  - Specific feature requests
  - Documentation improvements
  - Security vulnerability reports

### 🔍 Search Before Asking

Before creating a new issue:

1. **Search existing issues**: Check if your problem has already been reported
2. **Check documentation**: Review relevant documentation sections
3. **Review examples**: Look through code examples and use cases in the documentation

## Reporting Issues

### 🐛 Bug Reports

When reporting bugs, please use our bug report template and include:

#### Required Information
- **MockLoop MCP Version**: `mockloop-mcp --version`
- **Python Version**: `python --version`
- **Operating System**: OS name and version
- **Installation Method**: PyPI, development, or other

#### Reproduction Steps
1. Clear, numbered steps to reproduce the issue
2. Expected behavior vs. actual behavior
3. Error messages (complete stack traces)
4. Minimal code example if applicable

#### Example Bug Report
```markdown
**Bug Description**
MockLoop MCP fails to generate mock server from OpenAPI spec with circular references.

**To Reproduce**
1. Install mockloop-mcp via pip
2. Use the attached OpenAPI spec (circular-refs.yaml)
3. Run: `generate_mock_api` tool with the spec
4. Error occurs during parsing

**Expected Behavior**
Should generate mock server or provide clear error about unsupported circular references.

**Environment**
- MockLoop MCP Version: 2.1.0
- Python Version: 3.11.5
- OS: Ubuntu 22.04
- Installation: PyPI

**Additional Context**
Spec works fine with other tools like Swagger UI.
```

### 🚨 Security Issues

For security vulnerabilities:

1. **DO NOT** create public issues
2. **Email**: security@mockloop.com
3. **Include**: Detailed description and reproduction steps
4. **Response**: We aim to respond within 48 hours

See our [Security Policy](https://github.com/mockloop/mockloop-mcp/blob/main/.github/SECURITY.md) for more details.

### 📦 PyPI-Related Issues

For PyPI installation or distribution issues:

#### Installation Problems
- **Template**: Use the PyPI Installation Issue template
- **Include**: 
  - Complete pip install command used
  - Full error output
  - Python environment details (`pip list`)
  - Network/proxy configuration if applicable

#### Package Distribution Issues
- **Examples**:
  - Missing files in PyPI package
  - Incorrect metadata
  - Version conflicts
  - Dependency issues

## Feature Requests

### 💡 Suggesting Features

We welcome feature suggestions! Please:

1. **Check existing requests**: Search existing issues first
2. **Use the template**: Follow our feature request template
3. **Provide context**: Explain the use case and problem
4. **Consider alternatives**: Mention any workarounds you've tried

#### Good Feature Request Example
```markdown
**Problem Statement**
As a developer using MockLoop MCP with GraphQL APIs, I need support for GraphQL schema parsing to generate mock servers.

**Proposed Solution**
Add GraphQL schema support to the `generate_mock_api` tool, similar to existing OpenAPI support.

**Use Case**
- Parse GraphQL schema files (.graphql, .gql)
- Generate mock resolvers for queries and mutations
- Support for custom scalar types
- Integration with existing admin UI

**Alternatives Considered**
- Converting GraphQL to OpenAPI (complex and lossy)
- Using separate GraphQL mocking tools (breaks workflow)

**Additional Context**
GraphQL is increasingly popular, and this would make MockLoop MCP more versatile.
```

## Community Guidelines

### 🤝 Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please read and follow our [Code of Conduct](https://github.com/mockloop/mockloop-mcp/blob/main/CODE_OF_CONDUCT.md).

### 💬 Communication Guidelines

#### Be Respectful
- Use inclusive language
- Respect different perspectives and experience levels
- Provide constructive feedback
- Be patient with newcomers

#### Be Helpful
- Provide clear, actionable advice
- Share relevant documentation links
- Offer to help with testing or reproduction
- Acknowledge when you don't know something

#### Be Specific
- Use clear, descriptive titles
- Provide complete information
- Include relevant code examples
- Reference specific documentation sections

### 🏷️ Issue Labels

Understanding our label system helps you find relevant issues:

#### Type Labels
- `bug`: Something isn't working
- `enhancement`: New feature or improvement
- `documentation`: Documentation improvements
- `question`: General questions
- `security`: Security-related issues

#### Priority Labels
- `critical`: Urgent issues affecting many users
- `high`: Important issues for next release
- `medium`: Standard priority
- `low`: Nice-to-have improvements

#### Component Labels
- `core`: Core functionality
- `api`: API-related issues
- `docs`: Documentation
- `pypi`: PyPI distribution
- `tests`: Testing infrastructure

#### Status Labels
- `needs-triage`: Needs initial review
- `needs-reproduction`: Needs reproduction steps
- `in-progress`: Being worked on
- `blocked`: Waiting on external dependency
- `ready-for-review`: Ready for code review

## Contributing Back

### 🛠️ Ways to Contribute

Even if you're not ready to contribute code, you can help:

#### Documentation
- Fix typos and improve clarity
- Add examples and use cases
- Translate documentation
- Create tutorials and guides

#### Testing
- Test new releases and report issues
- Verify bug fixes
- Test on different platforms
- Performance testing

#### Community Support
- Answer questions in issues
- Help with issue triage
- Share your use cases and examples
- Mentor new contributors

#### Code Contributions
- Fix bugs
- Implement new features
- Improve performance
- Add tests

See our [Contributing Guidelines](guidelines.md) for detailed information.

### 🎯 Good First Issues

New contributors should look for:

- Issues labeled `good-first-issue`
- Documentation improvements
- Test additions
- Small bug fixes
- Example additions

## Recognition

### 🏆 Contributor Recognition

We recognize contributors in several ways:

#### Contributors File
All contributors are listed in our CONTRIBUTORS.md file (to be created).

#### Release Notes
Significant contributions are mentioned in release notes with contributor attribution.

#### GitHub Features
- Contributor graphs and statistics
- Issue and PR attribution
- Community insights

#### Special Recognition
Outstanding contributors may be:
- Invited to join the maintainer team
- Featured in community highlights
- Recognized at conferences or events

## Support Channels Summary

| Channel | Purpose | Response Time | Best For |
|---------|---------|---------------|----------|
| GitHub Issues | Bug reports, feature requests, questions | 1-3 days | All support needs |
| Documentation | Self-service help | Immediate | Common questions |
| Security Email | Security vulnerabilities | 48 hours | Security issues |

## Frequently Asked Questions

### Installation and Setup

**Q: How do I install MockLoop MCP?**
A: Use `pip install mockloop-mcp`. See our [Installation Guide](../getting-started/installation.md) for details.

**Q: Which Python versions are supported?**
A: Python 3.9+ is supported, with 3.10+ recommended.

**Q: Can I use MockLoop MCP without Docker?**
A: Yes, Docker is only required for containerized mock servers. You can run mocks directly with Python.

### Usage

**Q: What API specification formats are supported?**
A: Currently OpenAPI v2 (Swagger) and v3 (JSON/YAML). GraphQL and other formats are planned.

**Q: How do I update mock responses dynamically?**
A: Use the `manage_mock_data` tool to update responses without restarting the server.

**Q: Can I use MockLoop MCP in production?**
A: MockLoop MCP is designed for development and testing. For production use, consider proper API gateways.

### Troubleshooting

**Q: MockLoop MCP won't start with my MCP client**
A: Check the configuration path and ensure the command is correct. See [Quick Start](../getting-started/quick-start.md) for examples.

**Q: I'm getting import errors after installation**
A: Verify your Python environment and try reinstalling: `pip uninstall mockloop-mcp && pip install mockloop-mcp`

**Q: The generated mock server returns empty responses**
A: Check your OpenAPI specification for examples or default values. MockLoop MCP uses these for realistic responses.

## Getting Started Checklist

For new community members:

- [ ] Read the [Installation Guide](../getting-started/installation.md)
- [ ] Try the [Quick Start](../getting-started/quick-start.md)
- [ ] Explore the [API Reference](../api/mcp-tools.md) and examples
- [ ] Star the [repository](https://github.com/mockloop/mockloop-mcp) ⭐
- [ ] Follow our [Code of Conduct](https://github.com/mockloop/mockloop-mcp/blob/main/CODE_OF_CONDUCT.md)
- [ ] Consider contributing (see [Contributing Guidelines](guidelines.md))

Welcome to the MockLoop MCP community! 🎉