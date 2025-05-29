"""
HTTP client utilities for communicating with mock servers.
"""
import asyncio
import json
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin, urlparse
import aiohttp
import socket


class MockServerClient:
    """Client for communicating with MockLoop generated mock servers."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize the mock server client.
        
        Args:
            base_url: Base URL of the mock server (e.g., "http://localhost:8000")
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the mock server is healthy and responsive.
        
        Returns:
            Dict containing health status and server info
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "healthy",
                            "server_info": data,
                            "response_time_ms": response.headers.get("X-Process-Time", "unknown")
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "status_code": response.status,
                            "error": f"Health check returned {response.status}"
                        }
        except Exception as e:
            return {
                "status": "unreachable",
                "error": str(e)
            }
    
    async def query_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        method: Optional[str] = None,
        path: Optional[str] = None,
        include_admin: bool = False,
        log_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Query request logs from the mock server.
        
        Args:
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            method: Filter by HTTP method
            path: Filter by path pattern
            include_admin: Include admin requests in results
            log_id: Get specific log by ID
            
        Returns:
            Dict containing logs and metadata
        """
        try:
            params = {
                "limit": limit,
                "offset": offset,
                "include_admin": include_admin
            }
            
            if method:
                params["method"] = method
            if path:
                params["path"] = path
            if log_id:
                params["id"] = log_id
                
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(
                    f"{self.base_url}/admin/api/requests",
                    params=params
                ) as response:
                    if response.status == 200:
                        logs = await response.json()
                        return {
                            "status": "success",
                            "logs": logs if isinstance(logs, list) else [logs],
                            "total_count": len(logs) if isinstance(logs, list) else 1,
                            "filters_applied": {
                                "method": method,
                                "path": path,
                                "include_admin": include_admin,
                                "log_id": log_id
                            }
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "error",
                            "error": f"Request failed with status {response.status}: {error_text}",
                            "logs": []
                        }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "logs": []
            }
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get request statistics from the mock server.
        
        Returns:
            Dict containing request statistics
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/admin/api/requests/stats") as response:
                    if response.status == 200:
                        stats = await response.json()
                        return {
                            "status": "success",
                            "stats": stats
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "error",
                            "error": f"Stats request failed with status {response.status}: {error_text}"
                        }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_debug_info(self) -> Dict[str, Any]:
        """
        Get debug information from the mock server.
        
        Returns:
            Dict containing debug information
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/admin/api/debug") as response:
                    if response.status == 200:
                        debug_info = await response.json()
                        return {
                            "status": "success",
                            "debug_info": debug_info
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "error",
                            "error": f"Debug request failed with status {response.status}: {error_text}"
                        }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


async def discover_running_servers(
    ports: List[int] = None,
    check_health: bool = True
) -> List[Dict[str, Any]]:
    """
    Discover running MockLoop servers by scanning common ports.
    
    Args:
        ports: List of ports to scan. If None, scans common ports.
        check_health: Whether to perform health checks on discovered servers
        
    Returns:
        List of discovered server information
    """
    if ports is None:
        ports = [8000, 8001, 8002, 8003, 8004, 8005, 3000, 3001, 5000, 5001]
    
    discovered_servers = []
    
    for port in ports:
        try:
            # Quick port check
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:  # Port is open
                server_url = f"http://localhost:{port}"
                server_info = {
                    "url": server_url,
                    "port": port,
                    "status": "discovered"
                }
                
                if check_health:
                    client = MockServerClient(server_url, timeout=5)
                    health_result = await client.health_check()
                    server_info.update(health_result)
                    
                    # Try to get additional server info if it's a MockLoop server
                    if health_result.get("status") == "healthy":
                        debug_result = await client.get_debug_info()
                        if debug_result.get("status") == "success":
                            server_info["is_mockloop_server"] = True
                            server_info["debug_info"] = debug_result.get("debug_info", {})
                        else:
                            server_info["is_mockloop_server"] = False
                
                discovered_servers.append(server_info)
                
        except Exception as e:
            # Port scan failed, continue to next port
            continue
    
    return discovered_servers


def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid and properly formatted.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


async def test_server_connectivity(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Test connectivity to a server URL.
    
    Args:
        url: Server URL to test
        timeout: Connection timeout in seconds
        
    Returns:
        Dict containing connectivity test results
    """
    if not is_valid_url(url):
        return {
            "status": "error",
            "error": "Invalid URL format"
        }
    
    client = MockServerClient(url, timeout=timeout)
    return await client.health_check()