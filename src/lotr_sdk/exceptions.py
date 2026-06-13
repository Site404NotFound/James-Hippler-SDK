"""Exception hierarchy for the SDK.

All errors derive from :class:`LotrError`, so callers can catch everything the
SDK raises with a single ``except LotrError``. HTTP failures derive from
:class:`APIError` and are further specialised by status code, letting callers
handle (say) rate limiting differently from a missing resource.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "APIError",
    "AuthenticationError",
    "ConfigurationError",
    "ForbiddenError",
    "LotrError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "TransportError",
    "api_error_from_status",
]


class LotrError(Exception):
    """Base class for every error raised by the SDK."""


class ConfigurationError(LotrError):
    """The client was misconfigured (e.g. a missing API key)."""


class TransportError(LotrError):
    """A network-level failure (timeout, connection reset) before a response."""


class APIError(LotrError):
    """The API returned a non-success HTTP status.

    Args:
        status_code: The HTTP status code of the response.
        message: A human-readable description of the failure.
        response: The originating response object, if available.
    """

    def __init__(self, status_code: int, message: str, *, response: Any | None = None) -> None:
        super().__init__(f"[{status_code}] {message}")
        self.status_code = status_code
        self.message = message
        self.response = response


class AuthenticationError(APIError):
    """The API key was missing or invalid (HTTP 401)."""


class ForbiddenError(APIError):
    """The request was understood but refused (HTTP 403)."""


class NotFoundError(APIError):
    """The requested resource does not exist (HTTP 404)."""


class RateLimitError(APIError):
    """The client exceeded the rate limit (HTTP 429).

    ``retry_after`` carries the server's suggested cool-off in seconds, when
    provided via the ``Retry-After`` header.
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        retry_after: float | None = None,
        response: Any | None = None,
    ) -> None:
        super().__init__(status_code, message, response=response)
        self.retry_after = retry_after


class ServerError(APIError):
    """The API failed to handle the request (HTTP 5xx)."""


_STATUS_TO_ERROR: dict[int, type[APIError]] = {
    401: AuthenticationError,
    403: ForbiddenError,
    404: NotFoundError,
    429: RateLimitError,
}


def api_error_from_status(
    status_code: int,
    message: str,
    *,
    retry_after: float | None = None,
    response: Any | None = None,
) -> APIError:
    """Build the most specific :class:`APIError` for an HTTP status code.

    Known codes map to dedicated subclasses; any other 5xx becomes a
    :class:`ServerError`, and everything else falls back to :class:`APIError`.
    """
    error_cls = _STATUS_TO_ERROR.get(status_code)
    if error_cls is None:
        error_cls = ServerError if status_code >= 500 else APIError

    if error_cls is RateLimitError:
        return RateLimitError(status_code, message, retry_after=retry_after, response=response)
    return error_cls(status_code, message, response=response)
