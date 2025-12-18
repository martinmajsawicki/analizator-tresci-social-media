# Analizator Treści Social Media

System agentowy AI do tworzenia treści social media - od eksploracji tematu po szlifowanie gotowych postów.

## Dla kogo

- **Twórcy treści** - copywriterzy, content creatorzy, social media managerowie
- **Dziennikarze i publicyści** - piszący na LinkedIn, blogi, newslettery
- **Eksperci budujący markę osobistą** - dzielący się wiedzą w social media
- **Producenci wideo** - potrzebujący tekstowych scenariuszy do Reels/Shorts

---

# Instalacja krok po kroku

## Krok 1: Otwórz Terminal

**macOS:**
1. Naciśnij `Cmd + Spacja` (otworzy się Spotlight)
2. Wpisz `Terminal`
3. Naciśnij `Enter`

**Windows:**
1. Naciśnij `Win + R`
2. Wpisz `cmd`
3. Naciśnij `Enter`

> Terminal to czarne okno, w którym wpisujesz komendy tekstowe. Każdą komendę zatwierdzasz klawiszem `Enter`.

---

## Krok 2: Sprawdź czy masz Pythona

Wpisz w terminalu:

```bash
python3 --version
```

**Jeśli widzisz** coś jak `Python 3.10.0` lub wyższą wersję - masz Pythona, przejdź do kroku 3.

**Jeśli widzisz błąd** "command not found" lub "nie rozpoznano polecenia" - musisz zainstalować Pythona:

### Instalacja Pythona na macOS:

1. Wejdź na https://www.python.org/downloads/
2. Kliknij żółty przycisk "Download Python 3.x.x"
3. Otwórz pobrany plik `.pkg`
4. Klikaj "Kontynuuj" / "Continue" aż do końca instalacji
5. Zamknij i otwórz Terminal ponownie
6. Sprawdź jeszcze raz: `python3 --version`

### Instalacja Pythona na Windows:

1. Wejdź na https://www.python.org/downloads/
2. Kliknij żółty przycisk "Download Python 3.x.x"
3. Otwórz pobrany plik `.exe`
4. **WAŻNE:** Zaznacz checkbox "Add Python to PATH" na dole okna!
5. Kliknij "Install Now"
6. Zamknij i otwórz cmd ponownie
7. Sprawdź: `python --version` (bez "3" na Windows)

---

## Krok 3: Sprawdź czy masz Git

Wpisz w terminalu:

```bash
git --version
```

**Jeśli widzisz** coś jak `git version 2.x.x` - masz Git, przejdź do kroku 4.

**Jeśli widzisz błąd** - zainstaluj Git:

### Instalacja Git na macOS:

Wpisz w terminalu:
```bash
xcode-select --install
```
Pojawi się okno - kliknij "Zainstaluj" i poczekaj.

### Instalacja Git na Windows:

1. Wejdź na https://git-scm.com/download/win
2. Pobierz i uruchom instalator
3. Klikaj "Next" używając domyślnych opcji
4. Zamknij i otwórz cmd ponownie

---

## Krok 4: Pobierz projekt

Wpisz w terminalu (skopiuj całość i wklej):

```bash
git clone https://github.com/martinmajsawicki/analizator-tresci-social-media.git
```

> Ta komenda pobiera projekt z internetu na Twój komputer.

**Co powinieneś zobaczyć:**
```
Cloning into 'analizator-tresci-social-media'...
remote: Enumerating objects: ...
Receiving objects: 100% ...
```

---

## Krok 5: Wejdź do folderu projektu

Wpisz:

```bash
cd analizator-tresci-social-media
```

> `cd` znaczy "change directory" - wchodzisz do folderu.

**Sprawdź czy jesteś w dobrym miejscu:**
```bash
ls
```

**Powinieneś zobaczyć pliki** jak `app.py`, `start.sh`, `requirements.txt` itd.

---

## Krok 6: Utwórz środowisko wirtualne

Wpisz:

**macOS:**
```bash
python3 -m venv venv
```

**Windows:**
```bash
python -m venv venv
```

> Ta komenda tworzy folder `venv` z izolowanym środowiskiem Pythona. Nic się nie wyświetli - to normalne.

---

## Krok 7: Aktywuj środowisko wirtualne

**macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

**Skąd wiesz, że zadziałało?** Na początku linii terminala pojawi się `(venv)`:
```
(venv) twoja-nazwa@komputer:~/analizator-tresci-social-media$
```

---

## Krok 8: Zainstaluj zależności

Wpisz:

```bash
pip install -r requirements.txt
```

> Ta komenda instaluje wszystkie biblioteki potrzebne do działania programu.

**Co zobaczysz:** Długa lista instalowanych pakietów. Poczekaj aż skończy się na:
```
Successfully installed ...
```

---

## Krok 9: Skonfiguruj klucz API

### 9a. Skopiuj plik przykładowy:

**macOS:**
```bash
cp .env.example .env
```

**Windows:**
```bash
copy .env.example .env
```

### 9b. Otwórz plik .env w edytorze:

**macOS:**
```bash
open -e .env
```

**Windows:**
```bash
notepad .env
```

### 9c. Uzyskaj klucz API:

Najprostszy sposób - OpenRouter (jeden klucz do wszystkich modeli AI):

1. Wejdź na https://openrouter.ai
2. Kliknij "Sign In" (prawy górny róg)
3. Zaloguj się przez Google lub utwórz konto
4. Po zalogowaniu kliknij swoje zdjęcie → "Keys"
5. Kliknij "Create Key"
6. Skopiuj klucz (zaczyna się od `sk-or-v1-...`)

### 9d. Wklej klucz do pliku .env:

W pliku `.env` znajdź linię:
```
OPENROUTER_API_KEY=
```

Wklej swój klucz po znaku `=` (bez spacji):
```
OPENROUTER_API_KEY=sk-or-v1-tutaj-twój-klucz
```

**Zapisz plik** (`Cmd+S` na macOS, `Ctrl+S` na Windows) i zamknij edytor.

---

## Krok 10: Uruchom aplikację

**macOS:**
```bash
./start.sh
```

Jeśli pojawi się błąd "permission denied":
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
streamlit run app.py
```

**Co się stanie:** Otworzy się przeglądarka z interfejsem aplikacji.

Jeśli przeglądarka się nie otworzy, skopiuj adres z terminala (np. `http://localhost:8501`) i wklej go w przeglądarkę.

---

# Jak używać aplikacji

## 3 tryby pracy

| Tryb | Kiedy używać | Co dostajesz |
|------|--------------|--------------|
| **EKSPLORACJA** | Mam materiał, nie mam pomysłu | Kąty, perspektywy, pytania, hooki |
| **ROZWINIĘCIE** | Mam materiał + wstępny kierunek | Warianty, hooki, kontrargumenty |
| **SZLIF** | Mam gotowy tekst | Ocenę, poprawki, ulepszoną wersję |

## Wspierane platformy

- **LinkedIn** - posty tekstowe
- **Facebook** - posty tekstowe
- **X / Bluesky / Threads** - posty lub wątki
- **Instagram / YouTube** - scenariusze do Reels/Shorts

---

# Następne uruchomienia

Gdy chcesz ponownie uruchomić aplikację (po restarcie komputera):

1. Otwórz Terminal
2. Wejdź do folderu:
   ```bash
   cd analizator-tresci-social-media
   ```
3. Uruchom:
   ```bash
   ./start.sh
   ```
   (Windows: `venv\Scripts\activate` a potem `streamlit run app.py`)

---

# Rozwiązywanie problemów

## "python3: command not found"
Nie masz zainstalowanego Pythona. Wróć do Kroku 2.

## "git: command not found"
Nie masz zainstalowanego Git. Wróć do Kroku 3.

## "No such file or directory"
Nie jesteś w folderze projektu. Wpisz:
```bash
cd analizator-tresci-social-media
```

## "OPENROUTER_API_KEY not found" lub "Brak kluczy API"
Plik `.env` nie istnieje lub jest pusty. Wróć do Kroku 9.

## "ModuleNotFoundError: No module named 'streamlit'"
Środowisko wirtualne nie jest aktywne. Wpisz:

**macOS:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

## "./start.sh: Permission denied"
Wpisz:
```bash
chmod +x start.sh
./start.sh
```

## Przeglądarka się nie otworzy
Skopiuj adres z terminala (np. `http://localhost:8501`) i wklej w przeglądarkę ręcznie.

## "Error: Invalid API key"
Klucz API jest nieprawidłowy. Sprawdź czy:
- Skopiowałeś cały klucz (zaczyna się od `sk-or-v1-`)
- Nie ma spacji przed ani po kluczu
- Masz środki na koncie OpenRouter

---

# Informacje techniczne

## Obsługiwane formaty plików

| Format | Rozszerzenie |
|--------|--------------|
| Tekst | `.txt` |
| Markdown | `.md` |
| Word | `.docx` |
| PDF | `.pdf` |

## Struktura projektu

```
analizator-tresci-social-media/
├── start.sh          # Uruchom GUI (macOS)
├── app.py            # Interfejs graficzny
├── .env              # Twój klucz API (tworzysz sam)
├── .env.example      # Przykładowy plik konfiguracji
├── agents/           # Agenci AI
├── core/             # Moduły bazowe
├── posts/            # Twoje pliki źródłowe
└── output/           # Wyniki analiz
```

## Alternatywne klucze API

Zamiast OpenRouter możesz użyć kluczy bezpośrednio od dostawców:

| Klucz | Gdzie uzyskać | Obsługuje |
|-------|---------------|-----------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/) | Claude |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) | GPT |
| `GOOGLE_API_KEY` | [aistudio.google.com](https://aistudio.google.com/apikey) | Gemini |

---

## Licencja

MIT
