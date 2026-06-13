"""Runnable demonstration of the synchronous Client.

Usage:
    export THE_ONE_API_KEY=...        # or put it in a .env and `set -a; . ./.env`
    poetry run python examples/demo_sync.py
"""

from __future__ import annotations

import os
import sys

from lotr_sdk import Client, Query
from lotr_sdk.exceptions import ServerError


def main() -> int:
    if not os.environ.get("THE_ONE_API_KEY"):
        print(
            "Set THE_ONE_API_KEY first (free key: https://the-one-api.dev/sign-up).",
            file=sys.stderr,
        )
        return 1

    with Client() as client:  # reads THE_ONE_API_KEY from the environment
        print("== Movies ==")
        movies = client.movies.list()
        print(f"{movies.total} movies total. A few:")
        for movie in list(movies)[:5]:
            print(
                f"  - {movie.name} (budget ${movie.budget_in_millions}M, "
                f"{movie.academy_award_wins} Oscars)"
            )

        print("\n== Filter: budget over $100M ==")
        for movie in client.movies.list(Query().where("budgetInMillions").gt(100)):
            print(f"  - {movie.name}: ${movie.budget_in_millions}M")

        print("\n== Regex: names matching /ring/i ==")
        for movie in client.movies.list(Query().where("name").matches("/ring/i")):
            print(f"  - {movie.name}")

        print("\n== A movie and its quotes ==")
        sample = client.quotes.list(Query().limit(1))[0]
        movie = client.movies.get(sample.movie_id)
        quotes = client.movies.quotes(movie.id, Query().limit(3))
        print(f"  {movie.name} has {quotes.total} quotes; e.g.:")
        for quote in quotes:
            print(f'    "{quote.dialog}"')

        print("\n== Auto-pagination (limit=2 forces several pages) ==")
        count = sum(1 for _ in client.movies.iter_all(Query().limit(2)))
        print(f"  iter_all() transparently walked every page and yielded {count} movies")

        print("\n== Typed errors ==")
        try:
            client.movies.list(Query().sort("name"))
        except ServerError as exc:
            print(f"  the live API 500s when sorting /movie -> {type(exc).__name__}: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
