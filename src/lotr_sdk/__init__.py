"""A clean, fully typed Python SDK for The One API (https://the-one-api.dev).

Typical use::

    from lotr_sdk import Client, Query

    with Client(api_key="...") as client:  # or set THE_ONE_API_KEY
        movies = client.movies.list(Query().where("budgetInMillions").gt(100))
"""

from __future__ import annotations

import logging

from lotr_sdk.client import AsyncClient, Client
from lotr_sdk.config import ClientConfig
from lotr_sdk.exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    ForbiddenError,
    LotrError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TransportError,
)
from lotr_sdk.fields import MovieField, QuoteField
from lotr_sdk.models import Movie, Page, Quote
from lotr_sdk.query import FieldFilter, Query
from lotr_sdk.version import __version__

__all__ = [
    "APIError",
    "AsyncClient",
    "AuthenticationError",
    "Client",
    "ClientConfig",
    "ConfigurationError",
    "FieldFilter",
    "ForbiddenError",
    "LotrError",
    "Movie",
    "MovieField",
    "NotFoundError",
    "Page",
    "Query",
    "Quote",
    "QuoteField",
    "RateLimitError",
    "ServerError",
    "TransportError",
    "__version__",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())
