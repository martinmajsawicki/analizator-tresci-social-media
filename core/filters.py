"""Filtry bazowe, kontekstowe i nieoczywiste dla Łowcy Rezonansu."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class FilterMatch:
    """Wynik dopasowania filtra."""
    filter_type: str  # "bazowy", "kontekstowy", "nieoczywisty"
    filter_name: str
    strength: int  # 1-5
    hook_suggestion: str
    explanation: str


# FILTRY BAZOWE - 7 obaw + 2 zarzuty dotyczące AI
BASE_FEARS = {
    "praca": {
        "name": "AI zabierze nam pracę",
        "keywords": ["automatyzacja", "zastąpi", "bezrobocie", "redukcje", "zwolnienia",
                     "rekrutacja", "CV", "rozmowa kwalifikacyjna", "stanowisko"],
        "hook_templates": [
            "Czy Twój zawód przetrwa do 2030?",
            "AI właśnie przejęła pierwsze stanowisko w Twojej firmie",
            "Twój szef już wie, kogo zastąpi AI. Czy Ty też?",
        ],
    },
    "kreatywnosc": {
        "name": "AI zabije kreatywność",
        "keywords": ["sztuka", "twórczość", "artysta", "pisarz", "muzyka", "design",
                     "kreacja", "wyobraźnia", "oryginalność", "inspiracja"],
        "hook_templates": [
            "Ostatni ludzki artysta właśnie stracił pracę",
            "Maszyna napisała lepszy tekst niż Ty. Co teraz?",
            "Kreatywność umarła. Albo właśnie się narodziła na nowo.",
        ],
    },
    "plagiat_miernota": {
        "name": "AI to maszynka do plagiatu i miernoty",
        "keywords": ["plagiat", "kopiowanie", "średniak", "banalny", "generyczny",
                     "wtórny", "powtarzalny", "nudny", "szablon"],
        "hook_templates": [
            "AI pisze tak samo nudno jak 90% ludzi. Problem?",
            "Twój 'unikalny' content AI wygeneruje w 3 sekundy",
            "Miernota teraz ma własnego asystenta",
        ],
    },
    "inwigilacja": {
        "name": "AI to narzędzie wszechobecnej inwigilacji",
        "keywords": ["prywatność", "dane", "śledzenie", "monitoring", "kamery",
                     "rozpoznawanie", "inwigilacja", "szpiegowanie", "kontrola"],
        "hook_templates": [
            "AI wie o Tobie więcej niż Twoja mama",
            "Twoja twarz jest już w bazie. Przepraszam, ale tak.",
            "Prywatność? To słowo za 5 lat nie będzie istnieć.",
        ],
    },
    "deepfake_klamstwo": {
        "name": "AI zaleje nas kłamstwem (deepfake)",
        "keywords": ["deepfake", "fake news", "dezinformacja", "manipulacja",
                     "fałszywy", "prawda", "kłamstwo", "weryfikacja"],
        "hook_templates": [
            "Ten filmik z Twoim szefem? To nie on.",
            "Za rok nie odróżnisz prawdy od fikcji. I to dosłownie.",
            "Twój głos właśnie został sklonowany. Bez Twojej zgody.",
        ],
    },
    "klimat_planeta": {
        "name": "AI niszczy naszą planetę",
        "keywords": ["energia", "prąd", "centra danych", "ślad węglowy", "klimat",
                     "środowisko", "ekologia", "zasoby", "woda"],
        "hook_templates": [
            "Jeden prompt ChatGPT = 10 wyszukiwań Google. Energia ma cenę.",
            "AI zużywa tyle prądu co małe państwo. Kto za to płaci?",
            "Twój chatbot właśnie wypił szklankę wody. Dosłownie.",
        ],
    },
    "kontrola_singularnosc": {
        "name": "AI jest mądrzejsza od nas i przejmie kontrolę",
        "keywords": ["singularność", "superinteligencja", "AGI", "kontrola",
                     "dominacja", "zagłada", "Skynet", "przejęcie"],
        "hook_templates": [
            "AI właśnie oszukała swojego twórcę. Pierwszy raz.",
            "Czy to już moment, kiedy tracimy kontrolę?",
            "GPT-5 będzie mądrzejszy od 99% ludzi. Kiedy od Ciebie?",
        ],
    },
}

BASE_OBJECTIONS = {
    "nie_inteligentna": {
        "name": "AI w ogóle nie jest inteligentna - oszustwo",
        "keywords": ["hype", "bańka", "przesada", "marketing", "buzzword",
                     "nie rozumie", "papuga", "korelacja", "statystyka"],
        "hook_templates": [
            "AI nie myśli. Ale Ty też nie myślisz, że myśli, prawda?",
            "Największe oszustwo dekady? AI jako 'inteligencja'.",
            "To nie jest AI. To bardzo drogie autouzupełnianie.",
        ],
    },
    "bezuzyteczna": {
        "name": "AI jest tak głupia, że nie ma zastosowania",
        "keywords": ["halucynacje", "błędy", "pomyłki", "nieprzydatna",
                     "zawodna", "niedokładna", "wymyśla", "kłamie"],
        "hook_templates": [
            "AI zmyśliła prawo, które nie istnieje. Prawnik uwierzył.",
            "3 rzeczy, których NIE powierzysz AI. I 1, którą powinieneś.",
            "Twoje 'superinteligentne' narzędzie nie umie liczyć do 10.",
        ],
    },
}


# FILTRY KONTEKSTOWE - tu i teraz
CONTEXTUAL_FILTERS = {
    "polska_polityka": {
        "name": "Polska aktualność polityczna",
        "keywords": ["wybory", "sejm", "prezydent", "PiS", "PO", "KO", "Konfederacja",
                     "Trzaskowski", "Nawrocki", "Tusk", "rząd", "minister"],
        "current_events": [
            "wybory prezydenckie 2025",
            "kampania wyborcza",
        ],
    },
    "polska_gospodarka": {
        "name": "Polska aktualność gospodarcza",
        "keywords": ["inflacja", "ZUS", "podatki", "przedsiębiorcy", "firmy",
                     "ceny", "kredyt", "stopy procentowe", "NBP"],
        "current_events": [],
    },
    "sezonowosc": {
        "name": "Sezonowość",
        "keywords": [],  # Dynamicznie ustalane
        "current_events": [],
    },
    "zawody_grupy": {
        "name": "Konkretne zawody i grupy",
        "keywords": ["programiści", "prawnicy", "lekarze", "nauczyciele",
                     "księgowi", "marketerzy", "copywriterzy", "tłumacze",
                     "graficy", "dziennikarze", "studenci", "emeryci"],
        "current_events": [],
    },
}


# FILTRY NIEOCZYWISTE - poza schematem
UNEXPECTED_FILTERS = {
    "zaskakujace_analogie": {
        "name": "Zaskakujące analogie",
        "patterns": [
            "AI to jak {X} - {nieoczywiste podobieństwo}",
            "To co AI robi z {X}, kiedyś zrobiło {Y} z {Z}",
        ],
        "examples": [
            "AI to jak Excel w latach 80. Wszyscy się śmiali, a potem stracili pracę.",
            "Chatboty to jak automaty telefoniczne - irytujące, ale nieuniknione.",
        ],
    },
    "prowokacyjne_pytania": {
        "name": "Prowokacyjne pytania",
        "patterns": [
            "A co jeśli {kontrowersyjna teza}?",
            "Czy na pewno {powszechne przekonanie}?",
            "Kiedy ostatnio {coś oczywistego} okazało się fałszywe?",
        ],
        "examples": [
            "A co jeśli AI NIE zabierze Ci pracy - tylko sprawi, że staniesz się zbędny?",
            "Czy na pewno chcesz, żeby AI była 'uczciwa'?",
        ],
    },
    "odwrocenia": {
        "name": "Odwrócenia perspektywy",
        "patterns": [
            "A co jeśli to dobrze, że {coś 'złego'}?",
            "Wszyscy mówią {X}, ale co jeśli {nie-X}?",
            "Problem nie w {X}, problem w {Y}",
        ],
        "examples": [
            "A co jeśli to dobrze, że AI pisze przeciętne teksty?",
            "Problem nie w tym, że AI kłamie. Problem w tym, że my jej wierzymy.",
        ],
    },
    "personalizacja": {
        "name": "Personalizacja do czytelnika",
        "patterns": [
            "Twój {konkret} właśnie...",
            "Czy Ty też {zachowanie}?",
            "Ostatni raz gdy Ty {czynność}, AI...",
        ],
        "examples": [
            "Twój LinkedIn właśnie pokazał Ci ten post. AI zdecydowała, że go potrzebujesz.",
            "Czy Ty też udajesz, że rozumiesz AI?",
        ],
    },
}


def get_seasonal_keywords() -> list[str]:
    """Zwraca słowa kluczowe związane z aktualnym sezonem."""
    month = datetime.now().month

    seasonal = {
        1: ["postanowienia", "nowy rok", "podsumowanie", "plany"],
        2: ["walentynki", "miłość", "zima"],
        3: ["wiosna", "kobieta", "dzień kobiet", "początek"],
        4: ["wielkanoc", "wiosna", "zmiana"],
        5: ["majówka", "matka", "dzień matki"],
        6: ["ojciec", "dzień ojca", "wakacje", "egzaminy", "matura"],
        7: ["wakacje", "urlop", "lato", "odpoczynek"],
        8: ["wakacje", "powrót", "przygotowania"],
        9: ["szkoła", "praca", "nowy sezon", "jesień", "powrót"],
        10: ["jesień", "halloween", "zmiana"],
        11: ["niepodległość", "black friday", "zakupy", "singles day"],
        12: ["święta", "boże narodzenie", "podsumowanie", "prezenty", "sylwester"],
    }

    return seasonal.get(month, [])


def analyze_content_for_filters(content: str) -> dict:
    """
    Analizuje treść i zwraca dopasowane filtry.

    Returns:
        dict z kluczami: "bazowe", "kontekstowe", "nieoczywiste"
    """
    content_lower = content.lower()
    results = {
        "bazowe": [],
        "kontekstowe": [],
        "nieoczywiste_suggestions": [],
    }

    # Sprawdź filtry bazowe (obawy)
    for key, fear in BASE_FEARS.items():
        matches = [kw for kw in fear["keywords"] if kw.lower() in content_lower]
        if matches:
            results["bazowe"].append({
                "key": key,
                "name": fear["name"],
                "matched_keywords": matches,
                "hook_templates": fear["hook_templates"],
                "strength": min(5, len(matches) + 1),
            })

    # Sprawdź filtry bazowe (zarzuty)
    for key, objection in BASE_OBJECTIONS.items():
        matches = [kw for kw in objection["keywords"] if kw.lower() in content_lower]
        if matches:
            results["bazowe"].append({
                "key": key,
                "name": objection["name"],
                "matched_keywords": matches,
                "hook_templates": objection["hook_templates"],
                "strength": min(5, len(matches) + 1),
            })

    # Sprawdź filtry kontekstowe
    for key, ctx in CONTEXTUAL_FILTERS.items():
        matches = [kw for kw in ctx["keywords"] if kw.lower() in content_lower]
        if matches:
            results["kontekstowe"].append({
                "key": key,
                "name": ctx["name"],
                "matched_keywords": matches,
                "current_events": ctx.get("current_events", []),
            })

    # Dodaj sezonowe
    seasonal = get_seasonal_keywords()
    seasonal_matches = [kw for kw in seasonal if kw.lower() in content_lower]
    if seasonal_matches:
        results["kontekstowe"].append({
            "key": "sezonowosc",
            "name": "Sezonowość",
            "matched_keywords": seasonal_matches,
            "current_events": [],
        })

    # Sugestie dla filtrów nieoczywistych
    results["nieoczywiste_suggestions"] = [
        {
            "type": "analogia",
            "suggestion": "Znajdź zaskakującą analogię do historycznego wydarzenia lub codziennej sytuacji",
        },
        {
            "type": "pytanie",
            "suggestion": "Zadaj prowokacyjne pytanie kwestionujące oczywistość",
        },
        {
            "type": "odwrocenie",
            "suggestion": "Odwróć perspektywę - co jeśli to co 'złe' jest dobre?",
        },
        {
            "type": "personalizacja",
            "suggestion": "Zacznij od 'Twój...' lub 'Czy Ty też...'",
        },
    ]

    return results


def get_all_base_filters() -> dict:
    """Zwraca wszystkie filtry bazowe do wykorzystania w promptach."""
    return {
        "fears": BASE_FEARS,
        "objections": BASE_OBJECTIONS,
    }


def get_all_contextual_filters() -> dict:
    """Zwraca wszystkie filtry kontekstowe."""
    return CONTEXTUAL_FILTERS


def get_all_unexpected_filters() -> dict:
    """Zwraca wszystkie filtry nieoczywiste."""
    return UNEXPECTED_FILTERS
