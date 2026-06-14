"""The asynchronous client facade."""

from __future__ import annotations

from lotr_sdk._transport import AsyncTransport
from lotr_sdk.client.base import BaseClient
from lotr_sdk.resources import AsyncMoviesResource, AsyncQuotesResource

__all__ = ["AsyncClient"]


class AsyncClient(BaseClient):
    """Asynchronous client for The One API. See :class:`~lotr_sdk.Client` for arguments."""

    def _init_resources(self) -> None:
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
