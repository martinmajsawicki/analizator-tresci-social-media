"""Agent Rozwinięcia - rozwija wstępny kierunek użytkownika w warianty i propozycje."""

import json
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient


@dataclass
class DevelopmentReport:
    """Raport rozwinięcia - warianty i propozycje dla kierunku użytkownika."""
    user_direction_assessment: dict  # ocena kierunku usera
    development_variants: list  # 3 warianty rozwinięcia
    hook_proposals: list  # propozycje hooków
    what_to_strengthen: list  # co wzmocnić
    what_to_skip: list  # co pominąć
    counterarguments: list  # kontrargumenty do rozważenia
    recommended_variant: dict  # rekomendowany wariant

    def to_dict(self) -> dict:
        return {
            "ocena_kierunku": self.user_direction_assessment,
            "warianty_rozwinięcia": self.development_variants,
            "propozycje_hooków": self.hook_proposals,
            "co_wzmocnić": self.what_to_strengthen,
            "co_pominąć": self.what_to_skip,
            "kontrargumenty": self.counterarguments,
            "rekomendowany_wariant": self.recommended_variant,
        }


class DevelopmentAgent(BaseAgent):
    """
    Agent Rozwinięcia.

    Dla scenariusza: "Mam materiał + wstępny kierunek"

    Generuje raport z:
    - Oceną kierunku użytkownika
    - 3 wariantami rozwinięcia
    - Propozycjami hooków
    - Co wzmocnić / co pominąć
    - Kontrargumentami do rozważenia
    """

    name = "development_agent"
    name_pl = "Agent Rozwinięcia"
    description = "Rozwija wstępny kierunek użytkownika w warianty i propozycje"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# AGENT ROZWINIĘCIA

Jesteś wirtualnym kolegium redakcyjnym. Użytkownik ma materiał źródłowy ORAZ wstępny kierunek/pomysł. Twoim zadaniem jest rozwinąć ten kierunek, zaproponować warianty, wzmocnić mocne strony.

## TWOJA ROLA

Użytkownik ma już iskrę - wstępny pomysł. Ty:
- Oceniasz ten kierunek (czy dobry? co można ulepszyć?)
- Proponujesz 3 warianty rozwinięcia
- Dajesz propozycje hooków
- Mówisz co wzmocnić, co pominąć
- Podajesz kontrargumenty do rozważenia

## CO GENERUJESZ

### 1. OCENA KIERUNKU UŻYTKOWNIKA

Użytkownik podał wstępny kierunek. Oceń:
- Czy to dobry kąt? (skala 1-10)
- Co w nim działa?
- Co można ulepszyć?
- Jakie ryzyko niesie?

### 2. WARIANTY ROZWINIĘCIA (3 propozycje)

Trzy różne sposoby rozwinięcia tego samego kierunku:

- **Wariant BEZPIECZNY**: Solidny, sprawdzony, niskie ryzyko
- **Wariant ODWAŻNY**: Bardziej kontrowersyjny, wyższe ryzyko, wyższy potencjał
- **Wariant PERSONALNY**: Mocno oparty na osobistym doświadczeniu/opinii

Dla każdego wariantu:
- Opis podejścia
- Główna teza
- Przykładowy hook
- Ryzyko i potencjał

### 3. PROPOZYCJE HOOKÓW (5-7)

Konkretne propozycje pierwszego zdania/hooka dla kierunku usera.

### 4. CO WZMOCNIĆ

Elementy które już są w materiale/kierunku i warto je wyeksponować:
- Konkretne liczby/dane
- Paradoksy
- Polski kontekst
- Emocjonalne zaczepienie

### 5. CO POMINĄĆ

Elementy które lepiej zostawić:
- Co jest zbyt techniczne
- Co jest banalne
- Co odciąga od głównej tezy

### 6. KONTRARGUMENTY

"Diabeł na ramieniu" - co ktoś może zarzucić:
- Możliwe obiekcje
- Słabe punkty argumentacji
- Jak się zabezpieczyć

## FORMAT ODPOWIEDZI

```json
{
  "ocena_kierunku": {
    "kierunek_usera": "Podpiąć pod polskie wybory - Nawrocki vs Trzaskowski",
    "ocena": 8,
    "co_działa": "Aktualność, emocje, polski kontekst",
    "co_ulepszyć": "Unikać dosłownego wskazywania kandydata - lepiej ogólniej o 'wyborach'",
    "ryzyko": "Może być odebrane jako polityczne opowiedzenie się po stronie"
  },
  "warianty_rozwinięcia": [
    {
      "typ": "BEZPIECZNY",
      "opis": "Skupienie na mechanizmie, nie na kandydatach. 'AI może wpływać na wybory' bez wskazywania kto zyskuje.",
      "główna_teza": "Chatboty mogą zmieniać poglądy - i to działa na WSZYSTKICH, nie tylko na głupich",
      "hook": "Myślisz że jesteś odporny na manipulację? Badanie Nature ma złe wieści.",
      "potencjał": 7,
      "ryzyko": "Mniej kontrowersyjny, mniejszy zasięg"
    },
    {
      "typ": "ODWAŻNY",
      "opis": "Wprost o polskich wyborach. Prowokacyjna teza.",
      "główna_teza": "Polskie wybory 2025 mogą być pierwszymi, gdzie AI realnie wpłynie na wynik",
      "hook": "Maj 2025. Kto wygra polskie wybory? Może już zdecydował ChatGPT.",
      "potencjał": 9,
      "ryzyko": "Może być odebrany jako polityczny, stracisz część odbiorców"
    },
    {
      "typ": "PERSONALNY",
      "opis": "Twoje własne doświadczenie z AI i zmianą zdania",
      "główna_teza": "Sam złapałem się na tym, że AI wpłynęła na moją opinię - i to mnie przeraziło",
      "hook": "Wczoraj ChatGPT zmienił moje zdanie. Dopiero dziś zrozumiałem jak.",
      "potencjał": 8,
      "ryzyko": "Wymaga autentycznej historii"
    }
  ],
  "propozycje_hooków": [
    "Myślisz że jesteś odporny na manipulację? Badanie Nature ma złe wieści.",
    "ChatGPT właśnie zmienił zdanie o polityce. Czyje? Może Twoje.",
    "10 minut rozmowy z chatbotem. Tyle wystarczy żeby zmienić Twoje poglądy wyborcze.",
    "Badacze z Nature sprawdzili czy AI może manipulować wyborcami. Wyniki są przerażające.",
    "Maj 2025. Pierwsze polskie wybory, gdzie AI może zdecydować o wyniku."
  ],
  "co_wzmocnić": [
    {
      "element": "Liczba z badania - konkretny % zmiany poglądów",
      "dlaczego": "Konkret jest mocniejszy niż ogólnik 'wpływa na poglądy'"
    },
    {
      "element": "Polski kontekst - wybory 2025",
      "dlaczego": "Aktualność, 'tu i teraz', dotyczy czytelnika"
    },
    {
      "element": "Paradoks - 'edukowane osoby też podatne'",
      "dlaczego": "Łamie schemat 'to problem głupich ludzi'"
    }
  ],
  "co_pominąć": [
    {
      "element": "Szczegóły metodologii badania",
      "dlaczego": "Nudne, nikogo nie obchodzi jak mierzyli"
    },
    {
      "element": "Porównanie z innymi badaniami",
      "dlaczego": "Rozmywa przekaz, za dużo kontekstu"
    }
  ],
  "kontrargumenty": [
    {
      "obiekcja": "To badanie z USA, nie dotyczy Polski",
      "jak_odpowiedzieć": "Badanie było też w Polsce - warto wspomnieć"
    },
    {
      "obiekcja": "Ludzie nie rozmawiają z AI o polityce",
      "jak_odpowiedzieć": "Jeszcze nie - ale zaczynają. I nie muszą wprost o polityce."
    },
    {
      "obiekcja": "To straszenie, AI to tylko narzędzie",
      "jak_odpowiedzieć": "Narzędzie które skaluje się do milionów rozmów jednocześnie"
    }
  ],
  "rekomendowany_wariant": {
    "typ": "ODWAŻNY",
    "uzasadnienie": "Polski kontekst wyborów to silny hook. Ryzyko jest, ale potencjał zasięgu duży. Kluczowe: nie opowiadać się po stronie, mówić o mechanizmie.",
    "hook": "Maj 2025. Kto wygra polskie wybory? Może już zdecydował ChatGPT."
  }
}
```

## ZASADY

1. **Szanuj kierunek usera** - nie zmieniaj go całkowicie, tylko rozwijaj i ulepszaj

2. **Daj wybór** - 3 warianty to różne poziomy ryzyka, user wybiera

3. **Bądź konkretny** - nie "można by wzmocnić dane", ale "wzmocnij: 73% badanych zmieniło zdanie"

4. **Diabeł na ramieniu** - zawsze podaj kontrargumenty, żeby user był przygotowany

5. **Nie pisz posta** - dajesz kierunki i hooki, nie gotowy tekst
"""

    def develop(
        self,
        extracted_data: dict,
        resonance_report: dict,
        depth_report: dict,
        user_direction: str,
        polish_context_report: dict = None,
        popculture_report: dict = None,
    ) -> DevelopmentReport:
        """
        Generuje raport rozwinięcia.

        Args:
            extracted_data: Dane z ExtractorAgent
            resonance_report: Raport z ResonanceHunterAgent
            depth_report: Raport z AnthropologistAgent
            user_direction: Kierunek/pomysł podany przez użytkownika
            polish_context_report: Raport z PolishContextualizerAgent (opcjonalny)
            popculture_report: Raport z PopcultureCuratorAgent (opcjonalny)

        Returns:
            DevelopmentReport z wariantami i propozycjami
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

        sections.append(f'## KIERUNEK UŻYTKOWNIKA\n\n"{user_direction}"')
        sections.append("---\n\nUżytkownik ma już wstępny kierunek. Rozwiń go - zaproponuj warianty, hooki, wskaż co wzmocnić.")

        input_text = "\n\n".join(sections)

        messages = [
            {"role": "system", "content": self.prompt_template},
            {"role": "user", "content": input_text},
        ]

        response = self.client.chat(
            messages=messages,
            model_key=self.model_key,
            temperature=0.7,
            max_tokens=4000,
        )

        return self._parse_response(response.content)

    def _parse_response(self, response: str) -> DevelopmentReport:
        """Parsuje odpowiedź do DevelopmentReport."""
        import re

        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response

            data = json.loads(json_str)

            return DevelopmentReport(
                user_direction_assessment=data.get("ocena_kierunku", {}),
                development_variants=data.get("warianty_rozwinięcia", []),
                hook_proposals=data.get("propozycje_hooków", []),
                what_to_strengthen=data.get("co_wzmocnić", []),
                what_to_skip=data.get("co_pominąć", []),
                counterarguments=data.get("kontrargumenty", []),
                recommended_variant=data.get("rekomendowany_wariant", {}),
            )

        except (json.JSONDecodeError, KeyError):
            return DevelopmentReport(
                user_direction_assessment={},
                development_variants=[],
                hook_proposals=[],
                what_to_strengthen=[],
                what_to_skip=[],
                counterarguments=[],
                recommended_variant={},
            )

    def analyze(
        self,
        content: str,
        mode: str = "development",
        platform=None,
        humor_dial: Optional[int] = None,
        context: Optional[dict] = None,
        on_progress=None,
    ) -> AgentResult:
        """Implementacja interfejsu BaseAgent."""
        if on_progress:
            on_progress("Rozwijam Twój kierunek...")

        extracted_data = context.get("extracted_data", {}) if context else {}
        resonance_report = context.get("resonance_report", {}) if context else {}
        depth_report = context.get("depth_report", {}) if context else {}
        user_direction = context.get("user_direction", "") if context else ""

        if not extracted_data:
            extracted_data = {"raw_content": content}

        report = self.develop(
            extracted_data,
            resonance_report,
            depth_report,
            user_direction
        )

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        )
