import json
import logging
import re

from groq import Groq, RateLimitError

import config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert competitive programmer and computer-science tutor. "
    "Be precise and technically correct. Never invent facts, complexities, or outputs: "
    "every complexity must be the true worst case, every example output must be exactly "
    "what the code would produce, and all code must compile/run as written. "
    "If code has undefined behaviour, say so instead of claiming a specific output. "
    "Use Markdown. Put all code in fenced code blocks with the language tag."
)


class LLMError(Exception):
    """Raised when the LLM cannot produce a usable answer."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        if not config.GROQ_API_KEY:
            raise LLMError("GROQ_API_KEY is missing. Add it to backend/.env.")
        _client = Groq(api_key=config.GROQ_API_KEY, timeout=config.LLM_TIMEOUT,
                       max_retries=config.LLM_MAX_RETRIES)
    return _client


def call_llm(prompt: str, temperature: float = None) -> str:
    """Send a prompt and return the text answer. Raises LLMError on failure."""
    try:
        response = _get_client().chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=config.LLM_TEMPERATURE if temperature is None else temperature,
        )
    except LLMError:
        raise
    except RateLimitError as e:
        logger.warning("LLM rate limit reached: %s", e)
        raise LLMError("The AI provider's rate limit was reached (Groq free tier allows a limited number "
                       "of tokens per minute). Please wait about a minute and try again.", 429) from e
    except Exception as e:
        logger.exception("LLM request failed")
        raise LLMError(f"LLM request failed: {e}") from e

    output = (response.choices[0].message.content or "").strip()
    if not output:
        raise LLMError("LLM returned an empty response.")
    return output


def _extract_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("no JSON object found")
    return json.loads(text[start:end + 1])


def as_bool(value, default: bool = True) -> bool:
    """Read a JSON boolean that the LLM may have sent as a string."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lower() in ("true", "false"):
        return value.strip().lower() == "true"
    return default


def call_llm_json(prompt: str) -> dict:
    """Ask for a JSON object; retries once if the answer is not valid JSON."""
    prompt += "\n\nRespond with ONLY a valid JSON object. No Markdown, no extra text."
    last_error = None
    for _ in range(2):
        text = call_llm(prompt, temperature=0)
        try:
            return _extract_json(text)
        except ValueError as e:  # json.JSONDecodeError is a ValueError
            last_error = e
            logger.warning("Invalid JSON from LLM: %s", text[:300])
    raise LLMError(f"LLM did not return valid JSON ({last_error}).")
