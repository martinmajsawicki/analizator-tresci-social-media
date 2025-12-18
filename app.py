"""
Social Media Analyzer - Streamlit UI
Uruchomienie: streamlit run app.py
"""

import streamlit as st
from pathlib import Path
import json
import os

from core.config import Config, AVAILABLE_MODELS
from core.file_reader import FileReader
from core.agent_registry import get_agents_for_mode, get_default_agents_for_mode
from agents.orchestrator_v3 import OrchestratorV3, WorkflowResult


# Konfiguracja strony
st.set_page_config(
    page_title="Social Media Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Stałe
MODE_CONFIG = {
    "exploration": {
        "icon": "🔭",
        "name": "EKSPLORACJA",
        "description": "Mam materiał, nie mam pomysłu",
        "output": "kąty, perspektywy, pytania",
    },
    "development": {
        "icon": "🛠️",
        "name": "ROZWINIĘCIE",
        "description": "Mam materiał + wstępny kierunek",
        "output": "warianty, hooki, kontrargumenty",
    },
    "polish": {
        "icon": "💎",
        "name": "SZLIF",
        "description": "Mam gotowy tekst",
        "output": "ocenę, poprawki, ulepszoną wersję",
    },
}

PLATFORM_CONFIG = {
    "linkedin": {"icon": "💼", "name": "LinkedIn"},
    "facebook": {"icon": "👥", "name": "Facebook"},
    "microblog": {"icon": "🐦", "name": "X / Bluesky / Threads"},
    "video": {"icon": "🎬", "name": "Instagram / YouTube"},
}

CATEGORY_NAMES = {
    "analytical": "📊 Analityczni",
    "review": "🔍 Recenzujący",
    "enhancement": "✨ Ulepszający",
}


def init_session_state():
    """Inicjalizacja stanu sesji."""
    if "result" not in st.session_state:
        st.session_state.result = None
    if "draft" not in st.session_state:
        st.session_state.draft = None


def render_header():
    """Nagłówek aplikacji."""
    st.markdown("""
    <h1 style='text-align: center;'>🎯 Social Media Analyzer</h1>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Sidebar z konfiguracją."""
    with st.sidebar:
        st.header("⚙️ Konfiguracja")

        # Model
        model_options = {key: f"{model.name}" for key, model in AVAILABLE_MODELS.items()}
        selected_model = st.selectbox(
            "Model AI",
            options=list(model_options.keys()),
            format_func=lambda x: model_options[x],
            index=0,
        )

        st.divider()
        st.markdown("**Koszt (estymacja):**")
        model = AVAILABLE_MODELS[selected_model]
        est_cost = (model.price_per_1k_input * 2 + model.price_per_1k_output * 3)
        st.caption(f"~${est_cost:.3f} / analiza")

        return selected_model


def render_mode_tabs():
    """Zakładki trybów pracy."""
    tabs = st.tabs([
        f"{MODE_CONFIG['exploration']['icon']} {MODE_CONFIG['exploration']['name']}",
        f"{MODE_CONFIG['development']['icon']} {MODE_CONFIG['development']['name']}",
        f"{MODE_CONFIG['polish']['icon']} {MODE_CONFIG['polish']['name']}",
    ])

    modes = ["exploration", "development", "polish"]
    return tabs, modes


def render_agent_selection(mode: str) -> list:
    """Wybór agentów dla danego trybu."""
    available_agents = get_agents_for_mode(mode)
    default_agents = get_default_agents_for_mode(mode)

    if not available_agents:
        return []

    st.markdown("#### 🤖 Agenci")

    # Grupuj po kategorii
    categories = {}
    for agent in available_agents:
        if agent.category not in categories:
            categories[agent.category] = []
        categories[agent.category].append(agent)

    # Sprawdź czy trzeba zresetować
    reset_key = f"reset_{mode}"
    if reset_key in st.session_state and st.session_state[reset_key]:
        # Resetuj wszystkie checkboxy do domyślnych
        for agent in available_agents:
            checkbox_key = f"agent_{mode}_{agent.key}"
            st.session_state[checkbox_key] = agent.key in default_agents
        st.session_state[reset_key] = False

    # Inicjalizacja checkboxów przy pierwszym renderze
    for agent in available_agents:
        checkbox_key = f"agent_{mode}_{agent.key}"
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = agent.key in default_agents

    # Przycisk resetu do domyślnych
    if st.button("🔄 Przywróć domyślnych", key=f"default_btn_{mode}", use_container_width=True):
        st.session_state[reset_key] = True
        st.rerun()

    selected = []

    # Checkboxy dla każdej kategorii
    for category, agents in categories.items():
        with st.expander(CATEGORY_NAMES.get(category, category), expanded=True):
            for agent in agents:
                is_default = agent.key in default_agents
                checkbox_key = f"agent_{mode}_{agent.key}"

                label = f"**{agent.name_pl}**" if is_default else agent.name_pl
                help_text = agent.description

                checked = st.checkbox(
                    label,
                    key=checkbox_key,
                    help=help_text,
                )

                if checked:
                    selected.append(agent.key)

    return selected


def render_input_section(mode: str):
    """Sekcja wprowadzania tekstu."""
    config = MODE_CONFIG[mode]

    st.markdown(f"**{config['description']}** → dostajesz: {config['output']}")
    st.divider()

    # Opcje wprowadzania
    input_method = st.radio(
        "Źródło tekstu",
        ["📝 Wklej tekst", "📁 Wybierz plik"],
        horizontal=True,
        key=f"input_method_{mode}",
    )

    content = None

    if input_method == "📝 Wklej tekst":
        content = st.text_area(
            "Tekst do analizy",
            height=200,
            placeholder="Wklej tutaj artykuł, badanie lub tekst do analizy...",
            key=f"text_input_{mode}",
        )
    else:
        file_reader = FileReader()

        # Wybór źródła pliku
        file_source = st.radio(
            "Źródło pliku",
            ["📂 Folder posts/", "📍 Podaj ścieżkę", "📤 Prześlij plik"],
            horizontal=True,
            key=f"file_source_{mode}",
        )

        if file_source == "📂 Folder posts/":
            # Lista plików z folderu posts/
            files = file_reader.list_files()

            if files:
                # Pokaż jako lista z info o dacie i rozmiarze
                file_options = {"-- Wybierz plik --": None}
                file_options.update({f"{f.name} ({f.modified_date}, {f.size_human})": f.path for f in files})

                selected_file = st.selectbox(
                    "Wybierz plik",
                    options=list(file_options.keys()),
                    key=f"file_select_{mode}",
                )

                if selected_file and selected_file != "-- Wybierz plik --":
                    try:
                        content = file_reader.read_file(file_options[selected_file])
                        st.success(f"✅ Wczytano: {len(content)} znaków")
                    except Exception as e:
                        st.error(f"Błąd wczytywania: {e}")
            else:
                st.warning("Brak plików w folderze posts/. Dodaj pliki .txt, .md, .pdf lub .docx")

        elif file_source == "📍 Podaj ścieżkę":
            # Pole na ścieżkę do pliku
            file_path = st.text_input(
                "Ścieżka do pliku",
                placeholder="/Users/.../dokument.txt lub ~/Documents/artykul.pdf",
                key=f"file_path_{mode}",
            )

            if file_path:
                file_info = file_reader.get_file_info(file_path)
                if file_info:
                    try:
                        content = file_reader.read_file(file_info.path)
                        st.success(f"✅ Wczytano: {file_info.name} ({len(content)} znaków)")
                    except Exception as e:
                        st.error(f"Błąd wczytywania: {e}")
                else:
                    st.error("Plik nie istnieje lub format nie jest obsługiwany (.txt, .md, .pdf, .docx)")

        else:  # Prześlij plik
            uploaded = st.file_uploader(
                "Wybierz plik z komputera",
                type=["txt", "md", "pdf", "docx"],
                key=f"upload_{mode}",
            )
            if uploaded:
                try:
                    # Dla txt/md - dekoduj jako tekst
                    if uploaded.name.endswith(('.txt', '.md')):
                        content = uploaded.read().decode("utf-8")
                    # Dla pdf/docx - zapisz tymczasowo i użyj FileReader
                    else:
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded.name).suffix) as tmp:
                            tmp.write(uploaded.read())
                            tmp_path = tmp.name
                        content = file_reader.read_file(tmp_path)
                        os.unlink(tmp_path)

                    st.success(f"✅ Wczytano: {uploaded.name} ({len(content)} znaków)")
                except Exception as e:
                    st.error(f"Błąd wczytywania: {e}")

    # Dla trybu ROZWINIĘCIE - dodatkowe pole na kierunek
    user_direction = None
    if mode == "development":
        st.divider()
        user_direction = st.text_input(
            "🎯 Twój wstępny kierunek/pomysł",
            placeholder="np. 'Podpiąć pod wybory w Polsce', 'Skupić się na aspekcie ekonomicznym'",
            key=f"direction_{mode}",
        )

    return content, user_direction


def render_results(result: WorkflowResult):
    """Wyświetlanie wyników."""
    if not result or not result.success:
        if result and result.errors:
            st.error(f"Błędy: {', '.join(result.errors)}")
        return

    st.divider()
    st.markdown("## 📊 Wyniki")

    report = result.report
    if not report:
        st.warning("Brak raportu")
        return

    # Różne wyświetlanie w zależności od trybu
    if result.mode == "exploration":
        render_exploration_report(report)
    elif result.mode == "development":
        render_development_report(report)
    elif result.mode == "polish":
        render_polish_report(report)

    # Eksport
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Pobierz JSON",
            data=json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            file_name=f"wynik_{result.mode}.json",
            mime="application/json",
        )


def render_brief(report: dict):
    """Wyświetla brief na górze raportu."""
    brief = report.get("brief", {})
    if not brief:
        return

    st.markdown("### 📋 Brief")

    # Najlepsze hooki
    hooks = brief.get("najlepsze_hooki", [])
    if hooks:
        st.markdown("**🎣 Najlepsze hooki:**")
        for hook in hooks[:3]:
            st.info(f"_{hook}_")

    # Kluczowe insighty
    insights = brief.get("kluczowe_insighty", [])
    if insights:
        st.markdown("**💡 Kluczowe insighty:**")
        for insight in insights[:3]:
            st.markdown(f"- {insight}")

    # Gotowe do użycia
    ready = brief.get("gotowe_do_uzycia", [])
    if ready:
        st.markdown("**✅ Gotowe do użycia:**")
        for item in ready[:3]:
            if isinstance(item, dict):
                st.success(f"**{item.get('typ', '')}:** {item.get('tekst', '')}")
            else:
                st.success(item)

    # Polskie konteksty
    polish = brief.get("polskie_konteksty", [])
    if polish:
        st.markdown("**🇵🇱 Polskie konteksty:**")
        for ctx in polish[:3]:
            st.markdown(f"- {ctx}")

    # Ostrzeżenia
    warnings = brief.get("ostrzezenia", [])
    if warnings:
        st.markdown("**⚠️ Ostrzeżenia:**")
        for warning in warnings[:3]:
            st.warning(warning)

    st.divider()


def render_exploration_report(report: dict):
    """Raport eksploracyjny."""
    # Brief na górze
    render_brief(report)

    # Pobierz exploration_report
    exploration = report.get("exploration_report", {})

    # Możliwe kąty
    angles = exploration.get("możliwe_kąty", [])
    if angles:
        st.markdown("### 🎯 Możliwe kąty")
        for i, angle in enumerate(angles, 1):
            with st.expander(f"**[{i}] {angle.get('nazwa', 'Kąt')}**", expanded=i<=2):
                st.markdown(angle.get("opis", ""))
                if angle.get("hook"):
                    st.info(f"💡 Hook: {angle['hook']}")
                if angle.get("siła"):
                    strength = angle["siła"]
                    st.progress(strength / 10, text=f"Siła: {strength}/10")
                if angle.get("dla_kogo"):
                    st.caption(f"Dla: {angle['dla_kogo']}")

    # Punkty napięcia
    tensions = exploration.get("punkty_napięcia", [])
    if tensions:
        st.markdown("### ⚡ Punkty napięcia")
        for t in tensions:
            if isinstance(t, dict):
                st.markdown(f"**{t.get('napięcie', '')}**")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"Strona A: {t.get('strona_A', '')}")
                with col2:
                    st.markdown(f"Strona B: {t.get('strona_B', '')}")
            else:
                st.markdown(f"- {t}")

    # Polski kontekst
    polish = exploration.get("polski_kontekst", [])
    if polish:
        st.markdown("### 🇵🇱 Polski kontekst")
        for ctx in polish:
            if isinstance(ctx, dict):
                st.markdown(f"- **{ctx.get('kontekst', '')}:** {ctx.get('jak_podpiąć', '')}")
            else:
                st.markdown(f"- {ctx}")

    # Pytania warte zadania
    questions = exploration.get("pytania_warte_zadania", [])
    if questions:
        st.markdown("### ❓ Pytania warte zadania")
        for q in questions:
            st.markdown(f"- {q}")

    # Pułapki do uniknięcia
    traps = exploration.get("pułapki_do_uniknięcia", [])
    if traps:
        st.markdown("### ⚠️ Pułapki do uniknięcia")
        for trap in traps:
            if isinstance(trap, dict):
                st.warning(f"**{trap.get('pułapka', '')}:** {trap.get('dlaczego_zła', '')}")
            else:
                st.warning(trap)

    # Rekomendowany kąt
    rec = exploration.get("rekomendowany_kąt", {})
    if rec:
        st.markdown("### 🎯 Rekomendowany kąt")
        st.success(f"**{rec.get('nazwa', '')}**")
        st.markdown(rec.get("uzasadnienie", ""))
        if rec.get("hook"):
            st.info(f"💡 Hook: {rec['hook']}")


def render_development_report(report: dict):
    """Raport rozwinięcia."""
    # Brief na górze
    render_brief(report)

    # Pobierz development_report
    dev = report.get("development_report", {})

    # Ocena kierunku
    assessment = dev.get("ocena_kierunku", {})
    if assessment:
        st.markdown("### 📝 Ocena Twojego kierunku")
        st.markdown(f"**Kierunek:** {assessment.get('kierunek_usera', '')}")
        if assessment.get("ocena"):
            st.progress(assessment["ocena"] / 10, text=f"Ocena: {assessment['ocena']}/10")
        st.markdown(f"**Co działa:** {assessment.get('co_działa', '')}")
        st.markdown(f"**Co ulepszyć:** {assessment.get('co_ulepszyć', '')}")
        if assessment.get("ryzyko"):
            st.warning(f"**Ryzyko:** {assessment['ryzyko']}")

    # Warianty rozwinięcia
    variants = dev.get("warianty_rozwinięcia", [])
    if variants:
        st.markdown("### 🔀 Warianty rozwinięcia")
        for v in variants:
            with st.expander(f"**{v.get('typ', 'Wariant')}** - potencjał: {v.get('potencjał', '?')}/10"):
                st.markdown(v.get("opis", ""))
                if v.get("główna_teza"):
                    st.markdown(f"**Teza:** {v['główna_teza']}")
                if v.get("hook"):
                    st.info(f"💡 Hook: {v['hook']}")
                if v.get("ryzyko"):
                    st.caption(f"Ryzyko: {v['ryzyko']}")

    # Propozycje hooków
    hooks = dev.get("propozycje_hooków", [])
    if hooks:
        st.markdown("### 🎣 Propozycje hooków")
        for hook in hooks:
            st.info(f"_{hook}_")

    # Co wzmocnić
    strengthen = dev.get("co_wzmocnić", [])
    if strengthen:
        st.markdown("### 💪 Co wzmocnić")
        for item in strengthen:
            if isinstance(item, dict):
                st.markdown(f"- **{item.get('element', '')}:** {item.get('dlaczego', '')}")
            else:
                st.markdown(f"- {item}")

    # Co pominąć
    skip = dev.get("co_pominąć", [])
    if skip:
        st.markdown("### ✂️ Co pominąć")
        for item in skip:
            if isinstance(item, dict):
                st.markdown(f"- **{item.get('element', '')}:** {item.get('dlaczego', '')}")
            else:
                st.markdown(f"- {item}")

    # Kontrargumenty
    counters = dev.get("kontrargumenty", [])
    if counters:
        st.markdown("### 🛡️ Kontrargumenty")
        for c in counters:
            if isinstance(c, dict):
                with st.expander(f"**Obiekcja:** {c.get('obiekcja', '')}"):
                    st.markdown(f"**Odpowiedź:** {c.get('jak_odpowiedzieć', '')}")
            else:
                st.markdown(f"- {c}")

    # Rekomendowany wariant
    rec = dev.get("rekomendowany_wariant", {})
    if rec:
        st.markdown("### 🎯 Rekomendowany wariant")
        st.success(f"**{rec.get('typ', '')}**")
        st.markdown(rec.get("uzasadnienie", ""))
        if rec.get("hook"):
            st.info(f"💡 Hook: {rec['hook']}")


def render_polish_report(report: dict):
    """Raport szlifu."""
    # Pobierz quality_report
    quality = report.get("quality_report", {})

    # Ocena główna
    score = quality.get("ocena", 0)
    status = quality.get("status", "")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Ocena", f"{score}/10")
    with col2:
        status_colors = {"OK": "🟢", "DROBNE POPRAWKI": "🟡", "PRZEPISZ": "🔴"}
        st.markdown(f"### {status_colors.get(status, '⚪')} {status}")

    # Mocne strony
    strengths = quality.get("mocne_strony", [])
    if strengths:
        st.markdown("### ✅ Mocne strony")
        for item in strengths:
            st.markdown(f"- {item}")

    # Problemy
    problems = quality.get("problemy", [])
    if problems:
        st.markdown("### ❌ Problemy")
        for prob in problems:
            if isinstance(prob, dict):
                with st.expander(f"**{prob.get('problem', '')}**"):
                    st.markdown(f"**Gdzie:** {prob.get('gdzie', '-')}")
                    st.markdown(f"**Wpływ:** {prob.get('wpływ', '-')}")
            else:
                st.warning(prob)

    # Poprawki
    fixes = quality.get("poprawki_inline", [])
    if fixes:
        st.markdown("### 🔧 Poprawki")
        for fix in fixes:
            st.markdown("**BYŁO:**")
            st.markdown(f"> {fix.get('oryginał', fix.get('oryginal', ''))}")
            st.markdown("**JEST:**")
            st.success(fix.get("poprawka", ""))
            st.caption(f"Powód: {fix.get('powód', fix.get('powod', '-'))}")
            st.divider()

    # Wersja po poprawkach
    improved = quality.get("wersja_po_poprawkach", "")
    if improved:
        st.markdown("### 📝 Wersja po poprawkach")
        st.text_area(
            "Gotowy tekst (skopiuj)",
            value=improved,
            height=300,
            key="polished_text",
        )

    # Alternatywne hooki
    alt_hooks = quality.get("alternatywne_hooki", [])
    if alt_hooks:
        st.markdown("### 🎣 Alternatywne hooki")
        for hook in alt_hooks:
            st.info(f"_{hook}_")


def render_draft_section(result: WorkflowResult, orchestrator: OrchestratorV3, content: str):
    """Sekcja generowania draftu."""
    if not result or not result.success:
        return

    st.divider()
    st.markdown("## 📝 Generuj draft posta")

    col1, col2 = st.columns(2)

    with col1:
        platform = st.selectbox(
            "Platforma",
            options=list(PLATFORM_CONFIG.keys()),
            format_func=lambda x: f"{PLATFORM_CONFIG[x]['icon']} {PLATFORM_CONFIG[x]['name']}",
        )

    with col2:
        draft_format = "post"
        if platform == "microblog":
            draft_format = st.selectbox(
                "Format",
                options=["post", "thread"],
                format_func=lambda x: "📄 Post" if x == "post" else "🧵 Wątek",
            )

    if st.button("🚀 Generuj draft", type="primary", use_container_width=True):
        with st.spinner("Generuję draft..."):
            try:
                draft_result = orchestrator.generate_draft(
                    workflow_result=result,
                    platform_group=platform,
                    draft_format=draft_format,
                )

                if draft_result and draft_result.draft:
                    st.session_state.draft = draft_result.draft
                    st.success("Draft wygenerowany!")
                else:
                    st.error("Nie udało się wygenerować draftu")
            except Exception as e:
                st.error(f"Błąd: {e}")

    # Wyświetl draft jeśli istnieje
    if st.session_state.draft:
        st.markdown("### Wygenerowany draft")
        draft = st.session_state.draft

        if isinstance(draft, dict):
            content = draft.get("content", {})

            # LinkedIn / Facebook - mają full_post
            if "full_post" in content:
                st.text_area("Treść", value=content["full_post"], height=200)
                if content.get("hashtags"):
                    st.markdown("**Hashtagi:** " + " ".join(content["hashtags"]))
                if content.get("hook_variants"):
                    with st.expander("Alternatywne hooki"):
                        for i, hook in enumerate(content["hook_variants"], 1):
                            st.markdown(f"**{i}.** {hook}")
            # Microblog - wątek
            elif content.get("is_thread") and content.get("thread"):
                for i, tweet in enumerate(content["thread"], 1):
                    st.markdown(f"**[{i}]** {tweet}")
            # Microblog - pojedynczy post
            elif "main_post" in content:
                st.text_area("Treść", value=content["main_post"], height=200)
                if content.get("hook_variants"):
                    with st.expander("Alternatywne wersje"):
                        for i, variant in enumerate(content["hook_variants"], 1):
                            st.markdown(f"**{i}.** {variant}")
            else:
                st.text_area("Treść", value=str(draft), height=200)
        else:
            st.text_area("Treść", value=str(draft), height=200)


def main():
    """Główna funkcja aplikacji."""
    init_session_state()
    render_header()

    # Sidebar
    selected_model = render_sidebar()

    # Zakładki trybów
    tabs, modes = render_mode_tabs()

    for tab, mode in zip(tabs, modes):
        with tab:
            # Wybór agentów
            with st.sidebar:
                st.divider()
                st.markdown(f"### {MODE_CONFIG[mode]['icon']} Agenci dla {MODE_CONFIG[mode]['name']}")
                selected_agents = render_agent_selection(mode)

            # Input
            content, user_direction = render_input_section(mode)

            # Przycisk analizy
            if content:
                if st.button(
                    f"🚀 Analizuj ({MODE_CONFIG[mode]['name']})",
                    type="primary",
                    use_container_width=True,
                    key=f"analyze_{mode}",
                ):
                    with st.spinner(f"Analizuję... ({len(selected_agents)} agentów)"):
                        try:
                            config = Config.from_env()
                            orchestrator = OrchestratorV3(config, selected_model)

                            if mode == "exploration":
                                result = orchestrator.run_exploration(
                                    content,
                                    selected_agents=selected_agents,
                                    verbose=False,
                                )
                            elif mode == "development":
                                result = orchestrator.run_development(
                                    content,
                                    user_direction=user_direction or "",
                                    selected_agents=selected_agents,
                                    verbose=False,
                                )
                            elif mode == "polish":
                                result = orchestrator.run_polish(
                                    content,
                                    verbose=False,
                                )

                            st.session_state.result = result
                            st.session_state.orchestrator = orchestrator
                            st.session_state.content = content

                        except Exception as e:
                            st.error(f"Błąd: {e}")
                            import traceback
                            st.code(traceback.format_exc())

            # Wyniki
            if st.session_state.result and st.session_state.result.mode == mode:
                render_results(st.session_state.result)

                # Draft (tylko dla exploration i development)
                if mode in ["exploration", "development"]:
                    if hasattr(st.session_state, "orchestrator") and hasattr(st.session_state, "content"):
                        render_draft_section(
                            st.session_state.result,
                            st.session_state.orchestrator,
                            st.session_state.content,
                        )


if __name__ == "__main__":
    main()
