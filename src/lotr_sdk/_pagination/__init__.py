"""Lazy auto-pagination helpers (sync + async)."""

from __future__ import annotations

from lotr_sdk._pagination.async_ import paginate_async
from lotr_sdk._pagination.sync import paginate_sync

__all__ = ["paginate_async", "paginate_sync"]
