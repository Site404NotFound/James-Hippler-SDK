"""Asynchronous auto-pagination."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from typing import TypeVar

from ..models import Page

__all__ = ["paginate_async"]

T = TypeVar("T")


async def paginate_async(fetch: Callable[[int], Awaitable[Page[T]]]) -> AsyncIterator[T]:
    """Asynchronously yield every item across all pages, fetching each lazily.

    ``fetch`` returns the page for a given 1-based page number, so this walking
    logic serves any resource.
    """
    page_number = 1
    while True:
        page = await fetch(page_number)
        for doc in page.docs:
            yield doc
        if not page.has_next_page:
            return
        page_number += 1
