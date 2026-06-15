"""Pydantic models for API resources and the paginated response envelope.

Models use field aliases to translate the API's camelCase / ``_id`` keys into
idiomatic snake_case attributes, and ignore unknown fields so that additive API
changes never break deserialization.
"""

from __future__ import annotations

from lotr_sdk.models.movie import Movie
from lotr_sdk.models.movie_with_quotes import MovieWithQuotes
from lotr_sdk.models.page import Page
from lotr_sdk.models.quote import Quote

__all__ = ["Movie", "MovieWithQuotes", "Page", "Quote"]
