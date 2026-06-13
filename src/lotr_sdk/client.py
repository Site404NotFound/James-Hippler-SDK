"""The public entry points: a synchronous ``Client`` and an async ``AsyncClient``.

Both are thin facades: they resolve configuration, own a transport, and expose
``movies`` and ``quotes`` resource groups. Use them as context managers so the
underlying HTTP connections are closed cleanly.
"""

from __future__ import annotations

from typing import Any

from ._transport import AsyncTransport, SyncTransport
from .config import ClientConfig
from .resources import (
    AsyncMoviesResource,
    AsyncQuotesResource,
    MoviesResource,
    QuotesResource,
)

__all__ = ["AsyncClient", "Client"]


def _overrides(
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


class Client:
    """Synchronous client for The One API.

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
            api_key, **_overrides(base_url, timeout, max_retries, backoff_factor)
        )
        self._transport = SyncTransport(self._config)
        self.movies = MoviesResource(self._transport)
        self.quotes = QuotesResource(self._transport)

    def close(self) -> None:
        """Close the underlying HTTP connections."""
        self._transport.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class AsyncClient:
    """Asynchronous client for The One API. See :class:`Client` for arguments."""

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
            api_key, **_overrides(base_url, timeout, max_retries, backoff_factor)
        )
        self._transport = AsyncTransport(self._config)
        self.movies = AsyncMoviesResource(self._transport)
        self.quotes = AsyncQuotesResource(self._transport)

    async def aclose(self) -> None:
        """Close the underlying HTTP connections."""
        await self._transport.aclose()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()
