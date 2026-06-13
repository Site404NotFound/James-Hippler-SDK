"""Runnable demonstration of the asynchronous AsyncClient.

Usage:
    export THE_ONE_API_KEY=...        # or put it in a .env and `set -a; . ./.env`
    poetry run python examples/demo_async.py
"""

from __future__ import annotations

import asyncio
import os
import sys

from lotr_sdk import AsyncClient, Query


async def main() -> int:
    if not os.environ.get("THE_ONE_API_KEY"):
        print(
            "Set THE_ONE_API_KEY first (free key: https://the-one-api.dev/sign-up).",
            file=sys.stderr,
        )
        return 1

    async with AsyncClient() as client:  # reads THE_ONE_API_KEY from the environment
        # Fetch independent resources concurrently — the payoff of the async client.
        movies, quotes = await asyncio.gather(
            client.movies.list(Query().where("budgetInMillions").gt(100)),
            client.quotes.list(Query().limit(3)),
        )

        print("== Movies with budget over $100M (fetched concurrently) ==")
        for movie in movies:
            print(f"  - {movie.name}: ${movie.budget_in_millions}M")

        print(f"\n== {quotes.total} quotes total; first few ==")
        for quote in quotes:
            print(f'  "{quote.dialog}"')

        print("\n== Async auto-pagination ==")
        count = 0
        async for _ in client.movies.iter_all(Query().limit(2)):
            count += 1
        print(f"  async iter_all() walked every page and yielded {count} movies")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
