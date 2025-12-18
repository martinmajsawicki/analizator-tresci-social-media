from .base import BaseAgent

# Consolidated agents (3)
from .voice_guardian import VoiceGuardianAgent
from .opening_sniper import OpeningSniperAgent
from .tension_architect import TensionArchitectAgent

# Core agents (2)
from .comedian import ComedianAgent
from .engagement import EngagementAgent

# Specialized agents (4)
from .platform_adapter import PlatformAdapterAgent
from .story_excavator import StoryExcavatorAgent
from .devils_advocate import DevilsAdvocateAgent
from .vulnerability_scanner import VulnerabilityScannerAgent

# Depth agent (1)
from .context_shifter import ContextShifterAgent

# Source analysis agent (1)
from .source_analyst import SourceAnalystAgent

# Analytical agents
from .extractor import ExtractorAgent
from .resonance_hunter import ResonanceHunterAgent
from .anthropologist import AnthropologistAgent, AnthropologyReport, DepthReport
from .polish_contextualizer import PolishContextualizerAgent
from .popculture_curator import PopcultureCuratorAgent

# Platform agents (v2)
from .linkedin_agent import LinkedInAgent
from .facebook_agent import FacebookAgent
from .twitter_agent import TwitterAgent
from .reels_agent import ReelsAgent

# Quality control
from .quality_controller import QualityControllerAgent

# Brief synthesis
from .brief_synthesizer import BriefSynthesizerAgent

# === V3 AGENTS (new workflow) ===
from .orchestrator_v3 import OrchestratorV3

# Mode agents
from .exploration_agent import ExplorationAgent
from .development_agent import DevelopmentAgent

# Platform agents (v3 - unified)
from .microblog_agent import MicroblogAgent
from .video_agent import VideoAgent

__all__ = [
    "BaseAgent",
    "VoiceGuardianAgent",
    "OpeningSniperAgent",
    "TensionArchitectAgent",
    "ComedianAgent",
    "EngagementAgent",
    "PlatformAdapterAgent",
    "StoryExcavatorAgent",
    "DevilsAdvocateAgent",
    "VulnerabilityScannerAgent",
    "ContextShifterAgent",
    "SourceAnalystAgent",
    "ExtractorAgent",
    "ResonanceHunterAgent",
    "AnthropologistAgent",
    "AnthropologyReport",
    "DepthReport",
    "PolishContextualizerAgent",
    "PopcultureCuratorAgent",
    "LinkedInAgent",
    "FacebookAgent",
    "TwitterAgent",
    "ReelsAgent",
    "QualityControllerAgent",
    "BriefSynthesizerAgent",
    # V3 New
    "OrchestratorV3",
    "ExplorationAgent",
    "DevelopmentAgent",
    "MicroblogAgent",
    "VideoAgent",
]
