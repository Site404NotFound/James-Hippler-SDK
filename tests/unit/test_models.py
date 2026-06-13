"""Tests for Pydantic models: field aliasing, forward-compat, and Page ergonomics."""

from __future__ import annotations

import pytest

from lotr_sdk.models import Movie, Page, Quote

MOVIE_JSON = {
    "_id": "5cd95395de30eff6ebccde5d",
    "name": "The Two Towers",
    "runtimeInMinutes": 179,
    "budgetInMillions": 94,
    "boxOfficeRevenueInMillions": 926,
    "academyAwardNominations": 6,
    "academyAwardWins": 2,
    "rottenTomatoesScore": 96,
}

QUOTE_JSON = {
    "_id": "5cd96e05de30eff6ebcce7e9",
    "dialog": "Deagol!",
    "movie": "5cd95395de30eff6ebccde5d",
    "character": "5cd99d4bde30eff6ebccfe9e",
}


def test_movie_maps_api_aliases_to_snake_case() -> None:
    movie = Movie.model_validate(MOVIE_JSON)
    assert movie.id == "5cd95395de30eff6ebccde5d"
    assert movie.name == "The Two Towers"
    assert movie.runtime_in_minutes == 179
    assert movie.box_office_revenue_in_millions == 926
    assert movie.academy_award_wins == 2


def test_quote_maps_reference_aliases() -> None:
    quote = Quote.model_validate(QUOTE_JSON)
    assert quote.id == "5cd96e05de30eff6ebcce7e9"
    assert quote.dialog == "Deagol!"
    assert quote.movie_id == "5cd95395de30eff6ebccde5d"
    assert quote.character_id == "5cd99d4bde30eff6ebccfe9e"


def test_unknown_fields_are_ignored_for_forward_compatibility() -> None:
    movie = Movie.model_validate({**MOVIE_JSON, "newFieldFromFutureApi": "ignored"})
    assert movie.name == "The Two Towers"


def test_models_are_immutable() -> None:
    movie = Movie.model_validate(MOVIE_JSON)
    with pytest.raises(Exception):  # noqa: B017 - pydantic raises on frozen mutation
        movie.name = "changed"  # type: ignore[misc]


def test_page_parses_envelope_into_typed_docs() -> None:
    page = Page[Movie].model_validate(
        {"docs": [MOVIE_JSON], "total": 8, "limit": 1, "offset": 0, "page": 1, "pages": 8}
    )
    assert page.total == 8
    assert isinstance(page.docs[0], Movie)
    assert page.docs[0].name == "The Two Towers"


def test_page_is_a_friendly_sequence() -> None:
    page = Page[Movie].model_validate(
        {
            "docs": [MOVIE_JSON, MOVIE_JSON],
            "total": 2,
            "limit": 2,
            "offset": 0,
            "page": 1,
            "pages": 1,
        }
    )
    assert len(page) == 2
    assert page[0].name == "The Two Towers"
    assert [m.name for m in page] == ["The Two Towers", "The Two Towers"]


@pytest.mark.parametrize(
    ("page_num", "pages", "expected"),
    [(1, 8, True), (7, 8, True), (8, 8, False), (1, 1, False)],
)
def test_page_reports_whether_more_pages_exist(page_num: int, pages: int, expected: bool) -> None:
    page = Page[Movie].model_validate(
        {"docs": [], "total": 8, "limit": 1, "offset": 0, "page": page_num, "pages": pages}
    )
    assert page.has_next_page is expected
