"""Synchronous movie resource: ``/movie``, ``/movie/{id}``, ``/movie/{id}/quote``."""

from __future__ import annotations

from collections.abc import Iterator

from ..._pagination import paginate_sync
from ..._transport import SyncTransport
from ...models import Movie, Page, Quote
from ...query import Query
from ..base import query_string, unwrap_single

__all__ = ["MoviesResource"]

_PATH = "movie"


class MoviesResource:
    """Synchronous access to movie endpoints."""

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(self, query: Query | None = None) -> Page[Movie]:
        """List movies, optionally filtered/sorted/paginated by ``query``."""
        data = self._transport.request("GET", _PATH, query_string(query))
        return Page[Movie].model_validate(data)

    def get(self, movie_id: str) -> Movie:
        """Fetch a single movie by id, raising ``NotFoundError`` if absent."""
        data = self._transport.request("GET", f"{_PATH}/{movie_id}")
        return unwrap_single(
            Page[Movie].model_validate(data), resource="movie", identifier=movie_id
        )

    def quotes(self, movie_id: str, query: Query | None = None) -> Page[Quote]:
        """List the quotes belonging to a movie."""
        data = self._transport.request("GET", f"{_PATH}/{movie_id}/quote", query_string(query))
        return Page[Quote].model_validate(data)

    def iter_all(self, query: Query | None = None) -> Iterator[Movie]:
        """Iterate over every matching movie, transparently fetching each page."""
        base = (query or Query()).copy()
        return paginate_sync(lambda page: self.list(base.copy().page(page)))
