"""
Configurable LLM client for HeatGuard AI.

Upgraded in Phase 3 to support environment-based configuration, graceful mock
mode fallbacks, and status checking without exposing tracebacks.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from app.config import Settings, settings as default_settings

logger = logging.getLogger("heatguard.llm_client")


@dataclass(frozen=True)
class LLMStatus:
    configured: bool
    model: str


class LLMClient:
    """Configurable LLM client with graceful fallback when unconfigured."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or default_settings

    def status(self) -> LLMStatus:
        return LLMStatus(
            configured=bool(self._settings.llm_api_key and self._settings.llm_model != "not-configured"),
            model=self._settings.llm_model,
        )

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """
        Generate text using the configured LLM, or return a graceful message
        if credentials are missing or unconfigured.
        """
        stat = self.status()
        if not stat.configured:
            return (
                "AI features are running in mock mode because LLM credentials are not configured. "
                "Please set LLM_API_KEY and LLM_MODEL in your environment variables."
            )

        try:
            # TODO: Integrate real LLM SDK provider client here once verified
            raise NotImplementedError("Real LLM API invocation not yet wired up.")
        except Exception as exc:
            logger.error("LLM generation failed: %s", exc)
            return "I cannot confirm this from the available data due to an AI service error."