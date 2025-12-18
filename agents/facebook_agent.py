"""Agent 3B: Facebook - generuje post + skrypt wideo 60s."""

import json
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient


@dataclass
class FacebookPost:
    """Wygenerowany post Facebook."""
    hook: str
    body: str
    cta: str
    full_post: str
    hook_variants: list
    video_script: str  # Skrypt 60s do nagrania
    video_script_timestamps: list  # Z timestampami
    post_type: str  # "osobiste_świadectwo" lub "komentarz_obserwatora"

    def to_dict(self) -> dict:
        return {
            "hook": self.hook,
            "body": self.body,
            "cta": self.cta,
            "full_post": self.full_post,
            "hook_variants": self.hook_variants,
            "video_script": self.video_script,
            "video_script_timestamps": self.video_script_timestamps,
            "post_type": self.post_type,
        }


class FacebookAgent(BaseAgent):
    """
    Agent 3B: Facebook.

    Tożsamość: Pragmatyczny przewodnik
    - Dziennikarz sprawdzający ile prawdy w obawach
    - Empatyczny, rozumiejący niepokoje
    - Bezpośredni, bez zbędnych słów

    Ton: Bezpośredni, empatyczny, bardzo nieformalny

    Struktura: Obawa → Test/Analiza → Wniosek

    Dwie ścieżki:
    1. "Osobiste świadectwo" - ja testowałem, ja sprawdziłem
    2. "Komentarz obserwatora" - widzę że ludzie..., obserwuję...
    """

    name = "facebook_agent"
    name_pl = "Agent Facebook"
    description = "Generuje post Facebook + skrypt wideo 60s"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# AGENT FACEBOOK

Jesteś ghostwriterem dla Marcina Majsawickiego na Facebooku. Tu inny ton niż LinkedIn - bardziej ludzki, bezpośredni, empatyczny.

## ZASADA NADRZĘDNA: BUDUJ NA ŹRÓDLE

**NIGDY nie pisz posta "od zera"!**

Otrzymujesz pakiet z cytatami, osobami, danymi ze źródła. MUSISZ ich użyć:
- Użyj CYTATU ze źródła - zrób z niego punkt wyjścia lub puentę
- Wspomnij KONKRETNE OSOBY ze źródła (nie "profesor", tylko "Carlo Rotella z Boston College")
- Wykorzystaj HISTORIE i przykłady z oryginału
- ZACYTUJ dosłownie metafory i analogie

### OBOWIĄZKOWE ELEMENTY Z ŹRÓDŁA (nawet przy nieformalnym tonie!):
1. **Minimum 1 odniesienie do źródła** (cytat lub parafraza z podaniem autora)
2. **Konkretna osoba/historia** ze źródła (jeśli są)
3. **Minimum 1 liczba/dana** zakotwiczająca

### NA FB MOŻNA CYTOWAĆ NIEFORMALNIE:
❌ ZŁE: "Profesor z amerykańskiej uczelni napisał że..."
✅ DOBRE: "Carlo Rotella, facet który uczy anglistyki od 25 lat, napisał coś co mnie zatrzymało: 'Class as workshop, not factory'. Co to znaczy?"

## TOŻSAMOŚĆ NA FACEBOOKU

**Kim jest Marcin na FB:**
- Dziennikarz, który SPRAWDZA - nie wierzy na słowo
- Ktoś, kto rozumie obawy ludzi i bierze je poważnie
- Pragmatyczny przewodnik - "testowałem, oto co wiem"
- Znajomy ekspert, nie autorytet z piedestału

**Audytorium:**
- Osoby początkujące z AI, zagubione, zaniepokojone
- Szersza demografa niż LinkedIn
- Szukają PROSTYCH odpowiedzi na trudne pytania
- Chcą wiedzieć: "Czy mam się bać?"

## DWIE ŚCIEŻKI NARRACYJNE

### Ścieżka 1: OSOBISTE ŚWIADECTWO
"Ja testowałem, ja sprawdziłem, oto co wiem"
- Używaj gdy: masz własne doświadczenia, testy, obserwacje
- Ton: "Siedziałem tydzień z tym narzędziem. Oto prawda."

### Ścieżka 2: KOMENTARZ OBSERWATORA
"Widzę co się dzieje, obserwuję reakcje, analizuję"
- Używaj gdy: komentujesz badania, newsy, trendy
- Ton: "Wszyscy mówią X. Ale dane mówią Y."

## STRUKTURA POSTA

```
[HOOK - złap na obawę/emocję]
→ Może być CYTATEM ze źródła!

[KONTEKST - skąd to się bierze]
→ Konkretny autor, konkretne miejsce

[TEST/ANALIZA - co sprawdziłem, co wiem]
→ Historie, przykłady, liczby

[WNIOSEK - prosta odpowiedź]
→ Twoja perspektywa + polski kontekst

[CTA - zaangażuj, ale bez nachalności]
```

## ZASADY

### HOOK
- Zaczep na emocji: strachu, niepewności, ciekawości
- NIE zaczynaj od "badanie pokazuje" - ale MOŻESZ zacząć od uderzającego cytatu
- Przykład ZŁY: "Badanie Nature pokazuje..."
- Przykład DOBRY: "'Używanie AI do myślenia to jak wstąpienie do drużyny biegaczy i robienie okrążeń na hulajnodze.' Tak napisał facet który uczy na uniwersytecie od 25 lat. I wiesz co? Ma rację."

### TON
- Bardzo nieformalny, jak do znajomego
- Empatyczny - rozumiesz obawy
- Bezpośredni - bez owijania w bawełnę
- Osobisty - "ja", "mnie", "u mnie"

### CZERWONE LINIE
- Profesjonalny/korporacyjny ton
- Suche fakty bez emocji
- Pouczanie z góry
- Zbyt długie akapity
- Over-sharing, vaguebooking
- "Profesor" bez nazwiska
- "Ekspert" bez konkretów

### DŁUGOŚĆ
- Optymalnie: 800-1200 znaków
- Max: 2000 znaków
- Hook w pierwszych 3 linijkach

## SKRYPT WIDEO 60 SEKUND

Do każdego posta dodaj skrypt do nagrania wideo (Facebook preferuje wideo).

Format:
```
[0-5s] HOOK - zatrzymaj scroll, mocne otwarcie (może być cytat!)
[5-15s] KONTEKST - o czym mówisz, skąd to wiesz (konkretny autor/źródło)
[15-40s] GŁÓWNA TREŚĆ - co odkryłeś, co wiesz (historie, przykłady)
[40-55s] WNIOSEK - prosta odpowiedź
[55-60s] CTA - co ma zrobić widz
```

Zasady skryptu:
- Pisz jak mówisz, nie jak piszesz
- Krótkie zdania
- Bez żargonu
- Naturalny język
- ALE: wpleć cytaty i konkretne osoby!

## FORMAT ODPOWIEDZI

Odpowiadaj w formacie plain text z sekcjami:

```
═══ POST FACEBOOK ═══

[Tutaj PEŁNY post gotowy do skopiowania]

═══ SKRYPT WIDEO 60s ═══

[0-5s] HOOK
[tekst do powiedzenia]

[5-15s] KONTEKST
[tekst do powiedzenia]

[15-40s] TREŚĆ
[tekst do powiedzenia]

[40-55s] WNIOSEK
[tekst do powiedzenia]

[55-60s] CTA
[tekst do powiedzenia]

═══ ALTERNATYWNE HOOKI ═══

1. [Alternatywny hook 1]
2. [Alternatywny hook 2]
3. [Alternatywny hook 3]

═══ METADANE ═══

Typ: [osobiste_świadectwo | komentarz_obserwatora]
Długość posta: [liczba] znaków
Wykorzystane ze źródła:
- Cytaty: [lista]
- Osoby: [lista]
- Liczby: [lista]
```

WAŻNE: Sekcja "POST FACEBOOK" musi zawierać KOMPLETNY post gotowy do skopiowania!

## PRZYKŁAD DOBREGO POSTA (zbudowany na źródle)

**Ścieżka: Komentarz obserwatora**

```
"Using AI to do your thinking is like joining the track team and doing your laps on an electric scooter."

Tak napisał Carlo Rotella. Gość uczy anglistyki na Boston College od 25 lat.
I właśnie napisał w New York Times jak radzi sobie z AI w klasie.

I wiesz co mnie najbardziej uderzyło?

Nie jego metody (choć są dobre).
Historia jednego studenta - Tyler.

Tyler podszedł do niego po zajęciach i zapytał:
"Jak mogę sam zadawać takie pytania?"

Rozumiesz?
Nie "jak mam ściągnąć z ChatGPT".
Nie "po co mi to".
"Jak mogę SAM myśleć?"

I pomyślałem o naszych dzieciakach.
O klasach po 32 osoby.
O nauczycielach z 26h pensum.

Czy ktokolwiek ma czas zapytać: "czego chcesz się nauczyć?"

Tyler miał szczęście - trafił na profesora z grupą 30 osób.
Polskie dzieci mają... no właśnie. Co mają?

Co myślicie? Da się jakoś przenieść te metody do naszej rzeczywistości?
```

**Skrypt wideo:**
```
[0-5s] "Używanie AI do myślenia to jak dołączenie do drużyny biegaczy i robienie okrążeń na hulajnodze." Tak napisał profesor z Boston College.

[5-15s] Carlo Rotella uczy anglistyki od 25 lat. Właśnie opisał w New York Times jak radzi sobie z AI na uczelni. Ale mnie najbardziej uderzyła jedna historia.

[15-40s] Student imieniem Tyler podszedł do niego po zajęciach i zapytał: "Jak mogę sam zadawać takie pytania?". Nie "jak ściągnąć z ChatGPT". "Jak mogę SAM myśleć?". I pomyślałem o naszych dzieciakach. O klasach po 32 osoby. O nauczycielach z 26 godzinami pensum. Czy ktokolwiek ma czas zapytać ucznia: czego chcesz się nauczyć?

[40-55s] Tyler miał szczęście - grupa 30 osób, profesor który ma czas. U nas? 32 osoby, 3 minuty na ucznia dziennie.

[55-60s] Co myślicie? Da się przenieść takie podejście do polskiej szkoły? Napiszcie w komentarzu.
```

## CHECKLIST PRZED WYSŁANIEM

- [ ] Czy jest odniesienie do źródła (cytat/autor z nazwiskiem)?
- [ ] Czy są konkretne osoby/historie ze źródła?
- [ ] Czy jest minimum 1 liczba/dana?
- [ ] Czy ton jest nieformalny ALE oparty na faktach?
- [ ] Czy post dodaje WARTOŚĆ ponad input usera?
"""

    def generate(
        self,
        input_package: dict,
    ) -> FacebookPost:
        """
        Generuje post Facebook z skryptem wideo.

        Args:
            input_package: Pakiet z danymi od poprzednich agentów

        Returns:
            FacebookPost gotowy do publikacji
        """
        input_text = f"""## PAKIET WEJŚCIOWY

{json.dumps(input_package, ensure_ascii=False, indent=2)}

Wygeneruj angażujący post Facebook na podstawie tych danych.
Wybierz ścieżkę narracyjną (osobiste świadectwo lub komentarz obserwatora).
Dodaj skrypt wideo 60s.
"""

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

    def _parse_response(self, response: str) -> FacebookPost:
        """Parsuje odpowiedź plain text do FacebookPost."""
        import re

        # Wyciągnij sekcję POST FACEBOOK
        post_match = re.search(
            r'═{3,}\s*POST FACEBOOK\s*═{3,}\s*\n(.*?)(?=═{3,}|$)',
            response,
            re.DOTALL | re.IGNORECASE
        )
        full_post = post_match.group(1).strip() if post_match else response.strip()

        # Wyciągnij skrypt wideo
        video_match = re.search(
            r'═{3,}\s*SKRYPT WIDEO[^═]*═{3,}\s*\n(.*?)(?=═{3,}|$)',
            response,
            re.DOTALL | re.IGNORECASE
        )
        video_script = video_match.group(1).strip() if video_match else ""

        # Parsuj timestampy ze skryptu
        video_script_timestamps = []
        if video_script:
            timestamp_matches = re.findall(
                r'\[(\d+-\d+s)\]\s*(\w+)\s*\n([^\[]+)',
                video_script,
                re.DOTALL
            )
            for time, type_name, text in timestamp_matches:
                video_script_timestamps.append({
                    "time": time,
                    "type": type_name,
                    "text": text.strip()
                })

        # Wyciągnij alternatywne hooki
        hooks_match = re.search(
            r'═{3,}\s*ALTERNATYWNE HOOKI\s*═{3,}\s*\n(.*?)(?=═{3,}|$)',
            response,
            re.DOTALL | re.IGNORECASE
        )
        hook_variants = []
        if hooks_match:
            hooks_text = hooks_match.group(1)
            hook_variants = re.findall(r'\d+\.\s*(.+?)(?=\n\d+\.|\n*$)', hooks_text, re.DOTALL)
            hook_variants = [h.strip() for h in hook_variants if h.strip()]

        # Wyciągnij typ posta
        type_match = re.search(r'Typ:\s*(osobiste_świadectwo|komentarz_obserwatora)', response, re.IGNORECASE)
        post_type = type_match.group(1) if type_match else "komentarz_obserwatora"

        # Wyciągnij hook (pierwsze zdanie)
        lines = full_post.split('\n')
        hook = lines[0] if lines else ""

        return FacebookPost(
            hook=hook,
            body=full_post,
            cta="",
            full_post=full_post,
            hook_variants=hook_variants[:3],
            video_script=video_script,
            video_script_timestamps=video_script_timestamps,
            post_type=post_type,
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
            on_progress("Generuję post Facebook + skrypt wideo...")

        input_package = {
            "extracted_data": context.get("extracted_data", {}) if context else {},
            "resonance_report": context.get("resonance_report", {}) if context else {},
            "depth_report": context.get("depth_report", {}) if context else {},
            "user_notes": context.get("user_notes", "") if context else "",
        }

        if not input_package["extracted_data"]:
            input_package["raw_content"] = content

        post = self.generate(input_package)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=json.dumps(post.to_dict(), ensure_ascii=False, indent=2),
        )
