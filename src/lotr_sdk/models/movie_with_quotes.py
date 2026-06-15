"""The ``MovieWithQuotes`` result returned by ``movies.get_with_quotes``."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from lotr_sdk.models.movie import Movie
from lotr_sdk.models.page import Page
from lotr_sdk.models.quote import Quote

__all__ = ["MovieWithQuotes"]


class MovieWithQuotes(BaseModel):
    """A movie together with a page of its quotes.

    Returned by ``movies.get_with_quotes``, which combines ``GET /movie/{id}``
    and ``GET /movie/{id}/quote`` — the async client issues the two concurrently.

    Unlike :class:`~lotr_sdk.models.base.ResourceModel`, this is a plain frozen
    ``BaseModel``: it is assembled in code from already-parsed objects rather than
    deserialized from the API (so it needs no aliasing), but it stays immutable
    and serializable (``model_dump``) like the rest of the models.
    """

    model_config = ConfigDict(frozen=True)

    movie: Movie
    quotes: Page[Quote]
