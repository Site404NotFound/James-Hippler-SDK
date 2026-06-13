# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0]

### Added
- Synchronous `Client` and asynchronous `AsyncClient` over a shared transport core.
- Coverage of the movie and quote endpoints: `movies.list/get/quotes/iter_all` and
  `quotes.list/get/iter_all`.
- Fluent `Query` builder for filtering (match, negate, include/exclude, exists, regex, comparisons),
  sorting, and pagination.
- Typed Pydantic v2 models (`Movie`, `Quote`, generic `Page[T]`) with alias mapping and
  forward-compatible parsing.
- Automatic pagination via lazy `iter_all()` iterators.
- Structured exception hierarchy and a resilient transport (retries with exponential backoff on
  429/5xx/network errors).
- API key held as a `SecretStr` so it can't leak into logs or reprs.
- Unit suite (100% coverage), opt-in live integration tests, and runnable sync/async demos.

[Unreleased]: https://github.com/Site404NotFound/James-Hippler-SDK/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Site404NotFound/James-Hippler-SDK/releases/tag/v0.1.0
