"""Architekt Napięcia - creates surprise and paradox throughout the post."""

import json
import re
import logging
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient

logger = logging.getLogger(__name__)


@dataclass
class TensionReport:
    """Raport z analizy napięcia."""
    verdict: str  # PŁASKIE / PRZEWIDYWALNE / NAPIĘCIE
    surprise_level: int  # 1-10
    paradox_level: int  # 1-10
    total_tension: int  # 1-10
    structure_diagnosis: dict  # diagnoza struktury
    cliches: list  # wykryte klisze
    available_paradoxes: list  # paradoksy do wykorzystania
    contrast_structures: list  # struktury kontrastu
    transformed_version: dict  # transformacja przed/po
    paradox_endings: list  # puenty z paradoksem

    def to_dict(self) -> dict:
        return {
            "werdykt": self.verdict,
            "poziom_zaskoczenia": self.surprise_level,
            "poziom_paradoksu": self.paradox_level,
            "napiecie_lacznie": self.total_tension,
            "diagnoza_struktury": self.structure_diagnosis,
            "klisze": self.cliches,
            "dostepne_paradoksy": self.available_paradoxes,
            "struktury_kontrastu": self.contrast_structures,
            "transformacja": self.transformed_version,
            "puenty_paradoks": self.paradox_endings,
        }


class TensionArchitectAgent(BaseAgent):
    """Agent that builds tension through surprise elements and logical paradoxes."""

    name = "tension_architect"
    name_pl = "Architekt Napięcia"
    description = "Łamie przewidywalność i buduje napięcie. Zaskoczenie na początku, paradoks w puentcie."

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# ARCHITEKT NAPIĘCIA

Budujesz napięcie przez zaskoczenie i paradoks. Liniowa narracja = SCROLL. Paradoks = ZATRZYMANIE.

## DWA WYMIARY

### 1. ZASKOCZENIE (łamanie przewidywalności)
- Czy można zgadnąć zakończenie?
- Gdzie złamać flow?

### 2. PARADOKS (napięcie logiczne)
- Im więcej X, tym mniej X
- Rozwiązanie tworzy problem
- Sukces = porażka

## ZASADY ZWIĘZŁOŚCI
- Max 3 klisze
- Max 3 paradoksy
- Max 3 puenty
- Transformacja = max 100 słów

## FORMAT ODPOWIEDZI

```json
{
  "werdykt": "PRZEWIDYWALNE",
  "poziom_zaskoczenia": 4,
  "poziom_paradoksu": 3,
  "napiecie_lacznie": 4,
  "diagnoza_struktury": {
    "typ": "liniowa",
    "przewidywalnosc": "wysoka",
    "wstep": "AI pomoże zaoszczędzić czas",
    "zakonczenie": "więc warto używać AI"
  },
  "klisze": [
    {"element": "5 porad na...", "jak_zlamac": "Zacznij od porażki zamiast porad"}
  ],
  "dostepne_paradoksy": [
    {
      "nazwa": "Oszczędność kosztuje",
      "formula": "Im więcej oszczędzamy, tym więcej wydajemy",
      "zdanie": "AI pisze maile szybciej, więc piszemy ich więcej, więc mamy mniej czasu."
    }
  ],
  "struktury_kontrastu": [
    {
      "typ": "Oczekiwanie vs Rzeczywistość",
      "propozycja": "Myślałem że AI zaoszczędzi czas. Teraz odpowiadam na 3x więcej maili."
    }
  ],
  "transformacja": {
    "przed": "AI pomoże nam pisać lepsze maile i zaoszczędzimy czas.",
    "po": "AI pisze maile szybciej. Więc piszemy ich więcej. Więc mamy mniej czasu. Oszczędność to pułapka.",
    "co_zmienione": "Dodano paradoks odwrócenia celu"
  },
  "puenty_paradoks": [
    {"puenta": "Efektywność bez celu to chaos z KPI.", "typ": "odwrócenie"},
    {"puenta": "Wolność to nowa klatka.", "typ": "samozaprzeczenie"}
  ]
}
```

## LOGIKA OCENY

🔴 PŁASKIE: Problem → Rozwiązanie, wstęp = zakończenie
🟡 PRZEWIDYWALNE: Jest napięcie ale słabe, brak paradoksu
🟢 NAPIĘCIE: Puenta odwraca tezę, mindfuck, nie da się przewidzieć

## ZŁOTE ZASADY
- Jeśli wniosek oczywisty z wstępu = PRZEPISZ
- Każde "więc" prowadzi do zaskoczenia
- Rozwiązanie MUSI mieć ukryty koszt
- Czytelnik wychodzi z pytaniem, nie odpowiedzią
"""

    def architect(self, content: str, context: Optional[dict] = None) -> TensionReport:
        """
        Analizuje napięcie w treści.

        Args:
            content: Treść do analizy
            context: Dodatkowy kontekst

        Returns:
            TensionReport z analizą napięcia
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

    def _parse_response(self, response: str) -> TensionReport:
        """Parsuje odpowiedź JSON do TensionReport."""
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
                    logger.warning("TensionArchitect: Używam fallback parsowania")
                else:
                    json_str = response

            json_str = json_str.strip()
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("TensionArchitect: Próba naprawy uciętego JSON...")
                repaired = self._repair_truncated_json(json_str)
                data = json.loads(repaired)

            return TensionReport(
                verdict=data.get("werdykt", "PRZEWIDYWALNE"),
                surprise_level=data.get("poziom_zaskoczenia", 5),
                paradox_level=data.get("poziom_paradoksu", 5),
                total_tension=data.get("napiecie_lacznie", 5),
                structure_diagnosis=data.get("diagnoza_struktury", {}),
                cliches=data.get("klisze", []),
                available_paradoxes=data.get("dostepne_paradoksy", []),
                contrast_structures=data.get("struktury_kontrastu", []),
                transformed_version=data.get("transformacja", {}),
                paradox_endings=data.get("puenty_paradoks", []),
            )

        except json.JSONDecodeError as e:
            logger.error(f"TensionArchitect: JSON parse error: {e}")
            logger.error(f"TensionArchitect: Raw response (first 500 chars): {response[:500]}")
            return TensionReport(
                verdict="BŁĄD",
                surprise_level=0,
                paradox_level=0,
                total_tension=0,
                structure_diagnosis={},
                cliches=[],
                available_paradoxes=[],
                contrast_structures=[],
                transformed_version={},
                paradox_endings=[],
            )
        except Exception as e:
            logger.error(f"TensionArchitect: Unexpected error: {e}")
            return TensionReport(
                verdict="BŁĄD",
                surprise_level=0,
                paradox_level=0,
                total_tension=0,
                structure_diagnosis={},
                cliches=[],
                available_paradoxes=[],
                contrast_structures=[],
                transformed_version={},
                paradox_endings=[],
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
            on_progress("Analizuję napięcie i paradoksy...")

        report = self.architect(content, context)
        result_content = json.dumps(report.to_dict(), ensure_ascii=False, indent=2)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=result_content,
            score=float(report.total_tension),
        )
