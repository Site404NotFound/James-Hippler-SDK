"""Comprehensive, runnable demonstration of the synchronous Client.

Exercises every movie and quote capability — list/get, a movie's quotes,
filtering, field enums, pagination, auto-pagination, and typed errors — with one
small function per concept. Each function makes real calls to The One API; the
final query cookbook makes none.

Usage:
    export THE_ONE_API_KEY=...        # or put it in a .env and `set -a; . ./.env`
    poetry run python examples/demo_sync.py
"""

from __future__ import annotations

from demo_helpers import (
    format_movie,
    format_quote,
    query_cookbook,
    require_api_key,
    section,
)

from lotr_sdk import Client, MovieField, Query, QuoteField
from lotr_sdk.exceptions import NotFoundError, ServerError


def demo_list_movies(client: Client) -> None:
    """GET /movie — list movies and read the Page envelope metadata."""
    section("List movies (/movie)")
    movies = client.movies.list()
    print(f"{movies.total} movies total (page {movies.page}/{movies.pages}, limit {movies.limit}).")
    for movie in movies[:3]:
        print(f"  - {format_movie(movie)}")


def demo_get_movie(client: Client) -> None:
    """GET /movie/{id} — take an id from a list, fetch the full record."""
    section("Get one movie (/movie/{id})")
    sample = client.movies.list(Query().limit(1))[0]
    movie = client.movies.get(sample.id)
    print(f"  fetched by id {movie.id}:")
    print(f"  - {format_movie(movie)}")


def demo_movie_quotes(client: Client) -> None:
    """GET /movie/{id}/quote — list the quotes belonging to a movie."""
    section("Quotes for a movie (/movie/{id}/quote)")
    movie = client.movies.list(Query().where(MovieField.NAME).matches("/two towers/i"))[0]
    quotes = client.movies.quotes(movie.id, Query().limit(3))
    print(f"  {movie.name} has {quotes.total} quotes; first {len(quotes)}:")
    for quote in quotes:
        print(f"  - {format_quote(quote)}")


def demo_list_quotes(client: Client) -> None:
    """GET /quote — list quotes."""
    section("List quotes (/quote)")
    quotes = client.quotes.list(Query().limit(3))
    print(f"{quotes.total} quotes total; first {len(quotes)}:")
    for quote in quotes:
        print(f"  - {format_quote(quote)}")


def demo_get_quote(client: Client) -> None:
    """GET /quote/{id} — fetch a single quote by id."""
    section("Get one quote (/quote/{id})")
    sample = client.quotes.list(Query().limit(1))[0]
    quote = client.quotes.get(sample.id)
    print(f"  - {format_quote(quote)}")


def demo_filtering(client: Client) -> None:
    """Live filters that return real data, including chained (ANDed) clauses."""
    section("Filtering (live)")

    print("  budget > $100M:")
    for movie in client.movies.list(Query().where(MovieField.BUDGET_IN_MILLIONS).gt(100)):
        print(f"  - {movie.name}: ${movie.budget_in_millions:g}M")

    print("  name matches /ring/i:")
    for movie in client.movies.list(Query().where(MovieField.NAME).matches("/ring/i")):
        print(f"  - {movie.name}")

    print("  budget > $100M AND > 1 Oscar win (chained .where is ANDed):")
    query = (
        Query()
        .where(MovieField.BUDGET_IN_MILLIONS)
        .gt(100)
        .where(MovieField.ACADEMY_AWARD_WINS)
        .gt(1)
    )
    for movie in client.movies.list(query):
        print(f"  - {movie.name}: {movie.academy_award_wins} wins")


def demo_field_enums(client: Client) -> None:
    """Typo-safe MovieField / QuoteField members instead of raw strings."""
    section("Typo-safe field enums (MovieField / QuoteField)")
    movies = client.movies.list(Query().where(MovieField.ROTTEN_TOMATOES_SCORE).gte(90))
    print(f"  {movies.total} movies with RT >= 90 (MovieField.ROTTEN_TOMATOES_SCORE)")
    quotes = client.quotes.list(Query().where(QuoteField.DIALOG).matches("/precious/i").limit(3))
    print(f"  {quotes.total} quotes match /precious/i (QuoteField.DIALOG); first {len(quotes)}:")
    for quote in quotes:
        print(f'  - "{quote.dialog}"')


def demo_pagination(client: Client) -> None:
    """limit / page / offset by hand, then iter_all to walk every page."""
    section("Pagination (limit / page / offset / has_next_page)")
    first = client.movies.list(Query().limit(2))
    print(f"  limit=2  -> page {first.page}/{first.pages}, has_next_page={first.has_next_page}")
    second = client.movies.list(Query().limit(2).page(2))
    print(f"  page=2   -> {[m.name for m in second]}")
    skipped = client.movies.list(Query().limit(2).offset(1))
    print(f"  offset=1 -> {[m.name for m in skipped]}")

    section("Auto-pagination (iter_all walks every page)")
    count = sum(1 for _ in client.movies.iter_all(Query().limit(2)))
    print(f"  iter_all() yielded {count} movies across all pages")


def demo_errors(client: Client) -> None:
    """The typed error hierarchy: a missing id and an upstream 500."""
    section("Typed errors")
    try:
        client.movies.get("5cd95395de30eff6ebccdeff")
    except NotFoundError as exc:
        print(f"  missing id        -> {type(exc).__name__}: {exc}")
    try:
        client.movies.list(Query().sort("name"))
    except ServerError as exc:
        print(f"  sorting /movie    -> {type(exc).__name__}: {exc}")


def demo_query_surface() -> None:
    """Every operator/sort/pagination call and what it serializes to (no calls)."""
    section("Full query surface (no requests — shows what each call serializes to)")
    query_cookbook()


def main() -> int:
    if not require_api_key():
        return 1

    with Client() as client:  # reads THE_ONE_API_KEY from the environment
        demo_list_movies(client)
        demo_get_movie(client)
        demo_movie_quotes(client)
        demo_list_quotes(client)
        demo_get_quote(client)
        demo_filtering(client)
        demo_field_enums(client)
        demo_pagination(client)
        demo_errors(client)

    demo_query_surface()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
