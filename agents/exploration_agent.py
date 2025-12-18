"""Agent Eksploracji - generuje raport z kątami i perspektywami dla materiału źródłowego."""

import json
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient


@dataclass
class ExplorationReport:
    """Raport eksploracyjny - perspektywy i kąty na temat."""
    possible_angles: list  # 5-7 możliwych kątów
    tension_points: list  # punkty napięcia / kontrowersje
    polish_context: list  # polski kontekst, do czego podpiąć
    questions_worth_asking: list  # pytania warte zadania
    traps_to_avoid: list  # pułapki, banały do uniknięcia
    recommended_angle: dict  # rekomendowany kąt z uzasadnieniem

    def to_dict(self) -> dict:
        return {
            "możliwe_kąty": self.possible_angles,
            "punkty_napięcia": self.tension_points,
            "polski_kontekst": self.polish_context,
            "pytania_warte_zadania": self.questions_worth_asking,
            "pułapki_do_uniknięcia": self.traps_to_avoid,
            "rekomendowany_kąt": self.recommended_angle,
        }


class ExplorationAgent(BaseAgent):
    """
    Agent Eksploracji.

    Dla scenariusza: "Mam materiał, nie mam pomysłu"

    Generuje raport z:
    - 5-7 możliwymi kątami/perspektywami
    - Punktami napięcia
    - Polskim kontekstem
    - Pytaniami wartymi zadania
    - Pułapkami do uniknięcia
    """

    name = "exploration_agent"
    name_pl = "Agent Eksploracji"
    description = "Generuje raport eksploracyjny z kątami i perspektywami"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# AGENT EKSPLORACJI

Jesteś wirtualnym kolegium redakcyjnym. Użytkownik ma materiał źródłowy (artykuł, badanie, raport), ale NIE MA jeszcze pomysłu na post. Twoim zadaniem jest dostarczyć mu perspektywy, kąty, pytania - materiał do przemyślenia.

## TWOJA ROLA

NIE piszesz posta. Dajesz użytkownikowi:
- Różne kąty spojrzenia na temat
- Punkty zapalne / kontrowersje
- Polski kontekst (do czego podpiąć)
- Pytania, które warto zadać
- Pułapki do uniknięcia (banały, oczywistości)

## CO GENERUJESZ

### 1. MOŻLIWE KĄTY (5-7 propozycji)

Każdy kąt to inny sposób opowiedzenia tej samej historii:

- **Kąt personalny**: "Jak to dotyczy CIEBIE osobiście"
- **Kąt kontrowersyjny**: "Co tu jest sporne / dzieli ludzi"
- **Kąt paradoksu**: "Co tu jest sprzeczne / nielogiczne"
- **Kąt praktyczny**: "Co z tym zrobić / jak wykorzystać"
- **Kąt emocjonalny**: "Co tu straszy / cieszy / złości"
- **Kąt kontrariański**: "Dlaczego większość się myli"
- **Kąt przyszłości**: "Co to zmieni za X lat"

Dla każdego kąta podaj:
- Krótki opis (1-2 zdania)
- Przykładowy hook
- Dla kogo ten kąt zadziała najlepiej

### 2. PUNKTY NAPIĘCIA

Co w tym temacie:
- Dzieli ludzi na obozy?
- Jest kontrowersyjne?
- Budzi emocje?
- Jest niedopowiedziane?

### 3. POLSKI KONTEKST

- Do jakiego polskiego wydarzenia/tematu można podpiąć?
- Jakie polskie firmy/osoby/zjawiska to dotyczy?
- Co jest specyficzne dla polskiego rynku/społeczeństwa?

### 4. PYTANIA WARTE ZADANIA

Prowokacyjne, otwierające dyskusję pytania, które autor może zadać czytelnikom lub sobie.

### 5. PUŁAPKI DO UNIKNIĘCIA

- Co wszyscy już o tym powiedzieli (banały)
- Jakie są oczywiste, nudne kąty
- Czego NIE robić

## FORMAT ODPOWIEDZI

```json
{
  "możliwe_kąty": [
    {
      "nazwa": "Kąt personalny",
      "opis": "Jak AI w rekrutacji dotyczy CIEBIE - czy Twoje CV przejdzie przez ATS?",
      "hook": "Wysłałeś 50 CV i zero odpowiedzi? To nie Ty. To algorytm.",
      "dla_kogo": "Osoby szukające pracy, zmieniające branżę",
      "siła": 8
    },
    {
      "nazwa": "Kąt paradoksu",
      "opis": "HR-owcy boją się AI, ale sami używają ATS który odrzuca 75% ludzi",
      "hook": "HR-owcy boją się że AI zabierze im pracę. Tymczasem ich własne narzędzia odrzucają lepszych kandydatów niż oni.",
      "dla_kogo": "HR, rekruterzy, menedżerowie",
      "siła": 9
    }
  ],
  "punkty_napięcia": [
    {
      "napięcie": "Technologia vs człowiek w rekrutacji",
      "strona_A": "ATS oszczędza czas i jest obiektywny",
      "strona_B": "ATS odrzuca świetnych kandydatów przez brak słów kluczowych",
      "potencjał_dyskusji": "wysoki"
    }
  ],
  "polski_kontekst": [
    {
      "kontekst": "Fala zwolnień w IT w Polsce 2024",
      "jak_podpiąć": "Ludzie szukają pracy, wysyłają setki CV, frustracja rośnie"
    },
    {
      "kontekst": "Polski rynek pracy vs zachodni",
      "jak_podpiąć": "Czy polskie firmy używają ATS tak samo? Różnice?"
    }
  ],
  "pytania_warte_zadania": [
    "Kiedy ostatnio rekruter naprawdę PRZECZYTAŁ Twoje CV?",
    "Czy Twoje CV jest pisane dla człowieka czy dla robota?",
    "Ile świetnych pracowników straciła Twoja firma przez ATS?"
  ],
  "pułapki_do_uniknięcia": [
    {
      "pułapka": "Zaczynanie od 'Nowe badanie pokazuje...'",
      "dlaczego_zła": "Nudne, nikogo nie obchodzi badanie - obchodzi go wpływ na niego"
    },
    {
      "pułapka": "Ogólne narzekanie na AI w rekrutacji",
      "dlaczego_zła": "Wszyscy to robią, zero wartości"
    },
    {
      "pułapka": "Lista tipów jak przejść przez ATS",
      "dlaczego_zła": "Takich artykułów są tysiące, generyczne"
    }
  ],
  "rekomendowany_kąt": {
    "nazwa": "Kąt paradoksu",
    "uzasadnienie": "Najwyższy potencjał viralowy - HR-owcy boją się AI ale sami są częścią problemu. Prowokuje, ale nie obraża. Otwiera dyskusję.",
    "hook": "HR-owcy boją się że AI zabierze im pracę. Tymczasem ich własne narzędzia odrzucają lepszych kandydatów niż oni."
  }
}
```

## ZASADY

1. **Bądź konkretny** - nie "może warto napisać o wpływie na pracę", ale "Kąt: Twoje CV nie trafia do człowieka. Hook: 50 CV, zero odpowiedzi."

2. **Myśl jak redaktor** - szukasz kąta który:
   - Zatrzyma scroll
   - Wzbudzi emocje
   - Otworzy dyskusję
   - Będzie świeży (nie banał)

3. **Priorytetyzuj** - podaj siłę każdego kąta (1-10), zarekomenduj najlepszy

4. **Polski kontekst** - zawsze szukaj zaczepienia w polskiej rzeczywistości

5. **Nie pisz posta** - dajesz perspektywy, nie gotowy tekst
"""

    def explore(
        self,
        extracted_data: dict,
        resonance_report: dict,
        depth_report: dict,
        polish_context_report: dict = None,
        popculture_report: dict = None,
    ) -> ExplorationReport:
        """
        Generuje raport eksploracyjny.

        Args:
            extracted_data: Dane z ExtractorAgent
            resonance_report: Raport z ResonanceHunterAgent
            depth_report: Raport z AnthropologistAgent
            polish_context_report: Raport z PolishContextualizerAgent (opcjonalny)
            popculture_report: Raport z PopcultureCuratorAgent (opcjonalny)

        Returns:
            ExplorationReport z kątami i perspektywami
        """
        # Buduj input text z dostępnych raportów
        sections = [
            f"## DANE ŹRÓDŁOWE\n\n{json.dumps(extracted_data, ensure_ascii=False, indent=2)}",
            f"## RAPORT REZONANSU (punkty zaczepienia)\n\n{json.dumps(resonance_report, ensure_ascii=False, indent=2)}",
            f"## RAPORT ANTROPOLOGICZNY (etnografia, socjologia, psychologia)\n\n{json.dumps(depth_report, ensure_ascii=False, indent=2)}",
        ]

        if polish_context_report:
            sections.append(f"## POLSKI KONTEKST (przeliczenia, tematy PL, eksperci)\n\n{json.dumps(polish_context_report, ensure_ascii=False, indent=2)}")

        if popculture_report:
            sections.append(f"## ANALOGIE POPKULTUROWE (filmy, sport, codzienność)\n\n{json.dumps(popculture_report, ensure_ascii=False, indent=2)}")

        sections.append("---\n\nNa podstawie powyższych danych wygeneruj raport eksploracyjny.\nPamiętaj: użytkownik NIE MA jeszcze pomysłu - daj mu perspektywy do przemyślenia.")

        input_text = "\n\n".join(sections)

        messages = [
            {"role": "system", "content": self.prompt_template},
            {"role": "user", "content": input_text},
        ]

        response = self.client.chat(
            messages=messages,
            model_key=self.model_key,
            temperature=0.8,  # Wyższa dla kreatywności
            max_tokens=4000,
        )

        return self._parse_response(response.content)

    def _parse_response(self, response: str) -> ExplorationReport:
        """Parsuje odpowiedź do ExplorationReport."""
        import re

        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response

            data = json.loads(json_str)

            return ExplorationReport(
                possible_angles=data.get("możliwe_kąty", []),
                tension_points=data.get("punkty_napięcia", []),
                polish_context=data.get("polski_kontekst", []),
                questions_worth_asking=data.get("pytania_warte_zadania", []),
                traps_to_avoid=data.get("pułapki_do_uniknięcia", []),
                recommended_angle=data.get("rekomendowany_kąt", {}),
            )

        except (json.JSONDecodeError, KeyError):
            return ExplorationReport(
                possible_angles=[],
                tension_points=[],
                polish_context=[],
                questions_worth_asking=[],
                traps_to_avoid=[],
                recommended_angle={},
            )

    def analyze(
        self,
        content: str,
        mode: str = "exploration",
        platform=None,
        humor_dial: Optional[int] = None,
        context: Optional[dict] = None,
        on_progress=None,
    ) -> AgentResult:
        """Implementacja interfejsu BaseAgent."""
        if on_progress:
            on_progress("Eksploruję możliwe kąty i perspektywy...")

        extracted_data = context.get("extracted_data", {}) if context else {}
        resonance_report = context.get("resonance_report", {}) if context else {}
        depth_report = context.get("depth_report", {}) if context else {}

        if not extracted_data:
            extracted_data = {"raw_content": content}

        report = self.explore(extracted_data, resonance_report, depth_report)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        )
