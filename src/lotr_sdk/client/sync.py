"""The synchronous client facade."""

from __future__ import annotations

from .._transport import SyncTransport
from ..resources import MoviesResource, QuotesResource
from .base import BaseClient

__all__ = ["Client"]


class Client(BaseClient):
    """Synchronous client for The One API. See :class:`BaseClient` for arguments."""

    def _init_resources(self) -> None:
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
