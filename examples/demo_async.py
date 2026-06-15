"""Comprehensive, runnable demonstration of the asynchronous AsyncClient.

Mirrors ``demo_sync.py`` with one small function per concept, but leans on the
async payoff: ``asyncio.gather`` for concurrent requests and ``async for`` over
``iter_all``. Each function makes real calls to The One API; the final query
cookbook makes none.

Usage:
    export THE_ONE_API_KEY=...        # or put it in a .env and `set -a; . ./.env`
    poetry run python examples/demo_async.py
"""

from __future__ import annotations

import asyncio

from demo_helpers import (
    format_movie,
    format_quote,
    query_cookbook,
    require_api_key,
    section,
)

from lotr_sdk import AsyncClient, MovieField, Query, QuoteField, RegexFlag
from lotr_sdk.exceptions import NotFoundError, ServerError


async def demo_concurrent_fetch(client: AsyncClient) -> None:
    """asyncio.gather — fetch independent movie and quote pages concurrently."""
    section("Concurrent fetch (asyncio.gather — the async payoff)")
    movies, quotes = await asyncio.gather(
        client.movies.list(Query().where(MovieField.BUDGET_IN_MILLIONS).gt(100)),
        client.quotes.list(Query().limit(3)),
    )
    print(f"  fetched {len(movies)} movies and {len(quotes)} quotes at once")
    for movie in movies[:3]:
        print(f"  - {format_movie(movie)}")
    for quote in quotes:
        print(f"  - {format_quote(quote)}")


async def demo_get_movie(client: AsyncClient) -> None:
    """GET /movie/{id} — take an id from a list, fetch the full record."""
    section("Get one movie (/movie/{id})")
    sample = (await client.movies.list(Query().limit(1)))[0]
    movie = await client.movies.get(sample.id)
    print(f"  - {format_movie(movie)}")


async def demo_movie_quotes(client: AsyncClient) -> None:
    """GET /movie/{id}/quote — list the quotes belonging to a movie."""
    section("Quotes for a movie (/movie/{id}/quote)")
    movies = await client.movies.list(
        Query().where(MovieField.NAME).matches("two towers", flags=[RegexFlag.IGNORE_CASE])
    )
    movie = movies[0]
    quotes = await client.movies.quotes(movie.id, Query().limit(3))
    print(f"  {movie.name} has {quotes.total} quotes; first {len(quotes)}:")
    for quote in quotes:
        print(f"  - {format_quote(quote)}")


async def demo_movie_with_quotes(client: AsyncClient) -> None:
    """get_with_quotes — bundles a movie and its quotes, fetched concurrently."""
    section("Combined call: movie + its quotes (fetched concurrently)")
    movies = await client.movies.list(
        Query().where(MovieField.NAME).matches("two towers", flags=[RegexFlag.IGNORE_CASE])
    )
    bundle = await client.movies.get_with_quotes(movies[0].id, Query().limit(2))
    print(f"  {bundle.movie.name}: {bundle.quotes.total} quotes; first {len(bundle.quotes)}:")
    for quote in bundle.quotes:
        print(f"  - {format_quote(quote)}")


async def demo_get_quote(client: AsyncClient) -> None:
    """GET /quote and GET /quote/{id}."""
    section("Quotes (/quote and /quote/{id})")
    sample = (await client.quotes.list(Query().limit(1)))[0]
    quote = await client.quotes.get(sample.id)
    print(f"  - {format_quote(quote)}")


async def demo_filtering(client: AsyncClient) -> None:
    """Live filters that return real data, including chained (ANDed) clauses."""
    section("Filtering (live)")

    print("  name matches /ring/i:")
    for movie in await client.movies.list(
        Query().where(MovieField.NAME).matches("ring", flags=[RegexFlag.IGNORE_CASE])
    ):
        print(f"  - {movie.name}")

    print("  budget > $100M AND > 1 Oscar win (chained .where is ANDed):")
    query = (
        Query()
        .where(MovieField.BUDGET_IN_MILLIONS)
        .gt(100)
        .where(MovieField.ACADEMY_AWARD_WINS)
        .gt(1)
    )
    for movie in await client.movies.list(query):
        print(f"  - {movie.name}: {movie.academy_award_wins} wins")


async def demo_field_enums(client: AsyncClient) -> None:
    """Typo-safe MovieField / QuoteField members instead of raw strings."""
    section("Typo-safe field enums (MovieField / QuoteField)")
    movies = await client.movies.list(Query().where(MovieField.ROTTEN_TOMATOES_SCORE).gte(90))
    print(f"  {movies.total} movies with RT >= 90 (MovieField.ROTTEN_TOMATOES_SCORE)")
    quotes = await client.quotes.list(
        Query().where(QuoteField.DIALOG).matches("precious", flags=[RegexFlag.IGNORE_CASE]).limit(3)
    )
    print(f"  {quotes.total} quotes match /precious/i (QuoteField.DIALOG); first {len(quotes)}:")
    for quote in quotes:
        print(f'  - "{quote.dialog}"')


async def demo_async_pagination(client: AsyncClient) -> None:
    """Read Page metadata, then walk every page with async iter_all."""
    section("Async pagination (limit / page, then async iter_all)")
    first = await client.movies.list(Query().limit(2))
    print(f"  limit=2 -> page {first.page}/{first.pages}, has_next_page={first.has_next_page}")
    count = 0
    async for _ in client.movies.iter_all(Query().limit(2)):
        count += 1
    print(f"  async iter_all() yielded {count} movies across all pages")


async def demo_errors(client: AsyncClient) -> None:
    """The typed error hierarchy: a missing id and an upstream 500."""
    section("Typed errors")
    try:
        await client.movies.get("5cd95395de30eff6ebccdeff")
    except NotFoundError as exc:
        print(f"  missing id     -> {type(exc).__name__}: {exc}")
    try:
        await client.movies.list(Query().sort("name"))
    except ServerError as exc:
        print(f"  sorting /movie -> {type(exc).__name__}: {exc}")


def demo_query_surface() -> None:
    """Every operator/sort/pagination call and what it serializes to (no calls)."""
    section("Full query surface (no requests — shows what each call serializes to)")
    query_cookbook()


async def main() -> int:
    if not require_api_key():
        return 1

    async with AsyncClient() as client:  # reads THE_ONE_API_KEY from the environment
        await demo_concurrent_fetch(client)
        await demo_get_movie(client)
        await demo_movie_quotes(client)
        await demo_movie_with_quotes(client)
        await demo_get_quote(client)
        await demo_filtering(client)
        await demo_field_enums(client)
        await demo_async_pagination(client)
        await demo_errors(client)

    demo_query_surface()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
