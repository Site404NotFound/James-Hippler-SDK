"""Asynchronous resource groups."""

from __future__ import annotations

from .movies import AsyncMoviesResource
from .quotes import AsyncQuotesResource

__all__ = ["AsyncMoviesResource", "AsyncQuotesResource"]
