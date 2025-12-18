"""Adwokat Diabła - challenges assumptions and prevents cringe."""

import json
import re
import logging
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient

logger = logging.getLogger(__name__)


@dataclass
class CritiqueReport:
    """Raport krytycznej analizy."""
    argument_strength: int  # 1-10
    red_flags: list  # czerwone flagi
    claim_verification: list  # weryfikacja twierdzeń
    counterarguments: list  # kontrargumenty (tryb źródło)
    unaddressed_objections: list  # nieadresowane obiekcje
    uncomfortable_questions: list  # niewygodne pytania
    cringe_assessment: dict  # ocena cringe
    missing_perspectives: list  # brakujące perspektywy
    alternative_interpretations: list  # alternatywne interpretacje (tryb źródło)
    strengthening_suggestions: list  # sugestie wzmocnienia
    verdict: str  # OK / WYMAGA_POPRAWEK / NIE_PUBLIKUJ

    def to_dict(self) -> dict:
        return {
            "sila_argumentu": self.argument_strength,
            "czerwone_flagi": self.red_flags,
            "weryfikacja_twierdzen": self.claim_verification,
            "kontrargumenty": self.counterarguments,
            "nieadresowane_obiekcje": self.unaddressed_objections,
            "niewygodne_pytania": self.uncomfortable_questions,
            "ocena_cringe": self.cringe_assessment,
            "brakujace_perspektywy": self.missing_perspectives,
            "alternatywne_interpretacje": self.alternative_interpretations,
            "sugestie_wzmocnienia": self.strengthening_suggestions,
            "werdykt": self.verdict,
        }


class DevilsAdvocateAgent(BaseAgent):
    """Agent that provides critical review and cringe detection."""

    name = "devils_advocate"
    name_pl = "Adwokat Diabła"
    description = "Kwestionuje założenia, znajduje słabe argumenty, zapobiega cringe'owi"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# ADWOKAT DIABŁA

Jesteś bezlitosnym krytykiem. Szukasz tego, co MOŻNA powiedzieć przeciwko - nie żeby zniszczyć, ale żeby wzmocnić.

## DWA TRYBY PRACY

### TRYB ŹRÓDŁO (eksploracja badania/artykułu)
Gdy analizujesz materiał źródłowy, szukasz:
- **Kontrargumentów** - co powie sceptyk?
- **Alternatywnych interpretacji** - co jeśli dane znaczą coś innego?
- **Brakujących perspektyw** - kto nie został wysłuchany?
- **Niewygodnych pytań** - czego autor nie adresuje?

### TRYB POST (recenzja gotowego tekstu)
Gdy recenzujesz gotowy post, szukasz:
- **Luk logicznych** - czy argument się trzyma?
- **Przesad** - "zawsze", "nigdy", "najlepszy"
- **Cringe** - humble-brag, virtue signaling

## ZASADY ZWIĘZŁOŚCI
- Max 3 czerwone flagi
- Max 3 kontrargumenty
- Max 3 obiekcje
- Max 3 pytania
- Max 2 alternatywne interpretacje

## FORMAT ODPOWIEDZI

```json
{
  "sila_argumentu": 6,
  "czerwone_flagi": [
    {"problem": "Dane z jednego badania przedstawione jako pewnik", "jak_naprawic": "Zaznacz że to wstępne wyniki"}
  ],
  "weryfikacja_twierdzen": [
    {"twierdzenie": "AI zwiększa produktywność o 40%", "dowod": "jedno badanie, mała próba", "jak_naprawic": "Podaj kontekst ograniczeń"}
  ],
  "kontrargumenty": [
    {"argument": "AI zwiększa produktywność", "kontra": "Ale kosztem kreatywności?", "sila_kontry": 7},
    {"argument": "Badanie potwierdza skuteczność", "kontra": "W laboratorium - a w życiu?", "sila_kontry": 8}
  ],
  "nieadresowane_obiekcje": [
    {"obiekcja": "To działa tylko w kontrolowanych warunkach", "jak_zaadresowac": "Przyznaj ograniczenie wprost"}
  ],
  "niewygodne_pytania": [
    "A co z tymi, którym nie pomogło?",
    "Kto finansował badanie?",
    "Czy wyniki są replikowalne?"
  ],
  "ocena_cringe": {
    "humble_brag": 2,
    "virtue_signaling": 1,
    "ryzyko_screenshota": "niskie",
    "komentarz": "Treść rzeczowa"
  },
  "brakujace_perspektywy": [
    {"kto": "Sceptycy technologii", "ich_argument": "To kolejny hype jak blockchain", "jak_zaadresowac": "Przyznaj że czas pokaże"},
    {"kto": "Osoby zagrożone automatyzacją", "ich_argument": "Łatwo entuzjazmować się z bezpiecznej pozycji", "jak_zaadresowac": "Okaż empatię"}
  ],
  "alternatywne_interpretacje": [
    {"dane": "Produktywność wzrosła o 40%", "alternatywa": "Może mierzyli tylko szybkość, nie jakość końcową?"},
    {"dane": "Użytkownicy są zadowoleni", "alternatywa": "Bo nie mają porównania? Bo to nowość?"}
  ],
  "sugestie_wzmocnienia": [
    "Zaadresuj wprost główny kontrargument przed krytykami",
    "Przyznaj jedno ograniczenie - to buduje wiarygodność"
  ],
  "werdykt": "WYMAGA_POPRAWEK"
}
```

## LOGIKA WERDYKTU
- **OK**: Argumenty solidne, główne obiekcje można zaadresować
- **WYMAGA_POPRAWEK**: Dobre jądro, ale są luki do załatania
- **NIE_PUBLIKUJ**: Łatwe do obalenia, może się odwrócić

## ZŁOTE ZASADY
- Myśl jak inteligentny sceptyk, nie hater
- Każda krytyka = konstruktywna sugestia
- Kontrargument to prezent - pozwala wzmocnić tekst
- Znajdź 3 rzeczy które przeciwnik MOŻE powiedzieć
"""

    def critique(self, content: str, context: Optional[dict] = None) -> CritiqueReport:
        """
        Przeprowadza krytyczną analizę treści.

        Args:
            content: Treść do analizy
            context: Dodatkowy kontekst

        Returns:
            CritiqueReport z krytyczną oceną
        """
        input_text = f"## TREŚĆ DO KRYTYCZNEJ ANALIZY\n\n{content}"

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

    def _parse_response(self, response: str) -> CritiqueReport:
        """Parsuje odpowiedź JSON do CritiqueReport."""
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
                    logger.warning("DevilsAdvocate: Używam fallback parsowania")
                else:
                    json_str = response

            json_str = json_str.strip()
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("DevilsAdvocate: Próba naprawy uciętego JSON...")
                repaired = self._repair_truncated_json(json_str)
                data = json.loads(repaired)

            return CritiqueReport(
                argument_strength=data.get("sila_argumentu", 5),
                red_flags=data.get("czerwone_flagi", []),
                claim_verification=data.get("weryfikacja_twierdzen", []),
                counterarguments=data.get("kontrargumenty", []),
                unaddressed_objections=data.get("nieadresowane_obiekcje", []),
                uncomfortable_questions=data.get("niewygodne_pytania", []),
                cringe_assessment=data.get("ocena_cringe", {}),
                missing_perspectives=data.get("brakujace_perspektywy", []),
                alternative_interpretations=data.get("alternatywne_interpretacje", []),
                strengthening_suggestions=data.get("sugestie_wzmocnienia", []),
                verdict=data.get("werdykt", "WYMAGA_POPRAWEK"),
            )

        except json.JSONDecodeError as e:
            logger.error(f"DevilsAdvocate: JSON parse error: {e}")
            logger.error(f"DevilsAdvocate: Raw response (first 500 chars): {response[:500]}")
            return CritiqueReport(
                argument_strength=0,
                red_flags=[],
                claim_verification=[],
                counterarguments=[],
                unaddressed_objections=[],
                uncomfortable_questions=[],
                cringe_assessment={},
                missing_perspectives=[],
                alternative_interpretations=[],
                strengthening_suggestions=[],
                verdict="BŁĄD",
            )
        except Exception as e:
            logger.error(f"DevilsAdvocate: Unexpected error: {e}")
            return CritiqueReport(
                argument_strength=0,
                red_flags=[],
                claim_verification=[],
                counterarguments=[],
                unaddressed_objections=[],
                uncomfortable_questions=[],
                cringe_assessment={},
                missing_perspectives=[],
                alternative_interpretations=[],
                strengthening_suggestions=[],
                verdict="BŁĄD",
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
            on_progress("Przeprowadzam krytyczną analizę...")

        report = self.critique(content, context)
        result_content = json.dumps(report.to_dict(), ensure_ascii=False, indent=2)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=result_content,
            score=float(report.argument_strength),
        )
