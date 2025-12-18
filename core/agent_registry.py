"""
Rejestr agentów dostępnych do wyboru w pipeline.

Definiuje które agenty są dostępne w każdym trybie pracy.
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class AgentDefinition:
    """Definicja agenta do wyboru."""
    key: str                    # Unikalny klucz (np. "anthropologist")
    name_pl: str               # Polska nazwa do wyświetlenia
    description: str           # Krótki opis co robi
    category: str              # Kategoria: "analytical", "review", "enhancement"
    available_in: List[str]    # Tryby gdzie dostępny: ["exploration", "development", "polish"]
    default_in: List[str] = field(default_factory=list)  # Tryby gdzie domyślnie włączony


# Agenty analityczne - wydobywają dane ze źródła
ANALYTICAL_AGENTS = [
    AgentDefinition(
        key="source_analyst",
        name_pl="Analityk Źródła",
        description="Analizuje wiarygodność badań: kto, co, jak, wyniki, ograniczenia",
        category="analytical",
        available_in=["exploration", "development", "polish"],
        default_in=["exploration", "development"],  # nie w SZLIF
    ),
    AgentDefinition(
        key="anthropologist",
        name_pl="Antropolog",
        description="Analiza etnograficzna, socjologiczna i psychologiczna",
        category="analytical",
        available_in=["exploration", "development", "polish"],
        default_in=["exploration", "development", "polish"],  # wszędzie
    ),
    AgentDefinition(
        key="polish_contextualizer",
        name_pl="Polski Kontekstualizator",
        description="Tłumaczy obce realia na polski kontekst",
        category="analytical",
        available_in=["exploration", "development", "polish"],
        default_in=["exploration", "development", "polish"],  # wszędzie
    ),
    AgentDefinition(
        key="popculture_curator",
        name_pl="Kurator Popkultury",
        description="Analogie z filmów, sportu, codzienności",
        category="analytical",
        available_in=["exploration", "development", "polish"],
        default_in=["exploration", "development"],  # nie w SZLIF
    ),
    AgentDefinition(
        key="story_excavator",
        name_pl="Archeolog Historii",
        description="Wydobywa narracje i dramaturgie ze źródła",
        category="analytical",
        available_in=["exploration", "development", "polish"],
        default_in=["development"],  # tylko ROZWINIĘCIE
    ),
    AgentDefinition(
        key="tension_architect",
        name_pl="Architekt Napięcia",
        description="Buduje napięcie narracyjne, znajdzie konflikt i rozwiązanie",
        category="analytical",
        available_in=["exploration", "development", "polish"],
        default_in=["development"],  # tylko ROZWINIĘCIE
    ),
    AgentDefinition(
        key="context_shifter",
        name_pl="Poszerzacz Kontekstu",
        description="Pogłębia wymiary: historyczny, społeczny, ekonomiczny",
        category="analytical",
        available_in=["exploration", "development", "polish"],
        default_in=[],  # nigdzie domyślnie
    ),
]

# Agenty recenzujące - oceniają gotowy tekst
REVIEW_AGENTS = [
    AgentDefinition(
        key="devils_advocate",
        name_pl="Adwokat Diabła",
        description="Kwestionuje założenia, kontrargumenty, zapobiega cringe",
        category="review",
        available_in=["exploration", "development", "polish"],
        default_in=["development"],  # tylko ROZWINIĘCIE
    ),
    AgentDefinition(
        key="voice_guardian",
        name_pl="Strażnik Głosu",
        description="Sprawdza autentyczny głos, wykrywa zombie-frazy",
        category="review",
        available_in=["polish"],
        default_in=["polish"],  # domyślny w SZLIF
    ),
    AgentDefinition(
        key="opening_sniper",
        name_pl="Snajper Otwarcia",
        description="Specjalista od hooków, zabija banały",
        category="review",
        available_in=["polish"],
        default_in=["polish"],  # domyślny w SZLIF
    ),
    AgentDefinition(
        key="vulnerability_scanner",
        name_pl="Wykrywacz Skazy",
        description="Szuka ludzkiej autentyczności i vulnerability",
        category="review",
        available_in=["polish"],
        default_in=[],  # nie domyślny
    ),
]

# Agenty ulepszające - dodają engagement/humor
ENHANCEMENT_AGENTS = [
    AgentDefinition(
        key="comedian",
        name_pl="Komik",
        description="Znajduje okazje na humor dopasowany do platformy",
        category="enhancement",
        available_in=["exploration", "development", "polish"],
        default_in=[],  # nie domyślny
    ),
    AgentDefinition(
        key="engagement",
        name_pl="Inżynier Zaangażowania",
        description="Przekształca monologi w rozmowy, tworzy haki do interakcji",
        category="enhancement",
        available_in=["exploration", "development", "polish"],
        default_in=[],  # nie domyślny
    ),
]

# Wszystkie agenty do wyboru
ALL_SELECTABLE_AGENTS = ANALYTICAL_AGENTS + REVIEW_AGENTS + ENHANCEMENT_AGENTS


def get_agents_for_mode(mode: str) -> List[AgentDefinition]:
    """Zwraca agentów dostępnych w danym trybie."""
    return [
        agent for agent in ALL_SELECTABLE_AGENTS
        if mode in agent.available_in
    ]


def get_default_agents_for_mode(mode: str) -> List[str]:
    """Zwraca klucze domyślnie włączonych agentów dla trybu."""
    return [
        agent.key for agent in ALL_SELECTABLE_AGENTS
        if mode in agent.default_in
    ]


def get_agent_by_key(key: str) -> Optional[AgentDefinition]:
    """Zwraca definicję agenta po kluczu."""
    for agent in ALL_SELECTABLE_AGENTS:
        if agent.key == key:
            return agent
    return None
