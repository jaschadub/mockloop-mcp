# This file makes Python treat the `mockloop_mcp` directory as a package.

__version__ = "2.2.9"

# Import proxy module components
from .proxy import PluginManager, ProxyHandler, AuthHandler, ProxyConfig

__all__ = [
    "AuthHandler",
    "PluginManager",
    "ProxyConfig",
    "ProxyHandler",
]
