"""Tests for the HTTP transport: auth, query passthrough, errors, and retries."""

from __future__ import annotations

import logging
from typing import Any

import httpx
import pytest
import respx

from lotr_sdk._transport import AsyncTransport, SyncTransport
from lotr_sdk.config import ClientConfig
from lotr_sdk.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TransportError,
)

BASE_URL = "https://the-one-api.dev/v2"


def make_sync(**overrides: Any) -> SyncTransport:
    config = ClientConfig.resolve(
        api_key="test-key", base_url=BASE_URL, backoff_factor=0, **overrides
    )
    return SyncTransport(config)


def make_async(**overrides: Any) -> AsyncTransport:
    config = ClientConfig.resolve(
        api_key="test-key", base_url=BASE_URL, backoff_factor=0, **overrides
    )
    return AsyncTransport(config)


@respx.mock
def test_request_sends_bearer_auth_and_returns_json() -> None:
    route = respx.get(f"{BASE_URL}/movie").mock(return_value=httpx.Response(200, json={"ok": True}))
    with make_sync() as transport:
        assert transport.request("GET", "movie") == {"ok": True}
    assert route.calls.last.request.headers["Authorization"] == "Bearer test-key"


@respx.mock
def test_query_string_is_passed_through_verbatim() -> None:
    route = respx.get(url__startswith=f"{BASE_URL}/movie").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    with make_sync() as transport:
        transport.request("GET", "movie", "budgetInMillions%3E100&limit=5")
    assert route.calls.last.request.url.query == b"budgetInMillions%3E100&limit=5"


@respx.mock
@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (401, AuthenticationError),
        (404, NotFoundError),
        (429, RateLimitError),
        (500, ServerError),
    ],
)
def test_error_statuses_map_to_exceptions(status: int, expected: type[APIError]) -> None:
    respx.get(f"{BASE_URL}/movie").mock(
        return_value=httpx.Response(status, json={"success": False, "message": "boom"})
    )
    with make_sync(max_retries=0) as transport, pytest.raises(expected) as exc_info:
        transport.request("GET", "movie")
    assert exc_info.value.status_code == status
    assert exc_info.value.message == "boom"


@respx.mock
def test_rate_limit_error_reads_retry_after_header() -> None:
    respx.get(f"{BASE_URL}/movie").mock(
        return_value=httpx.Response(429, headers={"Retry-After": "7"}, json={"message": "slow"})
    )
    with make_sync(max_retries=0) as transport, pytest.raises(RateLimitError) as exc_info:
        transport.request("GET", "movie")
    assert exc_info.value.retry_after == 7.0


@respx.mock
def test_non_object_json_is_an_api_error() -> None:
    respx.get(f"{BASE_URL}/movie").mock(return_value=httpx.Response(200, json=[1, 2, 3]))
    with make_sync() as transport, pytest.raises(APIError):
        transport.request("GET", "movie")


@respx.mock
def test_retries_then_succeeds() -> None:
    route = respx.get(f"{BASE_URL}/movie").mock(
        side_effect=[
            httpx.Response(500, json={"message": "x"}),
            httpx.Response(503, json={"message": "x"}),
            httpx.Response(200, json={"ok": True}),
        ]
    )
    with make_sync(max_retries=3) as transport:
        assert transport.request("GET", "movie") == {"ok": True}
    assert route.call_count == 3


@respx.mock
def test_retries_are_exhausted_and_raise() -> None:
    route = respx.get(f"{BASE_URL}/movie").mock(
        return_value=httpx.Response(500, json={"message": "x"})
    )
    with make_sync(max_retries=2) as transport, pytest.raises(ServerError):
        transport.request("GET", "movie")
    assert route.call_count == 3  # initial try + 2 retries


@respx.mock
def test_network_failure_becomes_transport_error() -> None:
    respx.get(f"{BASE_URL}/movie").mock(side_effect=httpx.ConnectError("no route"))
    with make_sync(max_retries=0) as transport, pytest.raises(TransportError):
        transport.request("GET", "movie")


@respx.mock
def test_network_failure_retries_then_succeeds() -> None:
    route = respx.get(f"{BASE_URL}/movie").mock(
        side_effect=[httpx.ConnectError("flaky"), httpx.Response(200, json={"ok": True})]
    )
    with make_sync(max_retries=2) as transport:
        assert transport.request("GET", "movie") == {"ok": True}
    assert route.call_count == 2


@respx.mock
def test_error_message_falls_back_to_body_text_when_unstructured() -> None:
    respx.get(f"{BASE_URL}/movie").mock(return_value=httpx.Response(500, text="upstream exploded"))
    with make_sync(max_retries=0) as transport, pytest.raises(ServerError) as exc_info:
        transport.request("GET", "movie")
    assert exc_info.value.message == "upstream exploded"


@respx.mock
def test_non_numeric_retry_after_is_ignored() -> None:
    respx.get(f"{BASE_URL}/movie").mock(
        return_value=httpx.Response(429, headers={"Retry-After": "later"}, json={"message": "no"})
    )
    with make_sync(max_retries=0) as transport, pytest.raises(RateLimitError) as exc_info:
        transport.request("GET", "movie")
    assert exc_info.value.retry_after is None


@respx.mock
def test_error_body_without_message_falls_back_to_text() -> None:
    respx.get(f"{BASE_URL}/movie").mock(
        return_value=httpx.Response(503, json={"success": False, "code": 9})
    )
    with make_sync(max_retries=0) as transport, pytest.raises(ServerError) as exc_info:
        transport.request("GET", "movie")
    assert exc_info.value.message  # non-empty fallback


@respx.mock
async def test_async_transport_returns_json() -> None:
    respx.get(f"{BASE_URL}/movie").mock(return_value=httpx.Response(200, json={"ok": True}))
    async with make_async() as transport:
        assert await transport.request("GET", "movie") == {"ok": True}


@respx.mock
async def test_async_transport_retries_then_succeeds() -> None:
    route = respx.get(f"{BASE_URL}/movie").mock(
        side_effect=[httpx.Response(500, json={"m": 1}), httpx.Response(200, json={"ok": True})]
    )
    async with make_async(max_retries=3) as transport:
        assert await transport.request("GET", "movie") == {"ok": True}
    assert route.call_count == 2


@respx.mock
async def test_async_network_failure_becomes_transport_error() -> None:
    respx.get(f"{BASE_URL}/movie").mock(side_effect=httpx.ConnectError("down"))
    async with make_async(max_retries=1) as transport:
        with pytest.raises(TransportError):
            await transport.request("GET", "movie")


@respx.mock
async def test_async_server_error_maps_to_exception() -> None:
    respx.get(f"{BASE_URL}/movie").mock(
        return_value=httpx.Response(500, json={"success": False, "message": "boom"})
    )
    async with make_async(max_retries=0) as transport:
        with pytest.raises(ServerError):
            await transport.request("GET", "movie")


@respx.mock
def test_log_success_emits_request_debug(caplog: pytest.LogCaptureFixture) -> None:
    respx.get(f"{BASE_URL}/movie").mock(return_value=httpx.Response(200, json={"ok": True}))
    caplog.set_level(logging.DEBUG, logger="lotr_sdk")
    with make_sync() as transport:
        transport.request("GET", "movie")
    records = [r for r in caplog.records if r.getMessage() == "request"]
    assert len(records) == 1
    assert records[0].levelname == "DEBUG"
    assert records[0].method == "GET"
    assert records[0].path == "movie"
    assert records[0].status == 200
    assert isinstance(records[0].elapsed_ms, float)


@respx.mock
def test_log_status_retry_then_success(caplog: pytest.LogCaptureFixture) -> None:
    respx.get(f"{BASE_URL}/movie").mock(
        side_effect=[httpx.Response(503, json={"m": 1}), httpx.Response(200, json={"ok": True})]
    )
    caplog.set_level(logging.DEBUG, logger="lotr_sdk")
    with make_sync(max_retries=2) as transport:
        transport.request("GET", "movie")
    retries = [r for r in caplog.records if r.getMessage() == "retry"]
    assert len(retries) == 1
    assert retries[0].levelname == "WARNING"
    assert retries[0].attempt == 1
    assert retries[0].status == 503
    assert retries[0].delay_s == 0.0
    assert any(r.getMessage() == "request" for r in caplog.records)


@respx.mock
def test_log_network_retry_then_success(caplog: pytest.LogCaptureFixture) -> None:
    respx.get(f"{BASE_URL}/movie").mock(
        side_effect=[httpx.ConnectError("flaky"), httpx.Response(200, json={"ok": True})]
    )
    caplog.set_level(logging.DEBUG, logger="lotr_sdk")
    with make_sync(max_retries=2) as transport:
        transport.request("GET", "movie")
    retries = [r for r in caplog.records if r.getMessage() == "retry"]
    assert len(retries) == 1
    assert retries[0].attempt == 1
    assert retries[0].status is None


@respx.mock
def test_log_retryable_exhausted_emits_failure(caplog: pytest.LogCaptureFixture) -> None:
    respx.get(f"{BASE_URL}/movie").mock(return_value=httpx.Response(500, json={"m": 1}))
    caplog.set_level(logging.DEBUG, logger="lotr_sdk")
    with make_sync(max_retries=2) as transport, pytest.raises(ServerError):
        transport.request("GET", "movie")
    failures = [r for r in caplog.records if r.getMessage() == "request_failed"]
    assert len(failures) == 1
    assert failures[0].levelname == "ERROR"
    assert failures[0].attempts == 3
    assert failures[0].reason == "ServerError"


@respx.mock
def test_log_non_retryable_4xx_has_no_failure(caplog: pytest.LogCaptureFixture) -> None:
    respx.get(f"{BASE_URL}/movie").mock(return_value=httpx.Response(404, json={"message": "no"}))
    caplog.set_level(logging.DEBUG, logger="lotr_sdk")
    with make_sync(max_retries=2) as transport, pytest.raises(NotFoundError):
        transport.request("GET", "movie")
    assert not [r for r in caplog.records if r.getMessage() == "request_failed"]
    assert not [r for r in caplog.records if r.getMessage() == "request"]


@respx.mock
def test_log_network_exhausted_emits_failure(caplog: pytest.LogCaptureFixture) -> None:
    respx.get(f"{BASE_URL}/movie").mock(side_effect=httpx.ConnectError("down"))
    caplog.set_level(logging.DEBUG, logger="lotr_sdk")
    with make_sync(max_retries=0) as transport, pytest.raises(TransportError):
        transport.request("GET", "movie")
    failures = [r for r in caplog.records if r.getMessage() == "request_failed"]
    assert len(failures) == 1
    assert failures[0].reason == "TransportError"
    assert failures[0].attempts == 1


@respx.mock
async def test_async_log_success_emits_request_debug(caplog: pytest.LogCaptureFixture) -> None:
    respx.get(f"{BASE_URL}/movie").mock(return_value=httpx.Response(200, json={"ok": True}))
    caplog.set_level(logging.DEBUG, logger="lotr_sdk")
    async with make_async() as transport:
        await transport.request("GET", "movie")
    records = [r for r in caplog.records if r.getMessage() == "request"]
    assert len(records) == 1
    assert records[0].status == 200
    assert isinstance(records[0].elapsed_ms, float)


@respx.mock
async def test_async_log_status_retry_then_success(caplog: pytest.LogCaptureFixture) -> None:
    respx.get(f"{BASE_URL}/movie").mock(
        side_effect=[httpx.Response(500, json={"m": 1}), httpx.Response(200, json={"ok": True})]
    )
    caplog.set_level(logging.DEBUG, logger="lotr_sdk")
    async with make_async(max_retries=2) as transport:
        await transport.request("GET", "movie")
    retries = [r for r in caplog.records if r.getMessage() == "retry"]
    assert len(retries) == 1
    assert retries[0].status == 500


@respx.mock
async def test_async_log_network_retry_then_success(caplog: pytest.LogCaptureFixture) -> None:
    respx.get(f"{BASE_URL}/movie").mock(
        side_effect=[httpx.ConnectError("flaky"), httpx.Response(200, json={"ok": True})]
    )
    caplog.set_level(logging.DEBUG, logger="lotr_sdk")
    async with make_async(max_retries=2) as transport:
        await transport.request("GET", "movie")
    retries = [r for r in caplog.records if r.getMessage() == "retry"]
    assert len(retries) == 1
    assert retries[0].status is None


@respx.mock
async def test_async_log_network_exhausted_emits_failure(
    caplog: pytest.LogCaptureFixture,
) -> None:
    respx.get(f"{BASE_URL}/movie").mock(side_effect=httpx.ConnectError("down"))
    caplog.set_level(logging.DEBUG, logger="lotr_sdk")
    async with make_async(max_retries=0) as transport:
        with pytest.raises(TransportError):
            await transport.request("GET", "movie")
    failures = [r for r in caplog.records if r.getMessage() == "request_failed"]
    assert len(failures) == 1
    assert failures[0].reason == "TransportError"
