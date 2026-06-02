import json
from functools import lru_cache
from typing import Any

from openai import OpenAI

from app.core.config import get_settings


class LLMConfigurationError(RuntimeError):
    pass


class LLMResponseParseError(RuntimeError):
    pass


@lru_cache
def get_llm_client() -> OpenAI:
    settings = get_settings()

    if not settings.llm_api_key:
        raise LLMConfigurationError("LLM API key is not configured")

    return OpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout=settings.llm_timeout_seconds,
    )


def generate_text(system_prompt: str, user_prompt: str) -> str:
    llm_client = get_llm_client()
    settings = get_settings()
    response = llm_client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("LLM response does not contain content")
    return content


def generate_json(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    text = generate_text(system_prompt, user_prompt)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        try:
            parsed = json.loads(extract_json_object(text))
        except json.JSONDecodeError as e:
            raise LLMResponseParseError(
                f"Failed to parse LLM response as JSON: {e}"
            ) from e

    if not isinstance(parsed, dict):
        raise LLMResponseParseError("LLM response is not a JSON object")
    return parsed


def extract_json_object(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or start >= end:
        raise LLMResponseParseError("No JSON object found in LLM response")
    return text[start : end + 1]
