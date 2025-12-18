"""Agent: Polski Kontekstualizator - tłumaczy zagraniczne realia na polski kontekst."""

import json
import re
from dataclasses import dataclass, field
from typing import Optional, List

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient


@dataclass
class PolishEquivalent:
    """Polskie tłumaczenie liczby/skali."""
    oryginalna_wartosc: str
    polska_skala: str
    przyklad: str
    cytat_zrodlowy: str


@dataclass
class PolishConnection:
    """Temat do którego można się odnieść w Polsce."""
    temat_ze_zrodla: str
    polski_temat: str
    co_laczy: str
    jak_uzyc: str


@dataclass
class PolishVoiceSource:
    """Gdzie szukać polskich głosów na dany temat."""
    typ_eksperta: str
    instytucje: list
    jak_znalezc: str
    co_by_wiedzial: str


@dataclass
class PolishFramework:
    """Polski sposób myślenia o temacie."""
    framework_zrodla: str
    polski_framework: str
    dlaczego_lepiej_rezonuje: str
    przyklad_uzycia: str


@dataclass
class PolishContextReport:
    """Raport polskiej kontekstualizacji - uproszczony format."""
    przeliczenia: List[dict] = field(default_factory=list)
    polskie_tematy: List[dict] = field(default_factory=list)
    gdzie_szukac_glosow: List[dict] = field(default_factory=list)
    polskie_liczby: List[dict] = field(default_factory=list)
    top3: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "przeliczenia": self.przeliczenia,
            "polskie_tematy": self.polskie_tematy,
            "gdzie_szukac_glosow": self.gdzie_szukac_glosow,
            "polskie_liczby": self.polskie_liczby,
            "top3": self.top3,
        }


class PolishContextualizerAgent(BaseAgent):
    """
    Agent: Polski Kontekstualizator.

    Tłumaczy zagraniczne realia na polski kontekst:
    1. LICZBY I SKALE - przelicza na polskie proporcje
    2. POLSKIE POŁĄCZENIA - znajduje lokalne tematy do odniesienia
    3. POLSCY EKSPERCI - wskazuje kto mógłby to skomentować
    4. POLSKIE RAMY MYŚLENIA - jak Polacy myślą o tym temacie

    KLUCZOWE: Każda kontekstualizacja musi być PRZYDATNA dla agenta piszącego post!
    """

    name = "polish_contextualizer"
    name_pl = "Polski Kontekstualizator"
    description = "Tłumaczy zagraniczne realia na polski kontekst"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-sonnet-4-20250514"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# POLSKI KONTEKSTUALIZATOR

Jesteś ekspertem od polskiej rzeczywistości z głęboką znajomością kontekstu społecznego,
edukacyjnego, biznesowego i kulturowego Polski.

## TWOJE ZADANIE

Tłumaczysz zagraniczne źródła na POLSKI KONTEKST - tak żeby czytelnik z Polski
mógł się z tym odnieść, zrozumieć skalę, poczuć że to dotyczy JEGO świata.

## CZTERY PERSPEKTYWY

### 1. PRZELICZENIA NA POLSKIE REALIA

**Cel:** Amerykańskie/zagraniczne liczby są abstrakcyjne. Przelicz na polską skalę.

Przykłady:
- "30 studentów w grupie" → "W Polsce klasa to 32 osoby, więc podobnie"
- "$50,000 rocznie na studia" → "10x więcej niż średnia pensja w Polsce"
- "18,000 studentów na wydziale" → "Tyle co cała Politechnika Wrocławska"
- "25 lat nauczania" → "Zaczynał w czasach kiedy Polacy dopiero słyszeli o internecie"

Szukaj w tekście:
- Liczb (ile osób, ile kosztuje, ile trwa)
- Porównań które nic nie mówią Polakowi
- Skal które trzeba "przetłumaczyć"

### 2. POLSKIE TEMATY DO POŁĄCZENIA

**Cel:** Znajdź polski temat/debatę, z którą można połączyć źródło.

Pytania:
- O czym teraz dyskutuje się w Polsce w tym temacie?
- Jakie polskie wydarzenia/zmiany to odbijają?
- Kto w Polsce już o tym mówił?
- Jaka polska debata mogłaby skorzystać z tego przykładu?

Przykłady:
- AI w edukacji → Debata o smartfonach w polskich szkołach
- AI w edukacji → Reforma Czarnka i cyfryzacja szkół
- AI w edukacji → Polski program "Laptop dla ucznia"
- Praca profesora → Pensum 26h polskiego nauczyciela vs czas na relację ze studentem

### 3. GDZIE SZUKAĆ POLSKICH GŁOSÓW

**Cel:** Wskaż TYPY ekspertów i GDZIE ICH SZUKAĆ.

⚠️ KRYTYCZNE: NIE podawaj konkretnych imion i nazwisk!
LLM nie ma możliwości zweryfikowania czy dana osoba istnieje i czy rzeczywiście
wypowiadała się na ten temat. Fałszywe cytaty to dezinformacja.

ZAMIAST konkretnych osób, podaj:
- Typy ekspertów (naukowiec, praktyk, publicysta, aktywista)
- Instytucje gdzie ich szukać (uczelnie, fundacje, think-tanki, media)
- Jak ich znaleźć (hashtagi, konferencje, publikacje, podcasty)
- Co by wiedzieli o tym temacie

Format:
{
  "typ_eksperta": "Badacz AI z polskiej uczelni",
  "instytucje": ["IDEAS NCBR", "Wydziały informatyki PW/UW/AGH", "NASK"],
  "jak_znalezc": "Google Scholar: 'AI education Poland', konferencje ML in PL",
  "co_by_wiedzial": "Techniczne aspekty wpływu LLM na edukację"
}

### 4. POLSKIE RAMY MYŚLENIA

**Cel:** Jak Polacy myślą o tym temacie? Jakie mają obawy? Jakie nadzieje?

Pytania:
- Jaki jest POLSKI nastrój wobec tego tematu?
- Jakie są polskie stereotypy i uprzedzenia?
- Co Polacy już "wiedzą" o tym temacie (nawet jeśli źle)?
- Jakie polskie doświadczenia kształtują opinię?

Przykłady:
- AI w edukacji → Polacy boją się "ściągania", nie martwią się o "atrofię myślenia"
- AI w edukacji → W Polsce nauczyciel to autorytet (był), w USA "facilitator"
- AI w edukacji → Polskie szkoły są przeludnione - stąd problem indywidualizacji

### 5. POLSKIE REALIA - KONKRETY

**Cel:** Podaj konkretne polskie liczby, fakty, konteksty.

Zbierz:
- Ile wynosi pensum nauczyciela w Polsce?
- Ile osób jest w klasie?
- Ile zarabia nauczyciel?
- Jakie są przepisy o AI w szkołach?
- Co mówi podstawa programowa?

## ZASADY ZWIĘZŁOŚCI

- PRZELICZENIE + POLSKI KONTEKST = najważniejsze
- Max 3 elementy na kategorię
- Nie tłumacz "jak użyć" - dobre przeliczenie mówi samo za siebie
- NIE WYMYŚLAJ konkretnych osób - dawaj tylko typy i gdzie szukać!

## FORMAT ODPOWIEDZI

```json
{
  "przeliczenia": [
    {
      "zagraniczne": "30 osób w grupie",
      "polskie": "Tyle co klasa. Ale profesor ma 1 grupę, polski nauczyciel ma 6."
    }
  ],
  "polskie_tematy": [
    {
      "temat": "Debata o ChatGPT na maturze 2025",
      "jak_podpiac": "CKE nie ma stanowiska, Boston College już ma odpowiedź"
    }
  ],
  "gdzie_szukac_glosow": [
    {
      "typ_eksperta": "Naukowiec AI/ML",
      "instytucje": ["IDEAS NCBR", "Wydziały informatyki UW/PW/AGH", "NASK"],
      "jak_znalezc": "Google Scholar, konferencje ML in PL, Twitter #AIwPolsce",
      "co_by_wiedzial": "Techniczne aspekty LLM w edukacji"
    },
    {
      "typ_eksperta": "Praktyk edukacji",
      "instytucje": ["ZNP", "CEO", "Fundacja Orange", "Superbelfrzy"],
      "jak_znalezc": "Blogi nauczycielskie, podcasty edukacyjne, LinkedIn",
      "co_by_wiedzial": "Codzienne wyzwania z AI w klasie"
    }
  ],
  "polskie_liczby": [
    {
      "co": "Obciążenie nauczyciela",
      "liczba": "Pensum 26h, 180 uczniów, 3 min na ucznia dziennie"
    }
  ],
  "top3": [
    {
      "hook_pl": "Profesor z Yale ma metodę. Polski nauczyciel ma 26h pensum.",
      "siła": 9
    }
  ]
}
```

## PRZYKŁAD DOBREJ KONTEKSTUALIZACJI

Dla artykułu NYT o AI w amerykańskiej uczelni:

**Przeliczenie:**
- "30 osób w grupie" → "Tyle co polska klasa. Ale profesor ma JEDNĄ grupę. Polski nauczyciel ma SZEŚĆ."

**Polski temat:**
- "AI detektory" → "CKE przed maturą 2024 - zakaz kalkulatorów z AI. A co z maturą 2025?"

**Gdzie szukać głosów:**
- Typ: Naukowiec AI → Instytucje: IDEAS NCBR, grupy badawcze AI na UW/PW
- Typ: Praktyk edukacji → Instytucje: ZNP, Superbelfrzy, blogerzy-nauczyciele
- Jak znaleźć: konferencje EdTech, hashtag #AIwszkole, podcasty edukacyjne

**Polska rama:**
- "W USA pytanie brzmi: jak nauczyć myślenia z AI? W Polsce: jak złapać na ściąganiu?"

## CZERWONE FLAGI

❌ Generyczne stwierdzenia bez konkretów ("Polska jest inna")
❌ Przeliczenia bez źródła ("około", "mniej więcej")
❌ KONKRETNE IMIONA I NAZWISKA EKSPERTÓW - to jest ZAKAZANE!
❌ Cytaty przypisane konkretnym osobom - nie masz jak zweryfikować!
❌ Stare dane (używaj najnowszych dostępnych)
❌ Moralizowanie zamiast analizy
❌ Polska jako "gorsza" - szukaj różnic, nie oceniaj

## ŹRÓDŁA DO WERYFIKACJI (sugestie)

- GUS - dane o edukacji
- Karta Nauczyciela - przepisy
- CKE - matura, egzaminy
- MEN - reformy, podstawa programowa
- NASK - cyfryzacja, raporty o AI
- LinkedIn/Twitter polskich ekspertów
"""

    def analyze_polish_context(
        self,
        raw_source_text: str,
        extracted_data: dict,
    ) -> PolishContextReport:
        """
        Analizuje tekst i tłumaczy na polski kontekst.

        Args:
            raw_source_text: ORYGINALNY tekst źródłowy (pełny!)
            extracted_data: Dane z ExtractorAgent (pomocniczo)

        Returns:
            PolishContextReport z polskimi kontekstualizacjami
        """
        input_text = f"""## ORYGINALNY TEKST ŹRÓDŁOWY

Przeczytaj UWAŻNIE i szukaj:
- LICZB do przeliczenia na polską skalę
- TEMATÓW do połączenia z polską debatą
- OSÓB których polscy odpowiednicy mogliby komentować
- RAM MYŚLENIA do przetłumaczenia na polską mentalność

---
{raw_source_text}
---

## WYCIĄG Z EKSTRAKCJI (pomocniczo)

{json.dumps(extracted_data, ensure_ascii=False, indent=2)}

## TWOJE ZADANIE

Przygotuj POLSKĄ KONTEKSTUALIZACJĘ:
1. Przelicz liczby i skale na polskie realia
2. Znajdź polskie tematy do połączenia
3. Wskaż polskich ekspertów/głosy
4. Opisz polskie ramy myślenia o tym temacie
5. Podaj konkretne polskie dane i konteksty

PAMIĘTAJ: To ma być PRZYDATNE dla agenta piszącego post dla polskiego odbiorcy!
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

    def _parse_response(self, response: str) -> PolishContextReport:
        """Parsuje odpowiedź JSON do PolishContextReport."""
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
                    logger.warning("PolishContextualizer: Używam fallback parsowania")
                else:
                    json_str = response

            json_str = json_str.strip()
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("PolishContextualizer: Próba naprawy uciętego JSON...")
                repaired = self._repair_truncated_json(json_str)
                data = json.loads(repaired)

            return PolishContextReport(
                przeliczenia=data.get("przeliczenia", []),
                polskie_tematy=data.get("polskie_tematy", []),
                gdzie_szukac_glosow=data.get("gdzie_szukac_glosow", []),
                polskie_liczby=data.get("polskie_liczby", []),
                top3=data.get("top3", []),
            )

        except json.JSONDecodeError as e:
            logger.error(f"PolishContextualizer: JSON parse error: {e}")
            logger.error(f"PolishContextualizer: Raw response (first 500 chars): {response[:500]}")
            return PolishContextReport()
        except KeyError as e:
            logger.error(f"PolishContextualizer: Missing key: {e}")
            return PolishContextReport()
        except Exception as e:
            logger.error(f"PolishContextualizer: Unexpected error: {e}")
            return PolishContextReport()

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
            on_progress("Tłumaczę na polski kontekst...")

        extracted_data = context.get("extracted_data", {}) if context else {}
        raw_source_text = context.get("raw_source_text", "") if context else ""

        if not raw_source_text:
            raw_source_text = content

        report = self.analyze_polish_context(raw_source_text, extracted_data)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        )
