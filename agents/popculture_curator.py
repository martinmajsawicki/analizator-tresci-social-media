"""Agent: Kurator Popkultury - znajduje analogie z filmów, seriali, sportu, codzienności."""

import json
import re
from dataclasses import dataclass, field
from typing import Optional, List

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient


@dataclass
class FilmAnalogy:
    """Analogia filmowa/serialowa."""
    scena_z_filmu: str
    film_serial: str
    co_laczy: str
    cytat_filmowy: str
    jak_uzyc: str


@dataclass
class SportsAnalogy:
    """Analogia sportowa."""
    sytuacja_sportowa: str
    dyscyplina: str
    co_laczy: str
    jak_uzyc: str


@dataclass
class EverydayAnalogy:
    """Analogia z codzienności."""
    sytuacja_codzienna: str
    co_laczy: str
    dlaczego_dziala: str
    jak_uzyc: str


@dataclass
class PopcultureReport:
    """Raport popkulturowy - uproszczony format."""
    filmy_seriale: List[dict] = field(default_factory=list)
    sport: List[dict] = field(default_factory=list)
    codziennosc: List[dict] = field(default_factory=list)
    memy: List[dict] = field(default_factory=list)
    literatura: List[dict] = field(default_factory=list)
    top3: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "filmy_seriale": self.filmy_seriale,
            "sport": self.sport,
            "codziennosc": self.codziennosc,
            "memy": self.memy,
            "literatura": self.literatura,
            "top3": self.top3,
        }


class PopcultureCuratorAgent(BaseAgent):
    """
    Agent: Kurator Popkultury.

    Znajduje analogie i metafory z:
    1. FILMÓW I SERIALI - sceny, postacie, cytaty
    2. SPORTU - mecze, zawodnicy, sytuacje boiskowe
    3. CODZIENNOŚCI - sytuacje uniwersalne, zrozumiałe dla każdego
    4. MEMÓW I INTERNETU - virale, trendy, format memowy
    5. LITERATURY - klasyka, cytaty, postacie

    KLUCZOWE: Analogie muszą OŚWIETLAĆ temat, nie tylko być ozdobnikiem!
    """

    name = "popculture_curator"
    name_pl = "Kurator Popkultury"
    description = "Znajduje analogie z filmów, sportu, codzienności"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-sonnet-4-20250514"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# KURATOR POPKULTURY

Jesteś ekspertem od znajdowania TRAFNYCH analogii i metafor z popkultury,
sportu i codziennego życia, które pomagają zrozumieć abstrakcyjne tematy.

## TWOJE ZADANIE

Znajdź analogie, które OŚWIETLAJĄ temat - pomagają czytelnikowi zrozumieć
coś trudnego przez coś znajomego. NIE chodzi o ozdobniki, tylko o ZROZUMIENIE.

## PIĘĆ OBSZARÓW

### 1. FILMY I SERIALE

**Cel:** Znajdź scenę, postać lub cytat który WYJAŚNIA dynamikę z tekstu.

Przykłady dobrych analogii:
- "To jak scena z Matrix - czerwona czy niebieska pigułka. Studenci muszą wybrać: łatwa droga z AI czy trudna droga myślenia."
- "Nauczyciel jak Gandalf na moście: 'You shall not pass!' - ale demon to nie AI, to lenistwo."
- "Jak w 'The Office' - Michael Scott robi 100 spotkań, żadne nic nie znaczy. Tak samo z esejami pisanymi przez AI."

Szukaj:
- Scen które pokazują TĘ SAMĄ dynamikę
- Postaci w podobnej sytuacji
- Dialogów które można sparafrazować
- Uniwersalnych momentów (zdrada, odkrycie, przemiana)

**WAŻNE:** Wybieraj filmy ZNANE szerokiej publiczności (nie niszowe).

### 2. SPORT

**Cel:** Znajdź sytuację sportową która wyjaśnia mechanizm z tekstu.

Przykłady:
- "Używanie AI do myślenia to jak wjechanie na maraton na rowerze. Dotrzesz szybciej, ale nie będziesz biegaczem."
- "Profesor jak trener - nie biega za zawodnika, ale pokazuje jak biegać."
- "To jak doping - chwilowa przewaga, długoterminowa strata."

Sport działa bo:
- Jasne reguły, jasne zwycięstwa/porażki
- Zrozumiały wysiłek i nagroda
- Powszechnie znane sytuacje

### 3. CODZIENNOŚĆ

**Cel:** Znajdź sytuację z życia KAŻDEGO która wyjaśnia abstrakcję.

Przykłady:
- "To jak używanie GPS-a - super że dojedziesz, ale nie nauczysz się drogi."
- "Jak dieta cud - efekt jest, ale nie utrzymasz."
- "Jak zlecanie dziecku sprzątania i robienie tego za nie - pokój czysty, dziecko nie umie sprzątać."

Codzienność działa bo:
- KAŻDY to zna
- Nie trzeba tłumaczyć
- Od razu "klika"

### 4. MEMY I INTERNET

**Cel:** Czy istnieje format memowy który to wyjaśnia? Viral który to pokazuje?

Przykłady:
- "Jak ten mem 'me explaining to my mom' - tylko tu student tłumaczy AI jak pisać essay"
- "Viral 'ok boomer' - tyle że teraz to studenci mówią do AI 'ok, ChatGPT, napisz to za mnie'"
- "Like the 'distracted boyfriend' meme - student, essay, ChatGPT"

**UWAGA:** Memy szybko się starzeją. Używaj klasycznych lub wyjaśniaj nowe.

### 5. LITERATURA I KLASYKA

**Cel:** Czy istnieje klasyczny tekst, mit, bajka która to wyjaśnia?

Przykłady:
- "Jak Faustowska umowa - moc teraz, koszt później"
- "Jak Syzyf - tylko że student SAM wtacza kamień AI na górę i dziwi się że spada"
- "Jak bajka o wilku i owcach - tylko że wilk to nie AI, to nasza własna leniwa natura"

## ZASADY ZWIĘZŁOŚCI

- ANALOGIA + źródło (film/sport/codzienność) = najważniejsze
- Max 2-3 na kategorię
- Jeśli źródło MA świetną metaforę - UŻYJ JEJ, nie wymyślaj gorszej
- Tylko ZNANE filmy/seriale (nie niszowe)

## FORMAT ODPOWIEDZI

```json
{
  "filmy_seriale": [
    {
      "źródło": "Matrix",
      "analogia": "Wybór pigułki = wybór: trudna prawda (myślenie) czy wygodne kłamstwo (AI)"
    }
  ],
  "sport": [
    {
      "analogia": "Hulajnoga na maratonie - dotrzesz, ale nie będziesz biegaczem",
      "uwaga": "JUŻ W TEKŚCIE - użyj dosłownie!"
    }
  ],
  "codzienność": [
    {
      "analogia": "GPS - dojedziesz, ale nie nauczysz się drogi"
    }
  ],
  "memy": [
    {
      "mem": "Distracted boyfriend: student / essay / ChatGPT"
    }
  ],
  "literatura": [
    {
      "źródło": "Ikar",
      "analogia": "Skrzydła z wosku - technologia która zawodzi w kluczowym momencie"
    }
  ],
  "top3": [
    {
      "analogia": "Hulajnoga na maratonie",
      "ze_źródła": true,
      "siła": 9
    }
  ]
}
```

## KRYTERIA DOBREJ ANALOGII

✅ OŚWIETLA - pomaga ZROZUMIEĆ, nie tylko ilustruje
✅ ZNANA - odbiorca od razu wie o co chodzi
✅ TRAFNA - mechanizm jest TEN SAM, nie tylko podobny
✅ ZAPAMIĘTYWALNA - zostaje w głowie
✅ NIE WYMAGA TŁUMACZENIA - od razu "klika"

## CZERWONE FLAGI

❌ Analogia wymaga 3 zdań wyjaśnienia → za skomplikowana
❌ Film/serial niszowy → nikt nie zrozumie
❌ Mechanizm tylko PODOBNY, nie TAKI SAM → myląca
❌ Wymyślona dla ozdoby → pusta
❌ Źródło MA świetną metaforę a ty wymyślasz nową → głupie

## WAŻNE: SZANUJ ŹRÓDŁO!

Jeśli w tekście źródłowym JEST świetna metafora (np. "hulajnoda na maratonie"),
to UŻYJ JEJ. Nie wymyślaj gorszej. Twoje zadanie to:

1. ZNALEŹĆ dobre metafory w źródle
2. DODAĆ nowe TYLKO jeśli brakuje dla danego obszaru
3. ZAPROPONOWAĆ jak ich użyć (hook, puenta, rozwinięcie)

## PRZYKŁAD DOBREJ ANALIZY

Dla artykułu o AI w edukacji:

**ZE ŹRÓDŁA (użyj!):**
- "Using AI to do your thinking is like joining the track team and doing your laps on an electric scooter" → IDEALNA analogia sportowa, już gotowa!

**DODANE (bo brakuje):**
- FILM: Matrix + wybór pigułki → inny aspekt (wybór, nie wysiłek)
- CODZIENNOŚĆ: GPS → dla szerszej publiczności
- LITERATURA: Faust → dla LinkedIn (profesjonalna metafora kosztu)

**REKOMENDACJA:**
- LinkedIn: "Hulajnoga na maratonie" jako hook + "Faust" jako rozwinięcie
- Facebook: "GPS" - prostsze, bardziej codzienne
"""

    def analyze_popculture(
        self,
        raw_source_text: str,
        extracted_data: dict,
    ) -> PopcultureReport:
        """
        Znajduje analogie popkulturowe dla tematu.

        Args:
            raw_source_text: ORYGINALNY tekst źródłowy (pełny!)
            extracted_data: Dane z ExtractorAgent (pomocniczo)

        Returns:
            PopcultureReport z analogiami z różnych obszarów
        """
        input_text = f"""## ORYGINALNY TEKST ŹRÓDŁOWY

Przeczytaj UWAŻNIE i szukaj:
- METAFOR i ANALOGII które już są w tekście (użyj ich!)
- Dynamik i mechanizmów które można zilustrować przez popkulturę
- Sytuacji które mają odpowiedniki w filmach, sporcie, codzienności

---
{raw_source_text}
---

## WYCIĄG Z EKSTRAKCJI (pomocniczo)

{json.dumps(extracted_data, ensure_ascii=False, indent=2)}

## TWOJE ZADANIE

Znajdź TRAFNE analogie z pięciu obszarów:
1. FILMY I SERIALE - sceny, postacie, cytaty
2. SPORT - sytuacje, mechanizmy, metafory
3. CODZIENNOŚĆ - uniwersalne sytuacje
4. MEMY I INTERNET - formaty, virale
5. LITERATURA - klasyka, mity, bajki

PAMIĘTAJ:
- Najpierw sprawdź co już JEST w źródle!
- Analogia ma OŚWIETLAĆ, nie ozdabiać!
- Wybieraj ZNANE, nie niszowe!
"""

        messages = [
            {"role": "system", "content": self.prompt_template},
            {"role": "user", "content": input_text},
        ]

        response = self.client.chat(
            messages=messages,
            model_key=self.model_key,
            temperature=0.8,  # Wyższa temperatura dla kreatywności
            max_tokens=4000,
        )

        return self._parse_response(response.content)

    def _parse_response(self, response: str) -> PopcultureReport:
        """Parsuje odpowiedź JSON do PopcultureReport."""
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
                    logger.warning("PopcultureCurator: Używam fallback parsowania")
                else:
                    json_str = response

            json_str = json_str.strip()
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("PopcultureCurator: Próba naprawy uciętego JSON...")
                repaired = self._repair_truncated_json(json_str)
                data = json.loads(repaired)

            return PopcultureReport(
                filmy_seriale=data.get("filmy_seriale", []),
                sport=data.get("sport", []),
                codziennosc=data.get("codzienność", data.get("codziennosc", [])),
                memy=data.get("memy", []),
                literatura=data.get("literatura", []),
                top3=data.get("top3", []),
            )

        except json.JSONDecodeError as e:
            logger.error(f"PopcultureCurator: JSON parse error: {e}")
            logger.error(f"PopcultureCurator: Raw response (first 500 chars): {response[:500]}")
            return PopcultureReport()
        except KeyError as e:
            logger.error(f"PopcultureCurator: Missing key: {e}")
            return PopcultureReport()
        except Exception as e:
            logger.error(f"PopcultureCurator: Unexpected error: {e}")
            return PopcultureReport()

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
            on_progress("Szukam analogii popkulturowych...")

        extracted_data = context.get("extracted_data", {}) if context else {}
        raw_source_text = context.get("raw_source_text", "") if context else ""

        if not raw_source_text:
            raw_source_text = content

        report = self.analyze_popculture(raw_source_text, extracted_data)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        )
