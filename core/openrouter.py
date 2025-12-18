"""OpenRouter API client - wrapper dla wstecznej kompatybilności.

Ten moduł re-eksportuje UnifiedAPIClient jako OpenRouterClient
dla zachowania kompatybilności z istniejącym kodem.
"""

from .api_client import UnifiedAPIClient, APIResponse

# Alias for backward compatibility
OpenRouterClient = UnifiedAPIClient

__all__ = ["OpenRouterClient", "APIResponse"]
