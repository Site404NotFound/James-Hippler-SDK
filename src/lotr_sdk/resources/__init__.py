"""API resource groups; each endpoint's sync and async twins share a module."""

from __future__ import annotations

from lotr_sdk.resources.movies import AsyncMoviesResource, MoviesResource
from lotr_sdk.resources.quotes import AsyncQuotesResource, QuotesResource

__all__ = [
    "AsyncMoviesResource",
    "AsyncQuotesResource",
    "MoviesResource",
    "QuotesResource",
]
