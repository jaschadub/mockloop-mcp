# CrewAI Integration

CrewAI is a cutting-edge framework for orchestrating role-playing, autonomous AI agents. MockLoop MCP provides comprehensive integration with CrewAI, enabling you to test multi-agent systems with realistic API interactions and complex scenario management.

## Overview

CrewAI applications involve multiple agents working together, each with specific roles and responsibilities. MockLoop MCP enhances CrewAI development by:

- **Multi-Agent API Testing**: Provide different mock services for different agents
- **Role-Based Scenarios**: Create scenarios tailored to specific agent roles
- **Collaborative Workflow Testing**: Test agent interactions through mock APIs
- **Task Validation**: Verify agent outputs against expected API responses
- **Performance Analysis**: Monitor agent behavior and API usage patterns

## Installation and Setup

### Prerequisites

```bash
pip install crewai mockloop-mcp
```

### Basic Integration

```python
from crewai import Agent, Task, Crew
from mockloop_mcp import MockLoopClient
import asyncio

# Initialize MockLoop client
mockloop = MockLoopClient()

# Generate mock servers for different services
await mockloop.generate_mock_api(
    spec_url_or_path="./research-api.yaml",
    output_dir_name="research_service_mock"
)

await mockloop.generate_mock_api(
    spec_url_or_path="./writing-api.yaml", 
    output_dir_name="writing_service_mock"
)
```

## Core Integration Patterns

### Pattern 1: Role-Based Mock Services

Configure different mock services for different agent roles:

```python
class CrewAIMockManager:
    def __init__(self):
        self.mockloop = MockLoopClient()
        self.agent_services = {
            "researcher": "http://localhost:8001",
            "writer": "http://localhost:8002", 
            "reviewer": "http://localhost:8003",
            "publisher": "http://localhost:8004"
        }
    
    async def setup_agent_services(self):
        """Setup mock services for each agent role"""
        service_configs = [
            {"role": "researcher", "spec": "./research-api.yaml", "port": 8001},
            {"role": "writer", "spec": "./writing-api.yaml", "port": 8002},
            {"role": "reviewer", "spec": "./review-api.yaml", "port": 8003},
            {"role": "publisher", "spec": "./publish-api.yaml", "port": 8004}
        ]
        
        for config in service_configs:
            await self.mockloop.generate_mock_api(
                spec_url_or_path=config["spec"],
                output_dir_name=f"{config['role']}_service"
            )
    
    async def configure_agent_scenario(self, agent_role: str, scenario_data: dict):
        """Configure mock responses for a specific agent"""
        service_url = self.agent_services[agent_role]
        
        for endpoint, response_data in scenario_data.items():
            await self.mockloop.manage_mock_data(
                server_url=service_url,
                operation="update_response",
                endpoint_path=endpoint,
                response_data=response_data
            )

# Usage with CrewAI agents
def create_research_agent():
    return Agent(
        role='Senior Research Analyst',
        goal='Conduct thorough research on given topics',
        backstory="""You are a senior research analyst with expertise in 
        gathering and analyzing information from various sources.""",
        verbose=True,
        tools=[research_tool]  # Custom tool that uses mock API
    )

def create_writer_agent():
    return Agent(
        role='Content Writer',
        goal='Create engaging and informative content',
        backstory="""You are a skilled content writer who can transform 
        research into compelling articles.""",
        verbose=True,
        tools=[writing_tool]  # Custom tool that uses mock API
    )
```

### Pattern 2: Collaborative Workflow Testing

Test agent collaboration through shared mock services:

```python
class CollaborativeWorkflowTester:
    def __init__(self):
        self.mockloop = MockLoopClient()
        self.shared_workspace_url = "http://localhost:8000"
        self.workflow_state = {}
    
    async def setup_shared_workspace(self):
        """Setup shared workspace for agent collaboration"""
        await self.mockloop.generate_mock_api(
            spec_url_or_path="./workspace-api.yaml",
            output_dir_name="shared_workspace"
        )
    
    async def simulate_agent_collaboration(self, scenario_name: str):
        """Simulate multi-agent collaboration scenario"""
        
        collaboration_scenarios = {
            "research_to_writing": {
                "initial_state": {
                    "/workspace/documents": {"documents": []},
                    "/workspace/research": {"status": "pending"},
                    "/workspace/drafts": {"drafts": []}
                },
                "research_complete": {
                    "/workspace/research": {
                        "status": "complete",
                        "findings": ["Finding 1", "Finding 2", "Finding 3"]
                    },
                    "/workspace/documents": {
                        "documents": [
                            {"id": 1, "type": "research", "content": "Research data..."}
                        ]
                    }
                },
                "writing_complete": {
                    "/workspace/drafts": {
                        "drafts": [
                            {"id": 1, "title": "Article Draft", "content": "Article content..."}
                        ]
                    }
                }
            }
        }
        
        scenario = collaboration_scenarios[scenario_name]
        
        # Set initial state
        for endpoint, data in scenario["initial_state"].items():
            await self.mockloop.manage_mock_data(
                server_url=self.shared_workspace_url,
                operation="update_response",
                endpoint_path=endpoint,
                response_data=data
            )
        
        return scenario
    
    async def advance_workflow_state(self, stage: str, scenario: dict):
        """Advance workflow to next stage"""
        if stage in scenario:
            for endpoint, data in scenario[stage].items():
                await self.mockloop.manage_mock_data(
                    server_url=self.shared_workspace_url,
                    operation="update_response",
                    endpoint_path=endpoint,
                    response_data=data
                )
```

### Pattern 3: Task Validation and Monitoring

Monitor and validate agent task execution:

```python
class AgentTaskValidator:
    def __init__(self):
        self.mockloop = MockLoopClient()
        self.task_expectations = {}
        self.agent_performance = {}
    
    async def setup_task_validation(self, task_id: str, expectations: dict):
        """Setup validation criteria for a task"""
        self.task_expectations[task_id] = expectations
        
        # Configure mock responses based on expectations
        await self.mockloop.manage_mock_data(
            operation="create_scenario",
            scenario_name=f"task_{task_id}_validation",
            scenario_config=expectations["mock_responses"]
        )
    
    async def monitor_agent_task(self, agent_name: str, task_id: str):
        """Monitor agent performance during task execution"""
        
        # Switch to task validation scenario
        await self.mockloop.manage_mock_data(
            operation="switch_scenario",
            scenario_name=f"task_{task_id}_validation"
        )
        
        # Monitor API interactions
        start_time = time.time()
        
        # Get baseline metrics
        initial_logs = await self.mockloop.query_mock_logs(
            server_url="http://localhost:8000",
            limit=0,
            analyze=True
        )
        
        return {
            "agent": agent_name,
            "task_id": task_id,
            "start_time": start_time,
            "initial_request_count": initial_logs["analysis"]["total_requests"]
        }
    
    async def validate_task_completion(self, agent_name: str, task_id: str, monitoring_data: dict):
        """Validate task completion against expectations"""
        
        # Get final metrics
        final_logs = await self.mockloop.query_mock_logs(
            server_url="http://localhost:8000",
            analyze=True
        )
        
        execution_time = time.time() - monitoring_data["start_time"]
        api_calls_made = final_logs["analysis"]["total_requests"] - monitoring_data["initial_request_count"]
        
        expectations = self.task_expectations[task_id]
        
        validation_result = {
            "agent": agent_name,
            "task_id": task_id,
            "execution_time": execution_time,
            "api_calls_made": api_calls_made,
            "validations": {}
        }
        
        # Validate execution time
        if "max_execution_time" in expectations:
            validation_result["validations"]["execution_time"] = {
                "expected": f"<= {expectations['max_execution_time']}s",
                "actual": f"{execution_time:.2f}s",
                "passed": execution_time <= expectations["max_execution_time"]
            }
        
        # Validate API usage
        if "expected_api_calls" in expectations:
            validation_result["validations"]["api_calls"] = {
                "expected": expectations["expected_api_calls"],
                "actual": api_calls_made,
                "passed": api_calls_made == expectations["expected_api_calls"]
            }
        
        # Validate error rate
        error_rate = final_logs["analysis"].get("error_rate_percent", 0)
        if "max_error_rate" in expectations:
            validation_result["validations"]["error_rate"] = {
                "expected": f"<= {expectations['max_error_rate']}%",
                "actual": f"{error_rate}%",
                "passed": error_rate <= expectations["max_error_rate"]
            }
        
        return validation_result
```

## Advanced Integration Features

### Multi-Agent Scenario Management

Manage complex scenarios involving multiple agents:

```python
class MultiAgentScenarioManager:
    def __init__(self):
        self.mockloop = MockLoopClient()
        self.scenarios = {}
        self.active_scenario = None
    
    async def define_scenario(self, scenario_name: str, scenario_config: dict):
        """Define a multi-agent scenario"""
        self.scenarios[scenario_name] = scenario_config
        
        # Setup mock services for each agent in the scenario
        for agent_name, agent_config in scenario_config["agents"].items():
            service_url = agent_config["service_url"]
            mock_responses = agent_config["mock_responses"]
            
            # Create scenario for this agent
            await self.mockloop.manage_mock_data(
                operation="create_scenario",
                scenario_name=f"{scenario_name}_{agent_name}",
                scenario_config=mock_responses
            )
    
    async def activate_scenario(self, scenario_name: str):
        """Activate a multi-agent scenario"""
        if scenario_name not in self.scenarios:
            raise ValueError(f"Scenario {scenario_name} not found")
        
        self.active_scenario = scenario_name
        scenario_config = self.scenarios[scenario_name]
        
        # Activate scenario for each agent
        for agent_name in scenario_config["agents"].keys():
            await self.mockloop.manage_mock_data(
                operation="switch_scenario",
                scenario_name=f"{scenario_name}_{agent_name}"
            )
    
    async def update_scenario_state(self, agent_name: str, state_updates: dict):
        """Update scenario state for a specific agent"""
        if not self.active_scenario:
            raise ValueError("No active scenario")
        
        scenario_config = self.scenarios[self.active_scenario]
        agent_config = scenario_config["agents"][agent_name]
        service_url = agent_config["service_url"]
        
        # Update mock responses for the agent
        for endpoint, response_data in state_updates.items():
            await self.mockloop.manage_mock_data(
                server_url=service_url,
                operation="update_response",
                endpoint_path=endpoint,
                response_data=response_data
            )

# Example scenario definition
content_creation_scenario = {
    "agents": {
        "researcher": {
            "service_url": "http://localhost:8001",
            "mock_responses": {
                "/research/topics": {
                    "topics": ["AI trends", "Machine learning", "Data science"]
                },
                "/research/sources": {
                    "sources": [
                        {"url": "example.com", "credibility": 0.9},
                        {"url": "research.org", "credibility": 0.95}
                    ]
                }
            }
        },
        "writer": {
            "service_url": "http://localhost:8002",
            "mock_responses": {
                "/writing/templates": {
                    "templates": ["blog_post", "article", "whitepaper"]
                },
                "/writing/style_guide": {
                    "tone": "professional",
                    "length": "medium",
                    "audience": "technical"
                }
            }
        },
        "reviewer": {
            "service_url": "http://localhost:8003",
            "mock_responses": {
                "/review/criteria": {
                    "criteria": ["accuracy", "clarity", "engagement"]
                },
                "/review/feedback": {
                    "status": "pending"
                }
            }
        }
    }
}
```

### Performance Analytics

Analyze multi-agent system performance:

```python
class CrewAIPerformanceAnalyzer:
    def __init__(self):
        self.mockloop = MockLoopClient()
        self.performance_data = {}
    
    async def start_performance_monitoring(self, crew_name: str, agents: list):
        """Start monitoring crew performance"""
        self.performance_data[crew_name] = {
            "start_time": time.time(),
            "agents": agents,
            "initial_metrics": {}
        }
        
        # Get initial metrics for each agent's service
        for agent in agents:
            service_url = agent["service_url"]
            logs = await self.mockloop.query_mock_logs(
                server_url=service_url,
                limit=0,
                analyze=True
            )
            
            self.performance_data[crew_name]["initial_metrics"][agent["name"]] = {
                "requests": logs["analysis"]["total_requests"],
                "errors": logs["analysis"]["total_errors"]
            }
    
    async def analyze_crew_performance(self, crew_name: str):
        """Analyze crew performance after execution"""
        if crew_name not in self.performance_data:
            raise ValueError(f"No performance data for crew {crew_name}")
        
        crew_data = self.performance_data[crew_name]
        execution_time = time.time() - crew_data["start_time"]
        
        agent_analytics = {}
        
        # Analyze each agent's performance
        for agent in crew_data["agents"]:
            agent_name = agent["name"]
            service_url = agent["service_url"]
            
            # Get final metrics
            logs = await self.mockloop.query_mock_logs(
                server_url=service_url,
                analyze=True
            )
            
            initial_metrics = crew_data["initial_metrics"][agent_name]
            
            agent_analytics[agent_name] = {
                "requests_made": logs["analysis"]["total_requests"] - initial_metrics["requests"],
                "errors_encountered": logs["analysis"]["total_errors"] - initial_metrics["errors"],
                "avg_response_time": logs["analysis"]["avg_response_time_ms"],
                "error_rate": logs["analysis"]["error_rate_percent"]
            }
        
        return {
            "crew_name": crew_name,
            "total_execution_time": execution_time,
            "agent_analytics": agent_analytics,
            "overall_metrics": {
                "total_requests": sum(a["requests_made"] for a in agent_analytics.values()),
                "total_errors": sum(a["errors_encountered"] for a in agent_analytics.values()),
                "avg_error_rate": sum(a["error_rate"] for a in agent_analytics.values()) / len(agent_analytics)
            }
        }
```

## Testing Strategies

### Unit Testing Individual Agents

Test individual agents with mock APIs:

```python
import pytest
from crewai import Agent, Task

@pytest.mark.asyncio
async def test_research_agent():
    """Test research agent with mock research API"""
    
    # Setup mock research service
    mockloop = MockLoopClient()
    await mockloop.generate_mock_api(
        spec_url_or_path="./research-api.yaml",
        output_dir_name="test_research_service"
    )
    
    # Configure test data
    test_research_data = {
        "query": "AI trends 2024",
        "results": [
            {"title": "AI Trend 1", "summary": "Summary 1", "source": "source1.com"},
            {"title": "AI Trend 2", "summary": "Summary 2", "source": "source2.com"}
        ]
    }
    
    await mockloop.manage_mock_data(
        server_url="http://localhost:8001",
        operation="update_response",
        endpoint_path="/research/search",
        response_data=test_research_data
    )
    
    # Create and test agent
    research_agent = create_research_agent()
    research_task = Task(
        description="Research AI trends for 2024",
        agent=research_agent
    )
    
    # Execute task
    result = research_task.execute()
    
    # Verify results
    assert "AI trends" in result.lower()
    assert len(test_research_data["results"]) > 0

@pytest.mark.asyncio
async def test_writer_agent():
    """Test writer agent with mock writing service"""
    
    mockloop = MockLoopClient()
    
    # Configure mock writing service
    writing_templates = {
        "templates": [
            {"name": "blog_post", "structure": ["intro", "body", "conclusion"]},
            {"name": "article", "structure": ["headline", "lead", "body", "conclusion"]}
        ]
    }
    
    await mockloop.manage_mock_data(
        server_url="http://localhost:8002",
        operation="update_response",
        endpoint_path="/writing/templates",
        response_data=writing_templates
    )
    
    # Test writer agent
    writer_agent = create_writer_agent()
    writing_task = Task(
        description="Write a blog post about AI trends",
        agent=writer_agent
    )
    
    result = writing_task.execute()
    
    # Verify writing output
    assert len(result) > 100  # Minimum content length
    assert "AI" in result
```

### Integration Testing Multi-Agent Crews

Test complete crews with realistic scenarios:

```python
@pytest.mark.asyncio
async def test_content_creation_crew():
    """Test complete content creation crew"""
    
    # Setup multi-agent environment
    scenario_manager = MultiAgentScenarioManager()
    await scenario_manager.define_scenario("content_creation", content_creation_scenario)
    await scenario_manager.activate_scenario("content_creation")
    
    # Create agents
    researcher = create_research_agent()
    writer = create_writer_agent()
    reviewer = create_reviewer_agent()
    
    # Create tasks
    research_task = Task(
        description="Research AI trends for 2024",
        agent=researcher
    )
    
    writing_task = Task(
        description="Write an article based on research findings",
        agent=writer
    )
    
    review_task = Task(
        description="Review and provide feedback on the article",
        agent=reviewer
    )
    
    # Create and execute crew
    crew = Crew(
        agents=[researcher, writer, reviewer],
        tasks=[research_task, writing_task, review_task],
        verbose=True
    )
    
    # Monitor performance
    analyzer = CrewAIPerformanceAnalyzer()
    await analyzer.start_performance_monitoring("content_crew", [
        {"name": "researcher", "service_url": "http://localhost:8001"},
        {"name": "writer", "service_url": "http://localhost:8002"},
        {"name": "reviewer", "service_url": "http://localhost:8003"}
    ])
    
    # Execute crew
    result = crew.kickoff()
    
    # Analyze performance
    performance = await analyzer.analyze_crew_performance("content_crew")
    
    # Verify results
    assert result is not None
    assert performance["overall_metrics"]["total_requests"] > 0
    assert performance["overall_metrics"]["avg_error_rate"] < 10  # Less than 10% error rate
```

## Best Practices

### 1. Agent Role Separation

- **Dedicated Services**: Provide separate mock services for different agent roles
- **Role-Specific Data**: Tailor mock responses to agent responsibilities
- **Clear Boundaries**: Define clear API boundaries between agent roles

### 2. Realistic Collaboration

- **Shared State**: Use shared mock services for agent collaboration
- **State Transitions**: Model realistic state changes in collaborative workflows
- **Communication Patterns**: Test realistic agent communication patterns

### 3. Performance Monitoring

- **Individual Metrics**: Monitor each agent's API usage and performance
- **Crew Metrics**: Track overall crew performance and efficiency
- **Bottleneck Identification**: Identify performance bottlenecks in multi-agent workflows

### 4. Error Handling

- **Agent Resilience**: Test agent behavior under API failures
- **Graceful Degradation**: Verify crews handle individual agent failures
- **Recovery Mechanisms**: Test crew recovery from various error conditions

## Example: Customer Service Crew

Complete example of a customer service crew with MockLoop integration:

```python
from crewai import Agent, Task, Crew

# Define agents
def create_customer_service_crew():
    # Customer Support Agent
    support_agent = Agent(
        role='Customer Support Specialist',
        goal='Resolve customer issues efficiently and professionally',
        backstory="""You are an experienced customer support specialist 
        with access to customer data and support tools.""",
        tools=[customer_lookup_tool, ticket_management_tool]
    )
    
    # Technical Support Agent  
    tech_agent = Agent(
        role='Technical Support Engineer',
        goal='Diagnose and resolve technical issues',
        backstory="""You are a technical support engineer with deep 
        knowledge of system diagnostics and troubleshooting.""",
        tools=[system_diagnostic_tool, knowledge_base_tool]
    )
    
    # Escalation Manager
    manager_agent = Agent(
        role='Support Manager',
        goal='Handle escalated issues and ensure customer satisfaction',
        backstory="""You are a support manager who handles complex 
        escalations and makes final decisions on customer issues.""",
        tools=[escalation_tool, approval_tool]
    )
    
    return [support_agent, tech_agent, manager_agent]

# Setup mock services for customer service scenario
async def setup_customer_service_mocks():
    mockloop = MockLoopClient()
    
    # Customer database mock
    await mockloop.generate_mock_api(
        spec_url_or_path="./customer-db-api.yaml",
        output_dir_name="customer_db_service"
    )
    
    # Ticket system mock
    await mockloop.generate_mock_api(
        spec_url_or_path="./ticket-system-api.yaml", 
        output_dir_name="ticket_system_service"
    )
    
    # Knowledge base mock
    await mockloop.generate_mock_api(
        spec_url_or_path="./knowledge-base-api.yaml",
        output_dir_name="knowledge_base_service"
    )
    
    # Configure customer service scenarios
    scenarios = {
        "simple_issue": {
            "/customers/12345": {
                "id": 12345,
                "name": "John Doe", 
                "tier": "premium",
                "status": "active"
            },
            "/tickets": {
                "tickets": [
                    {"id": "T001", "status": "open", "priority": "low", "issue": "Login problem"}
                ]
            },
            "/knowledge-base/search": {
                "articles": [
                    {"id": "KB001", "title": "Login Issues", "solution": "Clear browser cache"}
                ]
            }
        },
        "complex_issue": {
            "/customers/12345": {
                "id": 12345,
                "name": "Jane Smith",
                "tier": "enterprise", 
                "status": "active"
            },
            "/tickets": {
                "tickets": [
                    {"id": "T002", "status": "escalated", "priority": "high", "issue": "Data corruption"}
                ]
            },
            "/knowledge-base/search": {
                "articles": []  # No solutions found
            }
        }
    }
    
    # Create scenarios
    for scenario_name, config in scenarios.items():
        await mockloop.manage_mock_data(
            operation="create_scenario",
            scenario_name=scenario_name,
            scenario_config=config
        )

# Usage
async def main():
    # Setup mock services
    await setup_customer_service_mocks()
    
    # Create crew
    agents = create_customer_service_crew()
    
    # Define tasks
    tasks = [
        Task(
            description="Handle incoming customer support ticket T001",
            agent=agents[0]  # Support agent
        ),
        Task(
            description="Provide technical diagnosis for escalated issues",
            agent=agents[1]  # Tech agent
        ),
        Task(
            description="Review and approve resolution for complex cases",
            agent=agents[2]  # Manager
        )
    ]
    
    # Create and run crew
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True
    )
    
    # Test with simple issue scenario
    await mockloop.manage_mock_data(
        operation="switch_scenario",
        scenario_name="simple_issue"
    )
    
    result = crew.kickoff()
    print(f"Simple issue result: {result}")
    
    # Test with complex issue scenario
    await mockloop.manage_mock_data(
        operation="switch_scenario", 
        scenario_name="complex_issue"
    )
    
    result = crew.kickoff()
    print(f"Complex issue result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

- **[LangChain Integration](langchain.md)**: Learn about chain testing with MockLoop
- **[Custom AI Workflows](custom-workflows.md)**: Create custom multi-agent patterns
- **[Performance Monitoring](../guides/performance-monitoring.md)**: Monitor crew performance

---

CrewAI integration with MockLoop MCP enables comprehensive testing of multi-agent systems. Start with simple agent interactions and gradually build more complex collaborative scenarios as your crews evolve.