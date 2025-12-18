"""Inżynier Zaangażowania - transforms monologues into conversations."""

import json
import re
import logging
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient

logger = logging.getLogger(__name__)


@dataclass
class EngagementReport:
    """Raport z analizy potencjału zaangażowania."""
    engagement_potential: int  # 1-10
    existing_hooks: list  # obecne haki
    missing_elements: list  # brakujące elementy
    boosters: list  # wzmacniacze zaangażowania
    question_improvements: list  # ulepszenia pytań
    cta_options: dict  # opcje CTA
    relatable_moments: list  # momenty relatable
    platform_ctas: dict  # CTA wg platformy

    def to_dict(self) -> dict:
        return {
            "potencjal_zaangazowania": self.engagement_potential,
            "obecne_haki": self.existing_hooks,
            "brakujace_elementy": self.missing_elements,
            "wzmacniacze": self.boosters,
            "ulepszenia_pytan": self.question_improvements,
            "opcje_cta": self.cta_options,
            "momenty_relatable": self.relatable_moments,
            "cta_platformy": self.platform_ctas,
        }


class EngagementAgent(BaseAgent):
    """Agent that creates engagement hooks and conversation triggers."""

    name = "engagement"
    name_pl = "Inżynier Zaangażowania"
    description = "Przekształca monologi w rozmowy, tworzy nieodparte haki do interakcji"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# INŻYNIER ZAANGAŻOWANIA

Tworzysz posty, na które ludzie CHCĄ odpowiadać - pytania, prowokacje, relatable walki.

## DWA TRYBY PRACY

### TRYB ŹRÓDŁO (eksploracja)
Gdy analizujesz badanie/artykuł - szukasz:
- **Kontrowersyjnych tez** które wywołają debatę
- **Uniwersalnych doświadczeń** ("Kto jeszcze miał tak że...")
- **Pytań otwierających dyskusję** (nie "czy się zgadzacie?" ale "jak to wygląda u was?")
- **Potencjału na polaryzację** (dwie strony sporu)

### TRYB POST (ulepszanie)
Gdy analizujesz gotowy post - szukasz:
- **Brakujących CTA** - gdzie dodać pytanie?
- **Zamkniętych pytań** do zamiany na otwarte
- **Możliwości personalizacji** ("Ty też?", "A jak u Ciebie?")

## WYZWALACZE ZAANGAŻOWANIA
- Prośba o radę: "Jak wy to rozwiązujecie?"
- Prośba o przykłady: "Podajcie z waszych branż"
- Zakwestionowanie: "Zmień moje zdanie: X > Y"
- Uzupełnij lukę: "Najgorsza rada: ___"
- Polaryzująca opinia: "Unpopular opinion: X"
- Oznacz kogoś: "Oznacz kogoś kto..."

## ZASADY ZWIĘZŁOŚCI
- Max 3 obecne haki (jeśli są)
- Max 3 brakujące elementy
- Max 3 wzmacniacze
- Max 2 ulepszenia pytań
- 4 opcje CTA
- Max 3 momenty relatable

## FORMAT ODPOWIEDZI

```json
{
  "potencjal_zaangazowania": 6,
  "obecne_haki": [
    "Jest pytanie na końcu"
  ],
  "brakujace_elementy": [
    "Bezpośrednie pytanie do widowni",
    "Relatable walka/wygrana",
    "Opinia warta debaty"
  ],
  "wzmacniacze": [
    {"technika": "Prośba o radę", "implementacja": "Jak wy to rozwiązaliście?", "efekt": "Ludzie lubią pomagać"}
  ],
  "ulepszenia_pytan": [
    {"obecne": "Czy się zgadzacie?", "lepsze": "Jakie jest wasze najgorsze doświadczenie z X?", "dlaczego": "Otwarte > zamknięte"}
  ],
  "opcje_cta": {
    "porada": "Jak wy to robicie w swoich zespołach?",
    "opinia": "Co jest gorszą radą: A czy B?",
    "historia": "Podzielcie się waszą wersją tej sytuacji",
    "debata": "Zmień moje zdanie: X jest przereklamowane"
  },
  "momenty_relatable": [
    "Frustracja z długimi spotkaniami",
    "Syndrom oszusta przy awansie"
  ],
  "cta_platformy": {
    "linkedin": "Jakie spotkanie powinno być mailem w waszej firmie?",
    "facebook": "Oznacz kogoś kto ma to samo w pracy",
    "twitter": "hot take: spotkania to choroba"
  }
}
```

## WAŻNE ZASADY
- Autentyczne zaangażowanie > engagement bait
- UNIKAJ: "Skomentuj TAK jeśli się zgadzasz"
- UNIKAJ: bezsensownych ankiet
- Czasem najlepsze CTA to silna opinia
- Na X/Twitter: implicit > explicit

## TRANSFORMACJA PRZYKŁAD

**Przed (monolog):**
> "Komunikacja w zespole jest ważna. Warto organizować spotkania."

**Po (rozmowa):**
> "Dodaliśmy 3 spotkania tygodniowo. Produktywność spadła.
> Teraz mamy jedno 25-min w poniedziałek.
> Jakie jest wasze najgorsze spotkanie które powinno być mailem?"
"""

    def engineer(self, content: str, context: Optional[dict] = None) -> EngagementReport:
        """
        Analizuje potencjał zaangażowania treści.

        Args:
            content: Treść do analizy
            context: Dodatkowy kontekst

        Returns:
            EngagementReport z propozycjami zaangażowania
        """
        input_text = f"## TREŚĆ DO ANALIZY\n\n{content}"

        if context:
            if context.get("extracted_data"):
                input_text += f"\n\n## WYEKSTRAHOWANE DANE\n{json.dumps(context['extracted_data'], ensure_ascii=False, indent=2)}"
            if context.get("platform"):
                input_text += f"\n\n## PLATFORMA: {context['platform']}"

        messages = [
            {"role": "system", "content": self.prompt_template},
            {"role": "user", "content": input_text},
        ]

        response = self.client.chat(
            messages=messages,
            model_key=self.model_key,
            temperature=0.7,
            max_tokens=3000,
        )

        return self._parse_response(response.content)

    def _parse_response(self, response: str) -> EngagementReport:
        """Parsuje odpowiedź JSON do EngagementReport."""
        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_start = re.search(r'```json\s*', response)
                if json_start:
                    json_str = response[json_start.end():]
                    if '```' in json_str:
                        json_str = json_str[:json_str.rfind('```')]
                    logger.warning("Engagement: Używam fallback parsowania")
                else:
                    json_str = response

            json_str = json_str.strip()
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("Engagement: Próba naprawy uciętego JSON...")
                repaired = self._repair_truncated_json(json_str)
                data = json.loads(repaired)

            return EngagementReport(
                engagement_potential=data.get("potencjal_zaangazowania", 5),
                existing_hooks=data.get("obecne_haki", []),
                missing_elements=data.get("brakujace_elementy", []),
                boosters=data.get("wzmacniacze", []),
                question_improvements=data.get("ulepszenia_pytan", []),
                cta_options=data.get("opcje_cta", {}),
                relatable_moments=data.get("momenty_relatable", []),
                platform_ctas=data.get("cta_platformy", {}),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Engagement: JSON parse error: {e}")
            logger.error(f"Engagement: Raw response (first 500 chars): {response[:500]}")
            return EngagementReport(
                engagement_potential=0,
                existing_hooks=[],
                missing_elements=[],
                boosters=[],
                question_improvements=[],
                cta_options={},
                relatable_moments=[],
                platform_ctas={},
            )
        except Exception as e:
            logger.error(f"Engagement: Unexpected error: {e}")
            return EngagementReport(
                engagement_potential=0,
                existing_hooks=[],
                missing_elements=[],
                boosters=[],
                question_improvements=[],
                cta_options={},
                relatable_moments=[],
                platform_ctas={},
            )

    def _repair_truncated_json(self, json_str: str) -> str:
        """Próbuje naprawić ucięty JSON."""
        open_braces = json_str.count('{') - json_str.count('}')
        open_brackets = json_str.count('[') - json_str.count(']')
        last_complete = max(json_str.rfind('},'), json_str.rfind('],'), json_str.rfind('",'))
        if last_complete > 0:
            json_str = json_str[:last_complete + 1]
            open_braces = json_str.count('{') - json_str.count('}')
            open_brackets = json_str.count('[') - json_str.count(']')
        json_str += ']' * open_brackets + '}' * open_braces
        return json_str

    def analyze(
        self,
        content: str,
        mode: str = "source",
        platform: Optional[str] = None,
        humor_dial: Optional[int] = None,
        context: Optional[dict] = None,
        on_progress=None,
    ) -> AgentResult:
        """Implementacja interfejsu BaseAgent."""
        if on_progress:
            on_progress("Analizuję potencjał zaangażowania...")

        if context is None:
            context = {}
        if platform:
            context["platform"] = platform

        report = self.engineer(content, context)
        result_content = json.dumps(report.to_dict(), ensure_ascii=False, indent=2)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=result_content,
            score=float(report.engagement_potential),
        )
