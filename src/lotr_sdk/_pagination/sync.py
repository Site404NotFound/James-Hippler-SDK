"""Synchronous auto-pagination."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import TypeVar

from ..models import Page

__all__ = ["paginate_sync"]

T = TypeVar("T")


def paginate_sync(fetch: Callable[[int], Page[T]]) -> Iterator[T]:
    """Yield every item across all pages, fetching each page lazily.

    ``fetch`` returns the page for a given 1-based page number, so this walking
    logic serves any resource.
    """
    page_number = 1
    while True:
        page = fetch(page_number)
        yield from page.docs
        if not page.has_next_page:
            return
        page_number += 1
