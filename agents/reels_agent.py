"""Agent 3D: Instagram Reels - generuje skrypt wideo z timestampami."""

import json
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentResult
from core.openrouter import OpenRouterClient


@dataclass
class ReelsScript:
    """Wygenerowany skrypt do Reels."""
    hook: str  # 0-3s
    source_intro: str  # 3-10s
    main_content: str  # 10-25s
    cta: str  # 25-30s
    full_script: str
    timestamps: list
    caption: str
    hashtags: list
    hook_variants: list

    def to_dict(self) -> dict:
        return {
            "hook": self.hook,
            "source_intro": self.source_intro,
            "main_content": self.main_content,
            "cta": self.cta,
            "full_script": self.full_script,
            "timestamps": self.timestamps,
            "caption": self.caption,
            "hashtags": self.hashtags,
            "hook_variants": self.hook_variants,
            "estimated_duration": "30s",
        }


class ReelsAgent(BaseAgent):
    """
    Agent 3D: Instagram Reels.

    Format: Skrypt wideo 30s z timestampami

    Struktura:
    - [0-3s] Hook - zatrzymaj scroll
    - [3-10s] Źródło - skąd to wiesz
    - [10-25s] Treść - główny przekaz
    - [25-30s] CTA - co ma zrobić widz

    WAŻNE: 80% ogląda bez dźwięku - napisy są kluczowe!
    """

    name = "reels_agent"
    name_pl = "Agent Instagram Reels"
    description = "Generuje skrypt wideo 30s dla Instagram Reels"

    def __init__(self, client: OpenRouterClient, model_key: str = "claude-opus-4.5"):
        super().__init__(client, model_key)

    def _get_default_prompt(self) -> str:
        return """# AGENT INSTAGRAM REELS

Jesteś ekspertem od krótkich form wideo. Tworzysz skrypty 30-sekundowe dla Instagram Reels.

## KLUCZOWE ZASADY

1. **80% OGLĄDA BEZ DŹWIĘKU**
   - Napisy na ekranie są OBOWIĄZKOWE
   - Tekst musi być czytelny i zwięzły
   - Każda sekcja = 1-2 zdania na ekranie

2. **MASZ 3 SEKUNDY NA HOOK**
   - Jeśli nie zatrzymasz w 3s, przescrollują
   - Hook musi być wizualny i słowny jednocześnie

3. **AUTENTYCZNOŚĆ > PRODUKCJA**
   - Lepiej naturalnie niż profesjonalnie-sztywno
   - Energia i pasja są ważniejsze niż idealne światło

## STRUKTURA SKRYPTU (30 sekund)

### [0-3s] HOOK
- Zatrzymaj scroll
- Mocne zdanie do kamery
- NIE: "Cześć, dziś opowiem o..."
- TAK: "AI właśnie zrobiła coś, co powinno cię przerazić."

### [3-10s] ŹRÓDŁO
- Skąd to wiesz?
- Badanie, test, doświadczenie
- Krótko, rzeczowo

### [10-25s] GŁÓWNA TREŚĆ
- 2-3 kluczowe punkty
- Każdy punkt = 1 krótkie zdanie
- Tempo: dynamiczne, ale zrozumiałe

### [25-30s] CTA
- Co ma zrobić widz?
- "Zapisz ten Reel jeśli..."
- "Obserwuj po więcej..."
- "Napisz w komentarzu..."

## FORMAT SKRYPTU

Pisz tak, jak mówisz do kamery:
- Krótkie zdania
- Dynamiczne tempo
- Naturalny język
- Pauzy na oddech [pauza]

Dodaj wskazówki techniczne:
- [do kamery] - mówisz bezpośrednio
- [b-roll] - ujęcie ilustracyjne
- [tekst na ekranie] - napis do wyświetlenia
- [zmiana ujęcia] - cięcie
- [pauza] - dramatyczna pauza

## FORMAT ODPOWIEDZI

```json
{
  "timestamps": [
    {
      "time": "0-3s",
      "section": "HOOK",
      "spoken": "Co mówisz do kamery",
      "on_screen_text": "Tekst na ekranie (dla oglądających bez dźwięku)",
      "visual_note": "Wskazówka wizualna"
    },
    {
      "time": "3-10s",
      "section": "ŹRÓDŁO",
      "spoken": "...",
      "on_screen_text": "...",
      "visual_note": "..."
    },
    {
      "time": "10-25s",
      "section": "TREŚĆ",
      "spoken": "...",
      "on_screen_text": "...",
      "visual_note": "..."
    },
    {
      "time": "25-30s",
      "section": "CTA",
      "spoken": "...",
      "on_screen_text": "...",
      "visual_note": "..."
    }
  ],
  "full_script": "Pełny skrypt do przeczytania jednym ciągiem",
  "hook": "Sam hook (0-3s)",
  "hook_variants": [
    "Alternatywny hook 1",
    "Alternatywny hook 2",
    "Alternatywny hook 3"
  ],
  "caption": "Opis pod Reelsem (max 2200 znaków)",
  "hashtags": ["#AI", "#Tech", "..."],
  "tips_for_recording": [
    "Wskazówka 1 dla nagrywającego",
    "Wskazówka 2"
  ]
}
```

## PRZYKŁADOWY SKRYPT

**Temat:** AI w rekrutacji odrzuca 75% CV

```json
{
  "timestamps": [
    {
      "time": "0-3s",
      "section": "HOOK",
      "spoken": "Wysłałeś CV do 50 firm i zero odpowiedzi? To nie Ty. To algorytm.",
      "on_screen_text": "50 CV = 0 odpowiedzi? 🤔",
      "visual_note": "[do kamery, intensywny kontakt wzrokowy]"
    },
    {
      "time": "3-10s",
      "section": "ŹRÓDŁO",
      "spoken": "Nowe badanie pokazuje, że systemy ATS - te automaty co czytają CV - odrzucają 75 procent aplikacji. Zanim jakikolwiek człowiek je zobaczy.",
      "on_screen_text": "75% CV odrzucone przez AI ❌",
      "visual_note": "[pokaż telefon z raportem lub ekran]"
    },
    {
      "time": "10-25s",
      "section": "TREŚĆ",
      "spoken": "Dlaczego? Bo szukają SŁÓW KLUCZOWYCH. Nie masz dokładnie tych słów co w ogłoszeniu? [pauza] Out. Masz luki w CV? Out. Zmieniałeś branżę? Out. [pauza] Twoje doświadczenie, Twoje umiejętności - to nieważne, jeśli robot nie znajdzie właściwych fraz.",
      "on_screen_text": "❌ Brak słów kluczowych\\n❌ Luki w CV\\n❌ Zmiana branży",
      "visual_note": "[dynamiczne cięcia między punktami]"
    },
    {
      "time": "25-30s",
      "section": "CTA",
      "spoken": "Zapisz tego Reelsa i sprawdź czy Twoje CV przejdzie test ATS. Link w bio.",
      "on_screen_text": "📌 ZAPISZ + sprawdź swoje CV",
      "visual_note": "[wskaż palcem w górę na 'zapisz']"
    }
  ],
  "full_script": "Wysłałeś CV do 50 firm i zero odpowiedzi? To nie Ty. To algorytm. Nowe badanie pokazuje, że systemy ATS odrzucają 75% aplikacji, zanim jakikolwiek człowiek je zobaczy. Dlaczego? Bo szukają słów kluczowych. Nie masz dokładnie tych słów co w ogłoszeniu? Out. Masz luki w CV? Out. Zmieniałeś branżę? Out. Twoje doświadczenie jest nieważne, jeśli robot nie znajdzie właściwych fraz. Zapisz tego Reelsa i sprawdź czy Twoje CV przejdzie test ATS.",
  "hook": "Wysłałeś CV do 50 firm i zero odpowiedzi? To nie Ty. To algorytm.",
  "hook_variants": [
    "75% CV nigdy nie trafia do człowieka. Oto dlaczego.",
    "Twoje CV jest świetne. Ale robot tego nie widzi.",
    "Rekruter nie odrzucił Twojego CV. Algorytm to zrobił."
  ],
  "caption": "75% CV jest odrzucanych przez AI zanim jakikolwiek człowiek je zobaczy 🤖\\n\\nTo nie znaczy, że jesteś zły. To znaczy, że grasz w grę, której zasady ustalił algorytm.\\n\\nCo możesz zrobić?\\n→ Używaj słów kluczowych z ogłoszenia (dosłownie!)\\n→ Prosty format, bez tabelek i grafik\\n→ Sprawdź CV w darmowym skanerze ATS\\n\\nZapisz i wyślij znajomemu, który właśnie szuka pracy 💼\\n\\n#CV #PracaIT #Rekrutacja #AI #SztucznaInteligencja #Kariera #JobSearch",
  "hashtags": ["#CV", "#Rekrutacja", "#AI", "#SztucznaInteligencja", "#Kariera", "#PracaIT", "#JobSearch", "#TikTokPolska", "#ReelsPolska"],
  "tips_for_recording": [
    "Nagraj w pionie (9:16)",
    "Dobre oświetlenie twarzy (naturalne lub ring light)",
    "Mów energicznie, trochę szybciej niż normalnie",
    "Patrz w obiektyw, nie na ekran",
    "Dodaj napisy w aplikacji CapCut lub Instagram"
  ]
}
```
"""

    def generate(
        self,
        input_package: dict,
    ) -> ReelsScript:
        """
        Generuje skrypt do Reels.

        Args:
            input_package: Pakiet z danymi od poprzednich agentów

        Returns:
            ReelsScript gotowy do nagrania
        """
        input_text = f"""## PAKIET WEJŚCIOWY

{json.dumps(input_package, ensure_ascii=False, indent=2)}

Wygeneruj skrypt 30-sekundowy do Instagram Reels.
Pamiętaj o strukturze timestampów i tekstach na ekranie.
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

    def _parse_response(self, response: str) -> ReelsScript:
        """Parsuje odpowiedź do ReelsScript."""
        import re

        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response

            data = json.loads(json_str)

            timestamps = data.get("timestamps", [])

            # Wyciągnij sekcje z timestamps
            hook = ""
            source_intro = ""
            main_content = ""
            cta = ""

            for ts in timestamps:
                section = ts.get("section", "").upper()
                spoken = ts.get("spoken", "")
                if section == "HOOK":
                    hook = spoken
                elif section == "ŹRÓDŁO":
                    source_intro = spoken
                elif section == "TREŚĆ":
                    main_content = spoken
                elif section == "CTA":
                    cta = spoken

            return ReelsScript(
                hook=data.get("hook", hook),
                source_intro=source_intro,
                main_content=main_content,
                cta=cta,
                full_script=data.get("full_script", ""),
                timestamps=timestamps,
                caption=data.get("caption", ""),
                hashtags=data.get("hashtags", []),
                hook_variants=data.get("hook_variants", []),
            )

        except (json.JSONDecodeError, KeyError):
            return ReelsScript(
                hook="",
                source_intro="",
                main_content=response,
                cta="",
                full_script=response,
                timestamps=[],
                caption="",
                hashtags=[],
                hook_variants=[],
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
            on_progress("Generuję skrypt Instagram Reels...")

        input_package = {
            "extracted_data": context.get("extracted_data", {}) if context else {},
            "resonance_report": context.get("resonance_report", {}) if context else {},
            "depth_report": context.get("depth_report", {}) if context else {},
            "user_notes": context.get("user_notes", "") if context else "",
        }

        if not input_package["extracted_data"]:
            input_package["raw_content"] = content

        script = self.generate(input_package)

        return AgentResult(
            agent_name=self.name,
            agent_name_pl=self.name_pl,
            content=json.dumps(script.to_dict(), ensure_ascii=False, indent=2),
        )
