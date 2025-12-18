# Analizator Treści Social Media

System agentowy AI do tworzenia treści social media - od eksploracji tematu po szlifowanie gotowych postów.

## Dla kogo

- **Twórcy treści** - copywriterzy, content creatorzy, social media managerowie
- **Dziennikarze i publicyści** - piszący na LinkedIn, blogi, newslettery
- **Eksperci budujący markę osobistą** - dzielący się wiedzą w social media
- **Producenci wideo** - potrzebujący tekstowych scenariuszy do Reels/Shorts

---

## Wymagania systemowe

Przed instalacją upewnij się, że masz:

| Wymaganie | Wersja | Jak sprawdzić | Jak zainstalować |
|-----------|--------|---------------|------------------|
| **Python** | 3.10+ | `python3 --version` | [python.org](https://www.python.org/downloads/) |
| **pip** | (dowolna) | `pip --version` | Instaluje się z Pythonem |
| **Git** | (dowolna) | `git --version` | [git-scm.com](https://git-scm.com/) |

> **macOS**: Python 3 możesz zainstalować przez Homebrew: `brew install python`
>
> **Windows**: Pobierz instalator z python.org, zaznacz "Add to PATH"

---

## Instalacja

### 1. Sklonuj repozytorium

```bash
git clone https://github.com/martinmajsawicki/analizator-tresci-social-media.git
cd analizator-tresci-social-media
```

### 2. Utwórz środowisko wirtualne

```bash
python3 -m venv venv
```

### 3. Zainstaluj zależności

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Skonfiguruj klucz API

Skopiuj plik przykładowy i uzupełnij swoje klucze:

```bash
cp .env.example .env
```

Następnie otwórz `.env` w edytorze i wklej **przynajmniej jeden** klucz API:

| Klucz | Gdzie uzyskać | Obsługuje |
|-------|---------------|-----------|
| `OPENROUTER_API_KEY` | [openrouter.ai/keys](https://openrouter.ai/keys) | Wszystkie modele |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/) | Claude |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) | GPT |
| `GOOGLE_API_KEY` | [aistudio.google.com](https://aistudio.google.com/apikey) | Gemini |

> **Tip:** OpenRouter to najprostszy start - jeden klucz do wszystkich modeli. Natywne klucze są szybsze (bez pośrednika).

---

## Uruchomienie (GUI)

**Jedna komenda:**

```bash
./start.sh
```

Otworzy się przeglądarka z interfejsem Streamlit.

> Jeśli skrypt nie działa, uruchom ręcznie:
> ```bash
> source venv/bin/activate && streamlit run app.py
> ```

---

## Jak to działa

### 3 tryby pracy

| Tryb | Kiedy używać | Co dostajesz |
|------|--------------|--------------|
| 🔭 **EKSPLORACJA** | Mam materiał, nie mam pomysłu | Kąty, perspektywy, pytania, hooki |
| 🛠️ **ROZWINIĘCIE** | Mam materiał + wstępny kierunek | Warianty, hooki, kontrargumenty |
| 💎 **SZLIF** | Mam gotowy tekst | Ocenę, poprawki, ulepszoną wersję |

### Wspierane platformy

- **LinkedIn** - posty tekstowe
- **Facebook** - posty tekstowe
- **X / Bluesky / Threads** - posty lub wątki
- **Instagram / YouTube** - scenariusze do Reels/Shorts

---

## Agenci

System wykorzystuje wyspecjalizowanych agentów AI. Każdy ma szczegółowe instrukcje (prompty) określające jego rolę.

### Agenci analityczni

| Agent | Plik | Zadanie |
|-------|------|---------|
| **Ekstraktor** | `agents/extractor.py` | Wyciąga ze źródła: cytaty, osoby, liczby, metafory. Oznacza soundbite'y. |
| **Łowca Rezonansu** | `agents/resonance_hunter.py` | Szuka punktów zaczepienia - co rezonuje z odbiorcą, co budzi emocje. |
| **Antropolog** | `agents/anthropologist.py` | Trzy perspektywy: etnografia (sceny, rytuały), socjologia (podziały), psychologia (emocje). |
| **Polski Kontekstualizator** | `agents/polish_contextualizer.py` | Przelicza zagraniczne realia na polską skalę. Znajduje polskie tematy do połączenia. Wskazuje gdzie szukać polskich ekspertów (bez wymyślania nazwisk!). |
| **Kurator Popkultury** | `agents/popculture_curator.py` | Analogie z filmów, seriali, sportu, codzienności, memów. |
| **Analityk Źródła** | `agents/source_analyst.py` | Ocenia wiarygodność badań: metodologia, próba, ograniczenia. Werdykt: MOCNE/UMIARKOWANE/SŁABE/WĄTPLIWE. |

### Agenci kreatywni

| Agent | Plik | Zadanie |
|-------|------|---------|
| **Archeolog Historii** | `agents/story_excavator.py` | Wydobywa narracje i dramaturgie ze źródła. Buduje posty fabularne. |
| **Architekt Napięcia** | `agents/tension_architect.py` | Buduje napięcie narracyjne. Znajduje konflikt, punkt kulminacyjny, rozwiązanie. |
| **Poszerzacz Kontekstu** | `agents/context_shifter.py` | Pogłębia wymiary: historyczny, społeczny, ekonomiczny, filozoficzny. |
| **Komik** | `agents/comedian.py` | Znajduje okazje na humor. 5 poziomów "pokrętła humoru" od 1 (suchy) do 5 (absurdalny). |
| **Inżynier Zaangażowania** | `agents/engagement.py` | Przekształca monologi w rozmowy. Tworzy CTA, pytania do odbiorców. |

### Agenci recenzujący

| Agent | Plik | Zadanie |
|-------|------|---------|
| **Adwokat Diabła** | `agents/devils_advocate.py` | Kwestionuje założenia. Znajduje słabe punkty. Zadaje niewygodne pytania. |
| **Strażnik Głosu** | `agents/voice_guardian.py` | Wykrywa zombie-frazy, LinkedIn-speak. Sprawdza czy tekst brzmi autentycznie. |
| **Snajper Otwarcia** | `agents/opening_sniper.py` | Specjalista od hooków. Zabija banały. Biblioteka formuł scroll-stopperów. |
| **Wykrywacz Skazy** | `agents/vulnerability_scanner.py` | Szuka ludzkiej autentyczności. Czy autor zdejmuje zbroję eksperta? |

### Agenci platformowi

| Agent | Plik | Zadanie |
|-------|------|---------|
| **Agent LinkedIn** | `agents/linkedin_agent.py` | Formatuje pod LinkedIn. Profesjonalny ton, odpowiednia długość. |
| **Agent Facebook** | `agents/facebook_agent.py` | Formatuje pod Facebook. Luźniejszy ton, emoji. |
| **Agent Microblog** | `agents/microblog_agent.py` | X/Bluesky/Threads. Limity znaków (280/300/500). Wątki. |
| **Agent Wideo** | `agents/video_agent.py` | Scenariusze do kamery. Reels (30-45s), Shorts (45-60s). |

### Synteza

| Agent | Plik | Zadanie |
|-------|------|---------|
| **Brief Synthesizer** | `agents/brief_synthesizer.py` | Tworzy podsumowanie z outputów wszystkich agentów. Dwufazowa architektura: tani model (Gemini Flash) do ekstrakcji, główny model do syntezy. |

---

## Kluczowe zasady agentów

### 1. Buduj na źródle
Każdy agent musi:
- Cytować dosłownie ze źródła
- Podawać osoby z imienia i nazwiska (jeśli są w źródle)
- **Nie wymyślać** - tylko wyciągać

### 2. Nie hallucynuj ekspertów
Polski Kontekstualizator **nie podaje konkretnych nazwisk** ekspertów. Zamiast tego:
- Typy ekspertów (naukowiec, praktyk, publicysta)
- Instytucje gdzie szukać (uczelnie, fundacje, think-tanki)
- Jak ich znaleźć (hashtagi, konferencje, publikacje)

### 3. Format JSON
Większość agentów zwraca ustrukturyzowane dane JSON, nie luźny tekst. Ułatwia to:
- Parsowanie przez inne agenty
- Generowanie raportów HTML
- Dalsze przetwarzanie

---

## Struktura projektu

```
analizator-tresci-social-media/
├── start.sh                # 🚀 Uruchom GUI (jedna komenda)
├── start-cli.sh            # Uruchom CLI
├── app.py                  # UI Streamlit
├── run_v3.py               # CLI
├── requirements.txt
├── .env                    # ⚠️ Utwórz ręcznie (klucz API)
│
├── agents/                 # Agenci AI
│   ├── orchestrator_v3.py  # Koordynator pipeline'u
│   ├── extractor.py
│   ├── anthropologist.py
│   ├── polish_contextualizer.py
│   ├── ... (pozostałe agenty)
│
├── core/                   # Moduły bazowe
│   ├── config.py           # Konfiguracja modeli
│   ├── openrouter.py       # Klient API
│   ├── file_reader.py      # Czytnik plików
│   ├── html_generator.py   # Generator raportów HTML
│   └── agent_registry.py   # Rejestr agentów
│
├── posts/                  # 📁 Twoje pliki źródłowe (tworzy się automatycznie)
├── output/                 # 📁 Wyniki analiz (tworzy się automatycznie)
└── logs/                   # 📁 Logi (tworzy się automatycznie)
```

---

## Uruchomienie CLI (alternatywnie)

```bash
./start-cli.sh
```

Lub ręcznie:

```bash
source venv/bin/activate
python run_v3.py
```

CLI oferuje interaktywny wybór:
1. Model AI
2. Tryb (Eksploracja / Rozwinięcie / Szlif)
3. Plik źródłowy
4. Agenci do analizy
5. Opcjonalnie: draft posta

---

## Obsługiwane formaty plików

| Format | Rozszerzenie | Uwagi |
|--------|--------------|-------|
| Tekst | `.txt` | UTF-8, CP1250, ISO-8859-2 |
| Markdown | `.md` | GitHub-flavored |
| Word | `.docx` | Wymaga `python-docx` |
| PDF | `.pdf` | Wymaga `PyPDF2` |

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

### Skrypt start.sh nie działa
```bash
chmod +x start.sh
./start.sh
```

---

## Licencja

MIT
