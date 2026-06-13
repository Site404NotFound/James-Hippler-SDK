"""A clean, fully typed Python SDK for The One API (https://the-one-api.dev).

Typical use::

    from lotr_sdk import Client, Query

    with Client(api_key="...") as client:  # or set THE_ONE_API_KEY
        movies = client.movies.list(Query().where("budgetInMillions").gt(100))
"""

from __future__ import annotations

from ._version import __version__
from .client import AsyncClient, Client
from .config import ClientConfig
from .exceptions import (
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
from .models import Movie, Page, Quote
from .query import FieldFilter, Query

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
    "NotFoundError",
    "Page",
    "Query",
    "Quote",
    "RateLimitError",
    "ServerError",
    "TransportError",
    "__version__",
]
