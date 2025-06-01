# This file makes Python treat the `mockloop_mcp` directory as a package.

__version__ = "2.2.1"

# Import proxy module components
from .proxy import PluginManager, ProxyHandler, AuthHandler, ProxyConfig

__all__ = [
    "PluginManager",
    "ProxyHandler",
    "AuthHandler",
    "ProxyConfig",
]
