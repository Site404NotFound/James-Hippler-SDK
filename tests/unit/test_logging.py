"""Tests for package-level logging configuration."""

from __future__ import annotations

import logging

import lotr_sdk


def test_package_logger_has_null_handler() -> None:
    logger = logging.getLogger(lotr_sdk.__name__)
    assert any(isinstance(handler, logging.NullHandler) for handler in logger.handlers)
