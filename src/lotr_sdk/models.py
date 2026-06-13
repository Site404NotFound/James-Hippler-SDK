"""Pydantic models for API resources and the paginated response envelope.

Models use field aliases to translate the API's camelCase / ``_id`` keys into
idiomatic snake_case attributes, and ignore unknown fields so that additive API
changes never break deserialization.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["Movie", "Page", "Quote"]


class _Resource(BaseModel):
    """Base for API resource models: immutable, alias-aware, forward-compatible."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="ignore")


class Movie(_Resource):
    """A Lord of the Rings movie."""

    id: str = Field(alias="_id")
    name: str
    runtime_in_minutes: int = Field(alias="runtimeInMinutes")
    budget_in_millions: float = Field(alias="budgetInMillions")
    box_office_revenue_in_millions: float = Field(alias="boxOfficeRevenueInMillions")
    academy_award_nominations: int = Field(alias="academyAwardNominations")
    academy_award_wins: int = Field(alias="academyAwardWins")
    rotten_tomatoes_score: float = Field(alias="rottenTomatoesScore")


class Quote(_Resource):
    """A single line of movie dialog, linked to its movie and character by id."""

    id: str = Field(alias="_id")
    dialog: str
    movie_id: str = Field(alias="movie")
    character_id: str = Field(alias="character")


T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """A page of results mirroring the API's list envelope.

    Behaves like a read-only sequence of ``docs`` (supports ``len()``, indexing,
    and iteration) while still exposing the pagination metadata.
    """

    model_config = ConfigDict(frozen=True)

    docs: list[T]
    total: int
    limit: int
    offset: int = 0
    page: int = 1
    pages: int = 1

    @property
    def has_next_page(self) -> bool:
        """Whether another page of results follows this one."""
        return self.page < self.pages

    def __len__(self) -> int:
        return len(self.docs)

    def __getitem__(self, index: int) -> T:
        return self.docs[index]

    # Override BaseModel.__iter__ (which yields field tuples) so iterating a
    # Page yields its docs, matching its sequence-like contract.
    def __iter__(self) -> Iterator[T]:  # type: ignore[override]
        return iter(self.docs)
