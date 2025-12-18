"""Base agent class for all social media analysis agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Callable
from pathlib import Path

from core.openrouter import OpenRouterClient, APIResponse
from core.config import PlatformConfig, PLATFORM_PROFILES


@dataclass
class AgentResult:
    """Result from an agent analysis."""
    agent_name: str
    agent_name_pl: str  # Polish name for display
    content: str
    score: Optional[float] = None  # 0-10 scale
    issues_count: int = 0
    suggestions_count: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    elapsed_seconds: float = 0.0
    cost_usd: float = 0.0
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None


class BaseAgent(ABC):
    """Base class for all social media analysis agents."""

    # Override in subclasses
    name: str = "base"
    name_pl: str = "Bazowy"
    description: str = "Bazowy agent"

    def __init__(
        self,
        client: OpenRouterClient,
        model_key: str = "claude-opus-4.5",
    ):
        self.client = client
        self.model_key = model_key
        self._prompt_template: Optional[str] = None

    @property
    def prompt_template(self) -> str:
        """Load prompt template from file."""
        if self._prompt_template is None:
            prompt_path = Path(__file__).parent.parent / "prompts" / "pl" / f"{self.name}.md"
            if prompt_path.exists():
                self._prompt_template = prompt_path.read_text(encoding="utf-8")
            else:
                self._prompt_template = self._get_default_prompt()
        return self._prompt_template

    @abstractmethod
    def _get_default_prompt(self) -> str:
        """Return default prompt if file not found."""
        pass

    def _build_platform_context(self, platform: PlatformConfig, humor_dial: int) -> str:
        """Build platform context section for the prompt."""
        return f"""
## KONTEKST PLATFORMY

**Platforma docelowa:** {platform.name_pl}
**Profil widowni:** {platform.audience_type}

### Charakterystyka widowni:
{platform.audience_description}

### Czego oczekują:
{chr(10).join('- ' + v for v in platform.values)}

### Czego NIE robić (anti-patterns):
{chr(10).join('- ' + ap for ap in platform.anti_patterns)}

### Ton i styl:
- Poziom humoru: Dial {humor_dial}/5 (zakres dla platformy: {platform.humor_range[0]}-{platform.humor_range[1]})
- Ton: {platform.tone}
- Max długość: {platform.max_length} znaków
- Tolerancja ryzyka: {platform.risk_tolerance}
- Hashtagi: {platform.hashtags}
- Emoji: {platform.emoji_level}
"""

    def _build_messages(
        self,
        content: str,
        mode: str,
        platform: Optional[PlatformConfig] = None,
        humor_dial: Optional[int] = None,
        context: Optional[dict] = None,
    ) -> list[dict]:
        """Build messages for the API call."""
        system_prompt = self.prompt_template

        # Add platform context if provided
        if platform:
            dial = humor_dial or platform.default_humor_dial
            platform_context = self._build_platform_context(platform, dial)
            system_prompt = platform_context + "\n---\n\n" + system_prompt

        # Add mode context
        mode_labels = {
            "idea": "TRYB: ROZWÓJ POMYSŁU - Masz surowy pomysł/temat do rozwinięcia w post",
            "source": "TRYB: TRANSFORMACJA ŹRÓDŁA - Masz artykuł/tekst do przekształcenia w post social media",
            "review": "TRYB: RECENZJA POSTA - Masz gotowy/szkic posta do oceny i ulepszenia",
        }
        mode_context = f"\n\n# {mode_labels.get(mode, 'TRYB: OGÓLNY')}\n"
        system_prompt = mode_context + system_prompt

        # Add additional context if provided
        if context:
            context_str = "\n\n# KONTEKST DODATKOWY\n"
            for key, value in context.items():
                if key not in ["platform", "mode", "humor_dial"]:
                    context_str += f"- {key}: {value}\n"
            system_prompt += context_str

        # Determine user message based on mode
        if mode == "idea":
            user_content = f"# POMYSŁ DO ROZWINIĘCIA\n\n{content}"
        elif mode == "source":
            user_content = f"# TEKST ŹRÓDŁOWY DO PRZEKSZTAŁCENIA\n\n{content}"
        else:  # review
            user_content = f"# POST DO RECENZJI\n\n{content}"

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

    def analyze(
        self,
        content: str,
        mode: str = "review",
        platform: Optional[str] = None,
        humor_dial: Optional[int] = None,
        context: Optional[dict] = None,
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> AgentResult:
        """
        Analyze the content.

        Args:
            content: The content to analyze (idea, source text, or draft post)
            mode: "idea", "source", or "review"
            platform: Platform key (linkedin, facebook, x_twitter) or None
            humor_dial: Override humor level (1-5) or None for platform default
            context: Additional context
            on_progress: Callback for progress updates

        Returns:
            AgentResult with analysis
        """
        if on_progress:
            on_progress(f"Rozpoczynam analizę...")

        try:
            # Get platform config if specified
            platform_config = None
            if platform:
                platform_config = PLATFORM_PROFILES.get(platform)

            messages = self._build_messages(
                content=content,
                mode=mode,
                platform=platform_config,
                humor_dial=humor_dial,
                context=context,
            )

            def on_retry(attempt: int, error: str) -> None:
                if on_progress:
                    on_progress(f"Próba {attempt} nie powiodła się, ponawiam...")

            response = self.client.chat(
                messages=messages,
                model_key=self.model_key,
                temperature=0.7,
                max_tokens=4096,
                on_retry=on_retry,
            )

            # Check for empty response
            if not response.content or response.content.strip() == "":
                if on_progress:
                    on_progress("Uwaga: model zwrócił pustą odpowiedź")
                response.content = "[Model nie zwrócił analizy - spróbuj ponownie lub wybierz inny model]"

            # Parse score from response if present
            score = self._extract_score(response.content)
            issues_count = self._count_issues(response.content)
            suggestions_count = self._count_suggestions(response.content)

            if on_progress:
                score_str = f"{score}/10" if score else "brak"
                on_progress(f"Zakończono (ocena: {score_str})")

            return AgentResult(
                agent_name=self.name,
                agent_name_pl=self.name_pl,
                content=response.content,
                score=score,
                issues_count=issues_count,
                suggestions_count=suggestions_count,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                elapsed_seconds=response.elapsed_seconds,
                cost_usd=response.cost_usd,
            )

        except Exception as e:
            if on_progress:
                on_progress(f"Błąd: {str(e)}")

            return AgentResult(
                agent_name=self.name,
                agent_name_pl=self.name_pl,
                content="",
                error=str(e),
            )

    def _extract_score(self, content: str) -> Optional[float]:
        """Extract score from agent response."""
        import re
        # Look for patterns like "Ocena: 5/10" or "X/10"
        patterns = [
            r"[Oo]cena[:\s]+(\d+(?:\.\d+)?)\s*/\s*10",
            r"OCENA[^:]*:[:\s]+(\d+(?:\.\d+)?)\s*/\s*10",
            r"(\d+(?:\.\d+)?)\s*/\s*10",
            r"ŚREDNIA[:\s]+(\d+(?:\.\d+)?)",
        ]
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        return None

    def _count_issues(self, content: str) -> int:
        """Count issues found in response."""
        import re
        # Count table rows or list items that look like issues
        issues = 0
        # Count markdown table rows (excluding header)
        table_rows = re.findall(r"^\|[^|]+\|[^|]+\|", content, re.MULTILINE)
        issues += max(0, len(table_rows) - 2)  # Subtract header rows
        return issues

    def _count_suggestions(self, content: str) -> int:
        """Count suggestions in response."""
        import re
        # Count lines starting with suggestion markers
        suggestions = len(re.findall(
            r"^(?:PROPOZYCJA|Propozycja|SUGESTIA|Sugestia|WARIANT|Wariant|→|➜|•|\d+\.)",
            content, re.MULTILINE
        ))
        return suggestions
