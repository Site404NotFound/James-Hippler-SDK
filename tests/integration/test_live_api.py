"""Integration tests that exercise the real API.

These are opt-in: they are marked ``integration`` (excluded from the default CI
run via ``-m "not integration"``) and skip entirely unless ``THE_ONE_API_KEY``
is set. Run them with::

    THE_ONE_API_KEY=... poetry run pytest -m integration
"""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

from lotr_sdk import AsyncClient, Client, Movie, Query, Quote
from lotr_sdk.exceptions import NotFoundError, ServerError

pytestmark = pytest.mark.integration

if not os.environ.get("THE_ONE_API_KEY"):
    pytest.skip("THE_ONE_API_KEY not set; skipping live integration tests", allow_module_level=True)

# A well-formed ObjectId that does not exist, for the not-found path.
MISSING_ID = "5cd95395de30eff6ebccdeff"


@pytest.fixture(scope="module")
def client() -> Iterator[Client]:
    with Client() as c:
        yield c


def test_list_movies(client: Client) -> None:
    page = client.movies.list()
    assert page.total >= 8
    assert all(isinstance(movie, Movie) for movie in page)


def test_filter_movies_by_budget(client: Client) -> None:
    page = client.movies.list(Query().where("budgetInMillions").gt(100))
    assert page.total >= 1
    assert all(movie.budget_in_millions > 100 for movie in page)


def test_regex_filter_on_name(client: Client) -> None:
    page = client.movies.list(Query().where("name").matches("/ring/i"))
    assert all("ring" in movie.name.lower() for movie in page)


def test_get_movie_by_id_round_trips(client: Client) -> None:
    listed = client.movies.list(Query().limit(1))[0]
    fetched = client.movies.get(listed.id)
    assert fetched.id == listed.id
    assert fetched.name == listed.name


def test_get_missing_movie_raises_not_found(client: Client) -> None:
    with pytest.raises(NotFoundError):
        client.movies.get(MISSING_ID)


def test_list_quotes(client: Client) -> None:
    page = client.quotes.list(Query().limit(5))
    assert page.total > 100
    assert all(isinstance(quote, Quote) for quote in page)


def test_get_quote_and_its_movie_quotes(client: Client) -> None:
    quote = client.quotes.list(Query().limit(1))[0]
    assert client.quotes.get(quote.id).id == quote.id

    movie_quotes = client.movies.quotes(quote.movie_id, Query().limit(3))
    assert movie_quotes.total >= 1


def test_iter_all_walks_every_movie(client: Client) -> None:
    total = client.movies.list().total
    streamed = list(client.movies.iter_all(Query().limit(2)))
    assert len(streamed) == total


def test_sort_on_movie_surfaces_upstream_server_error(client: Client) -> None:
    # The live API currently returns HTTP 500 when sorting /movie (works on
    # /book and /character). This asserts the SDK maps it cleanly; remove if
    # the upstream behavior changes.
    with pytest.raises(ServerError):
        client.movies.list(Query().sort("name"))


async def test_async_client_lists_movies() -> None:
    async with AsyncClient() as client:
        page = await client.movies.list(Query().limit(2))
        assert len(page) >= 1
        assert isinstance(page[0], Movie)
