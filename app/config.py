"""
Configuration management for HeatGuard AI.

All configuration comes from environment variables (loaded via .env in
local development). Nothing here is hardcoded. If a required variable
is missing, we fail loudly and early with a clear message rather than
letting the app crash later with a confusing stack trace.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load .env if present. In production (e.g. Streamlit Community Cloud),
# real environment variables / secrets take precedence and this is a no-op
# for any variable already set.
load_dotenv()


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    # --- FortyGuard ---
    fortyguard_api_key: str | None
    fortyguard_base_url: str
    use_mock_data: bool

    # --- LLM (scaffold only until Phase 3) ---
    llm_api_key: str | None
    llm_model: str

    # --- Cache ---
    cache_ttl_seconds: int

    def fortyguard_configured(self) -> bool:
        """True only if real (non-mock) FortyGuard credentials are present."""
        return bool(self.fortyguard_api_key) and not self.use_mock_data


def load_settings() -> Settings:
    """
    Build the application Settings from environment variables.

    USE_MOCK_DATA defaults to True. This is intentional: HeatGuard AI must
    always be runnable and demoable without live credentials.
    """
    use_mock_data = _get_bool("USE_MOCK_DATA", default=True)

    fortyguard_api_key = os.getenv("FORTYGUARD_API_KEY") or None
    fortyguard_base_url = os.getenv(
        "FORTYGUARD_BASE_URL", "https://api.fortyguard.example/v1"
    )

    if not use_mock_data and not fortyguard_api_key:
        raise ConfigError(
            "USE_MOCK_DATA is false but FORTYGUARD_API_KEY is not set. "
            "Either set USE_MOCK_DATA=true or provide a real API key."
        )

    llm_api_key = os.getenv("LLM_API_KEY") or None
    llm_model = os.getenv("LLM_MODEL", "not-configured")

    cache_ttl_seconds = int(os.getenv("CACHE_TTL_SECONDS", "300"))

    return Settings(
        fortyguard_api_key=fortyguard_api_key,
        fortyguard_base_url=fortyguard_base_url,
        use_mock_data=use_mock_data,
        llm_api_key=llm_api_key,
        llm_model=llm_model,
        cache_ttl_seconds=cache_ttl_seconds,
    )


# Module-level singleton used across the app. Import `settings` directly
# for simple access; call `load_settings()` again in tests to get a fresh
# instance under different env vars.
settings = load_settings()
