"""API resource groups, split by execution model into ``sync`` and ``aio``."""

from __future__ import annotations

from lotr_sdk.resources.aio import AsyncMoviesResource, AsyncQuotesResource
from lotr_sdk.resources.sync import MoviesResource, QuotesResource

__all__ = [
    "AsyncMoviesResource",
    "AsyncQuotesResource",
    "MoviesResource",
    "QuotesResource",
]
