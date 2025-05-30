# Troubleshooting

This guide helps you diagnose and resolve common issues with MockLoop MCP.

## Common Issues

### Installation Problems

#### Python Version Issues
```bash
# Check Python version
python --version
python3 --version

# Use specific Python version
python3.10 -m venv .venv
```

#### Dependency Conflicts
```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### MCP Server Issues

#### Server Won't Start
```bash
# Check if port is in use
lsof -i :8000

# Check MCP server logs
mcp dev src/mockloop_mcp/main.py --verbose
```

#### Connection Issues
1. Verify MCP client configuration
2. Check file paths in configuration
3. Ensure virtual environment is activated

### Mock Server Issues

#### Generation Failures
- Verify OpenAPI specification is valid
- Check network connectivity for remote specs
- Ensure sufficient disk space

#### Runtime Errors
- Check Docker status
- Verify port availability
- Review server logs

## Getting Help

1. Check this troubleshooting guide
2. Search [GitHub Issues](https://github.com/mockloop/mockloop-mcp/issues)
3. Create a new issue with detailed information

## Diagnostic Commands

```bash
# System information
python --version
docker --version
pip list | grep -E "(fastapi|mkdocs|mcp)"

# Check running processes
ps aux | grep -E "(mkdocs|uvicorn|docker)"

# Check ports
netstat -tulpn | grep -E "(8000|3000|5000)"