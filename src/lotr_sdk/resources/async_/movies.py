"""Asynchronous movie resource: ``/movie``, ``/movie/{id}``, ``/movie/{id}/quote``."""

from __future__ import annotations

from collections.abc import AsyncIterator
from http import HTTPMethod

from lotr_sdk._pagination import paginate_async
from lotr_sdk._transport import AsyncTransport
from lotr_sdk.models import Movie, Page, Quote
from lotr_sdk.query import Query
from lotr_sdk.resources.base import BaseResource, query_string, unwrap_single

__all__ = ["AsyncMoviesResource"]

_PATH = "movie"


class AsyncMoviesResource(BaseResource[AsyncTransport]):
    """Asynchronous access to movie endpoints."""

    async def list(self, query: Query | None = None) -> Page[Movie]:
        """List movies, optionally filtered/sorted/paginated by ``query``."""
        data = await self._transport.request(HTTPMethod.GET, _PATH, query_string(query))
        return Page[Movie].model_validate(data)

    async def get(self, movie_id: str) -> Movie:
        """Fetch a single movie by id, raising ``NotFoundError`` if absent."""
        data = await self._transport.request(HTTPMethod.GET, f"{_PATH}/{movie_id}")
        return unwrap_single(Page[Movie].model_validate(data), resource=_PATH, identifier=movie_id)

    async def quotes(self, movie_id: str, query: Query | None = None) -> Page[Quote]:
        """List the quotes belonging to a movie."""
        data = await self._transport.request(
            HTTPMethod.GET, f"{_PATH}/{movie_id}/quote", query_string(query)
        )
        return Page[Quote].model_validate(data)

    def iter_all(self, query: Query | None = None) -> AsyncIterator[Movie]:
        """Asynchronously iterate over every matching movie across all pages."""
        base = (query or Query()).copy()
        return paginate_async(lambda page: self.list(base.copy().page(page)))
