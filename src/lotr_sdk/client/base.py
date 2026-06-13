"""Shared helpers for the client facades."""

from __future__ import annotations

from typing import Any

__all__ = ["build_overrides"]


def build_overrides(
    base_url: str | None,
    timeout: float | None,
    max_retries: int | None,
    backoff_factor: float | None,
) -> dict[str, Any]:
    """Collect only the options the caller actually set, so config defaults win."""
    candidates = {
        "base_url": base_url,
        "timeout": timeout,
        "max_retries": max_retries,
        "backoff_factor": backoff_factor,
    }
    return {key: value for key, value in candidates.items() if value is not None}
