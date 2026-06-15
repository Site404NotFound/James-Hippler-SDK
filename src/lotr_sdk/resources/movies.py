"""Movie resource: ``/movie``, ``/movie/{id}``, ``/movie/{id}/quote``.

The synchronous ``MoviesResource`` and its asynchronous twin
``AsyncMoviesResource`` live in one module so their public surfaces stay in
lockstep (enforced by ``tests/unit/test_parity.py``).
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator
from http import HTTPMethod

from lotr_sdk.models import Movie, MovieWithQuotes, Page, Quote
from lotr_sdk.pagination import paginate_async, paginate_sync
from lotr_sdk.query import Query
from lotr_sdk.resources.base import BaseResource, query_string, unwrap_single
from lotr_sdk.transport import AsyncTransport, SyncTransport

__all__ = ["AsyncMoviesResource", "MoviesResource"]

_PATH = "movie"


class MoviesResource(BaseResource[SyncTransport]):
    """Synchronous access to movie endpoints."""

    def list(self, query: Query | None = None) -> Page[Movie]:
        """List movies, optionally filtered/sorted/paginated by ``query``."""
        data = self._transport.request(HTTPMethod.GET, _PATH, query_string(query))
        return Page[Movie].model_validate(data)

    def get(self, movie_id: str) -> Movie:
        """Fetch a single movie by id, raising ``NotFoundError`` if absent."""
        data = self._transport.request(HTTPMethod.GET, f"{_PATH}/{movie_id}")
        return unwrap_single(Page[Movie].model_validate(data), resource=_PATH, identifier=movie_id)

    def quotes(self, movie_id: str, query: Query | None = None) -> Page[Quote]:
        """List the quotes belonging to a movie."""
        data = self._transport.request(
            HTTPMethod.GET, f"{_PATH}/{movie_id}/quote", query_string(query)
        )
        return Page[Quote].model_validate(data)

    def get_with_quotes(self, movie_id: str, query: Query | None = None) -> MovieWithQuotes:
        """Fetch a movie and a page of its quotes, combining the two calls."""
        movie = self.get(movie_id)
        quotes = self.quotes(movie_id, query)
        return MovieWithQuotes(movie=movie, quotes=quotes)

    def iter_all(self, query: Query | None = None) -> Iterator[Movie]:
        """Iterate over every matching movie, transparently fetching each page."""
        base = (query or Query()).copy()
        return paginate_sync(lambda page: self.list(base.copy().page(page)))


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

    async def get_with_quotes(self, movie_id: str, query: Query | None = None) -> MovieWithQuotes:
        """Fetch a movie and a page of its quotes, the two calls run concurrently."""
        movie, quotes = await asyncio.gather(self.get(movie_id), self.quotes(movie_id, query))
        return MovieWithQuotes(movie=movie, quotes=quotes)

    def iter_all(self, query: Query | None = None) -> AsyncIterator[Movie]:
        """Asynchronously iterate over every matching movie across all pages."""
        base = (query or Query()).copy()
        return paginate_async(lambda page: self.list(base.copy().page(page)))
