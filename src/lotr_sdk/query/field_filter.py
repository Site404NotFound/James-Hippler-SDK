"""The :class:`FieldFilter` operator proxy returned by :meth:`Query.where`."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any

from lotr_sdk.query.flags import RegexFlag
from lotr_sdk.query.serialization import format_value

if TYPE_CHECKING:  # pragma: no cover
    from lotr_sdk.query.builder import Query

__all__ = ["FieldFilter"]

# Operator tokens the API recognizes once the query string is URL-decoded.
_NEGATE = "!"
_GREATER_THAN = ">"
_LESS_THAN = "<"
_LIST_SEPARATOR = ","
_REGEX_DELIMITER = "/"


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
        return self._append(self._field, format_value(value))

    def ne(self, value: Any) -> Query:
        """Match ``field != value``."""
        return self._append(f"{self._field}{_NEGATE}", format_value(value))

    def in_(self, values: Iterable[Any]) -> Query:
        """Match any of ``values`` (``field=a,b,c``)."""
        return self._append(self._field, _LIST_SEPARATOR.join(format_value(v) for v in values))

    def not_in(self, values: Iterable[Any]) -> Query:
        """Match none of ``values`` (``field!=a,b,c``)."""
        joined = _LIST_SEPARATOR.join(format_value(v) for v in values)
        return self._append(f"{self._field}{_NEGATE}", joined)

    def exists(self) -> Query:
        """Match documents where the field is present."""
        return self._append(self._field, None)

    def not_exists(self) -> Query:
        """Match documents where the field is absent."""
        return self._append(f"{_NEGATE}{self._field}", None)

    def matches(self, pattern: str, *, flags: Iterable[RegexFlag] = ()) -> Query:
        """Match a regular expression.

        Pass the bare ``pattern`` (no delimiters); the SDK wraps it in the API's
        ``/pattern/flags`` form. ``flags`` are :class:`RegexFlag` members, e.g.
        ``matches("ring", flags=[RegexFlag.IGNORE_CASE])``.
        """
        suffix = "".join(flags)
        return self._append(self._field, f"{_REGEX_DELIMITER}{pattern}{_REGEX_DELIMITER}{suffix}")

    def gt(self, value: Any) -> Query:
        """Match ``field > value``."""
        return self._append(f"{self._field}{_GREATER_THAN}{format_value(value)}", None)

    def lt(self, value: Any) -> Query:
        """Match ``field < value``."""
        return self._append(f"{self._field}{_LESS_THAN}{format_value(value)}", None)

    def gte(self, value: Any) -> Query:
        """Match ``field >= value``."""
        return self._append(f"{self._field}{_GREATER_THAN}", format_value(value))

    def lte(self, value: Any) -> Query:
        """Match ``field <= value``."""
        return self._append(f"{self._field}{_LESS_THAN}", format_value(value))
