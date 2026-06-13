# lotr-sdk

A clean, fully typed Python SDK for [The One API](https://the-one-api.dev) — the Lord of the
Rings API. It covers the **movie** and **quote** endpoints with a fluent query builder, automatic
pagination, typed models, structured errors, and both synchronous and asynchronous clients.

> Built as a take-home exercise. Please do not publish or share this SDK publicly.

## Features

- **Sync and async** clients sharing one core (`Client` / `AsyncClient`).
- **Fluent query builder** for filtering, sorting, and pagination.
- **Typed models** (Pydantic v2) with snake_case attributes and forward-compatible parsing.
- **Automatic pagination** via lazy `iter_all()` iterators.
- **Structured errors** — one base exception with per-status subclasses.
- **Resilient transport** — retries with exponential backoff on `429`/`5xx`/network errors.
- Fully type-hinted and ships a `py.typed` marker; 100% unit-test coverage.

## Requirements

- Python **3.11+**
- An API key — get a free one at <https://the-one-api.dev/sign-up>.

## Installation

The package is not published, so install it from source with [Poetry](https://python-poetry.org/):

```bash
git clone <this-repo>
cd James-Hippler-SDK
poetry install
```

This creates an isolated virtual environment with the SDK and its dependencies. Run code with
`poetry run python ...`, or `poetry shell` to activate the environment.

## Authentication

The client reads your key from the `THE_ONE_API_KEY` environment variable, or you can pass it
explicitly:

```bash
export THE_ONE_API_KEY="your-key"        # or copy .env.example to .env and fill it in
```

```python
from lotr_sdk import Client

client = Client()                         # uses THE_ONE_API_KEY
client = Client(api_key="your-key")       # or pass it directly
```

## Quickstart

```python
from lotr_sdk import Client, Query

with Client() as client:
    # List movies
    movies = client.movies.list()
    for movie in movies:
        print(movie.name, movie.budget_in_millions)

    # Filter, then fetch one by id and its quotes
    blockbusters = client.movies.list(Query().where("budgetInMillions").gt(100))
    movie = client.movies.get(blockbusters[0].id)
    quotes = client.movies.quotes(movie.id, Query().limit(10))

    # List and fetch quotes directly
    quote = client.quotes.list(Query().limit(1))[0]
    same = client.quotes.get(quote.id)
```

### Async

The async client mirrors the sync one; just `await` calls and use `async with` / `async for`:

```python
import asyncio
from lotr_sdk import AsyncClient, Query

async def main():
    async with AsyncClient() as client:
        # Fetch independent resources concurrently
        movies, quotes = await asyncio.gather(
            client.movies.list(Query().where("budgetInMillions").gt(100)),
            client.quotes.list(Query().limit(5)),
        )
        async for quote in client.quotes.iter_all():
            ...

asyncio.run(main())
```

## Filtering, sorting, and pagination

`Query` is a chainable builder. Start a filter with `.where(field)` and finish it with an operator;
combine with `.sort()`, `.limit()`, `.page()`, and `.offset()`.

```python
Query().where("budgetInMillions").gt(100).where("name").matches("/ring/i").limit(10)
```

| Builder call | Meaning | API form |
|---|---|---|
| `.where("name").eq("Gandalf")` | equals | `name=Gandalf` |
| `.where("name").ne("Gandalf")` | not equals | `name!=Gandalf` |
| `.where("name").in_(["A", "B"])` | one of | `name=A,B` |
| `.where("name").not_in(["A", "B"])` | none of | `name!=A,B` |
| `.where("name").exists()` | field present | `name` |
| `.where("name").not_exists()` | field absent | `!name` |
| `.where("name").matches("/ring/i")` | regex | `name=/ring/i` |
| `.where("budgetInMillions").gt(100)` | greater than | `budgetInMillions>100` |
| `.where("budgetInMillions").gte(100)` | ≥ | `budgetInMillions>=100` |
| `.where("runtimeInMinutes").lt(200)` | less than | `runtimeInMinutes<200` |
| `.where("runtimeInMinutes").lte(200)` | ≤ | `runtimeInMinutes<=200` |
| `.sort("budgetInMillions", descending=True)` | sort | `sort=budgetInMillions:desc` |
| `.limit(10).page(2).offset(5)` | paginate | `limit=10&page=2&offset=5` |

### Auto-pagination

`iter_all()` lazily walks every page so you can stream results without managing page numbers:

```python
for movie in client.movies.iter_all(Query().limit(100)):
    ...   # fetches the next page only when needed
```

## Error handling

All errors derive from `LotrError`, so you can catch everything with one `except`, or handle
specific cases:

```python
from lotr_sdk import Client
from lotr_sdk.exceptions import NotFoundError, RateLimitError, LotrError

try:
    movie = client.movies.get("does-not-exist")
except NotFoundError:
    ...
except RateLimitError as exc:
    retry_in = exc.retry_after
except LotrError:
    ...
```

| Exception | Raised when |
|---|---|
| `ConfigurationError` | No API key, or invalid options |
| `AuthenticationError` | `401` — missing/invalid key |
| `ForbiddenError` | `403` |
| `NotFoundError` | `404`, or a get-by-id with no match |
| `RateLimitError` | `429` (carries `retry_after`) |
| `ServerError` | `5xx` |
| `APIError` | base for the above HTTP errors (`status_code`, `message`) |
| `TransportError` | network failure / timeout |

## Configuration

```python
Client(
    api_key=None,        # falls back to THE_ONE_API_KEY
    base_url=None,       # default: https://the-one-api.dev/v2
    timeout=None,        # default: 30.0 seconds
    max_retries=None,    # default: 3 (429/5xx/network)
    backoff_factor=None, # default: 0.5 (exponential)
)
```

## Running the tests

```bash
# Unit tests (mocked, no network or key required)
poetry run pytest -m "not integration"

# Integration tests against the live API (requires a key)
export THE_ONE_API_KEY="your-key"
poetry run pytest -m integration

# Lint, format, and type checks
poetry run ruff check . && poetry run ruff format --check . && poetry run mypy src
```

## Running the demos

```bash
export THE_ONE_API_KEY="your-key"
poetry run python examples/demo_sync.py
poetry run python examples/demo_async.py
```

## Known upstream limitation

The live API currently returns **HTTP 500 when sorting `/movie` or `/quote`** (sorting works on
other collections such as `/book` and `/character`). The SDK's `sort()` is implemented per the API
spec and verified against the endpoints that support it; when the upstream `/movie` and `/quote`
sort is fixed it will work with no SDK change. Until then the SDK surfaces the upstream failure as
a `ServerError`.

## License

MIT — see [LICENSE](LICENSE). See [design.md](design.md) for the architecture and design rationale.
