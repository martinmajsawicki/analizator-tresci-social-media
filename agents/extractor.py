"""Agent 0: Ekstraktor inputu - rozdziela źródło od uwag usera."""

import json
import re
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient


@dataclass
class ExtractedInput:
    """Wynik ekstrakcji inputu."""
    # Źródło
    source_title: Optional[str] = None
    source_author: Optional[str] = None
    source_date: Optional[str] = None
    source_link: Optional[str] = None
    source_type: str = "unknown"  # "badanie", "artykuł", "news", "opinia", "własne_testy"
    key_facts: list = None
    quotes: list = None
    numbers: list = None
    conclusions: list = None

    # Uwagi usera
    user_notes: Optional[str] = None
    user_direction: Optional[str] = None
    user_priority: str = "normalny"  # "wysoki" jeśli user podał kierunek

    # Surowe dane
    raw_content: str = ""

    def __post_init__(self):
        if self.key_facts is None:
            self.key_facts = []
        if self.quotes is None:
            self.quotes = []
        if self.numbers is None:
            self.numbers = []
        if self.conclusions is None:
            self.conclusions = []

    def to_dict(self) -> dict:
        return {
            "źródło": {
                "tytuł": self.source_title,
                "autor": self.source_author,
                "data": self.source_date,
                "link": self.source_link,
                "typ": self.source_type,
                "kluczowe_fakty": self.key_facts,
            },
            "uwagi_usera": {
                "treść": self.user_notes,
                "kierunek": self.user_direction,
                "priorytet": self.user_priority,
            },
            "surowe_dane": {
                "cytaty": self.quotes,
                "liczby": self.numbers,
                "wnioski_badania": self.conclusions,
            },
        }


class ExtractorAgent(BaseAgent):
    """
    Agent 0: Ekstraktor inputu.

    Zadania:
    - Rozdziel: co jest ŹRÓDŁEM, a co jest UWAGĄ USERA
    - Uwagi usera = PRIORYTET (flaguj, przekaż dalej wszystkim)
    - Wyciągnij: fakty, dane, cytaty, źródło, datę
    """

    name = "extractor"
    name_pl = "Ekstraktor Inputu"
    description = "Rozdziela źródło od uwag użytkownika i ekstrahuje kluczowe dane"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# EKSTRAKTOR INPUTU

Jesteś ekspertem od ekstrakcji kluczowych danych z tekstów źródłowych.

## ZADANIE

1. **ROZDZIEL** input na: ŹRÓDŁO vs UWAGI USERA
2. **EKSTRAHUJ** najważniejsze elementy:
   - Cytaty dosłowne (max 5 najlepszych)
   - Liczby i dane (max 5)
   - Kluczowe fakty (max 5)
   - Wnioski badania/artykułu (max 3)

## ZASADY ZWIĘZŁOŚCI

- Max 5 elementów na kategorię
- Cytaty = dosłownie, krótkie
- Liczby = z kontekstem
- Fakty = 1 zdanie

## FORMAT ODPOWIEDZI

```json
{
  "źródło": {
    "tytuł": "...",
    "autor": "Imię Nazwisko, rola",
    "data": "...",
    "link": "...",
    "typ": "badanie|artykuł|news|opinia",
    "kluczowe_fakty": [
      "fakt 1",
      "fakt 2"
    ]
  },
  "cytaty": [
    {
      "cytat": "dosłowny cytat",
      "kto": "autor cytatu"
    }
  ],
  "liczby": [
    {
      "wartosc": "30%",
      "kontekst": "co to znaczy"
    }
  ],
  "wnioski": [
    "wniosek 1",
    "wniosek 2"
  ],
  "uwagi_usera": {
    "treść": "...",
    "kierunek": "...",
    "priorytet": "wysoki|normalny"
  }
}
```

## PRZYKŁAD

INPUT: Badanie Nature o AI w edukacji

OUTPUT:
```json
{
  "źródło": {
    "tytuł": "AI in Education: A Meta-Analysis",
    "autor": "John Smith, Harvard",
    "data": "2024-01",
    "typ": "badanie",
    "kluczowe_fakty": [
      "AI poprawia wyniki o 15%",
      "Efekt silniejszy u słabszych uczniów"
    ]
  },
  "cytaty": [
    {"cytat": "AI is not a replacement, but an amplifier", "kto": "John Smith"}
  ],
  "liczby": [
    {"wartosc": "15%", "kontekst": "poprawa wyników"}
  ],
  "wnioski": [
    "AI wspiera, nie zastępuje nauczyciela"
  ],
  "uwagi_usera": {
    "treść": null,
    "kierunek": null,
    "priorytet": "normalny"
  }
}
```
"""

    def extract(
        self,
        content: str,
        user_notes: Optional[str] = None,
    ) -> ExtractedInput:
        """
        Ekstrahuje dane z inputu.

        Args:
            content: Główna treść (źródło, artykuł, badanie)
            user_notes: Opcjonalne uwagi użytkownika

        Returns:
            ExtractedInput z rozdzielonymi danymi
        """
        # Przygotuj input
        full_input = content
        if user_notes:
            full_input = f"ŹRÓDŁO:\n{content}\n\nUWAGI UŻYTKOWNIKA:\n{user_notes}"

        messages = [
            {"role": "system", "content": self.prompt_template},
            {"role": "user", "content": full_input},
        ]

        response = self.client.chat(
            messages=messages,
            model_key=self.model_key,
            temperature=0.3,  # Niska temperatura dla precyzyjnej ekstrakcji
            max_tokens=3000,
        )

        # Parsuj JSON z odpowiedzi
        extracted = self._parse_response(response.content, content)

        return extracted

    def _parse_response(self, response: str, original_content: str) -> ExtractedInput:
        """Parsuje odpowiedź JSON do ExtractedInput."""
        import logging
        logger = logging.getLogger(__name__)

        try:
            # 1. Spróbuj normalnego regex z zamykającym tagiem
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 2. Fallback: wyciągnij JSON po ```json
                json_start = re.search(r'```json\s*', response)
                if json_start:
                    json_str = response[json_start.end():]
                    if '```' in json_str:
                        json_str = json_str[:json_str.rfind('```')]
                    logger.warning("Extractor: Używam fallback parsowania")
                else:
                    json_str = response

            json_str = json_str.strip()
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("Extractor: Próba naprawy uciętego JSON...")
                repaired = self._repair_truncated_json(json_str)
                data = json.loads(repaired)

            source = data.get("źródło", {})
            user = data.get("uwagi_usera", {})

            # Obsłuż oba warianty kluczy (nowy i stary format)
            quotes = data.get("cytaty", source.get("cytaty", []))
            numbers = data.get("liczby", source.get("liczby", []))
            conclusions = data.get("wnioski", source.get("wnioski", []))

            return ExtractedInput(
                source_title=source.get("tytuł"),
                source_author=source.get("autor"),
                source_date=source.get("data"),
                source_link=source.get("link"),
                source_type=source.get("typ", "unknown"),
                key_facts=source.get("kluczowe_fakty", []),
                quotes=quotes,
                numbers=numbers,
                conclusions=conclusions,
                user_notes=user.get("treść"),
                user_direction=user.get("kierunek"),
                user_priority=user.get("priorytet", "normalny"),
                raw_content=original_content,
            )

        except json.JSONDecodeError as e:
            logger.error(f"Extractor: JSON parse error: {e}")
            logger.error(f"Extractor: Raw response (first 500 chars): {response[:500]}")
            return ExtractedInput(
                raw_content=original_content,
                user_notes=None,
                source_type="unknown",
            )
        except Exception as e:
            logger.error(f"Extractor: Unexpected error: {e}")
            return ExtractedInput(
                raw_content=original_content,
                user_notes=None,
                source_type="unknown",
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
        """
        Implementacja interfejsu BaseAgent.
        """
        if on_progress:
            on_progress("Ekstrahuję dane z inputu...")

        user_notes = context.get("user_notes") if context else None
        extracted = self.extract(content, user_notes)

        result_content = json.dumps(extracted.to_dict(), ensure_ascii=False, indent=2)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=result_content,
        )
