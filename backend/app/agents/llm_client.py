"""
Shared Gemini chat model access for all agents.

Every agent imports `get_chat_model()` instead of calling
`init_chat_model()` directly, so model name, API key handling, and
future retry/rate-limit logic live in exactly one place.
"""

from functools import lru_cache
from typing import Any

from langchain.chat_models import init_chat_model
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import settings
from app.utils.exceptions import ConfigurationError
from app.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache
def get_chat_model(temperature: float = 0.2) -> Any:
    """Return a cached Gemini chat model instance for the given temperature."""
    if not settings.GOOGLE_API_KEY:
        raise ConfigurationError(
            "GOOGLE_API_KEY is not set. Every agent requires a valid Gemini API key."
        )

    logger.debug("Initializing Gemini chat model '%s' (temperature=%.2f)", settings.GEMINI_CHAT_MODEL, temperature)
    return init_chat_model(
        f"google_genai:{settings.GEMINI_CHAT_MODEL}",
        api_key=settings.GOOGLE_API_KEY,
        temperature=temperature,
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def invoke_structured(model: Any, schema: Any, messages: list) -> Any:
    """
    Invoke a chat model with structured output, retrying on transient failures
    (rate limits, brief network errors) with exponential backoff.
    """
    structured_model = model.with_structured_output(schema)
    return structured_model.invoke(messages)
