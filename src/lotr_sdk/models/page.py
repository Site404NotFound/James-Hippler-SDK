"""The generic paginated response envelope."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Generic, TypeVar, overload

from pydantic import BaseModel, ConfigDict

__all__ = ["Page"]

T = TypeVar("T")


class Page(BaseModel, Sequence[T], Generic[T]):
    """A page of results mirroring the API's list envelope.

    A read-only :class:`~collections.abc.Sequence` of ``docs`` (supports ``len()``,
    indexing, slicing, iteration, ``in``, ``count``, ``index``, and ``reversed``)
    that still exposes the pagination metadata.
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

    @overload
    def __getitem__(self, index: int) -> T: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[T]: ...
    def __getitem__(self, index: int | slice) -> T | Sequence[T]:
        return self.docs[index]

    # Override BaseModel.__iter__ (which yields field tuples) so iterating a
    # Page yields its docs. This also feeds the Sequence mixins (``in``, ``count``)
    # since BaseModel.__iter__ otherwise precedes Sequence's in the MRO.
    def __iter__(self) -> Iterator[T]:  # type: ignore[override]
        return iter(self.docs)
