"""Execution-agnostic transport behavior shared by the sync and async variants.

``BaseTransport`` owns request building, auth, response handling, error mapping,
and the retry *policy*. The concrete transports add only how a request is sent
and how the retry loop sleeps.
"""

from __future__ import annotations

from typing import Any

import httpx

from .._version import __version__
from ..config import ClientConfig
from ..exceptions import APIError, api_error_from_status

__all__ = ["BaseTransport"]


class BaseTransport:
    """Shared request building, response handling, and retry policy."""

    def __init__(self, config: ClientConfig) -> None:
        self._config = config

    def _build_request(self, method: str, path: str, query_string: str) -> httpx.Request:
        url = httpx.URL(f"{self._config.base_url}/{path}")
        if query_string:
            # Use the pre-encoded query verbatim; httpx would otherwise re-encode
            # the operator characters the API expects.
            url = url.copy_with(query=query_string.encode("ascii"))
        headers = {
            "Authorization": f"Bearer {self._config.api_key.get_secret_value()}",
            "Accept": "application/json",
            "User-Agent": f"lotr-sdk/{__version__}",
        }
        return httpx.Request(method, url, headers=headers)

    def _should_retry(self, status_code: int) -> bool:
        return status_code == 429 or status_code >= 500

    def _backoff(self, attempt: int) -> float:
        return self._config.backoff_factor * (2.0**attempt)

    def _retry_delay(self, attempt: int, response: httpx.Response) -> float:
        return self._retry_after(response) or self._backoff(attempt)

    @staticmethod
    def _retry_after(response: httpx.Response) -> float | None:
        raw = response.headers.get("Retry-After")
        if raw is None:
            return None
        try:
            return float(raw)
        except ValueError:
            return None

    def _process_response(self, response: httpx.Response) -> dict[str, Any]:
        if response.is_success:
            data = self._safe_json(response)
            if not isinstance(data, dict):
                raise APIError(
                    response.status_code,
                    "Expected a JSON object in the response body",
                    response=response,
                )
            return data
        raise api_error_from_status(
            response.status_code,
            self._error_message(response),
            retry_after=self._retry_after(response),
            response=response,
        )

    @staticmethod
    def _safe_json(response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return None

    def _error_message(self, response: httpx.Response) -> str:
        body = self._safe_json(response)
        if isinstance(body, dict):
            message = body.get("message")
            if isinstance(message, str):
                return message
        return response.text or "API request failed"
