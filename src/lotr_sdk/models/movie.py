"""The Movie resource model."""

from __future__ import annotations

from pydantic import Field

from lotr_sdk.models.base import ResourceModel

__all__ = ["Movie"]


class Movie(ResourceModel):
    """A Lord of the Rings movie."""

    id: str = Field(alias="_id")
    name: str
    runtime_in_minutes: int = Field(alias="runtimeInMinutes")
    budget_in_millions: float = Field(alias="budgetInMillions")
    box_office_revenue_in_millions: float = Field(alias="boxOfficeRevenueInMillions")
    academy_award_nominations: int = Field(alias="academyAwardNominations")
    academy_award_wins: int = Field(alias="academyAwardWins")
    rotten_tomatoes_score: float = Field(alias="rottenTomatoesScore")
