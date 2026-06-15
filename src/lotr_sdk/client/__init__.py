"""Client facades, split by execution model."""

from __future__ import annotations

from lotr_sdk.client.aio import AsyncClient
from lotr_sdk.client.sync import Client

__all__ = ["AsyncClient", "Client"]
