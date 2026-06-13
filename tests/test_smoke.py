"""Smoke test: the package imports and exposes a version."""

from __future__ import annotations

import lotr_sdk


def test_package_exposes_version() -> None:
    assert isinstance(lotr_sdk.__version__, str)
    assert lotr_sdk.__version__
