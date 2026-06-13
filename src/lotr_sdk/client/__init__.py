"""Client facades, split by execution model."""

from __future__ import annotations

from .async_ import AsyncClient
from .sync import Client

__all__ = ["AsyncClient", "Client"]
