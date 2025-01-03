"""LLM model configurations and factory functions."""
from functools import lru_cache
from typing import Optional

from langchain_openai import ChatOpenAI

from ..config.settings import settings


@lru_cache()
def get_llm(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> ChatOpenAI:
    """Get a configured LLM instance.

    Args:
        model_name: Optional model name override
        temperature: Optional temperature override
        max_tokens: Optional max tokens override

    Returns:
        Configured ChatOpenAI instance
    """
    return ChatOpenAI(
        model_name=model_name or settings.llm.llm_model_name,
        temperature=temperature
        if temperature is not None
        else settings.llm.temperature,
        max_tokens=max_tokens or settings.llm.max_tokens,
        top_p=settings.llm.top_p,
        frequency_penalty=settings.llm.frequency_penalty,
        presence_penalty=settings.llm.presence_penalty,
    )
