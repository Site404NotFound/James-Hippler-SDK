"""Enforce that the sync and async surfaces stay in lockstep.

The type system cannot express "the same method contract" across sync and async
(the return types diverge by ``Coroutine``), so this guarantee is checked at
runtime instead: paired resources must expose the same public methods with the
same parameters, and each client must attach the matching resource pair.
"""

from __future__ import annotations

import asyncio
import inspect

import pytest

from lotr_sdk import AsyncClient, Client
from lotr_sdk.resources.aio.movies import AsyncMoviesResource
from lotr_sdk.resources.aio.quotes import AsyncQuotesResource
from lotr_sdk.resources.sync.movies import MoviesResource
from lotr_sdk.resources.sync.quotes import QuotesResource


def _public_signatures(cls: type) -> dict[str, inspect.Signature]:
    """Map public methods to their parameters, dropping the return annotation.

    Return annotations are intentionally ignored: the sync and async twins differ
    there by design (``Page`` vs ``Awaitable[Page]``), but their parameters must
    match exactly.
    """
    result: dict[str, inspect.Signature] = {}
    for name, member in inspect.getmembers(cls, callable):
        if name.startswith("_"):
            continue
        signature = inspect.signature(member)
        result[name] = signature.replace(return_annotation=inspect.Signature.empty)
    return result


@pytest.mark.parametrize(
    ("sync_cls", "async_cls"),
    [
        (MoviesResource, AsyncMoviesResource),
        (QuotesResource, AsyncQuotesResource),
    ],
)
def test_resource_surface_parity(sync_cls: type, async_cls: type) -> None:
    assert _public_signatures(sync_cls) == _public_signatures(async_cls)


def test_clients_expose_paired_resources() -> None:
    with Client(api_key="test-key") as sync_client:
        assert isinstance(sync_client.movies, MoviesResource)
        assert isinstance(sync_client.quotes, QuotesResource)

    async_client = AsyncClient(api_key="test-key")
    try:
        assert isinstance(async_client.movies, AsyncMoviesResource)
        assert isinstance(async_client.quotes, AsyncQuotesResource)
    finally:
        asyncio.run(async_client.aclose())
