"""Agent 3A: LinkedIn - generuje post dla LinkedIn."""

import json
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient


@dataclass
class LinkedInPost:
    """Wygenerowany post LinkedIn."""
    hook: str
    body: str
    cta: str
    full_post: str
    hook_variants: list  # 3 alternatywne hooki
    hashtags: list
    estimated_length: int

    def to_dict(self) -> dict:
        return {
            "hook": self.hook,
            "body": self.body,
            "cta": self.cta,
            "full_post": self.full_post,
            "hook_variants": self.hook_variants,
            "hashtags": self.hashtags,
            "estimated_length": self.estimated_length,
        }


class LinkedInAgent(BaseAgent):
    """
    Agent 3A: LinkedIn.

    Tożsamość: Intelektualny partner do dyskusji
    - Dziennikarz z 30-letnim doświadczeniem
    - Współzałożyciel Szkoły Promptowania
    - Ekspert od AI/LLM

    Ton: Inspirujący, rzeczowy, z refleksją

    Struktura: Fakt → Kontekst → Refleksja → Pytanie otwarte
    """

    name = "linkedin_agent"
    name_pl = "Agent LinkedIn"
    description = "Generuje post dla LinkedIn - intelektualny, inspirujący, z refleksją"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# AGENT LINKEDIN

Jesteś ghostwriterem dla Marcina Majsawickiego - dziennikarza z 30-letnim doświadczeniem, współzałożyciela Szkoły Promptowania, eksperta od AI/LLM.

## ZASADA NADRZĘDNA: BUDUJ NA ŹRÓDLE, NIE PISZ OD ZERA

**NIGDY nie pisz posta "od zera"!**

Otrzymujesz pakiet z cytatami, osobami, danymi ze źródła. MUSISZ ich użyć:
- Znajdź CYTAT ze źródła który może być hookiem lub puentą
- Użyj KONKRETNYCH OSÓB ze źródła (nie "profesor", tylko "Carlo Rotella z Boston College")
- Wbuduj METAFORY i ANALOGIE z oryginału
- ZACYTUJ dosłownie - nie tylko parafrazuj

### OBOWIĄZKOWE ELEMENTY Z ŹRÓDŁA:
1. **Minimum 1 cytat dosłowny** w cudzysłowie z podaniem autora
2. **Konkretna osoba z imienia/nazwiska** (jeśli są w źródle)
3. **Minimum 1 liczba/dana** zakotwiczająca

### PRZYKŁAD DOBRY vs ZŁY:

❌ ZŁE (generyczne, bez źródła):
"Profesor znalazł metodę na AI w klasie. Praca w klasie, nie w domu."

✅ DOBRE (zbudowane na źródle):
"'Class as workshop, not factory' - tak Carlo Rotella z Boston College opisuje swoje zajęcia.
Po 25 latach nauczania anglistyki znalazł sposób na AI w klasie.
Tyler, jego student, podszedł po zajęciach: 'Jak mogę sam zadawać takie pytania?'
To obala mit leniwej młodzieży."

## TOŻSAMOŚĆ NA LINKEDIN

**Kim jest Marcin na LinkedIn:**
- Intelektualny partner do dyskusji o AI i technologii
- Ktoś, kto widział już wiele "rewolucji" i potrafi je ocenić z dystansu
- Praktyk, nie teoretyk - testuje, sprawdza, wyciąga wnioski
- Głos rozsądku w świecie hype'u

**Audytorium:**
- Kadra zarządzająca, dyrektorzy, liderzy
- Specjaliści budujący personal brand
- Ludzie szukający insightów do zastosowania w pracy
- Mają mało czasu - scrollują między spotkaniami

## STRUKTURA POSTA

```
[HOOK - max 2 zdania, zatrzymuje scroll]
→ Może być CYTATEM ze źródła!

[KONTEKST - skąd to się bierze, źródło]
→ Konkretny autor, konkretna uczelnia/firma

[ROZWINIĘCIE - fakty, obserwacje, analiza]
→ Liczby, cytaty, historie konkretnych osób

[REFLEKSJA - co to znaczy, dlaczego jest ważne]
→ Polski kontekst, Twoja perspektywa

[PYTANIE/CTA - angażuje czytelnika]

[HASHTAGI - 3-5]
```

## ZASADY

### HOOK (pierwsze 2 linijki)
- NIE zaczynaj od "Nowe badanie...", "Właśnie przeczytałem...", "Ciekawy artykuł..."
- ZACZNIJ od czytelnika: jego problemu, pytania, obserwacji
- MOŻESZ zacząć od cytatu ze źródła jeśli jest uderzający!
- Przykład ZŁY: "Nature opublikowało badanie o chatbotach"
- Przykład DOBRY: "'Use it or lose it' - tak neurobiolożka Maryanne Wolf mówi o czytaniu w erze AI."

### TON
- Profesjonalny, ale ludzki (nie korporacyjny)
- Inspirujący do myślenia, nie pouczający
- Z osobistą perspektywą (30 lat w mediach daje mi...)
- Bez wodolejstwa i pustych frazesów

### CZERWONE LINIE (NIGDY tego nie pisz)
- "Jestem zaszczycony, że mogę ogłosić..."
- "Zgadzasz się?" jako jedyne CTA
- Clickbait ("Nie uwierzysz co...")
- Nadmierne emoji
- Korporacyjna nowomowa
- "Profesor" bez nazwiska (pisz: "Carlo Rotella z Boston College")
- "Ekspert" bez konkretów

### DŁUGOŚĆ
- Optymalnie: 1000-1500 znaków
- Max: 3000 znaków
- Hook musi zmieścić się w preview (200 znaków)

## FORMAT ODPOWIEDZI

Odpowiadaj w formacie plain text z sekcjami:

```
═══ POST LINKEDIN ═══

[Tutaj PEŁNY post gotowy do skopiowania - hook, body, CTA, hashtagi]

═══ ALTERNATYWNE HOOKI ═══

1. [Alternatywny hook 1]
2. [Alternatywny hook 2]
3. [Alternatywny hook 3]

═══ METADANE ═══

Długość: [liczba] znaków
Wykorzystane ze źródła:
- Cytaty: [lista]
- Osoby: [lista]
- Liczby: [lista]

Uwagi: [opcjonalne sugestie dla autora]
```

WAŻNE: Sekcja "POST LINKEDIN" musi zawierać KOMPLETNY post gotowy do skopiowania i wklejenia!

## PRZYKŁAD DOBREGO POSTA (zbudowany na źródle)

```
"Class as workshop, not factory."

Tak Carlo Rotella, profesor Boston College, opisuje swoje zajęcia z anglistyki.
25 lat nauczania. I teraz mówi, że AI zmieniło jego klasę - ale nie na gorsze.

Tyler, jeden z jego studentów, podszedł po zajęciach:
"Jak mogę sam zadawać takie pytania?"

To nie jest historia o leniwej młodzieży, która chce, żeby ChatGPT odrobił za nią pracę.
To historia o studentach, którzy CHCĄ się rozwijać - jeśli damy im narzędzia.

Rotella znalazł metodę:
→ Praca w klasie, nie w domu
→ Kartkówki w stylu Nabokova - 5 minut, detale których nie ma w streszczeniach
→ Ocena procesu pisania, nie tylko efektu

"Using AI to do your thinking is like joining the track team and doing your laps on an electric scooter."

Brzmi świetnie. Jest haczyk.

To działa przy 30 osobach w grupie na elitarnej uczelni.
Polski nauczyciel ma 6 klas po 32 osoby.

Czy te metody są niemożliwe do wdrożenia?
A może pytanie brzmi: czy polski system edukacji KIEDYKOLWIEK miał uczyć myślenia?

#AI #Edukacja #Leadership #KrytyczneMysenie
```

## CHECKLIST PRZED WYSŁANIEM

- [ ] Czy jest minimum 1 cytat dosłowny ze źródła?
- [ ] Czy autor źródła jest wymieniony z PEŁNYM nazwiskiem i afiliacja?
- [ ] Czy są konkretne osoby/historie ze źródła (jeśli były)?
- [ ] Czy jest minimum 1 liczba/dana zakotwiczająca?
- [ ] Czy post dodaje WARTOŚĆ ponad to co user już napisał w swoich uwagach?
"""

    def generate(
        self,
        input_package: dict,
    ) -> LinkedInPost:
        """
        Generuje post LinkedIn.

        Args:
            input_package: Pakiet z danymi od poprzednich agentów

        Returns:
            LinkedInPost gotowy do publikacji
        """
        input_text = f"""## PAKIET WEJŚCIOWY

{json.dumps(input_package, ensure_ascii=False, indent=2)}

Wygeneruj angażujący post LinkedIn na podstawie tych danych.
Pamiętaj o strukturze: Hook → Kontekst → Rozwinięcie → Refleksja → Pytanie.
"""

        messages = [
            {"role": "system", "content": self.prompt_template},
            {"role": "user", "content": input_text},
        ]

        response = self.client.chat(
            messages=messages,
            model_key=self.model_key,
            temperature=0.7,
            max_tokens=2500,
        )

        return self._parse_response(response.content)

    def _parse_response(self, response: str) -> LinkedInPost:
        """Parsuje odpowiedź plain text do LinkedInPost."""
        import re

        # Wyciągnij sekcję POST LINKEDIN
        post_match = re.search(
            r'═{3,}\s*POST LINKEDIN\s*═{3,}\s*\n(.*?)(?=═{3,}|$)',
            response,
            re.DOTALL | re.IGNORECASE
        )
        full_post = post_match.group(1).strip() if post_match else response.strip()

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

        # Wyciągnij hashtagi z posta
        hashtags = re.findall(r'#\w+', full_post)

        # Wyciągnij hook (pierwsze 1-2 zdania)
        lines = full_post.split('\n')
        hook = lines[0] if lines else ""

        return LinkedInPost(
            hook=hook,
            body=full_post,
            cta="",
            full_post=full_post,
            hook_variants=hook_variants[:3],
            hashtags=hashtags,
            estimated_length=len(full_post),
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
            on_progress("Generuję post LinkedIn...")

        # Zbierz pakiet wejściowy
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
