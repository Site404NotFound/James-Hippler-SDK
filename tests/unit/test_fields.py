"""Tests for the query-field enums and their alignment with the models."""

from __future__ import annotations

from pydantic import BaseModel

from lotr_sdk import MovieField, QuoteField
from lotr_sdk.models import Movie, Quote
from lotr_sdk.query import Query


def _api_fields(model: type[BaseModel]) -> set[str]:
    """The set of wire field names a model exposes (alias where defined)."""
    return {field.alias or name for name, field in model.model_fields.items()}


def test_movie_field_enum_matches_model() -> None:
    assert {member.value for member in MovieField} == _api_fields(Movie)


def test_quote_field_enum_matches_model() -> None:
    assert {member.value for member in QuoteField} == _api_fields(Quote)


def test_field_enum_query_matches_raw_string() -> None:
    enum_form = Query().where(MovieField.BUDGET_IN_MILLIONS).gt(100).to_query_string()
    raw_form = Query().where("budgetInMillions").gt(100).to_query_string()
    assert enum_form == raw_form == "budgetInMillions%3E100"
