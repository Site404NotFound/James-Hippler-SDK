"""Wire serialization for query params.

The One API URL-decodes the query string before parsing operators, so operator
characters are percent-encoded while the ``=`` key/value separator and ``&``
joins stay literal. ``>``/``<`` produce valueless tokens (``field>value``);
``>=``/``<=``/``=``/``!=`` keep a literal ``=`` separator.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

__all__ = ["Param", "encode_param", "format_value"]

# A param is a key plus an optional value. ``None`` means a valueless token
# (e.g. existence checks and strict comparisons), serialized without ``=``.
Param = tuple[str, "str | None"]


def format_value(value: Any) -> str:
    """Render a filter value the way the API expects (lowercase booleans)."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def encode_param(key: str, value: str | None) -> str:
    """Encode one param, keeping the ``=`` separator literal for keyed values."""
    if value is None:
        return quote(key, safe="")
    return f"{quote(key, safe='')}={quote(value, safe='')}"
