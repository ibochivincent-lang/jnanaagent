"""Runtime configuration, overridable via environment variables (see .env.example)."""

import os

from dotenv import load_dotenv

load_dotenv()

# neatHack LiteLLM Sponsored Proxy ($20 team credits)
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY", "")
LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "https://litellm.vision.aivar.app/v1")

# Model selection: defaults to claude-haiku when using LiteLLM, or claude-opus-4-8 for direct Anthropic
default_model = "claude-haiku" if LITELLM_API_KEY else "claude-opus-4-8"
MODEL = os.getenv("RESEARCH_AGENT_MODEL", default_model)

MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "8"))
MAX_SOURCES = int(os.getenv("MAX_SOURCES", "6"))
MIN_SOURCES = int(os.getenv("MIN_SOURCES", "3"))
MAX_SEARCH_ROUNDS = int(os.getenv("MAX_SEARCH_ROUNDS", "2"))
MAX_PAGE_CHARS = int(os.getenv("MAX_PAGE_CHARS", "8000"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8192"))
FETCH_TIMEOUT_S = float(os.getenv("FETCH_TIMEOUT_S", "15"))
