"""API resource groups."""

from __future__ import annotations

from .movies import AsyncMoviesResource, MoviesResource
from .quotes import AsyncQuotesResource, QuotesResource

__all__ = [
    "AsyncMoviesResource",
    "AsyncQuotesResource",
    "MoviesResource",
    "QuotesResource",
]
