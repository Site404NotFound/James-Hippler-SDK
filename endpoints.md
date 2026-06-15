# Endpoint reference

This SDK covers the **movie** and **quote** endpoints of [The One API](https://the-one-api.dev)
(v2). Every request goes to `https://the-one-api.dev/v2` with an `Authorization: Bearer <api-key>`
header, which the client adds for you (see [Authentication](README.md#authentication)).

Responses come back in a paginated envelope, exposed by the SDK as `Page[T]`:

| Field | Meaning |
|---|---|
| `docs` | the results for this page |
| `total` | total matching documents across all pages |
| `limit` | page size (defaults to 1000) |
| `offset` | items skipped |
| `page` / `pages` | current page / total pages |

`Page` behaves like a read-only sequence of `docs` (`len`, indexing, slicing, iteration, `in`,
`count`, `index`) and exposes `has_next_page`. Use `iter_all()` to stream every page lazily.

**Filtering and sorting** use the fluent `Query` builder. Request URLs below show operators in their
**readable form** (`budgetInMillions>100`); the SDK percent-encodes them on the wire. See
[querying.md](querying.md) for the full operator reference and the encoding rules.

**Not found:** a get-by-id for a missing document returns **HTTP 200 with an empty `docs` array**
(not a 404). The SDK detects this and raises `NotFoundError`.

All responses below are **real**, captured from the live API; long `docs` arrays are trimmed to 1–2
entries (the envelope metadata is unmodified).

---

## Movies

### `GET /movie` — list movies

**SDK:** `client.movies.list(query=None)` → `Page[Movie]` (async: `await async_client.movies.list(...)`)

**Filterable fields:** `name`, `runtimeInMinutes`, `budgetInMillions`, `boxOfficeRevenueInMillions`,
`academyAwardNominations`, `academyAwardWins`, `rottenTomatoesScore`.

> Sorting `/movie` currently returns HTTP 500 upstream — see
> [Known upstream limitation](README.md#known-upstream-limitation).

```python
client.movies.list()
```

`GET /v2/movie`

```json
{
  "docs": [
    {
      "_id": "5cd95395de30eff6ebccde56",
      "name": "The Lord of the Rings Series",
      "runtimeInMinutes": 558,
      "budgetInMillions": 281,
      "boxOfficeRevenueInMillions": 2917,
      "academyAwardNominations": 30,
      "academyAwardWins": 17,
      "rottenTomatoesScore": 94
    }
  ],
  "total": 8,
  "limit": 1000,
  "offset": 0,
  "page": 1,
  "pages": 1
}
```

*(8 movies total; `docs` trimmed to 1.)*

**Filtered example** — budget over 100M, two per page:

```python
client.movies.list(Query().where("budgetInMillions").gt(100).limit(2))
```

`GET /v2/movie?budgetInMillions>100&limit=2`  *(wire: `?budgetInMillions%3E100&limit=2`)*

```json
{
  "docs": [
    {
      "_id": "5cd95395de30eff6ebccde56",
      "name": "The Lord of the Rings Series",
      "runtimeInMinutes": 558,
      "budgetInMillions": 281,
      "boxOfficeRevenueInMillions": 2917,
      "academyAwardNominations": 30,
      "academyAwardWins": 17,
      "rottenTomatoesScore": 94
    },
    {
      "_id": "5cd95395de30eff6ebccde57",
      "name": "The Hobbit Series",
      "runtimeInMinutes": 462,
      "budgetInMillions": 675,
      "boxOfficeRevenueInMillions": 2932,
      "academyAwardNominations": 7,
      "academyAwardWins": 1,
      "rottenTomatoesScore": 66.33333333
    }
  ],
  "total": 5,
  "limit": 2,
  "offset": 0,
  "page": 1,
  "pages": 3
}
```

**`Movie` model** (snake_case attributes via field aliases):

| API field | `Movie` attribute |
|---|---|
| `_id` | `id` |
| `name` | `name` |
| `runtimeInMinutes` | `runtime_in_minutes` |
| `budgetInMillions` | `budget_in_millions` |
| `boxOfficeRevenueInMillions` | `box_office_revenue_in_millions` |
| `academyAwardNominations` | `academy_award_nominations` |
| `academyAwardWins` | `academy_award_wins` |
| `rottenTomatoesScore` | `rotten_tomatoes_score` |

### `GET /movie/{id}` — get one movie

**SDK:** `client.movies.get(movie_id)` → `Movie` (raises `NotFoundError` if absent)

```python
client.movies.get("5cd95395de30eff6ebccde5b")
```

`GET /v2/movie/5cd95395de30eff6ebccde5b`

```json
{
  "docs": [
    {
      "_id": "5cd95395de30eff6ebccde5b",
      "name": "The Two Towers",
      "runtimeInMinutes": 179,
      "budgetInMillions": 94,
      "boxOfficeRevenueInMillions": 926,
      "academyAwardNominations": 6,
      "academyAwardWins": 2,
      "rottenTomatoesScore": 96
    }
  ],
  "total": 1,
  "limit": 1000,
  "offset": 0,
  "page": 1,
  "pages": 1
}
```

The SDK unwraps the single-element `docs` and returns the `Movie`.

### `GET /movie/{id}/quote` — quotes for a movie

**SDK:** `client.movies.quotes(movie_id, query=None)` → `Page[Quote]`

```python
client.movies.quotes("5cd95395de30eff6ebccde5b", Query().limit(2))
```

`GET /v2/movie/5cd95395de30eff6ebccde5b/quote?limit=2`

```json
{
  "docs": [
    {
      "_id": "5cd96e05de30eff6ebcce9b8",
      "dialog": "Sauron's wrath will be terrible, his retribution swift.",
      "movie": "5cd95395de30eff6ebccde5b",
      "character": "5cd99d4bde30eff6ebccfea0",
      "id": "5cd96e05de30eff6ebcce9b8"
    },
    {
      "_id": "5cd96e05de30eff6ebcce9b9",
      "dialog": "The battle for Helm's Deep is over. The battle for Middle-earth is about to begin.",
      "movie": "5cd95395de30eff6ebccde5b",
      "character": "5cd99d4bde30eff6ebccfea0",
      "id": "5cd96e05de30eff6ebcce9b9"
    }
  ],
  "total": 1008,
  "limit": 2,
  "offset": 0,
  "page": 1,
  "pages": 504
}
```

*(1008 quotes for The Two Towers; `docs` trimmed to 2.)*

---

## Quotes

### `GET /quote` — list quotes

**SDK:** `client.quotes.list(query=None)` → `Page[Quote]`

**Filterable fields:** `dialog`, `movie`, `character` (the latter two are id references).

```python
client.quotes.list(Query().limit(2))
```

`GET /v2/quote?limit=2`

```json
{
  "docs": [
    {
      "_id": "5cd96e05de30eff6ebcce7e9",
      "dialog": "Deagol!!",
      "movie": "5cd95395de30eff6ebccde5d",
      "character": "5cd99d4bde30eff6ebccfe9e",
      "id": "5cd96e05de30eff6ebcce7e9"
    },
    {
      "_id": "5cd96e05de30eff6ebcce7ea",
      "dialog": "Deagol!",
      "movie": "5cd95395de30eff6ebccde5d",
      "character": "5cd99d4bde30eff6ebccfe9e",
      "id": "5cd96e05de30eff6ebcce7ea"
    }
  ],
  "total": 2383,
  "limit": 2,
  "offset": 0,
  "page": 1,
  "pages": 1192
}
```

*(2383 quotes; `docs` trimmed to 2.)*

### `GET /quote/{id}` — get one quote

**SDK:** `client.quotes.get(quote_id)` → `Quote` (raises `NotFoundError` if absent)

```python
client.quotes.get("5cd96e05de30eff6ebcce7e9")
```

`GET /v2/quote/5cd96e05de30eff6ebcce7e9`

```json
{
  "docs": [
    {
      "_id": "5cd96e05de30eff6ebcce7e9",
      "dialog": "Deagol!!",
      "movie": "5cd95395de30eff6ebccde5d",
      "character": "5cd99d4bde30eff6ebccfe9e",
      "id": "5cd96e05de30eff6ebcce7e9"
    }
  ],
  "total": 1,
  "limit": 1000,
  "offset": 0,
  "page": 1,
  "pages": 1
}
```

**`Quote` model:**

| API field | `Quote` attribute |
|---|---|
| `_id` | `id` |
| `dialog` | `dialog` |
| `movie` | `movie_id` |
| `character` | `character_id` |

> The quote endpoints return both `_id` and a duplicate `id`; the SDK reads `_id` and ignores the
> rest (`extra="ignore"`).

---

## Not found

A get-by-id for a missing (but well-formed) id is **not** a 404 — the API answers HTTP 200 with an
empty `docs` list:

```python
client.movies.get("5cd95395de30eff6ebccdeff")  # raises NotFoundError
```

`GET /v2/movie/5cd95395de30eff6ebccdeff`

```json
{ "docs": [], "total": 0, "limit": 1000, "offset": 0, "page": 1, "pages": 1 }
```

The SDK detects the empty `docs` and raises `NotFoundError`, so absence is a typed error rather than
an `IndexError`.
