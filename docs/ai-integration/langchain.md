# LangChain Integration

LangChain is a powerful framework for developing applications with large language models. MockLoop MCP provides seamless integration with LangChain, enabling you to test chains, agents, and tools with realistic API interactions and comprehensive scenario management.

## Overview

LangChain applications often rely on external APIs for data retrieval, tool execution, and service integration. MockLoop MCP enhances LangChain development by:

- **Tool Integration**: Use MockLoop tools within LangChain applications
- **Chain Testing**: Test complex chains with realistic API responses
- **Memory Validation**: Verify chain memory against mock data
- **Retrieval Testing**: Mock external data sources for RAG applications
- **Agent Testing**: Test LangChain agents with controllable external services

## Installation and Setup

### Prerequisites

```bash
pip install langchain mockloop-mcp
```

### Basic Integration

```python
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from mockloop_mcp import MockLoopClient
import asyncio

# Initialize MockLoop client
mockloop = MockLoopClient()

# Generate mock server for external APIs
await mockloop.generate_mock_api(
    spec_url_or_path="./external-api.yaml",
    output_dir_name="langchain_mock_server"
)
```

## Core Integration Patterns

### Pattern 1: Custom Tools with Mock APIs

Create LangChain tools that use mock APIs:

```python
import requests
from langchain.tools import Tool
from typing import Optional

class MockAPITool:
    def __init__(self, mockloop_client, server_url: str):
        self.mockloop = mockloop_client
        self.server_url = server_url
    
    async def configure_response(self, endpoint: str, response_data: dict):
        """Configure mock API response"""
        await self.mockloop.manage_mock_data(
            server_url=self.server_url,
            operation="update_response",
            endpoint_path=endpoint,
            response_data=response_data
        )
    
    def search_knowledge_base(self, query: str) -> str:
        """Search knowledge base via mock API"""
        try:
            response = requests.get(
                f"{self.server_url}/search",
                params={"q": query}
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            if results:
                return f"Found {len(results)} results: " + "; ".join([
                    f"{r['title']}: {r['summary']}" for r in results[:3]
                ])
            else:
                return "No results found for the query."
                
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"
    
    def get_user_data(self, user_id: str) -> str:
        """Get user data via mock API"""
        try:
            response = requests.get(f"{self.server_url}/users/{user_id}")
            response.raise_for_status()
            
            user_data = response.json()
            return f"User {user_data['name']} (ID: {user_data['id']}) - Status: {user_data['status']}"
            
        except Exception as e:
            return f"Error retrieving user data: {str(e)}"

# Create LangChain tools
def create_langchain_tools(mock_api_tool):
    return [
        Tool(
            name="search_knowledge_base",
            description="Search the knowledge base for information about a topic",
            func=mock_api_tool.search_knowledge_base
        ),
        Tool(
            name="get_user_data", 
            description="Get user information by user ID",
            func=mock_api_tool.get_user_data
        )
    ]

# Usage with LangChain agent
async def create_test_agent():
    # Setup mock API tool
    mock_api_tool = MockAPITool(mockloop, "http://localhost:8000")
    
    # Configure mock responses
    await mock_api_tool.configure_response("/search", {
        "results": [
            {"title": "LangChain Guide", "summary": "Comprehensive guide to LangChain"},
            {"title": "AI Integration", "summary": "Best practices for AI integration"}
        ]
    })
    
    await mock_api_tool.configure_response("/users/123", {
        "id": "123",
        "name": "John Doe",
        "status": "active",
        "preferences": {"notifications": True}
    })
    
    # Create tools
    tools = create_langchain_tools(mock_api_tool)
    
    # Initialize agent
    llm = OpenAI(temperature=0)
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    
    return agent
```

### Pattern 2: Chain Testing with Mock Data

Test LangChain chains with controllable mock data:

```python
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

class ChainTester:
    def __init__(self, mockloop_client):
        self.mockloop = mockloop_client
        self.test_scenarios = {}
    
    async def setup_chain_test_scenario(self, scenario_name: str, mock_data: dict):
        """Setup a test scenario for chain testing"""
        self.test_scenarios[scenario_name] = mock_data
        
        # Configure mock API responses
        for endpoint, response_data in mock_data.items():
            await self.mockloop.manage_mock_data(
                server_url="http://localhost:8000",
                operation="update_response",
                endpoint_path=endpoint,
                response_data=response_data
            )
    
    async def test_chain_with_scenario(self, chain, scenario_name: str, input_data: dict):
        """Test a chain with a specific scenario"""
        if scenario_name not in self.test_scenarios:
            raise ValueError(f"Scenario {scenario_name} not found")
        
        # Switch to test scenario
        await self.mockloop.manage_mock_data(
            operation="switch_scenario",
            scenario_name=scenario_name
        )
        
        # Execute chain
        result = chain.run(input_data)
        
        # Get API interaction logs
        logs = await self.mockloop.query_mock_logs(
            server_url="http://localhost:8000",
            analyze=True
        )
        
        return {
            "scenario": scenario_name,
            "result": result,
            "api_interactions": logs["analysis"],
            "success": True
        }

# Example: Testing a research chain
def create_research_chain():
    # First chain: Research topic
    research_template = """
    Research the topic: {topic}
    Use the search tool to find relevant information.
    Topic: {topic}
    Research:"""
    
    research_prompt = PromptTemplate(
        input_variables=["topic"],
        template=research_template
    )
    
    research_chain = LLMChain(
        llm=OpenAI(temperature=0),
        prompt=research_prompt
    )
    
    # Second chain: Summarize research
    summary_template = """
    Summarize the following research:
    {research}
    Summary:"""
    
    summary_prompt = PromptTemplate(
        input_variables=["research"],
        template=summary_template
    )
    
    summary_chain = LLMChain(
        llm=OpenAI(temperature=0),
        prompt=summary_prompt
    )
    
    # Combine chains
    overall_chain = SimpleSequentialChain(
        chains=[research_chain, summary_chain],
        verbose=True
    )
    
    return overall_chain

# Test the chain
async def test_research_chain():
    chain_tester = ChainTester(mockloop)
    
    # Setup test scenarios
    await chain_tester.setup_chain_test_scenario("comprehensive_data", {
        "/search": {
            "results": [
                {"title": "AI Research Paper", "summary": "Latest AI developments"},
                {"title": "Machine Learning Guide", "summary": "ML best practices"},
                {"title": "Deep Learning Tutorial", "summary": "Neural network fundamentals"}
            ]
        }
    })
    
    await chain_tester.setup_chain_test_scenario("limited_data", {
        "/search": {
            "results": [
                {"title": "Basic AI Info", "summary": "Simple AI overview"}
            ]
        }
    })
    
    # Create and test chain
    research_chain = create_research_chain()
    
    # Test with comprehensive data
    result1 = await chain_tester.test_chain_with_scenario(
        research_chain,
        "comprehensive_data",
        {"topic": "artificial intelligence"}
    )
    
    # Test with limited data
    result2 = await chain_tester.test_chain_with_scenario(
        research_chain,
        "limited_data", 
        {"topic": "artificial intelligence"}
    )
    
    return [result1, result2]
```

### Pattern 3: RAG System Testing

Test Retrieval-Augmented Generation systems with mock knowledge bases:

```python
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

class RAGSystemTester:
    def __init__(self, mockloop_client):
        self.mockloop = mockloop_client
        self.knowledge_base_url = "http://localhost:8001"
    
    async def setup_knowledge_base_mock(self):
        """Setup mock knowledge base API"""
        await self.mockloop.generate_mock_api(
            spec_url_or_path="./knowledge-base-api.yaml",
            output_dir_name="knowledge_base_mock"
        )
    
    async def configure_knowledge_scenario(self, scenario_name: str, documents: list):
        """Configure knowledge base scenario"""
        scenario_config = {
            "/documents/search": {
                "documents": documents,
                "total": len(documents)
            }
        }
        
        for i, doc in enumerate(documents):
            scenario_config[f"/documents/{i+1}"] = {
                "id": i+1,
                "content": doc["content"],
                "metadata": doc.get("metadata", {})
            }
        
        await self.mockloop.manage_mock_data(
            operation="create_scenario",
            scenario_name=scenario_name,
            scenario_config=scenario_config
        )
    
    def create_mock_retriever(self):
        """Create a retriever that uses mock knowledge base"""
        class MockRetriever:
            def __init__(self, knowledge_base_url):
                self.knowledge_base_url = knowledge_base_url
            
            def get_relevant_documents(self, query: str):
                # Query mock knowledge base
                response = requests.get(
                    f"{self.knowledge_base_url}/documents/search",
                    params={"q": query}
                )
                
                documents = response.json().get("documents", [])
                
                # Convert to LangChain Document format
                from langchain.schema import Document
                return [
                    Document(
                        page_content=doc["content"],
                        metadata=doc.get("metadata", {})
                    )
                    for doc in documents
                ]
        
        return MockRetriever(self.knowledge_base_url)
    
    async def test_rag_system(self, scenario_name: str, questions: list):
        """Test RAG system with specific scenario"""
        
        # Switch to scenario
        await self.mockloop.manage_mock_data(
            operation="switch_scenario",
            scenario_name=scenario_name
        )
        
        # Create RAG chain with mock retriever
        retriever = self.create_mock_retriever()
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(temperature=0),
            chain_type="stuff",
            retriever=retriever
        )
        
        # Test questions
        results = []
        for question in questions:
            answer = qa_chain.run(question)
            results.append({
                "question": question,
                "answer": answer
            })
        
        # Get performance metrics
        logs = await self.mockloop.query_mock_logs(
            server_url=self.knowledge_base_url,
            analyze=True
        )
        
        return {
            "scenario": scenario_name,
            "results": results,
            "performance": logs["analysis"]
        }

# Example usage
async def test_rag_scenarios():
    rag_tester = RAGSystemTester(mockloop)
    await rag_tester.setup_knowledge_base_mock()
    
    # Configure scenarios
    comprehensive_docs = [
        {
            "content": "LangChain is a framework for developing applications with large language models.",
            "metadata": {"source": "langchain_docs", "topic": "introduction"}
        },
        {
            "content": "MockLoop MCP provides tools for generating and managing mock API servers.",
            "metadata": {"source": "mockloop_docs", "topic": "overview"}
        },
        {
            "content": "Integration between LangChain and MockLoop enables comprehensive testing.",
            "metadata": {"source": "integration_guide", "topic": "testing"}
        }
    ]
    
    limited_docs = [
        {
            "content": "Basic information about AI frameworks.",
            "metadata": {"source": "basic_guide", "topic": "general"}
        }
    ]
    
    await rag_tester.configure_knowledge_scenario("comprehensive", comprehensive_docs)
    await rag_tester.configure_knowledge_scenario("limited", limited_docs)
    
    # Test questions
    test_questions = [
        "What is LangChain?",
        "How does MockLoop work?",
        "What are the benefits of integration?"
    ]
    
    # Test both scenarios
    comprehensive_results = await rag_tester.test_rag_system("comprehensive", test_questions)
    limited_results = await rag_tester.test_rag_system("limited", test_questions)
    
    return [comprehensive_results, limited_results]
```

## Advanced Integration Features

### Memory Testing

Test LangChain memory components with mock data:

```python
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.chains import ConversationChain

class MemoryTester:
    def __init__(self, mockloop_client):
        self.mockloop = mockloop_client
        self.memory_store_url = "http://localhost:8002"
    
    async def setup_memory_store_mock(self):
        """Setup mock memory store"""
        await self.mockloop.generate_mock_api(
            spec_url_or_path="./memory-store-api.yaml",
            output_dir_name="memory_store_mock"
        )
    
    async def test_conversation_memory(self, memory_type: str, conversation_turns: list):
        """Test conversation memory with mock storage"""
        
        # Configure memory store responses
        memory_data = {"conversations": {}, "summaries": {}}
        
        await self.mockloop.manage_mock_data(
            server_url=self.memory_store_url,
            operation="update_response",
            endpoint_path="/memory/conversations",
            response_data=memory_data
        )
        
        # Create memory based on type
        if memory_type == "buffer":
            memory = ConversationBufferMemory()
        elif memory_type == "summary":
            memory = ConversationSummaryMemory(llm=OpenAI(temperature=0))
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")
        
        # Create conversation chain
        conversation = ConversationChain(
            llm=OpenAI(temperature=0),
            memory=memory,
            verbose=True
        )
        
        # Simulate conversation
        results = []
        for turn in conversation_turns:
            response = conversation.predict(input=turn["input"])
            results.append({
                "input": turn["input"],
                "output": response,
                "memory_state": str(memory.buffer) if hasattr(memory, 'buffer') else str(memory)
            })
        
        return {
            "memory_type": memory_type,
            "conversation_results": results,
            "final_memory_state": str(memory.buffer) if hasattr(memory, 'buffer') else str(memory)
        }

# Example usage
async def test_memory_scenarios():
    memory_tester = MemoryTester(mockloop)
    await memory_tester.setup_memory_store_mock()
    
    conversation_turns = [
        {"input": "Hi, my name is John"},
        {"input": "What's my name?"},
        {"input": "I like programming in Python"},
        {"input": "What do I like to do?"}
    ]
    
    # Test different memory types
    buffer_results = await memory_tester.test_conversation_memory("buffer", conversation_turns)
    summary_results = await memory_tester.test_conversation_memory("summary", conversation_turns)
    
    return [buffer_results, summary_results]
```

### Agent Performance Testing

Test LangChain agents under different performance conditions:

```python
from langchain.agents import initialize_agent, AgentType
import time

class AgentPerformanceTester:
    def __init__(self, mockloop_client):
        self.mockloop = mockloop_client
        self.performance_scenarios = {}
    
    async def setup_performance_scenarios(self):
        """Setup performance testing scenarios"""
        self.performance_scenarios = {
            "fast_apis": {
                "/search": {"delay_ms": 50, "results": ["Fast result 1", "Fast result 2"]},
                "/users": {"delay_ms": 30, "user": {"name": "John", "status": "active"}}
            },
            "slow_apis": {
                "/search": {"delay_ms": 2000, "results": ["Slow result 1"]},
                "/users": {"delay_ms": 1500, "user": {"name": "Jane", "status": "active"}}
            },
            "unreliable_apis": {
                "/search": {"error": "Service temporarily unavailable", "status": 503},
                "/users": {"delay_ms": 5000, "user": {"name": "Bob", "status": "active"}}
            }
        }
        
        # Create scenarios
        for scenario_name, config in self.performance_scenarios.items():
            await self.mockloop.manage_mock_data(
                operation="create_scenario",
                scenario_name=scenario_name,
                scenario_config=config
            )
    
    async def test_agent_performance(self, agent, test_queries: list, scenario_name: str):
        """Test agent performance under specific conditions"""
        
        # Switch to performance scenario
        await self.mockloop.manage_mock_data(
            operation="switch_scenario",
            scenario_name=scenario_name
        )
        
        results = []
        
        for query in test_queries:
            start_time = time.time()
            
            try:
                response = agent.run(query)
                execution_time = time.time() - start_time
                
                results.append({
                    "query": query,
                    "response": response,
                    "execution_time": execution_time,
                    "success": True
                })
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                results.append({
                    "query": query,
                    "error": str(e),
                    "execution_time": execution_time,
                    "success": False
                })
        
        # Get API performance metrics
        logs = await self.mockloop.query_mock_logs(
            server_url="http://localhost:8000",
            analyze=True
        )
        
        return {
            "scenario": scenario_name,
            "query_results": results,
            "api_performance": logs["analysis"],
            "avg_execution_time": sum(r["execution_time"] for r in results) / len(results),
            "success_rate": sum(1 for r in results if r["success"]) / len(results)
        }

# Example usage
async def test_agent_performance_scenarios():
    performance_tester = AgentPerformanceTester(mockloop)
    await performance_tester.setup_performance_scenarios()
    
    # Create agent with mock tools
    mock_api_tool = MockAPITool(mockloop, "http://localhost:8000")
    tools = create_langchain_tools(mock_api_tool)
    
    agent = initialize_agent(
        tools=tools,
        llm=OpenAI(temperature=0),
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    
    test_queries = [
        "Search for information about AI",
        "Get user data for user 123",
        "Find recent research papers"
    ]
    
    # Test under different performance conditions
    fast_results = await performance_tester.test_agent_performance(
        agent, test_queries, "fast_apis"
    )
    
    slow_results = await performance_tester.test_agent_performance(
        agent, test_queries, "slow_apis"
    )
    
    unreliable_results = await performance_tester.test_agent_performance(
        agent, test_queries, "unreliable_apis"
    )
    
    return [fast_results, slow_results, unreliable_results]
```

## Testing Strategies

### Unit Testing LangChain Components

```python
import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_custom_tool():
    """Test custom tool with mock API"""
    
    mockloop = MockLoopClient()
    mock_api_tool = MockAPITool(mockloop, "http://localhost:8000")
    
    # Configure mock response
    await mock_api_tool.configure_response("/search", {
        "results": [
            {"title": "Test Result", "summary": "Test summary"}
        ]
    })
    
    # Test tool
    result = mock_api_tool.search_knowledge_base("test query")
    
    assert "Found 1 results" in result
    assert "Test Result" in result

@pytest.mark.asyncio
async def test_chain_execution():
    """Test chain execution with mock data"""
    
    chain_tester = ChainTester(mockloop)
    
    # Setup test scenario
    await chain_tester.setup_chain_test_scenario("test_scenario", {
        "/search": {"results": [{"title": "Test", "summary": "Test data"}]}
    })
    
    # Create simple chain
    chain = create_research_chain()
    
    # Test chain
    result = await chain_tester.test_chain_with_scenario(
        chain, "test_scenario", {"topic": "test"}
    )
    
    assert result["success"] is True
    assert result["api_interactions"]["total_requests"] > 0

@pytest.mark.asyncio
async def test_rag_system():
    """Test RAG system with mock knowledge base"""
    
    rag_tester = RAGSystemTester(mockloop)
    await rag_tester.setup_knowledge_base_mock()
    
    # Configure test documents
    test_docs = [
        {"content": "Test document content", "metadata": {"source": "test"}}
    ]
    
    await rag_tester.configure_knowledge_scenario("test_docs", test_docs)
    
    # Test RAG system
    results = await rag_tester.test_rag_system("test_docs", ["What is the test about?"])
    
    assert len(results["results"]) == 1
    assert "test" in results["results"][0]["answer"].lower()
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_complete_langchain_workflow():
    """Test complete LangChain workflow with multiple components"""
    
    # Setup all mock services
    mockloop = MockLoopClient()
    
    # Setup knowledge base
    rag_tester = RAGSystemTester(mockloop)
    await rag_tester.setup_knowledge_base_mock()
    
    # Setup memory store
    memory_tester = MemoryTester(mockloop)
    await memory_tester.setup_memory_store_mock()
    
    # Configure comprehensive scenario
    await rag_tester.configure_knowledge_scenario("integration_test", [
        {"content": "LangChain integration guide", "metadata": {"topic": "integration"}},
        {"content": "MockLoop testing framework", "metadata": {"topic": "testing"}}
    ])
    
    # Create agent with all components
    mock_api_tool = MockAPITool(mockloop, "http://localhost:8001")
    tools = create_langchain_tools(mock_api_tool)
    
    agent = initialize_agent(
        tools=tools,
        llm=OpenAI(temperature=0),
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=ConversationBufferMemory(memory_key="chat_history"),
        verbose=True
    )
    
    # Test multi-turn conversation
    conversation_turns = [
        "Search for information about LangChain integration",
        "What did you find about testing frameworks?",
        "Can you summarize what we've discussed?"
    ]
    
    results = []
    for turn in conversation_turns:
        response = agent.run(turn)
        results.append({"input": turn, "output": response})
    
    # Verify results
    assert len(results) == 3
    assert any("langchain" in r["output"].lower() for r in results)
    assert any("testing" in r["output"].lower() for r in results)
```

## Best Practices

### 1. Tool Design

- **Focused Functionality**: Create tools with specific, well-defined purposes
- **Error Handling**: Implement robust error handling in custom tools
- **Response Validation**: Validate API responses before processing
- **Timeout Management**: Handle API timeouts gracefully

### 2. Chain Testing

- **Scenario Coverage**: Test chains with various data scenarios
- **Performance Testing**: Verify chain performance under different conditions
- **Error Scenarios**: Test chain behavior with API failures
- **Memory Validation**: Verify chain memory behaves correctly

### 3. Agent Testing

- **Tool Integration**: Test agent tool usage patterns
- **Decision Making**: Verify agent decision-making logic
- **Performance Monitoring**: Monitor agent execution times
- **Failure Recovery**: Test agent recovery from tool failures

### 4. RAG System Testing

- **Document Scenarios**: Test with different document availability
- **Retrieval Quality**: Verify retrieval relevance and accuracy
- **Performance Impact**: Monitor retrieval performance impact
- **Fallback Behavior**: Test behavior when no documents are found

## Example: Customer Support Assistant

Complete example of a LangChain-based customer support assistant:

```python
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferWindowMemory
from langchain.llms import OpenAI

class CustomerSupportAssistant:
    def __init__(self, mockloop_client):
        self.mockloop = mockloop_client
        self.services = {
            "customer_db": "http://localhost:8001",
            "ticket_system": "http://localhost:8002", 
            "knowledge_base": "http://localhost:8003"
        }
    
    async def setup_services(self):
        """Setup all mock services"""
        service_configs = [
            {"name": "customer_db", "spec": "./customer-db-api.yaml"},
            {"name": "ticket_system", "spec": "./ticket-system-api.yaml"},
            {"name": "knowledge_base", "spec": "./knowledge-base-api.yaml"}
        ]
        
        for config in service_configs:
            await self.mockloop.generate_mock_api(
                spec_url_or_path=config["spec"],
                output_dir_name=f"{config['name']}_service"
            )
    
    def create_tools(self):
        """Create customer support tools"""
        
        def lookup_customer(customer_id: str) -> str:
            """Look up customer information"""
            response = requests.get(f"{self.services['customer_db']}/customers/{customer_id}")
            if response.status_code == 200:
                customer = response.json()
                return f"Customer: {customer['name']}, Status: {customer['status']}, Tier: {customer['tier']}"
            return f"Customer {customer_id} not found"
        
        def search_knowledge_base(query: str) -> str:
            """Search knowledge base for solutions"""
            response = requests.get(
                f"{self.services['knowledge_base']}/search",
                params={"q": query}
            )
            if response.status_code == 200:
                results = response.json().get("articles", [])
                if results:
                    return f"Found solutions: " + "; ".join([
                        f"{article['title']}: {article['summary']}" 
                        for article in results[:2]
                    ])
            return "No solutions found in knowledge base"
        
        def create_ticket(customer_id: str, issue: str) -> str:
            """Create a support ticket"""
            ticket_data = {
                "customer_id": customer_id,
                "issue": issue,
                "priority": "medium"
            }
            response = requests.post(
                f"{self.services['ticket_system']}/tickets",
                json=ticket_data
            )
            if response.status_code == 201:
                ticket = response.json()
                return f"Created ticket {ticket['id']} for customer {customer_id}"
            return "Failed to create ticket"
        
        return [
            Tool(name="lookup_customer", description="Look up customer by ID", func=lookup_customer),
            Tool(name="search_knowledge_base", description="Search for solutions", func=search_knowledge_base),
            Tool(name="create_ticket", description="Create support ticket", func=create_ticket)
        ]
    
    def create_assistant(self):
        """Create the customer support assistant"""
        tools = self.create_tools()
        
        memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=5,  # Remember last 5 interactions
            return_messages=True
        )
        
        assistant = initialize_agent(
            tools=tools,
            llm=OpenAI(temperature=0),
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=True
        )
        
        return assistant

# Usage and testing
async def test_customer_support_scenarios():
    support_assistant = CustomerSupportAssistant(mockloop)
    await support_assistant.setup_services()
    
    # Configure test scenarios
    scenarios = {
        "premium_customer_issue": {
            "/customers/12345": {
                "id": "12345",
                "name": "John Premium",
                "status": "active",
                "tier": "premium"
            },
            "/search": {
                "articles": [
                    {"title": "Premium Support Guide", "summary": "Expedited resolution process"}
                ]
            }
        },
        "new_customer_issue": {
            "/customers/67890": {
                "id": "67890", 
                "name": "Jane Newbie",
                "status": "active",
                "tier": "basic"
            },
            "/search": {
                "articles": [
                    {"title": "Getting Started", "summary": "Basic setup instructions"}
                ]
            }
        }
    }
    
    # Create scenarios
    for scenario_name, config in scenarios.items():
        await mockloop.manage_mock_data(
            operation="create