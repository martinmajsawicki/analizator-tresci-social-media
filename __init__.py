"""
Social Media Post Analyzer

Narzędzie AI do transformacji profesjonalnych ale nudnych postów
w angażujące treści social media.
"""

__version__ = "1.0.0"
__author__ = "Marcin Majsawicki"

from core import Config, PLATFORM_PROFILES, OpenRouterClient
from agents import Orchestrator

__all__ = [
    "Config",
    "PLATFORM_PROFILES",
    "OpenRouterClient",
    "Orchestrator",
]
