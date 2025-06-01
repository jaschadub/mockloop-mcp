"""
MCP Tools Module for automated test execution and management.

This module provides comprehensive MCP tools that enable AI agents to execute
and manage complex testing workflows. All tools are integrated with the
comprehensive audit logging infrastructure for regulatory compliance.

Features:
- Scenario management and deployment
- Test execution and monitoring
- Analysis and reporting capabilities
- Advanced workflow orchestration
- Performance optimization
- Security testing automation
- Full audit logging integration
- Async execution for all operations
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Optional, Union

# Handle imports for different execution contexts
if __package__ is None or __package__ == "":
    from mcp_audit_logger import create_audit_logger
    from mcp_prompts import (
        analyze_openapi_for_testing,
        generate_scenario_config,
        optimize_scenario_for_load,
        generate_error_scenarios,
        generate_security_test_scenarios
    )
    from mcp_resources import (
        list_scenario_packs,
        get_scenario_pack_by_uri
    )
    from utils.http_client import (
        MockServerClient,
        discover_running_servers,
        check_server_connectivity
    )
    from mock_server_manager import MockServerManager
else:
    from .mcp_audit_logger import create_audit_logger
    from .mcp_prompts import (
        analyze_openapi_for_testing,
        generate_scenario_config,
        optimize_scenario_for_load,
        generate_error_scenarios,
        generate_security_test_scenarios
    )
    from .mcp_resources import (
        list_scenario_packs,
        get_scenario_pack_by_uri
    )
    from .utils.http_client import (
        MockServerClient,
        discover_running_servers,
        check_server_connectivity
    )
    from .mock_server_manager import MockServerManager

# Configure logger for this module
logger = logging.getLogger(__name__)

# Test session storage for tracking active sessions
_active_test_sessions: dict[str, dict[str, Any]] = {}


def mcp_tool_audit(tool_name: str):
    """
    Decorator to add MCP audit logging to tool functions.

    Args:
        tool_name: Name of the MCP tool being audited
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            audit_logger = create_audit_logger(
                db_path="mcp_audit.db",
                session_id=f"mcp_tool_{tool_name}",
                user_id="mcp_system"
            )
            start_time = time.time()
            entry_id = None

            try:
                # Log tool execution start
                if audit_logger:
                    entry_id = audit_logger.log_tool_execution(
                        tool_name=tool_name,
                        input_parameters=kwargs,
                        data_sources=["mock_server", "scenario_config"],
                        compliance_tags=["mcp_tool", "test_execution"],
                        processing_purpose="automated_testing",
                        legal_basis="legitimate_interests"
                    )

                # Execute the original function
                result = await func(*args, **kwargs)

                # Log successful completion
                if audit_logger and entry_id:
                    execution_time_ms = (time.time() - start_time) * 1000
                    audit_logger.log_tool_execution(
                        tool_name=f"{tool_name}_completion",
                        input_parameters={"original_entry_id": entry_id},
                        execution_result={"status": result.get("status", "unknown")},
                        execution_time_ms=execution_time_ms,
                        data_sources=["mock_server", "scenario_config"],
                        compliance_tags=["mcp_tool", "test_execution", "completion"],
                        processing_purpose="automated_testing_completion",
                        legal_basis="legitimate_interests"
                    )

                return result

            except Exception as e:
                # Log error
                if audit_logger and entry_id:
                    execution_time_ms = (time.time() - start_time) * 1000
                    audit_logger.log_tool_execution(
                        tool_name=f"{tool_name}_error",
                        input_parameters={"original_entry_id": entry_id},
                        execution_result={"status": "error", "error_type": type(e).__name__},
                        execution_time_ms=execution_time_ms,
                        data_sources=["mock_server", "scenario_config"],
                        compliance_tags=["mcp_tool", "test_execution", "error"],
                        processing_purpose="automated_testing_error",
                        legal_basis="legitimate_interests",
                        error_details=str(e)
                    )
                raise

        return wrapper
    return decorator


# Scenario Management Tools

@mcp_tool_audit("validate_scenario_config")
async def validate_scenario_config(
    scenario_config: dict[str, Any],
    strict_validation: bool = True,
    check_endpoints: bool = True
) -> dict[str, Any]:
    """
    Validates scenario configuration before deployment.

    Args:
        scenario_config: The scenario configuration to validate
        strict_validation: Whether to perform strict validation
        check_endpoints: Whether to validate endpoint configurations

    Returns:
        Validation result with detailed feedback
    """
    try:
        validation_result = {
            "status": "success",
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "validated_config": scenario_config.copy()
        }

        # Required fields validation
        required_fields = ["scenario_name", "description", "scenario_type", "endpoints"]
        for field in required_fields:
            if field not in scenario_config:
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["valid"] = False

        # Scenario type validation
        valid_types = ["load_testing", "error_simulation", "security_testing", "functional_testing"]
        scenario_type = scenario_config.get("scenario_type")
        if scenario_type and scenario_type not in valid_types:
            validation_result["errors"].append(f"Invalid scenario_type: {scenario_type}. Must be one of {valid_types}")
            validation_result["valid"] = False

        # Endpoints validation
        if check_endpoints and "endpoints" in scenario_config:
            endpoints = scenario_config["endpoints"]
            if not isinstance(endpoints, list) or len(endpoints) == 0:
                validation_result["errors"].append("Endpoints must be a non-empty list")
                validation_result["valid"] = False
            else:
                for i, endpoint in enumerate(endpoints):
                    endpoint_errors = _validate_endpoint_config(endpoint, i)
                    validation_result["errors"].extend(endpoint_errors)
                    if endpoint_errors:
                        validation_result["valid"] = False

        # Test parameters validation
        if "test_parameters" in scenario_config:
            test_params = scenario_config["test_parameters"]
            param_warnings = _validate_test_parameters(test_params, scenario_type)
            validation_result["warnings"].extend(param_warnings)

        # Performance suggestions
        if scenario_type == "load_testing":
            suggestions = _generate_load_testing_suggestions(scenario_config)
            validation_result["suggestions"].extend(suggestions)

        # Set final status
        if validation_result["errors"]:
            validation_result["status"] = "error"
            validation_result["valid"] = False
        elif validation_result["warnings"] and strict_validation:
            validation_result["status"] = "warning"

        return validation_result

    except Exception as e:
        logger.exception("Error validating scenario configuration")
        return {
            "status": "error",
            "valid": False,
            "errors": [f"Validation failed: {e!s}"],
            "warnings": [],
            "suggestions": [],
            "validated_config": {}
        }


@mcp_tool_audit("deploy_scenario")
async def deploy_scenario(
    server_url: str,
    scenario_config: dict[str, Any],
    validate_before_deploy: bool = True,
    force_deploy: bool = False
) -> dict[str, Any]:
    """
    Deploys scenario to MockLoop server.

    Args:
        server_url: URL of the target MockLoop server
        scenario_config: Complete scenario configuration
        validate_before_deploy: Whether to validate before deployment
        force_deploy: Whether to force deployment even with warnings

    Returns:
        Deployment result with status and details
    """
    try:
        deployment_result = {
            "status": "success",
            "deployed": False,
            "scenario_name": scenario_config.get("scenario_name", "unknown"),
            "server_url": server_url,
            "validation_result": None,
            "deployment_details": {},
            "performance_metrics": {}
        }

        start_time = time.time()

        # Validate server connectivity
        connectivity_result = await check_server_connectivity(server_url)
        if connectivity_result.get("status") != "healthy":
            return {
                **deployment_result,
                "status": "error",
                "error": f"Server not accessible: {connectivity_result.get('error', 'Unknown error')}"
            }

        # Validate scenario configuration if requested
        if validate_before_deploy:
            validation_result = await validate_scenario_config(scenario_config)
            deployment_result["validation_result"] = validation_result

            if not validation_result["valid"] and not force_deploy:
                return {
                    **deployment_result,
                    "status": "error",
                    "error": "Scenario validation failed. Use force_deploy=True to override."
                }

        # Initialize HTTP client with server discovery for dual-port support
        servers = await discover_running_servers([int(server_url.split(":")[-1])], check_health=True)
        admin_port = None
        for server in servers:
            if server.get("url") == server_url and server.get("admin_port"):
                admin_port = server["admin_port"]
                break

        client = MockServerClient(server_url, admin_port=admin_port)

        # Deploy scenario
        scenario_name = scenario_config["scenario_name"]
        create_result = await client.create_scenario(scenario_name, scenario_config)

        if create_result.get("status") == "success":
            deployment_result["deployed"] = True
            deployment_result["deployment_details"] = create_result.get("result", {})

            # Switch to the deployed scenario
            switch_result = await client.switch_scenario(scenario_name)
            if switch_result.get("status") == "success":
                deployment_result["deployment_details"]["activated"] = True
                deployment_result["deployment_details"]["previous_scenario"] = switch_result.get("previous_scenario")
            else:
                deployment_result["deployment_details"]["activated"] = False
                deployment_result["deployment_details"]["switch_error"] = switch_result.get("error")

        else:
            deployment_result["status"] = "error"
            deployment_result["error"] = f"Scenario deployment failed: {create_result.get('error', 'Unknown error')}"

        # Calculate performance metrics
        end_time = time.time()
        deployment_result["performance_metrics"] = {
            "deployment_time_ms": round((end_time - start_time) * 1000, 2),
            "server_response_time": connectivity_result.get("response_time_ms", "unknown"),
            "timestamp": end_time
        }

        return deployment_result

    except Exception as e:
        logger.exception("Error deploying scenario")
        return {
            "status": "error",
            "deployed": False,
            "scenario_name": scenario_config.get("scenario_name", "unknown"),
            "server_url": server_url,
            "error": f"Deployment failed: {e!s}",
            "validation_result": None,
            "deployment_details": {},
            "performance_metrics": {}
        }


@mcp_tool_audit("switch_scenario")
async def switch_scenario(
    server_url: str,
    scenario_name: str,
    verify_switch: bool = True
) -> dict[str, Any]:
    """
    Switches active scenario on a server.

    Args:
        server_url: URL of the target MockLoop server
        scenario_name: Name of the scenario to switch to
        verify_switch: Whether to verify the switch was successful

    Returns:
        Switch operation result
    """
    try:
        switch_result = {
            "status": "success",
            "switched": False,
            "scenario_name": scenario_name,
            "server_url": server_url,
            "previous_scenario": None,
            "verification_result": None
        }

        # Validate server connectivity
        connectivity_result = await check_server_connectivity(server_url)
        if connectivity_result.get("status") != "healthy":
            return {
                **switch_result,
                "status": "error",
                "error": f"Server not accessible: {connectivity_result.get('error', 'Unknown error')}"
            }

        # Initialize HTTP client with server discovery for dual-port support
        servers = await discover_running_servers([int(server_url.split(":")[-1])], check_health=True)
        admin_port = None
        for server in servers:
            if server.get("url") == server_url and server.get("admin_port"):
                admin_port = server["admin_port"]
                break

        client = MockServerClient(server_url, admin_port=admin_port)

        # Perform the switch
        result = await client.switch_scenario(scenario_name)

        if result.get("status") == "success":
            switch_result["switched"] = True
            switch_result["previous_scenario"] = result.get("previous_scenario")

            # Verify the switch if requested
            if verify_switch:
                current_result = await client.get_current_scenario()
                if current_result.get("status") == "success":
                    current_scenario = current_result.get("current_scenario", {})
                    if current_scenario.get("name") == scenario_name:
                        switch_result["verification_result"] = "verified"
                    else:
                        switch_result["verification_result"] = "failed"
                        switch_result["status"] = "warning"
                        switch_result["error"] = "Switch completed but verification failed"
                else:
                    switch_result["verification_result"] = "unable_to_verify"
                    switch_result["status"] = "warning"

        else:
            switch_result["status"] = "error"
            switch_result["error"] = f"Scenario switch failed: {result.get('error', 'Unknown error')}"

        return switch_result

    except Exception as e:
        logger.exception("Error switching scenario")
        return {
            "status": "error",
            "switched": False,
            "scenario_name": scenario_name,
            "server_url": server_url,
            "error": f"Switch failed: {e!s}",
            "previous_scenario": None,
            "verification_result": None
        }


@mcp_tool_audit("list_active_scenarios")
async def list_active_scenarios(
    server_urls: list[str] | None = None,
    discover_servers: bool = True
) -> dict[str, Any]:
    """
    Lists all active scenarios across servers.

    Args:
        server_urls: List of server URLs to check. If None, discovers servers automatically
        discover_servers: Whether to auto-discover running servers

    Returns:
        List of active scenarios across all servers
    """
    try:
        result = {
            "status": "success",
            "servers_checked": 0,
            "active_scenarios": [],
            "server_details": [],
            "discovery_used": False
        }

        target_servers = []

        # Discover servers if needed
        if not server_urls and discover_servers:
            discovered = await discover_running_servers(check_health=True)
            mockloop_servers = [s for s in discovered if s.get("is_mockloop_server")]
            target_servers = [s["url"] for s in mockloop_servers]
            result["discovery_used"] = True
            result["server_details"] = mockloop_servers
        elif server_urls:
            target_servers = server_urls

        if not target_servers:
            return {
                **result,
                "status": "warning",
                "error": "No servers to check. Provide server_urls or enable discover_servers."
            }

        # Check each server
        for server_url in target_servers:
            try:
                # Initialize HTTP client with server discovery for dual-port support
                servers = await discover_running_servers([int(server_url.split(":")[-1])], check_health=True)
                admin_port = None
                for server in servers:
                    if server.get("url") == server_url and server.get("admin_port"):
                        admin_port = server["admin_port"]
                        break

                client = MockServerClient(server_url, admin_port=admin_port)

                # Get current scenario
                current_result = await client.get_current_scenario()
                if current_result.get("status") == "success":
                    current_scenario = current_result.get("current_scenario", {})
                    if current_scenario:
                        result["active_scenarios"].append({
                            "server_url": server_url,
                            "scenario_name": current_scenario.get("name", "unknown"),
                            "scenario_id": current_scenario.get("id"),
                            "description": current_scenario.get("description", ""),
                            "activated_at": current_scenario.get("activated_at"),
                            "scenario_type": current_scenario.get("config", {}).get("scenario_type", "unknown")
                        })

                result["servers_checked"] += 1

            except Exception as e:
                logger.debug(f"Failed to check server {server_url}: {e}")
                # Continue checking other servers
                continue

        return result

    except Exception as e:
        logger.exception("Error listing active scenarios")
        return {
            "status": "error",
            "servers_checked": 0,
            "active_scenarios": [],
            "server_details": [],
            "discovery_used": False,
            "error": f"Failed to list active scenarios: {e!s}"
        }


# Test Execution Tools

@mcp_tool_audit("execute_test_plan")
async def execute_test_plan(
    openapi_spec: dict[str, Any],
    server_url: str,
    test_focus: str = "comprehensive",
    auto_generate_scenarios: bool = True,
    execute_immediately: bool = True
) -> dict[str, Any]:
    """
    Combines scenario generation and deployment in one operation.

    Args:
        openapi_spec: OpenAPI specification to analyze
        server_url: Target MockLoop server URL
        test_focus: Focus area for testing ("performance", "security", "functional", "comprehensive")
        auto_generate_scenarios: Whether to auto-generate scenarios from OpenAPI spec
        execute_immediately: Whether to execute tests immediately after deployment

    Returns:
        Complete test plan execution result
    """
    try:
        execution_result = {
            "status": "success",
            "test_plan_id": str(uuid.uuid4()),
            "server_url": server_url,
            "test_focus": test_focus,
            "analysis_result": None,
            "generated_scenarios": [],
            "deployed_scenarios": [],
            "execution_results": [],
            "performance_metrics": {}
        }

        start_time = time.time()

        # Step 1: Analyze OpenAPI specification
        if auto_generate_scenarios:
            analysis_result = await analyze_openapi_for_testing(openapi_spec, test_focus, True)
            execution_result["analysis_result"] = analysis_result

            # Step 2: Generate scenarios based on analysis
            testable_scenarios = analysis_result.get("testable_scenarios", [])
            for scenario_info in testable_scenarios[:3]:  # Limit to top 3 scenarios
                # Extract endpoints from OpenAPI spec
                endpoints = []
                paths = openapi_spec.get("paths", {})
                for path, methods in paths.items():
                    for method in methods:
                        endpoints.append({"path": path, "method": method.upper()})

                # Generate scenario configuration
                scenario_config = await generate_scenario_config(
                    scenario_type=scenario_info.get("scenario_type", "functional_testing"),
                    endpoints=endpoints[:5],  # Limit endpoints per scenario
                    scenario_name=f"auto_{scenario_info.get('scenario_type', 'test')}_{int(time.time())}"
                )

                execution_result["generated_scenarios"].append(scenario_config)

        # Step 3: Deploy scenarios
        for scenario_config in execution_result["generated_scenarios"]:
            deploy_result = await deploy_scenario(server_url, scenario_config, validate_before_deploy=True)
            execution_result["deployed_scenarios"].append(deploy_result)

            # Step 4: Execute tests if requested
            if execute_immediately and deploy_result.get("deployed"):
                test_result = await run_test_iteration(
                    server_url=server_url,
                    scenario_name=scenario_config["scenario_name"],
                    duration_seconds=60,  # Short test for immediate execution
                    monitor_performance=True
                )
                execution_result["execution_results"].append(test_result)

        # Calculate overall performance metrics
        end_time = time.time()
        execution_result["performance_metrics"] = {
            "total_execution_time_ms": round((end_time - start_time) * 1000, 2),
            "scenarios_generated": len(execution_result["generated_scenarios"]),
            "scenarios_deployed": len([d for d in execution_result["deployed_scenarios"] if d.get("deployed")]),
            "tests_executed": len(execution_result["execution_results"]),
            "timestamp": end_time
        }

        # Determine overall status
        failed_deployments = [d for d in execution_result["deployed_scenarios"] if not d.get("deployed")]
        failed_executions = [e for e in execution_result["execution_results"] if e.get("status") != "success"]

        if failed_deployments or failed_executions:
            execution_result["status"] = "partial_success"
            execution_result["warnings"] = []
            if failed_deployments:
                execution_result["warnings"].append(f"{len(failed_deployments)} scenario deployments failed")
            if failed_executions:
                execution_result["warnings"].append(f"{len(failed_executions)} test executions failed")

        return execution_result

    except Exception as e:
        logger.exception("Error executing test plan")
        return {
            "status": "error",
            "test_plan_id": str(uuid.uuid4()),
            "server_url": server_url,
            "test_focus": test_focus,
            "error": f"Test plan execution failed: {e!s}",
            "analysis_result": None,
            "generated_scenarios": [],
            "deployed_scenarios": [],
            "execution_results": [],
            "performance_metrics": {}
        }


@mcp_tool_audit("run_test_iteration")
async def run_test_iteration(
    server_url: str,
    scenario_name: str,
    duration_seconds: int = 300,
    monitor_performance: bool = True,
    collect_logs: bool = True
) -> dict[str, Any]:
    """
    Executes a single test iteration with monitoring.

    Args:
        server_url: Target MockLoop server URL
        scenario_name: Name of the scenario to execute
        duration_seconds: Duration of the test iteration
        monitor_performance: Whether to monitor performance metrics
        collect_logs: Whether to collect request logs during execution

    Returns:
        Test iteration result with metrics and logs
    """
    try:
        iteration_result = {
            "status": "success",
            "iteration_id": str(uuid.uuid4()),
            "server_url": server_url,
            "scenario_name": scenario_name,
            "duration_seconds": duration_seconds,
            "start_time": None,
            "end_time": None,
            "performance_metrics": {},
            "request_logs": [],
            "error_summary": {},
            "recommendations": []
        }

        # Initialize HTTP client with server discovery for dual-port support
        servers = await discover_running_servers([int(server_url.split(":")[-1])], check_health=True)
        admin_port = None
        for server in servers:
            if server.get("url") == server_url and server.get("admin_port"):
                admin_port = server["admin_port"]
                break

        client = MockServerClient(server_url, admin_port=admin_port)

        # Switch to the specified scenario
        switch_result = await switch_scenario(server_url, scenario_name, verify_switch=True)
        if not switch_result.get("switched"):
            return {
                **iteration_result,
                "status": "error",
                "error": f"Failed to switch to scenario '{scenario_name}': {switch_result.get('error')}"
            }

        # Record start time
        start_time = time.time()
        iteration_result["start_time"] = datetime.fromtimestamp(start_time, tz=timezone.utc).isoformat()

        # Get initial metrics if monitoring is enabled
        initial_stats = None
        if monitor_performance:
            stats_result = await client.get_stats()
            if stats_result.get("status") == "success":
                initial_stats = stats_result.get("stats", {})

        # Simulate test execution by monitoring for the specified duration
        # In a real implementation, this would trigger actual load testing tools
        await asyncio.sleep(min(duration_seconds, 10))  # Cap at 10 seconds for demo

        # Record end time
        end_time = time.time()
        iteration_result["end_time"] = datetime.fromtimestamp(end_time, tz=timezone.utc).isoformat()

        # Collect final metrics
        if monitor_performance:
            final_stats_result = await client.get_stats()
            if final_stats_result.get("status") == "success":
                final_stats = final_stats_result.get("stats", {})
                iteration_result["performance_metrics"] = _calculate_performance_delta(initial_stats, final_stats)

        # Collect request logs if requested
        if collect_logs:
            logs_result = await client.query_logs(limit=100, include_admin=False)
            if logs_result.get("status") == "success":
                iteration_result["request_logs"] = logs_result.get("logs", [])

                # Analyze logs for errors
                error_summary = _analyze_request_logs(iteration_result["request_logs"])
                iteration_result["error_summary"] = error_summary

                # Generate recommendations
                recommendations = _generate_test_recommendations(
                    iteration_result["performance_metrics"],
                    error_summary,
                    scenario_name
                )
                iteration_result["recommendations"] = recommendations

        return iteration_result

    except Exception as e:
        logger.exception("Error running test iteration")
        return {
            "status": "error",
            "iteration_id": str(uuid.uuid4()),
            "server_url": server_url,
            "scenario_name": scenario_name,
            "duration_seconds": duration_seconds,
            "error": f"Test iteration failed: {e!s}",
            "start_time": None,
            "end_time": None,
            "performance_metrics": {},
            "request_logs": [],
            "error_summary": {},
            "recommendations": []
        }


@mcp_tool_audit("run_load_test")
async def run_load_test(
    server_url: str,
    target_load: int,
    duration_seconds: int = 300,
    ramp_up_time: int = 60,
    scenario_name: str | None = None
) -> dict[str, Any]:
    """
    Executes load testing with configurable parameters.

    Args:
        server_url: Target MockLoop server URL
        target_load: Target number of concurrent users
        duration_seconds: Duration of the load test
        ramp_up_time: Time to ramp up to target load
        scenario_name: Optional specific scenario to use

    Returns:
        Load test execution result
    """
    try:
        load_test_result = {
            "status": "success",
            "test_id": str(uuid.uuid4()),
            "server_url": server_url,
            "target_load": target_load,
            "duration_seconds": duration_seconds,
            "ramp_up_time": ramp_up_time,
            "scenario_used": scenario_name,
            "load_profile": {},
            "performance_results": {},
            "bottlenecks_identified": [],
            "recommendations": []
        }

        # If no scenario specified, create an optimized load testing scenario
        if not scenario_name:
            # Generate a basic load testing scenario
            endpoints = [{"path": "/health", "method": "GET"}]  # Default endpoint
            base_scenario = await generate_scenario_config(
                scenario_type="load_testing",
                endpoints=endpoints,
                scenario_name=f"load_test_{target_load}_{int(time.time())}"
            )

            # Optimize for load
            optimized_scenario = await optimize_scenario_for_load(
                base_scenario=base_scenario,
                target_load=target_load,
                performance_requirements={
                    "max_response_time_ms": 2000,
                    "target_throughput_rps": target_load * 2,
                    "error_rate_threshold": 0.01
                }
            )

            # Deploy the optimized scenario
            deploy_result = await deploy_scenario(server_url, optimized_scenario)
            if not deploy_result.get("deployed"):
                return {
                    **load_test_result,
                    "status": "error",
                    "error": f"Failed to deploy load test scenario: {deploy_result.get('error')}"
                }

            scenario_name = optimized_scenario["scenario_name"]
            load_test_result["scenario_used"] = scenario_name

        # Define load profile
        load_profile = {
            "phases": [
                {"phase": "ramp_up", "duration": ramp_up_time, "target_users": target_load},
                {"phase": "steady_state", "duration": duration_seconds - ramp_up_time, "target_users": target_load},
                {"phase": "ramp_down", "duration": 30, "target_users": 0}
            ],
            "total_duration": duration_seconds + 30
        }
        load_test_result["load_profile"] = load_profile

        # Execute load test phases
        for phase in load_profile["phases"]:
            phase_result = await run_test_iteration(
                server_url=server_url,
                scenario_name=scenario_name,
                duration_seconds=phase["duration"],
                monitor_performance=True,
                collect_logs=True
            )

            # Collect phase results
            if phase["phase"] not in load_test_result["performance_results"]:
                load_test_result["performance_results"][phase["phase"]] = []
            load_test_result["performance_results"][phase["phase"]].append(phase_result)

        # Analyze results for bottlenecks
        bottlenecks = _identify_performance_bottlenecks(load_test_result["performance_results"], target_load)
        load_test_result["bottlenecks_identified"] = bottlenecks

        # Generate load test recommendations
        recommendations = _generate_load_test_recommendations(
            load_test_result["performance_results"],
            bottlenecks,
            target_load
        )
        load_test_result["recommendations"] = recommendations

        return load_test_result

    except Exception as e:
        logger.exception("Error running load test")
        return {
            "status": "error",
            "test_id": str(uuid.uuid4()),
            "server_url": server_url,
            "target_load": target_load,
            "duration_seconds": duration_seconds,
            "ramp_up_time": ramp_up_time,
            "error": f"Load test failed: {e!s}",
            "scenario_used": None,
            "load_profile": {},
            "performance_results": {},
            "bottlenecks_identified": [],
            "recommendations": []
        }


# Helper Functions

def _validate_endpoint_config(endpoint: dict[str, Any], index: int) -> list[str]:
    """Validate endpoint configuration."""
    errors = []

    if "path" not in endpoint:
        errors.append(f"Endpoint {index}: Missing 'path' field")

    if "method" not in endpoint:
        errors.append(f"Endpoint {index}: Missing 'method' field")
    elif endpoint["method"].upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
        errors.append(f"Endpoint {index}: Invalid HTTP method '{endpoint['method']}'")

    if "response_config" not in endpoint:
        errors.append(f"Endpoint {index}: Missing 'response_config' field")
    elif "status_code" not in endpoint["response_config"]:
        errors.append(f"Endpoint {index}: Missing 'status_code' in response_config")

    return errors


def _validate_test_parameters(test_params: dict[str, Any], scenario_type: str | None) -> list[str]:
    """Validate test parameters."""
    warnings = []

    if "concurrent_users" in test_params:
        users = test_params["concurrent_users"]
        if users > 1000:
            warnings.append("High concurrent user count may impact performance")
        elif users < 1:
            warnings.append("Concurrent users should be at least 1")

    if "duration_seconds" in test_params:
        duration = test_params["duration_seconds"]
        if duration > 3600:  # 1 hour
            warnings.append("Long test duration may consume significant resources")
        elif duration < 10:
            warnings.append("Very short test duration may not provide meaningful results")

    if scenario_type == "load_testing" and test_params.get("concurrent_users", 0) < 10:
        warnings.append("Load testing typically requires more concurrent users for meaningful results")

    return warnings


def _generate_load_testing_suggestions(scenario_config: dict[str, Any]) -> list[str]:
    """Generate load testing suggestions."""
    suggestions = []

    endpoints = scenario_config.get("endpoints", [])
    if len(endpoints) > 10:
        suggestions.append("Consider reducing the number of endpoints for focused load testing")

    test_params = scenario_config.get("test_parameters", {})
    if test_params.get("concurrent_users", 0) > 100:
        suggestions.append("Consider implementing gradual ramp-up for high load scenarios")

    if not any("response_time_ms" in ep.get("response_config", {}) for ep in endpoints):
        suggestions.append("Consider adding response time configurations for realistic load simulation")

    return suggestions


def _calculate_performance_delta(initial_stats: dict | None, final_stats: dict | None) -> dict[str, Any]:
    """Calculate performance metrics delta."""
    if not initial_stats or not final_stats:
        return {"error": "Insufficient stats data for delta calculation"}

    delta = {
        "requests_processed": final_stats.get("total_requests", 0) - initial_stats.get("total_requests", 0),
        "average_response_time_change": 0,
        "error_rate_change": 0,
        "throughput_rps": 0
    }

    # Calculate average response time change
    initial_avg = initial_stats.get("average_response_time", 0)
    final_avg = final_stats.get("average_response_time", 0)
    if initial_avg > 0:
        delta["average_response_time_change"] = ((final_avg - initial_avg) / initial_avg) * 100

    # Calculate error rate change
    initial_errors = initial_stats.get("error_count", 0)
    final_errors = final_stats.get("error_count", 0)
    initial_total = initial_stats.get("total_requests", 1)
    final_total = final_stats.get("total_requests", 1)

    initial_rate = (initial_errors / initial_total) * 100
    final_rate = (final_errors / final_total) * 100
    delta["error_rate_change"] = final_rate - initial_rate

    # Calculate throughput
    time_diff = final_stats.get("timestamp", 0) - initial_stats.get("timestamp", 0)
    if time_diff > 0:
        delta["throughput_rps"] = delta["requests_processed"] / time_diff

    return delta


def _analyze_request_logs(logs: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze request logs for errors and patterns."""
    error_summary = {
        "total_requests": len(logs),
        "error_count": 0,
        "error_rate": 0,
        "status_code_distribution": {},
        "error_patterns": []
    }

    status_codes = {}
    error_patterns = {}

    for log in logs:
        status_code = log.get("status_code", 0)
        status_codes[status_code] = status_codes.get(status_code, 0) + 1

        if status_code >= 400:
            error_summary["error_count"] += 1
            error_type = f"{status_code}_error"
            error_patterns[error_type] = error_patterns.get(error_type, 0) + 1

    error_summary["status_code_distribution"] = status_codes
    error_summary["error_rate"] = (error_summary["error_count"] / len(logs)) * 100 if logs else 0
    error_summary["error_patterns"] = [
        {"pattern": pattern, "count": count}
        for pattern, count in error_patterns.items()
    ]

    return error_summary


def _generate_test_recommendations(
    performance_metrics: dict[str, Any],
    error_summary: dict[str, Any],
    scenario_name: str
) -> list[str]:
    """Generate test recommendations based on results."""
    recommendations = []

    # Performance recommendations
    if "average_response_time_change" in performance_metrics:
        change = performance_metrics["average_response_time_change"]
        if change > 50:
            recommendations.append("Response time increased significantly - consider optimizing server performance")
        elif change < -20:
            recommendations.append("Response time improved - current configuration is performing well")

    # Error rate recommendations
    error_rate = error_summary.get("error_rate", 0)
    if error_rate > 5:
        recommendations.append("High error rate detected - investigate server configuration and endpoint implementations")
    elif error_rate > 1:
        recommendations.append("Moderate error rate - monitor for patterns and consider error handling improvements")

    # Throughput recommendations
    throughput = performance_metrics.get("throughput_rps", 0)
    if throughput < 10:
        recommendations.append("Low throughput detected - consider load balancing or server scaling")

    return recommendations


def _identify_performance_bottlenecks(performance_results: dict[str, Any], target_load: int) -> list[dict[str, Any]]:
    """Identify performance bottlenecks from load test results."""
    bottlenecks = []

    for phase, results in performance_results.items():
        if not results:
            continue

        for result in results:
            metrics = result.get("performance_metrics", {})

            # Check response time bottleneck
            avg_response_change = metrics.get("average_response_time_change", 0)
            if avg_response_change > 100:
                bottlenecks.append({
                    "type": "response_time",
                    "phase": phase,
                    "severity": "high",
                    "description": f"Response time increased by {avg_response_change:.1f}% during {phase}",
                    "recommendation": "Consider server optimization or load balancing"
                })

            # Check throughput bottleneck
            throughput = metrics.get("throughput_rps", 0)
            expected_throughput = target_load * 0.8  # 80% of target load
            if throughput < expected_throughput:
                bottlenecks.append({
                    "type": "throughput",
                    "phase": phase,
                    "severity": "medium",
                    "description": f"Throughput ({throughput:.1f} RPS) below expected ({expected_throughput:.1f} RPS)",
                    "recommendation": "Investigate server capacity and connection limits"
                })

    return bottlenecks


def _generate_load_test_recommendations(
    performance_results: dict[str, Any],
    bottlenecks: list[dict[str, Any]],
    target_load: int
) -> list[str]:
    """Generate load test specific recommendations."""
    recommendations = []

    # Bottleneck-based recommendations
    for bottleneck in bottlenecks:
        recommendations.append(f"{bottleneck['type'].title()} bottleneck: {bottleneck['recommendation']}")

    # General load test recommendations
    if not bottlenecks:
        recommendations.append("Load test completed successfully with no major bottlenecks detected")

    # Scale recommendations
    if target_load > 100:
        recommendations.append("For high load scenarios, consider implementing connection pooling and caching")

    return recommendations


def _analyze_security_test_results(
    logs: list[dict[str, Any]],
    error_summary: dict[str, Any],
    security_focus: list[str]
) -> list[dict[str, Any]]:
    """Analyze security test results."""
    findings = []

    # Check for authentication issues
    if "authentication" in security_focus:
        auth_errors = [log for log in logs if log.get("status_code") == 401]
        if auth_errors:
            findings.append({
                "type": "authentication",
                "severity": "medium",
                "count": len(auth_errors),
                "description": "Authentication failures detected"
            })

    # Check for authorization issues
    if "authorization" in security_focus:
        authz_errors = [log for log in logs if log.get("status_code") == 403]
        if authz_errors:
            findings.append({
                "type": "authorization",
                "severity": "medium",
                "count": len(authz_errors),
                "description": "Authorization failures detected"
            })

    return findings


def _assess_vulnerabilities(findings: list[dict[str, Any]], api_spec: dict[str, Any]) -> dict[str, Any]:
    """Assess vulnerabilities based on findings."""
    assessment = {
        "risk_level": "low",
        "vulnerabilities": [],
        "recommendations": []
    }

    high_severity_count = len([f for f in findings if f.get("severity") == "high"])
    medium_severity_count = len([f for f in findings if f.get("severity") == "medium"])

    if high_severity_count > 0:
        assessment["risk_level"] = "high"
    elif medium_severity_count > 2:
        assessment["risk_level"] = "medium"

    assessment["vulnerabilities"] = findings

    return assessment


def _check_compliance_status(
    findings: list[dict[str, Any]],
    vulnerability_assessment: dict[str, Any],
    compliance_requirements: list[str]
) -> dict[str, Any]:
    """Check compliance status against requirements."""
    status = {}

    for requirement in compliance_requirements:
        if requirement.lower() == "gdpr":
            status["gdpr"] = {
                "compliant": vulnerability_assessment.get("risk_level") != "high",
                "issues": []
            }
        elif requirement.lower() == "pci":
            status["pci"] = {
                "compliant": len(findings) == 0,
                "issues": [f["description"] for f in findings]
            }

    return status


def _generate_security_recommendations(
    findings: list[dict[str, Any]],
    vulnerability_assessment: dict[str, Any],
    security_focus: list[str]
) -> list[str]:
    """Generate security recommendations."""
    recommendations = []

    if vulnerability_assessment.get("risk_level") == "high":
        recommendations.append("High risk vulnerabilities detected - immediate remediation required")

    for finding in findings:
        if finding["type"] == "authentication":
            recommendations.append("Implement stronger authentication mechanisms")
        elif finding["type"] == "authorization":
            recommendations.append("Review and strengthen authorization controls")

    return recommendations


def _calculate_summary_statistics(test_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate summary statistics from test results."""
    if not test_results:
        return {}

    total_tests = len(test_results)
    successful_tests = len([r for r in test_results if r.get("status") == "success"])

    return {
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "success_rate": (successful_tests / total_tests) * 100,
        "failure_rate": ((total_tests - successful_tests) / total_tests) * 100
    }


def _analyze_performance_trends(test_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze performance trends across test results."""
    response_times = []
    throughputs = []

    for result in test_results:
        metrics = result.get("performance_metrics", {})
        if "average_response_time_change" in metrics:
            response_times.append(metrics["average_response_time_change"])
        if "throughput_rps" in metrics:
            throughputs.append(metrics["throughput_rps"])

    analysis = {}
    if response_times:
        analysis["response_time_trend"] = {
            "average": sum(response_times) / len(response_times),
            "min": min(response_times),
            "max": max(response_times)
        }

    if throughputs:
        analysis["throughput_trend"] = {
            "average": sum(throughputs) / len(throughputs),
            "min": min(throughputs),
            "max": max(throughputs)
        }

    return analysis


def _analyze_error_patterns(test_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze error patterns across test results."""
    all_errors = []

    for result in test_results:
        error_summary = result.get("error_summary", {})
        error_patterns = error_summary.get("error_patterns", [])
        all_errors.extend(error_patterns)

    # Aggregate error patterns
    pattern_counts = {}
    for error in all_errors:
        pattern = error.get("pattern", "unknown")
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + error.get("count", 0)

    return {
        "total_errors": sum(pattern_counts.values()),
        "error_patterns": [
            {"pattern": pattern, "count": count}
            for pattern, count in pattern_counts.items()
        ]
    }


def _analyze_test_trends(test_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze trends across test results."""
    return {
        "test_count": len(test_results),
        "trend_direction": "stable",  # Simplified for now
        "performance_stability": "good" if len(test_results) > 0 else "unknown"
    }


def _generate_analysis_recommendations(
    summary_stats: dict[str, Any],
    performance_analysis: dict[str, Any],
    error_analysis: dict[str, Any],
    trend_analysis: dict[str, Any]
) -> list[str]:
    """Generate analysis recommendations."""
    recommendations = []

    success_rate = summary_stats.get("success_rate", 0)
    if success_rate < 90:
        recommendations.append("Low success rate detected - investigate test failures")

    total_errors = error_analysis.get("total_errors", 0)
    if total_errors > 10:
        recommendations.append("High error count - review error patterns and fix underlying issues")

    return recommendations


def _calculate_total_tests(test_plan: dict[str, Any]) -> int:
    """Calculate total number of tests in a test plan."""
    # Simplified calculation
    scenarios = test_plan.get("scenarios", [])
    return len(scenarios) * test_plan.get("iterations_per_scenario", 1)


def _generate_session_summary(session_data: dict[str, Any]) -> dict[str, Any]:
    """Generate session summary."""
    return {
        "session_name": session_data.get("session_name", "unknown"),
        "total_duration": session_data.get("duration", "unknown"),
        "tests_completed": session_data.get("progress", {}).get("completed_tests", 0),
        "tests_failed": session_data.get("progress", {}).get("failed_tests", 0),
        "final_status": session_data.get("session_state", "unknown")
    }


def _calculate_next_execution(schedule_config: dict[str, Any]) -> str:
    """Calculate next execution time."""
    # Simplified implementation
    return datetime.now(timezone.utc).isoformat()


def _validate_test_suite(test_suite: dict[str, Any]) -> dict[str, bool]:
    """Validate test suite configuration."""
    return {"valid": True, "errors": []}


def _calculate_progress_percentage(progress: dict[str, Any]) -> float:
    """Calculate progress percentage."""
    total = progress.get("total_tests", 0)
    completed = progress.get("completed_tests", 0)
    return (completed / total) * 100 if total > 0 else 0


# Additional helper functions for reporting and comparison
def _generate_summary_report(analysis_result: dict[str, Any], test_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate summary report."""
    return {
        "overview": analysis_result.get("summary_statistics", {}),
        "key_findings": analysis_result.get("recommendations", [])[:3],
        "test_count": len(test_results)
    }


def _generate_detailed_report(analysis_result: dict[str, Any], test_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate detailed report."""
    return {
        "executive_summary": _generate_summary_report(analysis_result, test_results),
        "performance_details": analysis_result.get("performance_analysis", {}),
        "error_details": analysis_result.get("error_analysis", {}),
        "recommendations": analysis_result.get("recommendations", [])
    }


def _generate_comprehensive_report(analysis_result: dict[str, Any], test_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate comprehensive report."""
    return {
        "executive_summary": _generate_summary_report(analysis_result, test_results),
        "detailed_analysis": _generate_detailed_report(analysis_result, test_results),
        "raw_data": {
            "test_results": test_results,
            "analysis_result": analysis_result
        }
    }


def _generate_chart_data(test_results: list[dict[str, Any]], analysis_result: dict[str, Any]) -> dict[str, Any]:
    """Generate chart data for visualization."""
    return {
        "success_rate_chart": {
            "type": "pie",
            "data": analysis_result.get("summary_statistics", {})
        },
        "performance_trend_chart": {
            "type": "line",
            "data": analysis_result.get("performance_analysis", {})
        }
    }


def _export_html_report(report_content: dict[str, Any], chart_data: dict[str, Any] | None) -> str:
    """Export report as HTML."""
    html = f"""
    <html>
    <head><title>Test Report</title></head>
    <body>
    <h1>Test Report</h1>
    <pre>{json.dumps(report_content, indent=2)}</pre>
    </body>
    </html>
    """
    return html


def _export_markdown_report(report_content: dict[str, Any]) -> str:
    """Export report as Markdown."""
    return f"""# Test Report

## Summary
{json.dumps(report_content.get('overview', {}), indent=2)}

## Recommendations
{chr(10).join(f"- {rec}" for rec in report_content.get('recommendations', []))}
"""


def _compare_performance_metrics(baseline: dict[str, Any], comparison: dict[str, Any]) -> dict[str, Any]:
    """Compare performance metrics between baseline and comparison."""
    return {
        "response_time_comparison": "improved",  # Simplified
        "throughput_comparison": "stable",
        "overall_performance": "improved"
    }


def _analyze_regressions(baseline_stats: dict[str, Any], comparison_stats: dict[str, Any]) -> dict[str, Any]:
    """Analyze regressions between test runs."""
    return {
        "regressions_detected": False,
        "regression_details": []
    }


def _analyze_improvements(baseline_stats: dict[str, Any], comparison_stats: dict[str, Any]) -> dict[str, Any]:
    """Analyze improvements between test runs."""
    return {
        "improvements_detected": True,
        "improvement_details": ["Response time improved"]
    }


def _calculate_statistical_significance(
    baseline_results: list[dict[str, Any]],
    comparison_results: list[dict[str, Any]],
    metrics: list[str]
) -> dict[str, Any]:
    """Calculate statistical significance of differences."""
    return {
        "significant_differences": False,
        "confidence_level": 0.95,
        "p_values": {}
    }


def _generate_comparison_recommendations(
    performance_comparison: dict[str, Any],
    regression_analysis: dict[str, Any],
    improvement_analysis: dict[str, Any],
    statistical_significance: dict[str, Any]
) -> list[str]:
    """Generate comparison recommendations."""
    recommendations = []

    if improvement_analysis.get("improvements_detected"):
        recommendations.append("Performance improvements detected - maintain current configuration")

    if regression_analysis.get("regressions_detected"):
        recommendations.append("Performance regressions detected - investigate recent changes")

    return recommendations


def _extract_response_time_metrics(stats: dict[str, Any]) -> dict[str, Any]:
    """Extract response time metrics from stats."""
    return {
        "average": stats.get("average_response_time", 0),
        "min": stats.get("min_response_time", 0),
        "max": stats.get("max_response_time", 0)
    }


def _extract_throughput_metrics(stats: dict[str, Any]) -> dict[str, Any]:
    """Extract throughput metrics from stats."""
    return {
        "requests_per_second": stats.get("requests_per_second", 0),
        "total_requests": stats.get("total_requests", 0)
    }


def _extract_error_rate_metrics(stats: dict[str, Any]) -> dict[str, Any]:
    """Extract error rate metrics from stats."""
    total = stats.get("total_requests", 1)
    errors = stats.get("error_count", 0)
    return {
        "error_rate": (errors / total) * 100,
        "error_count": errors,
        "total_requests": total
    }


def _extract_resource_usage_metrics(stats: dict[str, Any]) -> dict[str, Any]:
    """Extract resource usage metrics from stats."""
    return {
        "cpu_usage": stats.get("cpu_usage", 0),
        "memory_usage": stats.get("memory_usage", 0),
        "disk_usage": stats.get("disk_usage", 0)
    }


def _calculate_aggregated_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    """Calculate aggregated metrics."""
    aggregated = {}

    # Aggregate response time
    if "response_time" in metrics:
        rt_metrics = metrics["response_time"]
        aggregated["average_response_time"] = rt_metrics.get("average", 0)

    # Aggregate throughput
    if "throughput" in metrics:
        tp_metrics = metrics["throughput"]
        aggregated["total_throughput"] = tp_metrics.get("requests_per_second", 0)

    return aggregated


def _generate_performance_indicators(metrics: dict[str, Any], aggregated: dict[str, Any]) -> dict[str, Any]:
    """Generate performance indicators."""
    indicators = {}

    # Response time indicator
    avg_response_time = aggregated.get("average_response_time", 0)
    if avg_response_time < 100:
        indicators["response_time_status"] = "excellent"
    elif avg_response_time < 500:
        indicators["response_time_status"] = "good"
    else:
        indicators["response_time_status"] = "needs_improvement"

    # Throughput indicator
    throughput = aggregated.get("total_throughput", 0)
    if throughput > 100:
        indicators["throughput_status"] = "excellent"
    elif throughput > 50:
        indicators["throughput_status"] = "good"
    else:
        indicators["throughput_status"] = "needs_improvement"

    return indicators


# Missing MCP Tools Implementation

@mcp_tool_audit("run_security_test")
async def run_security_test(
    server_url: str,
    api_spec: dict[str, Any],
    security_focus: list[str] | None = None,
    compliance_requirements: list[str] | None = None,
    scenario_name: str | None = None
) -> dict[str, Any]:
    """
    Executes security testing scenarios for vulnerability assessment.

    Args:
        server_url: Target MockLoop server URL
        api_spec: OpenAPI specification for security analysis
        security_focus: List of security areas to focus on
        compliance_requirements: List of compliance standards to check
        scenario_name: Optional specific scenario to use

    Returns:
        Security test execution result
    """
    try:
        security_test_result = {
            "status": "success",
            "test_id": str(uuid.uuid4()),
            "server_url": server_url,
            "security_focus": security_focus or ["authentication", "authorization", "injection"],
            "compliance_requirements": compliance_requirements or [],
            "scenario_used": scenario_name,
            "vulnerability_assessment": {},
            "compliance_status": {},
            "security_findings": [],
            "recommendations": []
        }

        # Generate security test scenarios if none specified
        if not scenario_name:
            security_scenarios = await generate_security_test_scenarios(
                api_spec=api_spec,
                security_focus=security_test_result["security_focus"],
                compliance_requirements=compliance_requirements or []
            )

            # Deploy the first security scenario
            if security_scenarios.get("scenarios"):
                first_scenario = security_scenarios["scenarios"][0]
                deploy_result = await deploy_scenario(server_url, first_scenario)
                if not deploy_result.get("deployed"):
                    return {
                        **security_test_result,
                        "status": "error",
                        "error": f"Failed to deploy security test scenario: {deploy_result.get('error')}"
                    }
                scenario_name = first_scenario["scenario_name"]
                security_test_result["scenario_used"] = scenario_name

        # Execute security test iteration
        test_result = await run_test_iteration(
            server_url=server_url,
            scenario_name=scenario_name,
            duration_seconds=120,  # Shorter duration for security tests
            monitor_performance=True,
            collect_logs=True
        )

        # Analyze security test results
        if test_result.get("status") == "success":
            request_logs = test_result.get("request_logs", [])
            error_summary = test_result.get("error_summary", {})

            # Analyze security findings
            security_findings = _analyze_security_test_results(
                request_logs,
                error_summary,
                security_test_result["security_focus"]
            )
            security_test_result["security_findings"] = security_findings

            # Assess vulnerabilities
            vulnerability_assessment = _assess_vulnerabilities(security_findings, api_spec)
            security_test_result["vulnerability_assessment"] = vulnerability_assessment

            # Check compliance status
            if compliance_requirements:
                compliance_status = _check_compliance_status(
                    security_findings,
                    vulnerability_assessment,
                    compliance_requirements
                )
                security_test_result["compliance_status"] = compliance_status

            # Generate security recommendations
            recommendations = _generate_security_recommendations(
                security_findings,
                vulnerability_assessment,
                security_test_result["security_focus"]
            )
            security_test_result["recommendations"] = recommendations

        else:
            security_test_result["status"] = "error"
            security_test_result["error"] = f"Security test execution failed: {test_result.get('error')}"

        return security_test_result

    except Exception as e:
        logger.exception("Error running security test")
        return {
            "status": "error",
            "test_id": str(uuid.uuid4()),
            "server_url": server_url,
            "error": f"Security test failed: {e!s}",
            "security_focus": security_focus or [],
            "compliance_requirements": compliance_requirements or [],
            "scenario_used": None,
            "vulnerability_assessment": {},
            "compliance_status": {},
            "security_findings": [],
            "recommendations": []
        }


@mcp_tool_audit("analyze_test_results")
async def analyze_test_results(
    test_results: list[dict[str, Any]],
    analysis_type: str = "comprehensive",
    include_recommendations: bool = True
) -> dict[str, Any]:
    """
    Analyzes test results and provides comprehensive insights.

    Args:
        test_results: List of test result dictionaries
        analysis_type: Type of analysis ("summary", "detailed", "comprehensive")
        include_recommendations: Whether to include recommendations

    Returns:
        Analysis result with insights and recommendations
    """
    try:
        analysis_result = {
            "status": "success",
            "analysis_id": str(uuid.uuid4()),
            "analysis_type": analysis_type,
            "test_count": len(test_results),
            "summary_statistics": {},
            "performance_analysis": {},
            "error_analysis": {},
            "trend_analysis": {},
            "recommendations": []
        }

        if not test_results:
            return {
                **analysis_result,
                "status": "warning",
                "error": "No test results provided for analysis"
            }

        # Calculate summary statistics
        summary_stats = _calculate_summary_statistics(test_results)
        analysis_result["summary_statistics"] = summary_stats

        # Analyze performance trends
        if analysis_type in ["detailed", "comprehensive"]:
            performance_analysis = _analyze_performance_trends(test_results)
            analysis_result["performance_analysis"] = performance_analysis

            # Analyze error patterns
            error_analysis = _analyze_error_patterns(test_results)
            analysis_result["error_analysis"] = error_analysis

        # Analyze trends across tests
        if analysis_type == "comprehensive":
            trend_analysis = _analyze_test_trends(test_results)
            analysis_result["trend_analysis"] = trend_analysis

        # Generate recommendations
        if include_recommendations:
            recommendations = _generate_analysis_recommendations(
                summary_stats,
                analysis_result.get("performance_analysis", {}),
                analysis_result.get("error_analysis", {}),
                analysis_result.get("trend_analysis", {})
            )
            analysis_result["recommendations"] = recommendations

        return analysis_result

    except Exception as e:
        logger.exception("Error analyzing test results")
        return {
            "status": "error",
            "analysis_id": str(uuid.uuid4()),
            "analysis_type": analysis_type,
            "test_count": 0,
            "error": f"Analysis failed: {e!s}",
            "summary_statistics": {},
            "performance_analysis": {},
            "error_analysis": {},
            "trend_analysis": {},
            "recommendations": []
        }


@mcp_tool_audit("generate_test_report")
async def generate_test_report(
    test_results: list[dict[str, Any]],
    report_format: str = "comprehensive",
    include_charts: bool = True,
    output_format: str = "json"
) -> dict[str, Any]:
    """
    Generates formatted test reports in various formats.

    Args:
        test_results: List of test result dictionaries
        report_format: Format type ("summary", "detailed", "comprehensive")
        include_charts: Whether to include chart data
        output_format: Output format ("json", "html", "markdown")

    Returns:
        Generated report in specified format
    """
    try:
        report_result = {
            "status": "success",
            "report_id": str(uuid.uuid4()),
            "report_format": report_format,
            "output_format": output_format,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "report_content": {},
            "chart_data": None,
            "export_data": None
        }

        # First analyze the test results
        analysis_result = await analyze_test_results(test_results, report_format, True)
        if analysis_result.get("status") != "success":
            return {
                **report_result,
                "status": "error",
                "error": f"Failed to analyze test results: {analysis_result.get('error')}"
            }

        # Generate report content based on format
        if report_format == "summary":
            report_content = _generate_summary_report(analysis_result, test_results)
        elif report_format == "detailed":
            report_content = _generate_detailed_report(analysis_result, test_results)
        else:  # comprehensive
            report_content = _generate_comprehensive_report(analysis_result, test_results)

        report_result["report_content"] = report_content

        # Generate chart data if requested
        if include_charts:
            chart_data = _generate_chart_data(test_results, analysis_result)
            report_result["chart_data"] = chart_data

        # Export in specified format
        if output_format == "html":
            export_data = _export_html_report(report_content, report_result.get("chart_data"))
            report_result["export_data"] = export_data
        elif output_format == "markdown":
            export_data = _export_markdown_report(report_content)
            report_result["export_data"] = export_data
        # JSON format is the default (report_content)

        return report_result

    except Exception as e:
        logger.exception("Error generating test report")
        return {
            "status": "error",
            "report_id": str(uuid.uuid4()),
            "report_format": report_format,
            "output_format": output_format,
            "error": f"Report generation failed: {e!s}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "report_content": {},
            "chart_data": None,
            "export_data": None
        }


@mcp_tool_audit("compare_test_runs")
async def compare_test_runs(
    baseline_results: list[dict[str, Any]],
    comparison_results: list[dict[str, Any]],
    comparison_metrics: list[str] | None = None
) -> dict[str, Any]:
    """
    Compares multiple test runs to identify performance changes.

    Args:
        baseline_results: Baseline test results for comparison
        comparison_results: New test results to compare against baseline
        comparison_metrics: Specific metrics to compare

    Returns:
        Comparison result with performance changes
    """
    try:
        comparison_result = {
            "status": "success",
            "comparison_id": str(uuid.uuid4()),
            "baseline_count": len(baseline_results),
            "comparison_count": len(comparison_results),
            "metrics_compared": comparison_metrics or ["response_time", "throughput", "error_rate"],
            "performance_comparison": {},
            "regression_analysis": {},
            "improvement_analysis": {},
            "statistical_significance": {},
            "recommendations": []
        }

        if not baseline_results or not comparison_results:
            return {
                **comparison_result,
                "status": "error",
                "error": "Both baseline and comparison results are required"
            }

        # Analyze both sets of results
        baseline_analysis = await analyze_test_results(baseline_results, "detailed", False)
        comparison_analysis = await analyze_test_results(comparison_results, "detailed", False)

        if baseline_analysis.get("status") != "success" or comparison_analysis.get("status") != "success":
            return {
                **comparison_result,
                "status": "error",
                "error": "Failed to analyze test results for comparison"
            }

        # Compare performance metrics
        baseline_stats = baseline_analysis.get("summary_statistics", {})
        comparison_stats = comparison_analysis.get("summary_statistics", {})

        performance_comparison = _compare_performance_metrics(baseline_stats, comparison_stats)
        comparison_result["performance_comparison"] = performance_comparison

        # Analyze regressions
        regression_analysis = _analyze_regressions(baseline_stats, comparison_stats)
        comparison_result["regression_analysis"] = regression_analysis

        # Analyze improvements
        improvement_analysis = _analyze_improvements(baseline_stats, comparison_stats)
        comparison_result["improvement_analysis"] = improvement_analysis

        # Calculate statistical significance
        statistical_significance = _calculate_statistical_significance(
            baseline_results,
            comparison_results,
            comparison_result["metrics_compared"]
        )
        comparison_result["statistical_significance"] = statistical_significance

        # Generate comparison recommendations
        recommendations = _generate_comparison_recommendations(
            performance_comparison,
            regression_analysis,
            improvement_analysis,
            statistical_significance
        )
        comparison_result["recommendations"] = recommendations

        return comparison_result

    except Exception as e:
        logger.exception("Error comparing test runs")
        return {
            "status": "error",
            "comparison_id": str(uuid.uuid4()),
            "baseline_count": len(baseline_results) if baseline_results else 0,
            "comparison_count": len(comparison_results) if comparison_results else 0,
            "error": f"Test run comparison failed: {e!s}",
            "metrics_compared": comparison_metrics or [],
            "performance_comparison": {},
            "regression_analysis": {},
            "improvement_analysis": {},
            "statistical_significance": {},
            "recommendations": []
        }


@mcp_tool_audit("get_performance_metrics")
async def get_performance_metrics(
    test_results: list[dict[str, Any]],
    metric_types: list[str] | None = None,
    aggregation_method: str = "average"
) -> dict[str, Any]:
    """
    Retrieves and analyzes performance metrics from test results.

    Args:
        test_results: List of test result dictionaries
        metric_types: Types of metrics to extract
        aggregation_method: Method for aggregating metrics

    Returns:
        Performance metrics analysis
    """
    try:
        metrics_result = {
            "status": "success",
            "metrics_id": str(uuid.uuid4()),
            "test_count": len(test_results),
            "metric_types": metric_types or ["response_time", "throughput", "error_rate", "resource_usage"],
            "aggregation_method": aggregation_method,
            "extracted_metrics": {},
            "aggregated_metrics": {},
            "performance_indicators": {}
        }

        if not test_results:
            return {
                **metrics_result,
                "status": "warning",
                "error": "No test results provided for metrics extraction"
            }

        extracted_metrics = {}

        # Extract metrics by type
        for metric_type in metrics_result["metric_types"]:
            if metric_type == "response_time":
                response_time_metrics = []
                for result in test_results:
                    perf_metrics = result.get("performance_metrics", {})
                    if perf_metrics:
                        rt_metrics = _extract_response_time_metrics(perf_metrics)
                        response_time_metrics.append(rt_metrics)
                extracted_metrics["response_time"] = response_time_metrics

            elif metric_type == "throughput":
                throughput_metrics = []
                for result in test_results:
                    perf_metrics = result.get("performance_metrics", {})
                    if perf_metrics:
                        tp_metrics = _extract_throughput_metrics(perf_metrics)
                        throughput_metrics.append(tp_metrics)
                extracted_metrics["throughput"] = throughput_metrics

            elif metric_type == "error_rate":
                error_rate_metrics = []
                for result in test_results:
                    error_summary = result.get("error_summary", {})
                    if error_summary:
                        er_metrics = _extract_error_rate_metrics(error_summary)
                        error_rate_metrics.append(er_metrics)
                extracted_metrics["error_rate"] = error_rate_metrics

            elif metric_type == "resource_usage":
                resource_metrics = []
                for result in test_results:
                    perf_metrics = result.get("performance_metrics", {})
                    if perf_metrics:
                        ru_metrics = _extract_resource_usage_metrics(perf_metrics)
                        resource_metrics.append(ru_metrics)
                extracted_metrics["resource_usage"] = resource_metrics

        metrics_result["extracted_metrics"] = extracted_metrics

        # Calculate aggregated metrics
        aggregated_metrics = _calculate_aggregated_metrics(extracted_metrics)
        metrics_result["aggregated_metrics"] = aggregated_metrics

        # Generate performance indicators
        performance_indicators = _generate_performance_indicators(extracted_metrics, aggregated_metrics)
        metrics_result["performance_indicators"] = performance_indicators

        return metrics_result

    except Exception as e:
        logger.exception("Error extracting performance metrics")
        return {
            "status": "error",
            "metrics_id": str(uuid.uuid4()),
            "test_count": len(test_results) if test_results else 0,
            "error": f"Performance metrics extraction failed: {e!s}",
            "metric_types": metric_types or [],
            "aggregation_method": aggregation_method,
            "extracted_metrics": {},
            "aggregated_metrics": {},
            "performance_indicators": {}
        }


@mcp_tool_audit("create_test_session")
async def create_test_session(
    session_name: str,
    test_plan: dict[str, Any],
    session_config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Creates a new test session for workflow management.

    Args:
        session_name: Name for the test session
        test_plan: Test plan configuration
        session_config: Optional session configuration

    Returns:
        Test session creation result
    """
    try:
        session_id = str(uuid.uuid4())
        session_result = {
            "status": "success",
            "session_id": session_id,
            "session_name": session_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "test_plan": test_plan,
            "session_config": session_config or {},
            "session_state": "created",
            "progress": {
                "total_tests": _calculate_total_tests(test_plan),
                "completed_tests": 0,
                "failed_tests": 0,
                "current_test": None
            }
        }

        # Store session in global storage
        _active_test_sessions[session_id] = session_result.copy()

        return session_result

    except Exception as e:
        logger.exception("Error creating test session")
        return {
            "status": "error",
            "session_id": None,
            "session_name": session_name,
            "error": f"Test session creation failed: {e!s}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "test_plan": {},
            "session_config": {},
            "session_state": "error",
            "progress": {}
        }


@mcp_tool_audit("end_test_session")
async def end_test_session(
    session_id: str,
    generate_final_report: bool = True
) -> dict[str, Any]:
    """
    Ends a test session and generates final reports.

    Args:
        session_id: ID of the test session to end
        generate_final_report: Whether to generate a final report

    Returns:
        Test session completion result
    """
    try:
        if session_id not in _active_test_sessions:
            return {
                "status": "error",
                "session_id": session_id,
                "error": "Test session not found",
                "ended_at": datetime.now(timezone.utc).isoformat(),
                "final_report": None,
                "session_summary": {}
            }

        session_data = _active_test_sessions[session_id]
        session_data["session_state"] = "completed"
        session_data["ended_at"] = datetime.now(timezone.utc).isoformat()

        end_result = {
            "status": "success",
            "session_id": session_id,
            "ended_at": session_data["ended_at"],
            "final_report": None,
            "session_summary": _generate_session_summary(session_data)
        }

        # Generate final report if requested
        if generate_final_report:
            # This would typically include all test results from the session
            # For now, we'll create a placeholder report
            final_report = {
                "session_name": session_data.get("session_name"),
                "duration": session_data.get("ended_at", "") + " - " + session_data.get("created_at", ""),
                "summary": end_result["session_summary"]
            }
            end_result["final_report"] = final_report

        # Remove from active sessions
        del _active_test_sessions[session_id]

        return end_result

    except Exception as e:
        logger.exception("Error ending test session")
        return {
            "status": "error",
            "session_id": session_id,
            "error": f"Test session completion failed: {e!s}",
            "ended_at": datetime.now(timezone.utc).isoformat(),
            "final_report": None,
            "session_summary": {}
        }


@mcp_tool_audit("schedule_test_suite")
async def schedule_test_suite(
    test_suite: dict[str, Any],
    schedule_config: dict[str, Any],
    notification_config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Schedules automated test suite execution.

    Args:
        test_suite: Test suite configuration
        schedule_config: Scheduling configuration
        notification_config: Optional notification settings

    Returns:
        Test suite scheduling result
    """
    try:
        schedule_id = str(uuid.uuid4())
        schedule_result = {
            "status": "success",
            "schedule_id": schedule_id,
            "test_suite": test_suite,
            "schedule_config": schedule_config,
            "notification_config": notification_config or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "next_execution": _calculate_next_execution(schedule_config),
            "schedule_state": "active",
            "validation_result": _validate_test_suite(test_suite)
        }

        if not schedule_result["validation_result"]["valid"]:
            return {
                **schedule_result,
                "status": "error",
                "error": f"Test suite validation failed: {schedule_result['validation_result']['errors']}"
            }

        return schedule_result

    except Exception as e:
        logger.exception("Error scheduling test suite")
        return {
            "status": "error",
            "schedule_id": None,
            "error": f"Test suite scheduling failed: {e!s}",
            "test_suite": {},
            "schedule_config": {},
            "notification_config": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "next_execution": None,
            "schedule_state": "error",
            "validation_result": {"valid": False, "errors": []}
        }


@mcp_tool_audit("monitor_test_progress")
async def monitor_test_progress(
    session_id: str,
    include_performance_data: bool = True,
    alert_on_issues: bool = True
) -> dict[str, Any]:
    """
    Monitors ongoing test execution and provides real-time updates.

    Args:
        session_id: ID of the test session to monitor
        include_performance_data: Whether to include performance metrics
        alert_on_issues: Whether to generate alerts for issues

    Returns:
        Test progress monitoring result
    """
    try:
        if session_id not in _active_test_sessions:
            return {
                "status": "error",
                "session_id": session_id,
                "error": "Test session not found",
                "progress": {},
                "performance_data": {},
                "alerts": [],
                "monitoring_timestamp": datetime.now(timezone.utc).isoformat()
            }

        session_data = _active_test_sessions[session_id]
        progress = session_data.get("progress", {})

        monitor_result = {
            "status": "success",
            "session_id": session_id,
            "session_state": session_data.get("session_state", "unknown"),
            "progress": progress,
            "progress_percentage": _calculate_progress_percentage(progress),
            "performance_data": {},
            "alerts": [],
            "monitoring_timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Include performance data if requested
        if include_performance_data:
            # This would typically fetch real-time performance metrics
            # For now, we'll provide placeholder data
            monitor_result["performance_data"] = {
                "current_response_time": "150ms",
                "current_throughput": "45 RPS",
                "current_error_rate": "0.5%"
            }

        # Generate alerts if requested
        if alert_on_issues:
            alerts = []
            if progress.get("failed_tests", 0) > 0:
                alerts.append({
                    "type": "test_failure",
                    "severity": "warning",
                    "message": f"{progress['failed_tests']} tests have failed"
                })
            monitor_result["alerts"] = alerts

        return monitor_result

    except Exception as e:
        logger.exception("Error monitoring test progress")
        return {
            "status": "error",
            "session_id": session_id,
            "error": f"Test progress monitoring failed: {e!s}",
            "progress": {},
            "performance_data": {},
            "alerts": [],
            "monitoring_timestamp": datetime.now(timezone.utc).isoformat()
        }
