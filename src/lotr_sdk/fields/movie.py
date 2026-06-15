"""Enum of the known ``movie`` query fields."""

from __future__ import annotations

from enum import StrEnum

__all__ = ["MovieField"]


class MovieField(StrEnum):
    """Known fields of the ``/movie`` endpoint.

    Pass a member to :meth:`~lotr_sdk.Query.where` for autocomplete and typo-safe
    field names; each member's value is the wire field name, so raw strings remain
    interchangeable.
    """

    ID = "_id"
    NAME = "name"
    RUNTIME_IN_MINUTES = "runtimeInMinutes"
    BUDGET_IN_MILLIONS = "budgetInMillions"
    BOX_OFFICE_REVENUE_IN_MILLIONS = "boxOfficeRevenueInMillions"
    ACADEMY_AWARD_NOMINATIONS = "academyAwardNominations"
    ACADEMY_AWARD_WINS = "academyAwardWins"
    ROTTEN_TOMATOES_SCORE = "rottenTomatoesScore"
