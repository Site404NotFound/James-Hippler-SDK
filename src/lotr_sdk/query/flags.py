"""Regex flags for :meth:`FieldFilter.matches`, as a typo-safe enum."""

from __future__ import annotations

from enum import StrEnum

__all__ = ["RegexFlag"]


class RegexFlag(StrEnum):
    """Modifiers for a :meth:`~lotr_sdk.Query.where` regex ``matches`` filter.

    Each member's value is the letter the API expects in the ``/pattern/flags``
    trailer, so members are interchangeable with the raw letters (just like the
    field enums). Pass one or more::

        Query().where("name").matches("ring", flags=[RegexFlag.IGNORE_CASE])
    """

    IGNORE_CASE = "i"
    MULTILINE = "m"
    DOTALL = "s"
    EXTENDED = "x"
