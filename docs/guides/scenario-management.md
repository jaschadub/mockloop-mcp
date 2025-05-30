# Scenario Management

MockLoop's scenario management system allows you to create, manage, and switch between different response configurations for comprehensive testing of your applications.

## Overview

Scenarios in MockLoop enable you to:

- **Define different response behaviors** for the same endpoints
- **Switch between test scenarios** dynamically
- **Create realistic testing environments** with varying data states
- **Test error conditions** and edge cases
- **Simulate different system states** (maintenance, high load, etc.)

## Understanding Scenarios

### What is a Scenario?

A scenario is a named configuration that defines:

- **Response data** for specific endpoints
- **Response delays** and timing behavior
- **Error conditions** and status codes
- **Dynamic behavior** rules

### Default Scenario

Every mock server starts with a "default" scenario based on your OpenAPI specification:

```python
from mockloop_mcp import manage_mock_data

# List available scenarios
scenarios = manage_mock_data(
    server_url="http://localhost:8000",
    operation="list_scenarios"
)

print("Available scenarios:", scenarios['scenarios'])
# Output: ['default', 'error_testing', 'performance_test']
```

## Creating Scenarios

### Basic Scenario Creation

Create a new scenario with custom responses:

```python
# Create a new scenario
manage_mock_data(
    server_url="http://localhost:8000",
    operation="create_scenario",
    scenario_name="user_testing",
    scenario_config={
        "description": "Scenario for user management testing",
        "endpoints": {
            "/api/users": {
                "GET": {
                    "response": {
                        "users": [
                            {"id": 1, "name": "Alice", "email": "alice@test.com"},
                            {"id": 2, "name": "Bob", "email": "bob@test.com"}
                        ]
                    },
                    "status_code": 200,
                    "delay_ms": 100
                }
            },
            "/api/users/{user_id}": {
                "GET": {
                    "response": {
                        "id": 1,
                        "name": "Alice",
                        "email": "alice@test.com",
                        "created_at": "2024-01-01T00:00:00Z"
                    },
                    "status_code": 200
                }
            }
        }
    }
)
```

### Error Testing Scenarios

Create scenarios to test error conditions:

```python
# Create error testing scenario
manage_mock_data(
    server_url="http://localhost:8000",
    operation="create_scenario",
    scenario_name="error_testing",
    scenario_config={
        "description": "Test various error conditions",
        "endpoints": {
            "/api/users": {
                "GET": {
                    "response": {"error": "Internal server error"},
                    "status_code": 500,
                    "delay_ms": 50
                },
                "POST": {
                    "response": {"error": "Validation failed", "details": "Email already exists"},
                    "status_code": 400
                }
            },
            "/api/users/{user_id}": {
                "GET": {
                    "response": {"error": "User not found"},
                    "status_code": 404
                },
                "DELETE": {
                    "response": {"error": "Forbidden"},
                    "status_code": 403
                }
            }
        }
    }
)
```

### Performance Testing Scenarios

Create scenarios with realistic delays:

```python
# Create performance testing scenario
manage_mock_data(
    server_url="http://localhost:8000",
    operation="create_scenario",
    scenario_name="slow_responses",
    scenario_config={
        "description": "Simulate slow network conditions",
        "global_delay_ms": 2000,  # Add 2 second delay to all responses
        "endpoints": {
            "/api/users": {
                "GET": {
                    "delay_ms": 5000,  # Extra slow for this endpoint
                    "response": {"users": []}
                }
            }
        }
    }
)
```

## Switching Scenarios

### Active Scenario Management

Switch between scenarios at runtime:

```python
# Switch to error testing scenario
manage_mock_data(
    server_url="http://localhost:8000",
    operation="switch_scenario",
    scenario_name="error_testing"
)

# Verify the switch
current = manage_mock_data(
    server_url="http://localhost:8000",
    operation="get_current_scenario"
)
print(f"Current scenario: {current['scenario_name']}")
```

### Scenario Switching via API

You can also switch scenarios using direct HTTP calls:

```bash
# Switch scenario via REST API
curl -X POST http://localhost:8000/admin/scenarios/switch \
  -H "Content-Type: application/json" \
  -d '{"scenario_name": "user_testing"}'

# Get current scenario
curl http://localhost:8000/admin/scenarios/current
```

## Advanced Scenario Features

### Dynamic Response Rules

Create scenarios with conditional logic:

```python
# Scenario with dynamic responses based on request data
manage_mock_data(
    server_url="http://localhost:8000",
    operation="create_scenario",
    scenario_name="dynamic_responses",
    scenario_config={
        "description": "Dynamic responses based on request",
        "endpoints": {
            "/api/users": {
                "POST": {
                    "rules": [
                        {
                            "condition": "request.json.email == 'admin@test.com'",
                            "response": {"error": "Admin email not allowed"},
                            "status_code": 400
                        },
                        {
                            "condition": "len(request.json.name) < 2",
                            "response": {"error": "Name too short"},
                            "status_code": 400
                        },
                        {
                            "default": True,
                            "response": {
                                "id": "{{random_int(1, 1000)}}",
                                "name": "{{request.json.name}}",
                                "email": "{{request.json.email}}",
                                "created_at": "{{now()}}"
                            },
                            "status_code": 201
                        }
                    ]
                }
            }
        }
    }
)
```

### Template Variables

Use template variables for dynamic content:

```python
# Scenario with template variables
scenario_config = {
    "endpoints": {
        "/api/users/{user_id}": {
            "GET": {
                "response": {
                    "id": "{{path.user_id}}",
                    "name": "User {{path.user_id}}",
                    "email": "user{{path.user_id}}@test.com",
                    "created_at": "{{now()}}",
                    "random_score": "{{random_int(1, 100)}}"
                }
            }
        }
    }
}
```

### Stateful Scenarios

Create scenarios that maintain state across requests:

```python
# Stateful scenario with in-memory storage
manage_mock_data(
    server_url="http://localhost:8000",
    operation="create_scenario",
    scenario_name="stateful_testing",
    scenario_config={
        "description": "Maintain state across requests",
        "state_enabled": True,
        "endpoints": {
            "/api/users": {
                "GET": {
                    "response": "{{state.users or []}}"
                },
                "POST": {
                    "actions": [
                        "state.users = state.users or []",
                        "new_user = {**request.json, 'id': len(state.users) + 1}",
                        "state.users.append(new_user)"
                    ],
                    "response": "{{new_user}}",
                    "status_code": 201
                }
            }
        }
    }
)
```

## Scenario Inheritance

### Base Scenarios

Create base scenarios that can be extended:

```python
# Create base scenario
manage_mock_data(
    server_url="http://localhost:8000",
    operation="create_scenario",
    scenario_name="base_api",
    scenario_config={
        "description": "Base API responses",
        "endpoints": {
            "/api/health": {
                "GET": {
                    "response": {"status": "healthy"},
                    "status_code": 200
                }
            }
        }
    }
)

# Create scenario that inherits from base
manage_mock_data(
    server_url="http://localhost:8000",
    operation="create_scenario",
    scenario_name="extended_api",
    scenario_config={
        "description": "Extended API with additional endpoints",
        "inherits_from": "base_api",
        "endpoints": {
            "/api/users": {
                "GET": {
                    "response": {"users": []},
                    "status_code": 200
                }
            }
        }
    }
)
```

## Scenario Testing Workflows

### Automated Scenario Testing

Create test suites that use different scenarios:

```python
import requests
from mockloop_mcp import manage_mock_data

def test_user_scenarios():
    base_url = "http://localhost:8000"
    
    # Test normal scenario
    manage_mock_data(base_url, "switch_scenario", scenario_name="user_testing")
    response = requests.get(f"{base_url}/api/users")
    assert response.status_code == 200
    assert len(response.json()["users"]) == 2
    
    # Test error scenario
    manage_mock_data(base_url, "switch_scenario", scenario_name="error_testing")
    response = requests.get(f"{base_url}/api/users")
    assert response.status_code == 500
    
    # Test performance scenario
    manage_mock_data(base_url, "switch_scenario", scenario_name="slow_responses")
    import time
    start = time.time()
    response = requests.get(f"{base_url}/api/users")
    duration = time.time() - start
    assert duration > 2.0  # Should be slow
```

### CI/CD Integration

Use scenarios in continuous integration:

```yaml
# .github/workflows/api-tests.yml
name: API Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Start MockLoop server
        run: |
          mockloop generate-mock-api openapi.yaml
          cd generated_mock_server && python main.py &
          
      - name: Test normal scenarios
        run: |
          python -c "
          from mockloop_mcp import manage_mock_data
          manage_mock_data('http://localhost:8000', 'switch_scenario', scenario_name='default')
          "
          pytest tests/test_normal_flow.py
          
      - name: Test error scenarios
        run: |
          python -c "
          from mockloop_mcp import manage_mock_data
          manage_mock_data('http://localhost:8000', 'switch_scenario', scenario_name='error_testing')
          "
          pytest tests/test_error_handling.py
```

## Scenario Management Best Practices

### Naming Conventions

Use clear, descriptive scenario names:

- `default` - Standard API responses
- `error_testing` - Various error conditions
- `performance_slow` - Slow response testing
- `user_empty_state` - No users in system
- `user_full_state` - System with many users
- `maintenance_mode` - System under maintenance

### Scenario Documentation

Document your scenarios:

```python
scenario_config = {
    "description": "User management testing scenario",
    "purpose": "Test user CRUD operations with realistic data",
    "test_cases": [
        "User creation with valid data",
        "User retrieval by ID",
        "User list pagination"
    ],
    "notes": "Uses 2 test users: Alice and Bob",
    "endpoints": {
        # ... endpoint configurations
    }
}
```

### Version Control

Store scenario configurations in version control:

```bash
# Export scenarios to files
mkdir scenarios
python -c "
from mockloop_mcp import manage_mock_data
import json

scenarios = manage_mock_data('http://localhost:8000', 'list_scenarios')
for scenario in scenarios['scenarios']:
    config = manage_mock_data('http://localhost:8000', 'get_scenario', scenario_name=scenario)
    with open(f'scenarios/{scenario}.json', 'w') as f:
        json.dump(config, f, indent=2)
"
```

## Troubleshooting Scenarios

### Common Issues

1. **Scenario not switching**: Check scenario name spelling
2. **Template errors**: Validate template syntax
3. **State not persisting**: Ensure state_enabled is true
4. **Performance issues**: Review complex rules and templates

### Debugging Scenarios

Enable debug logging for scenario operations:

```python
# Enable debug mode
manage_mock_data(
    server_url="http://localhost:8000",
    operation="configure_debug",
    config={"scenario_debug": True}
)

# Check scenario logs
logs = query_mock_logs(
    server_url="http://localhost:8000",
    include_admin=True,
    path_pattern="/admin/scenarios/*"
)
```

## Next Steps

- [Performance Monitoring](performance-monitoring.md) - Monitor scenario performance
- [Docker Integration](docker-integration.md) - Deploy scenarios in containers
- [Advanced Features](advanced-features.md) - Explore advanced scenario capabilities