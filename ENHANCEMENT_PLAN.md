# Enhanced MockLoop MCP Testing Feedback Loop Plan

## Overview

This document outlines the enhancement plan for MockLoop MCP to improve testing feedback loops for AI-assisted development. The goal is to enable coding assistants to iteratively test, analyze, and improve code using mock servers with advanced logging and analysis capabilities.

## Current State Analysis

MockLoop already provides:
- ✅ Basic request/response logging via SQLite database
- ✅ Admin UI with dashboard, request logs, and export functionality
- ✅ Admin API endpoints for requests, stats, debug, and export
- ✅ Docker containerization support
- ✅ MCP tool for generating mock servers

## Proposed Enhancements

### 1. Enhanced MCP Tools for Log Analysis

#### New MCP Tools to Add:

**1.1 `query_mock_logs` Tool**
- **Purpose**: Advanced log querying with filtering and analysis
- **Parameters**:
  - `server_url` (string): URL of the mock server
  - `time_range` (object): Start and end timestamps
  - `method` (string, optional): HTTP method filter
  - `path_pattern` (string, optional): Regex pattern for path filtering
  - `status_codes` (array, optional): Status code filters
  - `limit` (int, optional): Maximum number of results
- **Returns**: Filtered log entries with analysis metadata

**1.2 `manage_mock_data` Tool**
- **Purpose**: Dynamic response data management during testing
- **Parameters**:
  - `server_url` (string): URL of the mock server
  - `endpoint` (string): API endpoint to modify
  - `method` (string): HTTP method
  - `new_response_data` (object): New response data
  - `scenario_name` (string, optional): Named scenario for the change
- **Returns**: Updated mock configuration status

**1.3 `start_mock_server` Tool**
- **Purpose**: Start/stop mock servers programmatically
- **Parameters**:
  - `mock_name` (string): Name of the generated mock
  - `port` (int, optional): Port to run on
  - `detached_mode` (bool, optional): Run in background
- **Returns**: Server status and connection details

**1.4 `discover_mock_servers` Tool**
- **Purpose**: Find and list running mock servers
- **Parameters**:
  - `scan_ports` (array, optional): Ports to scan
  - `check_health` (bool, optional): Verify server health
- **Returns**: List of active mock servers with metadata

### 2. Enhanced Admin API Endpoints

#### New endpoints to add to generated mock servers:

**2.1 `/admin/api/logs/search`**
- **Method**: GET
- **Purpose**: Advanced log search with complex filtering
- **Query Parameters**:
  - `q`: Search query string
  - `time_from`, `time_to`: Time range filters
  - `method`: HTTP method filter
  - `status`: Status code filter
  - `path_regex`: Path pattern matching
  - `limit`, `offset`: Pagination
- **Response**: Paginated results with search highlighting

**2.2 `/admin/api/logs/analyze`**
- **Method**: GET
- **Purpose**: Log analysis and insights generation
- **Query Parameters**:
  - `time_range`: Analysis time window
  - `group_by`: Grouping criteria (endpoint, status, etc.)
- **Response**: Error patterns, performance metrics, endpoint usage statistics

**2.3 `/admin/api/mock-data/update`**
- **Method**: POST/PUT
- **Purpose**: Dynamic response updates without server restart
- **Body**:
  ```json
  {
    "endpoint": "/api/users",
    "method": "GET",
    "new_response": {...},
    "scenario_name": "test_scenario_1"
  }
  ```
- **Response**: Updated configuration status

**2.4 `/admin/api/mock-data/scenarios`**
- **Methods**: GET, POST, PUT, DELETE
- **Purpose**: Scenario management for different test configurations
- **GET**: List all scenarios
- **POST**: Create new scenario
- **PUT**: Switch to scenario or update scenario
- **DELETE**: Remove scenario

**2.5 `/admin/api/server/control`**
- **Method**: POST
- **Purpose**: Server control operations
- **Body**:
  ```json
  {
    "action": "restart|shutdown|reload-config",
    "parameters": {...}
  }
  ```
- **Response**: Operation status

**2.6 `/admin/api/testing/report`**
- **Method**: GET
- **Purpose**: Generate comprehensive testing reports
- **Query Parameters**:
  - `session_id`: Specific test session
  - `format`: Report format (json, html, csv)
- **Response**: Detailed test session analysis

### 3. Enhanced Logging and Storage

#### Database Schema Enhancements:

```sql
-- Add new columns to existing request_logs table
ALTER TABLE request_logs ADD COLUMN session_id TEXT;
ALTER TABLE request_logs ADD COLUMN test_scenario TEXT;
ALTER TABLE request_logs ADD COLUMN correlation_id TEXT;
ALTER TABLE request_logs ADD COLUMN user_agent TEXT;
ALTER TABLE request_logs ADD COLUMN response_size INTEGER;

-- New table for mock scenarios
CREATE TABLE mock_scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    config JSON NOT NULL,
    is_active BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- New table for test sessions
CREATE TABLE test_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    name TEXT,
    description TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    metadata JSON,
    total_requests INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0
);

-- New table for performance metrics
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    avg_response_time REAL,
    min_response_time REAL,
    max_response_time REAL,
    request_count INTEGER,
    error_count INTEGER,
    time_window TEXT -- '1m', '5m', '1h', etc.
);
```

### 4. AI Assistant Integration Workflow

```mermaid
sequenceDiagram
    participant AI as AI Assistant
    participant MCP as MCP Server
    participant Mock as Mock Server
    participant DB as SQLite DB
    
    AI->>MCP: generate_mock_api(openapi_spec)
    MCP->>Mock: Create mock server files
    AI->>MCP: start_mock_server(mock_name, port)
    MCP->>Mock: Start Docker container
    Mock->>DB: Initialize logging tables
    
    loop Testing Iteration
        AI->>Mock: Make test requests
        Mock->>DB: Log requests/responses with session_id
        AI->>MCP: query_mock_logs(filters, analysis)
        MCP->>Mock: Query admin API /admin/api/logs/search
        Mock->>DB: Execute filtered query
        DB->>Mock: Return results
        Mock->>MCP: Formatted log data with insights
        MCP->>AI: Analysis results and recommendations
        
        opt Update Mock Data
            AI->>MCP: manage_mock_data(endpoint, new_data)
            MCP->>Mock: POST /admin/api/mock-data/update
            Mock->>Mock: Update response handlers
            Mock->>MCP: Confirmation
        end
        
        opt Switch Test Scenario
            AI->>MCP: manage_mock_data(scenario_name)
            MCP->>Mock: PUT /admin/api/mock-data/scenarios
            Mock->>DB: Load scenario configuration
            Mock->>MCP: Scenario switched
        end
    end
    
    AI->>MCP: query_mock_logs(generate_report=true)
    MCP->>Mock: GET /admin/api/testing/report
    Mock->>DB: Aggregate session data
    Mock->>MCP: Comprehensive report
    MCP->>AI: Testing session insights and recommendations
```

### 5. Implementation Phases

#### Phase 1: Core MCP Tools (Priority 1)
**Timeline**: 1-2 weeks

1. **Add `query_mock_logs` tool** to [`src/mockloop_mcp/main.py`](src/mockloop_mcp/main.py)
   - Implement HTTP client to query mock server admin APIs
   - Add filtering and analysis logic
   - Return structured log data with insights

2. **Add `discover_mock_servers` tool**
   - Scan generated_mocks directory for active configurations
   - Check health endpoints of discovered servers
   - Return server metadata and status

3. **Enhance admin API endpoints** in generator templates
   - Update [`src/mockloop_mcp/generator.py`](src/mockloop_mcp/generator.py) to include new endpoints
   - Add `/admin/api/logs/search` endpoint
   - Add `/admin/api/logs/analyze` endpoint

4. **Database schema updates**
   - Update [`src/mockloop_mcp/templates/middleware_log_template.j2`](src/mockloop_mcp/templates/middleware_log_template.j2)
   - Add new columns to request_logs table
   - Implement automatic schema migration

#### Phase 2: Advanced Features (Priority 2)
**Timeline**: 2-3 weeks

1. **Add `manage_mock_data` tool**
   - Implement dynamic response updating
   - Add scenario management capabilities
   - Update mock server templates to support runtime configuration changes

2. **Add `start_mock_server` tool**
   - Implement Docker container management
   - Add port management and conflict resolution
   - Return connection details and health status

3. **Implement scenario management**
   - Add `/admin/api/mock-data/scenarios` endpoints
   - Create scenario storage and switching logic
   - Update admin UI to support scenario management

4. **Enhanced logging middleware**
   - Add session tracking
   - Implement correlation ID support
   - Add performance metrics collection

#### Phase 3: Analytics & Reporting (Priority 3)
**Timeline**: 1-2 weeks

1. **Advanced log analysis**
   - Implement pattern detection algorithms
   - Add performance trend analysis
   - Create automated insights generation

2. **Test session tracking**
   - Add session management endpoints
   - Implement session-based reporting
   - Add test coverage analysis

3. **Performance metrics dashboard**
   - Add real-time metrics collection
   - Implement metrics aggregation
   - Create performance alerts

### 6. File Structure Changes

```
src/mockloop_mcp/
├── main.py                           # Enhanced with new MCP tools
├── mock_server_manager.py            # New - server discovery and management
├── log_analyzer.py                   # New - advanced log analysis utilities
├── docker_manager.py                 # New - Docker container management
├── templates/
│   ├── enhanced_admin_api_template.j2    # New admin endpoints
│   ├── scenario_manager_template.j2      # Scenario management logic
│   ├── enhanced_middleware_template.j2   # Updated logging with sessions
│   ├── performance_metrics_template.j2   # Performance tracking
│   └── admin_ui_template.j2              # Updated UI with new features
└── utils/
    ├── database_utils.py             # Database migration utilities
    ├── http_client.py                # HTTP client for mock server communication
    └── analysis_utils.py             # Log analysis and pattern detection
```

### 7. Benefits for AI-Assisted Development

1. **Rapid Iteration**: AI can quickly test API changes and get immediate feedback through enhanced logging
2. **Intelligent Debugging**: Advanced log analysis helps AI identify issues and patterns faster
3. **Dynamic Testing**: AI can modify mock responses during testing without server restarts
4. **Comprehensive Reporting**: Detailed insights help AI improve code quality and identify edge cases
5. **Automated Workflows**: AI can manage entire test scenarios programmatically
6. **Performance Insights**: Real-time performance metrics enable AI to optimize code for efficiency
7. **Test Coverage**: Session tracking helps AI ensure comprehensive testing coverage

### 8. Integration with Existing Roadmap

This enhancement plan aligns with and accelerates several items from the existing roadmap:

- **Interactive Mock Configuration**: Implemented through `manage_mock_data` tool and scenario management
- **Integration with Testing Frameworks**: MCP tools enable seamless integration with AI testing workflows
- **Enhanced Response Mocking**: Dynamic response updates support realistic testing scenarios
- **Stateful Mocks**: Scenario management enables complex stateful testing workflows

### 9. Success Metrics

- **Developer Productivity**: Reduced time from code change to feedback
- **Bug Detection**: Increased early detection of issues through enhanced logging
- **Test Coverage**: Improved test scenario coverage through AI-driven testing
- **Code Quality**: Better code quality through iterative AI-assisted improvement
- **Integration Speed**: Faster integration testing with dynamic mock management

## Next Steps

1. Review and approve this enhancement plan
2. Set up development environment and branch
3. Begin Phase 1 implementation with core MCP tools
4. Iteratively test and refine features with AI assistant workflows
5. Gather feedback and adjust implementation based on real-world usage

This plan transforms MockLoop from a simple mock generator into a comprehensive testing platform that AI assistants can leverage for iterative development, debugging, and quality improvement.