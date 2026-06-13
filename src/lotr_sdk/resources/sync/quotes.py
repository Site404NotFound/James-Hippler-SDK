"""Synchronous quote resource: ``/quote`` and ``/quote/{id}``."""

from __future__ import annotations

from collections.abc import Iterator

from ..._pagination import paginate_sync
from ..._transport import SyncTransport
from ...models import Page, Quote
from ...query import Query
from ..base import query_string, unwrap_single

__all__ = ["QuotesResource"]

_PATH = "quote"


class QuotesResource:
    """Synchronous access to quote endpoints."""

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(self, query: Query | None = None) -> Page[Quote]:
        """List quotes, optionally filtered/sorted/paginated by ``query``."""
        data = self._transport.request("GET", _PATH, query_string(query))
        return Page[Quote].model_validate(data)

    def get(self, quote_id: str) -> Quote:
        """Fetch a single quote by id, raising ``NotFoundError`` if absent."""
        data = self._transport.request("GET", f"{_PATH}/{quote_id}")
        return unwrap_single(
            Page[Quote].model_validate(data), resource="quote", identifier=quote_id
        )

    def iter_all(self, query: Query | None = None) -> Iterator[Quote]:
        """Iterate over every matching quote, transparently fetching each page."""
        base = (query or Query()).copy()
        return paginate_sync(lambda page: self.list(base.copy().page(page)))
