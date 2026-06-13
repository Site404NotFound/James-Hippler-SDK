"""The synchronous client facade."""

from __future__ import annotations

from .._transport import SyncTransport
from ..config import ClientConfig
from ..resources import MoviesResource, QuotesResource
from .base import build_overrides

__all__ = ["Client"]


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
            api_key, **build_overrides(base_url, timeout, max_retries, backoff_factor)
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
