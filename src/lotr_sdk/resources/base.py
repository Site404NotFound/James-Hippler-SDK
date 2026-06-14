"""Shared helpers for resource classes."""

from __future__ import annotations

from http import HTTPStatus
from typing import TypeVar

from ..exceptions import NotFoundError
from ..models import Page
from ..query import Query

T = TypeVar("T")


def query_string(query: Query | None) -> str:
    """Serialize an optional query, or the empty string when none is given."""
    return query.to_query_string() if query is not None else ""


def unwrap_single(page: Page[T], *, resource: str, identifier: str) -> T:
    """Return the single document from a get-by-id response.

    The API answers a missing id with HTTP 200 and an empty ``docs`` list, so
    absence is detected here and surfaced as :class:`NotFoundError`.
    """
    if not page.docs:
        raise NotFoundError(HTTPStatus.NOT_FOUND, f"No {resource} found with id '{identifier}'")
    return page.docs[0]
