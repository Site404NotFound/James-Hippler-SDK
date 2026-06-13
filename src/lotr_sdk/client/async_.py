"""The asynchronous client facade."""

from __future__ import annotations

from .._transport import AsyncTransport
from ..config import ClientConfig
from ..resources import AsyncMoviesResource, AsyncQuotesResource
from .base import build_overrides

__all__ = ["AsyncClient"]


class AsyncClient:
    """Asynchronous client for The One API. See :class:`~lotr_sdk.Client` for arguments."""

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
