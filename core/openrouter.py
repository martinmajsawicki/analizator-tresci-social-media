"""OpenRouter API client with retry logic and error logging."""

import time
import logging
from dataclasses import dataclass
from typing import Optional, Callable
from pathlib import Path

from openai import OpenAI, APIError, APITimeoutError, RateLimitError

from .config import Config, ModelConfig

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
    retries: int = 0
    error_message: Optional[str] = None


class OpenRouterClient:
    """Client for OpenRouter API with retry logic."""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(
            base_url=self.BASE_URL,
            api_key=config.api_key,
            default_headers={
                "HTTP-Referer": "https://github.com/social-media-analyzer",
                "X-Title": "Social Media Post Analyzer",
            },
            timeout=config.timeout,
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

        Args:
            messages: List of message dicts with 'role' and 'content'
            model_key: Key from AVAILABLE_MODELS (e.g., 'claude-opus-4.5')
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            on_retry: Callback(attempt, error_message) when retrying

        Returns:
            APIResponse with content and usage stats
        """
        model_config = self.config.get_model(model_key)

        last_error = None
        retries = 0

        for attempt in range(1, self.config.max_retries + 1):
            start_time = time.time()

            try:
                logger.info(f"API call attempt {attempt}/{self.config.max_retries} to {model_config.id}")

                response = self.client.chat.completions.create(
                    model=model_config.id,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                elapsed = time.time() - start_time

                # Extract usage
                input_tokens = response.usage.prompt_tokens if response.usage else 0
                output_tokens = response.usage.completion_tokens if response.usage else 0

                # Calculate cost
                cost = (
                    (input_tokens / 1000) * model_config.price_per_1k_input +
                    (output_tokens / 1000) * model_config.price_per_1k_output
                )

                content = response.choices[0].message.content or ""

                # Log success
                logger.info(
                    f"API call successful: {input_tokens} in, {output_tokens} out, "
                    f"{elapsed:.1f}s, ${cost:.4f}"
                )

                # Warn if empty response
                if not content.strip():
                    logger.warning(f"API returned empty response for {model_config.id}")

                return APIResponse(
                    content=content,
                    model=model_config.name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    elapsed_seconds=elapsed,
                    cost_usd=cost,
                    retries=retries,
                )

            except APITimeoutError as e:
                last_error = f"Timeout po {self.config.timeout}s"
                logger.warning(f"Attempt {attempt} failed: {last_error}")
                retries += 1

            except RateLimitError as e:
                last_error = f"Rate limit: {str(e)}"
                logger.warning(f"Attempt {attempt} failed: {last_error}")
                retries += 1
                # Wait longer for rate limits
                if attempt < self.config.max_retries:
                    wait_time = 10 * attempt  # 10s, 20s, 30s...
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)

            except APIError as e:
                last_error = f"API error: {str(e)}"
                logger.error(f"Attempt {attempt} failed: {last_error}")
                retries += 1

            except Exception as e:
                last_error = f"Unexpected error: {type(e).__name__}: {str(e)}"
                logger.error(f"Attempt {attempt} failed: {last_error}")
                retries += 1

            # Notify about retry
            if on_retry and attempt < self.config.max_retries:
                on_retry(attempt, last_error)

            # Wait before retry (exponential backoff)
            if attempt < self.config.max_retries:
                wait_time = 2 ** attempt  # 2s, 4s, 8s
                time.sleep(wait_time)

        # All retries failed
        logger.error(f"All {self.config.max_retries} attempts failed. Last error: {last_error}")

        return APIResponse(
            content=f"[BŁĄD API po {retries} próbach: {last_error}]",
            model=model_config.name,
            input_tokens=0,
            output_tokens=0,
            elapsed_seconds=0,
            cost_usd=0,
            retries=retries,
            error_message=last_error,
        )

    def chat_stream(
        self,
        messages: list[dict],
        model_key: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 4096,
        on_token: Optional[Callable[[str], None]] = None,
    ) -> APIResponse:
        """
        Send a streaming chat completion request.
        Note: No retry logic for streaming (would be complex).
        """
        model_config = self.config.get_model(model_key)
        start_time = time.time()

        try:
            stream = self.client.chat.completions.create(
                model=model_config.id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                stream_options={"include_usage": True},
            )

            content_parts = []
            input_tokens = 0
            output_tokens = 0

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    content_parts.append(token)
                    if on_token:
                        on_token(token)

                if chunk.usage:
                    input_tokens = chunk.usage.prompt_tokens
                    output_tokens = chunk.usage.completion_tokens

            elapsed = time.time() - start_time
            content = "".join(content_parts)

            cost = (
                (input_tokens / 1000) * model_config.price_per_1k_input +
                (output_tokens / 1000) * model_config.price_per_1k_output
            )

            return APIResponse(
                content=content,
                model=model_config.name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                elapsed_seconds=elapsed,
                cost_usd=cost,
            )

        except Exception as e:
            logger.error(f"Streaming error: {type(e).__name__}: {str(e)}")
            return APIResponse(
                content=f"[BŁĄD STREAMING: {str(e)}]",
                model=model_config.name,
                input_tokens=0,
                output_tokens=0,
                elapsed_seconds=time.time() - start_time,
                cost_usd=0,
                error_message=str(e),
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
