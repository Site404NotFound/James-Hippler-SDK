# Querying: filters, sorting, and pagination

The `Query` builder produces the wire query string the API expects. It is fluent and chainable —
every call returns the same `Query`, so filters, sorting, and pagination compose in one expression:

```python
from lotr_sdk import Client, MovieField, Query, RegexFlag

with Client() as client:
    page = client.movies.list(
        Query()
        .where(MovieField.BUDGET_IN_MILLIONS).gt(100)
        .where(MovieField.NAME).matches("the", flags=[RegexFlag.IGNORE_CASE])
        .limit(5)
    )
```

Start a filter with `.where(field)`, then call one operator on it. `field` is a raw string or a
[field enum](#known-fields). Multiple `.where(...)` clauses are ANDed together in order.
`Query.copy()` returns an independent copy (used internally by `iter_all`).

> **Readable vs wire form.** The "Query" column below shows the decoded, readable form. On the wire
> the SDK percent-encodes operator characters (`>`→`%3E`, `<`→`%3C`, `:`→`%3A`, `,`→`%2C`, `!`→`%21`,
> `/`→`%2F`), because The One API URL-decodes before parsing. The "Wire" column is exactly what
> `Query.to_query_string()` emits. See [endpoints.md](endpoints.md) for full request/response
> examples.

## Known fields

Use the field enums for autocomplete and typo-safe field names — each member's value is the wire
field name, so they are interchangeable with raw strings:

```python
from lotr_sdk import MovieField, QuoteField, RegexFlag

Query().where(MovieField.BUDGET_IN_MILLIONS).gt(100)
Query().where(QuoteField.DIALOG).matches("ring", flags=[RegexFlag.IGNORE_CASE])
```

| `MovieField` | Wire field |
|---|---|
| `ID` | `_id` |
| `NAME` | `name` |
| `RUNTIME_IN_MINUTES` | `runtimeInMinutes` |
| `BUDGET_IN_MILLIONS` | `budgetInMillions` |
| `BOX_OFFICE_REVENUE_IN_MILLIONS` | `boxOfficeRevenueInMillions` |
| `ACADEMY_AWARD_NOMINATIONS` | `academyAwardNominations` |
| `ACADEMY_AWARD_WINS` | `academyAwardWins` |
| `ROTTEN_TOMATOES_SCORE` | `rottenTomatoesScore` |

| `QuoteField` | Wire field |
|---|---|
| `ID` | `_id` |
| `DIALOG` | `dialog` |
| `MOVIE` | `movie` (movie-id reference) |
| `CHARACTER` | `character` (character-id reference) |

Raw strings still work (`.where("budgetInMillions")`), so a new API field needs no SDK update.

## Filter operators

Each operator is a method on the proxy returned by `.where(field)`:

| Operator | Matches | Query (readable) | Wire |
|---|---|---|---|
| `.eq(v)` | field equals `v` | `name=Gandalf` | `name=Gandalf` |
| `.ne(v)` | field not equal to `v` | `name!=Frodo` | `name%21=Frodo` |
| `.in_(vs)` | field in any of `vs` | `race=Hobbit,Human` | `race=Hobbit%2CHuman` |
| `.not_in(vs)` | field in none of `vs` | `race!=Orc,Goblin` | `race%21=Orc%2CGoblin` |
| `.exists()` | field is present | `name` | `name` |
| `.not_exists()` | field is absent | `!name` | `%21name` |
| `.matches(p, flags=[...])` | regex on a bare pattern | `name=/ring/i` | `name=%2Fring%2Fi` |
| `.gt(v)` | field > `v` | `budgetInMillions>100` | `budgetInMillions%3E100` |
| `.lt(v)` | field < `v` | `budgetInMillions<100` | `budgetInMillions%3C100` |
| `.gte(v)` | field >= `v` | `runtimeInMinutes>=200` | `runtimeInMinutes%3E=200` |
| `.lte(v)` | field <= `v` | `runtimeInMinutes<=200` | `runtimeInMinutes%3C=200` |

Booleans render lowercase (`.eq(True)` → `isReal=true`). Note the API's parser quirk the builder
handles for you: `>` and `<` are valueless tokens (`field>value`), while `>=`, `<=`, `=`, and `!=`
keep a literal `=` separator.

Regex `flags` are `RegexFlag` members — `IGNORE_CASE` (`i`), `MULTILINE` (`m`), `DOTALL` (`s`),
`EXTENDED` (`x`) — passed as a list and interchangeable with the raw letters (`flags=["i"]`).

## Sorting

`.sort(field, *, descending=False)`:

| Call | Query (readable) | Wire |
|---|---|---|
| `.sort("name")` | `sort=name:asc` | `sort=name%3Aasc` |
| `.sort("name", descending=True)` | `sort=name:desc` | `sort=name%3Adesc` |

> Sorting `/movie` and `/quote` currently returns HTTP 500 upstream. `sort()` is correct and works on
> endpoints that support it — see [Known upstream limitation](README.md#known-upstream-limitation).

## Pagination

| Call | Query | Meaning |
|---|---|---|
| `.limit(n)` | `limit=10` | page size (`n >= 1`) |
| `.page(n)` | `page=2` | 1-based page number (`n >= 1`) |
| `.offset(n)` | `offset=5` | skip `n` results (`n >= 0`) |

Out-of-range values raise `ValueError`. To walk every page without managing page numbers, use
`iter_all()`:

```python
for movie in client.movies.iter_all(Query().where("budgetInMillions").gt(100)):
    ...  # fetches each page lazily, stops when has_next_page is False
```

If you would rather page manually, `Page` exposes `total`, `page`, `pages`, and `has_next_page`.
