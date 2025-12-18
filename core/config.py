"""Configuration for Social Media Post Analyzer."""

import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ModelConfig:
    """Configuration for a single model."""
    id: str
    name: str
    description: str
    price_per_1k_input: float  # USD
    price_per_1k_output: float  # USD
    supports_web_search: bool = False


# Available models - updated December 2025
AVAILABLE_MODELS = {
    "claude-opus-4.5": ModelConfig(
        id="anthropic/claude-opus-4.5",
        name="Claude Opus 4.5",
        description="Najwyższa jakość, najlepszy dla polskiego i humoru",
        price_per_1k_input=0.015,
        price_per_1k_output=0.075,
    ),
    "gpt-5.1": ModelConfig(
        id="openai/gpt-5.1",
        name="GPT-5.1",
        description="Dobra jakość, szybszy",
        price_per_1k_input=0.01,
        price_per_1k_output=0.03,
    ),
    "gemini-3-pro": ModelConfig(
        id="google/gemini-3-pro-preview",
        name="Gemini 3 Pro",
        description="Web search, tańszy",
        price_per_1k_input=0.00125,
        price_per_1k_output=0.005,
        supports_web_search=True,
    ),
    "gemini-3-flash": ModelConfig(
        id="google/gemini-3-flash-preview",
        name="Gemini 3 Flash",
        description="Bardzo szybki i tani, do prostych zadań",
        price_per_1k_input=0.0005,   # $0.50/M
        price_per_1k_output=0.003,   # $3/M
    ),
}


@dataclass
class PlatformConfig:
    """Configuration for a social media platform."""
    name: str
    name_pl: str
    audience_type: str
    audience_description: str
    values: list[str]
    anti_patterns: list[str]
    max_length: int
    preview_length: int
    tone: str
    default_humor_dial: int
    humor_range: tuple[int, int]
    risk_tolerance: str  # niska, średnia, wysoka
    hashtags: str  # "3-5", "0-2", "minimalne"
    emoji_level: str


# Platform profiles with audience characteristics
PLATFORM_PROFILES = {
    "linkedin": PlatformConfig(
        name="linkedin",
        name_pl="LinkedIn",
        audience_type="eksperci_profesjonalisci",
        audience_description="""Managerowie, dyrektorzy, specjaliści branżowi.
Ludzie budujący personal brand zawodowy.
Szukają insightów do zastosowania w pracy.
Cenią doświadczenie i wiarygodność.
Mają mało czasu - scrollują między spotkaniami.""",
        values=[
            "Praktyczne wnioski z doświadczenia",
            "Dane i konkretne przykłady",
            "Historie sukcesu i porażki z nauką",
            "Możliwości networkingu",
            "Thought leadership (ale autentyczne)",
        ],
        anti_patterns=[
            "Clickbait ('Nie uwierzysz co...')",
            "Agresywna sprzedaż",
            "Memy i żarty zbyt casualowe",
            "Zbyt osobiste/emocjonalne treści",
            "'Zgadzasz się?' jako jedyne CTA",
            "'Jestem zaszczycony, że mogę ogłosić...'",
        ],
        max_length=3000,
        preview_length=200,
        tone="profesjonalny_ludzki",
        default_humor_dial=2,
        humor_range=(1, 3),
        risk_tolerance="niska",
        hashtags="3-5",
        emoji_level="umiarkowany",
    ),
    "facebook": PlatformConfig(
        name="facebook",
        name_pl="Facebook",
        audience_type="szersza_casualowa",
        audience_description="""Znajomi, rodzina, mixed connections.
Ludzie odpoczywający przy scrollowaniu.
Szersza demograficznie widownia.
Mniej "profesjonalni" - bardziej ludzcy.
Szukają emocji, rozrywki, poczucia wspólnoty.""",
        values=[
            "Autentyczne emocje i historie",
            "Poczucie wspólnoty ('wszyscy to znamy')",
            "Rozrywka i lekkość",
            "Relatable content ('to ja!')",
            "Możliwość tagowania znajomych",
        ],
        anti_patterns=[
            "Zbyt profesjonalny ton",
            "Długie teksty bez emocjonalnego hooka",
            "Suche fakty bez ludzkiego kontekstu",
            "Język B2B",
            "Przesadna autopromocja",
            "Over-sharing, vaguebooking",
        ],
        max_length=2000,
        preview_length=150,
        tone="ciepły_osobisty",
        default_humor_dial=3,
        humor_range=(2, 4),
        risk_tolerance="średnia",
        hashtags="0-2",
        emoji_level="swobodny",
    ),
    "x_twitter": PlatformConfig(
        name="x_twitter",
        name_pl="X / BlueSky / Threads",
        audience_type="punchy_obserwatorzy",
        audience_description="""News junkies, early adopters.
Cenią humor i dowcip.
Lubią ostre obserwacje i gorące tezy.
Oczekują szybkiego dostarczenia wartości.
Nagradzają oryginalność i odwagę.""",
        values=[
            "Szybki hit dopaminy",
            "Zaskoczenie i moment 'aha!'",
            "Ironia i samoświadomość",
            "Kontrowersyjne tezy",
            "Viralność i możliwość podania dalej",
            "Humor obserwacyjny",
        ],
        anti_patterns=[
            "Długie, rozwlekłe posty",
            "Korporacyjna mowa (natychmiastowy ignore)",
            "Humor na siłę",
            "Wyjaśniane żarty",
            "Lekcje w stylu LinkedIn",
            "'Jako [tytuł], uważam że...'",
        ],
        max_length=280,
        preview_length=280,  # Full visibility
        tone="ostry_dowcipny",
        default_humor_dial=4,
        humor_range=(3, 5),
        risk_tolerance="wysoka",
        hashtags="0-2",
        emoji_level="ironiczny_lub_minimalny",
    ),
    "instagram_reels": PlatformConfig(
        name="instagram_reels",
        name_pl="Instagram Rolki",
        audience_type="wizualni_scrollerzy",
        audience_description="""Młodsza demografa, wizualni konsumenci.
Scrollują szybko - masz 1-3 sekundy na zatrzymanie.
80% ogląda bez dźwięku.
Oczekują autentyczności i energii.
Cenią krótką, wartościową treść.""",
        values=[
            "Hook w pierwszych 3 sekundach",
            "Autentyczność i energia",
            "Edukacja w formie rozrywki (edutainment)",
            "Napisy/tekst na ekranie",
            "Dynamiczny montaż",
            "CTA do zapisania/udostępnienia",
        ],
        anti_patterns=[
            "Nudne intro ('Cześć, dziś opowiem...')",
            "Brak napisów",
            "Monotonny ton głosu",
            "Zbyt długie (>60s bez powodu)",
            "Clickbait bez wartości",
            "Profesjonalna produkcja bez duszy",
        ],
        max_length=2200,  # Caption
        preview_length=125,  # Caption preview
        tone="energetyczny_autentyczny",
        default_humor_dial=3,
        humor_range=(2, 4),
        risk_tolerance="średnia",
        hashtags="5-15",
        emoji_level="umiarkowany",
    ),
}


@dataclass
class Config:
    """Main application configuration."""
    openrouter_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    default_model: str = "claude-opus-4.5"
    timeout: int = 120  # seconds - long timeout for complex analysis
    max_retries: int = 3

    # Backward compatibility
    @property
    def api_key(self) -> str:
        """Return OpenRouter API key for backward compatibility."""
        return self.openrouter_api_key or ""

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        google_key = os.getenv("GOOGLE_API_KEY")

        # Require at least one API key
        if not any([openrouter_key, anthropic_key, openai_key, google_key]):
            raise ValueError(
                "Brak kluczy API. Ustaw przynajmniej jeden w pliku .env:\n"
                "- OPENROUTER_API_KEY (uniwersalny - obsługuje wszystkie modele)\n"
                "- ANTHROPIC_API_KEY (dla Claude - bezpośrednio)\n"
                "- OPENAI_API_KEY (dla GPT - bezpośrednio)\n"
                "- GOOGLE_API_KEY (dla Gemini - bezpośrednio)"
            )

        default_model = os.getenv("DEFAULT_MODEL", "claude-opus-4.5")

        return cls(
            openrouter_api_key=openrouter_key,
            anthropic_api_key=anthropic_key,
            openai_api_key=openai_key,
            google_api_key=google_key,
            default_model=default_model,
        )

    def get_model(self, model_key: str) -> ModelConfig:
        """Get model configuration by key."""
        if model_key not in AVAILABLE_MODELS:
            raise ValueError(f"Unknown model: {model_key}")
        return AVAILABLE_MODELS[model_key]

    @property
    def available_models(self) -> dict[str, ModelConfig]:
        """Get all available models."""
        return AVAILABLE_MODELS

    @staticmethod
    def get_platform(platform_key: str) -> PlatformConfig:
        """Get platform configuration by key."""
        if platform_key not in PLATFORM_PROFILES:
            raise ValueError(f"Unknown platform: {platform_key}")
        return PLATFORM_PROFILES[platform_key]

    @staticmethod
    def available_platforms() -> dict[str, PlatformConfig]:
        """Get all available platforms."""
        return PLATFORM_PROFILES
