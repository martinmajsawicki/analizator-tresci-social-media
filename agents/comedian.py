"""Komik - finds opportunities for wit and humor."""

import json
import re
import logging
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient

logger = logging.getLogger(__name__)


@dataclass
class HumorReport:
    """Raport z analizy potencjału humoru."""
    humor_potential: int  # 1-10
    recommended_dial: int  # 1-5
    humor_opportunities: list  # okazje na humor
    self_deprecation_moments: list  # momenty na self-deprecation
    rewrite_options: dict  # opcje przepisania wg dial
    humor_warnings: list  # czego unikać
    techniques: list  # techniki do zastosowania

    def to_dict(self) -> dict:
        return {
            "potencjal_humoru": self.humor_potential,
            "rekomendowany_dial": self.recommended_dial,
            "okazje_na_humor": self.humor_opportunities,
            "momenty_self_deprecation": self.self_deprecation_moments,
            "wersje_wg_dial": self.rewrite_options,
            "ostrzezenia": self.humor_warnings,
            "techniki": self.techniques,
        }


class ComedianAgent(BaseAgent):
    """Agent that finds and suggests humor opportunities."""

    name = "comedian"
    name_pl = "Komik"
    description = "Znajduje okazje na humor i lekkość bez wymuszania żartów"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# KOMIK

Dodajesz lekkość i zapamiętywalność przez humor dopasowany do platformy.

## DWA TRYBY PRACY

### TRYB ŹRÓDŁO (eksploracja)
Gdy analizujesz badanie/artykuł - szukasz:
- **Potencjału komediowego** w temacie (co jest absurdalne, zaskakujące?)
- **Uniwersalnych obserwacji** które rozśmieszą ("wszyscy to znamy")
- **Kontrastów** między oczekiwaniem a rzeczywistością

### TRYB POST (ulepszanie)
Gdy analizujesz gotowy post - szukasz:
- **Miejsc na wstawkę** humorystyczną
- **Zbyt poważnych fragmentów** które można rozluźnić

## POKRĘTŁO HUMORU (1-5)
1. Subtelny dowcip - bezpieczny dla LinkedIn
2. Self-deprecation - śmianie się z siebie
3. Komedia obserwacyjna - "wszyscy to znamy"
4. Odważny/sarkazm - kontrowersja z uśmiechem
5. Pełny absurd - niespodziewane zwroty

## ZASADY ZWIĘZŁOŚCI
- Max 3 okazje na humor
- Max 2 momenty self-deprecation
- 3 wersje dial (poziom 2, 3, 4)
- Max 2 ostrzeżenia
- Max 2 techniki

## FORMAT ODPOWIEDZI

```json
{
  "potencjal_humoru": 7,
  "rekomendowany_dial": 3,
  "okazje_na_humor": [
    {"lokalizacja": "otwarcie", "typ": "obserwacja", "sugestia": "Konkretny żart...", "dial": 3}
  ],
  "momenty_self_deprecation": [
    "Przyznanie do błędu z mrugnięciem oka"
  ],
  "wersje_wg_dial": {
    "dial_2_linkedin": "Bezpieczna wersja z subtelną ironią...",
    "dial_3_facebook": "Odważniejsza wersja z obserwacją...",
    "dial_4_twitter": "Sarkastyczna wersja..."
  },
  "ostrzezenia": [
    "Unikaj żartów o konkretnych firmach"
  ],
  "techniki": [
    {"nazwa": "Kontrast oczekiwań", "przyklad": "Spodziewałem się X. Dostałem Y."}
  ]
}
```

## WAŻNE ZASADY
- NIE wymuszaj humoru gdzie nie pasuje
- Humor wzmacnia przekaz, nie rozprasza
- Self-deprecation > żarty z innych
- Krótsze = śmieszniejsze
- Jeśli musisz wyjaśniać żart - nie jest dobry

## PRZYKŁADY WG DIAL

**Dial 2 (LinkedIn):**
"Moja pierwsza prezentacja? Slajdy w złej kolejności."

**Dial 3 (Facebook):**
"Mówiłem że nigdy nie będę TYM rodzicem. Piszę to ze sklepu o 7:45."

**Dial 4 (X/Twitter):**
"dzisiejszy błąd: reply-all. jutrzejszy błąd: tbd ale nadchodzi"
"""

    def find_humor(self, content: str, context: Optional[dict] = None) -> HumorReport:
        """
        Szuka okazji na humor w treści.

        Args:
            content: Treść do analizy
            context: Dodatkowy kontekst

        Returns:
            HumorReport z propozycjami humoru
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
            temperature=0.8,  # Wyższa temperatura dla kreatywności
            max_tokens=3000,
        )

        return self._parse_response(response.content)

    def _parse_response(self, response: str) -> HumorReport:
        """Parsuje odpowiedź JSON do HumorReport."""
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
                    logger.warning("Comedian: Używam fallback parsowania")
                else:
                    json_str = response

            json_str = json_str.strip()
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("Comedian: Próba naprawy uciętego JSON...")
                repaired = self._repair_truncated_json(json_str)
                data = json.loads(repaired)

            return HumorReport(
                humor_potential=data.get("potencjal_humoru", 5),
                recommended_dial=data.get("rekomendowany_dial", 3),
                humor_opportunities=data.get("okazje_na_humor", []),
                self_deprecation_moments=data.get("momenty_self_deprecation", []),
                rewrite_options=data.get("wersje_wg_dial", {}),
                humor_warnings=data.get("ostrzezenia", []),
                techniques=data.get("techniki", []),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Comedian: JSON parse error: {e}")
            logger.error(f"Comedian: Raw response (first 500 chars): {response[:500]}")
            return HumorReport(
                humor_potential=0,
                recommended_dial=3,
                humor_opportunities=[],
                self_deprecation_moments=[],
                rewrite_options={},
                humor_warnings=[],
                techniques=[],
            )
        except Exception as e:
            logger.error(f"Comedian: Unexpected error: {e}")
            return HumorReport(
                humor_potential=0,
                recommended_dial=3,
                humor_opportunities=[],
                self_deprecation_moments=[],
                rewrite_options={},
                humor_warnings=[],
                techniques=[],
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
            on_progress("Szukam okazji na humor...")

        if context is None:
            context = {}
        if platform:
            context["platform"] = platform

        report = self.find_humor(content, context)
        result_content = json.dumps(report.to_dict(), ensure_ascii=False, indent=2)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=result_content,
            score=float(report.humor_potential),
        )
