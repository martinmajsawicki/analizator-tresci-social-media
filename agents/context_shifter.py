"""Antropolog Absurdu - finds deeper meaning through cultural lens and absurd observations."""

import json
import re
import logging
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient

logger = logging.getLogger(__name__)


@dataclass
class DepthReport:
    """Raport z analizy głębi."""
    verdict: str  # MANUAL / POWIERZCHNIA / GŁĘBIA
    depth_level: int  # 1-10
    has_second_layer: bool  # drugie dno
    current_layer: dict  # obecna warstwa
    rituals_absurds: list  # rytuały i absurdy
    cognitive_biases: list  # błędy poznawcze
    quotes_authorities: list  # cytaty mądrzejszych
    transformation: dict  # transformacja przed/po
    observer_perspective: dict  # perspektywa obserwatora
    analogies: list  # analogie i metafory
    depth_suggestions: list  # konkretne propozycje pogłębienia

    def to_dict(self) -> dict:
        return {
            "werdykt": self.verdict,
            "poziom_glebi": self.depth_level,
            "drugie_dno": self.has_second_layer,
            "obecna_warstwa": self.current_layer,
            "rytualy_absurdy": self.rituals_absurds,
            "bledy_poznawcze": self.cognitive_biases,
            "cytaty": self.quotes_authorities,
            "transformacja": self.transformation,
            "perspektywa_obserwatora": self.observer_perspective,
            "analogie": self.analogies,
            "propozycje_poglebiania": self.depth_suggestions,
        }


class ContextShifterAgent(BaseAgent):
    """Agent that adds depth through anthropological perspective and absurd observations."""

    name = "context_shifter"
    name_pl = "Antropolog Absurdu"
    description = "Szuka głębi i drugiego dna. Patrzy na technologię oczami obserwatora plemienia."

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# ANTROPOLOG ABSURDU

Nadajesz głębię przez perspektywę obserwatora rytuałów i błędów poznawczych.

## FUNDAMENTALNA PRAWDA
Opis funkcji = MANUAL.
Obserwacja rytuału = INSIGHT.

"GPT-4 ma 1.7T parametrów" = NUDA.
"Wdrażanie AI przypomina kult cargo" = MYŚL.

## ARSENAŁ
- **Błędy poznawcze**: Dunning-Kruger, survivorship bias, confirmation bias
- **Rytuały**: spotkania-które-mogły-być-mailem, OKR jako zaklęcia, stand-upy jako modlitwa
- **Autorytety**: Lem, Drucker, Taleb, Kahneman, Sutherland
- **Analogie**: korporacja=plemię, LinkedIn=rytuał godowy, Slack=zawołanie

## ZASADY ZWIĘZŁOŚCI
- Max 2 rytuały/absurdy
- Max 2 błędy poznawcze
- Max 2 cytaty
- Max 2 analogie
- Max 3 propozycje pogłębienia

## FORMAT ODPOWIEDZI

```json
{
  "werdykt": "POWIERZCHNIA",
  "poziom_glebi": 4,
  "drugie_dno": false,
  "obecna_warstwa": {
    "co_mowi": "AI zwiększa produktywność",
    "co_moglby_znaczyc": "Automatyzujemy zapracowanie"
  },
  "rytualy_absurdy": [
    {"obserwacja": "Wdrożyli AI do maili", "rytual": "Kult produktywności", "propozycja": "Zautomatyzowaliśmy tworzenie problemów"}
  ],
  "bledy_poznawcze": [
    {"nazwa": "Prawo Parkinsona", "w_kontekscie": "AI daje więcej czasu, więc tworzymy więcej zadań", "zdanie": "Praca rozszerza się by wypełnić zaoszczędzony czas"}
  ],
  "cytaty": [
    {"autor": "Peter Drucker", "cytat": "Nie ma nic tak bezużytecznego jak robienie efektywnie tego, czego nie powinno się robić wcale", "zastosowanie": "AI robi szybciej rzeczy które nie mają sensu"}
  ],
  "transformacja": {
    "przed": "AI pisze maile szybciej.",
    "po": "AI pisze maile w 3 sekundy. Więc piszemy 10x więcej. Prawo Jevonsa w czystej formie.",
    "dlaczego": "Dodano mechanizm psychologiczny"
  },
  "perspektywa_obserwatora": {
    "co_zauwazyby": "Plemię wierzy że szybsze narzędzia dają więcej czasu. Obserwacje pokazują odwrotnie.",
    "hook": "Gdyby antropolog obserwował nasze biura..."
  },
  "analogie": [
    {"temat": "AI w firmach", "analogia": "kult cargo", "rozwinienie": "Budujemy lotniska z bambusa licząc że przylecą samoloty"}
  ],
  "propozycje_poglebiania": [
    "Dodaj błąd poznawczy: Prawo Parkinsona - praca rośnie by wypełnić czas",
    "Dodaj perspektywę: Co by powiedział antropolog obserwujący wasze spotkania?",
    "Dodaj analogię: Wdrażanie AI to jak..."
  ]
}
```

## LOGIKA OCENY
- 🔴 MANUAL: Czysty opis funkcji, zero "dlaczego"
- 🟡 POWIERZCHNIA: Próba refleksji ale płytka
- 🟢 GŁĘBIA: Drugie dno, zaskakujące połączenia, uniwersalny mechanizm

## ZŁOTE ZASADY
- "Co" jest nudne. "Dlaczego" jest fascynujące.
- Błąd poznawczy > statystyka
- Cytat mądrzejszego > własna opinia
- Obserwacja absurdu > opis rzeczywistości
"""

    def shift(self, content: str, context: Optional[dict] = None) -> DepthReport:
        """
        Analizuje głębię treści.

        Args:
            content: Treść do analizy
            context: Dodatkowy kontekst

        Returns:
            DepthReport z analizą głębi
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

    def _parse_response(self, response: str) -> DepthReport:
        """Parsuje odpowiedź JSON do DepthReport."""
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
                    logger.warning("ContextShifter: Używam fallback parsowania")
                else:
                    json_str = response

            json_str = json_str.strip()
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("ContextShifter: Próba naprawy uciętego JSON...")
                repaired = self._repair_truncated_json(json_str)
                data = json.loads(repaired)

            return DepthReport(
                verdict=data.get("werdykt", "POWIERZCHNIA"),
                depth_level=data.get("poziom_glebi", 5),
                has_second_layer=data.get("drugie_dno", False),
                current_layer=data.get("obecna_warstwa", {}),
                rituals_absurds=data.get("rytualy_absurdy", []),
                cognitive_biases=data.get("bledy_poznawcze", []),
                quotes_authorities=data.get("cytaty", []),
                transformation=data.get("transformacja", {}),
                observer_perspective=data.get("perspektywa_obserwatora", {}),
                analogies=data.get("analogie", []),
                depth_suggestions=data.get("propozycje_poglebiania", []),
            )

        except json.JSONDecodeError as e:
            logger.error(f"ContextShifter: JSON parse error: {e}")
            logger.error(f"ContextShifter: Raw response (first 500 chars): {response[:500]}")
            return DepthReport(
                verdict="BŁĄD",
                depth_level=0,
                has_second_layer=False,
                current_layer={},
                rituals_absurds=[],
                cognitive_biases=[],
                quotes_authorities=[],
                transformation={},
                observer_perspective={},
                analogies=[],
                depth_suggestions=[],
            )
        except Exception as e:
            logger.error(f"ContextShifter: Unexpected error: {e}")
            return DepthReport(
                verdict="BŁĄD",
                depth_level=0,
                has_second_layer=False,
                current_layer={},
                rituals_absurds=[],
                cognitive_biases=[],
                quotes_authorities=[],
                transformation={},
                observer_perspective={},
                analogies=[],
                depth_suggestions=[],
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
            on_progress("Szukam głębi i drugiego dna...")

        report = self.shift(content, context)
        result_content = json.dumps(report.to_dict(), ensure_ascii=False, indent=2)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=result_content,
            score=float(report.depth_level),
        )
