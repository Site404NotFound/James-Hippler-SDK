"""API resource groups, split by execution model into ``sync`` and ``async_``."""

from __future__ import annotations

from .async_ import AsyncMoviesResource, AsyncQuotesResource
from .sync import MoviesResource, QuotesResource

__all__ = [
    "AsyncMoviesResource",
    "AsyncQuotesResource",
    "MoviesResource",
    "QuotesResource",
]
