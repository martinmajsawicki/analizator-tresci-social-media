"""Unified API client - obsługuje OpenRouter, OpenAI, Anthropic, Google."""

import time
import logging
import os
from dataclasses import dataclass
from typing import Optional, Callable
from pathlib import Path

from .config import Config, ModelConfig, AVAILABLE_MODELS

# Setup logging
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "api.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Response from API call."""
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    elapsed_seconds: float
    cost_usd: float
    provider: str = "unknown"
    retries: int = 0
    error_message: Optional[str] = None


class UnifiedAPIClient:
    """
    Unified client that routes to the best available API.

    Priority:
    1. Native API (Anthropic/OpenAI/Google) if key available for model
    2. OpenRouter as fallback
    """

    def __init__(self, config: Config):
        self.config = config
        self._clients = {}
        self._init_clients()

    def _init_clients(self):
        """Initialize available API clients."""

        # OpenRouter (fallback for all models)
        if self.config.openrouter_api_key:
            from openai import OpenAI
            self._clients["openrouter"] = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.config.openrouter_api_key,
                default_headers={
                    "HTTP-Referer": "https://github.com/social-media-analyzer",
                    "X-Title": "Social Media Analyzer",
                },
                timeout=self.config.timeout,
            )
            logger.info("Initialized OpenRouter client")

        # Anthropic (native)
        if self.config.anthropic_api_key:
            try:
                import anthropic
                self._clients["anthropic"] = anthropic.Anthropic(
                    api_key=self.config.anthropic_api_key,
                    timeout=self.config.timeout,
                )
                logger.info("Initialized Anthropic client")
            except ImportError:
                logger.warning("anthropic package not installed, skipping native Anthropic")

        # OpenAI (native)
        if self.config.openai_api_key:
            from openai import OpenAI
            self._clients["openai"] = OpenAI(
                api_key=self.config.openai_api_key,
                timeout=self.config.timeout,
            )
            logger.info("Initialized OpenAI client")

        # Google (native)
        if self.config.google_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.config.google_api_key)
                self._clients["google"] = genai
                logger.info("Initialized Google AI client")
            except ImportError:
                logger.warning("google-generativeai package not installed, skipping native Google")

        if not self._clients:
            raise ValueError(
                "Brak kluczy API. Ustaw przynajmniej jeden w pliku .env:\n"
                "- OPENROUTER_API_KEY (uniwersalny)\n"
                "- ANTHROPIC_API_KEY (dla Claude)\n"
                "- OPENAI_API_KEY (dla GPT)\n"
                "- GOOGLE_API_KEY (dla Gemini)"
            )

    def _get_provider_for_model(self, model_key: str) -> tuple[str, str]:
        """
        Determine which provider to use for a model.

        Returns:
            (provider_name, model_id)
        """
        model_config = AVAILABLE_MODELS.get(model_key)
        if not model_config:
            raise ValueError(f"Unknown model: {model_key}")

        # Check native providers first
        if "claude" in model_key.lower() and "anthropic" in self._clients:
            # Anthropic native model ID (without provider prefix)
            native_id = model_config.id.replace("anthropic/", "")
            return ("anthropic", native_id)

        if "gpt" in model_key.lower() and "openai" in self._clients:
            native_id = model_config.id.replace("openai/", "")
            return ("openai", native_id)

        if "gemini" in model_key.lower() and "google" in self._clients:
            native_id = model_config.id.replace("google/", "")
            return ("google", native_id)

        # Fallback to OpenRouter
        if "openrouter" in self._clients:
            return ("openrouter", model_config.id)

        raise ValueError(
            f"Brak odpowiedniego klucza API dla modelu {model_key}. "
            f"Ustaw OPENROUTER_API_KEY lub natywny klucz dla tego modelu."
        )

    def chat(
        self,
        messages: list[dict],
        model_key: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 4096,
        on_retry: Optional[Callable[[int, str], None]] = None,
    ) -> APIResponse:
        """
        Send a chat completion request with retry logic.
        Routes to the best available provider.
        """
        provider, model_id = self._get_provider_for_model(model_key)
        model_config = AVAILABLE_MODELS[model_key]

        logger.info(f"Using {provider} for {model_key} (model_id: {model_id})")

        if provider == "anthropic":
            return self._chat_anthropic(messages, model_id, model_config, temperature, max_tokens, on_retry)
        elif provider == "openai":
            return self._chat_openai(messages, model_id, model_config, temperature, max_tokens, on_retry, native=True)
        elif provider == "google":
            return self._chat_google(messages, model_id, model_config, temperature, max_tokens, on_retry)
        else:  # openrouter
            return self._chat_openai(messages, model_id, model_config, temperature, max_tokens, on_retry, native=False)

    def _chat_openai(
        self,
        messages: list[dict],
        model_id: str,
        model_config: ModelConfig,
        temperature: float,
        max_tokens: Optional[int],
        on_retry: Optional[Callable],
        native: bool = False,
    ) -> APIResponse:
        """Chat via OpenAI SDK (works for OpenAI native and OpenRouter)."""
        client = self._clients["openai" if native else "openrouter"]
        provider_name = "OpenAI" if native else "OpenRouter"

        last_error = None
        retries = 0

        for attempt in range(1, self.config.max_retries + 1):
            start_time = time.time()

            try:
                logger.info(f"[{provider_name}] Attempt {attempt}/{self.config.max_retries} to {model_id}")

                response = client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                elapsed = time.time() - start_time
                input_tokens = response.usage.prompt_tokens if response.usage else 0
                output_tokens = response.usage.completion_tokens if response.usage else 0

                cost = (
                    (input_tokens / 1000) * model_config.price_per_1k_input +
                    (output_tokens / 1000) * model_config.price_per_1k_output
                )

                content = response.choices[0].message.content or ""

                logger.info(f"[{provider_name}] Success: {input_tokens} in, {output_tokens} out, ${cost:.4f}")

                return APIResponse(
                    content=content,
                    model=model_config.name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    elapsed_seconds=elapsed,
                    cost_usd=cost,
                    provider=provider_name,
                    retries=retries,
                )

            except Exception as e:
                last_error = f"{type(e).__name__}: {str(e)}"
                logger.warning(f"[{provider_name}] Attempt {attempt} failed: {last_error}")
                retries += 1

                if on_retry and attempt < self.config.max_retries:
                    on_retry(attempt, last_error)

                if attempt < self.config.max_retries:
                    time.sleep(2 ** attempt)

        logger.error(f"[{provider_name}] All {self.config.max_retries} attempts failed")
        return APIResponse(
            content=f"[BŁĄD API po {retries} próbach: {last_error}]",
            model=model_config.name,
            input_tokens=0,
            output_tokens=0,
            elapsed_seconds=0,
            cost_usd=0,
            provider=provider_name,
            retries=retries,
            error_message=last_error,
        )

    def _chat_anthropic(
        self,
        messages: list[dict],
        model_id: str,
        model_config: ModelConfig,
        temperature: float,
        max_tokens: Optional[int],
        on_retry: Optional[Callable],
    ) -> APIResponse:
        """Chat via Anthropic native SDK."""
        client = self._clients["anthropic"]

        # Convert messages format (Anthropic uses different format)
        system_msg = None
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                chat_messages.append(msg)

        last_error = None
        retries = 0

        for attempt in range(1, self.config.max_retries + 1):
            start_time = time.time()

            try:
                logger.info(f"[Anthropic] Attempt {attempt}/{self.config.max_retries} to {model_id}")

                kwargs = {
                    "model": model_id,
                    "messages": chat_messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens or 4096,
                }
                if system_msg:
                    kwargs["system"] = system_msg

                response = client.messages.create(**kwargs)

                elapsed = time.time() - start_time
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens

                cost = (
                    (input_tokens / 1000) * model_config.price_per_1k_input +
                    (output_tokens / 1000) * model_config.price_per_1k_output
                )

                content = response.content[0].text if response.content else ""

                logger.info(f"[Anthropic] Success: {input_tokens} in, {output_tokens} out, ${cost:.4f}")

                return APIResponse(
                    content=content,
                    model=model_config.name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    elapsed_seconds=elapsed,
                    cost_usd=cost,
                    provider="Anthropic",
                    retries=retries,
                )

            except Exception as e:
                last_error = f"{type(e).__name__}: {str(e)}"
                logger.warning(f"[Anthropic] Attempt {attempt} failed: {last_error}")
                retries += 1

                if on_retry and attempt < self.config.max_retries:
                    on_retry(attempt, last_error)

                if attempt < self.config.max_retries:
                    time.sleep(2 ** attempt)

        logger.error(f"[Anthropic] All {self.config.max_retries} attempts failed")
        return APIResponse(
            content=f"[BŁĄD API po {retries} próbach: {last_error}]",
            model=model_config.name,
            input_tokens=0,
            output_tokens=0,
            elapsed_seconds=0,
            cost_usd=0,
            provider="Anthropic",
            retries=retries,
            error_message=last_error,
        )

    def _chat_google(
        self,
        messages: list[dict],
        model_id: str,
        model_config: ModelConfig,
        temperature: float,
        max_tokens: Optional[int],
        on_retry: Optional[Callable],
    ) -> APIResponse:
        """Chat via Google AI native SDK."""
        genai = self._clients["google"]

        # Convert messages to Google format
        system_instruction = None
        history = []
        current_content = None

        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                current_content = msg["content"]
            elif msg["role"] == "assistant":
                if current_content:
                    history.append({"role": "user", "parts": [current_content]})
                history.append({"role": "model", "parts": [msg["content"]]})
                current_content = None

        last_error = None
        retries = 0

        for attempt in range(1, self.config.max_retries + 1):
            start_time = time.time()

            try:
                logger.info(f"[Google] Attempt {attempt}/{self.config.max_retries} to {model_id}")

                model = genai.GenerativeModel(
                    model_name=model_id,
                    system_instruction=system_instruction,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    }
                )

                chat = model.start_chat(history=history)
                response = chat.send_message(current_content)

                elapsed = time.time() - start_time

                # Google doesn't always return token counts
                input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0
                output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0

                cost = (
                    (input_tokens / 1000) * model_config.price_per_1k_input +
                    (output_tokens / 1000) * model_config.price_per_1k_output
                )

                content = response.text

                logger.info(f"[Google] Success: {input_tokens} in, {output_tokens} out, ${cost:.4f}")

                return APIResponse(
                    content=content,
                    model=model_config.name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    elapsed_seconds=elapsed,
                    cost_usd=cost,
                    provider="Google",
                    retries=retries,
                )

            except Exception as e:
                last_error = f"{type(e).__name__}: {str(e)}"
                logger.warning(f"[Google] Attempt {attempt} failed: {last_error}")
                retries += 1

                if on_retry and attempt < self.config.max_retries:
                    on_retry(attempt, last_error)

                if attempt < self.config.max_retries:
                    time.sleep(2 ** attempt)

        logger.error(f"[Google] All {self.config.max_retries} attempts failed")
        return APIResponse(
            content=f"[BŁĄD API po {retries} próbach: {last_error}]",
            model=model_config.name,
            input_tokens=0,
            output_tokens=0,
            elapsed_seconds=0,
            cost_usd=0,
            provider="Google",
            retries=retries,
            error_message=last_error,
        )

    def test_connection(self) -> bool:
        """Test if API connection works."""
        try:
            response = self.chat(
                messages=[{"role": "user", "content": "Powiedz 'OK' i nic więcej."}],
                model_key=self.config.default_model,
                max_tokens=10,
            )
            return "OK" in response.content.upper() and not response.error_message
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    @property
    def available_providers(self) -> list[str]:
        """Return list of initialized providers."""
        return list(self._clients.keys())


# Alias for backward compatibility
OpenRouterClient = UnifiedAPIClient
