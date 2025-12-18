"""Agent: Brief Synthesizer - tworzy zwięzły brief z outputów wszystkich agentów."""

import json
import re
import logging
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient

logger = logging.getLogger(__name__)


@dataclass
class BriefReport:
    """Zwięzły brief z najlepszymi elementami od wszystkich agentów."""
    najlepsze_hooki: List[str] = field(default_factory=list)
    kluczowe_insighty: List[str] = field(default_factory=list)
    gotowe_do_uzycia: List[Dict[str, str]] = field(default_factory=list)
    ostrzezenia: List[str] = field(default_factory=list)
    polskie_konteksty: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "najlepsze_hooki": self.najlepsze_hooki,
            "kluczowe_insighty": self.kluczowe_insighty,
            "gotowe_do_uzycia": self.gotowe_do_uzycia,
            "ostrzezenia": self.ostrzezenia,
            "polskie_konteksty": self.polskie_konteksty,
        }


class BriefSynthesizerAgent(BaseAgent):
    """
    Agent: Brief Synthesizer.

    Tworzy zwięzły brief z outputów wszystkich agentów.
    Używa dwufazowej architektury dla oszczędności tokenów:
    1. Faza ekstrakcji (tani model) - wyciąga top elementy z każdego agenta
    2. Faza syntezy (główny model) - tworzy końcowy brief

    Output to gotowe do użycia elementy, nie oceny liczbowe.
    """

    name = "brief_synthesizer"
    name_pl = "Syntetyzator Briefu"
    description = "Tworzy zwięzły brief z najlepszymi elementami od wszystkich agentów"

    # Model do ekstrakcji (tani, szybki)
    EXTRACTION_MODEL = "gemini-3-flash"
    # Model do syntezy (główny)
    SYNTHESIS_MODEL = "claude-sonnet-4-20250514"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-sonnet-4-20250514"):
        super().__init__(client, model_key)
        self.synthesis_model = model_key

    def _get_default_prompt(self) -> str:
        return """# SYNTETYZATOR BRIEFU

Jesteś ekspertem od wyciągania esencji z analiz wielu agentów.

## TWOJE ZADANIE

Otrzymujesz skompresowane outputy od wielu agentów analitycznych.
Tworzysz JEDEN BRIEF z najlepszymi elementami do natychmiastowego użycia.

## ZASADY

1. NIE OCENIAJ liczbowo (żadnych 7/10, "dobry", "średni")
2. POKAZUJ przykłady - dobre hooki, gotowe frazy, konkretne propozycje
3. WYBIERAJ najlepsze - max 3 hooki, max 3 insighty, max 3 ostrzeżenia
4. BĄDŹ ZWIĘZŁY - brief ma być szybki do przeskanowania

## FORMAT ODPOWIEDZI

```json
{
  "najlepsze_hooki": [
    "Hook 1 - dosłowny cytat lub propozycja gotowa do użycia",
    "Hook 2...",
    "Hook 3..."
  ],
  "kluczowe_insighty": [
    "Insight 1 - co warto wiedzieć pisząc post",
    "Insight 2...",
    "Insight 3..."
  ],
  "gotowe_do_uzycia": [
    {
      "typ": "przeliczenie/analogia/cytat/fraza",
      "tekst": "Gotowy element do wklejenia w post"
    }
  ],
  "ostrzezenia": [
    "Czego unikać - konkretna fraza lub podejście"
  ],
  "polskie_konteksty": [
    "Polski temat/debata do połączenia"
  ]
}
```
"""

    def _get_extraction_prompt(self) -> str:
        """Prompt dla fazy ekstrakcji (tani model)."""
        return """Wyciągnij TOP elementy z tego outputu agenta.

ZASADY:
- Max 3 najlepsze elementy
- Zachowaj dosłowne cytaty/propozycje gdzie możliwe
- Nie dodawaj własnych interpretacji
- Jeśli output jest pusty lub błędny, zwróć puste listy

FORMAT:
```json
{
  "agent": "nazwa agenta",
  "top_hooki": ["hook1", "hook2"],
  "top_insighty": ["insight1"],
  "top_propozycje": ["propozycja1"],
  "ostrzezenia": ["ostrzezenie1"],
  "polskie": ["polski element1"]
}
```
"""

    def _extract_from_agent(self, agent_name: str, agent_output: str) -> Dict[str, Any]:
        """Faza 1: Ekstrakcja top elementów z jednego agenta (tani model)."""

        # Skróć output jeśli za długi (max ~2000 znaków)
        if len(agent_output) > 2500:
            agent_output = agent_output[:2500] + "\n... [ucięte]"

        messages = [
            {"role": "system", "content": self._get_extraction_prompt()},
            {"role": "user", "content": f"AGENT: {agent_name}\n\nOUTPUT:\n{agent_output}"},
        ]

        try:
            response = self.client.chat(
                messages=messages,
                model_key=self.EXTRACTION_MODEL,
                temperature=0.3,
                max_tokens=800,
            )

            # Parse JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                # Spróbuj parsować bezpośrednio
                return json.loads(response.content)

        except Exception as e:
            logger.warning(f"Extraction failed for {agent_name}: {e}")
            return {
                "agent": agent_name,
                "top_hooki": [],
                "top_insighty": [],
                "top_propozycje": [],
                "ostrzezenia": [],
                "polskie": [],
            }

    def _synthesize_brief(self, extractions: List[Dict[str, Any]]) -> BriefReport:
        """Faza 2: Synteza końcowego briefu (główny model)."""

        # Przygotuj skompresowany input
        compressed_input = "## WYCIĄGI Z AGENTÓW\n\n"
        for ext in extractions:
            if not ext:
                continue
            compressed_input += f"### {ext.get('agent', 'Unknown')}\n"
            if ext.get('top_hooki'):
                compressed_input += f"Hooki: {json.dumps(ext['top_hooki'], ensure_ascii=False)}\n"
            if ext.get('top_insighty'):
                compressed_input += f"Insighty: {json.dumps(ext['top_insighty'], ensure_ascii=False)}\n"
            if ext.get('top_propozycje'):
                compressed_input += f"Propozycje: {json.dumps(ext['top_propozycje'], ensure_ascii=False)}\n"
            if ext.get('ostrzezenia'):
                compressed_input += f"Ostrzeżenia: {json.dumps(ext['ostrzezenia'], ensure_ascii=False)}\n"
            if ext.get('polskie'):
                compressed_input += f"Polski kontekst: {json.dumps(ext['polskie'], ensure_ascii=False)}\n"
            compressed_input += "\n"

        messages = [
            {"role": "system", "content": self.prompt_template},
            {"role": "user", "content": compressed_input + "\n\nStwórz BRIEF z najlepszymi elementami."},
        ]

        response = self.client.chat(
            messages=messages,
            model_key=self.synthesis_model,
            temperature=0.5,
            max_tokens=1500,
        )

        return self._parse_response(response.content)

    def _parse_response(self, response: str) -> BriefReport:
        """Parsuje odpowiedź JSON do BriefReport."""
        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response

            data = json.loads(json_str.strip())

            return BriefReport(
                najlepsze_hooki=data.get("najlepsze_hooki", []),
                kluczowe_insighty=data.get("kluczowe_insighty", []),
                gotowe_do_uzycia=data.get("gotowe_do_uzycia", []),
                ostrzezenia=data.get("ostrzezenia", []),
                polskie_konteksty=data.get("polskie_konteksty", []),
            )

        except Exception as e:
            logger.error(f"BriefSynthesizer parse error: {e}")
            return BriefReport()

    def synthesize(
        self,
        agent_outputs: Dict[str, str],
        on_progress=None,
    ) -> BriefReport:
        """
        Główna metoda - tworzy brief z outputów agentów.

        Args:
            agent_outputs: Dict {agent_name: output_string}
            on_progress: Callback dla statusu

        Returns:
            BriefReport z najlepszymi elementami
        """
        if on_progress:
            on_progress("Ekstrakcja kluczowych elementów...")

        # Faza 1: Ekstrakcja (równolegle można by, ale sekwencyjnie dla prostoty)
        extractions = []
        for agent_name, output in agent_outputs.items():
            if on_progress:
                on_progress(f"Analizuję: {agent_name}...")
            extraction = self._extract_from_agent(agent_name, output)
            extractions.append(extraction)

        if on_progress:
            on_progress("Synteza briefu...")

        # Faza 2: Synteza
        brief = self._synthesize_brief(extractions)

        return brief

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
            on_progress("Tworzę brief...")

        # Oczekujemy agent_outputs w context
        agent_outputs = context.get("agent_outputs", {}) if context else {}

        if not agent_outputs:
            return AgentResult(
                agent_name=self.name,
                agent_name_pl=self.name_pl,
                content=json.dumps({"error": "Brak outputów agentów do syntezy"}, ensure_ascii=False),
            )

        brief = self.synthesize(agent_outputs, on_progress)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=json.dumps(brief.to_dict(), ensure_ascii=False, indent=2),
        )
