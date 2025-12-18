"""Agent 1: Łowca Rezonansu - znajduje punkty zaczepienia z odbiorcą."""

import json
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient
from core.filters import (
    BASE_FEARS,
    BASE_OBJECTIONS,
    CONTEXTUAL_FILTERS,
    UNEXPECTED_FILTERS,
    analyze_content_for_filters,
    get_seasonal_keywords,
)


@dataclass
class ResonanceReport:
    """Raport rezonansu."""
    user_direction_assessment: dict  # ocena uwag usera
    base_filter_matches: list  # dopasowania do obaw/zarzutów
    contextual_matches: list  # dopasowania kontekstowe
    unexpected_suggestions: list  # sugestie nieoczywiste
    top3_recommendations: list  # TOP 3 rekomendacje hooków

    def to_dict(self) -> dict:
        return {
            "uwaga_usera_ocena": self.user_direction_assessment,
            "filtry_bazowe": self.base_filter_matches,
            "filtry_kontekstowe": self.contextual_matches,
            "filtry_nieoczywiste": self.unexpected_suggestions,
            "rekomendacja_top3": self.top3_recommendations,
        }


class ResonanceHunterAgent(BaseAgent):
    """
    Agent 1: Łowca Rezonansu.

    Zadanie: Znaleźć WSZYSTKIE możliwe punkty zaczepienia z odbiorcą.

    Filtry:
    - BAZOWE: 7 obaw + 2 zarzuty dotyczące AI
    - KONTEKSTOWE: polska aktualność, sezonowość, zawody
    - NIEOCZYWISTE: analogie, prowokacje, odwrócenia, personalizacja
    """

    name = "resonance_hunter"
    name_pl = "Łowca Rezonansu"
    description = "Znajduje wszystkie możliwe punkty zaczepienia treści z odbiorcą"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return self._build_full_prompt()

    def _build_full_prompt(self) -> str:
        """Buduje pełny prompt z wszystkimi filtrami."""

        # Sekcja obaw
        fears_section = "### 7 OBAW DOTYCZĄCYCH AI\n\n"
        for key, fear in BASE_FEARS.items():
            fears_section += f"**{fear['name']}**\n"
            fears_section += f"- Słowa kluczowe: {', '.join(fear['keywords'][:5])}...\n"
            fears_section += f"- Przykładowe hooki: {fear['hook_templates'][0]}\n\n"

        # Sekcja zarzutów
        objections_section = "### 2 ZARZUTY WOBEC AI\n\n"
        for key, obj in BASE_OBJECTIONS.items():
            objections_section += f"**{obj['name']}**\n"
            objections_section += f"- Słowa kluczowe: {', '.join(obj['keywords'][:5])}...\n"
            objections_section += f"- Przykładowy hook: {obj['hook_templates'][0]}\n\n"

        # Sekcja kontekstowa
        context_section = "### FILTRY KONTEKSTOWE (tu i teraz)\n\n"
        for key, ctx in CONTEXTUAL_FILTERS.items():
            context_section += f"**{ctx['name']}**\n"
            if ctx['keywords']:
                context_section += f"- Szukaj: {', '.join(ctx['keywords'][:5])}...\n"
            context_section += "\n"

        # Sekcja sezonowa
        seasonal = get_seasonal_keywords()
        context_section += f"**Aktualny sezon** (grudzień):\n"
        context_section += f"- Słowa: {', '.join(seasonal)}\n\n"

        # Sekcja nieoczywista
        unexpected_section = "### FILTRY NIEOCZYWISTE\n\n"
        for key, unexp in UNEXPECTED_FILTERS.items():
            unexpected_section += f"**{unexp['name']}**\n"
            unexpected_section += f"- Wzorce: {unexp['patterns'][0]}\n"
            unexpected_section += f"- Przykład: {unexp['examples'][0]}\n\n"

        return f"""# ŁOWCA REZONANSU

Jesteś ekspertem od znajdowania punktów zaczepienia treści z odbiorcą. Twoje zadanie to przeszukanie WSZYSTKICH możliwych połączeń między tematem a tym, co interesuje/niepokoi czytelnika.

## ZASADA NADRZĘDNA

**Jeśli user podał własny kierunek → TESTUJ GO NAJPIERW**

Uwagi usera mają priorytet nad automatyczną analizą. Sprawdź czy kierunek usera jest dobry, oceń go, ale jeśli jest sensowny - rozwijaj przede wszystkim ten kierunek.

## FILTRY BAZOWE (obawy i zarzuty)

{fears_section}

{objections_section}

## FILTRY KONTEKSTOWE

{context_section}

## FILTRY NIEOCZYWISTE (poza schematem)

{unexpected_section}

## ZASADY ZWIĘZŁOŚCI

- HOOK = najważniejsze. Reszta to kontekst.
- Max 3-5 hooków na kategorię (nie 10)
- Nie tłumacz dlaczego coś jest dobre - po prostu daj hook
- Skala siły: 1-10 (nie 1-5)

## FORMAT ODPOWIEDZI

```json
{{
  "uwaga_usera_ocena": {{
    "kierunek_usera": "...",
    "ocena": "doskonały|dobry|słaby|brak"
  }},
  "filtry_bazowe": [
    {{
      "hook": "propozycja hooka",
      "źródło": "nazwa obawy/zarzutu",
      "siła": 8
    }}
  ],
  "filtry_kontekstowe": [
    {{
      "hook": "propozycja hooka",
      "kontekst": "polski kontekst (max 5 słów)",
      "siła": 7
    }}
  ],
  "filtry_nieoczywiste": [
    {{
      "hook": "propozycja hooka",
      "typ": "analogia|pytanie|odwrócenie|personalizacja",
      "siła": 9
    }}
  ],
  "top3": [
    {{
      "hook": "najlepszy hook",
      "siła": 9
    }}
  ]
}}
```

## WSKAZÓWKI

1. **NIE zaczynaj od źródła** - hook ma zaczynać od czytelnika, nie od "Nowe badanie..."
2. **Szukaj paradoksów** - "Boimy się X, ale robimy Y"
3. **Personalizuj** - "Twój...", "Czy Ty też..."
4. **Bądź konkretny** - liczby, nazwy, daty
5. **Testuj kontrowersję** - co by było, gdyby...

## PRZYKŁAD DOBREJ ANALIZY

INPUT: Badanie Nature o wpływie chatbotów na poglądy wyborcze
USER: Podpiąć pod polskie wybory

ANALIZA:
- Kierunek usera: DOSKONAŁY (wybory PL to gorący temat)
- Filtr bazowy: "AI zaleje nas kłamstwem" → siła 5
- Filtr kontekstowy: Wybory prezydenckie 2025
- Filtr nieoczywisty: Odwrócenie - "A co jeśli to wyborcy manipulują AI?"

TOP HOOK: "ChatGPT właśnie zmienił zdanie o Nawrockim. A może to Ty zmieniłeś swoje?"
"""

    def hunt(
        self,
        extracted_data: dict,
        user_direction: Optional[str] = None,
    ) -> ResonanceReport:
        """
        Szuka punktów rezonansu.

        Args:
            extracted_data: Dane z ExtractorAgent
            user_direction: Kierunek podany przez usera

        Returns:
            ResonanceReport z wszystkimi dopasowaniami
        """
        # Przygotuj input dla agenta
        input_text = f"""## DANE ŹRÓDŁOWE

{json.dumps(extracted_data, ensure_ascii=False, indent=2)}

## KIERUNEK UŻYTKOWNIKA

{user_direction if user_direction else "Brak - znajdź najlepsze zaczepienia automatycznie"}

Przeanalizuj wszystkie możliwe punkty rezonansu z odbiorcą.
"""

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

    def _parse_response(self, response: str) -> ResonanceReport:
        """Parsuje odpowiedź do ResonanceReport."""
        import re
        import logging
        logger = logging.getLogger(__name__)

        try:
            # 1. Spróbuj normalnego regex z zamykającym tagiem
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 2. Fallback: wyciągnij JSON po ```json (nawet bez zamknięcia)
                json_start = re.search(r'```json\s*', response)
                if json_start:
                    json_str = response[json_start.end():]
                    if '```' in json_str:
                        json_str = json_str[:json_str.rfind('```')]
                    logger.warning("ResonanceHunter: Używam fallback parsowania")
                else:
                    json_str = response

            json_str = json_str.strip()
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("ResonanceHunter: Próba naprawy uciętego JSON...")
                repaired = self._repair_truncated_json(json_str)
                data = json.loads(repaired)

            # Obsłuż oba warianty kluczy (top3 i rekomendacja_top3)
            top3 = data.get("top3", data.get("rekomendacja_top3", []))

            return ResonanceReport(
                user_direction_assessment=data.get("uwaga_usera_ocena", {}),
                base_filter_matches=data.get("filtry_bazowe", []),
                contextual_matches=data.get("filtry_kontekstowe", []),
                unexpected_suggestions=data.get("filtry_nieoczywiste", []),
                top3_recommendations=top3,
            )

        except json.JSONDecodeError as e:
            logger.error(f"ResonanceHunter: JSON parse error: {e}")
            logger.error(f"ResonanceHunter: Raw response (first 500 chars): {response[:500]}")
            return ResonanceReport(
                user_direction_assessment={},
                base_filter_matches=[],
                contextual_matches=[],
                unexpected_suggestions=[],
                top3_recommendations=[],
            )
        except Exception as e:
            logger.error(f"ResonanceHunter: Unexpected error: {e}")
            return ResonanceReport(
                user_direction_assessment={},
                base_filter_matches=[],
                contextual_matches=[],
                unexpected_suggestions=[],
                top3_recommendations=[],
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
        platform=None,
        humor_dial: Optional[int] = None,
        context: Optional[dict] = None,
        on_progress=None,
    ) -> AgentResult:
        """Implementacja interfejsu BaseAgent."""
        if on_progress:
            on_progress("Szukam punktów rezonansu...")

        # Pobierz dane z kontekstu
        extracted_data = context.get("extracted_data", {}) if context else {}
        user_direction = context.get("user_direction") if context else None

        # Jeśli brak extracted_data, użyj content jako surowych danych
        if not extracted_data:
            extracted_data = {"raw_content": content}

        report = self.hunt(extracted_data, user_direction)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        )
