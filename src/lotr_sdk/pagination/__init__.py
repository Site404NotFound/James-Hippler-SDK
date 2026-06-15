"""Lazy auto-pagination helpers (sync + async)."""

from __future__ import annotations

from lotr_sdk.pagination.aio import paginate_async
from lotr_sdk.pagination.sync import paginate_sync

__all__ = ["paginate_async", "paginate_sync"]
