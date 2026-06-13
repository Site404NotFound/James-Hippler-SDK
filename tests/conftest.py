"""Shared fixtures and sample payloads for the test suite."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest

from lotr_sdk import AsyncClient, Client

BASE_URL = "https://the-one-api.dev/v2"

MOVIE_JSON: dict[str, Any] = {
    "_id": "5cd95395de30eff6ebccde5d",
    "name": "The Two Towers",
    "runtimeInMinutes": 179,
    "budgetInMillions": 94,
    "boxOfficeRevenueInMillions": 926,
    "academyAwardNominations": 6,
    "academyAwardWins": 2,
    "rottenTomatoesScore": 96,
}

QUOTE_JSON: dict[str, Any] = {
    "_id": "5cd96e05de30eff6ebcce7e9",
    "dialog": "Deagol!",
    "movie": "5cd95395de30eff6ebccde5d",
    "character": "5cd99d4bde30eff6ebccfe9e",
}


def envelope(
    docs: list[dict[str, Any]], *, page: int = 1, pages: int = 1, limit: int = 1000
) -> dict[str, Any]:
    """Build an API list envelope around ``docs``."""
    return {
        "docs": docs,
        "total": len(docs),
        "limit": limit,
        "offset": 0,
        "page": page,
        "pages": pages,
    }


@pytest.fixture
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def client() -> Iterator[Client]:
    # backoff_factor=0 keeps retry tests instant.
    with Client(api_key="test-key", base_url=BASE_URL, backoff_factor=0) as c:
        yield c


@pytest.fixture
async def async_client() -> Any:
    async with AsyncClient(api_key="test-key", base_url=BASE_URL, backoff_factor=0) as c:
        yield c
