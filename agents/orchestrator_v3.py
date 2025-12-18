"""Orchestrator v3 - obsługuje 3 tryby pracy: Eksploracja, Rozwinięcie, Szlif."""

import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal
from dataclasses import dataclass, field

from core.config import Config
from core.openrouter import OpenRouterClient

# Agenci analityczni (PERSPEKTYWY)
from .extractor import ExtractorAgent
from .resonance_hunter import ResonanceHunterAgent
from .anthropologist import AnthropologistAgent
from .polish_contextualizer import PolishContextualizerAgent
from .popculture_curator import PopcultureCuratorAgent
from .story_excavator import StoryExcavatorAgent
from .tension_architect import TensionArchitectAgent
from .context_shifter import ContextShifterAgent
from .source_analyst import SourceAnalystAgent

# Agenci trybu
from .exploration_agent import ExplorationAgent
from .development_agent import DevelopmentAgent

# Agenci platformowi
from .linkedin_agent import LinkedInAgent
from .facebook_agent import FacebookAgent
from .microblog_agent import MicroblogAgent
from .video_agent import VideoAgent

# Kontroler jakości (dla trybu Szlif)
from .quality_controller import QualityControllerAgent

# Agenci recenzujący (KRYTYKA)
from .voice_guardian import VoiceGuardianAgent
from .opening_sniper import OpeningSniperAgent
from .vulnerability_scanner import VulnerabilityScannerAgent
from .devils_advocate import DevilsAdvocateAgent

# Agenci ulepszający (ULEPSZENIA)
from .comedian import ComedianAgent
from .engagement import EngagementAgent

# Brief Synthesizer
from .brief_synthesizer import BriefSynthesizerAgent


# Setup logging
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "orchestrator_v3.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger("orchestrator_v3")


# Typy
WorkflowMode = Literal["exploration", "development", "polish"]
PlatformGroup = Literal["linkedin", "facebook", "microblog", "video"]
DraftFormat = Literal["post", "thread"]


@dataclass
class WorkflowResult:
    """Wynik workflow."""
    mode: str
    success: bool
    report: Optional[dict] = None  # Raport z trybu (eksploracja/rozwinięcie/szlif)
    draft: Optional[dict] = None  # Opcjonalny draft posta
    errors: list = field(default_factory=list)
    total_duration: float = 0.0

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "success": self.success,
            "report": self.report,
            "draft": self.draft,
            "errors": self.errors,
            "total_duration": self.total_duration,
        }


class OrchestratorV3:
    """
    Orchestrator v3 - 3 tryby pracy.

    Tryby:
    1. EKSPLORACJA - Mam materiał, nie mam pomysłu
       → Raport z kątami, perspektywami
       → Opcjonalnie: draft posta

    2. ROZWINIĘCIE - Mam materiał + wstępny kierunek
       → Raport z wariantami, hookami
       → Opcjonalnie: draft posta

    3. SZLIF - Mam gotowy tekst
       → Ocena + poprawki
    """

    def __init__(self, config: Optional[Config] = None, model_key: Optional[str] = None):
        """Inicjalizacja orchestratora."""
        self.config = config or Config.from_env()
        self.model_key = model_key or self.config.default_model
        self.client = OpenRouterClient(self.config)

        logger.info(f"Inicjalizacja OrchestratorV3 z modelem: {self.model_key}")

        # Agenci analityczni (wspólni dla eksploracji i rozwinięcia)
        self.extractor = ExtractorAgent(self.client, self.model_key)
        self.resonance_hunter = ResonanceHunterAgent(self.client, self.model_key)
        self.anthropologist = AnthropologistAgent(self.client, self.model_key)
        self.polish_contextualizer = PolishContextualizerAgent(self.client, self.model_key)
        self.popculture_curator = PopcultureCuratorAgent(self.client, self.model_key)

        # Agenci kreatywni (PERSPEKTYWY - nowe)
        self.story_excavator = StoryExcavatorAgent(self.client, self.model_key)
        self.tension_architect = TensionArchitectAgent(self.client, self.model_key)
        self.context_shifter = ContextShifterAgent(self.client, self.model_key)

        # Analityk źródła (fundamentalny dla wszystkich trybów)
        self.source_analyst = SourceAnalystAgent(self.client, self.model_key)

        # Agenci trybu
        self.exploration_agent = ExplorationAgent(self.client, self.model_key)
        self.development_agent = DevelopmentAgent(self.client, self.model_key)

        # Agenci platformowi (dla opcji draftu)
        self.linkedin_agent = LinkedInAgent(self.client, self.model_key)
        self.facebook_agent = FacebookAgent(self.client, self.model_key)
        self.microblog_agent = MicroblogAgent(self.client, self.model_key)
        self.video_agent = VideoAgent(self.client, self.model_key)

        # Kontroler jakości (dla trybu szlif)
        self.quality_controller = QualityControllerAgent(self.client, self.model_key)

        # Agenci recenzujący (KRYTYKA)
        self.voice_guardian = VoiceGuardianAgent(self.client, self.model_key)
        self.opening_sniper = OpeningSniperAgent(self.client, self.model_key)
        self.vulnerability_scanner = VulnerabilityScannerAgent(self.client, self.model_key)
        self.devils_advocate = DevilsAdvocateAgent(self.client, self.model_key)

        # Agenci ulepszający (ULEPSZENIA)
        self.comedian = ComedianAgent(self.client, self.model_key)
        self.engagement = EngagementAgent(self.client, self.model_key)

        # Brief Synthesizer (używa taniego modelu do ekstrakcji)
        self.brief_synthesizer = BriefSynthesizerAgent(self.client, self.model_key)

        # Mapa wszystkich agentów do wyboru (GRUPY)
        self._perspective_agents_map = {
            "anthropologist": self.anthropologist,
            "polish_contextualizer": self.polish_contextualizer,
            "popculture_curator": self.popculture_curator,
            "story_excavator": self.story_excavator,
            "tension_architect": self.tension_architect,
            "context_shifter": self.context_shifter,
            "source_analyst": self.source_analyst,
        }

        self._review_agents_map = {
            "voice_guardian": self.voice_guardian,
            "opening_sniper": self.opening_sniper,
            "vulnerability_scanner": self.vulnerability_scanner,
            "devils_advocate": self.devils_advocate,
        }

        self._enhancement_agents_map = {
            "comedian": self.comedian,
            "engagement": self.engagement,
        }

        # Połączona mapa wszystkich opcjonalnych agentów
        self._all_agents_map = {
            **self._perspective_agents_map,
            **self._review_agents_map,
            **self._enhancement_agents_map,
        }

    # ==========================================
    # TRYB 1: EKSPLORACJA
    # ==========================================

    def run_exploration(
        self,
        content: str,
        selected_agents: Optional[list] = None,
        verbose: bool = True,
    ) -> WorkflowResult:
        """
        Tryb EKSPLORACJA: Mam materiał, nie mam pomysłu.

        Args:
            content: Tekst źródłowy
            selected_agents: Lista kluczy wybranych agentów (None = wszystkie domyślne)
            verbose: Czy wyświetlać postęp

        Returns:
            WorkflowResult z raportem eksploracyjnym
        """
        import time
        start_time = time.time()

        # Domyślnie wszystkie agenty analityczne + source_analyst
        if selected_agents is None:
            selected_agents = ["source_analyst", "anthropologist", "polish_contextualizer", "popculture_curator"]

        logger.info(f"Rozpoczynam tryb EKSPLORACJA z agentami: {selected_agents}")
        result = WorkflowResult(mode="exploration", success=True)

        try:
            # Etap 1: Ekstrakcja (zawsze)
            if verbose:
                print("🔍 Ekstrakcja danych źródłowych...")
            extracted = self.extractor.extract(content, None)
            extracted_data = extracted.to_dict()

            # Etap 2: Analiza źródła naukowego (jeśli wybrany - REKOMENDOWANY)
            source_analysis_data = {}
            if "source_analyst" in selected_agents:
                if verbose:
                    print("🔬 Analizuję źródło naukowe (metodologia, wiarygodność)...")
                source_analysis = self.source_analyst.analyze_source(content, {"extracted_data": extracted_data})
                source_analysis_data = source_analysis.to_dict()

            # Etap 3: Rezonans (zawsze)
            if verbose:
                print("🎯 Szukam punktów rezonansu...")
            resonance = self.resonance_hunter.hunt(extracted_data, None)
            resonance_data = resonance.to_dict()

            # Etap 4: Antropolog (jeśli wybrany)
            depth_data = {}
            if "anthropologist" in selected_agents:
                if verbose:
                    print("🧠 Pogłębiam analizę (etnografia, socjologia, psychologia)...")
                depth = self.anthropologist.deepen(extracted_data, resonance_data, raw_source_text=content)
                depth_data = depth.to_dict()

            # Etap 4: Polski Kontekstualizator (jeśli wybrany)
            polish_context_data = {}
            if "polish_contextualizer" in selected_agents:
                if verbose:
                    print("🇵🇱 Tłumaczę na polski kontekst...")
                polish_context = self.polish_contextualizer.analyze_polish_context(content, extracted_data)
                polish_context_data = polish_context.to_dict()

            # Etap 5: Kurator Popkultury (jeśli wybrany)
            popculture_data = {}
            if "popculture_curator" in selected_agents:
                if verbose:
                    print("🎬 Szukam analogii popkulturowych...")
                popculture = self.popculture_curator.analyze_popculture(content, extracted_data)
                popculture_data = popculture.to_dict()

            # Etap 6: Nowe agenty kreatywne (jeśli wybrane)
            story_data = {}
            if "story_excavator" in selected_agents:
                if verbose:
                    print("📖 Wydobywam elementy narracyjne...")
                story = self.story_excavator.excavate(content, {"extracted_data": extracted_data})
                story_data = story.to_dict()

            tension_data = {}
            if "tension_architect" in selected_agents:
                if verbose:
                    print("⚡ Analizuję napięcie i paradoksy...")
                tension = self.tension_architect.architect(content, {"extracted_data": extracted_data})
                tension_data = tension.to_dict()

            context_shift_data = {}
            if "context_shifter" in selected_agents:
                if verbose:
                    print("🔬 Szukam głębi i drugiego dna...")
                context_shift = self.context_shifter.shift(content, {"extracted_data": extracted_data})
                context_shift_data = context_shift.to_dict()

            # Etap 7: Agenty ulepszające (jeśli wybrane)
            humor_data = {}
            if "comedian" in selected_agents:
                if verbose:
                    print("😄 Szukam okazji na humor...")
                humor = self.comedian.find_humor(content, {"extracted_data": extracted_data})
                humor_data = humor.to_dict()

            engagement_data = {}
            if "engagement" in selected_agents:
                if verbose:
                    print("💬 Analizuję potencjał zaangażowania...")
                engage = self.engagement.engineer(content, {"extracted_data": extracted_data})
                engagement_data = engage.to_dict()

            # Etap 8: Agenty krytyczne (jeśli wybrane)
            critique_data = {}
            if "devils_advocate" in selected_agents:
                if verbose:
                    print("😈 Przeprowadzam krytyczną analizę...")
                critique = self.devils_advocate.critique(content, {"extracted_data": extracted_data})
                critique_data = critique.to_dict()

            # Etap 9: Eksploracja (zawsze)
            if verbose:
                print("🔬 Generuję perspektywy i kąty...")
            exploration = self.exploration_agent.explore(
                extracted_data, resonance_data, depth_data,
                polish_context_report=polish_context_data,
                popculture_report=popculture_data,
            )

            # Etap 10: Brief Synthesizer - zbierz outputy i stwórz brief
            if verbose:
                print("📋 Tworzę brief z najlepszymi elementami...")

            agent_outputs = {}
            if source_analysis_data:
                agent_outputs["Analityk Źródła"] = json.dumps(source_analysis_data, ensure_ascii=False)
            if depth_data:
                agent_outputs["Antropolog"] = json.dumps(depth_data, ensure_ascii=False)
            if polish_context_data:
                agent_outputs["Polski Kontekstualizator"] = json.dumps(polish_context_data, ensure_ascii=False)
            if popculture_data:
                agent_outputs["Kurator Popkultury"] = json.dumps(popculture_data, ensure_ascii=False)
            if story_data:
                agent_outputs["Archeolog Historii"] = json.dumps(story_data, ensure_ascii=False)
            if tension_data:
                agent_outputs["Architekt Napięcia"] = json.dumps(tension_data, ensure_ascii=False)
            if context_shift_data:
                agent_outputs["Poszerzacz Kontekstu"] = json.dumps(context_shift_data, ensure_ascii=False)
            if humor_data:
                agent_outputs["Komik"] = json.dumps(humor_data, ensure_ascii=False)
            if engagement_data:
                agent_outputs["Inżynier Zaangażowania"] = json.dumps(engagement_data, ensure_ascii=False)
            if critique_data:
                agent_outputs["Adwokat Diabła"] = json.dumps(critique_data, ensure_ascii=False)
            # Dodaj też eksplorację
            agent_outputs["Eksploracja"] = json.dumps(exploration.to_dict(), ensure_ascii=False)

            brief_data = {}
            if agent_outputs:
                brief = self.brief_synthesizer.synthesize(agent_outputs)
                brief_data = brief.to_dict()

            result.report = {
                "type": "exploration",
                "brief": brief_data,  # Brief na górze!
                "exploration_report": exploration.to_dict(),
                "extracted_data": extracted_data,
                "source_analysis_data": source_analysis_data,
                "resonance_data": resonance_data,
                "depth_data": depth_data,
                "polish_context_data": polish_context_data,
                "popculture_data": popculture_data,
                "story_data": story_data,
                "tension_data": tension_data,
                "context_shift_data": context_shift_data,
                "humor_data": humor_data,
                "engagement_data": engagement_data,
                "critique_data": critique_data,
                "raw_source_text": content,
                "selected_agents": selected_agents,
            }

        except Exception as e:
            error_msg = f"Błąd eksploracji: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            result.errors.append(error_msg)
            result.success = False

        result.total_duration = time.time() - start_time
        return result

    # ==========================================
    # TRYB 2: ROZWINIĘCIE
    # ==========================================

    def run_development(
        self,
        content: str,
        user_direction: str,
        selected_agents: Optional[list] = None,
        verbose: bool = True,
    ) -> WorkflowResult:
        """
        Tryb ROZWINIĘCIE: Mam materiał + wstępny kierunek.

        Args:
            content: Tekst źródłowy
            user_direction: Kierunek/pomysł użytkownika
            selected_agents: Lista kluczy wybranych agentów (None = wszystkie domyślne)
            verbose: Czy wyświetlać postęp

        Returns:
            WorkflowResult z raportem rozwinięcia
        """
        import time
        start_time = time.time()

        # Domyślnie wszystkie agenty analityczne + source_analyst
        if selected_agents is None:
            selected_agents = ["source_analyst", "anthropologist", "polish_contextualizer", "popculture_curator"]

        logger.info(f"Rozpoczynam tryb ROZWINIĘCIE z agentami: {selected_agents}, kierunek: {user_direction[:50]}...")
        result = WorkflowResult(mode="development", success=True)

        try:
            # Etap 1: Ekstrakcja (zawsze)
            if verbose:
                print("🔍 Ekstrakcja danych źródłowych...")
            extracted = self.extractor.extract(content, user_direction)
            extracted_data = extracted.to_dict()

            # Etap 2: Analiza źródła naukowego (jeśli wybrany)
            source_analysis_data = {}
            if "source_analyst" in selected_agents:
                if verbose:
                    print("🔬 Analizuję źródło naukowe (metodologia, wiarygodność)...")
                source_analysis = self.source_analyst.analyze_source(content, {"extracted_data": extracted_data})
                source_analysis_data = source_analysis.to_dict()

            # Etap 3: Rezonans (zawsze)
            if verbose:
                print("🎯 Szukam punktów rezonansu...")
            resonance = self.resonance_hunter.hunt(extracted_data, user_direction)
            resonance_data = resonance.to_dict()

            # Etap 4: Antropolog (jeśli wybrany)
            depth_data = {}
            if "anthropologist" in selected_agents:
                if verbose:
                    print("🧠 Pogłębiam analizę (etnografia, socjologia, psychologia)...")
                depth = self.anthropologist.deepen(extracted_data, resonance_data, raw_source_text=content)
                depth_data = depth.to_dict()

            # Etap 4: Polski Kontekstualizator (jeśli wybrany)
            polish_context_data = {}
            if "polish_contextualizer" in selected_agents:
                if verbose:
                    print("🇵🇱 Tłumaczę na polski kontekst...")
                polish_context = self.polish_contextualizer.analyze_polish_context(content, extracted_data)
                polish_context_data = polish_context.to_dict()

            # Etap 5: Kurator Popkultury (jeśli wybrany)
            popculture_data = {}
            if "popculture_curator" in selected_agents:
                if verbose:
                    print("🎬 Szukam analogii popkulturowych...")
                popculture = self.popculture_curator.analyze_popculture(content, extracted_data)
                popculture_data = popculture.to_dict()

            # Etap 6: Nowe agenty kreatywne (jeśli wybrane)
            story_data = {}
            if "story_excavator" in selected_agents:
                if verbose:
                    print("📖 Wydobywam elementy narracyjne...")
                story = self.story_excavator.excavate(content, {"extracted_data": extracted_data})
                story_data = story.to_dict()

            tension_data = {}
            if "tension_architect" in selected_agents:
                if verbose:
                    print("⚡ Analizuję napięcie i paradoksy...")
                tension = self.tension_architect.architect(content, {"extracted_data": extracted_data})
                tension_data = tension.to_dict()

            context_shift_data = {}
            if "context_shifter" in selected_agents:
                if verbose:
                    print("🔬 Szukam głębi i drugiego dna...")
                context_shift = self.context_shifter.shift(content, {"extracted_data": extracted_data})
                context_shift_data = context_shift.to_dict()

            # Etap 7: Agenty ulepszające (jeśli wybrane)
            humor_data = {}
            if "comedian" in selected_agents:
                if verbose:
                    print("😄 Szukam okazji na humor...")
                humor = self.comedian.find_humor(content, {"extracted_data": extracted_data})
                humor_data = humor.to_dict()

            engagement_data = {}
            if "engagement" in selected_agents:
                if verbose:
                    print("💬 Analizuję potencjał zaangażowania...")
                engage = self.engagement.engineer(content, {"extracted_data": extracted_data})
                engagement_data = engage.to_dict()

            # Etap 8: Agenty krytyczne (jeśli wybrane)
            critique_data = {}
            if "devils_advocate" in selected_agents:
                if verbose:
                    print("😈 Przeprowadzam krytyczną analizę...")
                critique = self.devils_advocate.critique(content, {"extracted_data": extracted_data})
                critique_data = critique.to_dict()

            # Etap 9: Rozwinięcie (zawsze)
            if verbose:
                print("🌱 Rozwijam Twój kierunek...")
            development = self.development_agent.develop(
                extracted_data, resonance_data, depth_data, user_direction,
                polish_context_report=polish_context_data,
                popculture_report=popculture_data,
            )

            # Etap 10: Brief Synthesizer - zbierz outputy i stwórz brief
            if verbose:
                print("📋 Tworzę brief z najlepszymi elementami...")

            agent_outputs = {}
            if source_analysis_data:
                agent_outputs["Analityk Źródła"] = json.dumps(source_analysis_data, ensure_ascii=False)
            if depth_data:
                agent_outputs["Antropolog"] = json.dumps(depth_data, ensure_ascii=False)
            if polish_context_data:
                agent_outputs["Polski Kontekstualizator"] = json.dumps(polish_context_data, ensure_ascii=False)
            if popculture_data:
                agent_outputs["Kurator Popkultury"] = json.dumps(popculture_data, ensure_ascii=False)
            if story_data:
                agent_outputs["Archeolog Historii"] = json.dumps(story_data, ensure_ascii=False)
            if tension_data:
                agent_outputs["Architekt Napięcia"] = json.dumps(tension_data, ensure_ascii=False)
            if context_shift_data:
                agent_outputs["Poszerzacz Kontekstu"] = json.dumps(context_shift_data, ensure_ascii=False)
            if humor_data:
                agent_outputs["Komik"] = json.dumps(humor_data, ensure_ascii=False)
            if engagement_data:
                agent_outputs["Inżynier Zaangażowania"] = json.dumps(engagement_data, ensure_ascii=False)
            if critique_data:
                agent_outputs["Adwokat Diabła"] = json.dumps(critique_data, ensure_ascii=False)
            # Dodaj też rozwinięcie
            agent_outputs["Rozwinięcie"] = json.dumps(development.to_dict(), ensure_ascii=False)

            brief_data = {}
            if agent_outputs:
                brief = self.brief_synthesizer.synthesize(agent_outputs)
                brief_data = brief.to_dict()

            result.report = {
                "type": "development",
                "brief": brief_data,  # Brief na górze!
                "development_report": development.to_dict(),
                "user_direction": user_direction,
                "extracted_data": extracted_data,
                "source_analysis_data": source_analysis_data,
                "resonance_data": resonance_data,
                "depth_data": depth_data,
                "polish_context_data": polish_context_data,
                "popculture_data": popculture_data,
                "story_data": story_data,
                "tension_data": tension_data,
                "context_shift_data": context_shift_data,
                "humor_data": humor_data,
                "engagement_data": engagement_data,
                "critique_data": critique_data,
                "raw_source_text": content,
                "selected_agents": selected_agents,
            }

        except Exception as e:
            error_msg = f"Błąd rozwinięcia: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            result.errors.append(error_msg)
            result.success = False

        result.total_duration = time.time() - start_time
        return result

    # ==========================================
    # TRYB 3: SZLIF
    # ==========================================

    def run_polish(
        self,
        text: str,
        platform: Optional[str] = None,
        verbose: bool = True,
    ) -> WorkflowResult:
        """
        Tryb SZLIF: Mam gotowy tekst, chcę ocenę i poprawki.

        Returns:
            WorkflowResult z oceną i poprawkami
        """
        import time
        start_time = time.time()

        logger.info("Rozpoczynam tryb SZLIF")
        result = WorkflowResult(mode="polish", success=True)

        try:
            if verbose:
                print("✍️ Analizuję Twój tekst...")

            # Użyj quality_controller do oceny
            quality_result = self.quality_controller.check_all(
                generated_posts={platform or "unknown": {"full_post": text}},
                user_direction=None,
            )

            result.report = {
                "type": "polish",
                "quality_report": quality_result.to_dict(),
                "original_text": text,
                "platform": platform,
            }

        except Exception as e:
            error_msg = f"Błąd szlifu: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            result.errors.append(error_msg)
            result.success = False

        result.total_duration = time.time() - start_time
        return result

    # ==========================================
    # AGENCI ANALITYCZNI (dla trybu SZLIF)
    # ==========================================

    def run_analytical_agents_for_polish(
        self,
        text: str,
        selected_agents: list[str],
        verbose: bool = True,
    ) -> dict:
        """
        Uruchamia wybrane agenty analityczne dla gotowego tekstu w trybie SZLIF.

        Args:
            text: Tekst do analizy
            selected_agents: Lista kluczy agentów do uruchomienia
            verbose: Czy wyświetlać postęp

        Returns:
            Słownik z wynikami od każdego agenta
        """
        results = {}

        # Najpierw podstawowa ekstrakcja (potrzebna dla innych agentów)
        if verbose:
            print("🔍 Ekstrakcja danych z tekstu...")
        extracted = self.extractor.extract(text, None)
        extracted_data = extracted.to_dict()

        # Antropolog
        if "anthropologist" in selected_agents:
            if verbose:
                print("🧠 Antropolog analizuje tekst...")
            try:
                # Potrzebujemy też resonance dla anthropologa
                resonance = self.resonance_hunter.hunt(extracted_data, None)
                resonance_data = resonance.to_dict()

                depth = self.anthropologist.deepen(extracted_data, resonance_data, raw_source_text=text)
                results["anthropologist"] = {
                    "name_pl": "Antropolog",
                    "data": depth.to_dict(),
                    "success": True,
                }
                if verbose:
                    print("   ✅ Antropolog: gotowe")
            except Exception as e:
                logger.error(f"Błąd Antropologa: {str(e)}")
                results["anthropologist"] = {
                    "name_pl": "Antropolog",
                    "data": {},
                    "success": False,
                    "error": str(e),
                }
                if verbose:
                    print(f"   ❌ Antropolog: błąd - {str(e)}")

        # Polski Kontekstualizator
        if "polish_contextualizer" in selected_agents:
            if verbose:
                print("🇵🇱 Polski Kontekstualizator analizuje tekst...")
            try:
                polish_context = self.polish_contextualizer.analyze_polish_context(text, extracted_data)
                results["polish_contextualizer"] = {
                    "name_pl": "Polski Kontekstualizator",
                    "data": polish_context.to_dict(),
                    "success": True,
                }
                if verbose:
                    print("   ✅ Polski Kontekstualizator: gotowe")
            except Exception as e:
                logger.error(f"Błąd Polskiego Kontekstualizatora: {str(e)}")
                results["polish_contextualizer"] = {
                    "name_pl": "Polski Kontekstualizator",
                    "data": {},
                    "success": False,
                    "error": str(e),
                }
                if verbose:
                    print(f"   ❌ Polski Kontekstualizator: błąd - {str(e)}")

        # Kurator Popkultury
        if "popculture_curator" in selected_agents:
            if verbose:
                print("🎬 Kurator Popkultury analizuje tekst...")
            try:
                popculture = self.popculture_curator.analyze_popculture(text, extracted_data)
                results["popculture_curator"] = {
                    "name_pl": "Kurator Popkultury",
                    "data": popculture.to_dict(),
                    "success": True,
                }
                if verbose:
                    print("   ✅ Kurator Popkultury: gotowe")
            except Exception as e:
                logger.error(f"Błąd Kuratora Popkultury: {str(e)}")
                results["popculture_curator"] = {
                    "name_pl": "Kurator Popkultury",
                    "data": {},
                    "success": False,
                    "error": str(e),
                }
                if verbose:
                    print(f"   ❌ Kurator Popkultury: błąd - {str(e)}")

        return results

    # ==========================================
    # AGENCI RECENZUJĄCY (dla trybu SZLIF)
    # ==========================================

    def run_review_agents(
        self,
        text: str,
        selected_agents: list[str],
        verbose: bool = True,
    ) -> dict:
        """
        Uruchamia wybrane agenty recenzujące dla gotowego tekstu.

        Args:
            text: Tekst do recenzji
            selected_agents: Lista kluczy agentów do uruchomienia
            verbose: Czy wyświetlać postęp

        Returns:
            Słownik z wynikami od każdego agenta
        """
        results = {}

        agent_names = {
            "voice_guardian": "Straznik Glosu",
            "opening_sniper": "Snajper Otwarcia",
            "vulnerability_scanner": "Wykrywacz Skazy",
        }

        for agent_key in selected_agents:
            if agent_key not in self._review_agents_map:
                continue

            agent = self._review_agents_map[agent_key]
            agent_name = agent_names.get(agent_key, agent_key)

            if verbose:
                print(f"🔍 {agent_name} analizuje tekst...")

            try:
                # Legacy agenci używają metody analyze()
                agent_result = agent.analyze(
                    content=text,
                    mode="review",
                    platform=None,
                )

                results[agent_key] = {
                    "name_pl": agent_name,
                    "content": agent_result.content,
                    "score": agent_result.score,
                    "success": agent_result.success,
                    "error": agent_result.error,
                }

                if verbose and agent_result.success:
                    score_str = f"{agent_result.score}/10" if agent_result.score else "brak"
                    print(f"   ✅ {agent_name}: {score_str}")

            except Exception as e:
                logger.error(f"Błąd agenta {agent_key}: {str(e)}")
                results[agent_key] = {
                    "name_pl": agent_name,
                    "content": "",
                    "score": None,
                    "success": False,
                    "error": str(e),
                }
                if verbose:
                    print(f"   ❌ {agent_name}: błąd - {str(e)}")

        return results

    # ==========================================
    # GENEROWANIE DRAFTU (opcjonalne)
    # ==========================================

    def generate_draft(
        self,
        workflow_result: WorkflowResult,
        platform_group: PlatformGroup,
        draft_format: DraftFormat = "post",
        platform_variant: Optional[str] = None,
        verbose: bool = True,
    ) -> WorkflowResult:
        """
        Generuje draft posta na podstawie raportu z eksploracji/rozwinięcia.

        Args:
            workflow_result: Wynik z run_exploration lub run_development
            platform_group: Grupa platform (linkedin, facebook, microblog, video)
            draft_format: Format (post lub thread) - tylko dla microblog
            platform_variant: Wariant platformy (np. x_twitter, bluesky dla microblog)

        Returns:
            WorkflowResult z dodanym draftem
        """
        import time
        start_time = time.time()

        if not workflow_result.report:
            workflow_result.errors.append("Brak raportu do generowania draftu")
            return workflow_result

        # Przygotuj pakiet wejściowy
        report = workflow_result.report
        input_package = {
            "extracted_data": report.get("extracted_data", {}),
            "resonance_report": report.get("resonance_data", {}),
            "depth_report": report.get("depth_data", {}),
            "polish_context_report": report.get("polish_context_data", {}),
            "popculture_report": report.get("popculture_data", {}),
            "user_notes": report.get("user_direction", ""),
            # WAŻNE: Przekaż też oryginalny tekst dla agentów platformowych
            "raw_source_text": report.get("raw_source_text", ""),
        }

        # Dodaj rekomendację z raportu
        if report.get("type") == "exploration":
            exploration_data = report.get("exploration_report", {})
            recommended = exploration_data.get("rekomendowany_kąt", {})
            if recommended:
                input_package["recommended_angle"] = recommended
        elif report.get("type") == "development":
            development_data = report.get("development_report", {})
            recommended = development_data.get("rekomendowany_wariant", {})
            if recommended:
                input_package["recommended_variant"] = recommended

        try:
            if platform_group == "linkedin":
                if verbose:
                    print("📝 Generuję draft dla LinkedIn...")
                post = self.linkedin_agent.generate(input_package)
                workflow_result.draft = {
                    "platform": "linkedin",
                    "content": post.to_dict(),
                }

            elif platform_group == "facebook":
                if verbose:
                    print("📝 Generuję draft dla Facebook...")
                post = self.facebook_agent.generate(input_package)
                workflow_result.draft = {
                    "platform": "facebook",
                    "content": post.to_dict(),
                }

            elif platform_group == "microblog":
                platform = platform_variant or "x_twitter"
                platform_name = {
                    "x_twitter": "X (Twitter)",
                    "bluesky": "Bluesky",
                    "threads": "Threads"
                }.get(platform, platform)

                if verbose:
                    format_name = "wątek" if draft_format == "thread" else "post"
                    print(f"📝 Generuję {format_name} dla {platform_name}...")

                post = self.microblog_agent.generate(
                    input_package,
                    platform=platform,
                    format_type=draft_format,
                )
                workflow_result.draft = {
                    "platform": platform,
                    "format": draft_format,
                    "content": post.to_dict(),
                }

            elif platform_group == "video":
                platform = platform_variant or "instagram_reels"
                platform_name = {
                    "instagram_reels": "Instagram Reels",
                    "youtube_shorts": "YouTube Shorts"
                }.get(platform, platform)

                if verbose:
                    print(f"📝 Generuję tekst wideo dla {platform_name}...")

                script = self.video_agent.generate(input_package, platform=platform)
                workflow_result.draft = {
                    "platform": platform,
                    "content": script.to_dict(),
                }

        except Exception as e:
            error_msg = f"Błąd generowania draftu: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            workflow_result.errors.append(error_msg)

        workflow_result.total_duration += time.time() - start_time
        return workflow_result

    # ==========================================
    # ZAPIS WYNIKÓW
    # ==========================================

    def save_results(
        self,
        result: WorkflowResult,
        output_dir: Optional[str] = None,
        topic_slug: Optional[str] = None,
    ) -> str:
        """Zapisuje wyniki do plików."""
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "output"
        else:
            output_dir = Path(output_dir)

        date_str = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H%M%S")

        if topic_slug:
            base_folder_name = f"{date_str}-{topic_slug}"
        else:
            base_folder_name = f"{date_str}-{time_str}-{result.mode}"

        # Sprawdź czy folder istnieje - jeśli tak, dodaj numer
        folder_name = base_folder_name
        result_dir = output_dir / folder_name
        counter = 1

        while result_dir.exists():
            folder_name = f"{base_folder_name}-{counter}"
            result_dir = output_dir / folder_name
            counter += 1

        result_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Zapisuję wyniki do: {result_dir}")

        # Zapisz pełne wyniki JSON
        full_results = result.to_dict()
        with open(result_dir / "full_results.json", "w", encoding="utf-8") as f:
            json.dump(full_results, f, ensure_ascii=False, indent=2)

        # Zapisz osobne pliki JSON per agent
        self._save_agent_reports(result_dir, result)

        # Generuj i otwórz HTML
        try:
            from core.html_generator import generate_html_report
            html_path = generate_html_report(
                full_report=full_results,
                output_dir=str(result_dir),
                mode=result.mode,
                auto_open=True
            )
            print(f"📊 Raport HTML: {html_path}")
        except Exception as e:
            logger.warning(f"Nie udało się wygenerować HTML: {e}")

        # Zapisz raport w czytelnej formie (markdown backup)
        if result.report:
            self._save_report_markdown(result_dir, result)

        # Zapisz draft jeśli istnieje
        if result.draft:
            self._save_draft_markdown(result_dir, result.draft)

        print(f"\n💾 Wyniki zapisane do: {result_dir}")
        return str(result_dir)

    def _save_report_markdown(self, result_dir: Path, result: WorkflowResult):
        """Zapisuje raport jako markdown."""
        report = result.report
        report_type = report.get("type", "unknown")

        lines = [f"# RAPORT: {report_type.upper()}\n"]
        lines.append(f"*Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

        if report_type == "exploration":
            exploration = report.get("exploration_report", {})

            lines.append("## Możliwe kąty\n")
            for angle in exploration.get("możliwe_kąty", []):
                lines.append(f"### {angle.get('nazwa', 'Kąt')}")
                lines.append(f"**Opis:** {angle.get('opis', '')}")
                lines.append(f"**Hook:** _{angle.get('hook', '')}_")
                lines.append(f"**Dla kogo:** {angle.get('dla_kogo', '')}")
                lines.append(f"**Siła:** {angle.get('siła', 0)}/10\n")

            lines.append("## Punkty napięcia\n")
            for tension in exploration.get("punkty_napięcia", []):
                lines.append(f"- **{tension.get('napięcie', '')}**")
                lines.append(f"  - Strona A: {tension.get('strona_A', '')}")
                lines.append(f"  - Strona B: {tension.get('strona_B', '')}\n")

            lines.append("## Polski kontekst\n")
            for ctx in exploration.get("polski_kontekst", []):
                lines.append(f"- **{ctx.get('kontekst', '')}**: {ctx.get('jak_podpiąć', '')}")

            lines.append("\n## Pytania warte zadania\n")
            for q in exploration.get("pytania_warte_zadania", []):
                lines.append(f"- {q}")

            lines.append("\n## Pułapki do uniknięcia\n")
            for trap in exploration.get("pułapki_do_uniknięcia", []):
                lines.append(f"- **{trap.get('pułapka', '')}**: {trap.get('dlaczego_zła', '')}")

            rec = exploration.get("rekomendowany_kąt", {})
            if rec:
                lines.append(f"\n## 🎯 Rekomendowany kąt\n")
                lines.append(f"**{rec.get('nazwa', '')}**\n")
                lines.append(f"{rec.get('uzasadnienie', '')}\n")
                lines.append(f"**Hook:** _{rec.get('hook', '')}_")

        elif report_type == "development":
            dev = report.get("development_report", {})

            assessment = dev.get("ocena_kierunku", {})
            if assessment:
                lines.append("## Ocena Twojego kierunku\n")
                lines.append(f"**Kierunek:** {assessment.get('kierunek_usera', '')}")
                lines.append(f"**Ocena:** {assessment.get('ocena', 0)}/10")
                lines.append(f"**Co działa:** {assessment.get('co_działa', '')}")
                lines.append(f"**Co ulepszyć:** {assessment.get('co_ulepszyć', '')}")
                lines.append(f"**Ryzyko:** {assessment.get('ryzyko', '')}\n")

            lines.append("## Warianty rozwinięcia\n")
            for variant in dev.get("warianty_rozwinięcia", []):
                lines.append(f"### {variant.get('typ', '')}")
                lines.append(f"**Opis:** {variant.get('opis', '')}")
                lines.append(f"**Główna teza:** {variant.get('główna_teza', '')}")
                lines.append(f"**Hook:** _{variant.get('hook', '')}_")
                lines.append(f"**Potencjał:** {variant.get('potencjał', 0)}/10")
                lines.append(f"**Ryzyko:** {variant.get('ryzyko', '')}\n")

            lines.append("## Propozycje hooków\n")
            for i, hook in enumerate(dev.get("propozycje_hooków", []), 1):
                lines.append(f"{i}. _{hook}_")

            lines.append("\n## Co wzmocnić\n")
            for item in dev.get("co_wzmocnić", []):
                lines.append(f"- **{item.get('element', '')}**: {item.get('dlaczego', '')}")

            lines.append("\n## Co pominąć\n")
            for item in dev.get("co_pominąć", []):
                lines.append(f"- **{item.get('element', '')}**: {item.get('dlaczego', '')}")

            lines.append("\n## Kontrargumenty\n")
            for counter in dev.get("kontrargumenty", []):
                lines.append(f"- **Obiekcja:** {counter.get('obiekcja', '')}")
                lines.append(f"  **Odpowiedź:** {counter.get('jak_odpowiedzieć', '')}\n")

            rec = dev.get("rekomendowany_wariant", {})
            if rec:
                lines.append(f"\n## 🎯 Rekomendowany wariant\n")
                lines.append(f"**{rec.get('typ', '')}**\n")
                lines.append(f"{rec.get('uzasadnienie', '')}\n")
                lines.append(f"**Hook:** _{rec.get('hook', '')}_")

        elif report_type == "polish":
            quality = report.get("quality_report", {})

            # Ocena
            score = quality.get("ocena", 0)
            status = quality.get("status", "?")
            lines.append(f"## Ocena: {score}/10 [{status}]\n")

            # Mocne strony
            strengths = quality.get("mocne_strony", [])
            if strengths:
                lines.append("## ✅ Mocne strony\n")
                for s in strengths:
                    lines.append(f"- {s}")
                lines.append("")

            # Problemy
            issues = quality.get("problemy", [])
            if issues:
                lines.append("## ❌ Problemy\n")
                for issue in issues:
                    if isinstance(issue, dict):
                        lines.append(f"- **{issue.get('problem', '')}**")
                        lines.append(f"  - Gdzie: {issue.get('gdzie', '')}")
                        lines.append(f"  - Wpływ: {issue.get('wpływ', '')}")
                    else:
                        lines.append(f"- {issue}")
                lines.append("")

            # Poprawki inline
            corrections = quality.get("poprawki_inline", [])
            if corrections:
                lines.append("## 🔧 Poprawki\n")
                for corr in corrections:
                    lines.append(f"**BYŁO:**")
                    lines.append(f"> {corr.get('oryginał', corr.get('oryginal', ''))}")
                    lines.append(f"\n**JEST:**")
                    lines.append(f"> {corr.get('poprawka', '')}")
                    lines.append(f"\n*Powód: {corr.get('powód', corr.get('powod', ''))}*\n")

            # Wersja po poprawkach
            improved = quality.get("wersja_po_poprawkach", "")
            if improved:
                lines.append("## 📝 Wersja po poprawkach\n")
                lines.append("```")
                lines.append(improved)
                lines.append("```\n")

            # Alternatywne hooki
            alt_hooks = quality.get("alternatywne_hooki", [])
            if alt_hooks:
                lines.append("## 🎣 Alternatywne hooki\n")
                for i, hook in enumerate(alt_hooks, 1):
                    lines.append(f"{i}. _{hook}_")

        with open(result_dir / "report.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _save_agent_reports(self, result_dir: Path, result: WorkflowResult):
        """Zapisuje osobne pliki JSON per agent."""
        if not result.report:
            return

        agents_dir = result_dir / "agents"
        agents_dir.mkdir(exist_ok=True)

        report = result.report
        report_type = report.get("type", "unknown")

        # Mapowanie kluczy do nazw plików
        agent_data_map = {
            "extracted_data": ("extractor.json", "Ekstraktor"),
            "source_analysis_data": ("source_analyst.json", "Analityk Źródła"),
            "resonance_data": ("resonance_hunter.json", "Resonance Hunter"),
            "depth_data": ("anthropologist.json", "Antropolog"),
            "polish_context_data": ("polish_contextualizer.json", "Polski Kontekstualizator"),
            "popculture_data": ("popculture_curator.json", "Kurator Popkultury"),
            # Nowe agenty kreatywne
            "story_data": ("story_excavator.json", "Archeolog Historii"),
            "tension_data": ("tension_architect.json", "Architekt Napięcia"),
            "context_shift_data": ("context_shifter.json", "Antropolog Absurdu"),
            # Agenty ulepszające
            "humor_data": ("comedian.json", "Komik"),
            "engagement_data": ("engagement.json", "Inżynier Zaangażowania"),
            # Agent krytyczny
            "critique_data": ("devils_advocate.json", "Adwokat Diabła"),
        }

        # Zapisz dane każdego agenta
        for key, (filename, agent_name) in agent_data_map.items():
            data = report.get(key, {})
            if data:
                agent_report = {
                    "agent_name": agent_name,
                    "mode": report_type,
                    "data": data,
                    "timestamp": datetime.now().isoformat(),
                }
                with open(agents_dir / filename, "w", encoding="utf-8") as f:
                    json.dump(agent_report, f, ensure_ascii=False, indent=2)

        # Dla trybu exploration/development - zapisz też raport główny agenta
        if report_type == "exploration" and report.get("exploration_report"):
            with open(agents_dir / "exploration_agent.json", "w", encoding="utf-8") as f:
                json.dump({
                    "agent_name": "Exploration Agent",
                    "mode": report_type,
                    "data": report["exploration_report"],
                    "timestamp": datetime.now().isoformat(),
                }, f, ensure_ascii=False, indent=2)

        elif report_type == "development" and report.get("development_report"):
            with open(agents_dir / "development_agent.json", "w", encoding="utf-8") as f:
                json.dump({
                    "agent_name": "Development Agent",
                    "mode": report_type,
                    "data": report["development_report"],
                    "timestamp": datetime.now().isoformat(),
                }, f, ensure_ascii=False, indent=2)

        elif report_type == "polish" and report.get("quality_report"):
            with open(agents_dir / "quality_controller.json", "w", encoding="utf-8") as f:
                json.dump({
                    "agent_name": "Quality Controller",
                    "mode": report_type,
                    "data": report["quality_report"],
                    "timestamp": datetime.now().isoformat(),
                }, f, ensure_ascii=False, indent=2)

        # Dla trybu SZLIF z agentami analitycznymi
        analytical_results = report.get("analytical_results", {})
        if analytical_results:
            for agent_key, agent_data in analytical_results.items():
                if agent_data.get("success") and agent_data.get("data"):
                    filename = f"{agent_key}.json"
                    with open(agents_dir / filename, "w", encoding="utf-8") as f:
                        json.dump({
                            "agent_name": agent_data.get("name_pl", agent_key),
                            "mode": report_type,
                            "data": agent_data["data"],
                            "timestamp": datetime.now().isoformat(),
                        }, f, ensure_ascii=False, indent=2)

        logger.info(f"Zapisano raporty agentów do: {agents_dir}")

    def _save_draft_markdown(self, result_dir: Path, draft: dict):
        """Zapisuje draft jako markdown."""
        platform = draft.get("platform", "unknown")
        content = draft.get("content", {})
        draft_format = draft.get("format", "post")

        lines = [f"# DRAFT: {platform.upper()}\n"]

        if platform == "linkedin":
            lines.append("## Post\n")
            lines.append("```")
            lines.append(content.get("full_post", ""))
            lines.append("```\n")

            if content.get("hook_variants"):
                lines.append("## Alternatywne hooki\n")
                for i, hook in enumerate(content["hook_variants"], 1):
                    lines.append(f"{i}. {hook}")

        elif platform == "facebook":
            lines.append("## Post\n")
            lines.append("```")
            lines.append(content.get("full_post", ""))
            lines.append("```\n")

        elif platform in ["x_twitter", "bluesky", "threads"]:
            if draft_format == "thread" and content.get("thread"):
                lines.append("## Wątek\n")
                for i, post in enumerate(content["thread"], 1):
                    lines.append(f"### Tweet {i}")
                    lines.append("```")
                    lines.append(post)
                    lines.append("```\n")
            else:
                lines.append("## Tweet\n")
                lines.append("```")
                lines.append(content.get("main_tweet", ""))
                lines.append("```")
                lines.append(f"\n*({content.get('character_count', 0)} znaków)*\n")

            if content.get("hook_variants"):
                lines.append("## Alternatywne wersje\n")
                for i, hook in enumerate(content["hook_variants"], 1):
                    lines.append(f"{i}. `{hook}`")

        elif platform in ["instagram_reels", "youtube_shorts"]:
            lines.append("## Tekst do kamery\n")
            lines.append("```")
            lines.append(content.get("tekst_do_kamery", ""))
            lines.append("```\n")
            lines.append(f"*Szacowany czas: {content.get('szacowany_czas', '?')}*\n")

            if content.get("warianty_hooka"):
                lines.append("## Alternatywne hooki\n")
                for i, hook in enumerate(content["warianty_hooka"], 1):
                    lines.append(f"{i}. {hook}")

            if content.get("cta"):
                lines.append(f"\n## CTA\n{content['cta']}")

        with open(result_dir / f"draft_{platform}.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
