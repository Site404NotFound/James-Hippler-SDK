"""Tests for ClientConfig resolution, defaults, and validation."""

from __future__ import annotations

import pytest

from lotr_sdk.config import ENV_API_KEY, ClientConfig
from lotr_sdk.exceptions import ConfigurationError


@pytest.fixture(autouse=True)
def _clear_api_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep tests hermetic regardless of the ambient environment."""
    monkeypatch.delenv(ENV_API_KEY, raising=False)


def test_explicit_api_key_is_used() -> None:
    config = ClientConfig.resolve(api_key="abc123")
    assert config.api_key == "abc123"


def test_api_key_falls_back_to_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_API_KEY, "from-env")
    assert ClientConfig.resolve().api_key == "from-env"


def test_explicit_api_key_takes_precedence_over_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(ENV_API_KEY, "from-env")
    assert ClientConfig.resolve(api_key="explicit").api_key == "explicit"


def test_missing_api_key_raises_configuration_error() -> None:
    with pytest.raises(ConfigurationError):
        ClientConfig.resolve()


def test_empty_api_key_raises_configuration_error() -> None:
    with pytest.raises(ConfigurationError):
        ClientConfig.resolve(api_key="")


def test_sensible_defaults() -> None:
    config = ClientConfig.resolve(api_key="k")
    assert config.base_url == "https://the-one-api.dev/v2"
    assert config.timeout == 30.0
    assert config.max_retries == 3
    assert config.backoff_factor == 0.5


def test_base_url_trailing_slash_is_stripped() -> None:
    config = ClientConfig.resolve(api_key="k", base_url="https://example.com/v2/")
    assert config.base_url == "https://example.com/v2"


def test_invalid_numeric_options_raise_configuration_error() -> None:
    with pytest.raises(ConfigurationError):
        ClientConfig.resolve(api_key="k", timeout=0)
    with pytest.raises(ConfigurationError):
        ClientConfig.resolve(api_key="k", max_retries=-1)


def test_config_is_immutable() -> None:
    config = ClientConfig.resolve(api_key="k")
    with pytest.raises(Exception):  # noqa: B017 - pydantic raises on frozen mutation
        config.api_key = "changed"  # type: ignore[misc]
