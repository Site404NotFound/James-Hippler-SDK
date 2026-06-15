"""The fluent :class:`Query` builder for filtering, sorting, and pagination.

Example:
    >>> Query().where("budgetInMillions").gt(100).sort("name").limit(10)
"""

from __future__ import annotations

import copy

from lotr_sdk.query.field_filter import FieldFilter
from lotr_sdk.query.serialization import Param, encode_param

__all__ = ["Query"]

# API query-parameter keys for sorting and pagination.
_SORT = "sort"
_LIMIT = "limit"
_PAGE = "page"
_OFFSET = "offset"

# Sort direction tokens and the ``field:direction`` separator.
_SORT_DELIMITER = ":"
_ASC = "asc"
_DESC = "desc"


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
        self._sort = f"{field}{_SORT_DELIMITER}{_DESC if descending else _ASC}"
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
        return "&".join(encode_param(key, value) for key, value in self.to_params())

    def _add(self, key: str, value: str | None) -> Query:
        self._filters.append((key, value))
        return self

    def _set_pagination(self, key: str, value: int) -> Query:
        self._pagination = [(k, v) for k, v in self._pagination if k != key]
        self._pagination.append((key, str(value)))
        return self
