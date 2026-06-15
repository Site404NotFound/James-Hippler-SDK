"""Enum of the known ``quote`` query fields."""

from __future__ import annotations

from enum import StrEnum

__all__ = ["QuoteField"]


class QuoteField(StrEnum):
    """Known fields of the ``/quote`` endpoint.

    Pass a member to :meth:`~lotr_sdk.Query.where` for autocomplete and typo-safe
    field names; each member's value is the wire field name, so raw strings remain
    interchangeable. ``MOVIE`` and ``CHARACTER`` are id references.
    """

    ID = "_id"
    DIALOG = "dialog"
    MOVIE = "movie"
    CHARACTER = "character"
