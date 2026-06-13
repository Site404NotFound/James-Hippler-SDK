"""Asynchronous auto-pagination."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from typing import TypeVar

from ..models import Page

__all__ = ["paginate_async"]

T = TypeVar("T")


async def iter_pages_async(fetch: Callable[[int], Awaitable[Page[T]]]) -> AsyncIterator[Page[T]]:
    """Yield each page in turn, fetching the next only while one remains.

    ``fetch`` returns the page for a given 1-based page number, so this walking
    logic serves any resource.
    """
    page = await fetch(1)
    yield page
    while page.has_next_page:
        page = await fetch(page.page + 1)
        yield page


async def paginate_async(fetch: Callable[[int], Awaitable[Page[T]]]) -> AsyncIterator[T]:
    """Asynchronously yield every item across all pages, fetching each lazily."""
    async for page in iter_pages_async(fetch):
        for doc in page.docs:
            yield doc
