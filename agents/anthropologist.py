"""Agent: Antropolog Treści - perspektywa etnograficzna, socjologiczna, psychologiczna."""

import json
import re
from dataclasses import dataclass, field
from typing import Optional, List

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient


@dataclass
class EthnographicObservation:
    """Obserwacja etnograficzna."""
    scena: str
    cytat: str
    co_to_pokazuje: str
    jak_uzyc: str


@dataclass
class SocialDivision:
    """Podział społeczny."""
    podzial: str
    strona_a: str
    strona_b: str
    cytat: str
    kto_zyskuje: str
    kto_traci: str


@dataclass
class Emotion:
    """Emocja zidentyfikowana w tekście."""
    emocja: str
    kto: str
    cytat: str
    kontekst: str
    jak_uzyc: str


@dataclass
class PersonToUse:
    """Osoba do wykorzystania w poście."""
    osoba: str
    rola: str
    historia: str
    cytat: str
    dlaczego_ciekawa: str


@dataclass
class AnthropologyReport:
    """Raport antropologiczny - uproszczony format."""
    etnografia: List[dict] = field(default_factory=list)
    socjologia: List[dict] = field(default_factory=list)
    psychologia: List[dict] = field(default_factory=list)
    osoby: List[dict] = field(default_factory=list)
    top3_cytaty: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "etnografia": self.etnografia,
            "socjologia": self.socjologia,
            "psychologia": self.psychologia,
            "osoby": self.osoby,
            "top3_cytaty": self.top3_cytaty,
        }


# Alias dla kompatybilności wstecznej z orchestrator_v2
DepthReport = AnthropologyReport


class AnthropologistAgent(BaseAgent):
    """
    Agent: Antropolog Treści.

    Analizuje tekst przez trzy soczewki:
    1. ETNOGRAFICZNA - jak to wygląda w praktyce, rytuały, nawyki
    2. SOCJOLOGICZNA - kto zyskuje, kto traci, podziały, konflikty
    3. PSYCHOLOGICZNA - emocje, potrzeby, mechanizmy obronne

    KLUCZOWE: Każdy insight musi być OPARTY na cytacie z tekstu źródłowego!
    """

    name = "anthropologist"
    name_pl = "Antropolog Treści"
    description = "Analizuje wymiar ludzki: etnografia, socjologia, psychologia"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-sonnet-4-20250514"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# ANTROPOLOG TREŚCI

Jesteś antropologiem kultury cyfrowej z głębokim zrozumieniem społeczeństw.
Twoje zadanie to odkrycie GŁĘBSZYCH warstw tematu poprzez trzy soczewki:
etnograficzną, socjologiczną i psychologiczną.

## ZASADA NADRZĘDNA

**Otrzymujesz ORYGINALNY TEKST ŹRÓDŁOWY - nie tylko streszczenie!**

KAŻDY insight musi być OPARTY na fragmencie tekstu:
- Cytuj dosłownie
- Wskazuj konkretne osoby i historie
- Nie wymyślaj - wyciągaj

## TRZY PERSPEKTYWY

### 1. ETNOGRAFICZNA (jak to wygląda w praktyce)

Szukasz: Jak abstrakcyjny temat przejawia się w KONKRETNYM życiu ludzi?

Pytania:
- Jak to wygląda w domu? Przy śniadaniu? Wieczorem?
- Jak wygląda w pracy? Na spotkaniu? W mailu?
- Jakie RYTUAŁY i NAWYKI to tworzy lub niszczy?
- Kto z kim o tym rozmawia? Kto milczy?

Szukaj w tekście:
- Scen, które można sobie wyobrazić
- Opisów codziennych interakcji
- Rytuałów i nawyków
- Momentów które pokazują "jak to naprawdę wygląda"

### 2. SOCJOLOGICZNA (kto zyskuje, kto traci)

Szukasz: Jakie GRUPY i PODZIAŁY ujawnia ten temat?

Pytania:
- Kto zyskuje na obecnej sytuacji? Kto traci?
- Jakie podziały ujawnia? (wiek, klasa, region, dostęp)
- Kto ma WŁADZĘ w tej sytuacji? Kto jest bezsilny?
- Jakie SOJUSZE i KONFLIKTY się tworzą?

Szukaj w tekście:
- Porównań między grupami
- Konfliktów (nawet subtelnych)
- Kto podejmuje decyzje, kto je wykonuje
- Nierówności i asymetrii

### 3. PSYCHOLOGICZNA (co czują ludzie)

Szukasz: Jakie EMOCJE i MECHANIZMY OBRONNE uruchamia temat?

Pytania:
- Jakie podstawowe emocje wywołuje? (strach, nadzieja, wstyd, duma, zazdrość, ulga)
- Jakie mechanizmy obronne? (wyparcie, racjonalizacja, projekcja)
- Jakie POTRZEBY zaspokaja lub frustruje? (bezpieczeństwo, przynależność, uznanie, autonomia)
- Jaki WEWNĘTRZNY KONFLIKT może wywołać?

Szukaj w tekście:
- Słów opisujących emocje
- Reakcji ludzi (zaskoczenie, ulga, strach)
- Dylematów i wyborów
- Tego co ludzie CHCĄ vs co ROBIĄ

## ZASADY ZWIĘZŁOŚCI

- CYTAT + SCENA = najważniejsze. Interpretacje skracaj do 1 zdania.
- Max 3 elementy na kategorię
- Nie tłumacz "jak użyć" - dobry cytat mówi sam za siebie
- Jeśli czegoś nie ma w tekście - pomiń kategorię (nie wymyślaj)

## FORMAT ODPOWIEDZI

```json
{
  "etnografia": [
    {
      "scena": "Krótki opis sceny (max 15 słów)",
      "cytat": "Dosłowny cytat ze źródła"
    }
  ],
  "socjologia": [
    {
      "podzial": "Kto vs kto (np. elity vs masy)",
      "cytat": "Cytat pokazujący ten podział"
    }
  ],
  "psychologia": [
    {
      "emocja": "Nazwa emocji + kto ją czuje",
      "cytat": "Cytat wyrażający tę emocję"
    }
  ],
  "osoby": [
    {
      "kto": "Imię, rola",
      "cytat": "Ich najsilniejsze słowa"
    }
  ],
  "top3_cytaty": [
    {
      "cytat": "Najsilniejszy cytat",
      "typ": "emocja|konflikt|scena"
    }
  ]
}
```

## PRZYKŁAD DOBREJ ANALIZY

Dla artykułu o AI w edukacji:

**Etnograficzna:**
- SCENA: "Tyler approached me... 'Can we talk sometime about how we can ask the questions on our own?'"
  → Student podchodzi PO zajęciach, potrzebuje odwagi, to nie jest norma

**Socjologiczna:**
- PODZIAŁ: Boston College (30 osób) vs Penn State (18,000)
  → "Stuart Selber... provides required writing courses to 18,000 students"
- KONFLIKT WEWNĄTRZ GRUPY: Studenci vs studenci
  → "at least some of them 'are not that OK' with peers who rely on A.I." (Josie)

**Psychologiczna:**
- EMOCJA: Ulga profesorów
  → "it has come as a pleasant surprise... that the A.I. apocalypse has not come to pass"
- POTRZEBA ZASKAKUJĄCA: Studenci CHCĄ być offline
  → "Device-free classrooms feel like a respite"

## CZERWONE FLAGI

❌ Piszesz "ludzie boją się" bez cytatu KTO i CO powiedział
❌ Wymyślasz emocje których nie ma w tekście
❌ Generujesz abstrakcyjne "napięcia społeczne" zamiast konkretnych z tekstu
❌ Pomijasz osoby wymienione z imienia
❌ Nie dajesz cytatów do użycia
❌ Twoje "obserwacje" nie mają oparcia w tekście źródłowym
"""

    def analyze_anthropology(
        self,
        raw_source_text: str,
        extracted_data: dict,
    ) -> AnthropologyReport:
        """
        Analizuje tekst przez pryzmat antropologiczny.

        Args:
            raw_source_text: ORYGINALNY tekst źródłowy (pełny!)
            extracted_data: Dane z ExtractorAgent (pomocniczo)

        Returns:
            AnthropologyReport z trzema perspektywami
        """
        input_text = f"""## ORYGINALNY TEKST ŹRÓDŁOWY

Przeczytaj UWAŻNIE i szukaj:
- Konkretnych SCEN i INTERAKCJI (etnografia)
- PODZIAŁÓW i KONFLIKTÓW między grupami (socjologia)
- EMOCJI i POTRZEB wyrażonych explicite (psychologia)
- OSÓB wymienionych z imienia - ich historie są cenne!

---
{raw_source_text}
---

## WYCIĄG Z EKSTRAKCJI (pomocniczo)

{json.dumps(extracted_data, ensure_ascii=False, indent=2)}

## TWOJE ZADANIE

Przeanalizuj tekst przez TRZY SOCZEWKI:
1. ETNOGRAFICZNA - sceny, rytuały, jak to wygląda w praktyce
2. SOCJOLOGICZNA - podziały, konflikty, kto zyskuje/traci
3. PSYCHOLOGICZNA - emocje, potrzeby, dylematy

PAMIĘTAJ: Każdy insight = cytat z tekstu!
"""

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

    def _parse_response(self, response: str) -> AnthropologyReport:
        """Parsuje odpowiedź JSON do AnthropologyReport."""
        import logging
        logger = logging.getLogger(__name__)

        try:
            # 1. Spróbuj normalnego regex z zamykającym tagiem
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 2. Fallback: wyciągnij JSON po ```json (nawet bez zamknięcia - ucięta odpowiedź)
                json_start = re.search(r'```json\s*', response)
                if json_start:
                    json_str = response[json_start.end():]
                    # Usuń końcowy ``` jeśli jest
                    if '```' in json_str:
                        json_str = json_str[:json_str.rfind('```')]
                    logger.warning("Anthropologist: Używam fallback parsowania (możliwe ucięcie odpowiedzi)")
                else:
                    # 3. Może JSON jest bezpośrednio (bez znaczników)
                    json_str = response

            # Próba naprawy uciętego JSON
            json_str = json_str.strip()
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                # Spróbuj naprawić ucięty JSON - zamknij otwarte struktury
                logger.warning("Anthropologist: Próba naprawy uciętego JSON...")
                repaired = self._repair_truncated_json(json_str)
                data = json.loads(repaired)

            return AnthropologyReport(
                etnografia=data.get("etnografia", []),
                socjologia=data.get("socjologia", []),
                psychologia=data.get("psychologia", []),
                osoby=data.get("osoby", []),
                top3_cytaty=data.get("top3_cytaty", []),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Anthropologist: JSON parse error: {e}")
            logger.error(f"Anthropologist: Raw response (first 500 chars): {response[:500]}")
            return AnthropologyReport()
        except KeyError as e:
            logger.error(f"Anthropologist: Missing key: {e}")
            return AnthropologyReport()
        except Exception as e:
            logger.error(f"Anthropologist: Unexpected error: {e}")
            return AnthropologyReport()

    def _repair_truncated_json(self, json_str: str) -> str:
        """Próbuje naprawić ucięty JSON zamykając otwarte struktury."""
        # Zlicz otwarte nawiasy
        open_braces = json_str.count('{') - json_str.count('}')
        open_brackets = json_str.count('[') - json_str.count(']')

        # Usuń niedokończony element (po ostatnim przecinku)
        last_complete = max(
            json_str.rfind('},'),
            json_str.rfind('],'),
            json_str.rfind('",'),
        )

        if last_complete > 0:
            json_str = json_str[:last_complete + 1]
            open_braces = json_str.count('{') - json_str.count('}')
            open_brackets = json_str.count('[') - json_str.count(']')

        # Zamknij otwarte struktury
        json_str += ']' * open_brackets
        json_str += '}' * open_braces

        return json_str

    # Aliasy dla kompatybilności wstecznej
    def deepen(
        self,
        extracted_data: dict,
        resonance_report: dict,
        raw_source_text: str = "",
    ) -> AnthropologyReport:
        """Alias dla analyze_anthropology - kompatybilność wsteczna."""
        return self.analyze_anthropology(raw_source_text, extracted_data)

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
            on_progress("Analizuję wymiar ludzki (etnografia, socjologia, psychologia)...")

        extracted_data = context.get("extracted_data", {}) if context else {}
        raw_source_text = context.get("raw_source_text", "") if context else ""

        if not raw_source_text:
            raw_source_text = content

        report = self.analyze_anthropology(raw_source_text, extracted_data)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        )
