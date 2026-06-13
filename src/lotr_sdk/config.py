"""Immutable client configuration and environment resolution."""

from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from .exceptions import ConfigurationError

__all__ = ["ENV_API_KEY", "ClientConfig"]

ENV_API_KEY = "THE_ONE_API_KEY"
DEFAULT_BASE_URL = "https://the-one-api.dev/v2"


class ClientConfig(BaseModel):
    """Validated, immutable settings shared by the sync and async clients.

    Prefer :meth:`resolve`, which also pulls the API key from the
    ``THE_ONE_API_KEY`` environment variable when one isn't passed explicitly.
    """

    model_config = ConfigDict(frozen=True)

    api_key: str = Field(min_length=1, repr=False)
    base_url: str = DEFAULT_BASE_URL
    timeout: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=3, ge=0)
    backoff_factor: float = Field(default=0.5, ge=0)

    @field_validator("base_url")
    @classmethod
    def _strip_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")

    @classmethod
    def resolve(cls, api_key: str | None = None, **overrides: Any) -> ClientConfig:
        """Build a config, sourcing the API key from the environment if needed.

        Raises:
            ConfigurationError: if no key can be found or any value is invalid.
        """
        key = api_key if api_key is not None else os.environ.get(ENV_API_KEY)
        if not key:
            raise ConfigurationError(
                "No API key provided. Pass api_key=... or set the "
                f"{ENV_API_KEY} environment variable. Get a key at "
                "https://the-one-api.dev/sign-up."
            )
        try:
            return cls(api_key=key, **overrides)
        except ValidationError as exc:
            raise ConfigurationError(f"Invalid client configuration: {exc}") from exc
