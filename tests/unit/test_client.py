"""End-to-end tests of the public Client / AsyncClient surface (respx-mocked)."""

from __future__ import annotations

import httpx
import pytest
import respx

from lotr_sdk import AsyncClient, Client, Movie, Page, Quote
from lotr_sdk.exceptions import NotFoundError
from tests.conftest import BASE_URL, MOVIE_JSON, QUOTE_JSON, envelope


@respx.mock
def test_movies_list_returns_typed_page(client: Client) -> None:
    respx.get(f"{BASE_URL}/movie").mock(
        return_value=httpx.Response(200, json=envelope([MOVIE_JSON]))
    )
    page = client.movies.list()
    assert isinstance(page, Page)
    assert isinstance(page[0], Movie)
    assert page[0].name == "The Two Towers"


@respx.mock
def test_movies_list_forwards_query(client: Client) -> None:
    from lotr_sdk import Query

    route = respx.get(url__startswith=f"{BASE_URL}/movie").mock(
        return_value=httpx.Response(200, json=envelope([MOVIE_JSON]))
    )
    client.movies.list(Query().where("budgetInMillions").gt(90).limit(5))
    assert route.calls.last.request.url.query == b"budgetInMillions%3E90&limit=5"


@respx.mock
def test_movies_get_unwraps_single_doc(client: Client) -> None:
    respx.get(f"{BASE_URL}/movie/{MOVIE_JSON['_id']}").mock(
        return_value=httpx.Response(200, json=envelope([MOVIE_JSON]))
    )
    movie = client.movies.get(MOVIE_JSON["_id"])
    assert isinstance(movie, Movie)
    assert movie.id == MOVIE_JSON["_id"]


@respx.mock
def test_movies_get_raises_not_found_on_empty_docs(client: Client) -> None:
    respx.get(f"{BASE_URL}/movie/missing").mock(return_value=httpx.Response(200, json=envelope([])))
    with pytest.raises(NotFoundError):
        client.movies.get("missing")


@respx.mock
def test_movie_quotes_subresource(client: Client) -> None:
    respx.get(f"{BASE_URL}/movie/{MOVIE_JSON['_id']}/quote").mock(
        return_value=httpx.Response(200, json=envelope([QUOTE_JSON]))
    )
    page = client.movies.quotes(MOVIE_JSON["_id"])
    assert isinstance(page[0], Quote)
    assert page[0].dialog == "Deagol!"


@respx.mock
def test_quotes_list_and_get(client: Client) -> None:
    respx.get(f"{BASE_URL}/quote").mock(
        return_value=httpx.Response(200, json=envelope([QUOTE_JSON]))
    )
    respx.get(f"{BASE_URL}/quote/{QUOTE_JSON['_id']}").mock(
        return_value=httpx.Response(200, json=envelope([QUOTE_JSON]))
    )
    assert client.quotes.list()[0].dialog == "Deagol!"
    assert client.quotes.get(QUOTE_JSON["_id"]).movie_id == MOVIE_JSON["_id"]


@respx.mock
def test_iter_all_walks_every_page(client: Client) -> None:
    route = respx.get(url__startswith=f"{BASE_URL}/movie").mock(
        side_effect=[
            httpx.Response(200, json=envelope([MOVIE_JSON, MOVIE_JSON], page=1, pages=2, limit=2)),
            httpx.Response(200, json=envelope([MOVIE_JSON], page=2, pages=2, limit=2)),
        ]
    )
    movies = list(client.movies.iter_all())
    assert len(movies) == 3
    assert route.call_count == 2


def test_client_closes_underlying_http_client() -> None:
    client = Client(api_key="test-key", base_url=BASE_URL)
    client.close()
    assert client._transport._client.is_closed


@respx.mock
async def test_async_movies_list(async_client: AsyncClient) -> None:
    respx.get(f"{BASE_URL}/movie").mock(
        return_value=httpx.Response(200, json=envelope([MOVIE_JSON]))
    )
    page = await async_client.movies.list()
    assert page[0].name == "The Two Towers"


@respx.mock
async def test_async_movies_get_not_found(async_client: AsyncClient) -> None:
    respx.get(f"{BASE_URL}/movie/missing").mock(return_value=httpx.Response(200, json=envelope([])))
    with pytest.raises(NotFoundError):
        await async_client.movies.get("missing")


@respx.mock
def test_sync_quotes_iter_all(client: Client) -> None:
    respx.get(url__startswith=f"{BASE_URL}/quote").mock(
        return_value=httpx.Response(200, json=envelope([QUOTE_JSON]))
    )
    assert len(list(client.quotes.iter_all())) == 1


@respx.mock
async def test_async_movies_get_and_quotes(async_client: AsyncClient) -> None:
    respx.get(f"{BASE_URL}/movie/{MOVIE_JSON['_id']}").mock(
        return_value=httpx.Response(200, json=envelope([MOVIE_JSON]))
    )
    respx.get(f"{BASE_URL}/movie/{MOVIE_JSON['_id']}/quote").mock(
        return_value=httpx.Response(200, json=envelope([QUOTE_JSON]))
    )
    movie = await async_client.movies.get(MOVIE_JSON["_id"])
    assert movie.name == "The Two Towers"
    quotes = await async_client.movies.quotes(MOVIE_JSON["_id"])
    assert quotes[0].dialog == "Deagol!"


@respx.mock
async def test_async_quotes_list_and_get(async_client: AsyncClient) -> None:
    respx.get(f"{BASE_URL}/quote").mock(
        return_value=httpx.Response(200, json=envelope([QUOTE_JSON]))
    )
    respx.get(f"{BASE_URL}/quote/{QUOTE_JSON['_id']}").mock(
        return_value=httpx.Response(200, json=envelope([QUOTE_JSON]))
    )
    assert (await async_client.quotes.list())[0].dialog == "Deagol!"
    assert (await async_client.quotes.get(QUOTE_JSON["_id"])).id == QUOTE_JSON["_id"]


@respx.mock
async def test_async_movies_iter_all(async_client: AsyncClient) -> None:
    respx.get(url__startswith=f"{BASE_URL}/movie").mock(
        side_effect=[
            httpx.Response(200, json=envelope([MOVIE_JSON, MOVIE_JSON], page=1, pages=2, limit=2)),
            httpx.Response(200, json=envelope([MOVIE_JSON], page=2, pages=2, limit=2)),
        ]
    )
    movies = [m async for m in async_client.movies.iter_all()]
    assert len(movies) == 3


@respx.mock
async def test_async_iter_all_walks_every_page(async_client: AsyncClient) -> None:
    respx.get(url__startswith=f"{BASE_URL}/quote").mock(
        side_effect=[
            httpx.Response(200, json=envelope([QUOTE_JSON, QUOTE_JSON], page=1, pages=2, limit=2)),
            httpx.Response(200, json=envelope([QUOTE_JSON], page=2, pages=2, limit=2)),
        ]
    )
    quotes = [q async for q in async_client.quotes.iter_all()]
    assert len(quotes) == 3
