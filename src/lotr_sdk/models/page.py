"""The generic paginated response envelope."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

__all__ = ["Page"]

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """A page of results mirroring the API's list envelope.

    Behaves like a read-only sequence of ``docs`` (supports ``len()``, indexing,
    and iteration) while still exposing the pagination metadata.
    """

    model_config = ConfigDict(frozen=True)

    docs: list[T]
    total: int
    limit: int
    offset: int = 0
    page: int = 1
    pages: int = 1

    @property
    def has_next_page(self) -> bool:
        """Whether another page of results follows this one."""
        return self.page < self.pages

    def __len__(self) -> int:
        return len(self.docs)

    def __getitem__(self, index: int) -> T:
        return self.docs[index]

    # Override BaseModel.__iter__ (which yields field tuples) so iterating a
    # Page yields its docs, matching its sequence-like contract.
    def __iter__(self) -> Iterator[T]:  # type: ignore[override]
        return iter(self.docs)
