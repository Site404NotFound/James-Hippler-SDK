"""Tests for the fluent Query builder and its wire serialization.

The expected query strings were validated against the live API: the server
URL-decodes before parsing, so operators are percent-encoded while the ``=``
key/value separator and ``&`` joins stay literal. ``>``/``<`` are valueless
tokens (``field>value``); ``>=``/``<=``/``=``/``!=`` use a literal ``=``.
"""

from __future__ import annotations

import pytest

from lotr_sdk.query import Query


def qs(query: Query) -> str:
    return query.to_query_string()


def test_empty_query_serializes_to_empty_string() -> None:
    assert qs(Query()) == ""


def test_eq_match_encodes_value() -> None:
    assert qs(Query().where("name").eq("The Two Towers")) == "name=The%20Two%20Towers"


def test_ne_negates_via_bang_on_the_key() -> None:
    assert qs(Query().where("name").ne("Frodo")) == "name%21=Frodo"


def test_in_builds_a_comma_list() -> None:
    assert qs(Query().where("name").in_(["Gandalf", "Frodo"])) == "name=Gandalf%2CFrodo"


def test_not_in_negates_a_comma_list() -> None:
    assert qs(Query().where("name").not_in(["Gandalf", "Frodo"])) == "name%21=Gandalf%2CFrodo"


def test_gt_is_a_valueless_token() -> None:
    assert qs(Query().where("budgetInMillions").gt(100)) == "budgetInMillions%3E100"


def test_lt_is_a_valueless_token() -> None:
    assert qs(Query().where("budgetInMillions").lt(100)) == "budgetInMillions%3C100"


def test_gte_uses_a_literal_equals_separator() -> None:
    assert qs(Query().where("runtimeInMinutes").gte(200)) == "runtimeInMinutes%3E=200"


def test_lte_uses_a_literal_equals_separator() -> None:
    assert qs(Query().where("runtimeInMinutes").lte(200)) == "runtimeInMinutes%3C=200"


def test_exists_is_a_bare_key() -> None:
    assert qs(Query().where("name").exists()) == "name"


def test_not_exists_prefixes_a_bang() -> None:
    assert qs(Query().where("name").not_exists()) == "%21name"


def test_matches_passes_a_regex_literal() -> None:
    assert qs(Query().where("name").matches("/ring/i")) == "name=%2Fring%2Fi"


def test_boolean_values_render_lowercase() -> None:
    assert qs(Query().where("isReal").eq(True)) == "isReal=true"
    assert qs(Query().where("isReal").eq(False)) == "isReal=false"


def test_copy_is_independent_of_the_original() -> None:
    original = Query().where("name").eq("Frodo").limit(5)
    clone = original.copy()
    clone.where("budgetInMillions").gt(100).page(2)

    assert qs(original) == "name=Frodo&limit=5"
    assert qs(clone) == "name=Frodo&budgetInMillions%3E100&limit=5&page=2"


def test_sort_ascending_by_default() -> None:
    assert qs(Query().sort("name")) == "sort=name%3Aasc"


def test_sort_descending() -> None:
    assert qs(Query().sort("budgetInMillions", descending=True)) == "sort=budgetInMillions%3Adesc"


def test_pagination_params() -> None:
    assert qs(Query().limit(10)) == "limit=10"
    assert qs(Query().page(2)) == "page=2"
    assert qs(Query().offset(5)) == "offset=5"


def test_filters_then_sort_then_pagination_are_ordered() -> None:
    query = (
        Query()
        .where("budgetInMillions")
        .gt(100)
        .sort("boxOfficeRevenueInMillions", descending=True)
        .limit(5)
    )
    assert qs(query) == "budgetInMillions%3E100&sort=boxOfficeRevenueInMillions%3Adesc&limit=5"


def test_multiple_filters_are_anded_in_order() -> None:
    query = Query().where("academyAwardWins").gt(0).where("name").matches("/the/i")
    assert qs(query) == "academyAwardWins%3E0&name=%2Fthe%2Fi"


def test_builder_methods_return_query_for_chaining() -> None:
    query = Query()
    assert query.where("name").eq("x") is query
    assert query.limit(1) is query
    assert query.sort("name") is query


def test_to_params_exposes_structured_pairs() -> None:
    pairs = Query().where("name").eq("Sam").limit(3).to_params()
    assert pairs == [("name", "Sam"), ("limit", "3")]
    assert Query().where("name").exists().to_params() == [("name", None)]


@pytest.mark.parametrize("bad_limit", [0, -1])
def test_invalid_limit_raises(bad_limit: int) -> None:
    with pytest.raises(ValueError, match="limit"):
        Query().limit(bad_limit)


def test_invalid_page_and_offset_raise() -> None:
    with pytest.raises(ValueError, match="page"):
        Query().page(0)
    with pytest.raises(ValueError, match="offset"):
        Query().offset(-1)
