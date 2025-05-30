# Custom AI Workflows

MockLoop MCP provides a flexible foundation for creating custom AI workflow integrations beyond the standard frameworks. This guide covers patterns, techniques, and best practices for integrating MockLoop with custom AI systems, proprietary frameworks, and specialized workflows.

## Overview

Custom AI workflows often have unique requirements that don't fit standard frameworks. MockLoop MCP enables:

- **Framework-Agnostic Integration**: Work with any AI system that makes HTTP requests
- **Custom Protocol Support**: Adapt to proprietary communication protocols
- **Specialized Testing Scenarios**: Create domain-specific testing patterns
- **Hybrid Architectures**: Integrate multiple AI systems and frameworks
- **Legacy System Integration**: Connect with existing AI infrastructure

## Core Integration Principles

### 1. HTTP-Based Integration

Most AI systems communicate via HTTP APIs, making integration straightforward:

```python
from mockloop_mcp import MockLoopClient
import asyncio
import httpx

class CustomAIWorkflow:
    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.mockloop = MockLoopClient()
        self.services = {}
        self.workflow_state = {}
    
    async def register_service(self, service_name: str, spec_path: str, port: int):
        """Register a mock service for the workflow"""
        await self.mockloop.generate_mock_api(
            spec_url_or_path=spec_path,
            output_dir_name=f"{self.workflow_name}_{service_name}"
        )
        
        self.services[service_name] = f"http://localhost:{port}"
    
    async def configure_workflow_scenario(self, scenario_name: str, scenario_config: dict):
        """Configure a complete workflow scenario"""
        for service_name, service_config in scenario_config.items():
            if service_name in self.services:
                service_url = self.services[service_name]
                
                for endpoint, response_data in service_config.items():
                    await self.mockloop.manage_mock_data(
                        server_url=service_url,
                        operation="update_response",
                        endpoint_path=endpoint,
                        response_data=response_data
                    )
    
    async def execute_workflow_step(self, step_name: str, step_config: dict):
        """Execute a single workflow step"""
        service_name = step_config["service"]
        endpoint = step_config["endpoint"]
        method = step_config.get("method", "GET")
        data = step_config.get("data", {})
        
        if service_name not in self.services:
            raise ValueError(f"Service {service_name} not registered")
        
        service_url = self.services[service_name]
        
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(f"{service_url}{endpoint}")
            elif method.upper() == "POST":
                response = await client.post(f"{service_url}{endpoint}", json=data)
            elif method.upper() == "PUT":
                response = await client.put(f"{service_url}{endpoint}", json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
        
        result = {
            "step": step_name,
            "status_code": response.status_code,
            "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            "success": 200 <= response.status_code < 300
        }
        
        # Update workflow state
        self.workflow_state[step_name] = result
        
        return result
```

### 2. State-Driven Workflows

Create workflows that adapt based on current state:

```python
class StateDrivenAIWorkflow:
    def __init__(self, workflow_definition: dict):
        self.workflow_definition = workflow_definition
        self.mockloop = MockLoopClient()
        self.current_state = "initial"
        self.state_history = []
        self.context = {}
    
    async def setup_workflow(self):
        """Setup all services defined in the workflow"""
        for service_name, service_config in self.workflow_definition["services"].items():
            await self.mockloop.generate_mock_api(
                spec_url_or_path=service_config["spec"],
                output_dir_name=f"workflow_{service_name}"
            )
    
    async def transition_to_state(self, new_state: str, context_updates: dict = None):
        """Transition workflow to a new state"""
        if new_state not in self.workflow_definition["states"]:
            raise ValueError(f"Unknown state: {new_state}")
        
        # Update context
        if context_updates:
            self.context.update(context_updates)
        
        # Record state transition
        self.state_history.append({
            "from_state": self.current_state,
            "to_state": new_state,
            "timestamp": time.time(),
            "context": self.context.copy()
        })
        
        self.current_state = new_state
        
        # Configure mock services for new state
        state_config = self.workflow_definition["states"][new_state]
        await self.configure_state_services(state_config)
    
    async def configure_state_services(self, state_config: dict):
        """Configure mock services for current state"""
        for service_name, service_responses in state_config.get("services", {}).items():
            service_url = f"http://localhost:{self.workflow_definition['services'][service_name]['port']}"
            
            for endpoint, response_template in service_responses.items():
                # Process response template with current context
                response_data = self.process_response_template(response_template, self.context)
                
                await self.mockloop.manage_mock_data(
                    server_url=service_url,
                    operation="update_response",
                    endpoint_path=endpoint,
                    response_data=response_data
                )
    
    def process_response_template(self, template: dict, context: dict) -> dict:
        """Process response template with context variables"""
        import json
        
        # Convert template to string, substitute variables, convert back
        template_str = json.dumps(template)
        
        for key, value in context.items():
            template_str = template_str.replace(f"${{{key}}}", str(value))
        
        return json.loads(template_str)
    
    async def execute_state_actions(self):
        """Execute actions defined for current state"""
        state_config = self.workflow_definition["states"][self.current_state]
        actions = state_config.get("actions", [])
        
        results = []
        for action in actions:
            result = await self.execute_action(action)
            results.append(result)
            
            # Check for state transitions based on action results
            if result.get("trigger_transition"):
                next_state = result["trigger_transition"]
                await self.transition_to_state(next_state, result.get("context_updates", {}))
        
        return results
    
    async def execute_action(self, action: dict):
        """Execute a single action"""
        action_type = action["type"]
        
        if action_type == "api_call":
            return await self.execute_api_call_action(action)
        elif action_type == "condition_check":
            return await self.execute_condition_check(action)
        elif action_type == "data_transform":
            return await self.execute_data_transform(action)
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    async def execute_api_call_action(self, action: dict):
        """Execute API call action"""
        service_name = action["service"]
        endpoint = action["endpoint"]
        method = action.get("method", "GET")
        
        service_config = self.workflow_definition["services"][service_name]
        service_url = f"http://localhost:{service_config['port']}"
        
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(f"{service_url}{endpoint}")
            elif method.upper() == "POST":
                data = action.get("data", {})
                # Process data template with context
                processed_data = self.process_response_template(data, self.context)
                response = await client.post(f"{service_url}{endpoint}", json=processed_data)
        
        result = {
            "action": action["name"],
            "type": "api_call",
            "status_code": response.status_code,
            "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            "success": 200 <= response.status_code < 300
        }
        
        # Check for transition conditions
        if "transition_on_success" in action and result["success"]:
            result["trigger_transition"] = action["transition_on_success"]
        elif "transition_on_failure" in action and not result["success"]:
            result["trigger_transition"] = action["transition_on_failure"]
        
        return result

# Example workflow definition
ml_pipeline_workflow = {
    "services": {
        "data_service": {"spec": "./data-api.yaml", "port": 8001},
        "model_service": {"spec": "./model-api.yaml", "port": 8002},
        "validation_service": {"spec": "./validation-api.yaml", "port": 8003}
    },
    "states": {
        "initial": {
            "services": {
                "data_service": {
                    "/status": {"status": "ready", "data_available": True}
                }
            },
            "actions": [
                {
                    "name": "check_data_availability",
                    "type": "api_call",
                    "service": "data_service",
                    "endpoint": "/status",
                    "transition_on_success": "data_loading"
                }
            ]
        },
        "data_loading": {
            "services": {
                "data_service": {
                    "/data": {"data": "${data_batch}", "size": "${batch_size}"}
                }
            },
            "actions": [
                {
                    "name": "load_data_batch",
                    "type": "api_call",
                    "service": "data_service",
                    "endpoint": "/data",
                    "transition_on_success": "model_training"
                }
            ]
        },
        "model_training": {
            "services": {
                "model_service": {
                    "/train": {"status": "training", "progress": "${training_progress}"},
                    "/status": {"status": "training", "epoch": "${current_epoch}"}
                }
            },
            "actions": [
                {
                    "name": "start_training",
                    "type": "api_call",
                    "service": "model_service",
                    "endpoint": "/train",
                    "method": "POST",
                    "data": {"batch_size": "${batch_size}", "epochs": "${max_epochs}"},
                    "transition_on_success": "model_validation"
                }
            ]
        },
        "model_validation": {
            "services": {
                "validation_service": {
                    "/validate": {"accuracy": "${model_accuracy}", "status": "complete"}
                }
            },
            "actions": [
                {
                    "name": "validate_model",
                    "type": "api_call",
                    "service": "validation_service",
                    "endpoint": "/validate",
                    "method": "POST",
                    "transition_on_success": "complete"
                }
            ]
        },
        "complete": {
            "services": {},
            "actions": []
        }
    }
}
```

### 3. Event-Driven Workflows

Create workflows that respond to events and webhooks:

```python
import asyncio
from typing import Dict, List, Callable

class EventDrivenAIWorkflow:
    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.mockloop = MockLoopClient()
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.webhook_servers = {}
        self.event_queue = asyncio.Queue()
        self.running = False
    
    async def setup_webhook_service(self, service_name: str, port: int):
        """Setup webhook service for receiving events"""
        await self.mockloop.generate_mock_api(
            spec_url_or_path="./webhook-api.yaml",
            output_dir_name=f"{self.workflow_name}_webhook_{service_name}"
        )
        
        self.webhook_servers[service_name] = f"http://localhost:{port}"
        
        # Configure webhook endpoint to capture events
        await self.mockloop.manage_mock_data(
            server_url=self.webhook_servers[service_name],
            operation="update_response",
            endpoint_path="/webhook",
            response_data={"status": "received", "timestamp": "{{timestamp}}"}
        )
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register handler for specific event type"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
    
    async def emit_event(self, event_type: str, event_data: dict):
        """Emit an event to the workflow"""
        event = {
            "type": event_type,
            "data": event_data,
            "timestamp": time.time()
        }
        
        await self.event_queue.put(event)
    
    async def start_event_processing(self):
        """Start processing events from the queue"""
        self.running = True
        
        while self.running:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                await self.process_event(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error processing event: {e}")
    
    async def process_event(self, event: dict):
        """Process a single event"""
        event_type = event["type"]
        
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    print(f"Error in event handler: {e}")
    
    async def stop_event_processing(self):
        """Stop event processing"""
        self.running = False

# Example event-driven workflow
class AIModelMonitoringWorkflow(EventDrivenAIWorkflow):
    def __init__(self):
        super().__init__("ai_model_monitoring")
        self.model_metrics = {}
        self.alert_thresholds = {
            "accuracy": 0.85,
            "latency_ms": 1000,
            "error_rate": 0.05
        }
    
    async def setup(self):
        """Setup monitoring workflow"""
        await self.setup_webhook_service("metrics", 8001)
        await self.setup_webhook_service("alerts", 8002)
        
        # Register event handlers
        self.register_event_handler("model_prediction", self.handle_prediction_event)
        self.register_event_handler("model_error", self.handle_error_event)
        self.register_event_handler("performance_metric", self.handle_metric_event)
    
    async def handle_prediction_event(self, event: dict):
        """Handle model prediction events"""
        prediction_data = event["data"]
        model_id = prediction_data["model_id"]
        
        # Update model metrics
        if model_id not in self.model_metrics:
            self.model_metrics[model_id] = {
                "predictions": 0,
                "errors": 0,
                "total_latency": 0
            }
        
        metrics = self.model_metrics[model_id]
        metrics["predictions"] += 1
        metrics["total_latency"] += prediction_data.get("latency_ms", 0)
        
        # Check for performance issues
        avg_latency = metrics["total_latency"] / metrics["predictions"]
        if avg_latency > self.alert_thresholds["latency_ms"]:
            await self.emit_event("performance_alert", {
                "model_id": model_id,
                "alert_type": "high_latency",
                "value": avg_latency,
                "threshold": self.alert_thresholds["latency_ms"]
            })
    
    async def handle_error_event(self, event: dict):
        """Handle model error events"""
        error_data = event["data"]
        model_id = error_data["model_id"]
        
        if model_id in self.model_metrics:
            self.model_metrics[model_id]["errors"] += 1
            
            # Calculate error rate
            metrics = self.model_metrics[model_id]
            error_rate = metrics["errors"] / metrics["predictions"]
            
            if error_rate > self.alert_thresholds["error_rate"]:
                await self.emit_event("performance_alert", {
                    "model_id": model_id,
                    "alert_type": "high_error_rate",
                    "value": error_rate,
                    "threshold": self.alert_thresholds["error_rate"]
                })
    
    async def handle_metric_event(self, event: dict):
        """Handle performance metric events"""
        metric_data = event["data"]
        
        # Configure mock responses based on metrics
        if metric_data["metric_type"] == "accuracy":
            accuracy = metric_data["value"]
            
            if accuracy < self.alert_thresholds["accuracy"]:
                # Configure alert service to return alert
                await self.mockloop.manage_mock_data(
                    server_url=self.webhook_servers["alerts"],
                    operation="update_response",
                    endpoint_path="/alert",
                    response_data={
                        "alert": True,
                        "type": "low_accuracy",
                        "model_id": metric_data["model_id"],
                        "accuracy": accuracy
                    }
                )
```

## Advanced Integration Patterns

### 1. Multi-Framework Orchestration

Orchestrate multiple AI frameworks in a single workflow:

```python
class MultiFrameworkOrchestrator:
    def __init__(self):
        self.mockloop = MockLoopClient()
        self.frameworks = {}
        self.data_flow = {}
    
    async def register_framework(self, framework_name: str, framework_config: dict):
        """Register an AI framework with its mock services"""
        self.frameworks[framework_name] = framework_config
        
        # Setup mock services for framework
        for service_name, service_config in framework_config["services"].items():
            await self.mockloop.generate_mock_api(
                spec_url_or_path=service_config["spec"],
                output_dir_name=f"{framework_name}_{service_name}"
            )
    
    async def configure_data_flow(self, flow_definition: dict):
        """Configure data flow between frameworks"""
        self.data_flow = flow_definition
        
        # Setup data transformation endpoints
        for step_name, step_config in flow_definition["steps"].items():
            source_framework = step_config["source_framework"]
            target_framework = step_config["target_framework"]
            
            # Configure mock endpoints for data transformation
            await self.setup_data_transformation(step_name, step_config)
    
    async def setup_data_transformation(self, step_name: str, step_config: dict):
        """Setup data transformation between frameworks"""
        transform_service_url = f"http://localhost:{step_config['transform_port']}"
        
        # Generate transformation service
        await self.mockloop.generate_mock_api(
            spec_url_or_path="./data-transform-api.yaml",
            output_dir_name=f"transform_{step_name}"
        )
        
        # Configure transformation logic
        await self.mockloop.manage_mock_data(
            server_url=transform_service_url,
            operation="update_response",
            endpoint_path="/transform",
            response_data={
                "transformed_data": step_config["transformation_template"],
                "source_format": step_config["source_format"],
                "target_format": step_config["target_format"]
            }
        )
    
    async def execute_orchestrated_workflow(self, workflow_input: dict):
        """Execute workflow across multiple frameworks"""
        results = {}
        current_data = workflow_input
        
        for step_name in self.data_flow["execution_order"]:
            step_config = self.data_flow["steps"][step_name]
            
            # Execute step
            step_result = await self.execute_framework_step(
                step_name, step_config, current_data
            )
            
            results[step_name] = step_result
            
            # Update current data for next step
            if step_result["success"]:
                current_data = step_result["output_data"]
            else:
                # Handle step failure
                break
        
        return results
    
    async def execute_framework_step(self, step_name: str, step_config: dict, input_data: dict):
        """Execute a single framework step"""
        framework_name = step_config["framework"]
        framework_config = self.frameworks[framework_name]
        
        # Call framework service
        service_url = f"http://localhost:{framework_config['services']['main']['port']}"
        endpoint = step_config["endpoint"]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{service_url}{endpoint}",
                json=input_data
            )
        
        if response.status_code == 200:
            output_data = response.json()
            
            # Apply data transformation if needed
            if "transform_to" in step_config:
                output_data = await self.transform_data(
                    output_data,
                    step_config["transform_to"]
                )
            
            return {
                "step": step_name,
                "framework": framework_name,
                "success": True,
                "output_data": output_data
            }
        else:
            return {
                "step": step_name,
                "framework": framework_name,
                "success": False,
                "error": response.text
            }
    
    async def transform_data(self, data: dict, transform_config: dict):
        """Transform data between framework formats"""
        transform_service_url = f"http://localhost:{transform_config['port']}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{transform_service_url}/transform",
                json={"data": data, "config": transform_config}
            )
        
        if response.status_code == 200:
            return response.json()["transformed_data"]
        else:
            raise Exception(f"Data transformation failed: {response.text}")

# Example multi-framework workflow
nlp_pipeline_config = {
    "frameworks": {
        "preprocessing": {
            "services": {
                "main": {"spec": "./preprocessing-api.yaml", "port": 8001}
            }
        },
        "langchain": {
            "services": {
                "main": {"spec": "./langchain-api.yaml", "port": 8002}
            }
        },
        "custom_ml": {
            "services": {
                "main": {"spec": "./custom-ml-api.yaml", "port": 8003}
            }
        }
    },
    "data_flow": {
        "execution_order": ["preprocess", "extract_features", "classify"],
        "steps": {
            "preprocess": {
                "framework": "preprocessing",
                "endpoint": "/preprocess",
                "transform_to": {"port": 8004, "format": "langchain_input"}
            },
            "extract_features": {
                "framework": "langchain",
                "endpoint": "/extract_features",
                "transform_to": {"port": 8005, "format": "ml_input"}
            },
            "classify": {
                "framework": "custom_ml",
                "endpoint": "/classify"
            }
        }
    }
}
```

### 2. Legacy System Integration

Integrate with legacy AI systems and proprietary protocols:

```python
class LegacyAISystemIntegrator:
    def __init__(self):
        self.mockloop = MockLoopClient()
        self.protocol_adapters = {}
        self.legacy_systems = {}
    
    async def register_legacy_system(self, system_name: str, system_config: dict):
        """Register a legacy AI system"""
        self.legacy_systems[system_name] = system_config
        
        # Create protocol adapter
        adapter_config = system_config["protocol_adapter"]
        await self.create_protocol_adapter(system_name, adapter_config)
    
    async def create_protocol_adapter(self, system_name: str, adapter_config: dict):
        """Create protocol adapter for legacy system"""
        protocol_type = adapter_config["type"]
        
        if protocol_type == "soap":
            await self.create_soap_adapter(system_name, adapter_config)
        elif protocol_type == "xml_rpc":
            await self.create_xml_rpc_adapter(system_name, adapter_config)
        elif protocol_type == "custom_tcp":
            await self.create_tcp_adapter(system_name, adapter_config)
        else:
            raise ValueError(f"Unsupported protocol: {protocol_type}")
    
    async def create_soap_adapter(self, system_name: str, adapter_config: dict):
        """Create SOAP protocol adapter"""
        # Generate mock SOAP service
        await self.mockloop.generate_mock_api(
            spec_url_or_path="./soap-adapter-api.yaml",
            output_dir_name=f"{system_name}_soap_adapter"
        )
        
        adapter_url = f"http://localhost:{adapter_config['port']}"
        self.protocol_adapters[system_name] = {
            "type": "soap",
            "url": adapter_url,
            "config": adapter_config
        }
        
        # Configure SOAP response templates
        soap_responses = adapter_config.get("responses", {})
        for operation, response_template in soap_responses.items():
            await self.mockloop.manage_mock_data(
                server_url=adapter_url,
                operation="update_response",
                endpoint_path=f"/soap/{operation}",
                response_data=response_template
            )
    
    async def create_xml_rpc_adapter(self, system_name: str, adapter_config: dict):
        """Create XML-RPC protocol adapter"""
        await self.mockloop.generate_mock_api(
            spec_url_or_path="./xmlrpc-adapter-api.yaml",
            output_dir_name=f"{system_name}_xmlrpc_adapter"
        )
        
        adapter_url = f"http://localhost:{adapter_config['port']}"
        self.protocol_adapters[system_name] = {
            "type": "xml_rpc",
            "url": adapter_url,
            "config": adapter_config
        }
    
    async def call_legacy_system(self, system_name: str, operation: str, parameters: dict):
        """Call legacy system through protocol adapter"""
        if system_name not in self.protocol_adapters:
            raise ValueError(f"No adapter for system: {system_name}")
        
        adapter = self.protocol_adapters[system_name]
        adapter_type = adapter["type"]
        
        if adapter_type == "soap":
            return await self.call_soap_service(adapter, operation, parameters)
        elif adapter_type == "xml_rpc":
            return await self.call_xml_rpc_service(adapter, operation, parameters)
        else:
            raise ValueError(f"Unsupported adapter type: {adapter_type}")
    
    async def call_soap_service(self, adapter: dict, operation: str, parameters: dict):
        """Call SOAP service through adapter"""
        adapter_url = adapter["url"]
        
        # Create SOAP envelope
        soap_envelope = self.create_soap_envelope(operation, parameters)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{adapter_url}/soap/{operation}",
                content=soap_envelope,
                headers={"Content-Type": "text/xml; charset=utf-8"}
            )
        
        if response.status_code == 200:
            return self.parse_soap_response(response.text)
        else:
            raise Exception(f"SOAP call failed: {response.text}")
    
    def create_soap_envelope(self, operation: str, parameters: dict) -> str:
        """Create SOAP envelope for operation"""
        # Simplified SOAP envelope creation
        params_xml = ""
        for key, value in parameters.items():
            params_xml += f"<{key}>{value}</{key}>"
        
        return f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <{operation}>
                    {params_xml}
                </{operation}>
            </soap:Body>
        </soap:Envelope>"""
    
    def parse_soap_response(self, response_xml: str) -> dict:
        """Parse SOAP response"""
        # Simplified SOAP response parsing
        import xml.etree.ElementTree as ET
        
        root = ET.fromstring(response_xml)
        
        # Extract response data (simplified)
        result = {}
        for elem in root.iter():
            if elem.text and elem.tag.split('}')[-1] not in ['Envelope', 'Body']:
                result[elem.tag.split('}')[-1]] = elem.text
        
        return result
```

## Testing Custom Workflows

### Comprehensive Workflow Testing

```python
import pytest
import asyncio

class CustomWorkflowTester:
    def __init__(self):
        self.mockloop = MockLoopClient()
        self.test_scenarios = {}
        self.performance_metrics = {}
    
    async def setup_test_environment(self, workflow_config: dict):
        """Setup test environment for custom workflow"""
        # Generate all required mock services
        for service_name, service_config in workflow_config["services"].items():
            await self.mockloop.generate_mock_api(
                spec_url_or_path=service_config["spec"],
                output_dir_name=f"test_{service_name}"
            )
    
    async def create_test_scenario(self, scenario_name: str, scenario_config: dict):
        """Create a test scenario"""
        self.test_scenarios[scenario_name] = scenario_config
        
        # Configure mock services for scenario
        for service_name, service_responses in scenario_config["services"].items():
            service_url = f"http://localhost:{scenario_config['ports'][service_name]}"
            
            for endpoint, response_data in service_responses.items():
                await self.mockloop.manage_mock_data(
                    server_url=service_url,
                    operation="update_response",
                    endpoint_path=endpoint,
                    response_data=response_data
                )
    
    async def test_workflow_scenario(self, workflow, scenario_name: str, test_input: dict):
        """Test workflow with specific scenario"""
        if scenario_name not in self.test_scenarios:
            raise ValueError(f"Scenario {scenario_name} not found")
        
        # Switch to test scenario
        scenario_config = self.test_scenarios[scenario_name]
        await self.activate_scenario(scenario_config)
        
        # Execute workflow
        start_time = time.time()
        
        try:
            result = await workflow.execute