# Security Policy

## Supported Versions

We actively support the following versions of mockloop-mcp with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take the security of mockloop-mcp seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of the following methods:

1. **Email**: Send details to [jascha@tarnover.com](mailto:jascha@tarnover.com)
2. **GitHub Security Advisories**: Use the [GitHub Security Advisory](https://github.com/mockloop/mockloop-mcp/security/advisories/new) feature

### What to Include

Please include the following information in your report:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

### Response Timeline

We will acknowledge receipt of your vulnerability report within 48 hours and will send a more detailed response within 72 hours indicating the next steps in handling your report.

After the initial reply to your report, we will:

- Confirm the problem and determine the affected versions
- Audit code to find any potential similar problems
- Prepare fixes for all supported releases
- Release patched versions as soon as possible

### Security Update Policy

- **Critical vulnerabilities**: Patches released within 24-48 hours
- **High severity vulnerabilities**: Patches released within 1 week
- **Medium/Low severity vulnerabilities**: Patches included in next regular release

### Disclosure Policy

We follow a coordinated disclosure process:

1. Security issue is reported privately
2. We confirm and analyze the issue
3. We develop and test a fix
4. We prepare a security advisory
5. We release the fix and publish the advisory
6. After 90 days, full details may be disclosed publicly

### Security Best Practices

When using mockloop-mcp, we recommend:

#### For Development
- Always use the latest version
- Keep dependencies up to date
- Use virtual environments
- Enable security scanning in your CI/CD pipeline
- Review generated mock server code before deployment

#### For Production Use
- **Never use mock servers in production environments**
- Mock servers are intended for development and testing only
- If you must use mocks in staging environments, ensure they are:
  - Behind proper authentication
  - Not accessible from public networks
  - Regularly updated and monitored

#### For Generated Mock Servers
- Review generated authentication middleware
- Validate webhook endpoints before use
- Monitor logs for suspicious activity
- Use HTTPS in any network-accessible deployments
- Implement proper access controls

### Security Features

mockloop-mcp includes several security features:

- **Input validation** for API specifications
- **Secure template rendering** with Jinja2
- **Configurable authentication** in generated servers
- **Request logging** for monitoring
- **Dependency scanning** in CI/CD
- **Static analysis** with bandit and semgrep

### Known Security Considerations

- Generated mock servers are for development/testing only
- Default configurations may not be production-ready
- Template injection risks if using untrusted specifications
- Network exposure risks if mock servers are publicly accessible

### Security Contact

For security-related questions or concerns:

- **Primary Contact**: Jascha Wanger ([jascha@tarnover.com](mailto:jascha@tarnover.com))
- **Organization**: Tarnover, LLC
- **Response Time**: Within 48 hours for security issues

### Hall of Fame

We appreciate security researchers who help keep mockloop-mcp secure. Researchers who responsibly disclose security vulnerabilities will be acknowledged here (with their permission).

---

**Note**: This security policy applies to the mockloop-mcp package and its generated code. For security issues in dependencies, please report them to the respective maintainers.

Last updated: May 30, 2025