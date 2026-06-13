"""Shared base for API resource models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

__all__ = ["ResourceModel"]


class ResourceModel(BaseModel):
    """Base for API resource models: immutable, alias-aware, forward-compatible.

    ``populate_by_name`` lets models be built from either the API alias or the
    snake_case attribute name; ``extra="ignore"`` keeps deserialization working
    when the API adds new fields.
    """

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="ignore")
