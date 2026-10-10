"""Single place the LLM is constructed — supports Anthropic and neatHack LiteLLM proxy."""

import os
from langchain_core.language_models.chat_models import BaseChatModel

from . import config


def get_llm(max_tokens: int | None = None) -> BaseChatModel:
    litellm_key = config.LITELLM_API_KEY or os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if litellm_key and (not anthropic_key or os.getenv("USE_LITELLM", "true").lower() == "true"):
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=config.MODEL,
            api_key=litellm_key,
            base_url=config.LITELLM_BASE_URL,
            max_tokens=max_tokens or config.MAX_TOKENS,
            timeout=180,
        )

    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(
        model=config.MODEL,
        max_tokens=max_tokens or config.MAX_TOKENS,
        timeout=180,
    )
