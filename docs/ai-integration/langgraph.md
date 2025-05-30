# LangGraph Integration

LangGraph is a powerful framework for building stateful, multi-actor applications with LLMs. MockLoop MCP provides seamless integration with LangGraph, enabling you to test complex state machines and workflows with realistic API interactions.

## Overview

LangGraph applications often require external API calls for data retrieval, service interactions, and state transitions. MockLoop MCP allows you to:

- **Mock External Services**: Replace real APIs with controllable mock servers
- **Test State Transitions**: Verify workflow behavior under different conditions
- **Simulate Failures**: Test error handling and recovery mechanisms
- **Performance Testing**: Evaluate workflow performance with varying API response times

## Installation and Setup

### Prerequisites

```bash
pip install langgraph mockloop-mcp
```

### Basic Integration

```python
from langgraph import StateGraph, END
from mockloop_mcp import MockLoopClient
import asyncio

# Initialize MockLoop client
mockloop = MockLoopClient()

# Generate mock server for your API
await mockloop.generate_mock_api(
    spec_url_or_path="./external-service-api.yaml",
    output_dir_name="langgraph_mock_server"
)
```

## Core Integration Patterns

### Pattern 1: State-Driven API Responses

Configure mock responses based on LangGraph state:

```python
from typing import TypedDict
from langgraph import StateGraph

class WorkflowState(TypedDict):
    user_input: str
    api_data: dict
    processing_stage: str
    result: str

async def fetch_data_node(state: WorkflowState):
    """Node that fetches data from mock API"""
    
    # Configure mock response based on current state
    if state["processing_stage"] == "initial":
        response_data = {
            "status": "processing",
            "data": {"stage": "validation"},
            "next_step": "validate"
        }
    elif state["processing_stage"] == "validation":
        response_data = {
            "status": "ready",
            "data": {"validated": True, "confidence": 0.95},
            "next_step": "complete"
        }
    
    # Update mock server response
    await mockloop.manage_mock_data(
        server_url="http://localhost:8000",
        operation="update_response",
        endpoint_path="/api/process",
        response_data=response_data
    )
    
    # Make API call (will get the configured response)
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/process")
        api_data = response.json()
    
    return {
        **state,
        "api_data": api_data,
        "processing_stage": api_data["data"]["stage"]
    }

# Build the graph
workflow = StateGraph(WorkflowState)
workflow.add_node("fetch_data", fetch_data_node)
workflow.set_entry_point("fetch_data")
workflow.add_edge("fetch_data", END)

app = workflow.compile()
```

### Pattern 2: Multi-Service Workflows

Test workflows that interact with multiple services:

```python
class MultiServiceWorkflow:
    def __init__(self):
        self.mockloop = MockLoopClient()
        self.services = {
            "user_service": "http://localhost:8001",
            "payment_service": "http://localhost:8002",
            "inventory_service": "http://localhost:8003"
        }
    
    async def setup_services(self):
        """Setup mock servers for all services"""
        service_specs = [
            {"spec": "./user-service.yaml", "port": 8001},
            {"spec": "./payment-service.yaml", "port": 8002},
            {"spec": "./inventory-service.yaml", "port": 8003}
        ]
        
        for service in service_specs:
            await self.mockloop.generate_mock_api(
                spec_url_or_path=service["spec"],
                output_dir_name=f"service_{service['port']}"
            )
    
    async def configure_scenario(self, scenario_name: str):
        """Configure all services for a specific scenario"""
        scenarios = {
            "happy_path": {
                "user_service": {"status": "active", "balance": 1000},
                "payment_service": {"status": "available", "processing_time": 100},
                "inventory_service": {"status": "in_stock", "quantity": 50}
            },
            "payment_failure": {
                "user_service": {"status": "active", "balance": 1000},
                "payment_service": {"status": "error", "error": "Payment gateway down"},
                "inventory_service": {"status": "in_stock", "quantity": 50}
            },
            "out_of_stock": {
                "user_service": {"status": "active", "balance": 1000},
                "payment_service": {"status": "available", "processing_time": 100},
                "inventory_service": {"status": "out_of_stock", "quantity": 0}
            }
        }
        
        scenario_config = scenarios[scenario_name]
        for service_name, config in scenario_config.items():
            service_url = self.services[service_name]
            await self.mockloop.manage_mock_data(
                server_url=service_url,
                operation="update_response",
                endpoint_path="/status",
                response_data=config
            )

# Usage in LangGraph workflow
async def check_user_node(state):
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8001/status")
        user_data = response.json()
    
    return {**state, "user_status": user_data}

async def process_payment_node(state):
    if state["user_status"]["status"] != "active":
        return {**state, "payment_result": "user_inactive"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8002/process")
        payment_data = response.json()
    
    return {**state, "payment_result": payment_data}
```

### Pattern 3: Error Handling and Recovery

Test error scenarios and recovery mechanisms:

```python
class ErrorHandlingWorkflow:
    def __init__(self):
        self.mockloop = MockLoopClient()
        self.retry_count = 0
        self.max_retries = 3
    
    async def setup_error_scenarios(self):
        """Setup various error scenarios"""
        error_scenarios = {
            "network_timeout": {
                "/api/data": {"error": "timeout", "status": 408, "delay_ms": 5000}
            },
            "server_error": {
                "/api/data": {"error": "Internal server error", "status": 500}
            },
            "rate_limit": {
                "/api/data": {"error": "Rate limit exceeded", "status": 429}
            },
            "success": {
                "/api/data": {"data": {"result": "success"}, "status": 200}
            }
        }
        
        for scenario_name, config in error_scenarios.items():
            await self.mockloop.manage_mock_data(
                operation="create_scenario",
                scenario_name=scenario_name,
                scenario_config=config
            )
    
    async def api_call_with_retry(self, state):
        """Node that implements retry logic"""
        
        # Start with error scenario
        if self.retry_count == 0:
            await self.mockloop.manage_mock_data(
                operation="switch_scenario",
                scenario_name="network_timeout"
            )
        elif self.retry_count == 1:
            await self.mockloop.manage_mock_data(
                operation="switch_scenario",
                scenario_name="server_error"
            )
        else:
            # Success on final retry
            await self.mockloop.manage_mock_data(
                operation="switch_scenario",
                scenario_name="success"
            )
        
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get("http://localhost:8000/api/data")
                
                if response.status_code == 200:
                    return {**state, "api_result": response.json(), "success": True}
                else:
                    raise httpx.HTTPStatusError(
                        f"HTTP {response.status_code}", 
                        request=response.request, 
                        response=response
                    )
                    
        except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
            self.retry_count += 1
            
            if self.retry_count >= self.max_retries:
                return {**state, "api_result": None, "success": False, "error": str(e)}
            
            # Continue to retry
            return {**state, "retry_count": self.retry_count}
```

## Advanced Integration Features

### Dynamic State Management

Synchronize mock server state with LangGraph state:

```python
class StateSynchronizedMock:
    def __init__(self, mockloop_client, server_url):
        self.mockloop = mockloop_client
        self.server_url = server_url
        self.state_history = []
    
    async def sync_state(self, langgraph_state):
        """Synchronize mock responses with LangGraph state"""
        
        # Track state changes
        self.state_history.append(langgraph_state.copy())
        
        # Generate responses based on state
        if langgraph_state.get("user_authenticated"):
            auth_response = {
                "authenticated": True,
                "user_id": langgraph_state.get("user_id"),
                "permissions": ["read", "write"]
            }
        else:
            auth_response = {
                "authenticated": False,
                "error": "Authentication required"
            }
        
        await self.mockloop.manage_mock_data(
            server_url=self.server_url,
            operation="update_response",
            endpoint_path="/auth/status",
            response_data=auth_response
        )
        
        # Update data endpoints based on processing stage
        stage = langgraph_state.get("processing_stage", "initial")
        data_response = self.generate_stage_response(stage)
        
        await self.mockloop.manage_mock_data(
            server_url=self.server_url,
            operation="update_response",
            endpoint_path="/data/current",
            response_data=data_response
        )
    
    def generate_stage_response(self, stage):
        """Generate appropriate response for processing stage"""
        stage_responses = {
            "initial": {"status": "ready", "data": None},
            "processing": {"status": "processing", "progress": 0.5},
            "validation": {"status": "validating", "progress": 0.8},
            "complete": {"status": "complete", "data": {"result": "processed"}}
        }
        return stage_responses.get(stage, {"status": "unknown"})
```

### Performance Testing

Test LangGraph workflow performance under different conditions:

```python
class PerformanceTester:
    def __init__(self, mockloop_client):
        self.mockloop = mockloop_client
        self.performance_scenarios = {}
    
    async def setup_performance_scenarios(self):
        """Setup scenarios with different response times"""
        self.performance_scenarios = {
            "fast": {"delay_ms": 50, "data": {"size": "small"}},
            "medium": {"delay_ms": 500, "data": {"size": "medium"}},
            "slow": {"delay_ms": 2000, "data": {"size": "large"}},
            "timeout": {"delay_ms": 10000, "data": {"error": "timeout"}}
        }
        
        for scenario_name, config in self.performance_scenarios.items():
            await self.mockloop.manage_mock_data(
                operation="create_scenario",
                scenario_name=f"perf_{scenario_name}",
                scenario_config={"/api/data": config}
            )
    
    async def test_workflow_performance(self, workflow, test_input):
        """Test workflow under different performance conditions"""
        results = {}
        
        for scenario_name in self.performance_scenarios.keys():
            # Switch to performance scenario
            await self.mockloop.manage_mock_data(
                operation="switch_scenario",
                scenario_name=f"perf_{scenario_name}"
            )
            
            # Measure workflow execution time
            start_time = time.time()
            try:
                result = await workflow.ainvoke(test_input)
                execution_time = time.time() - start_time
                
                results[scenario_name] = {
                    "success": True,
                    "execution_time": execution_time,
                    "result": result
                }
            except Exception as e:
                execution_time = time.time() - start_time
                results[scenario_name] = {
                    "success": False,
                    "execution_time": execution_time,
                    "error": str(e)
                }
        
        return results
```

## Testing Strategies

### Unit Testing LangGraph Nodes

Test individual nodes with mock APIs:

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_data_fetch_node():
    """Test data fetching node with mock API"""
    
    # Setup mock server
    mockloop = MockLoopClient()
    await mockloop.generate_mock_api(
        spec_url_or_path="./test-api.yaml",
        output_dir_name="test_mock"
    )
    
    # Configure test response
    test_data = {"id": 123, "name": "test", "status": "active"}
    await mockloop.manage_mock_data(
        server_url="http://localhost:8000",
        operation="update_response",
        endpoint_path="/api/data",
        response_data=test_data
    )
    
    # Test the node
    initial_state = {"user_id": 123, "stage": "fetch"}
    result_state = await fetch_data_node(initial_state)
    
    # Verify results
    assert result_state["api_data"] == test_data
    assert result_state["stage"] == "fetch"

@pytest.mark.asyncio
async def test_error_handling_node():
    """Test node error handling with mock failures"""
    
    mockloop = MockLoopClient()
    
    # Configure error response
    await mockloop.manage_mock_data(
        server_url="http://localhost:8000",
        operation="update_response",
        endpoint_path="/api/data",
        response_data={"error": "Service unavailable", "status": 503}
    )
    
    # Test error handling
    initial_state = {"user_id": 123, "retry_count": 0}
    result_state = await api_call_with_retry(initial_state)
    
    # Verify error handling
    assert result_state["retry_count"] > 0
    assert "error" in result_state or result_state.get("success") is False
```

### Integration Testing

Test complete workflows with realistic scenarios:

```python
@pytest.mark.asyncio
async def test_complete_workflow():
    """Test complete LangGraph workflow with mock services"""
    
    # Setup multi-service environment
    workflow_tester = MultiServiceWorkflow()
    await workflow_tester.setup_services()
    
    # Test happy path scenario
    await workflow_tester.configure_scenario("happy_path")
    
    # Build and run workflow
    workflow = build_complete_workflow()
    initial_state = {
        "user_id": 123,
        "order_items": [{"id": 1, "quantity": 2}],
        "payment_method": "credit_card"
    }
    
    result = await workflow.ainvoke(initial_state)
    
    # Verify successful completion
    assert result["order_status"] == "completed"
    assert result["payment_status"] == "processed"
    assert result["inventory_updated"] is True
    
    # Test failure scenario
    await workflow_tester.configure_scenario("payment_failure")
    result = await workflow.ainvoke(initial_state)
    
    # Verify failure handling
    assert result["order_status"] == "failed"
    assert result["payment_status"] == "error"
```

## Best Practices

### 1. State Management

- **Consistent State**: Keep mock responses consistent with LangGraph state
- **State History**: Track state changes for debugging
- **State Validation**: Validate state transitions in tests

### 2. Error Simulation

- **Realistic Errors**: Use realistic error responses and status codes
- **Progressive Failures**: Test escalating failure scenarios
- **Recovery Testing**: Verify recovery mechanisms work correctly

### 3. Performance Considerations

- **Response Times**: Test with realistic API response times
- **Timeout Handling**: Test timeout scenarios and handling
- **Load Testing**: Test workflow performance under load

### 4. Debugging and Monitoring

- **Request Logging**: Monitor all API interactions
- **State Logging**: Log state changes and transitions
- **Performance Metrics**: Track execution times and bottlenecks

## Example: E-commerce Order Processing

Complete example of LangGraph workflow with MockLoop integration:

```python
from langgraph import StateGraph, END
from typing import TypedDict

class OrderState(TypedDict):
    order_id: str
    user_id: str
    items: list
    payment_status: str
    inventory_status: str
    order_status: str

async def validate_user_node(state: OrderState):
    """Validate user and check account status"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8001/users/{state['user_id']}")
        user_data = response.json()
    
    if user_data["status"] != "active":
        return {**state, "order_status": "user_invalid"}
    
    return {**state, "user_validated": True}

async def check_inventory_node(state: OrderState):
    """Check item availability"""
    async with httpx.AsyncClient() as client:
        for item in state["items"]:
            response = await client.get(f"http://localhost:8003/inventory/{item['id']}")
            inventory = response.json()
            
            if inventory["quantity"] < item["quantity"]:
                return {**state, "inventory_status": "insufficient", "order_status": "failed"}
    
    return {**state, "inventory_status": "available"}

async def process_payment_node(state: OrderState):
    """Process payment"""
    if state.get("order_status") == "failed":
        return state
    
    async with httpx.AsyncClient() as client:
        payment_data = {
            "user_id": state["user_id"],
            "amount": sum(item["price"] * item["quantity"] for item in state["items"])
        }
        response = await client.post("http://localhost:8002/payments", json=payment_data)
        payment_result = response.json()
    
    if payment_result["status"] == "success":
        return {**state, "payment_status": "processed", "order_status": "completed"}
    else:
        return {**state, "payment_status": "failed", "order_status": "failed"}

# Build the workflow
def build_order_workflow():
    workflow = StateGraph(OrderState)
    
    workflow.add_node("validate_user", validate_user_node)
    workflow.add_node("check_inventory", check_inventory_node)
    workflow.add_node("process_payment", process_payment_node)
    
    workflow.set_entry_point("validate_user")
    workflow.add_edge("validate_user", "check_inventory")
    workflow.add_edge("check_inventory", "process_payment")
    workflow.add_edge("process_payment", END)
    
    return workflow.compile()

# Usage
async def main():
    # Setup mock services
    workflow_tester = MultiServiceWorkflow()
    await workflow_tester.setup_services()
    await workflow_tester.configure_scenario("happy_path")
    
    # Run workflow
    workflow = build_order_workflow()
    result = await workflow.ainvoke({
        "order_id": "order_123",
        "user_id": "user_456",
        "items": [{"id": "item_1", "quantity": 2, "price": 29.99}],
        "payment_status": "",
        "inventory_status": "",
        "order_status": "pending"
    })
    
    print(f"Order result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

- **[CrewAI Integration](crewai.md)**: Learn about multi-agent testing
- **[Custom AI Workflows](custom-workflows.md)**: Create custom integration patterns
- **[Performance Monitoring](../guides/performance-monitoring.md)**: Monitor workflow performance

---

LangGraph integration with MockLoop MCP enables comprehensive testing of complex AI workflows. Start with simple state-driven mocks and gradually build more sophisticated testing scenarios as your workflows evolve.