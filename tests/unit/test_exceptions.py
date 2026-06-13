"""Tests for the SDK exception hierarchy and status -> exception mapping."""

from __future__ import annotations

import pytest

from lotr_sdk.exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    ForbiddenError,
    LotrError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TransportError,
    api_error_from_status,
)


def test_all_errors_share_a_common_base() -> None:
    for exc in (
        ConfigurationError,
        TransportError,
        APIError,
        AuthenticationError,
        ForbiddenError,
        NotFoundError,
        RateLimitError,
        ServerError,
    ):
        assert issubclass(exc, LotrError)


def test_http_errors_share_the_api_error_base() -> None:
    for exc in (AuthenticationError, ForbiddenError, NotFoundError, RateLimitError, ServerError):
        assert issubclass(exc, APIError)


def test_api_error_carries_status_and_message() -> None:
    err = APIError(404, "not found")
    assert err.status_code == 404
    assert err.message == "not found"
    assert "404" in str(err)
    assert "not found" in str(err)


def test_rate_limit_error_carries_retry_after() -> None:
    err = RateLimitError(429, "slow down", retry_after=12.0)
    assert err.retry_after == 12.0


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (401, AuthenticationError),
        (403, ForbiddenError),
        (404, NotFoundError),
        (429, RateLimitError),
        (500, ServerError),
        (503, ServerError),
        (418, APIError),  # unmapped 4xx falls back to the generic APIError
    ],
)
def test_api_error_from_status_maps_to_the_right_subclass(
    status: int, expected: type[APIError]
) -> None:
    err = api_error_from_status(status, "boom")
    assert type(err) is expected
    assert err.status_code == status


def test_api_error_from_status_propagates_retry_after_for_429() -> None:
    err = api_error_from_status(429, "boom", retry_after=5.0)
    assert isinstance(err, RateLimitError)
    assert err.retry_after == 5.0
