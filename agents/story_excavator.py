"""Archeolog Historii - finds narrative elements hidden in dry content."""

import json
import re
import logging
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient

logger = logging.getLogger(__name__)


@dataclass
class StoryReport:
    """Raport z analizy narracyjnej."""
    narrative_potential: int  # 1-10
    characters: list  # postacie
    conflict: dict  # konflikt/napięcie
    transformation_arc: dict  # łuk transformacji
    story_based_post: str  # wariant posta
    missing_elements: list  # pytania do autora
    alternative_angles: list  # alternatywne kąty

    def to_dict(self) -> dict:
        return {
            "potencjal_narracyjny": self.narrative_potential,
            "postacie": self.characters,
            "konflikt": self.conflict,
            "luk_transformacji": self.transformation_arc,
            "post_narracyjny": self.story_based_post,
            "brakujace_elementy": self.missing_elements,
            "alternatywne_katy": self.alternative_angles,
        }


class StoryExcavatorAgent(BaseAgent):
    """Agent that extracts story elements from source content."""

    name = "story_excavator"
    name_pl = "Archeolog Historii"
    description = "Znajduje i wydobywa elementy narracyjne ukryte w suchej treści"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# ARCHEOLOG HISTORII

Wydobywasz historie z suchych treści. Ludzie pamiętają historie, nie fakty.

## ZASADA
"68% firm upada" → zapominam
"Zamknąłem firmę, zostało 2000 zł" → pamiętam

## CO SZUKASZ
1. **Ukryci protagoniści** - kto podjął decyzję? kto zapłacił cenę?
2. **Konflikt** - walka, przeszkoda, ryzyko
3. **Transformacja** - Przed → Wyzwalacz → Po
4. **Konkretne momenty** - "3 w nocy, laptop..."
5. **Emocje** - dlaczego to ważne?

## ZASADY ZWIĘZŁOŚCI
- Max 3 postacie
- Max 3 pytania do autora
- Max 3 alternatywne kąty
- Post narracyjny = max 200 słów

## FORMAT ODPOWIEDZI

```json
{
  "potencjal_narracyjny": 8,
  "postacie": [
    {"kto": "Jan Kowalski", "rola": "założyciel", "potencjal": "upadek i powrót"}
  ],
  "konflikt": {
    "glowny": "walka z rynkiem",
    "stawka": "firma i oszczędności",
    "antagonista": "brak klientów"
  },
  "luk_transformacji": {
    "przed": "pewny sukcesu",
    "wyzwalacz": "pierwszy miesiąc bez klienta",
    "po": "nauczył się słuchać rynku",
    "znaczenie": "pokora ważniejsza od wizji"
  },
  "post_narracyjny": "Gotowy wariant posta oparty na historii...",
  "brakujace_elementy": [
    "Co czułeś w momencie decyzji?",
    "Jaki był najtrudniejszy dzień?"
  ],
  "alternatywne_katy": [
    {"perspektywa": "historia porażki", "hook": "Zamknąłem firmę po 11 miesiącach..."},
    {"perspektywa": "behind the scenes", "hook": "Nikt nie widział nocnych maili..."}
  ]
}
```

## ZŁOTE ZASADY
- Konkret > abstrakcja ("wtorek 15:47" > "pewnego dnia")
- Pokaż, nie mów ("trzęsły mi się ręce" > "byłem zdenerwowany")
- Jedna osoba > statystyka
- NIE wymyślaj faktów - pytaj autora o detale
"""

    def excavate(self, content: str, context: Optional[dict] = None) -> StoryReport:
        """
        Wydobywa elementy narracyjne z treści.

        Args:
            content: Treść do analizy
            context: Dodatkowy kontekst

        Returns:
            StoryReport z elementami narracyjnymi
        """
        input_text = f"## TREŚĆ DO ANALIZY\n\n{content}"

        if context:
            if context.get("extracted_data"):
                input_text += f"\n\n## WYEKSTRAHOWANE DANE\n{json.dumps(context['extracted_data'], ensure_ascii=False, indent=2)}"

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

    def _parse_response(self, response: str) -> StoryReport:
        """Parsuje odpowiedź JSON do StoryReport."""
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
                    logger.warning("StoryExcavator: Używam fallback parsowania")
                else:
                    json_str = response

            json_str = json_str.strip()
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("StoryExcavator: Próba naprawy uciętego JSON...")
                repaired = self._repair_truncated_json(json_str)
                data = json.loads(repaired)

            return StoryReport(
                narrative_potential=data.get("potencjal_narracyjny", 5),
                characters=data.get("postacie", []),
                conflict=data.get("konflikt", {}),
                transformation_arc=data.get("luk_transformacji", {}),
                story_based_post=data.get("post_narracyjny", ""),
                missing_elements=data.get("brakujace_elementy", []),
                alternative_angles=data.get("alternatywne_katy", []),
            )

        except json.JSONDecodeError as e:
            logger.error(f"StoryExcavator: JSON parse error: {e}")
            logger.error(f"StoryExcavator: Raw response (first 500 chars): {response[:500]}")
            return StoryReport(
                narrative_potential=0,
                characters=[],
                conflict={},
                transformation_arc={},
                story_based_post="",
                missing_elements=[],
                alternative_angles=[],
            )
        except Exception as e:
            logger.error(f"StoryExcavator: Unexpected error: {e}")
            return StoryReport(
                narrative_potential=0,
                characters=[],
                conflict={},
                transformation_arc={},
                story_based_post="",
                missing_elements=[],
                alternative_angles=[],
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
            on_progress("Wydobywam elementy narracyjne...")

        report = self.excavate(content, context)
        result_content = json.dumps(report.to_dict(), ensure_ascii=False, indent=2)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=result_content,
            score=float(report.narrative_potential),
        )
