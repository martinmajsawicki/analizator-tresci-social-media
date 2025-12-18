#!/usr/bin/env python3
"""
Social Media Analyzer v3 - CLI z 3 trybami pracy.

Tryby:
1. EKSPLORACJA  - Mam materiał, nie mam pomysłu
2. ROZWINIĘCIE  - Mam materiał + wstępny kierunek
3. SZLIF        - Mam gotowy tekst
"""

import sys
from pathlib import Path

from core.config import Config, AVAILABLE_MODELS
from core.file_reader import FileReader, format_file_list
from core.agent_registry import get_agents_for_mode, get_default_agents_for_mode
from agents.orchestrator_v3 import OrchestratorV3


def print_banner():
    """Print welcome banner."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🎯 SOCIAL MEDIA ANALYZER v3                        ║
╚══════════════════════════════════════════════════════════════╝
""")


def select_model() -> str:
    """Interactive model selection."""
    print("🤖 WYBIERZ MODEL AI:")
    print("─" * 40)

    models_list = list(AVAILABLE_MODELS.items())

    for i, (key, model) in enumerate(models_list, 1):
        rec = " (zalecany)" if i == 1 else ""
        print(f"  [{i}] {model.name}{rec}")

    print("─" * 40)

    while True:
        choice = input(f"Wybierz (1-{len(models_list)}) [Enter = 1]: ").strip()
        if choice == "":
            return models_list[0][0]
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(models_list):
                return models_list[idx][0]
        except ValueError:
            pass
        print(f"  ❌ Wpisz liczbę 1-{len(models_list)}")


def select_mode() -> str:
    """Interactive mode selection."""
    print("\n📋 NA JAKIM ETAPIE JESTEŚ?")
    print("─" * 50)
    print("  [1] 🔬 EKSPLORACJA  - Mam materiał, nie mam pomysłu")
    print("                       → dostajesz: kąty, perspektywy, pytania")
    print()
    print("  [2] 🌱 ROZWINIĘCIE  - Mam materiał + wstępny kierunek")
    print("                       → dostajesz: warianty, hooki, kontrargumenty")
    print()
    print("  [3] ✍️  SZLIF        - Mam gotowy tekst")
    print("                       → dostajesz: ocenę, poprawki, ulepszoną wersję")
    print("─" * 50)

    while True:
        choice = input("\nWybierz tryb (1/2/3): ").strip()
        if choice == "1":
            return "exploration"
        elif choice == "2":
            return "development"
        elif choice == "3":
            return "polish"
        else:
            print("❌ Wpisz 1, 2 lub 3")


def get_multiline_input(prompt: str) -> str:
    """Get multiline input from user."""
    print(f"\n{prompt}")
    print("(wpisz tekst, zakończ pustą linią)")
    print("─" * 40)

    lines = []
    while True:
        try:
            line = input()
            if line == "":
                if lines:
                    break
            else:
                lines.append(line)
        except EOFError:
            break

    return "\n".join(lines)


def select_source_file(file_reader: FileReader) -> str:
    """
    Interaktywny wybór pliku źródłowego.

    Returns:
        Zawartość wybranego pliku
    """
    files = file_reader.list_files()

    print("\n📂 PLIKI ŹRÓDŁOWE (posts/):")
    print("─" * 65)

    if files:
        print(format_file_list(files))
    else:
        print("  (brak plików - dodaj pliki .txt, .md, .docx lub .pdf do folderu posts/)")

    print("─" * 65)
    print("  [P] 📁 Podaj ścieżkę do pliku")
    print("  [0] ❌ Anuluj")
    print("─" * 65)

    while True:
        if files:
            choice = input(f"\nWybierz (1-{len(files)} / P / 0): ").strip()
        else:
            choice = input("\nWybierz (P / 0): ").strip()

        # Anuluj
        if choice == "0":
            return None

        # Podaj ścieżkę
        if choice.upper() == "P":
            path_str = input("\n📁 Podaj ścieżkę do pliku: ").strip()

            if not path_str:
                print("  ❌ Nie podano ścieżki")
                continue

            # Rozwiń ~ i sprawdź
            path = Path(path_str).expanduser().resolve()

            if not path.exists():
                print(f"  ❌ Plik nie istnieje: {path}")
                continue

            if path.suffix.lower() not in file_reader.SUPPORTED_EXTENSIONS:
                print(f"  ❌ Nieobsługiwany format: {path.suffix}")
                print(f"     Obsługiwane: {', '.join(file_reader.SUPPORTED_EXTENSIONS)}")
                continue

            try:
                content = file_reader.read_file(path)
                print(f"  ✅ Wczytano: {path.name} ({len(content)} znaków)")
                return content
            except Exception as e:
                print(f"  ❌ Błąd czytania pliku: {e}")
                continue

        # Wybór z listy
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                selected_file = files[idx]
                try:
                    content = file_reader.read_file(selected_file.path)
                    print(f"  ✅ Wczytano: {selected_file.name} ({len(content)} znaków)")
                    return content
                except Exception as e:
                    print(f"  ❌ Błąd czytania pliku: {e}")
                    continue
            else:
                print(f"  ❌ Wpisz liczbę 1-{len(files)}, P lub 0")
        except ValueError:
            if files:
                print(f"  ❌ Wpisz liczbę 1-{len(files)}, P lub 0")
            else:
                print("  ❌ Wpisz P lub 0")


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    """Ask yes/no question."""
    default_hint = "(T/n)" if default else "(t/N)"
    answer = input(f"{prompt} {default_hint}: ").strip().lower()
    if answer == "":
        return default
    return answer in ("t", "tak", "y", "yes")


def select_agents(mode: str) -> list[str]:
    """
    Interactive agent selection for the given mode.

    Returns:
        List of selected agent keys
    """
    available_agents = get_agents_for_mode(mode)

    if not available_agents:
        return []

    default_agents = get_default_agents_for_mode(mode)

    print("\n🤖 WYBIERZ AGENTÓW DO ANALIZY:")
    print("─" * 60)

    # Grupuj agentów po kategorii
    categories = {}
    for agent in available_agents:
        if agent.category not in categories:
            categories[agent.category] = []
        categories[agent.category].append(agent)

    category_names = {
        "analytical": "📊 AGENCI ANALITYCZNI (wydobywają dane ze źródła)",
        "review": "🔍 AGENCI RECENZUJĄCY (oceniają gotowy tekst)",
        "enhancement": "✨ AGENCI ULEPSZAJĄCY (dodają humor/engagement)",
    }

    agent_map = {}  # numer -> agent_key
    current_num = 1

    for category, agents in categories.items():
        print(f"\n{category_names.get(category, category.upper())}:")
        for agent in agents:
            default_mark = "✓" if agent.key in default_agents else " "
            print(f"  [{current_num}] [{default_mark}] {agent.name_pl}")
            print(f"       {agent.description}")
            agent_map[current_num] = agent.key
            current_num += 1

    print("─" * 60)
    print("  [A] Wybierz wszystkich")
    print("  [D] Użyj domyślnych (zaznaczone ✓)")
    print("  [0] Pomiń agentów (tylko podstawowa analiza)")
    print("─" * 60)

    while True:
        choice = input(f"\nWybierz (1-{current_num - 1}, oddziel przecinkami / A / D / 0) [Enter = D]: ").strip()

        # Domyślne
        if choice == "" or choice.upper() == "D":
            print(f"  ✅ Wybrano domyślnych: {', '.join(default_agents) if default_agents else 'brak'}")
            return default_agents

        # Wszyscy
        if choice.upper() == "A":
            all_keys = [agent.key for agent in available_agents]
            print(f"  ✅ Wybrano wszystkich: {', '.join(all_keys)}")
            return all_keys

        # Pomiń
        if choice == "0":
            print("  ⏭️ Pominięto agentów")
            return []

        # Parsuj wybór numeryczny
        try:
            selected_nums = [int(n.strip()) for n in choice.split(",")]
            selected_keys = []

            for num in selected_nums:
                if num in agent_map:
                    selected_keys.append(agent_map[num])
                else:
                    print(f"  ❌ Nieprawidłowy numer: {num}")
                    selected_keys = []
                    break

            if selected_keys:
                print(f"  ✅ Wybrano: {', '.join(selected_keys)}")
                return selected_keys

        except ValueError:
            pass

        print(f"  ❌ Wpisz numery oddzielone przecinkami (1-{current_num - 1}), A, D lub 0")


def select_platform_group() -> str:
    """Select platform group for draft."""
    print("\n📱 GDZIE PUBLIKUJESZ?")
    print("─" * 40)
    print("  [1] 💼 LinkedIn")
    print("  [2] 👥 Facebook")
    print("  [3] 🐦 X / Bluesky / Threads")
    print("  [4] 🎬 Instagram / YouTube (wideo)")
    print("─" * 40)

    while True:
        choice = input("\nWybierz (1-4): ").strip()
        if choice == "1":
            return "linkedin"
        elif choice == "2":
            return "facebook"
        elif choice == "3":
            return "microblog"
        elif choice == "4":
            return "video"
        else:
            print("❌ Wpisz 1, 2, 3 lub 4")


def select_microblog_platform() -> str:
    """Select specific microblog platform."""
    print("\n🐦 KTÓRA PLATFORMA?")
    print("─" * 40)
    print("  [1] X (Twitter)")
    print("  [2] Bluesky")
    print("  [3] Threads")
    print("─" * 40)

    while True:
        choice = input("\nWybierz (1-3): ").strip()
        if choice == "1":
            return "x_twitter"
        elif choice == "2":
            return "bluesky"
        elif choice == "3":
            return "threads"
        else:
            print("❌ Wpisz 1, 2 lub 3")


def select_video_platform() -> str:
    """Select specific video platform."""
    print("\n🎬 KTÓRA PLATFORMA?")
    print("─" * 40)
    print("  [1] Instagram Reels")
    print("  [2] YouTube Shorts")
    print("─" * 40)

    while True:
        choice = input("\nWybierz (1-2): ").strip()
        if choice == "1":
            return "instagram_reels"
        elif choice == "2":
            return "youtube_shorts"
        else:
            print("❌ Wpisz 1 lub 2")


def select_draft_format() -> str:
    """Select post or thread format."""
    print("\n📝 FORMAT?")
    print("─" * 40)
    print("  [1] 📄 Pojedynczy post")
    print("  [2] 🧵 Wątek")
    print("─" * 40)

    while True:
        choice = input("\nWybierz (1-2): ").strip()
        if choice == "1":
            return "post"
        elif choice == "2":
            return "thread"
        else:
            print("❌ Wpisz 1 lub 2")


def select_polish_platform() -> str:
    """Select platform for polish mode."""
    print("\n📱 DLA JAKIEJ PLATFORMY TEN TEKST? (opcjonalne)")
    print("─" * 40)
    print("  [1] 💼 LinkedIn")
    print("  [2] 👥 Facebook")
    print("  [3] 🐦 X (Twitter)")
    print("  [4] 🦋 Bluesky")
    print("  [5] 🧵 Threads")
    print("  [6] 🎬 Instagram/YouTube (tekst do kamery)")
    print("  [0] ⏭️  Pomiń (ogólna ocena)")
    print("─" * 40)

    platform_map = {
        "1": "linkedin",
        "2": "facebook",
        "3": "x_twitter",
        "4": "bluesky",
        "5": "threads",
        "6": "instagram_reels",
        "0": None,
        "": None,
    }

    choice = input("\nWybierz (0-6) [Enter = pomiń]: ").strip()
    return platform_map.get(choice)


def display_exploration_report(report: dict):
    """Display exploration report in readable format."""
    exploration = report.get("exploration_report", {})

    print("\n" + "═" * 60)
    print("📊 RAPORT EKSPLORACYJNY")
    print("═" * 60)

    # Możliwe kąty
    print("\n🎯 MOŻLIWE KĄTY:")
    print("─" * 40)
    for i, angle in enumerate(exploration.get("możliwe_kąty", []), 1):
        print(f"\n  [{i}] {angle.get('nazwa', 'Kąt')}")
        print(f"      {angle.get('opis', '')}")
        print(f"      Hook: \"{angle.get('hook', '')}\"")
        print(f"      Dla kogo: {angle.get('dla_kogo', '')}")
        print(f"      Siła: {'█' * angle.get('siła', 0)}{'░' * (10 - angle.get('siła', 0))} {angle.get('siła', 0)}/10")

    # Punkty napięcia
    tensions = exploration.get("punkty_napięcia", [])
    if tensions:
        print("\n⚡ PUNKTY NAPIĘCIA:")
        print("─" * 40)
        for t in tensions:
            print(f"  • {t.get('napięcie', '')}")

    # Polski kontekst
    polish_ctx = exploration.get("polski_kontekst", [])
    if polish_ctx:
        print("\n🇵🇱 POLSKI KONTEKST:")
        print("─" * 40)
        for ctx in polish_ctx:
            print(f"  • {ctx.get('kontekst', '')}: {ctx.get('jak_podpiąć', '')}")

    # Pytania
    questions = exploration.get("pytania_warte_zadania", [])
    if questions:
        print("\n❓ PYTANIA WARTE ZADANIA:")
        print("─" * 40)
        for q in questions:
            print(f"  • {q}")

    # Pułapki
    traps = exploration.get("pułapki_do_uniknięcia", [])
    if traps:
        print("\n⚠️  PUŁAPKI DO UNIKNIĘCIA:")
        print("─" * 40)
        for trap in traps:
            print(f"  • {trap.get('pułapka', '')}")

    # Rekomendacja
    rec = exploration.get("rekomendowany_kąt", {})
    if rec:
        print("\n" + "═" * 60)
        print("🏆 REKOMENDOWANY KĄT:")
        print(f"   {rec.get('nazwa', '')}")
        print(f"   {rec.get('uzasadnienie', '')}")
        print(f"   Hook: \"{rec.get('hook', '')}\"")
        print("═" * 60)


def display_development_report(report: dict):
    """Display development report in readable format."""
    dev = report.get("development_report", {})

    print("\n" + "═" * 60)
    print("📊 RAPORT ROZWINIĘCIA")
    print("═" * 60)

    # Ocena kierunku
    assessment = dev.get("ocena_kierunku", {})
    if assessment:
        print("\n📝 TWÓJ KIERUNEK:")
        print("─" * 40)
        print(f"   \"{assessment.get('kierunek_usera', '')}\"")
        score = assessment.get('ocena', 0)
        print(f"   Ocena: {'█' * score}{'░' * (10 - score)} {score}/10")
        print(f"   Co działa: {assessment.get('co_działa', '')}")
        print(f"   Co ulepszyć: {assessment.get('co_ulepszyć', '')}")

    # Warianty
    print("\n🔀 WARIANTY ROZWINIĘCIA:")
    print("─" * 40)
    for variant in dev.get("warianty_rozwinięcia", []):
        print(f"\n  [{variant.get('typ', '')}]")
        print(f"   {variant.get('opis', '')}")
        print(f"   Teza: {variant.get('główna_teza', '')}")
        print(f"   Hook: \"{variant.get('hook', '')}\"")
        print(f"   Potencjał: {variant.get('potencjał', 0)}/10 | Ryzyko: {variant.get('ryzyko', '')}")

    # Propozycje hooków
    hooks = dev.get("propozycje_hooków", [])
    if hooks:
        print("\n🎣 PROPOZYCJE HOOKÓW:")
        print("─" * 40)
        for i, hook in enumerate(hooks, 1):
            print(f"   {i}. \"{hook}\"")

    # Co wzmocnić / pominąć
    strengthen = dev.get("co_wzmocnić", [])
    if strengthen:
        print("\n💪 CO WZMOCNIĆ:")
        print("─" * 40)
        for item in strengthen:
            print(f"   • {item.get('element', '')}")

    skip = dev.get("co_pominąć", [])
    if skip:
        print("\n🚫 CO POMINĄĆ:")
        print("─" * 40)
        for item in skip:
            print(f"   • {item.get('element', '')}")

    # Kontrargumenty
    counters = dev.get("kontrargumenty", [])
    if counters:
        print("\n👿 KONTRARGUMENTY:")
        print("─" * 40)
        for c in counters:
            print(f"   Obiekcja: {c.get('obiekcja', '')}")
            print(f"   → Odpowiedź: {c.get('jak_odpowiedzieć', '')}")
            print()

    # Rekomendacja
    rec = dev.get("rekomendowany_wariant", {})
    if rec:
        print("═" * 60)
        print("🏆 REKOMENDOWANY WARIANT:")
        print(f"   {rec.get('typ', '')}")
        print(f"   {rec.get('uzasadnienie', '')}")
        print(f"   Hook: \"{rec.get('hook', '')}\"")
        print("═" * 60)


def display_polish_report(report: dict):
    """Display polish report in readable format."""
    quality = report.get("quality_report", {})

    # Jeśli to PolishReport (z metodą polish)
    if "oryginalny_tekst" in quality or "ocena" in quality:
        print("\n" + "═" * 60)
        print("📊 RAPORT SZLIFU")
        print("═" * 60)

        score = quality.get("ocena", 0)
        status = quality.get("status", "?")
        print(f"\n📈 OCENA: {'█' * score}{'░' * (10 - score)} {score}/10 [{status}]")

        # Mocne strony
        strengths = quality.get("mocne_strony", [])
        if strengths:
            print("\n✅ MOCNE STRONY:")
            print("─" * 40)
            for s in strengths:
                print(f"   • {s}")

        # Problemy
        issues = quality.get("problemy", [])
        if issues:
            print("\n❌ PROBLEMY:")
            print("─" * 40)
            for issue in issues:
                if isinstance(issue, dict):
                    print(f"   • {issue.get('problem', '')}")
                    print(f"     Gdzie: {issue.get('gdzie', '')}")
                else:
                    print(f"   • {issue}")

        # Poprawki inline
        corrections = quality.get("poprawki_inline", [])
        if corrections:
            print("\n🔧 POPRAWKI:")
            print("─" * 40)
            for corr in corrections:
                print(f"   BYŁO: \"{corr.get('oryginał', '')}\"")
                print(f"   JEST: \"{corr.get('poprawka', '')}\"")
                print(f"   Powód: {corr.get('powód', '')}")
                print()

        # Wersja po poprawkach
        improved = quality.get("wersja_po_poprawkach", "")
        if improved:
            print("\n" + "═" * 60)
            print("📝 WERSJA PO POPRAWKACH:")
            print("─" * 40)
            print(improved)
            print("─" * 40)

        # Alternatywne hooki
        alt_hooks = quality.get("alternatywne_hooki", [])
        if alt_hooks:
            print("\n🎣 ALTERNATYWNE HOOKI:")
            print("─" * 40)
            for i, hook in enumerate(alt_hooks, 1):
                print(f"   {i}. \"{hook}\"")

        print("═" * 60)

    # Wyświetl wyniki agentów analitycznych
    analytical_results = report.get("analytical_results", {})
    if analytical_results:
        print("\n" + "═" * 60)
        print("📊 ANALIZY DODATKOWE")
        print("═" * 60)

        for agent_key, result in analytical_results.items():
            if not result.get("success"):
                continue

            name_pl = result.get("name_pl", agent_key)
            data = result.get("data", {})

            print(f"\n{'─' * 60}")
            print(f"🔬 {name_pl}")
            print("─" * 60)

            # Wyświetl dane w zależności od agenta
            if agent_key == "anthropologist":
                # Perspektywa etnograficzna
                ethno = data.get("perspektywa_etnograficzna", {})
                if ethno:
                    print("\n🎭 PERSPEKTYWA ETNOGRAFICZNA:")
                    for scene in ethno.get("sceny", [])[:2]:
                        print(f"   • {scene.get('nazwa', '')}: {scene.get('znaczenie', '')}")

                # Perspektywa psychologiczna
                psych = data.get("perspektywa_psychologiczna", {})
                if psych:
                    print("\n🧠 PERSPEKTYWA PSYCHOLOGICZNA:")
                    for emotion in psych.get("emocje", [])[:3]:
                        print(f"   • {emotion.get('emocja', '')}: {emotion.get('wyzwalacz', '')}")

            elif agent_key == "polish_contextualizer":
                # Przeliczenia
                conversions = data.get("przeliczenia_na_pl", [])
                if conversions:
                    print("\n🇵🇱 PRZELICZENIA NA POLSKIE REALIA:")
                    for conv in conversions[:3]:
                        print(f"   • {conv.get('oryginał', '')} → {conv.get('polski_odpowiednik', '')}")

                # Polskie tematy
                topics = data.get("polskie_tematy", [])
                if topics:
                    print("\n📌 POLSKIE TEMATY DO PODPIĘCIA:")
                    for topic in topics[:3]:
                        print(f"   • {topic.get('temat', '')}: {topic.get('jak_podpiąć', '')}")

            elif agent_key == "popculture_curator":
                # Analogie filmowe
                films = data.get("analogie_filmowe", [])
                if films:
                    print("\n🎬 ANALOGIE FILMOWE:")
                    for film in films[:2]:
                        print(f"   • {film.get('tytuł', '')}: {film.get('jak_użyć', '')}")

                # Analogie sportowe
                sports = data.get("analogie_sportowe", [])
                if sports:
                    print("\n⚽ ANALOGIE SPORTOWE:")
                    for sport in sports[:2]:
                        print(f"   • {sport.get('wydarzenie', '')}: {sport.get('jak_użyć', '')}")

        print("═" * 60)

    # Wyświetl wyniki dodatkowych agentów recenzujących
    additional_reviews = report.get("additional_reviews", {})
    if additional_reviews:
        print("\n" + "═" * 60)
        print("🔍 DODATKOWE RECENZJE")
        print("═" * 60)

        for agent_key, review in additional_reviews.items():
            if not review.get("success"):
                continue

            name_pl = review.get("name_pl", agent_key)
            score = review.get("score")
            content = review.get("content", "")

            print(f"\n{'─' * 60}")
            score_str = f" [{score}/10]" if score else ""
            print(f"🎭 {name_pl}{score_str}")
            print("─" * 60)

            # Wyświetl treść recenzji (skróconą jeśli za długa)
            if len(content) > 2000:
                print(content[:2000])
                print("\n... (skrócono)")
            else:
                print(content)

        print("═" * 60)

    # Fallback dla starego formatu
    if not ("oryginalny_tekst" in quality or "ocena" in quality):
        print("\n📊 RAPORT JAKOŚCI")
        print(f"   Status: {quality.get('overall_status', '?')}")
        print(f"   Ocena: {quality.get('overall_score', 0)}/10")


def display_draft(draft: dict):
    """Display generated draft."""
    platform = draft.get("platform", "?")
    content = draft.get("content", {})
    draft_format = draft.get("format", "post")

    print("\n" + "═" * 60)
    print(f"📝 DRAFT: {platform.upper()}")
    print("═" * 60)

    if platform == "linkedin":
        print("\n" + content.get("full_post", ""))
        hooks = content.get("hook_variants", [])
        if hooks:
            print("\n🎣 Alternatywne hooki:")
            for i, h in enumerate(hooks, 1):
                print(f"   {i}. {h}")

    elif platform == "facebook":
        print("\n" + content.get("full_post", ""))

    elif platform in ["x_twitter", "bluesky", "threads"]:
        if draft_format == "thread" and content.get("thread"):
            print("\n🧵 WĄTEK:")
            for i, post in enumerate(content["thread"], 1):
                print(f"\n   [{i}] {post}")
        else:
            print(f"\n{content.get('main_post', '')}")
            print(f"\n({content.get('character_count', 0)} znaków)")

        hooks = content.get("hook_variants", [])
        if hooks:
            print("\n🎣 Alternatywne wersje:")
            for i, h in enumerate(hooks, 1):
                print(f"   {i}. {h}")

    elif platform in ["instagram_reels", "youtube_shorts"]:
        print("\n🎬 TEKST DO KAMERY:")
        print("─" * 40)
        print(content.get("tekst_do_kamery", ""))
        print("─" * 40)
        print(f"Szacowany czas: {content.get('szacowany_czas', '?')}")

        hooks = content.get("warianty_hooka", [])
        if hooks:
            print("\n🎣 Alternatywne hooki:")
            for i, h in enumerate(hooks, 1):
                print(f"   {i}. {h}")

        cta = content.get("cta")
        if cta:
            print(f"\n📢 CTA: {cta}")

    print("═" * 60)


def run_interactive():
    """Run interactive CLI session."""
    print_banner()

    # Check configuration
    try:
        config = Config.from_env()
    except Exception as e:
        print(f"❌ Błąd konfiguracji: {e}")
        print("   Upewnij się że plik .env zawiera OPENROUTER_API_KEY")
        sys.exit(1)

    # Select model
    model_key = select_model()
    print(f"\n✅ Model: {AVAILABLE_MODELS[model_key].name}")

    # Select mode
    mode = select_mode()

    # Initialize orchestrator and file reader
    orchestrator = OrchestratorV3(config, model_key)
    file_reader = FileReader()

    # Run based on mode
    if mode == "exploration":
        # Get source content from file
        content = select_source_file(file_reader)

        if not content:
            print("❌ Anulowano.")
            sys.exit(0)

        # Select agents
        selected_agents = select_agents(mode)

        print("\n🔄 Analizuję...")
        result = orchestrator.run_exploration(content, selected_agents=selected_agents, verbose=True)

        if result.success and result.report:
            display_exploration_report(result.report)

            # Ask about draft
            if ask_yes_no("\n📝 Wygenerować draft posta?"):
                platform_group = select_platform_group()

                platform_variant = None
                draft_format = "post"

                if platform_group == "microblog":
                    platform_variant = select_microblog_platform()
                    draft_format = select_draft_format()
                elif platform_group == "video":
                    platform_variant = select_video_platform()

                print("\n🔄 Generuję draft...")
                result = orchestrator.generate_draft(
                    result,
                    platform_group=platform_group,
                    draft_format=draft_format,
                    platform_variant=platform_variant,
                    verbose=True
                )

                if result.draft:
                    display_draft(result.draft)
        else:
            print(f"\n❌ Błąd: {result.errors}")

    elif mode == "development":
        # Get source content from file
        content = select_source_file(file_reader)

        if not content:
            print("❌ Anulowano.")
            sys.exit(0)

        # Get user direction
        print("\n💡 Twój wstępny kierunek/pomysł:")
        user_direction = input("> ").strip()

        if not user_direction:
            print("❌ Nie podano kierunku. Użyj trybu EKSPLORACJA jeśli nie masz pomysłu.")
            sys.exit(1)

        # Select agents
        selected_agents = select_agents(mode)

        print("\n🔄 Analizuję i rozwijam...")
        result = orchestrator.run_development(content, user_direction, selected_agents=selected_agents, verbose=True)

        if result.success and result.report:
            display_development_report(result.report)

            # Ask about draft
            if ask_yes_no("\n📝 Wygenerować draft posta?"):
                platform_group = select_platform_group()

                platform_variant = None
                draft_format = "post"

                if platform_group == "microblog":
                    platform_variant = select_microblog_platform()
                    draft_format = select_draft_format()
                elif platform_group == "video":
                    platform_variant = select_video_platform()

                print("\n🔄 Generuję draft...")
                result = orchestrator.generate_draft(
                    result,
                    platform_group=platform_group,
                    draft_format=draft_format,
                    platform_variant=platform_variant,
                    verbose=True
                )

                if result.draft:
                    display_draft(result.draft)
        else:
            print(f"\n❌ Błąd: {result.errors}")

    elif mode == "polish":
        # Get text to polish - from file or paste
        print("\n✍️ TEKST DO OCENY:")
        print("─" * 40)
        print("  [1] 📂 Wybierz z plików")
        print("  [2] 📋 Wklej tekst")
        print("─" * 40)

        polish_choice = input("\nWybierz (1/2): ").strip()

        if polish_choice == "1":
            text = select_source_file(file_reader)
            if not text:
                print("❌ Anulowano.")
                sys.exit(0)
        else:
            text = get_multiline_input("📋 Wklej tekst do oceny:")
            if not text.strip():
                print("❌ Nie podano tekstu.")
                sys.exit(1)

        # Optionally select platform
        platform = select_polish_platform()

        # Select agents (both analytical and review available in polish mode)
        selected_agents = select_agents(mode)

        # Rozdziel agentów na analitycznych i recenzujących
        analytical_keys = {"anthropologist", "polish_contextualizer", "popculture_curator"}
        review_keys = {"voice_guardian", "opening_sniper", "vulnerability_scanner"}

        selected_analytical = [a for a in selected_agents if a in analytical_keys]
        selected_review = [a for a in selected_agents if a in review_keys]

        print("\n🔄 Analizuję tekst...")

        # Use polish method directly
        polish_report = orchestrator.quality_controller.polish(text, platform)

        # Run analytical agents if selected
        analytical_results = {}
        if selected_analytical:
            analytical_results = orchestrator.run_analytical_agents_for_polish(
                text, selected_analytical, verbose=True
            )

        # Run review agents if selected
        additional_reviews = {}
        if selected_review:
            additional_reviews = orchestrator.run_review_agents(text, selected_review, verbose=True)

        # Wrap in WorkflowResult format for display
        result = type('Result', (), {
            'success': True,
            'report': {
                'type': 'polish',
                'quality_report': polish_report.to_dict(),
                'analytical_results': analytical_results,
                'additional_reviews': additional_reviews,
            }
        })()

        display_polish_report(result.report)

    # Ask to save
    if result.success:
        if ask_yes_no("\n💾 Zapisać wyniki do pliku?"):
            if hasattr(result, 'to_dict'):
                # It's a WorkflowResult
                output_path = orchestrator.save_results(result)
            else:
                # Create a minimal result for saving
                from agents.orchestrator_v3 import WorkflowResult
                save_result = WorkflowResult(
                    mode=mode,
                    success=True,
                    report=result.report if hasattr(result, 'report') else None,
                )
                output_path = orchestrator.save_results(save_result)
            print(f"✅ Zapisano: {output_path}")

    print("\n👋 Do zobaczenia!")


def main():
    """Main entry point."""
    run_interactive()


if __name__ == "__main__":
    main()
