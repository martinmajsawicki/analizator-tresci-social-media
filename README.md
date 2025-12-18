# Social Media Analyzer v3

System agentowy do pracy z treściami dla social media - od eksploracji tematu po szlifowanie gotowych postów.

## Dla kogo

- **Twórcy treści** - copywriterzy, content creatorzy, social media managerowie
- **Dziennikarze i publicyści** - piszący na LinkedIn, blogi, newslettery
- **Eksperci budujący markę osobistą** - dzielący się wiedzą w social media
- **Producenci wideo** - potrzebujący tekstowych scenariuszy do Reels/Shorts

## Problem

1. **Mam materiał, ale nie wiem co z nim zrobić** - artykuł, badanie, news - ale brak pomysłu na kąt
2. **Mam pomysł, ale nie wiem jak go rozwinąć** - wstępny kierunek, ale potrzebuję perspektyw
3. **Mam gotowy tekst, ale nie wiem czy dobry** - potrzebuję oceny i konkretnych poprawek

## Rozwiązanie: 3 tryby pracy

```
╔══════════════════════════════════════════════════════════════╗
║           🎯 SOCIAL MEDIA ANALYZER v3                        ║
╚══════════════════════════════════════════════════════════════╝

📋 NA JAKIM ETAPIE JESTEŚ?
───────────────────────────────────────────────────────────────
[1] 🔬 EKSPLORACJA  - Mam materiał, nie mam pomysłu
                      → dostajesz: kąty, perspektywy, pytania

[2] 🌱 ROZWINIĘCIE  - Mam materiał + wstępny kierunek
                      → dostajesz: warianty, hooki, kontrargumenty

[3] ✍️  SZLIF        - Mam gotowy tekst
                      → dostajesz: ocenę, poprawki, ulepszoną wersję
```

### Po każdym trybie (opcjonalnie):

```
📝 Wygenerować draft posta? (t/N)

📱 GDZIE PUBLIKUJESZ?
───────────────────────────────────────
[1] 💼 LinkedIn
[2] 👥 Facebook
[3] 🐦 X / Bluesky / Threads  → post czy wątek?
[4] 🎬 Instagram / YouTube    → tekst do kamery
```

---

## Szybki start

```bash
# 1. Aktywuj środowisko
source venv/bin/activate

# 2. Uruchom CLI
python run_v3.py

# LUB uruchom UI (Streamlit)
streamlit run app.py
```

### Dwa interfejsy

| Interfejs | Komenda | Opis |
|-----------|---------|------|
| **CLI** | `python run_v3.py` | Tekstowy, w terminalu |
| **UI** | `streamlit run app.py` | Graficzny, w przeglądarce |

---

## Pliki źródłowe

System czyta pliki z folderu `posts/` (lub z dowolnej ścieżki).

### Obsługiwane formaty
| Format | Rozszerzenie | Uwagi |
|--------|--------------|-------|
| Tekst | `.txt` | UTF-8, CP1250, ISO-8859-2 |
| Markdown | `.md` | GitHub-flavored |
| Word | `.docx` | Wymaga `python-docx` |
| PDF | `.pdf` | Wymaga `PyPDF2` |

### Jak dodać plik źródłowy

1. **Z folderu posts/** - skopiuj plik do `posts/`, pojawi się w menu
2. **Z dowolnego miejsca** - wybierz `[P]` i podaj pełną ścieżkę

```bash
# Przykład: skopiuj artykuł do folderu posts/
cp ~/Downloads/artykul.pdf posts/
```

---

## Tryby szczegółowo

### 🔬 EKSPLORACJA

**Kiedy:** Masz artykuł/badanie, ale nie wiesz jak o tym napisać.

**Co dostajesz:**
- 5-7 możliwych kątów (z hookami i oceną siły)
- Punkty napięcia / kontrowersje
- Polski kontekst (do czego podpiąć)
- Pytania warte zadania
- Pułapki do uniknięcia (banały)
- Rekomendowany kąt

**Przykład outputu:**
```
🎯 MOŻLIWE KĄTY:

  [1] Kąt personalny
      Jak to dotyczy CIEBIE - czy Twoje CV przejdzie przez ATS?
      Hook: "Wysłałeś 50 CV i zero odpowiedzi? To nie Ty. To algorytm."
      Siła: ████████░░ 8/10

  [2] Kąt paradoksu
      HR-owcy boją się AI, ale sami używają ATS który odrzuca 75% ludzi
      Hook: "HR-owcy boją się że AI zabierze im pracę..."
      Siła: █████████░ 9/10
```

### 🌱 ROZWINIĘCIE

**Kiedy:** Masz materiał + wstępny pomysł ("podpiąć pod wybory PL").

**Co dostajesz:**
- Ocena Twojego kierunku (czy dobry? co ulepszyć?)
- 3 warianty rozwinięcia (bezpieczny / odważny / personalny)
- 5-7 propozycji hooków
- Co wzmocnić / co pominąć
- Kontrargumenty do rozważenia

**Przykład outputu:**
```
📝 TWÓJ KIERUNEK:
   "Podpiąć pod wybory PL"
   Ocena: ████████░░ 8/10
   Co działa: Aktualność, emocje, polski kontekst

🔀 WARIANTY ROZWINIĘCIA:

  [BEZPIECZNY]
   Skupienie na mechanizmie, nie na kandydatach
   Hook: "Myślisz że jesteś odporny na manipulację?"
   Potencjał: 7/10

  [ODWAŻNY]
   Wprost o polskich wyborach
   Hook: "Maj 2025. Kto wygra? Może zdecydował ChatGPT."
   Potencjał: 9/10 | Ryzyko: może być odebrany jako polityczny
```

### ✍️ SZLIF

**Kiedy:** Masz gotowy tekst i chcesz go ulepszyć.

**Co dostajesz:**
- Ocena (1-10) + status (OK / POPRAW / PRZEPISZ)
- Mocne strony
- Problemy (z lokalizacją i wpływem)
- Konkretne poprawki inline (było → jest + powód)
- Pełna wersja po poprawkach
- Alternatywne hooki

**Przykład outputu:**
```
📈 OCENA: ███████░░░ 7/10 [POPRAW]

✅ MOCNE STRONY:
   • Dobry polski kontekst
   • Konkretne liczby

❌ PROBLEMY:
   • Hook zaczyna się od źródła
     Gdzie: Pierwsze zdanie
     Wpływ: Ludzie scrollują dalej

🔧 POPRAWKI:
   BYŁO: "Nowe badanie Nature pokazuje, że AI wpływa na poglądy."
   JEST: "Twoje poglądy polityczne? AI może je zmienić w 10 minut."
   Powód: Personalizacja + hook od czytelnika
```

---

## Pipeline analityczny (v3)

```
Źródło → Extractor → Resonance Hunter → Anthropologist → Polish Contextualizer → Popculture Curator → [Mode Agent] → [Platform Agent]
```

### Agenci analityczni (wybieralni)

Po wybraniu trybu i pliku, możesz zdecydować których agentów użyć:

```
🤖 WYBIERZ AGENTOW DO ANALIZY:
────────────────────────────────────────────────────────────────

📊 AGENCI ANALITYCZNI (wydobywaja dane ze zrodla):
  [1] [✓] Antropolog
       Analiza etnograficzna, socjologiczna i psychologiczna
  [2] [✓] Polski Kontekstualizator
       Tłumaczy obce realia na polski kontekst
  [3] [✓] Kurator Popkultury
       Analogie z filmow, sportu, codziennosci
────────────────────────────────────────────────────────────────
  [A] Wybierz wszystkich
  [D] Uzyj domyslnych (zaznaczone ✓)
  [0] Pomin agentow (tylko podstawowa analiza)
```

**Dla trybu SZLIF** dostępni są dodatkowi agenci recenzujący:

```
🔍 AGENCI RECENZUJACY (oceniaja gotowy tekst):
  [1] [ ] Straznik Glosu
       Sprawdza autentyczny glos, wykrywa zombie-frazy
  [2] [ ] Snajper Otwarcia
       Specjalista od hookow, zabija banaly
  [3] [ ] Wykrywacz Skazy
       Szuka ludzkiej autentycznosci i vulnerability
```

| Agent | Rola | Co dostarcza |
|-------|------|--------------|
| **Extractor** | Wyciąga surowe dane | Cytaty (z oznaczeniem soundbite), osoby (z pełnymi danymi), liczby, metafory |
| **Resonance Hunter** | Szuka punktów zaczepienia | Co rezonuje z odbiorcą, co budzi emocje |
| **Anthropologist** | Trzy perspektywy | Etnografia (sceny, rytuały), Socjologia (podziały, konflikty), Psychologia (emocje, potrzeby) |
| **Polish Contextualizer** | Polski kontekst | Przeliczenia na PL skalę, polskie tematy, polscy eksperci, polskie ramy myślenia |
| **Popculture Curator** | Analogie | Filmy/seriale, sport, codzienność, memy, literatura |
| **Voice Guardian** | Strażnik autentyczności | Wykrywa zombie-frazy, LinkedIn-speak, sprawdza czy brzmi jak TY |
| **Opening Sniper** | Specjalista od hooków | Zabija banały, tworzy scroll-stoppery, biblioteka formuł hooków |
| **Vulnerability Scanner** | Wykrywacz ludzkiej skazy | Szuka autentyczności, czy autor zdejmuje zbroję eksperta |

### Zasada: Buduj na źródle

Każdy agent musi:
- Cytować dosłownie ze źródła
- Podawać osoby z imienia i nazwiska
- Nie wymyślać - wyciągać

---

## Platformy

| Grupa | Platformy | Output |
|-------|-----------|--------|
| **LinkedIn** | LinkedIn | Post tekstowy |
| **Facebook** | Facebook | Post tekstowy |
| **Microblog** | X, Bluesky, Threads | Post lub wątek |
| **Wideo** | Instagram Reels, YouTube Shorts | Tekst do kamery |

### Limity znaków (microblog)
- X (Twitter): 280
- Bluesky: 300
- Threads: 500

### Wideo
- Instagram Reels: 30-45s (~100-150 słów)
- YouTube Shorts: 45-60s (~150-200 słów)

Output wideo to **sam tekst do powiedzenia do kamery** - bez timestampów, bez visual notes. Gadająca głowa.

---

## Instalacja

### 1. Sklonuj projekt

```bash
git clone https://github.com/USER/social-media-analyzer.git
cd social-media-analyzer
```

### 2. Utwórz środowisko wirtualne

```bash
python3 -m venv venv
```

### 3. Aktywuj środowisko

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Zainstaluj zależności

```bash
pip install -r requirements.txt
```

### 5. Skonfiguruj API

Utwórz plik `.env` w głównym katalogu:

```bash
OPENROUTER_API_KEY=sk-or-v1-twój-klucz-api
```

Klucz API uzyskasz na: https://openrouter.ai

---

## Użycie

```bash
python run_v3.py
```

Interaktywny wybór:
1. Model AI
2. Tryb (Eksploracja / Rozwinięcie / Szlif)
3. Plik źródłowy
4. Agenci do analizy
5. Opcjonalnie: draft posta

---

## Struktura projektu

### Po sklonowaniu z GitHub

```
SOCIAL_MEDIA_ANALYZER/
├── run_v3.py               # CLI
├── app.py                  # UI Streamlit
├── cli_v3.py               # Logika CLI
├── requirements.txt        # Zależności
├── .gitignore
├── README.md
│
├── agents/                 # Agenci (kod)
├── core/                   # Moduły bazowe (kod)
│
└── .env                    # ⚠️ UTWÓRZ RĘCZNIE!
```

### Foldery tworzone automatycznie

Te foldery **tworzą się same** przy pierwszym uruchomieniu:

| Folder | Kiedy się tworzy | Co zawiera |
|--------|------------------|------------|
| `posts/` | Przy starcie | Pliki źródłowe do analizy |
| `logs/` | Przy starcie | Logi API i orchestratora |
| `output/` | Przy zapisie wyników | Raporty JSON i HTML |
| `venv/` | `python -m venv venv` | Środowisko wirtualne |

### Po pierwszym uruchomieniu

```
SOCIAL_MEDIA_ANALYZER/
├── run_v3.py               # 🚀 Uruchom to!
├── app.py                  # 🌐 Lub to (UI)
├── cli_v3.py               # Interfejs (3 tryby)
│
├── agents/
│   ├── orchestrator_v3.py  # Koordynator (3 ścieżki)
│   ├── exploration_agent.py # Agent Eksploracji
│   ├── development_agent.py # Agent Rozwinięcia
│   │
│   │ # Agenci analityczni
│   ├── extractor.py        # Ekstraktor (cytaty, osoby, dane)
│   ├── resonance_hunter.py # Łowca Rezonansu
│   ├── anthropologist.py   # Antropolog (etnografia, socjologia, psychologia)
│   ├── polish_contextualizer.py # Polski Kontekstualizator
│   ├── popculture_curator.py # Kurator Popkultury
│   │
│   │ # Agenci recenzujący
│   ├── voice_guardian.py   # Strażnik Głosu
│   ├── opening_sniper.py   # Snajper Otwarć
│   ├── vulnerability_scanner.py # Wykrywacz Skazy
│   │
│   │ # Agenci platformowi
│   ├── linkedin_agent.py   # Agent LinkedIn
│   ├── facebook_agent.py   # Agent Facebook
│   ├── microblog_agent.py  # X / Bluesky / Threads
│   ├── video_agent.py      # Reels / Shorts
│   └── quality_controller.py # Kontroler Jakości + tryb Szlif
│
├── core/
│   ├── config.py           # Konfiguracja + modele
│   ├── openrouter.py       # Klient API
│   ├── file_reader.py      # Czytnik plików (txt, md, docx, pdf)
│   └── agent_registry.py   # Rejestr agentów do wyboru
│
├── posts/                  # Pliki źródłowe
├── output/                 # Wygenerowane wyniki
├── logs/                   # Logi
│
└── .env                    # Klucz API (nie commituj!)
```

---

## Przykład sesji

```
╔══════════════════════════════════════════════════════════════╗
║           🎯 SOCIAL MEDIA ANALYZER v3                        ║
╚══════════════════════════════════════════════════════════════╝

🤖 WYBIERZ MODEL AI:
────────────────────────────────────────
  [1] Claude Opus 4.5 (zalecany)
  [2] GPT-5.1
  [3] Gemini 3 Pro
────────────────────────────────────────
Wybierz (1-3) [Enter = 1]:

✅ Model: Claude Opus 4.5

📋 NA JAKIM ETAPIE JESTEŚ?
──────────────────────────────────────────────────────
  [1] 🔬 EKSPLORACJA  - Mam materiał, nie mam pomysłu
  [2] 🌱 ROZWINIĘCIE  - Mam materiał + wstępny kierunek
  [3] ✍️  SZLIF        - Mam gotowy tekst

Wybierz tryb (1/2/3): 1

📂 PLIKI ŹRÓDŁOWE (posts/):
─────────────────────────────────────────────────────────────────
  [1] artykul-nyt-ai-edukacja.pdf          (2024-12-10, 15KB)
  [2] notatki-linkedin.txt                  (2024-12-09, 2KB)
  [3] badanie-nature-chatboty.docx          (2024-12-08, 45KB)
─────────────────────────────────────────────────────────────────
  [P] 📁 Podaj ścieżkę do pliku
  [0] ❌ Anuluj
─────────────────────────────────────────────────────────────────

Wybierz (1-3 / P / 0): 1
  ✅ Wczytano: artykul-nyt-ai-edukacja.pdf (12543 znaków)

🤖 WYBIERZ AGENTOW DO ANALIZY:
────────────────────────────────────────────────────────────────

📊 AGENCI ANALITYCZNI (wydobywaja dane ze zrodla):
  [1] [✓] Antropolog
       Analiza etnograficzna, socjologiczna i psychologiczna
  [2] [✓] Polski Kontekstualizator
       Tłumaczy obce realia na polski kontekst
  [3] [✓] Kurator Popkultury
       Analogie z filmow, sportu, codziennosci
────────────────────────────────────────────────────────────────
  [A] Wybierz wszystkich
  [D] Uzyj domyslnych (zaznaczone ✓)
  [0] Pomin agentow (tylko podstawowa analiza)
────────────────────────────────────────────────────────────────

Wybierz (1-3, oddziel przecinkami / A / D / 0) [Enter = D]:
  ✅ Wybrano domyslnych: anthropologist, polish_contextualizer, popculture_curator

🔄 Analizuję...
🔍 Ekstrakcja danych źródłowych...
🎯 Szukam punktów rezonansu...
🧠 Pogłębiam analizę (etnografia, socjologia, psychologia)...
🇵🇱 Tłumaczę na polski kontekst...
🎬 Szukam analogii popkulturowych...
🔬 Generuję perspektywy i kąty...

════════════════════════════════════════════════════════════════
📊 RAPORT EKSPLORACYJNY
════════════════════════════════════════════════════════════════

🎯 MOŻLIWE KĄTY:
[...]

📝 Wygenerować draft posta? (t/N): t

📱 GDZIE PUBLIKUJESZ?
────────────────────────────────────────
  [1] 💼 LinkedIn
  [2] 👥 Facebook
  [3] 🐦 X / Bluesky / Threads
  [4] 🎬 Instagram / YouTube (wideo)

Wybór: 3

📝 FORMAT?
────────────────────────────────────────
  [1] 📄 Pojedynczy post
  [2] 🧵 Wątek

Wybór: 2

🔄 Generuję wątek...

════════════════════════════════════════════════════════════════
📝 DRAFT: X_TWITTER
════════════════════════════════════════════════════════════════

🧵 WĄTEK:

   [1] Wysłałeś 50 CV i zero odpowiedzi? To nie Ty. To algorytm.

   [2] Systemy ATS odrzucają 75% aplikacji zanim człowiek je zobaczy...

   [3] Co możesz zrobić? Kopiuj słowa kluczowe z ogłoszenia. Dosłownie.

💾 Zapisać wyniki do pliku? (t/N): t
✅ Zapisano: output/2025-12-11-123456-exploration/
```

---

## Troubleshooting

### "OPENROUTER_API_KEY not found"
```bash
echo "OPENROUTER_API_KEY=sk-or-v1-xxx" > .env
```

### "ModuleNotFoundError"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Timeout API
```bash
# W .env:
TIMEOUT=180
```

---

## Licencja

MIT
