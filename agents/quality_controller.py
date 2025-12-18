"""Agent 4: Kontroler Jakości - sprawdza posty i proponuje poprawki (tryb SZLIF)."""

import json
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient


@dataclass
class QualityCheck:
    """Wynik kontroli jakości dla jednej platformy."""
    platform: str
    status: str  # "OK" lub "POPRAW"
    score: int  # 1-10
    checks: dict  # wyniki poszczególnych sprawdzeń
    issues: list  # lista problemów
    suggestions: list  # lista sugestii

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "status": self.status,
            "score": self.score,
            "checks": self.checks,
            "issues": self.issues,
            "suggestions": self.suggestions,
        }


@dataclass
class PolishReport:
    """Raport trybu SZLIF - ocena + konkretne poprawki."""
    original_text: str
    score: int  # 1-10
    status: str  # OK, POPRAW, PRZEPISZ
    strengths: list  # mocne strony
    issues: list  # problemy
    inline_corrections: list  # poprawki inline: [{"original": "...", "corrected": "...", "reason": "..."}]
    improved_version: str  # przepisana wersja
    hook_alternatives: list  # alternatywne hooki

    def to_dict(self) -> dict:
        return {
            "oryginalny_tekst": self.original_text,
            "ocena": self.score,
            "status": self.status,
            "mocne_strony": self.strengths,
            "problemy": self.issues,
            "poprawki_inline": self.inline_corrections,
            "wersja_po_poprawkach": self.improved_version,
            "alternatywne_hooki": self.hook_alternatives,
        }


@dataclass
class QualityReport:
    """Pełny raport kontroli jakości."""
    platform_results: dict  # wyniki per platforma
    overall_status: str
    overall_score: float
    critical_issues: list
    summary: str

    def to_dict(self) -> dict:
        return {
            "platform_results": {k: v.to_dict() if hasattr(v, 'to_dict') else v for k, v in self.platform_results.items()},
            "overall_status": self.overall_status,
            "overall_score": self.overall_score,
            "critical_issues": self.critical_issues,
            "summary": self.summary,
        }


class QualityControllerAgent(BaseAgent):
    """
    Agent 4: Kontroler Jakości.

    Sprawdza dla każdej platformy:
    - [ ] Hook NIE zaczyna się od źródła
    - [ ] Jest element "tu i teraz" (Polska, aktualność)
    - [ ] Źródło jest podane (ale nie na początku)
    - [ ] Brak wodolejstwa i korporacyjnego tonu
    - [ ] Uwagi usera zostały uwzględnione
    - [ ] Ton pasuje do platformy
    """

    name = "quality_controller"
    name_pl = "Kontroler Jakości"
    description = "Sprawdza jakość wszystkich wygenerowanych postów"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# KONTROLER JAKOŚCI

Jesteś bezwzględnym recenzentem treści. Twoje zadanie to znaleźć WSZYSTKIE problemy, zanim post ujrzy światło dzienne.

## CHECKLISTY DO SPRAWDZENIA

### A) CHECKLIST FORMALNY (dla wszystkich platform):

1. **HOOK NIE ZACZYNA SIĘ OD ŹRÓDŁA**
   - ❌ "Nowe badanie Nature pokazuje..."
   - ❌ "Według raportu McKinsey..."
   - ❌ "Właśnie przeczytałem, że..."
   - ✅ "Twój szef właśnie dostał email o AI. I teraz myśli o Tobie."
   - ✅ "Boisz się, że AI zabierze ci pracę? Ja też się bałem."

2. **JEST ELEMENT "TU I TERAZ"**
   - Polski kontekst (wybory, firmy, znane osoby)
   - Aktualność (sezon, wydarzenia)
   - Personalizacja ("Twój...", "Czy Ty...")

3. **ŹRÓDŁO JEST PODANE (ale nie na początku)**
   - Źródło musi być wspomniane
   - Ale NIE jako pierwsze zdanie
   - Dobre miejsce: po hooku, w środku

4. **BRAK WODOLEJSTWA**
   - Zero pustych frazesów
   - Zero korporacyjnej nowomowy
   - Każde zdanie musi nieść wartość

5. **UWAGI USERA UWZGLĘDNIONE**
   - Jeśli user podał kierunek → czy został użyty?
   - Priorytet uwag usera nad automatyczną analizą

6. **TON PASUJE DO PLATFORMY**
   - LinkedIn: profesjonalny, inspirujący, z refleksją
   - Facebook: bezpośredni, empatyczny, nieformalny
   - X/Twitter: ostry, punchy, ironiczny
   - Reels: energetyczny, autentyczny, wizualny

### B) CHECKLIST MERYTORYCZNY (KRYTYCZNY!):

7. **POPRAWNOŚĆ FAKTOGRAFICZNA**
   - Czy autor źródła jest poprawnie nazwany? (imię, nazwisko, afiliacja)
   - Czy uczelnia/firma jest prawidłowa? (Boston College ≠ Yale!)
   - Czy cytaty są przypisane właściwym osobom?
   - Czy liczby są dokładne?

   CZERWONA FLAGA: Przypisanie cytatu/afiliacji złej osobie = ODRZUĆ

8. **WYKORZYSTANIE ŹRÓDŁA**
   - Czy użyto cytatów ze źródła? (nie tylko parafrazy)
   - Czy wykorzystano konkretne osoby/historie? (Tyler, Josie, nie "student")
   - Czy są metafory/analogie z oryginału?
   - Czy post wnosi WARTOŚĆ PONAD streszczenie?

   CZERWONA FLAGA: Zero cytatów + zero konkretnych osób = post jest banalny

9. **WARTOŚĆ DODANA vs INPUT USERA**
   - Porównaj post z tym co user SAM już napisał
   - Czy post dodaje coś NOWEGO?
   - Czy nie jest tylko przeformatowaniem inputu usera?

   CZERWONA FLAGA: Post powtarza tylko to co user już napisał = ODRZUĆ

10. **KOMPLETNOŚĆ WYKORZYSTANIA NAJLEPSZYCH ELEMENTÓW**
    - Czy najlepsze cytaty ze źródła zostały użyte?
    - Czy kluczowe osoby/historie są wspomniane?
    - Co wartościowego pominięto (a mogło być użyte)?

### C) CHECKLIST PLATFORMOWY:

**LINKEDIN:**
- [ ] Brak "Jestem zaszczycony..."
- [ ] Brak "Zgadzasz się?" jako jedynego CTA
- [ ] Profesjonalny ale ludzki ton
- [ ] Długość 1000-3000 znaków

**FACEBOOK:**
- [ ] Nieformalny ton ("ja", "ty", "my")
- [ ] Emocjonalny hook
- [ ] Skrypt wideo ma sens i jest nagrywany
- [ ] Długość 800-2000 znaków

**X/TWITTER:**
- [ ] Max 280 znaków na tweet
- [ ] Brak hashtags (cringe na X)
- [ ] Ostry, punchy ton
- [ ] Żart nie jest wyjaśniany

**INSTAGRAM REELS:**
- [ ] Hook w pierwszych 3 sekundach
- [ ] Napisy na ekranie (dla 80% bez dźwięku)
- [ ] CTA (zapisz/obserwuj)
- [ ] Hashtagi 5-15

## FORMAT ODPOWIEDZI

```json
{
  "platform_results": {
    "linkedin": {
      "status": "OK|POPRAW|ODRZUĆ",
      "score": 8,
      "checks": {
        "hook_nie_od_zrodla": {"passed": true, "note": ""},
        "element_tu_i_teraz": {"passed": true, "note": "wybory PL"},
        "zrodlo_podane": {"passed": true, "note": "w 3 akapicie"},
        "brak_wodolejstwa": {"passed": false, "note": "zbyt wiele 'innowacyjny'"},
        "uwagi_usera": {"passed": true, "note": "kierunek użyty"},
        "ton_platformy": {"passed": true, "note": ""},
        "poprawnosc_faktograficzna": {
          "passed": false,
          "note": "BŁĄD: Autor to Carlo Rotella z Boston College, NIE 'profesor z Yale'"
        },
        "wykorzystanie_zrodla": {
          "passed": false,
          "note": "Zero cytatów z artykułu, zero konkretnych osób (Tyler, Josie pominięci)"
        },
        "wartosc_dodana": {
          "passed": false,
          "note": "Post powtarza tylko punkty z inputu usera, nie dodaje nic nowego"
        },
        "kompletnosc": {
          "passed": false,
          "note": "Pominięto: metaforę o skuterze, cytat 'Use it or lose it', historię Tylera"
        }
      },
      "issues": [
        "KRYTYCZNY: Błędna afiliacja autora (Yale zamiast Boston College)",
        "Brak cytatów ze źródła",
        "Pominięto historię Tylera która obala narrację o leniwej młodzieży"
      ],
      "suggestions": [
        "Popraw: Carlo Rotella, Boston College (nie Yale)",
        "Dodaj cytat: 'Class as workshop, not factory'",
        "Użyj historii Tylera: student SAM poprosił o naukę zadawania pytań"
      ],
      "niewykorzystane_elementy": [
        "'$5 a minute for college classes' - świetne zakotwiczenie",
        "'like joining the track team and doing your laps on an electric scooter' - metafora",
        "Maryanne Wolf - 'Use it or lose it' - ekspert od neuroplastyczności"
      ]
    },
    "facebook": { ... },
    "x_twitter": { ... },
    "instagram_reels": { ... }
  },
  "cross_check_zrodlo_vs_output": {
    "cytaty_ze_zrodla_w_postach": ["lista użytych cytatów"],
    "cytaty_pominiete": ["lista pominiętych wartościowych cytatów"],
    "osoby_wykorzystane": ["lista osób użytych w postach"],
    "osoby_pominiete": ["lista osób z artykułu które pominięto"],
    "bledy_faktograficzne": ["lista błędów: złe przypisania, złe afiliacje"],
    "ocena_wykorzystania_zrodla": "X/10"
  },
  "porownanie_z_inputem_usera": {
    "co_user_juz_napisal": ["lista punktów z inputu usera"],
    "co_dodaly_posty": ["lista nowych elementów"],
    "czy_jest_wartosc_dodana": true/false,
    "jezeli_nie_dlaczego": "..."
  },
  "overall_status": "OK|POPRAW|ODRZUĆ",
  "overall_score": 7.5,
  "critical_issues": [
    "FAKTOGRAFICZNY: Yale → Boston College",
    "MERYTORYCZNY: Zero cytatów ze źródła"
  ],
  "summary": "3/4 platform OK formalnie, ale WSZYSTKIE mają problemy merytoryczne: brak cytatów, błędna afiliacja, brak wartości dodanej ponad input usera."
}
```

## OCENA KOŃCOWA

- **OK** (8-10): Post gotowy do publikacji, merytorycznie solidny
- **POPRAW** (5-7): Wymaga zmian, ale fundament jest dobry
- **ODRZUĆ** (1-4): Błędy krytyczne lub brak wartości - przepisz od nowa

### AUTOMATYCZNE ODRZUCENIE (bez względu na formę):
- Błąd faktograficzny (złe nazwisko, uczelnia, przypisanie cytatu)
- Zero cytatów ze źródła + zero konkretnych osób
- Post jest tylko przeformatowaniem inputu usera bez wartości dodanej

## BĄDŹ BEZWZGLĘDNY

Lepiej złapać problem teraz niż po publikacji.
Jeśli coś jest "prawie OK" - to znaczy że NIE jest OK.
Szukaj aktywnie problemów, nie wymówek.

**PAMIĘTAJ:** Ładna forma przy pustej treści = ODRZUĆ.
Post który "dobrze wygląda" ale nie ma cytatów, ma błędy faktograficzne
i nie dodaje wartości ponad input usera = post banalny i niewarty publikacji.
"""

    def check_all(
        self,
        generated_posts: dict,
        user_direction: Optional[str] = None,
    ) -> QualityReport:
        """
        Sprawdza wszystkie wygenerowane posty.

        Args:
            generated_posts: Dict z postami per platforma
            user_direction: Kierunek podany przez usera

        Returns:
            QualityReport z wynikami
        """
        input_text = f"""## WYGENEROWANE POSTY DO SPRAWDZENIA

{json.dumps(generated_posts, ensure_ascii=False, indent=2)}

## KIERUNEK UŻYTKOWNIKA (jeśli podany)

{user_direction if user_direction else "Brak"}

Sprawdź każdą platformę według checklisty.
Bądź bezwzględny - lepiej znaleźć problem teraz.
"""

        messages = [
            {"role": "system", "content": self.prompt_template},
            {"role": "user", "content": input_text},
        ]

        response = self.client.chat(
            messages=messages,
            model_key=self.model_key,
            temperature=0.3,  # Niska dla precyzyjnej oceny
            max_tokens=4000,
        )

        return self._parse_response(response.content)

    def _parse_response(self, response: str) -> QualityReport:
        """Parsuje odpowiedź do QualityReport."""
        import re

        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response

            data = json.loads(json_str)

            platform_results = {}
            for platform, result in data.get("platform_results", {}).items():
                platform_results[platform] = QualityCheck(
                    platform=platform,
                    status=result.get("status", "POPRAW"),
                    score=result.get("score", 5),
                    checks=result.get("checks", {}),
                    issues=result.get("issues", []),
                    suggestions=result.get("suggestions", []),
                )

            return QualityReport(
                platform_results=platform_results,
                overall_status=data.get("overall_status", "POPRAW"),
                overall_score=data.get("overall_score", 5.0),
                critical_issues=data.get("critical_issues", []),
                summary=data.get("summary", ""),
            )

        except (json.JSONDecodeError, KeyError):
            return QualityReport(
                platform_results={},
                overall_status="BŁĄD",
                overall_score=0,
                critical_issues=["Nie udało się przeanalizować postów"],
                summary="Błąd parsowania odpowiedzi",
            )

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
            on_progress("Kontroluję jakość postów...")

        generated_posts = context.get("generated_posts", {}) if context else {}
        user_direction = context.get("user_direction") if context else None

        if not generated_posts:
            # Fallback - traktuj content jako pojedynczy post
            generated_posts = {"unknown": content}

        report = self.check_all(generated_posts, user_direction)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
            score=report.overall_score,
        )

    # ==========================================
    # TRYB SZLIF - ocena + poprawki
    # ==========================================

    def _get_polish_prompt(self) -> str:
        """Prompt dla trybu SZLIF."""
        return """# TRYB SZLIF - Ocena i poprawki tekstu

Jesteś bezwzględnym redaktorem. Użytkownik daje Ci GOTOWY tekst do oceny i poprawy.

## TWOJE ZADANIE

1. **OCEŃ** tekst (1-10)
2. **WSKAŻ** mocne strony i problemy
3. **ZAPROPONUJ** konkretne poprawki inline
4. **PRZEPISZ** ulepszoną wersję (OBOWIĄZKOWE!)
5. **DAJ** alternatywne hooki (OBOWIĄZKOWE - minimum 3!)

## KRYTERIA OCENY

### HOOK (pierwsze zdanie)
- Czy zatrzymuje scroll?
- Czy NIE zaczyna się od źródła ("Nowe badanie...")?
- Czy jest personalny ("Ty", "Twój")?

### STRUKTURA
- Czy jest jasny flow?
- Czy każde zdanie pracuje?
- Czy jest puenta/CTA na końcu?

### TON
- Czy naturalny (nie korporacyjny)?
- Czy pasuje do platformy?
- Czy jest autentyczny głos autora?

### TREŚĆ
- Czy jest konkret (liczby, przykłady)?
- Czy jest polski kontekst?
- Czy jest wartość dla czytelnika?

## ZASADY POPRAWIANIA

### ZACHOWAJ AUTENTYCZNOŚĆ
- **NIE zmieniaj autentycznych detali z historii** (nazwy, miejsca, konkrety)
- Jeśli autor pisze o "kurzych nóżkach" - zostaw kurze nóżki, nie zmieniaj na "pho"
- Jeśli autor pisze o konkretnej osobie "M." - zachowaj tę konwencję
- Twoje zadanie to ULEPSZYĆ przekaz, nie ZMIENIĆ historię

### CO MOŻESZ ZMIENIAĆ
- Interpunkcję i formatowanie
- Zbędne słowa i wodolejstwo
- Strukturę zdań (skracać, upraszyczać)
- Dodawać CTA na końcu
- Usuwać zbędne parentezy i wykrzykniki

### CZEGO NIE ZMIENIAJ
- Autentycznych detali z opowieści (nazwy, przedmioty, miejsca)
- Unikalnych metafor autora (to jego głos!)
- Tonu - tylko go wzmacniaj, nie zmieniaj

## FORMAT ODPOWIEDZI

**WAŻNE:** Pola `wersja_po_poprawkach` i `alternatywne_hooki` są OBOWIĄZKOWE!

```json
{
  "ocena": 7,
  "status": "POPRAW",
  "mocne_strony": [
    "Dobry hook - zatrzymuje scroll",
    "Oryginalna metafora",
    "Naturalny flow"
  ],
  "problemy": [
    {
      "problem": "Brak CTA na końcu",
      "gdzie": "Ostatni akapit",
      "wpływ": "Post się kończy, ale nie angażuje"
    },
    {
      "problem": "Zbędne parentezy osłabiają przekaz",
      "gdzie": "Środek tekstu",
      "wpływ": "Traci tempo"
    }
  ],
  "poprawki_inline": [
    {
      "oryginał": "Pomyślałem: mój Boże, przecież to jest niesamowite (!!!).",
      "poprawka": "Pomyślałem: to jest niesamowite.",
      "powód": "Siła w prostocie. Wykrzykniki osłabiają, nie wzmacniają."
    }
  ],
  "wersja_po_poprawkach": "PEŁNY TEKST PO WSZYSTKICH POPRAWKACH - złóż wszystkie poprawki w całość i przepisz cały tekst od początku do końca. To pole MUSI zawierać kompletny, gotowy do publikacji tekst.",
  "alternatywne_hooki": [
    "Alternatywny hook 1 - inna perspektywa",
    "Alternatywny hook 2 - bardziej prowokacyjny",
    "Alternatywny hook 3 - bardziej osobisty"
  ]
}
```

## SKALA OCEN

- **9-10 (OK)**: Publikuj od razu, ewentualnie drobne poprawki
- **7-8 (DROBNE POPRAWKI)**: Dobry tekst, wymaga kosmetyki
- **5-6 (POPRAW)**: Ma potencjał, wymaga pracy
- **1-4 (PRZEPISZ)**: Fundamentalne problemy

## PRZYKŁAD DOBREJ POPRAWKI

**ORYGINAŁ:**
"Zacząłem się zastanawiać, czy my wszyscy nie jesteśmy zbyt surowi dla halucynacji. Mamy obsesję na punkcie mapy i celu. A przecież te momenty, kiedy stajemy w nieoczekiwanym miejscu, patrząc na coś, czego nie planowaliśmy zobaczyć - to są te chwile, które w ostatecznym rozrachunku mogą nas skłonić do myślenia."

**POPRAWKA:**
"Czy nie jesteśmy zbyt surowi dla halucynacji? Mamy obsesję na punkcie mapy i celu. A może właśnie te momenty, gdy trafiamy nie tam gdzie chcieliśmy - prowadzą nas tam, gdzie powinniśmy?"

**POWÓD:** Krócej, mocniej, pytanie retoryczne na końcu zostaje w głowie.

## PAMIĘTAJ

1. **wersja_po_poprawkach** - MUSI być wypełnione pełnym tekstem!
2. **alternatywne_hooki** - MUSI zawierać minimum 3 propozycje!
3. Zachowaj autentyczne detale z historii autora
4. Każda poprawka ma uzasadnienie
"""

    def polish(
        self,
        text: str,
        platform: Optional[str] = None,
    ) -> PolishReport:
        """
        Tryb SZLIF - ocena i poprawki tekstu.

        Args:
            text: Tekst do oceny i poprawy
            platform: Opcjonalna platforma (wpływa na ocenę tonu)

        Returns:
            PolishReport z oceną i poprawkami
        """
        platform_context = ""
        if platform:
            platform_hints = {
                "linkedin": "LinkedIn - ton profesjonalny ale ludzki, długość 1000-3000 znaków",
                "facebook": "Facebook - ton nieformalny, empatyczny, długość 800-2000 znaków",
                "x_twitter": "X/Twitter - max 280 znaków, punchy, bez hashtags",
                "bluesky": "Bluesky - max 300 znaków, ostry ale mniej agresywny niż X",
                "threads": "Threads - max 500 znaków, cieplejszy ton",
                "instagram_reels": "Instagram Reels - tekst do kamery, 30-45s, energetyczny",
                "youtube_shorts": "YouTube Shorts - tekst do kamery, 45-60s, informacyjny",
            }
            platform_context = f"\n\nPLATFORMA: {platform_hints.get(platform, platform)}"

        input_text = f"""## TEKST DO OCENY I POPRAWY

```
{text}
```
{platform_context}

Oceń ten tekst i zaproponuj konkretne poprawki.
"""

        messages = [
            {"role": "system", "content": self._get_polish_prompt()},
            {"role": "user", "content": input_text},
        ]

        response = self.client.chat(
            messages=messages,
            model_key=self.model_key,
            temperature=0.4,
            max_tokens=4000,
        )

        return self._parse_polish_response(response.content, text)

    def _parse_polish_response(self, response: str, original_text: str) -> PolishReport:
        """Parsuje odpowiedź do PolishReport."""
        import re

        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response

            data = json.loads(json_str)

            return PolishReport(
                original_text=original_text,
                score=data.get("ocena", 5),
                status=data.get("status", "POPRAW"),
                strengths=data.get("mocne_strony", []),
                issues=data.get("problemy", []),
                inline_corrections=data.get("poprawki_inline", []),
                improved_version=data.get("wersja_po_poprawkach", ""),
                hook_alternatives=data.get("alternatywne_hooki", []),
            )

        except (json.JSONDecodeError, KeyError):
            return PolishReport(
                original_text=original_text,
                score=0,
                status="BŁĄD",
                strengths=[],
                issues=[{"problem": "Nie udało się przeanalizować tekstu"}],
                inline_corrections=[],
                improved_version="",
                hook_alternatives=[],
            )
