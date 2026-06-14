"""The Quote resource model."""

from __future__ import annotations

from pydantic import Field

from lotr_sdk.models.base import ResourceModel

__all__ = ["Quote"]


class Quote(ResourceModel):
    """A single line of movie dialog, linked to its movie and character by id."""

    id: str = Field(alias="_id")
    dialog: str
    movie_id: str = Field(alias="movie")
    character_id: str = Field(alias="character")
