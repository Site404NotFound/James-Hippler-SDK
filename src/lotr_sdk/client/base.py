"""Shared construction for the client facades."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..config import ClientConfig

__all__ = ["BaseClient", "build_overrides"]


def build_overrides(
    base_url: str | None,
    timeout: float | None,
    max_retries: int | None,
    backoff_factor: float | None,
) -> dict[str, Any]:
    """Collect only the options the caller actually set, so config defaults win."""
    candidates = {
        "base_url": base_url,
        "timeout": timeout,
        "max_retries": max_retries,
        "backoff_factor": backoff_factor,
    }
    return {key: value for key, value in candidates.items() if value is not None}


class BaseClient(ABC):
    """Shared construction for the sync and async client facades.

    Args:
        api_key: API key; falls back to the ``THE_ONE_API_KEY`` env var.
        base_url: Override the API base URL.
        timeout: Per-request timeout in seconds.
        max_retries: Retries for transient failures (429 / 5xx / network).
        backoff_factor: Base seconds for exponential backoff between retries.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        backoff_factor: float | None = None,
    ) -> None:
        self._config = ClientConfig.resolve(
            api_key, **build_overrides(base_url, timeout, max_retries, backoff_factor)
        )
        self._init_resources()

    @abstractmethod
    def _init_resources(self) -> None:
        """Construct the transport and attach the resource groups."""
