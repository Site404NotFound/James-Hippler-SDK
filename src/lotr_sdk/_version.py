"""Single source of the package version, read from installed metadata."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("lotr-sdk")
except PackageNotFoundError:  # pragma: no cover - only hit when running from a non-installed tree
    __version__ = "0.0.0"

__all__ = ["__version__"]
