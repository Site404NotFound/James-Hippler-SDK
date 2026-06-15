# Examples

Two runnable scripts that exercise the full movie and quote surface of the SDK,
with one small function per concept.

- [`demo_sync.py`](demo_sync.py) — the synchronous `Client`.
- [`demo_async.py`](demo_async.py) — the asynchronous `AsyncClient`; leads with
  `asyncio.gather` concurrency and `async for` auto-pagination.
- [`demo_helpers.py`](demo_helpers.py) — shared narration plus the offline query
  cookbook reused by both.

## Running

```sh
export THE_ONE_API_KEY=...        # free key: https://the-one-api.dev/sign-up
poetry run python examples/demo_sync.py
poetry run python examples/demo_async.py
```

## Sample output

Captured against the live API. The closing **query surface** section makes no
requests — it prints what each `Query` call serializes to (readable form, then
the percent-encoded wire form).

### `demo_sync.py`

```text
== List movies (/movie) ==
8 movies total (page 1/1, limit 1000).
  - The Lord of the Rings Series — $281M budget, $2917M box office, 17/30 Oscars, 94% RT, 558 min
  - The Hobbit Series — $675M budget, $2932M box office, 1/7 Oscars, 66.3333% RT, 462 min
  - The Unexpected Journey — $200M budget, $1021M box office, 1/3 Oscars, 64% RT, 169 min

== Get one movie (/movie/{id}) ==
  fetched by id 5cd95395de30eff6ebccde56:
  - The Lord of the Rings Series — $281M budget, $2917M box office, 17/30 Oscars, 94% RT, 558 min

== Quotes for a movie (/movie/{id}/quote) ==
  The Two Towers has 1008 quotes; first 3:
  - "Sauron's wrath will be terrible, his retribution swift." (movie 5cd95395de30eff6ebccde5b, character 5cd99d4bde30eff6ebccfea0)
  - "The battle for Helm's Deep is over. The battle for Middle-earth is about to begin." (movie 5cd95395de30eff6ebccde5b, character 5cd99d4bde30eff6ebccfea0)
  - "All our hopes now lie with two little Hobbits..." (movie 5cd95395de30eff6ebccde5b, character 5cd99d4bde30eff6ebccfea0)

== List quotes (/quote) ==
2383 quotes total; first 3:
  - "Deagol!!" (movie 5cd95395de30eff6ebccde5d, character 5cd99d4bde30eff6ebccfe9e)
  - "Deagol!" (movie 5cd95395de30eff6ebccde5d, character 5cd99d4bde30eff6ebccfe9e)
  - "Deagol!" (movie 5cd95395de30eff6ebccde5d, character 5cd99d4bde30eff6ebccfe9e)

== Get one quote (/quote/{id}) ==
  - "Deagol!!" (movie 5cd95395de30eff6ebccde5d, character 5cd99d4bde30eff6ebccfe9e)

== Filtering (live) ==
  budget > $100M:
  - The Lord of the Rings Series: $281M
  - The Hobbit Series: $675M
  - The Unexpected Journey: $200M
  - The Desolation of Smaug: $217M
  - The Battle of the Five Armies: $250M
  name matches /ring/i:
  - The Lord of the Rings Series
  - The Fellowship of the Ring
  budget > $100M AND > 1 Oscar win (chained .where is ANDed):
  - The Lord of the Rings Series: 17 wins

== Typo-safe field enums (MovieField / QuoteField) ==
  4 movies with RT >= 90 (MovieField.ROTTEN_TOMATOES_SCORE)
  32 quotes match /precious/i (QuoteField.DIALOG); first 3:
  - "My precious."
  - "My precious!"
  - "Gollum' Gollum' Gollum', and we wept precious. We wept to be so alone."

== Pagination (limit / page / offset / has_next_page) ==
  limit=2  -> page 1/4, has_next_page=True
  page=2   -> ['The Unexpected Journey', 'The Desolation of Smaug']
  offset=1 -> ['The Hobbit Series', 'The Unexpected Journey']

== Auto-pagination (iter_all walks every page) ==
  iter_all() yielded 8 movies across all pages

== Typed errors ==
  missing id        -> NotFoundError: [404] No movie found with id '5cd95395de30eff6ebccdeff'
  sorting /movie    -> ServerError: [500] Something went wrong.

== Full query surface (no requests — shows what each call serializes to) ==
  .eq(v)         name=The Two Towers                      (wire: name=The%20Two%20Towers)
  .ne(v)         name!=The Hobbit Series                  (wire: name%21=The%20Hobbit%20Series)
  .in_(vs)       name=The Two Towers,The Hobbit           (wire: name=The%20Two%20Towers%2CThe%20Hobbit)
  .not_in(vs)    name!=The Hobbit Series                  (wire: name%21=The%20Hobbit%20Series)
  .exists()      academyAwardWins                         (wire: academyAwardWins)
  .not_exists()  !dialog                                  (wire: %21dialog)
  .matches(re)   name=/ring/i                             (wire: name=%2Fring%2Fi)
  .gt(v)         budgetInMillions>100                     (wire: budgetInMillions%3E100)
  .lt(v)         budgetInMillions<100                     (wire: budgetInMillions%3C100)
  .gte(v)        runtimeInMinutes>=160                    (wire: runtimeInMinutes%3E=160)
  .lte(v)        runtimeInMinutes<=200                    (wire: runtimeInMinutes%3C=200)
  .sort(asc)     sort=name:asc                            (wire: sort=name%3Aasc)
  .sort(desc)    sort=name:desc                           (wire: sort=name%3Adesc)
  .limit(n)      limit=10                                 (wire: limit=10)
  .page(n)       page=2                                   (wire: page=2)
  .offset(n)     offset=5                                 (wire: offset=5)
  chained (AND)  budgetInMillions>100&name=/the/i&limit=5 (wire: budgetInMillions%3E100&name=%2Fthe%2Fi&limit=5)
```

### `demo_async.py`

```text
== Concurrent fetch (asyncio.gather — the async payoff) ==
  fetched 5 movies and 3 quotes at once
  - The Lord of the Rings Series — $281M budget, $2917M box office, 17/30 Oscars, 94% RT, 558 min
  - The Hobbit Series — $675M budget, $2932M box office, 1/7 Oscars, 66.3333% RT, 462 min
  - The Unexpected Journey — $200M budget, $1021M box office, 1/3 Oscars, 64% RT, 169 min
  - "Deagol!!" (movie 5cd95395de30eff6ebccde5d, character 5cd99d4bde30eff6ebccfe9e)
  - "Deagol!" (movie 5cd95395de30eff6ebccde5d, character 5cd99d4bde30eff6ebccfe9e)
  - "Deagol!" (movie 5cd95395de30eff6ebccde5d, character 5cd99d4bde30eff6ebccfe9e)

== Get one movie (/movie/{id}) ==
  - The Lord of the Rings Series — $281M budget, $2917M box office, 17/30 Oscars, 94% RT, 558 min

== Quotes for a movie (/movie/{id}/quote) ==
  The Two Towers has 1008 quotes; first 3:
  - "Sauron's wrath will be terrible, his retribution swift." (movie 5cd95395de30eff6ebccde5b, character 5cd99d4bde30eff6ebccfea0)
  - "The battle for Helm's Deep is over. The battle for Middle-earth is about to begin." (movie 5cd95395de30eff6ebccde5b, character 5cd99d4bde30eff6ebccfea0)
  - "All our hopes now lie with two little Hobbits..." (movie 5cd95395de30eff6ebccde5b, character 5cd99d4bde30eff6ebccfea0)

== Quotes (/quote and /quote/{id}) ==
  - "Deagol!!" (movie 5cd95395de30eff6ebccde5d, character 5cd99d4bde30eff6ebccfe9e)

== Filtering (live) ==
  name matches /ring/i:
  - The Lord of the Rings Series
  - The Fellowship of the Ring
  budget > $100M AND > 1 Oscar win (chained .where is ANDed):
  - The Lord of the Rings Series: 17 wins

== Typo-safe field enums (MovieField / QuoteField) ==
  4 movies with RT >= 90 (MovieField.ROTTEN_TOMATOES_SCORE)
  32 quotes match /precious/i (QuoteField.DIALOG); first 3:
  - "My precious."
  - "My precious!"
  - "Gollum' Gollum' Gollum', and we wept precious. We wept to be so alone."

== Async pagination (limit / page, then async iter_all) ==
  limit=2 -> page 1/4, has_next_page=True
  async iter_all() yielded 8 movies across all pages

== Typed errors ==
  missing id     -> NotFoundError: [404] No movie found with id '5cd95395de30eff6ebccdeff'
  sorting /movie -> ServerError: [500] Something went wrong.

== Full query surface (no requests — shows what each call serializes to) ==
  .eq(v)         name=The Two Towers                      (wire: name=The%20Two%20Towers)
  .ne(v)         name!=The Hobbit Series                  (wire: name%21=The%20Hobbit%20Series)
  .in_(vs)       name=The Two Towers,The Hobbit           (wire: name=The%20Two%20Towers%2CThe%20Hobbit)
  .not_in(vs)    name!=The Hobbit Series                  (wire: name%21=The%20Hobbit%20Series)
  .exists()      academyAwardWins                         (wire: academyAwardWins)
  .not_exists()  !dialog                                  (wire: %21dialog)
  .matches(re)   name=/ring/i                             (wire: name=%2Fring%2Fi)
  .gt(v)         budgetInMillions>100                     (wire: budgetInMillions%3E100)
  .lt(v)         budgetInMillions<100                     (wire: budgetInMillions%3C100)
  .gte(v)        runtimeInMinutes>=160                    (wire: runtimeInMinutes%3E=160)
  .lte(v)        runtimeInMinutes<=200                    (wire: runtimeInMinutes%3C=200)
  .sort(asc)     sort=name:asc                            (wire: sort=name%3Aasc)
  .sort(desc)    sort=name:desc                           (wire: sort=name%3Adesc)
  .limit(n)      limit=10                                 (wire: limit=10)
  .page(n)       page=2                                   (wire: page=2)
  .offset(n)     offset=5                                 (wire: offset=5)
  chained (AND)  budgetInMillions>100&name=/the/i&limit=5 (wire: budgetInMillions%3E100&name=%2Fthe%2Fi&limit=5)
```
