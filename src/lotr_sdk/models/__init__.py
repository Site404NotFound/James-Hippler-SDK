"""Pydantic models for API resources and the paginated response envelope.

Models use field aliases to translate the API's camelCase / ``_id`` keys into
idiomatic snake_case attributes, and ignore unknown fields so that additive API
changes never break deserialization.
"""

from __future__ import annotations

from .movie import Movie
from .page import Page
from .quote import Quote

__all__ = ["Movie", "Page", "Quote"]
