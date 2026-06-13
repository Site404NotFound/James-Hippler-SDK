# Security Policy

## Reporting a vulnerability

Please report security issues privately via GitHub's
[private vulnerability reporting](https://github.com/Site404NotFound/James-Hippler-SDK/security/advisories/new)
rather than opening a public issue. We'll acknowledge the report and work on a fix before any
public disclosure.

## Handling of secrets

The SDK never logs or persists your API key. It is held as a `pydantic.SecretStr`, so it is masked
in `repr()`, logs, and tracebacks, and is read only when building the request's `Authorization`
header. Provide it via the `THE_ONE_API_KEY` environment variable (or a git-ignored `.env`) — never
commit it to source control.

## Supported versions

This project is pre-1.0; only the latest version on `main` is supported.
