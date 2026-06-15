"""Quote resource: ``/quote`` and ``/quote/{id}``.

The synchronous ``QuotesResource`` and its asynchronous twin
``AsyncQuotesResource`` live in one module so their public surfaces stay in
lockstep (enforced by ``tests/unit/test_parity.py``).
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from http import HTTPMethod

from lotr_sdk.models import Page, Quote
from lotr_sdk.pagination import paginate_async, paginate_sync
from lotr_sdk.query import Query
from lotr_sdk.resources.base import BaseResource, query_string, unwrap_single
from lotr_sdk.transport import AsyncTransport, SyncTransport

__all__ = ["AsyncQuotesResource", "QuotesResource"]

_PATH = "quote"


class QuotesResource(BaseResource[SyncTransport]):
    """Synchronous access to quote endpoints."""

    def list(self, query: Query | None = None) -> Page[Quote]:
        """List quotes, optionally filtered/sorted/paginated by ``query``."""
        data = self._transport.request(HTTPMethod.GET, _PATH, query_string(query))
        return Page[Quote].model_validate(data)

    def get(self, quote_id: str) -> Quote:
        """Fetch a single quote by id, raising ``NotFoundError`` if absent."""
        data = self._transport.request(HTTPMethod.GET, f"{_PATH}/{quote_id}")
        return unwrap_single(Page[Quote].model_validate(data), resource=_PATH, identifier=quote_id)

    def iter_all(self, query: Query | None = None) -> Iterator[Quote]:
        """Iterate over every matching quote, transparently fetching each page."""
        base = (query or Query()).copy()
        return paginate_sync(lambda page: self.list(base.copy().page(page)))


class AsyncQuotesResource(BaseResource[AsyncTransport]):
    """Asynchronous access to quote endpoints."""

    async def list(self, query: Query | None = None) -> Page[Quote]:
        """List quotes, optionally filtered/sorted/paginated by ``query``."""
        data = await self._transport.request(HTTPMethod.GET, _PATH, query_string(query))
        return Page[Quote].model_validate(data)

    async def get(self, quote_id: str) -> Quote:
        """Fetch a single quote by id, raising ``NotFoundError`` if absent."""
        data = await self._transport.request(HTTPMethod.GET, f"{_PATH}/{quote_id}")
        return unwrap_single(Page[Quote].model_validate(data), resource=_PATH, identifier=quote_id)

    def iter_all(self, query: Query | None = None) -> AsyncIterator[Quote]:
        """Asynchronously iterate over every matching quote across all pages."""
        base = (query or Query()).copy()
        return paginate_async(lambda page: self.list(base.copy().page(page)))
