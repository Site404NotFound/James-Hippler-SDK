"""Shared narration and query helpers for the runnable demos.

Imported by both ``demo_sync.py`` and ``demo_async.py`` so each demo function
stays small and focused on the SDK call it illustrates. The query cookbook does
no I/O, so the sync and async demos reuse it directly.
"""

from __future__ import annotations

import os
import sys
from urllib.parse import unquote

from lotr_sdk import MovieField, Query, QuoteField
from lotr_sdk.models import Movie, Quote


def require_api_key() -> bool:
    """Return ``True`` if ``THE_ONE_API_KEY`` is set, else explain how to set it."""
    if os.environ.get("THE_ONE_API_KEY"):
        return True
    print(
        "Set THE_ONE_API_KEY first (free key: https://the-one-api.dev/sign-up).",
        file=sys.stderr,
    )
    return False


def section(title: str) -> None:
    """Print a section header."""
    print(f"\n== {title} ==")


def format_movie(movie: Movie) -> str:
    """Render a movie on one line, surfacing every field of the model."""
    return (
        f"{movie.name} — ${movie.budget_in_millions:g}M budget, "
        f"${movie.box_office_revenue_in_millions:g}M box office, "
        f"{movie.academy_award_wins}/{movie.academy_award_nominations} Oscars, "
        f"{movie.rotten_tomatoes_score:g}% RT, {movie.runtime_in_minutes} min"
    )


def format_quote(quote: Quote) -> str:
    """Render a quote on one line, including its movie/character id references."""
    return f'"{quote.dialog}" (movie {quote.movie_id}, character {quote.character_id})'


def query_cookbook() -> None:
    """Print every Query operator, sort, and pagination call as it serializes.

    No requests are made: this shows the exact wire query string the builder
    produces, next to the human-readable (URL-decoded) form, so every part of
    the query surface is demonstrated without depending on live data.
    """
    chained = (
        Query()
        .where(MovieField.BUDGET_IN_MILLIONS)
        .gt(100)
        .where(MovieField.NAME)
        .matches("/the/i")
        .limit(5)
    )
    examples: list[tuple[str, Query]] = [
        (".eq(v)", Query().where(MovieField.NAME).eq("The Two Towers")),
        (".ne(v)", Query().where(MovieField.NAME).ne("The Hobbit Series")),
        (".in_(vs)", Query().where(MovieField.NAME).in_(["The Two Towers", "The Hobbit"])),
        (".not_in(vs)", Query().where(MovieField.NAME).not_in(["The Hobbit Series"])),
        (".exists()", Query().where(MovieField.ACADEMY_AWARD_WINS).exists()),
        (".not_exists()", Query().where(QuoteField.DIALOG).not_exists()),
        (".matches(re)", Query().where(MovieField.NAME).matches("/ring/i")),
        (".gt(v)", Query().where(MovieField.BUDGET_IN_MILLIONS).gt(100)),
        (".lt(v)", Query().where(MovieField.BUDGET_IN_MILLIONS).lt(100)),
        (".gte(v)", Query().where(MovieField.RUNTIME_IN_MINUTES).gte(160)),
        (".lte(v)", Query().where(MovieField.RUNTIME_IN_MINUTES).lte(200)),
        (".sort(asc)", Query().sort("name")),
        (".sort(desc)", Query().sort("name", descending=True)),
        (".limit(n)", Query().limit(10)),
        (".page(n)", Query().page(2)),
        (".offset(n)", Query().offset(5)),
        ("chained (AND)", chained),
    ]
    for label, query in examples:
        wire = query.to_query_string()
        print(f"  {label:<14} {unquote(wire):<40} (wire: {wire})")
