"""Lazy auto-pagination helpers (sync + async)."""

from __future__ import annotations

from .async_ import paginate_async
from .sync import paginate_sync

__all__ = ["paginate_async", "paginate_sync"]
