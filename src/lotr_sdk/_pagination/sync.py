"""Synchronous auto-pagination."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import TypeVar

from ..models import Page

__all__ = ["paginate_sync"]

T = TypeVar("T")


def iter_pages_sync(fetch: Callable[[int], Page[T]]) -> Iterator[Page[T]]:
    """Yield each page in turn, fetching the next only while one remains.

    ``fetch`` returns the page for a given 1-based page number, so this walking
    logic serves any resource.
    """
    page = fetch(1)
    yield page
    while page.has_next_page:
        page = fetch(page.page + 1)
        yield page


def paginate_sync(fetch: Callable[[int], Page[T]]) -> Iterator[T]:
    """Yield every item across all pages, fetching each page lazily."""
    for page in iter_pages_sync(fetch):
        yield from page.docs
