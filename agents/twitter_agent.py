"""Agent 3C: X/Twitter - generuje tweet lub wątek."""

import json
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient


@dataclass
class TwitterPost:
    """Wygenerowany tweet/wątek."""
    main_tweet: str  # Max 280 znaków
    thread: list  # Opcjonalny wątek
    hook_variants: list  # Alternatywne wersje
    is_thread: bool
    total_tweets: int

    def to_dict(self) -> dict:
        return {
            "main_tweet": self.main_tweet,
            "thread": self.thread,
            "hook_variants": self.hook_variants,
            "is_thread": self.is_thread,
            "total_tweets": self.total_tweets,
            "character_count": len(self.main_tweet),
        }


class TwitterAgent(BaseAgent):
    """
    Agent 3C: X/Twitter.

    Tożsamość: Ostry obserwator
    - Punchy, bez tłumaczenia
    - Ironiczny, samoświadomy
    - News junkie, early adopter

    Ton: Ostry, dowcipny, ironiczny

    Struktura: Jedna teza (max 280) lub wątek
    """

    name = "twitter_agent"
    name_pl = "Agent X/Twitter"
    description = "Generuje tweet lub wątek - ostry, punchy, bez zbędnych słów"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# AGENT X/TWITTER

Jesteś ghostwriterem dla Marcina Majsawickiego na X (Twitter). Tu liczy się ostrość, dowcip i szybkość.

## TOŻSAMOŚĆ NA X

**Kim jest Marcin na X:**
- Ostry obserwator sceny AI
- Ktoś, kto widział wystarczająco dużo, żeby być cyniczny (ale konstruktywnie)
- Early adopter z dystansem do hype'u
- Dowcipny komentator

**Audytorium:**
- News junkies, early adopters
- Ludzie, którzy cenią dowcip i ostrość
- Szukają szybkiego "aha!" moment
- Nagradzają oryginalność i odwagę

## ZASADY TWEETA

### FORMAT
- Max 280 znaków (BEZWZGLĘDNIE)
- Jeden tweet = jedna teza
- Albo wątek jeśli temat wymaga rozwinięcia

### TON
- Punchy - każde słowo musi pracować
- Ironiczny - ale nie złośliwy
- Samoświadomy - możesz się sam z siebie śmiać
- Bez tłumaczenia żartu - kto zrozumie, ten zrozumie

### TYPY TWEETÓW

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
- Długie, rozwlekłe tweety
- Korporacyjna mowa (natychmiastowy unfollow)
- Wyjaśniane żarty (jeśli musisz wyjaśnić, usuń)
- "Jako [tytuł], uważam że..."
- Lekcje w stylu LinkedIn
- Hashtagi (na X to cringe)

### WĄTEK (opcjonalny)
Jeśli temat wymaga rozwinięcia:
- Tweet 1: Hook (najważniejszy)
- Tweet 2-4: Rozwinięcie
- Tweet 5: Puenta

Zasady wątku:
- Każdy tweet musi działać samodzielnie
- Pierwszy tweet musi być na tyle mocny, że ludzie klikną "Show thread"
- Nie numeruj ("1/5") - to passé

## FORMAT ODPOWIEDZI

Odpowiadaj w formacie plain text z sekcjami:

**Dla pojedynczego tweeta:**
```
═══ TWEET ═══

[Tutaj tweet - max 280 znaków!]

═══ ALTERNATYWNE WERSJE ═══

1. [Alternatywna wersja 1]
2. [Alternatywna wersja 2]
3. [Alternatywna wersja 3]

═══ METADANE ═══

Typ: [obserwacja | gorąca_teza | paradoks | prowokacja | ironia]
Znaków: [liczba]/280
```

**Dla wątku:**
```
═══ WĄTEK ═══

[Tweet 1 - hook]

---

[Tweet 2]

---

[Tweet 3]

---

[Tweet 4 - puenta]

═══ ALTERNATYWNE HOOKI ═══

1. [Alternatywny hook 1]
2. [Alternatywny hook 2]

═══ METADANE ═══

Typ: wątek
Tweetów: [liczba]
```

WAŻNE: Każdy tweet MUSI mieć max 280 znaków!

## PRZYKŁADY DOBRYCH TWEETÓW

**Obserwacja:**
"Najbardziej ironiczne w dyskusji o AI jest to, że ludzie piszą 2000-słowne artykuły tłumacząc, dlaczego AI nigdy nie będzie umieć pisać."

**Gorąca teza:**
"Większość ludzi boi się nie tego, że AI zabierze im pracę. Boi się, że AI pokaże, jak mało tej pracy było potrzebne."

**Paradoks:**
"Im więcej narzędzi AI do produktywności, tym mniej czasu. Curious."

**Prowokacja:**
"Jeśli Twoja 'kreatywna praca' składa się z wklejania jednego tekstu w drugi - mam złe wieści."

**Ironia:**
"GPT-4: rozwiązuje olimpiady matematyczne
Też GPT-4: 'przepraszam, nie mogę policzyć ile to 7+8'"

## LICZ ZNAKI

ZAWSZE upewnij się, że tweet ma max 280 znaków.
Licz: spacje, znaki interpunkcyjne, emoji - wszystko.
Jeśli przekraczasz - skróć bezlitośnie.
"""

    def generate(
        self,
        input_package: dict,
    ) -> TwitterPost:
        """
        Generuje tweet lub wątek.

        Args:
            input_package: Pakiet z danymi od poprzednich agentów

        Returns:
            TwitterPost gotowy do publikacji
        """
        input_text = f"""## PAKIET WEJŚCIOWY

{json.dumps(input_package, ensure_ascii=False, indent=2)}

Wygeneruj tweet lub wątek na podstawie tych danych.
PAMIĘTAJ: max 280 znaków na tweet!
Wybierz najostrzejszy, najbardziej "twitterowy" kąt.
"""

        messages = [
            {"role": "system", "content": self.prompt_template},
            {"role": "user", "content": input_text},
        ]

        response = self.client.chat(
            messages=messages,
            model_key=self.model_key,
            temperature=0.8,  # Wyższa dla kreatywności
            max_tokens=1500,
        )

        return self._parse_response(response.content)

    def _parse_response(self, response: str) -> TwitterPost:
        """Parsuje odpowiedź plain text do TwitterPost."""
        import re

        # Sprawdź czy to wątek czy pojedynczy tweet
        is_thread = '═══ WĄTEK ═══' in response or '═══ WATEK ═══' in response

        if is_thread:
            # Wyciągnij wątek
            thread_match = re.search(
                r'═{3,}\s*W[AĄ]TEK\s*═{3,}\s*\n(.*?)(?=═{3,}|$)',
                response,
                re.DOTALL | re.IGNORECASE
            )
            thread_content = thread_match.group(1).strip() if thread_match else ""

            # Podziel na tweety po separatorze ---
            tweets = [t.strip() for t in re.split(r'\n-{3,}\n', thread_content) if t.strip()]
            tweets = [t[:280] for t in tweets]  # Enforce limit

            main_tweet = tweets[0] if tweets else ""
            thread = tweets
        else:
            # Pojedynczy tweet
            tweet_match = re.search(
                r'═{3,}\s*TWEET\s*═{3,}\s*\n(.*?)(?=═{3,}|$)',
                response,
                re.DOTALL | re.IGNORECASE
            )
            main_tweet = tweet_match.group(1).strip()[:280] if tweet_match else response.strip()[:280]
            thread = []

        # Wyciągnij alternatywne wersje/hooki
        variants_match = re.search(
            r'═{3,}\s*ALTERNATYWNE[^═]*═{3,}\s*\n(.*?)(?=═{3,}|$)',
            response,
            re.DOTALL | re.IGNORECASE
        )
        hook_variants = []
        if variants_match:
            variants_text = variants_match.group(1)
            hook_variants = re.findall(r'\d+\.\s*(.+?)(?=\n\d+\.|\n*$)', variants_text, re.DOTALL)
            hook_variants = [h.strip()[:280] for h in hook_variants if h.strip()]

        return TwitterPost(
            main_tweet=main_tweet,
            thread=thread,
            hook_variants=hook_variants[:3],
            is_thread=is_thread,
            total_tweets=len(thread) if is_thread else 1,
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
            on_progress("Generuję tweet...")

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
