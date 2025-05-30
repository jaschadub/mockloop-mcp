# Release Process

This document outlines the complete release process for MockLoop MCP, including version management, testing procedures, deployment steps, and post-release activities.

## Overview

MockLoop MCP follows a structured release process that ensures quality, stability, and proper communication with users. Our release process includes:

- **Version Planning**: Feature planning and version scoping
- **Development Cycle**: Feature development and integration
- **Pre-Release Testing**: Comprehensive testing and validation
- **Release Preparation**: Documentation, changelog, and packaging
- **Release Deployment**: Publishing and distribution
- **Post-Release Activities**: Monitoring, support, and feedback collection

## Release Types

### Major Releases (X.0.0)

Major releases introduce significant new features, architectural changes, or breaking changes.

**Characteristics:**
- Breaking API changes
- Major new features
- Architectural improvements
- Database schema changes
- Configuration format changes

**Timeline:** Every 6-12 months

**Example Changes:**
- New authentication system
- Database migration to different engine
- API version upgrade
- Major performance improvements

### Minor Releases (X.Y.0)

Minor releases add new features and enhancements while maintaining backward compatibility.

**Characteristics:**
- New features and capabilities
- Performance improvements
- Enhanced existing functionality
- New configuration options
- Backward compatible changes

**Timeline:** Every 1-2 months

**Example Changes:**
- New MCP tools
- Additional API endpoints
- Enhanced logging capabilities
- New integration options

### Patch Releases (X.Y.Z)

Patch releases fix bugs and security issues without adding new features.

**Characteristics:**
- Bug fixes
- Security patches
- Documentation corrections
- Minor performance improvements
- Dependency updates

**Timeline:** As needed (typically 1-2 weeks for critical issues)

**Example Changes:**
- Fix memory leak
- Resolve authentication bug
- Update vulnerable dependency
- Correct documentation errors

## Version Management

### Semantic Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]

Examples:
1.0.0       - Major release
1.1.0       - Minor release
1.1.1       - Patch release
1.2.0-rc.1  - Release candidate
1.2.0-beta.1 - Beta release
1.2.0-alpha.1 - Alpha release
```

### Automated Version Management

We use automated scripts for version management to ensure consistency and reduce errors:

#### Version Bumping Script

```bash
# Bump patch version (1.0.0 -> 1.0.1)
python scripts/bump_version.py patch

# Bump minor version (1.0.1 -> 1.1.0)
python scripts/bump_version.py minor

# Bump major version (1.1.0 -> 2.0.0)
python scripts/bump_version.py major

# Set specific version
python scripts/bump_version.py --version 1.2.3

# Create pre-release version
python scripts/bump_version.py minor --pre-release alpha

# Dry run to see what would change
python scripts/bump_version.py patch --dry-run

# Skip git operations
python scripts/bump_version.py patch --no-git
```

The version bumping script automatically:
- Updates version in `pyproject.toml` and `src/mockloop_mcp/__init__.py`
- Updates `CHANGELOG.md` with new version and date
- Creates git commit and tag
- Validates version consistency across files

#### Version Consistency

Versions are maintained in two locations:
- `pyproject.toml`: `version = "X.Y.Z"`
- `src/mockloop_mcp/__init__.py`: `__version__ = "X.Y.Z"`

The automated tools ensure these stay in sync.

### Branch Strategy

```bash
# Main branches
main        # Production releases
develop     # Integration branch
release/*   # Release preparation

# Supporting branches
feature/*   # New features
bugfix/*    # Bug fixes
hotfix/*    # Critical production fixes

# Release branch example
release/v1.2.0
```

## Release Planning

### Feature Planning

#### 1. Roadmap Review

```markdown
# Release Planning Template

## Version: 1.2.0
## Target Date: 2024-03-15
## Release Type: Minor

### Planned Features
- [ ] Enhanced webhook support
- [ ] New authentication methods
- [ ] Performance improvements
- [ ] Additional MCP tools

### Bug Fixes
- [ ] Fix memory leak in request processing
- [ ] Resolve database connection issues
- [ ] Correct OpenAPI validation

### Documentation Updates
- [ ] API reference updates
- [ ] New integration guides
- [ ] Performance tuning guide

### Breaking Changes
- None (minor release)

### Dependencies
- Feature A depends on Feature B
- Performance improvements require database changes

### Risk Assessment
- Medium: New authentication system
- Low: Additional MCP tools
- High: Database schema changes
```

#### 2. Issue Triage

```bash
# GitHub issue management
# Label issues for release
gh issue list --label "milestone:v1.2.0"

# Assign issues to release milestone
gh issue edit 123 --milestone "v1.2.0"

# Track progress
gh issue list --milestone "v1.2.0" --state open
```

### Release Timeline

#### 6 Weeks Before Release
- [ ] Feature freeze for major features
- [ ] Begin integration testing
- [ ] Update documentation
- [ ] Security review

#### 4 Weeks Before Release
- [ ] Code freeze for new features
- [ ] Comprehensive testing
- [ ] Performance benchmarking
- [ ] Documentation review

#### 2 Weeks Before Release
- [ ] Release candidate creation
- [ ] Community testing
- [ ] Final bug fixes
- [ ] Release notes preparation

#### 1 Week Before Release
- [ ] Final testing
- [ ] Package preparation
- [ ] Deployment preparation
- [ ] Communication planning

## Development Cycle

### Feature Development

```bash
# Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/enhanced-webhooks

# Development workflow
# ... implement feature ...

# Testing
pytest tests/
pytest tests/integration/
pytest tests/e2e/

# Code review
git push origin feature/enhanced-webhooks
# Create pull request to develop

# Merge to develop
git checkout develop
git merge feature/enhanced-webhooks
git push origin develop
```

### Integration Testing

```bash
# Automated integration tests
pytest tests/integration/ --verbose

# Manual integration testing
docker-compose -f docker-compose.test.yml up -d
python scripts/integration_test.py
docker-compose -f docker-compose.test.yml down

# Performance testing
python scripts/performance_test.py
locust -f tests/load/locustfile.py --host=http://localhost:8080
```

### Quality Gates

#### Code Quality
```bash
# Static analysis
flake8 src/ tests/
mypy src/
bandit -r src/

# Code coverage
pytest --cov=mockloop_mcp --cov-report=html --cov-fail-under=80

# Security scanning
safety check
pip-audit
```

#### Performance Benchmarks
```python
# Performance criteria
PERFORMANCE_CRITERIA = {
    "request_throughput": 1000,  # requests/second
    "response_time_p95": 100,    # milliseconds
    "memory_usage_max": 512,     # MB
    "startup_time_max": 10,      # seconds
}

def validate_performance():
    """Validate performance meets criteria."""
    results = run_performance_tests()
    
    for metric, threshold in PERFORMANCE_CRITERIA.items():
        if results[metric] > threshold:
            raise ValueError(f"Performance regression: {metric}")
```

## Pre-Release Testing

### Testing Strategy

#### 1. Automated Testing

```yaml
# .github/workflows/release-testing.yml
name: Release Testing

on:
  push:
    branches: [release/*]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11, 3.12]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -e ".[dev,test]"
      - name: Run tests
        run: |
          pytest tests/unit/ --cov=mockloop_mcp

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - name: Run integration tests
        run: |
          pytest tests/integration/

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - name: Run E2E tests
        run: |
          pytest tests/e2e/ --slow

  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Security scan
        run: |
          pip install bandit safety
          bandit -r src/
          safety check
```

#### 2. Manual Testing

```markdown
# Manual Testing Checklist

## Core Functionality
- [ ] Generate mock server from OpenAPI spec
- [ ] Start and stop mock server
- [ ] Process HTTP requests correctly
- [ ] Log requests to database
- [ ] Admin API functionality

## MCP Integration
- [ ] MCP tools work correctly
- [ ] Tool parameters validation
- [ ] Error handling
- [ ] Resource access

## Authentication & Authorization
- [ ] JWT authentication
- [ ] API key authentication
- [ ] Role-based access control
- [ ] Security headers

## Database Operations
- [ ] Database migrations
- [ ] Data persistence
- [ ] Query performance
- [ ] Backup and restore

## Docker Integration
- [ ] Docker image builds
- [ ] Container startup
- [ ] Environment variables
- [ ] Volume mounting

## Documentation
- [ ] API documentation accuracy
- [ ] Code examples work
- [ ] Installation instructions
- [ ] Configuration examples
```

#### 3. Community Testing

```bash
# Release candidate announcement
# Post to GitHub Discussions, Discord, etc.

# Beta testing program
# Invite community members to test RC

# Feedback collection
# GitHub issues, Discord feedback, surveys
```

## Release Preparation

### Automated Release Preparation

We provide an interactive script to guide release preparation:

```bash
# Run release preparation checks
python scripts/prepare_release.py

# Check specific version
python scripts/prepare_release.py --version 1.2.0

# Run checks only (for CI)
python scripts/prepare_release.py --check-only
```

The preparation script validates:
- Git working directory is clean
- Version consistency across files
- Changelog is updated
- All tests pass
- Security scans are clean
- Dependencies are secure
- Package builds successfully

### Manual Release Branch Creation (Alternative)

```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# Use automated version bumping
python scripts/bump_version.py --version 1.2.0

# Push release branch
git push origin release/v1.2.0
```

### Changelog Generation

```python
# scripts/generate_changelog.py
import subprocess
import re
from datetime import datetime

def generate_changelog(from_tag: str, to_tag: str) -> str:
    """Generate changelog from git commits."""
    
    # Get commits between tags
    cmd = f"git log {from_tag}..{to_tag} --oneline --no-merges"
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    
    commits = result.stdout.strip().split('\n')
    
    # Categorize commits
    features = []
    fixes = []
    docs = []
    chores = []
    
    for commit in commits:
        if commit.startswith('feat'):
            features.append(commit)
        elif commit.startswith('fix'):
            fixes.append(commit)
        elif commit.startswith('docs'):
            docs.append(commit)
        else:
            chores.append(commit)
    
    # Generate changelog
    changelog = f"""
# Changelog

## [{to_tag}] - {datetime.now().strftime('%Y-%m-%d')}

### Added
{format_commits(features)}

### Fixed
{format_commits(fixes)}

### Documentation
{format_commits(docs)}

### Internal
{format_commits(chores)}
"""
    
    return changelog

def format_commits(commits: list) -> str:
    """Format commits for changelog."""
    if not commits:
        return "- No changes"
    
    formatted = []
    for commit in commits:
        # Extract commit message
        match = re.match(r'^[a-f0-9]+ (.+)$', commit)
        if match:
            message = match.group(1)
            formatted.append(f"- {message}")
    
    return '\n'.join(formatted)

if __name__ == "__main__":
    changelog = generate_changelog("v1.1.0", "v1.2.0")
    print(changelog)
```

### Documentation Updates

```bash
# Update version in documentation
find docs/ -name "*.md" -exec sed -i 's/v1\.1\.0/v1.2.0/g' {} \;

# Update API documentation
python scripts/generate_api_docs.py

# Update examples
python scripts/update_examples.py

# Build documentation
mkdocs build

# Validate documentation
mkdocs serve --dev-addr=localhost:8000
# Manual review of documentation
```

### Package Preparation

```python
# setup.py version update
setup(
    name="mockloop-mcp",
    version="1.2.0",
    # ... other configuration
)

# pyproject.toml version update
[tool.poetry]
name = "mockloop-mcp"
version = "1.2.0"

# Docker image preparation
# Update Dockerfile version labels
LABEL version="1.2.0"
LABEL release-date="2024-03-15"
```

## Release Deployment

### Automated Release Workflow

Our release process is fully automated through GitHub Actions. The workflow is triggered when you push a version tag:

```bash
# Use the version bumping script to create a release
python scripts/bump_version.py minor  # This creates the tag

# Push the changes and tag
git push && git push --tags
```

The automated release workflow (`.github/workflows/release.yml`) will:

1. **Run Full Test Suite**: Execute all tests across Python 3.10, 3.11, and 3.12
2. **Security Validation**: Run security scans (Bandit, Safety, pip-audit)
3. **Build Packages**: Create source distribution and wheel
4. **Version Validation**: Ensure tag version matches package version
5. **Create GitHub Release**: Generate release with changelog notes
6. **Upload Artifacts**: Attach build artifacts to the release
7. **Publish to TestPyPI**: Test package publishing and installation
8. **Verify TestPyPI Installation**: Cross-platform installation verification
9. **Publish to PyPI**: Production package publishing
10. **Verify PyPI Installation**: Final cross-platform verification

### PyPI Publishing Process

#### Automatic Publishing (Recommended)

The release workflow automatically publishes to PyPI when you create a version tag:

```bash
# Create and push a version tag
python scripts/bump_version.py minor
git push && git push --tags

# The workflow will automatically:
# 1. Test the package thoroughly
# 2. Publish to TestPyPI for validation
# 3. Verify installation across platforms
# 4. Publish to production PyPI
# 5. Verify final installation
```

#### Manual Publishing

For manual control over publishing, use the manual publishing workflow:

```bash
# Trigger manual publishing workflow
gh workflow run publish.yml \
  --field target=testpypi \
  --field version=1.2.0

# After TestPyPI validation, publish to PyPI
gh workflow run publish.yml \
  --field target=pypi \
  --field version=1.2.0
```

#### Publishing Workflow Features

**TestPyPI Staging:**
- All packages are first published to TestPyPI
- Cross-platform installation verification (Ubuntu, Windows, macOS)
- Python version compatibility testing (3.10, 3.11, 3.12)
- CLI functionality verification

**Production PyPI:**
- Only published after successful TestPyPI verification
- Additional propagation time for global availability
- Final cross-platform verification
- Automatic rollback instructions if issues detected

**Security & Quality Gates:**
- Package validation with `twine check`
- Security scanning before publishing
- Version consistency verification
- Test suite must pass completely

#### PyPI Configuration Requirements

**Repository Secrets:**
```bash
# Required GitHub repository secrets
PYPI_API_TOKEN          # Production PyPI API token
TEST_PYPI_API_TOKEN     # TestPyPI API token
```

**Environment Protection:**
- `pypi` environment: Requires manual approval for production releases
- `testpypi` environment: Automatic for testing

#### Installation Verification

The publishing process includes comprehensive installation verification:

```bash
# Automated verification script
python scripts/verify_installation.py --version 1.2.0

# TestPyPI verification
python scripts/verify_installation.py --testpypi --version 1.2.0

# Generate installation report
python scripts/verify_installation.py --output verification_report.md
```

**Verification Tests:**
- Package installation from PyPI/TestPyPI
- CLI command functionality (`mockloop-mcp --version`, `--help`)
- Python package import verification
- Basic functionality testing (mock server generation)
- Dependency availability verification
- Cross-platform compatibility

#### Troubleshooting PyPI Issues

**Common Issues:**

1. **Version Already Exists**
   ```bash
   # PyPI doesn't allow re-uploading the same version
   # Solution: Bump to next patch version
   python scripts/bump_version.py patch
   ```

2. **Package Validation Errors**
   ```bash
   # Check package locally
   python -m build
   twine check dist/*
   
   # Fix issues and rebuild
   rm -rf dist/ build/
   python -m build
   ```

3. **Installation Failures**
   ```bash
   # Test installation locally
   pip install --index-url https://test.pypi.org/simple/ \
     --extra-index-url https://pypi.org/simple/ \
     mockloop-mcp==1.2.0
   
   # Check dependencies
   pip check
   ```

4. **Propagation Delays**
   ```bash
   # PyPI can take time to propagate globally
   # Wait 2-5 minutes and retry installation
   # Check PyPI project page for availability
   ```

**Rollback Procedures:**

```bash
# PyPI packages cannot be deleted, but can be yanked
twine yank mockloop-mcp 1.2.0 --reason "Critical bug found"

# For critical issues, publish a hotfix immediately
python scripts/bump_version.py patch
git push && git push --tags
```

#### TestPyPI Testing Workflow

Before production release, always test with TestPyPI:

```bash
# 1. Publish to TestPyPI (automatic in release workflow)
# 2. Test installation
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  mockloop-mcp==1.2.0

# 3. Verify functionality
mockloop-mcp --version
python -c "import mockloop_mcp; print('Import successful')"

# 4. Test basic functionality
echo '{"openapi": "3.0.0", "info": {"title": "Test", "version": "1.0.0"}, "paths": {}}' > test_spec.json
mockloop-mcp generate-mock test_spec.json --output test_output

# 5. If all tests pass, proceed to PyPI
```

### Manual Release Process (Fallback)

If you need to create a release manually:

```bash
# Final validation
python scripts/prepare_release.py --check-only

# Create and push tag
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0

# The GitHub Actions workflow will handle the rest
```

### Release Workflow Features

- **Automatic Changelog Extraction**: Pulls release notes from CHANGELOG.md
- **Multi-Python Testing**: Tests on Python 3.10, 3.11, and 3.12
- **Security Validation**: Comprehensive security scanning
- **Package Validation**: Ensures packages are PyPI-ready
- **Artifact Management**: Uploads all build artifacts to GitHub release
- **Pre-release Detection**: Automatically marks pre-release versions

### Documentation Deployment

```bash
# Deploy documentation
mkdocs gh-deploy --force

# Update documentation site
# Automated via GitHub Actions
```

## Post-Release Activities

### Release Announcement

```markdown
# Release Announcement Template

## MockLoop MCP v1.2.0 Released! 🎉

We're excited to announce the release of MockLoop MCP v1.2.0! This release includes several new features, performance improvements, and bug fixes.

### 🚀 New Features
- Enhanced webhook support with custom headers
- New authentication methods (OAuth2, SAML)
- Additional MCP tools for advanced scenarios
- Improved performance monitoring

### 🐛 Bug Fixes
- Fixed memory leak in request processing
- Resolved database connection pool issues
- Corrected OpenAPI validation edge cases

### 📈 Performance Improvements
- 30% faster request processing
- Reduced memory usage
- Improved startup time

### 📚 Documentation
- Updated API reference
- New integration guides
- Performance tuning documentation

### 🔄 Migration Guide
For users upgrading from v1.1.x, please see our migration guide (to be created for actual releases).

### 📦 Installation
```bash
pip install --upgrade mockloop-mcp==1.2.0
```

### 🙏 Thanks
Special thanks to our contributors and community members who helped make this release possible!

### 🔗 Links
- [Release Notes](https://github.com/mockloop/mockloop-mcp/releases/tag/v1.2.0)
- [Documentation](https://mockloop.github.io/mockloop-mcp/)
- Migration Guide (to be created for actual releases)
```

### Monitoring and Support

#### 1. Release Monitoring

```python
# scripts/monitor_release.py
import requests
import time
from datetime import datetime

def monitor_release_health():
    """Monitor release health metrics."""
    
    metrics = {
        "pypi_downloads": get_pypi_downloads(),
        "docker_pulls": get_docker_pulls(),
        "github_issues": get_github_issues(),
        "error_reports": get_error_reports()
    }
    
    # Alert on anomalies
    if metrics["error_reports"] > THRESHOLD:
        send_alert("High error rate detected")
    
    return metrics

def get_pypi_downloads():
    """Get PyPI download statistics."""
    url = "https://pypistats.org/api/packages/mockloop-mcp/recent"
    response = requests.get(url)
    return response.json()

def get_docker_pulls():
    """Get Docker Hub pull statistics."""
    url = "https://hub.docker.com/v2/repositories/mockloop/mockloop-mcp/"
    response = requests.get(url)
    return response.json()["pull_count"]

def get_github_issues():
    """Get GitHub issue statistics."""
    url = "https://api.github.com/repos/mockloop/mockloop-mcp/issues"
    response = requests.get(url)
    return len(response.json())
```

#### 2. User Support

```markdown
# Support Checklist

## Immediate Post-Release (24 hours)
- [ ] Monitor error reports
- [ ] Check community channels for issues
- [ ] Respond to GitHub issues
- [ ] Update documentation if needed

## First Week
- [ ] Collect user feedback
- [ ] Monitor performance metrics
- [ ] Address critical issues
- [ ] Plan hotfix if necessary

## First Month
- [ ] Analyze adoption metrics
- [ ] Collect feature requests
- [ ] Plan next release
- [ ] Update roadmap
```

### Hotfix Process

```bash
# Emergency hotfix process
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/v1.2.1

# Fix critical issue
# ... make changes ...

# Test fix
pytest tests/
pytest tests/integration/

# Use automated version bumping for hotfix
python scripts/bump_version.py patch

# Push changes and tag (triggers automated release)
git push && git push --tags

# Merge back to develop
git checkout develop
git merge main
git push origin develop

# The automated release workflow handles:
# - Package building and validation
# - GitHub release creation
# - Artifact uploads
# - PyPI preparation
```

## Release Metrics

### Success Criteria

```python
# Release success metrics
RELEASE_SUCCESS_CRITERIA = {
    "adoption_rate": 0.7,        # 70% of users upgrade within 30 days
    "error_rate": 0.01,          # Less than 1% error rate
    "performance_regression": 0, # No performance regression
    "critical_issues": 0,        # No critical issues reported
    "documentation_coverage": 0.95, # 95% documentation coverage
}

def evaluate_release_success(version: str) -> bool:
    """Evaluate if release meets success criteria."""
    metrics = collect_release_metrics(version)
    
    for criterion, threshold in RELEASE_SUCCESS_CRITERIA.items():
        if metrics[criterion] < threshold:
            return False
    
    return True
```

### Analytics and Reporting

```python
# scripts/release_analytics.py
def generate_release_report(version: str):
    """Generate comprehensive release report."""
    
    report = {
        "version": version,
        "release_date": get_release_date(version),
        "adoption_metrics": {
            "downloads": get_download_stats(version),
            "active_users": get_active_users(version),
            "upgrade_rate": calculate_upgrade_rate(version)
        },
        "quality_metrics": {
            "bug_reports": count_bug_reports(version),
            "performance": get_performance_metrics(version),
            "user_satisfaction": get_satisfaction_score(version)
        },
        "community_metrics": {
            "github_stars": get_github_stars(),
            "contributors": count_contributors(version),
            "community_feedback": collect_feedback(version)
        }
    }
    
    return report
```

## Continuous Improvement

### Release Retrospective

```markdown
# Release Retrospective Template

## Release: v1.2.0
## Date: 2024-03-15

### What Went Well
- Smooth testing process
- Good community feedback
- No critical issues
- Documentation was comprehensive

### What Could Be Improved
- Release timeline was too aggressive
- Need better performance testing
- Communication could be earlier
- More beta testing needed

### Action Items
- [ ] Extend testing phase by 1 week
- [ ] Implement automated performance regression testing
- [ ] Create release communication template
- [ ] Establish beta testing program

### Metrics
- Time to release: 8 weeks
- Critical issues: 0
- Adoption rate: 75% (30 days)
- User satisfaction: 4.2/5
```

### Process Optimization

```python
# Automation improvements
def automate_release_process():
    """Identify automation opportunities."""
    
    automation_opportunities = [
        "Automated changelog generation",
        "Version bumping automation",
        "Release note generation",
        "Package publishing automation",
        "Documentation deployment",
        "Release announcement posting"
    ]
    
    return automation_opportunities
```

## Conclusion

The release process is critical to maintaining quality and user trust. Key principles:

- **Quality First**: Never compromise on testing and validation
- **Communication**: Keep users informed throughout the process
- **Automation**: Automate repetitive tasks to reduce errors
- **Monitoring**: Continuously monitor release health
- **Improvement**: Learn from each release and improve the process

By following this structured approach, we ensure that each release of MockLoop MCP meets our high standards for quality, reliability, and user experience.

### PyPI Publishing Troubleshooting Guide

#### Common PyPI Issues and Solutions

**1. Authentication Errors**
```bash
# Error: Invalid credentials
# Solution: Check API tokens in repository secrets
# Verify PYPI_API_TOKEN and TEST_PYPI_API_TOKEN are correctly set

# Test token locally (for debugging only)
twine upload --repository testpypi dist/* --username __token__ --password $TEST_PYPI_API_TOKEN
```

**2. Version Conflicts**
```bash
# Error: File already exists
# PyPI doesn't allow re-uploading the same version
# Solution: Bump version and republish
python scripts/bump_version.py patch
git push && git push --tags
```

**3. Package Validation Failures**
```bash
# Check package structure
twine check dist/*

# Common issues:
# - Missing long_description in pyproject.toml
# - Invalid README format
# - Missing required metadata

# Fix and rebuild
rm -rf dist/ build/
python -m build
twine check dist/*
```

**4. Installation Verification Failures**
```bash
# Test installation manually
python scripts/verify_installation.py --testpypi --version 1.2.0

# Common issues:
# - Missing dependencies in pyproject.toml
# - Incorrect entry points configuration
# - Import path issues

# Check package contents
pip show mockloop-mcp
pip show -f mockloop-mcp
```

**5. Cross-Platform Issues**
```bash
# Test on different platforms using GitHub Actions
# Check workflow logs for platform-specific failures

# Common issues:
# - Path separator differences (Windows vs Unix)
# - Case sensitivity issues
# - Binary dependency conflicts
```

**6. Propagation Delays**
```bash
# PyPI can take time to propagate globally
# Wait 2-5 minutes for TestPyPI
# Wait 5-10 minutes for production PyPI

# Check package availability
curl -s https://pypi.org/pypi/mockloop-mcp/1.2.0/json | jq .info.version
curl -s https://test.pypi.org/pypi/mockloop-mcp/1.2.0/json | jq .info.version
```

#### Emergency Procedures

**Critical Bug in Published Version:**
```bash
# 1. Yank the problematic version (doesn't delete, but discourages installation)
twine yank mockloop-mcp 1.2.0 --reason "Critical security vulnerability"

# 2. Immediately prepare hotfix
git checkout main
git checkout -b hotfix/v1.2.1
# Fix the issue
python scripts/bump_version.py patch
git push && git push --tags

# 3. Communicate with users
# - Update GitHub release notes
# - Post security advisory if needed
# - Notify community channels
```

**Rollback Procedures:**
```bash
# PyPI packages cannot be deleted, only yanked
# For critical issues:

# 1. Yank problematic version
twine yank mockloop-mcp 1.2.0

# 2. Publish fixed version immediately
python scripts/bump_version.py patch
git push && git push --tags

# 3. Update documentation
# - Add migration notes
# - Update installation instructions
# - Document breaking changes
```

#### Monitoring and Alerts

**Release Health Monitoring:**
```bash
# Monitor download statistics
python scripts/verify_installation.py --version 1.2.0 --output health_report.md

# Check for issues
gh issue list --label "bug" --label "pypi"
gh issue list --label "installation"

# Monitor community channels
# - GitHub Discussions
# - Discord/Slack channels
# - Stack Overflow tags
```

**Automated Monitoring:**
- GitHub Actions workflow monitors installation success
- Cross-platform verification runs automatically
- Community issue tracking for installation problems
- Download statistics and adoption metrics

## See Also

- **[Development Setup](development-setup.md)**: Setting up your development environment
- **[Contributing Guidelines](guidelines.md)**: Code standards and contribution process
- **[Testing Guide](testing.md)**: Comprehensive testing practices
- **[Installation Verification Script](https://github.com/mockloop/mockloop-mcp/blob/main/scripts/verify_installation.py)**: Automated installation testing
- **[PyPI Project Page](https://pypi.org/project/mockloop-mcp/)**: Official package distribution