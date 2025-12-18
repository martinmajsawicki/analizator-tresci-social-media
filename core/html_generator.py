"""Generator raportów HTML - prosty, czytelny layout."""
import json
import os
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Optional


def generate_html_report(
    full_report: dict,
    output_dir: str,
    mode: str = "exploration",
    auto_open: bool = True
) -> str:
    """
    Generuje raport HTML z danych JSON.

    Args:
        full_report: Pełny raport ze wszystkich agentów
        output_dir: Katalog wyjściowy
        mode: Tryb (exploration/development/polish)
        auto_open: Czy automatycznie otworzyć w przeglądarce

    Returns:
        Ścieżka do wygenerowanego pliku HTML
    """
    html_content = _build_html(full_report, mode)

    output_path = os.path.join(output_dir, "report.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    if auto_open:
        webbrowser.open(f"file://{os.path.abspath(output_path)}")

    return output_path


def _build_html(report: dict, mode: str) -> str:
    """Buduje zawartość HTML - prosty linearny layout."""

    mode_names = {
        "exploration": "EKSPLORACJA",
        "development": "ROZWINIĘCIE",
        "polish": "SZLIF"
    }
    mode_name = mode_names.get(mode, mode.upper())

    inner_report = report.get("report", {})
    report_type = inner_report.get("type", mode)

    # Buduj sekcje w zależności od trybu
    content_html = ""

    # Brief - na samej górze (jeśli dostępny)
    brief_html = _build_brief_section(inner_report)

    if report_type == "exploration":
        content_html = _build_exploration_content(inner_report)
    elif report_type == "development":
        content_html = _build_development_content(inner_report)
    elif report_type == "polish":
        content_html = _build_polish_content(inner_report)

    # Zbierz hooki z agentów analitycznych
    hooks_html = _build_hooks_section(inner_report)

    # Sekcje agentów
    agents_html = _build_agents_section(inner_report)

    return f'''<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Media Analyzer - {mode_name}</title>
    <style>
        :root {{
            --bg: #1a1a2e;
            --bg-light: #25253d;
            --accent: #4361ee;
            --accent2: #7209b7;
            --green: #06d6a0;
            --yellow: #ffd166;
            --text: #f0f0f5;
            --text-dim: #9090a0;
            --border: #3a3a5a;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.7;
            padding: 2rem;
            max-width: 900px;
            margin: 0 auto;
        }}

        h1 {{
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .meta {{
            color: var(--text-dim);
            margin-bottom: 2rem;
            font-size: 0.9rem;
        }}

        h2 {{
            font-size: 1.3rem;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--accent);
            color: var(--accent);
        }}

        h3 {{
            font-size: 1.1rem;
            margin: 1.5rem 0 0.5rem 0;
            color: var(--text);
        }}

        p {{ margin-bottom: 1rem; }}

        .hook {{
            background: var(--bg-light);
            border-left: 4px solid var(--accent);
            padding: 1rem 1.5rem;
            margin: 1rem 0;
            border-radius: 0 8px 8px 0;
        }}

        .hook-text {{
            font-size: 1.05rem;
            font-style: italic;
        }}

        .hook-meta {{
            display: flex;
            justify-content: space-between;
            margin-top: 0.5rem;
            font-size: 0.85rem;
            color: var(--text-dim);
        }}

        .strength {{
            color: var(--green);
            font-weight: 700;
        }}

        .card {{
            background: var(--bg-light);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem 1.5rem;
            margin: 1rem 0;
        }}

        .card-title {{
            font-weight: 600;
            color: var(--accent);
            margin-bottom: 0.5rem;
        }}

        .tension {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin: 0.5rem 0;
        }}

        .tension-side {{
            background: var(--bg);
            padding: 0.75rem;
            border-radius: 6px;
            font-size: 0.9rem;
        }}

        .tension-side strong {{
            color: var(--accent);
        }}

        ul {{
            margin: 0.5rem 0 1rem 1.5rem;
        }}

        li {{
            margin-bottom: 0.5rem;
        }}

        .quote {{
            background: var(--bg);
            border-left: 3px solid var(--accent2);
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            font-style: italic;
            color: var(--text-dim);
        }}

        .recommendation {{
            background: linear-gradient(135deg, rgba(67, 97, 238, 0.15), rgba(114, 9, 183, 0.15));
            border: 1px solid var(--accent);
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1.5rem 0;
        }}

        .recommendation h3 {{
            color: var(--green);
            margin-top: 0;
        }}

        .agent-section {{
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }}

        .agent-title {{
            font-size: 1rem;
            color: var(--accent2);
            margin-bottom: 1rem;
        }}

        .agent-item {{
            background: var(--bg-light);
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            border-radius: 6px;
            font-size: 0.95rem;
        }}

        .agent-label {{
            font-size: 0.75rem;
            color: var(--accent);
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }}

        footer {{
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
            text-align: center;
            color: var(--text-dim);
            font-size: 0.85rem;
        }}

        @media (max-width: 600px) {{
            body {{ padding: 1rem; }}
            .tension {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <h1>Social Media Analyzer</h1>
    <p class="meta">Tryb: {mode_name} | Wygenerowano: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>

    {brief_html}

    {content_html}

    {hooks_html}

    {agents_html}

    <footer>
        Social Media Analyzer v3
    </footer>
</body>
</html>'''


def _build_brief_section(report: dict) -> str:
    """Buduje sekcję briefu - najważniejsze elementy na górze."""
    brief = report.get("brief", {})
    if not brief:
        return ""

    html = '''
    <div class="recommendation" style="margin-bottom: 2rem;">
        <h2 style="margin-top: 0; border: none; color: var(--green);">📋 Brief</h2>
    '''

    # Najlepsze hooki
    hooks = brief.get("najlepsze_hooki", [])
    if hooks:
        html += '<h3 style="margin-top: 1rem;">🎣 Najlepsze hooki</h3>'
        for i, hook in enumerate(hooks[:3], 1):
            html += f'<div class="hook"><div class="hook-text">{i}. {hook}</div></div>'

    # Kluczowe insighty
    insights = brief.get("kluczowe_insighty", [])
    if insights:
        html += '<h3>💡 Kluczowe insighty</h3><ul>'
        for insight in insights[:3]:
            html += f'<li>{insight}</li>'
        html += '</ul>'

    # Gotowe do użycia
    ready = brief.get("gotowe_do_uzycia", [])
    if ready:
        html += '<h3>✅ Gotowe do użycia</h3>'
        for item in ready[:3]:
            if isinstance(item, dict):
                typ = item.get("typ", "Element")
                text = item.get("tekst", "")
                html += f'<div class="agent-item"><div class="agent-label">{typ}</div>{text}</div>'
            else:
                html += f'<div class="agent-item">{item}</div>'

    # Polskie konteksty
    polish = brief.get("polskie_konteksty", [])
    if polish:
        html += '<h3>🇵🇱 Polskie konteksty</h3><ul>'
        for ctx in polish[:3]:
            html += f'<li>{ctx}</li>'
        html += '</ul>'

    # Ostrzeżenia
    warnings = brief.get("ostrzezenia", [])
    if warnings:
        html += '<h3 style="color: #ff6b6b;">⚠️ Ostrzeżenia</h3><ul>'
        for warning in warnings[:3]:
            html += f'<li style="color: #ff9f43;">{warning}</li>'
        html += '</ul>'

    html += '</div>'
    return html


def _build_exploration_content(report: dict) -> str:
    """Buduje treść dla trybu EKSPLORACJA."""
    exploration = report.get("exploration_report", {})
    if not exploration:
        return ""

    html = ""

    # Możliwe kąty
    angles = exploration.get("możliwe_kąty", [])
    if angles:
        html += "<h2>Możliwe kąty</h2>"
        for angle in angles:
            html += f'''
            <div class="card">
                <div class="card-title">{angle.get("nazwa", "Kąt")}</div>
                <p>{angle.get("opis", "")}</p>
                <div class="hook">
                    <div class="hook-text">{angle.get("hook", "")}</div>
                    <div class="hook-meta">
                        <span>Dla: {angle.get("dla_kogo", "")}</span>
                        <span class="strength">{angle.get("siła", "?")}/10</span>
                    </div>
                </div>
            </div>
            '''

    # Punkty napięcia
    tensions = exploration.get("punkty_napięcia", [])
    if tensions:
        html += "<h2>Punkty napięcia</h2>"
        for t in tensions:
            html += f'''
            <div class="card">
                <div class="card-title">{t.get("napięcie", "")}</div>
                <div class="tension">
                    <div class="tension-side"><strong>Strona A:</strong> {t.get("strona_A", "")}</div>
                    <div class="tension-side"><strong>Strona B:</strong> {t.get("strona_B", "")}</div>
                </div>
            </div>
            '''

    # Polski kontekst
    polish = exploration.get("polski_kontekst", [])
    if polish:
        html += "<h2>Polski kontekst</h2><ul>"
        for ctx in polish:
            html += f'<li><strong>{ctx.get("kontekst", "")}:</strong> {ctx.get("jak_podpiąć", "")}</li>'
        html += "</ul>"

    # Pytania
    questions = exploration.get("pytania_warte_zadania", [])
    if questions:
        html += "<h2>Pytania warte zadania</h2><ul>"
        for q in questions:
            html += f'<li>{q}</li>'
        html += "</ul>"

    # Pułapki
    traps = exploration.get("pułapki_do_uniknięcia", [])
    if traps:
        html += "<h2>Pułapki do uniknięcia</h2><ul>"
        for trap in traps:
            html += f'<li><strong>{trap.get("pułapka", "")}:</strong> {trap.get("dlaczego_zła", "")}</li>'
        html += "</ul>"

    # Rekomendacja
    rec = exploration.get("rekomendowany_kąt", {})
    if rec:
        html += f'''
        <div class="recommendation">
            <h3>🎯 Rekomendowany kąt: {rec.get("nazwa", "")}</h3>
            <p>{rec.get("uzasadnienie", "")}</p>
            <div class="hook">
                <div class="hook-text">{rec.get("hook", "")}</div>
            </div>
        </div>
        '''

    return html


def _build_development_content(report: dict) -> str:
    """Buduje treść dla trybu ROZWINIĘCIE."""
    dev = report.get("development_report", {})
    if not dev:
        return ""

    html = ""

    # Ocena kierunku
    assessment = dev.get("ocena_kierunku", {})
    if assessment:
        html += f'''
        <h2>Ocena Twojego kierunku</h2>
        <div class="card">
            <p><strong>Kierunek:</strong> {assessment.get("kierunek_usera", "")}</p>
            <p><strong>Ocena:</strong> <span class="strength">{assessment.get("ocena", "?")}/10</span></p>
            <p><strong>Co działa:</strong> {assessment.get("co_działa", "")}</p>
            <p><strong>Co ulepszyć:</strong> {assessment.get("co_ulepszyć", "")}</p>
        </div>
        '''

    # Warianty
    variants = dev.get("warianty_rozwinięcia", [])
    if variants:
        html += "<h2>Warianty rozwinięcia</h2>"
        for v in variants:
            html += f'''
            <div class="card">
                <div class="card-title">{v.get("typ", "")}</div>
                <p>{v.get("opis", "")}</p>
                <p><strong>Teza:</strong> {v.get("główna_teza", "")}</p>
                <div class="hook">
                    <div class="hook-text">{v.get("hook", "")}</div>
                    <div class="hook-meta">
                        <span>Ryzyko: {v.get("ryzyko", "")}</span>
                        <span class="strength">{v.get("potencjał", "?")}/10</span>
                    </div>
                </div>
            </div>
            '''

    # Hooki
    hooks = dev.get("propozycje_hooków", [])
    if hooks:
        html += "<h2>Propozycje hooków</h2>"
        for i, hook in enumerate(hooks, 1):
            html += f'<div class="hook"><div class="hook-text">{i}. {hook}</div></div>'

    # Rekomendacja
    rec = dev.get("rekomendowany_wariant", {})
    if rec:
        html += f'''
        <div class="recommendation">
            <h3>🎯 Rekomendowany wariant: {rec.get("typ", "")}</h3>
            <p>{rec.get("uzasadnienie", "")}</p>
            <div class="hook">
                <div class="hook-text">{rec.get("hook", "")}</div>
            </div>
        </div>
        '''

    return html


def _build_polish_content(report: dict) -> str:
    """Buduje treść dla trybu SZLIF."""
    quality = report.get("quality_report", {})
    if not quality:
        return ""

    html = ""

    # Ocena
    score = quality.get("ocena", "?")
    status = quality.get("status", "")
    html += f'''
    <h2>Ocena: <span class="strength">{score}/10</span> [{status}]</h2>
    '''

    # Mocne strony
    strengths = quality.get("mocne_strony", [])
    if strengths:
        html += "<h3>✅ Mocne strony</h3><ul>"
        for s in strengths:
            html += f'<li>{s}</li>'
        html += "</ul>"

    # Problemy
    issues = quality.get("problemy", [])
    if issues:
        html += "<h3>❌ Problemy</h3>"
        for issue in issues:
            if isinstance(issue, dict):
                html += f'''
                <div class="card">
                    <div class="card-title">{issue.get("problem", "")}</div>
                    <p><strong>Gdzie:</strong> {issue.get("gdzie", "")}</p>
                    <p><strong>Wpływ:</strong> {issue.get("wpływ", "")}</p>
                </div>
                '''
            else:
                html += f'<div class="card">{issue}</div>'

    # Poprawki
    corrections = quality.get("poprawki_inline", [])
    if corrections:
        html += "<h3>🔧 Poprawki</h3>"
        for corr in corrections:
            html += f'''
            <div class="card">
                <p><strong>BYŁO:</strong></p>
                <div class="quote">{corr.get("oryginał", corr.get("oryginal", ""))}</div>
                <p><strong>JEST:</strong></p>
                <div class="quote" style="border-color: var(--green);">{corr.get("poprawka", "")}</div>
                <p><em>Powód: {corr.get("powód", corr.get("powod", ""))}</em></p>
            </div>
            '''

    # Wersja po poprawkach
    improved = quality.get("wersja_po_poprawkach", "")
    if improved:
        html += f'''
        <h3>📝 Wersja po poprawkach</h3>
        <div class="card" style="white-space: pre-wrap;">{improved}</div>
        '''

    # Alternatywne hooki
    alt_hooks = quality.get("alternatywne_hooki", [])
    if alt_hooks:
        html += "<h3>🎣 Alternatywne hooki</h3>"
        for i, hook in enumerate(alt_hooks, 1):
            html += f'<div class="hook"><div class="hook-text">{i}. {hook}</div></div>'

    return html


def _build_hooks_section(report: dict) -> str:
    """Buduje sekcję z hookami z agentów analitycznych."""
    hooks = []

    # Zbierz dane z obu struktur (bezpośrednio i z analytical_results)
    resonance_data = report.get("resonance_data", {})
    polish_data = report.get("polish_context_data", {})
    popculture_data = report.get("popculture_data", {})
    story_data = report.get("story_data", {})
    tension_data = report.get("tension_data", {})
    context_shift_data = report.get("context_shift_data", {})
    humor_data = report.get("humor_data", {})
    engagement_data = report.get("engagement_data", {})

    analytical = report.get("analytical_results", {})
    if analytical:
        resonance_data = analytical.get("resonance_hunter", {}).get("data", resonance_data)
        polish_data = analytical.get("polish_contextualizer", {}).get("data", polish_data)
        popculture_data = analytical.get("popculture_curator", {}).get("data", popculture_data)

    # Resonance Hunter
    for item in resonance_data.get("top3", resonance_data.get("rekomendacja_top3", [])):
        if item.get("hook"):
            hooks.append({
                "text": item["hook"],
                "strength": item.get("siła", 7),
                "source": "Resonance Hunter"
            })

    # Polish Contextualizer
    for item in polish_data.get("top3", []):
        text = item.get("hook_pl", item.get("hook", ""))
        if text:
            hooks.append({
                "text": text,
                "strength": item.get("siła", 7),
                "source": "Polski Kontekst"
            })

    # Popculture
    for item in popculture_data.get("top3", []):
        text = item.get("analogia", "")
        if text:
            hooks.append({
                "text": text,
                "strength": item.get("siła", 7),
                "source": "Popkultura"
            })

    # Story Excavator - alternatywne kąty
    for item in story_data.get("alternatywne_katy", []):
        text = item.get("hook", "")
        if text:
            hooks.append({
                "text": text,
                "strength": story_data.get("potencjal_narracyjny", 7),
                "source": "Archeolog Historii"
            })

    # Tension Architect - puenty z paradoksem
    for item in tension_data.get("puenty_paradoks", []):
        text = item.get("puenta", "")
        if text:
            hooks.append({
                "text": text,
                "strength": tension_data.get("napiecie_lacznie", 7),
                "source": "Architekt Napięcia"
            })

    # Context Shifter - perspektywa obserwatora
    observer = context_shift_data.get("perspektywa_obserwatora", {})
    if observer.get("hook"):
        hooks.append({
            "text": observer["hook"],
            "strength": context_shift_data.get("poziom_glebi", 7),
            "source": "Antropolog Absurdu"
        })

    # Engagement - CTA platformy
    cta_platform = engagement_data.get("cta_platformy", {})
    for platform, cta in cta_platform.items():
        if cta:
            hooks.append({
                "text": f"[{platform.upper()}] {cta}",
                "strength": engagement_data.get("potencjal_zaangazowania", 7),
                "source": "Inżynier Zaangażowania"
            })

    # Quality report
    quality = report.get("quality_report", {})
    for hook in quality.get("alternatywne_hooki", []):
        if isinstance(hook, str) and hook:
            hooks.append({
                "text": hook,
                "strength": 8,
                "source": "Quality Controller"
            })

    if not hooks:
        return ""

    # Sortuj i deduplikuj
    hooks.sort(key=lambda x: x.get("strength", 0), reverse=True)
    seen = set()
    unique_hooks = []
    for h in hooks:
        if h["text"] not in seen:
            seen.add(h["text"])
            unique_hooks.append(h)

    # Renderuj
    html = "<h2>Top Hooki z analizy</h2>"
    for hook in unique_hooks[:8]:
        html += f'''
        <div class="hook">
            <div class="hook-text">{hook["text"]}</div>
            <div class="hook-meta">
                <span>{hook["source"]}</span>
                <span class="strength">{hook["strength"]}</span>
            </div>
        </div>
        '''

    return html


def _build_agents_section(report: dict) -> str:
    """Buduje sekcję z raportami agentów analitycznych."""
    html = ""

    # Mapowanie danych - podstawowe agenty
    direct_data = {
        "Antropolog": report.get("depth_data", {}),
        "Polski Kontekstualizator": report.get("polish_context_data", {}),
        "Kurator Popkultury": report.get("popculture_data", {}),
    }

    # Analityk Źródła (fundamentalny)
    source_analysis_data = report.get("source_analysis_data", {})

    # Nowe agenty kreatywne
    creative_data = {
        "Archeolog Historii": report.get("story_data", {}),
        "Architekt Napięcia": report.get("tension_data", {}),
        "Antropolog Absurdu": report.get("context_shift_data", {}),
        "Komik": report.get("humor_data", {}),
        "Inżynier Zaangażowania": report.get("engagement_data", {}),
        "Adwokat Diabła": report.get("critique_data", {}),
    }

    analytical = report.get("analytical_results", {})
    if analytical:
        if analytical.get("anthropologist", {}).get("data"):
            direct_data["Antropolog"] = analytical["anthropologist"]["data"]
        if analytical.get("polish_contextualizer", {}).get("data"):
            direct_data["Polski Kontekstualizator"] = analytical["polish_contextualizer"]["data"]
        if analytical.get("popculture_curator", {}).get("data"):
            direct_data["Kurator Popkultury"] = analytical["popculture_curator"]["data"]

    # Renderuj Analityk Źródła (jeśli dostępny) - PIERWSZY bo fundamentalny
    if source_analysis_data:
        agent_html = '<div class="agent-section"><h3 class="agent-title">Analityk Źródła</h3>'

        # Werdykt zaufania
        verdict = source_analysis_data.get("werdykt_zaufania", "")
        level = source_analysis_data.get("poziom_zaufania", 0)
        color = {"MOCNE": "var(--green)", "UMIARKOWANE": "var(--yellow)", "SŁABE": "#ff9f43", "WĄTPLIWE": "#ff6b6b"}.get(verdict, "var(--text-dim)")
        agent_html += f'<div class="agent-item"><div class="agent-label">Wiarygodność</div><span style="color:{color};font-weight:bold;">{verdict}</span> ({level}/10)</div>'

        # Tłumaczenie dla laika
        summary = source_analysis_data.get("tlumaczenie_dla_laika", "")
        if summary:
            agent_html += f'<div class="agent-item"><div class="agent-label">Podsumowanie dla laika</div><div class="quote">{summary}</div></div>'

        # Metodologia
        methodology = source_analysis_data.get("jak", {})
        if methodology:
            method_str = f"N={methodology.get('proba_n', '?')}, {methodology.get('metodologia', '')}"
            agent_html += f'<div class="agent-item"><div class="agent-label">Metodologia</div>{method_str}</div>'

        # Kluczowe ograniczenia
        limitations = source_analysis_data.get("ograniczenia", [])
        for lim in limitations[:3]:
            if isinstance(lim, dict):
                impact = lim.get("wplyw", "")
                impact_color = {"KRYTYCZNE": "#ff6b6b", "ISTOTNE": "var(--yellow)", "DROBNE": "var(--text-dim)"}.get(impact, "var(--text-dim)")
                agent_html += f'<div class="agent-item"><div class="agent-label">Ograniczenie <span style="color:{impact_color};">[{impact}]</span></div>{lim.get("ograniczenie", "")} - {lim.get("co_to_znaczy", "")}</div>'

        # Bezpieczne twierdzenia
        safe = source_analysis_data.get("bezpieczne_twierdzenia", [])
        if safe:
            agent_html += '<div class="agent-item"><div class="agent-label">Bezpieczne twierdzenia</div><ul style="margin:0.5rem 0 0 1rem;">'
            for s in safe[:3]:
                agent_html += f'<li style="color:var(--green);">{s}</li>'
            agent_html += '</ul></div>'

        # Ryzykowne twierdzenia
        risky = source_analysis_data.get("ryzykowne_twierdzenia", [])
        if risky:
            agent_html += '<div class="agent-item"><div class="agent-label">Ryzykowne twierdzenia</div><ul style="margin:0.5rem 0 0 1rem;">'
            for r in risky[:3]:
                agent_html += f'<li style="color:#ff6b6b;">{r}</li>'
            agent_html += '</ul></div>'

        agent_html += '</div>'
        html += agent_html

    # Renderuj podstawowe agenty
    for agent_name, data in direct_data.items():
        if not data:
            continue

        agent_html = f'<div class="agent-section"><h3 class="agent-title">{agent_name}</h3>'

        # Antropolog
        if agent_name == "Antropolog":
            for key, label in [("etnografia", "Etnografia"), ("socjologia", "Socjologia"), ("psychologia", "Psychologia")]:
                items = data.get(key, [])
                for item in items[:3]:
                    if isinstance(item, dict):
                        main = item.get("scena", item.get("podzial", item.get("emocja", "")))
                        quote = item.get("cytat", "")
                        agent_html += f'<div class="agent-item"><div class="agent-label">{label}</div>{main}'
                        if quote:
                            agent_html += f'<div class="quote">"{quote}"</div>'
                        agent_html += '</div>'

        # Polski Kontekstualizator
        elif agent_name == "Polski Kontekstualizator":
            for key, label in [("przeliczenia", "Przeliczenia"), ("polskie_tematy", "Polskie tematy"), ("polskie_liczby", "Polskie liczby")]:
                items = data.get(key, [])
                for item in items[:2]:
                    if isinstance(item, dict):
                        main = item.get("polskie", item.get("temat", item.get("co", item.get("zagraniczne", ""))))
                        detail = item.get("jak_podpiac", item.get("liczba", ""))
                        agent_html += f'<div class="agent-item"><div class="agent-label">{label}</div>{main}'
                        if detail:
                            agent_html += f'<br><small>{detail}</small>'
                        agent_html += '</div>'

        # Kurator Popkultury
        elif agent_name == "Kurator Popkultury":
            for key, label in [("filmy_seriale", "Film/Serial"), ("sport", "Sport"), ("codziennosc", "Codzienność")]:
                items = data.get(key, [])
                for item in items[:2]:
                    if isinstance(item, dict):
                        main = item.get("analogia", item.get("źródło", ""))
                        agent_html += f'<div class="agent-item"><div class="agent-label">{label}</div>{main}</div>'

        agent_html += '</div>'
        html += agent_html

    # Renderuj nowe agenty kreatywne
    for agent_name, data in creative_data.items():
        if not data:
            continue

        agent_html = f'<div class="agent-section"><h3 class="agent-title">{agent_name}</h3>'

        # Archeolog Historii
        if agent_name == "Archeolog Historii":
            if data.get("post_narracyjny"):
                agent_html += f'<div class="agent-item"><div class="agent-label">Post narracyjny</div><div class="quote">{data["post_narracyjny"]}</div></div>'
            for item in data.get("alternatywne_katy", [])[:3]:
                if isinstance(item, dict):
                    agent_html += f'<div class="agent-item"><div class="agent-label">{item.get("perspektywa", "Kąt")}</div>{item.get("hook", "")}</div>'

        # Architekt Napięcia
        elif agent_name == "Architekt Napięcia":
            verdict = data.get("werdykt", "")
            if verdict:
                color = {"NAPIĘCIE": "var(--green)", "PRZEWIDYWALNE": "var(--yellow)", "PŁASKIE": "#ff6b6b"}.get(verdict, "var(--text-dim)")
                agent_html += f'<div class="agent-item"><div class="agent-label">Werdykt</div><span style="color:{color};font-weight:bold;">{verdict}</span> (napięcie: {data.get("napiecie_lacznie", "?")}/10)</div>'
            transform = data.get("transformacja", {})
            if transform.get("po"):
                agent_html += f'<div class="agent-item"><div class="agent-label">Transformacja</div><div class="quote">{transform.get("po", "")}</div><small>{transform.get("co_zmienione", "")}</small></div>'

        # Antropolog Absurdu
        elif agent_name == "Antropolog Absurdu":
            verdict = data.get("werdykt", "")
            if verdict:
                color = {"GŁĘBIA": "var(--green)", "POWIERZCHNIA": "var(--yellow)", "MANUAL": "#ff6b6b"}.get(verdict, "var(--text-dim)")
                agent_html += f'<div class="agent-item"><div class="agent-label">Werdykt</div><span style="color:{color};font-weight:bold;">{verdict}</span> (głębia: {data.get("poziom_glebi", "?")}/10)</div>'
            for item in data.get("bledy_poznawcze", [])[:2]:
                if isinstance(item, dict):
                    agent_html += f'<div class="agent-item"><div class="agent-label">{item.get("nazwa", "Błąd")}</div>{item.get("zdanie", item.get("w_kontekscie", ""))}</div>'

        # Komik
        elif agent_name == "Komik":
            agent_html += f'<div class="agent-item"><div class="agent-label">Potencjał humoru</div>{data.get("potencjal_humoru", "?")}/10 (dial: {data.get("rekomendowany_dial", "?")}/5)</div>'
            versions = data.get("wersje_wg_dial", {})
            for key, version in list(versions.items())[:2]:
                if version:
                    agent_html += f'<div class="agent-item"><div class="agent-label">{key}</div><div class="quote">{version}</div></div>'

        # Inżynier Zaangażowania
        elif agent_name == "Inżynier Zaangażowania":
            agent_html += f'<div class="agent-item"><div class="agent-label">Potencjał zaangażowania</div>{data.get("potencjal_zaangazowania", "?")}/10</div>'
            cta = data.get("opcje_cta", {})
            for key, value in list(cta.items())[:3]:
                if value:
                    agent_html += f'<div class="agent-item"><div class="agent-label">CTA: {key}</div>{value}</div>'

        # Adwokat Diabła
        elif agent_name == "Adwokat Diabła":
            verdict = data.get("werdykt", "")
            color = {"OK": "var(--green)", "WYMAGA_POPRAWEK": "var(--yellow)", "NIE_PUBLIKUJ": "#ff6b6b"}.get(verdict, "var(--text-dim)")
            agent_html += f'<div class="agent-item"><div class="agent-label">Werdykt</div><span style="color:{color};font-weight:bold;">{verdict}</span> (siła argumentu: {data.get("sila_argumentu", "?")}/10)</div>'
            for q in data.get("niewygodne_pytania", [])[:3]:
                agent_html += f'<div class="agent-item"><div class="agent-label">Pytanie</div>{q}</div>'

        agent_html += '</div>'
        html += agent_html

    return html
