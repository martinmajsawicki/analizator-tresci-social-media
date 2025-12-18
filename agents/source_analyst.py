"""Analityk Źródła - rozbiera badania naukowe na części i tłumaczy dla laika."""

import json
import re
import logging
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient

logger = logging.getLogger(__name__)


@dataclass
class SourceAnalysisReport:
    """Raport z analizy źródła naukowego."""
    confidence_level: int  # 1-10 jak bardzo można ufać
    confidence_verdict: str  # MOCNE / UMIARKOWANE / SŁABE / WĄTPLIWE

    # KTO
    authors: dict  # autorzy, instytucja, wiarygodność

    # CO
    subject: dict  # przedmiot badania, hipoteza, pytanie badawcze

    # JAK
    methodology: dict  # metoda, próba, warunki, czas

    # WYNIKI
    results: dict  # kluczowe wyniki, liczby, efekty

    # OGRANICZENIA
    limitations: list  # lista ograniczeń z oceną wpływu

    # TŁUMACZENIE
    layman_summary: str  # wyjaśnienie dla mądrego laika
    key_numbers_explained: list  # kluczowe liczby z wyjaśnieniem

    # CO MOŻNA TWIERDZIĆ
    safe_claims: list  # co można bezpiecznie twierdzić
    risky_claims: list  # czego lepiej unikać

    def to_dict(self) -> dict:
        return {
            "poziom_zaufania": self.confidence_level,
            "werdykt_zaufania": self.confidence_verdict,
            "kto": self.authors,
            "co": self.subject,
            "jak": self.methodology,
            "wyniki": self.results,
            "ograniczenia": self.limitations,
            "tlumaczenie_dla_laika": self.layman_summary,
            "kluczowe_liczby": self.key_numbers_explained,
            "bezpieczne_twierdzenia": self.safe_claims,
            "ryzykowne_twierdzenia": self.risky_claims,
        }


class SourceAnalystAgent(BaseAgent):
    """Agent analizujący źródła naukowe i tłumaczący je dla laika."""

    name = "source_analyst"
    name_pl = "Analityk Źródła"
    description = "Rozbiera badania naukowe na części, ocenia wiarygodność i tłumaczy dla mądrego laika"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# ANALITYK ŹRÓDŁA

Jesteś naukowym fact-checkerem i tłumaczem. Rozbierasz badania na części i wyjaśniasz je tak, żeby mądry laik zrozumiał CO NAPRAWDĘ zostało udowodnione.

## TWOJE ZADANIE

Dla każdego źródła odpowiedz na pytania:

### 1. KTO ZBADAŁ?
- Autorzy (nazwiska, afiliacja)
- Instytucja (Harvard? Uniwersytet prowincjonalny? Firma?)
- Czy są ekspertami w tej dziedzinie?
- Czy jest konflikt interesów? (sponsor = producent badanego produktu?)

### 2. CO ZBADALI?
- Dokładny przedmiot badania (nie "AI" ale "ChatGPT-4 w pisaniu esejów")
- Pytanie badawcze / hipoteza
- Co chcieli udowodnić?

### 3. JAK ZBADALI?
- Metodologia (eksperyment, ankieta, analiza danych, meta-analiza?)
- Próba: ile osób/przypadków? (N=12 vs N=5000)
- Kto był w próbie? (studenci psychologii vs reprezentatywna populacja)
- Warunki: laboratorium vs świat rzeczywisty
- Czas trwania: 2 godziny vs 2 lata
- Grupa kontrolna: była czy nie?

### 4. CO WYSZŁO?
- Kluczowe wyniki (liczby!)
- Wielkość efektu (duży vs mały vs nieistotny)
- Istotność statystyczna (p-value)
- Co to NAPRAWDĘ oznacza?

### 5. OGRANICZENIA
Oceń każde ograniczenie: [KRYTYCZNE / ISTOTNE / DROBNE]
- Mała próba
- Niereprezentatywna próba
- Laboratorium vs real life
- Krótki czas obserwacji
- Brak grupy kontrolnej
- Sponsoring przez zainteresowaną stronę
- Brak replikacji
- Korelacja ≠ przyczynowość

## ZASADY TŁUMACZENIA

- **p < 0.05** → "Wynik prawdopodobnie nie jest przypadkowy"
- **d = 0.8** → "Duży efekt - wyraźna różnica"
- **d = 0.2** → "Mały efekt - ledwo zauważalna różnica"
- **N = 47** → "Bardzo mała próba - wnioski niepewne"
- **r = 0.3** → "Słaba korelacja - związek istnieje, ale słaby"
- **RCT** → "Złoty standard badań - losowy przydział do grup"
- **meta-analiza** → "Podsumowanie wielu badań - mocniejsze wnioski"

## FORMAT ODPOWIEDZI

```json
{
  "poziom_zaufania": 7,
  "werdykt_zaufania": "UMIARKOWANE",
  "kto": {
    "autorzy": "Smith et al., Stanford University",
    "wiarygodnosc": "Renomowana uczelnia, autorzy publikowali w tym obszarze",
    "konflikt_interesow": "Brak lub Tak - badanie finansowane przez OpenAI"
  },
  "co": {
    "przedmiot": "Wpływ ChatGPT-4 na jakość esejów studentów pierwszego roku",
    "hipoteza": "Studenci używający ChatGPT piszą lepsze eseje",
    "kontekst": "Debata o AI w edukacji"
  },
  "jak": {
    "metodologia": "Eksperyment z grupą kontrolną (RCT)",
    "proba_n": 234,
    "proba_kto": "Studenci pierwszego roku, jeden uniwersytet",
    "warunki": "Kontrolowane - pisanie w laboratorium",
    "czas_trwania": "Jednorazowe zadanie (2h)",
    "grupa_kontrolna": "Tak - pisali bez AI"
  },
  "wyniki": {
    "glowny_wynik": "Grupa z AI uzyskała średnio 12% wyższe oceny",
    "wielkosc_efektu": "d = 0.45 (średni efekt)",
    "istotnosc": "p < 0.01 (bardzo prawdopodobnie nie przypadek)",
    "dodatkowe": "Efekt silniejszy u słabszych studentów"
  },
  "ograniczenia": [
    {
      "ograniczenie": "Jeden uniwersytet, studenci z USA",
      "wplyw": "ISTOTNE",
      "co_to_znaczy": "Może nie działać tak samo w Polsce lub na innych kierunkach"
    },
    {
      "ograniczenie": "Jednorazowe zadanie, nie długoterminowa nauka",
      "wplyw": "KRYTYCZNE",
      "co_to_znaczy": "Nie wiemy czy efekt utrzymuje się w czasie"
    },
    {
      "ograniczenie": "Warunki laboratoryjne",
      "wplyw": "ISTOTNE",
      "co_to_znaczy": "W domu, bez nadzoru, wyniki mogą być inne"
    }
  ],
  "tlumaczenie_dla_laika": "Badacze ze Stanforda sprawdzili czy studenci piszą lepsze eseje z pomocą ChatGPT. 234 studentów podzielono na dwie grupy - jedna pisała z AI, druga bez. Wynik: eseje pisane z AI były oceniane średnio o 12% wyżej. To nie przypadek (statystycznie pewne). ALE: badano tylko jeden uniwersytet, jedno zadanie, w kontrolowanych warunkach. Nie wiemy czy działa długoterminowo ani czy studenci czegoś się uczą.",
  "kluczowe_liczby": [
    {
      "liczba": "12% wyższe oceny",
      "co_znaczy": "Zauważalna poprawa, ale nie rewolucja",
      "kontekst": "Różnica między 3.0 a 3.4 w skali 1-5"
    },
    {
      "liczba": "N = 234",
      "co_znaczy": "Przyzwoita próba dla eksperymentu",
      "kontekst": "Wystarczająca do wstępnych wniosków, za mała do generalizacji"
    }
  ],
  "bezpieczne_twierdzenia": [
    "ChatGPT może pomóc studentom pisać lepiej oceniane eseje",
    "Efekt jest statystycznie istotny",
    "Słabsi studenci mogą zyskać więcej"
  ],
  "ryzykowne_twierdzenia": [
    "ChatGPT rewolucjonizuje edukację - za wcześnie na takie wnioski",
    "Studenci uczą się lepiej z AI - badanie nie mierzyło nauki, tylko oceny",
    "To działa wszędzie - badano tylko jeden uniwersytet w USA"
  ]
}
```

## WERDYKT ZAUFANIA

- **MOCNE** (8-10): Meta-analiza, duża próba, replikowane wyniki, brak konfliktu interesów
- **UMIARKOWANE** (5-7): Solidna metodologia ale ograniczenia, pojedyncze badanie
- **SŁABE** (3-4): Mała próba, problemy metodologiczne, brak replikacji
- **WĄTPLIWE** (1-2): Poważne błędy, konflikt interesów, niereprezentatywna próba

## ZŁOTE ZASADY

1. **Korelacja ≠ przyczynowość** - zawsze to zaznacz
2. **Studenci psychologii ≠ ludzie** - próby akademickie są specyficzne
3. **Laboratorium ≠ życie** - kontrolowane warunki ≠ rzeczywistość
4. **Jedno badanie ≠ prawda** - dopiero replikacje dają pewność
5. **Sponsor ma znaczenie** - badanie Coca-Coli o cukrze = czerwona flaga
6. **Wielkość efektu > p-value** - "istotne statystycznie" może być nieistotne praktycznie
"""

    def analyze_source(self, content: str, context: Optional[dict] = None) -> SourceAnalysisReport:
        """
        Analizuje źródło naukowe.

        Args:
            content: Treść źródła do analizy
            context: Dodatkowy kontekst

        Returns:
            SourceAnalysisReport z analizą
        """
        input_text = f"## ŹRÓDŁO DO ANALIZY\n\n{content}"

        if context:
            if context.get("extracted_data"):
                input_text += f"\n\n## WSTĘPNIE WYEKSTRAHOWANE DANE\n{json.dumps(context['extracted_data'], ensure_ascii=False, indent=2)}"

        messages = [
            {"role": "system", "content": self.prompt_template},
            {"role": "user", "content": input_text},
        ]

        response = self.client.chat(
            messages=messages,
            model_key=self.model_key,
            temperature=0.3,  # Niska temperatura dla precyzji
            max_tokens=4000,  # Więcej tokenów - to szczegółowa analiza
        )

        return self._parse_response(response.content)

    def _parse_response(self, response: str) -> SourceAnalysisReport:
        """Parsuje odpowiedź JSON do SourceAnalysisReport."""
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
                    logger.warning("SourceAnalyst: Używam fallback parsowania")
                else:
                    json_str = response

            json_str = json_str.strip()
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("SourceAnalyst: Próba naprawy uciętego JSON...")
                repaired = self._repair_truncated_json(json_str)
                data = json.loads(repaired)

            return SourceAnalysisReport(
                confidence_level=data.get("poziom_zaufania", 5),
                confidence_verdict=data.get("werdykt_zaufania", "UMIARKOWANE"),
                authors=data.get("kto", {}),
                subject=data.get("co", {}),
                methodology=data.get("jak", {}),
                results=data.get("wyniki", {}),
                limitations=data.get("ograniczenia", []),
                layman_summary=data.get("tlumaczenie_dla_laika", ""),
                key_numbers_explained=data.get("kluczowe_liczby", []),
                safe_claims=data.get("bezpieczne_twierdzenia", []),
                risky_claims=data.get("ryzykowne_twierdzenia", []),
            )

        except json.JSONDecodeError as e:
            logger.error(f"SourceAnalyst: JSON parse error: {e}")
            logger.error(f"SourceAnalyst: Raw response (first 500 chars): {response[:500]}")
            return SourceAnalysisReport(
                confidence_level=0,
                confidence_verdict="BŁĄD",
                authors={},
                subject={},
                methodology={},
                results={},
                limitations=[],
                layman_summary="",
                key_numbers_explained=[],
                safe_claims=[],
                risky_claims=[],
            )
        except Exception as e:
            logger.error(f"SourceAnalyst: Unexpected error: {e}")
            return SourceAnalysisReport(
                confidence_level=0,
                confidence_verdict="BŁĄD",
                authors={},
                subject={},
                methodology={},
                results={},
                limitations=[],
                layman_summary="",
                key_numbers_explained=[],
                safe_claims=[],
                risky_claims=[],
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
            on_progress("Analizuję źródło naukowe...")

        report = self.analyze_source(content, context)
        result_content = json.dumps(report.to_dict(), ensure_ascii=False, indent=2)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=result_content,
            score=float(report.confidence_level),
        )
