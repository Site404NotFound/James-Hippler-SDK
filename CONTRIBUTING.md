# Contributing

Thanks for your interest in improving the SDK. This guide covers local setup and the checks a
change must pass.

## Setup

The project targets Python 3.11+ and uses [Poetry](https://python-poetry.org/). Python itself is
managed locally (e.g. via [pyenv](https://github.com/pyenv/pyenv)) rather than installed globally.

```bash
poetry install          # creates an isolated in-project virtualenv with all dependencies
```

Copy `.env.example` to `.env` and add your `THE_ONE_API_KEY` (from
<https://the-one-api.dev/sign-up>) if you want to run the demos or integration tests.

## Quality gates

Every change must pass the same checks CI runs:

```bash
poetry run ruff check .              # lint
poetry run ruff format --check .     # formatting
poetry run mypy src                  # strict type checking
poetry run pytest -m "not integration"   # unit tests; coverage must stay at 100%
```

Coverage is enforced at **100%** (`fail_under = 100`). New code needs tests, written test-first
where practical.

Optional live checks (require `THE_ONE_API_KEY`):

```bash
poetry run pytest -m integration
poetry run python examples/demo_sync.py
```

## Workflow

- Branch off `main`; never push to `main` directly (it's protected).
- Keep commits small and self-contained, with concise, descriptive messages.
- Open a pull request; CI (lint, format, type check, tests across Python 3.11–3.14) must be green
  before merging.
- Update `README.md` / `design.md` when behavior or the public API changes.

## Design

See [design.md](design.md) for the architecture and the rationale behind the key decisions.
