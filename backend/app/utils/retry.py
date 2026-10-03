# backend/app/utils/retry.py

"""
Generic retry utility with exponential backoff.

Used for calls to external services (LLM providers, APIs) that can
fail transiently (network blips, rate limits, temporary overload) but
succeed if retried after a short delay.
"""

import time
import logging
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Error signals that mean "retrying won't help, it'll just fail again"
_NON_RETRYABLE_SIGNALS = (
    "invalid api key",
    "authentication",
    "unauthorized",
    "permission denied",
    "invalid_request_error",
    "does not exist",  # e.g. "model not found"
)


def _is_retryable(error: Exception) -> bool:
    message = str(error).lower()
    return not any(signal in message for signal in _NON_RETRYABLE_SIGNALS)


def retry_with_backoff(
    func: Callable[..., T],
    *args,
    max_retries: int = 3,
    base_delay: float = 1.0,
    **kwargs,
) -> T:
    """Calls func(*args, **kwargs), retrying on transient failures with
    exponential backoff (1s, 2s, 4s, ...).

    Re-raises immediately for errors that look permanent (bad API key,
    invalid request, model not found) — retrying those just wastes
    time and delays the real error from surfacing.
    """
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            if not _is_retryable(e):
                logger.warning("Non-retryable error, giving up immediately: %s", e)
                raise
            if attempt == max_retries:
                logger.error("Exhausted %d retries. Last error: %s", max_retries, e)
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(
                "Attempt %d/%d failed (%s), retrying in %.1fs...",
                attempt, max_retries, e, delay,
            )
            time.sleep(delay)

    raise last_error  # unreachable, keeps type-checkers happy