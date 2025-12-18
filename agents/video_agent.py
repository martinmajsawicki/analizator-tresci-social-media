"""Agent Video - generuje tekst do powiedzenia do kamery (Reels/Shorts)."""

import json
from dataclasses import dataclass
from typing import Optional, Literal

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient


PLATFORM_NAMES = {
    "instagram_reels": "Instagram Reels",
    "youtube_shorts": "YouTube Shorts",
}


@dataclass
class VideoScript:
    """Tekst do powiedzenia do kamery."""
    platform: str
    script: str  # Główny tekst do powiedzenia
    hook: str  # Pierwsze zdanie (0-3s)
    hook_variants: list  # Alternatywne hooki
    cta: str  # Call to action na koniec
    estimated_duration: str  # np. "30s", "45s", "60s"
    word_count: int

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "tekst_do_kamery": self.script,
            "hook": self.hook,
            "warianty_hooka": self.hook_variants,
            "cta": self.cta,
            "szacowany_czas": self.estimated_duration,
            "liczba_słów": self.word_count,
        }


class VideoAgent(BaseAgent):
    """
    Agent Video - Instagram Reels / YouTube Shorts.

    Generuje TYLKO tekst do powiedzenia do kamery.
    Bez timestampów, bez visual notes - prosta gadająca głowa.

    Długość: 30-60 sekund (~100-200 słów)
    """

    name = "video_agent"
    name_pl = "Agent Video"
    description = "Generuje tekst do powiedzenia do kamery (Reels/Shorts)"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# AGENT VIDEO (Reels / Shorts)

Generujesz TEKST DO POWIEDZENIA DO KAMERY. Nie skrypt z timestampami, nie scenariusz z ujęciami - tylko tekst który Marcin powie patrząc w kamerę.

## FORMAT WIDEO

To jest "gadająca głowa":
- Marcin patrzy w kamerę
- Mówi tekst naturalnie
- Czasem mina, wyglup, gestykulacja
- Ale zasadniczo: jedna osoba mówiąca do kamery

## STRUKTURA TEKSTU (30-60 sekund)

### HOOK (pierwsze 3 sekundy)
- Zatrzymaj scroll
- Mocne pierwsze zdanie
- NIE: "Cześć, dziś opowiem o..."
- TAK: "AI właśnie zrobiła coś, co powinno cię przerazić."

### TREŚĆ (20-50 sekund)
- 2-4 kluczowe punkty
- Napisane JAK MÓWISZ, nie jak piszesz
- Krótkie zdania
- Naturalne pauzy

### CTA (5 sekund)
- Co ma zrobić widz?
- "Obserwuj po więcej"
- "Napisz w komentarzu co myślisz"
- "Zapisz ten film"

## TON

- Energetyczny ale naturalny
- Bezpośredni - mówisz DO kogoś
- Autentyczny - jak do znajomego
- Pewny siebie ale nie arogancki

## ZASADY PISANIA

1. **Pisz jak mówisz**
   - Nie: "Należy zauważyć, że sztuczna inteligencja..."
   - Tak: "Słuchaj, AI właśnie zrobiła coś dziwnego..."

2. **Krótkie zdania**
   - Łatwiej powiedzieć
   - Łatwiej zapamiętać
   - Lepiej brzmi

3. **Naturalne przejścia**
   - "Ale to nie wszystko..."
   - "I teraz najlepsze..."
   - "Wiesz co jest w tym najgorsze?"

4. **Bez żargonu**
   - Tłumacz skomplikowane rzeczy prosto
   - Jeśli musisz użyć terminu - wyjaśnij

## DŁUGOŚĆ

- **Reels**: 30-45 sekund (~100-150 słów)
- **Shorts**: 45-60 sekund (~150-200 słów)

Tempo mówienia: ~150 słów/minutę

## FORMAT ODPOWIEDZI

```json
{
  "platform": "instagram_reels|youtube_shorts",
  "hook": "Pierwsze zdanie - to co zatrzymuje scroll",
  "tekst_do_kamery": "Pełny tekst do powiedzenia. Napisany naturalnie, jak mówisz. Krótkie zdania. Bez formatowania - jeden ciąg tekstu do przeczytania.",
  "cta": "Co widz ma zrobić na końcu",
  "warianty_hooka": [
    "Alternatywny hook 1",
    "Alternatywny hook 2",
    "Alternatywny hook 3"
  ],
  "szacowany_czas": "30s|45s|60s",
  "wskazówki": "Opcjonalne wskazówki dla nagrywającego"
}
```

## PRZYKŁAD

**Temat:** AI w rekrutacji odrzuca 75% CV

```json
{
  "platform": "instagram_reels",
  "hook": "Wysłałeś 50 CV i zero odpowiedzi? To nie Ty. To algorytm.",
  "tekst_do_kamery": "Wysłałeś 50 CV i zero odpowiedzi? To nie Ty. To algorytm. Nowe badanie pokazuje, że systemy ATS - to takie automaty które czytają CV - odrzucają 75% aplikacji. Zanim jakikolwiek człowiek je zobaczy. Dlaczego? Bo szukają słów kluczowych. Nie masz dokładnie tych słów co w ogłoszeniu? Out. Masz przerwę w CV? Out. Twoje doświadczenie może być świetne, ale jeśli robot nie znajdzie właściwych fraz - nawet się o tym nie dowiesz. Co możesz zrobić? Kopiuj słowa kluczowe z ogłoszenia. Dosłownie. I nie kombinuj z formatowaniem - prosty tekst, żadnych tabelek. Obserwuj po więcej takich tricków.",
  "cta": "Obserwuj po więcej takich tricków",
  "warianty_hooka": [
    "75% CV nigdy nie trafia do człowieka. Oto dlaczego.",
    "Twoje CV jest świetne. Ale robot tego nie widzi.",
    "Rekruter nie odrzucił Twojego CV. Algorytm to zrobił."
  ],
  "szacowany_czas": "45s",
  "wskazówki": "Mów energicznie, przy 'Out' możesz zrobić gest odrzucenia ręką"
}
```

## RÓŻNICE MIĘDZY PLATFORMAMI

### Instagram Reels
- Krótsze (30-45s)
- Można być bardziej casualowo
- Hashtagi w opisie (nie w tekście)

### YouTube Shorts
- Może być dłuższe (do 60s)
- Bardziej informacyjny ton
- Można więcej wyjaśniać
"""

    def generate(
        self,
        input_package: dict,
        platform: Literal["instagram_reels", "youtube_shorts"] = "instagram_reels",
    ) -> VideoScript:
        """
        Generuje tekst do kamery.

        Args:
            input_package: Pakiet z danymi od poprzednich agentów
            platform: Platforma docelowa (instagram_reels, youtube_shorts)

        Returns:
            VideoScript gotowy do nagrania
        """
        platform_name = PLATFORM_NAMES.get(platform, platform)

        # Sugerowana długość
        if platform == "youtube_shorts":
            length_hint = "45-60 sekund (~150-200 słów)"
        else:
            length_hint = "30-45 sekund (~100-150 słów)"

        input_text = f"""## PAKIET WEJŚCIOWY

{json.dumps(input_package, ensure_ascii=False, indent=2)}

## PARAMETRY

- Platforma: {platform_name}
- Sugerowana długość: {length_hint}

Wygeneruj tekst do powiedzenia do kamery.
Pamiętaj: to gadająca głowa - naturalny, mówiony tekst.
"""

        messages = [
            {"role": "system", "content": self.prompt_template},
            {"role": "user", "content": input_text},
        ]

        response = self.client.chat(
            messages=messages,
            model_key=self.model_key,
            temperature=0.7,
            max_tokens=1500,
        )

        return self._parse_response(response.content, platform)

    def _parse_response(self, response: str, platform: str) -> VideoScript:
        """Parsuje odpowiedź do VideoScript."""
        import re

        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response

            data = json.loads(json_str)

            script = data.get("tekst_do_kamery", "")
            word_count = len(script.split())

            # Oszacuj czas (150 słów/min)
            estimated_seconds = int(word_count / 150 * 60)
            if estimated_seconds <= 30:
                estimated_duration = "30s"
            elif estimated_seconds <= 45:
                estimated_duration = "45s"
            else:
                estimated_duration = "60s"

            return VideoScript(
                platform=platform,
                script=script,
                hook=data.get("hook", ""),
                hook_variants=data.get("warianty_hooka", []),
                cta=data.get("cta", ""),
                estimated_duration=data.get("szacowany_czas", estimated_duration),
                word_count=word_count,
            )

        except (json.JSONDecodeError, KeyError):
            # Fallback
            word_count = len(response.split())
            return VideoScript(
                platform=platform,
                script=response,
                hook="",
                hook_variants=[],
                cta="",
                estimated_duration="45s",
                word_count=word_count,
            )

    def analyze(
        self,
        content: str,
        mode: str = "source",
        platform: str = "instagram_reels",
        humor_dial: Optional[int] = None,
        context: Optional[dict] = None,
        on_progress=None,
    ) -> AgentResult:
        """Implementacja interfejsu BaseAgent."""
        platform_name = PLATFORM_NAMES.get(platform, platform)
        if on_progress:
            on_progress(f"Generuję tekst wideo dla {platform_name}...")

        input_package = {
            "extracted_data": context.get("extracted_data", {}) if context else {},
            "resonance_report": context.get("resonance_report", {}) if context else {},
            "depth_report": context.get("depth_report", {}) if context else {},
            "user_notes": context.get("user_notes", "") if context else "",
        }

        if not input_package["extracted_data"]:
            input_package["raw_content"] = content

        script = self.generate(input_package, platform)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=json.dumps(script.to_dict(), ensure_ascii=False, indent=2),
        )
