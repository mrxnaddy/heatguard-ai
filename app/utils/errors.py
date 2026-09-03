"""
Shared error types and a safe-call wrapper.

Goal: the Streamlit UI should never show a raw Python traceback. Every
call into the service layer goes through `safe_call`, which converts
any exception into a typed, user-safe `AppError` with a short message
and a machine-readable `code`, while still logging the real exception
for developers.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Generic, Optional, TypeVar

logger = logging.getLogger("heatguard")

T = TypeVar("T")


class HeatGuardError(Exception):
    """Base class for all HeatGuard-specific errors."""

    code = "internal_error"
    user_message = "Something went wrong. Please try again."


class ConfigurationError(HeatGuardError):
    code = "configuration_error"
    user_message = "The application is misconfigured. Check environment variables."


class APIConnectionError(HeatGuardError):
    code = "api_connection_error"
    user_message = "Could not reach the temperature data provider. Showing cached/mock data instead."


class InvalidResponseError(HeatGuardError):
    code = "invalid_response"
    user_message = "The data provider returned an unexpected response."


class LocationNotFoundError(HeatGuardError):
    code = "location_not_found"
    user_message = "That location could not be found."


class EmptyDataError(HeatGuardError):
    code = "empty_data"
    user_message = "No data is currently available."


@dataclass
class AppResult(Generic[T]):
    """Result wrapper: either `value` is set, or `error` is set — never both."""

    value: Optional[T] = None
    error: Optional[HeatGuardError] = None

    @property
    def ok(self) -> bool:
        return self.error is None


def safe_call(fn: Callable[[], T]) -> AppResult[T]:
    """
    Run `fn`, converting any exception into a safe AppResult.

    Known HeatGuardError subclasses are passed through as-is (their
    user_message is already safe to display). Any other exception is
    logged with full detail and converted into a generic internal error
    so nothing leaks a stack trace to the UI.
    """
    try:
        return AppResult(value=fn())
    except HeatGuardError as exc:
        logger.warning("Handled HeatGuardError: %s", exc)
        return AppResult(error=exc)
    except Exception as exc:  # noqa: BLE001 - intentional catch-all boundary
        logger.exception("Unexpected error in safe_call")
        return AppResult(error=HeatGuardError(str(exc)))
