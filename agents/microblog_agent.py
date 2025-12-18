"""Agent Microblog - generuje post lub wątek dla X/Bluesky/Threads."""

import json
from dataclasses import dataclass
from typing import Optional, Literal

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient


# Limity znaków dla platform
PLATFORM_LIMITS = {
    "x_twitter": 280,
    "bluesky": 300,
    "threads": 500,
}

PLATFORM_NAMES = {
    "x_twitter": "X (Twitter)",
    "bluesky": "Bluesky",
    "threads": "Threads",
}


@dataclass
class MicroblogPost:
    """Wygenerowany post lub wątek."""
    platform: str
    main_post: str
    thread: list  # Opcjonalny wątek
    hook_variants: list  # Alternatywne wersje
    is_thread: bool
    total_posts: int
    character_count: int

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "main_post": self.main_post,
            "thread": self.thread,
            "hook_variants": self.hook_variants,
            "is_thread": self.is_thread,
            "total_posts": self.total_posts,
            "character_count": self.character_count,
        }


class MicroblogAgent(BaseAgent):
    """
    Agent Microblog - X/Bluesky/Threads.

    Tożsamość: Ostry obserwator
    - Punchy, bez tłumaczenia
    - Ironiczny, samoświadomy
    - News junkie, early adopter

    Obsługuje:
    - X (Twitter): 280 znaków
    - Bluesky: 300 znaków
    - Threads: 500 znaków

    Format: Post lub wątek
    """

    name = "microblog_agent"
    name_pl = "Agent Microblog"
    description = "Generuje post lub wątek dla X/Bluesky/Threads"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# AGENT MICROBLOG (X / Bluesky / Threads)

Jesteś ghostwriterem dla Marcina Majsawickiego na platformach microblogowych. Tu liczy się ostrość, dowcip i szybkość.

## TOŻSAMOŚĆ

**Kim jest Marcin na microblogach:**
- Ostry obserwator sceny AI
- Ktoś, kto widział wystarczająco dużo, żeby być cyniczny (ale konstruktywnie)
- Early adopter z dystansem do hype'u
- Dowcipny komentator

**Audytorium:**
- News junkies, early adopters
- Ludzie, którzy cenią dowcip i ostrość
- Szukają szybkiego "aha!" moment
- Nagradzają oryginalność i odwagę

## RÓŻNICE MIĘDZY PLATFORMAMI

### X (Twitter) - 280 znaków
- Najbardziej punchy
- Ironiczny, czasem cyniczny
- Zero hashtags (cringe)
- Prowokacyjny

### Bluesky - 300 znaków
- Trochę więcej miejsca
- Mniej agresywny ton niż X
- Bardziej "kultywowany" cynizm
- Można być bardziej refleksyjny

### Threads - 500 znaków
- Więcej miejsca na rozwinięcie
- Ton bliższy Instagram - cieplejszy
- Można dodać kontekst
- Mniej "edgy" niż X

## ZASADY

### FORMAT
- Pilnuj limitu znaków dla danej platformy
- Jeden post = jedna teza
- Wątek jeśli temat wymaga rozwinięcia

### TON
- Punchy - każde słowo musi pracować
- Ironiczny - ale nie złośliwy
- Samoświadomy - możesz się sam z siebie śmiać
- Bez tłumaczenia żartu - kto zrozumie, ten zrozumie

### TYPY POSTÓW

1. **OBSERWACJA**
   "Firmy mówią, że AI to przyszłość. Potem każą ci wypełnić 50-stronicowy formularz PDF."

2. **GORĄCA TEZA**
   "Hot take: Prompt engineering to nie zawód. To umiejętność, która za 2 lata będzie tak podstawowa jak Excel."

3. **PARADOKS**
   "Najbardziej przerażeni AI są ci, którzy jej nie używają. Najbardziej zrelaksowani - ci, którzy używają codziennie."

4. **PROWOKACJA**
   "Jeśli AI może zastąpić Twoją pracę, to może ta praca nie była taka wartościowa?"

5. **IRONIA**
   "AI za 10 lat: wszechpotężna superinteligencja
   AI dziś: 'Jako model językowy nie mogę ci powiedzieć jak ugotować jajko'"

### CZERWONE LINIE
- Długie, rozwlekłe posty
- Korporacyjna mowa
- Wyjaśniane żarty
- "Jako [tytuł], uważam że..."
- Hashtagi na X (na Threads można)

### WĄTEK

Jeśli temat wymaga rozwinięcia:
- Post 1: Hook (najważniejszy)
- Post 2-4: Rozwinięcie
- Post 5: Puenta

Zasady wątku:
- Każdy post musi działać samodzielnie
- Pierwszy post musi być na tyle mocny, że ludzie klikną "Show thread"
- Nie numeruj ("1/5") - to passé

## FORMAT ODPOWIEDZI

```json
{
  "platform": "x_twitter|bluesky|threads",
  "main_post": "Główny post (pilnuj limitu znaków!)",
  "is_thread": false,
  "thread": [],
  "hook_variants": [
    "Alternatywna wersja 1",
    "Alternatywna wersja 2",
    "Alternatywna wersja 3"
  ],
  "post_type": "obserwacja|gorąca_teza|paradoks|prowokacja|ironia"
}
```

Jeśli wątek:
```json
{
  "platform": "x_twitter",
  "main_post": "Pierwszy post wątku",
  "is_thread": true,
  "thread": [
    "Post 1 (hook)",
    "Post 2",
    "Post 3",
    "Post 4 (puenta)"
  ],
  "hook_variants": [...],
  "total_posts": 4
}
```

## WAŻNE

ZAWSZE sprawdź limit znaków dla platformy:
- X: max 280
- Bluesky: max 300
- Threads: max 500

Licz: spacje, znaki interpunkcyjne, emoji - wszystko.
Jeśli przekraczasz - skróć bezlitośnie.
"""

    def generate(
        self,
        input_package: dict,
        platform: Literal["x_twitter", "bluesky", "threads"] = "x_twitter",
        format_type: Literal["post", "thread"] = "post",
    ) -> MicroblogPost:
        """
        Generuje post lub wątek.

        Args:
            input_package: Pakiet z danymi od poprzednich agentów
            platform: Platforma docelowa (x_twitter, bluesky, threads)
            format_type: Format (post lub thread)

        Returns:
            MicroblogPost gotowy do publikacji
        """
        char_limit = PLATFORM_LIMITS.get(platform, 280)
        platform_name = PLATFORM_NAMES.get(platform, platform)

        input_text = f"""## PAKIET WEJŚCIOWY

{json.dumps(input_package, ensure_ascii=False, indent=2)}

## PARAMETRY

- Platforma: {platform_name}
- Limit znaków: {char_limit}
- Format: {"wątek" if format_type == "thread" else "pojedynczy post"}

Wygeneruj {"wątek" if format_type == "thread" else "post"} dla {platform_name}.
PAMIĘTAJ: max {char_limit} znaków na post!
Wybierz najostrzejszy, najbardziej pasujący kąt.
"""

        messages = [
            {"role": "system", "content": self.prompt_template},
            {"role": "user", "content": input_text},
        ]

        response = self.client.chat(
            messages=messages,
            model_key=self.model_key,
            temperature=0.8,
            max_tokens=2000,
        )

        return self._parse_response(response.content, platform, char_limit)

    def _parse_response(
        self,
        response: str,
        platform: str,
        char_limit: int
    ) -> MicroblogPost:
        """Parsuje odpowiedź do MicroblogPost."""
        import re

        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response

            data = json.loads(json_str)

            main_post = data.get("main_post", "")[:char_limit]
            thread = data.get("thread", [])
            thread = [t[:char_limit] for t in thread]  # Enforce limit na każdy
            is_thread = data.get("is_thread", len(thread) > 0)

            return MicroblogPost(
                platform=platform,
                main_post=main_post,
                thread=thread,
                hook_variants=data.get("hook_variants", []),
                is_thread=is_thread,
                total_posts=len(thread) if is_thread else 1,
                character_count=len(main_post),
            )

        except (json.JSONDecodeError, KeyError):
            # Fallback
            main_post = response[:char_limit]
            return MicroblogPost(
                platform=platform,
                main_post=main_post,
                thread=[],
                hook_variants=[],
                is_thread=False,
                total_posts=1,
                character_count=len(main_post),
            )

    def analyze(
        self,
        content: str,
        mode: str = "source",
        platform: str = "x_twitter",
        humor_dial: Optional[int] = None,
        context: Optional[dict] = None,
        on_progress=None,
    ) -> AgentResult:
        """Implementacja interfejsu BaseAgent."""
        platform_name = PLATFORM_NAMES.get(platform, platform)
        if on_progress:
            on_progress(f"Generuję post dla {platform_name}...")

        input_package = {
            "extracted_data": context.get("extracted_data", {}) if context else {},
            "resonance_report": context.get("resonance_report", {}) if context else {},
            "depth_report": context.get("depth_report", {}) if context else {},
            "user_notes": context.get("user_notes", "") if context else "",
        }

        if not input_package["extracted_data"]:
            input_package["raw_content"] = content

        format_type = context.get("format_type", "post") if context else "post"

        post = self.generate(input_package, platform, format_type)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=json.dumps(post.to_dict(), ensure_ascii=False, indent=2),
        )
