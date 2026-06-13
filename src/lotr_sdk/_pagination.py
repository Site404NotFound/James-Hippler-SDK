"""Auto-pagination helpers that walk every page of a list endpoint.

Both variants take a ``fetch`` callable that returns the page for a given
1-based page number, so the same walking logic serves any resource.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import TypeVar

from .models import Page

T = TypeVar("T")


def paginate_sync(fetch: Callable[[int], Page[T]]) -> Iterator[T]:
    """Yield every item across all pages, fetching each page lazily."""
    page_number = 1
    while True:
        page = fetch(page_number)
        yield from page.docs
        if not page.has_next_page:
            return
        page_number += 1


async def paginate_async(fetch: Callable[[int], Awaitable[Page[T]]]) -> AsyncIterator[T]:
    """Asynchronously yield every item across all pages, fetching each lazily."""
    page_number = 1
    while True:
        page = await fetch(page_number)
        for doc in page.docs:
            yield doc
        if not page.has_next_page:
            return
        page_number += 1
