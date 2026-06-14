"""Asynchronous quote resource: ``/quote`` and ``/quote/{id}``."""

from __future__ import annotations

from collections.abc import AsyncIterator
from http import HTTPMethod

from lotr_sdk._pagination import paginate_async
from lotr_sdk._transport import AsyncTransport
from lotr_sdk.models import Page, Quote
from lotr_sdk.query import Query
from lotr_sdk.resources.base import BaseResource, query_string, unwrap_single

__all__ = ["AsyncQuotesResource"]

_PATH = "quote"


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
