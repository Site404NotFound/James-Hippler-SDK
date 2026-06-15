"""A fluent, chainable builder for filtering, sorting, and pagination.

Example:
    >>> Query().where("budgetInMillions").gt(100).sort("name").limit(10)

The builder accumulates filters and serializes them to the exact query string
The One API expects. The server URL-decodes before parsing operators, so
operator characters are percent-encoded while the ``=`` key/value separator and
``&`` joins are kept literal. ``>``/``<`` produce valueless tokens
(``field>value``); ``>=``/``<=``/``=``/``!=`` keep a literal ``=`` separator.
"""

from __future__ import annotations

import copy
from collections.abc import Callable, Iterable
from typing import Any
from urllib.parse import quote

__all__ = ["FieldFilter", "Query"]

# A param is a key plus an optional value. ``None`` means a valueless token
# (e.g. existence checks and strict comparisons), serialized without ``=``.
Param = tuple[str, "str | None"]

# API query-parameter keys for sorting and pagination.
_SORT = "sort"
_LIMIT = "limit"
_PAGE = "page"
_OFFSET = "offset"


def _format(value: Any) -> str:
    """Render a filter value the way the API expects (lowercase booleans)."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


class FieldFilter:
    """Operator methods for a single field, returned by :meth:`Query.where`.

    Each operator appends a filter to its parent :class:`Query` and returns that
    query, so calls keep chaining fluently. The append step is supplied as a
    callback by :meth:`Query.where`, so this proxy stays decoupled from the
    query's internals.
    """

    def __init__(self, append: Callable[[str, str | None], Query], field: str) -> None:
        self._append = append
        self._field = field

    def eq(self, value: Any) -> Query:
        """Match ``field == value``."""
        return self._append(self._field, _format(value))

    def ne(self, value: Any) -> Query:
        """Match ``field != value``."""
        return self._append(f"{self._field}!", _format(value))

    def in_(self, values: Iterable[Any]) -> Query:
        """Match any of ``values`` (``field=a,b,c``)."""
        return self._append(self._field, ",".join(_format(v) for v in values))

    def not_in(self, values: Iterable[Any]) -> Query:
        """Match none of ``values`` (``field!=a,b,c``)."""
        return self._append(f"{self._field}!", ",".join(_format(v) for v in values))

    def exists(self) -> Query:
        """Match documents where the field is present."""
        return self._append(self._field, None)

    def not_exists(self) -> Query:
        """Match documents where the field is absent."""
        return self._append(f"!{self._field}", None)

    def matches(self, pattern: str) -> Query:
        """Match a regular expression literal, e.g. ``/ring/i``."""
        return self._append(self._field, pattern)

    def gt(self, value: Any) -> Query:
        """Match ``field > value``."""
        return self._append(f"{self._field}>{_format(value)}", None)

    def lt(self, value: Any) -> Query:
        """Match ``field < value``."""
        return self._append(f"{self._field}<{_format(value)}", None)

    def gte(self, value: Any) -> Query:
        """Match ``field >= value``."""
        return self._append(f"{self._field}>", _format(value))

    def lte(self, value: Any) -> Query:
        """Match ``field <= value``."""
        return self._append(f"{self._field}<", _format(value))


class Query:
    """A composable filter/sort/pagination specification for list endpoints."""

    def __init__(self) -> None:
        self._filters: list[Param] = []
        self._sort: str | None = None
        self._pagination: list[Param] = []

    def where(self, field: str) -> FieldFilter:
        """Begin a filter on ``field``; chain an operator (e.g. ``.eq(...)``)."""
        return FieldFilter(self._add, field)

    def sort(self, field: str, *, descending: bool = False) -> Query:
        """Sort by ``field`` ascending (default) or descending."""
        self._sort = f"{field}:{'desc' if descending else 'asc'}"
        return self

    def limit(self, count: int) -> Query:
        """Cap the number of results per page (must be >= 1)."""
        if count < 1:
            raise ValueError(f"{_LIMIT} must be >= 1, got {count}")
        return self._set_pagination(_LIMIT, count)

    def page(self, number: int) -> Query:
        """Select the 1-based page number (must be >= 1)."""
        if number < 1:
            raise ValueError(f"{_PAGE} must be >= 1, got {number}")
        return self._set_pagination(_PAGE, number)

    def offset(self, count: int) -> Query:
        """Skip ``count`` results (must be >= 0)."""
        if count < 0:
            raise ValueError(f"{_OFFSET} must be >= 0, got {count}")
        return self._set_pagination(_OFFSET, count)

    def copy(self) -> Query:
        """Return an independent copy that can be modified without affecting this one."""
        return copy.deepcopy(self)

    def to_params(self) -> list[Param]:
        """Return the ordered (key, value) pairs: filters, then sort, then paging."""
        params: list[Param] = list(self._filters)
        if self._sort is not None:
            params.append((_SORT, self._sort))
        params.extend(self._pagination)
        return params

    def to_query_string(self) -> str:
        """Serialize to a percent-encoded query string (without a leading ``?``)."""
        return "&".join(_encode(key, value) for key, value in self.to_params())

    def _add(self, key: str, value: str | None) -> Query:
        self._filters.append((key, value))
        return self

    def _set_pagination(self, key: str, value: int) -> Query:
        self._pagination = [(k, v) for k, v in self._pagination if k != key]
        self._pagination.append((key, str(value)))
        return self


def _encode(key: str, value: str | None) -> str:
    """Encode one param, keeping the ``=`` separator literal for keyed values."""
    if value is None:
        return quote(key, safe="")
    return f"{quote(key, safe='')}={quote(value, safe='')}"
