# Behavior snapshots (golden master)

A behavior snapshot captures what the system *actually does* today, so you can
prove the upgraded system does the same. It catches what test suites miss: the
silent changes that do not crash but return different data.

Record snapshots **before the first change** and compare against that original
baseline after every hop and at the end.

## What to snapshot, by system type

| System type | Capture | How |
|---|---|---|
| HTTP / REST / GraphQL API | status, key headers, body | `scripts/snapshot.py` |
| Server-rendered web app | status, redirects, key HTML fragments or full HTML with dynamic parts stripped | `snapshot.py` (text bodies + `ignore_regex`), or a browser test tool if one already exists in the project |
| CLI tool | stdout, stderr, exit code, generated files, for a fixed set of inputs | small shell/script loop writing outputs to `snapshots/<case>.txt`, then `diff -r` |
| Library | public API surface (exported symbols, signatures) + outputs for representative inputs | characterization tests in the project's own test framework |
| Background jobs / queues | payloads enqueued, side effects (DB rows, emails, files) for a fixed trigger | run job against a fixture DB, dump affected tables |
| Database layer | schema dump; results of key queries | schema dump before/after (`pg_dump --schema-only`, `mysqldump --no-data`, framework schema dump); run key queries and save results as JSON/CSV |
| Reports / exports | generated CSV, PDF text, spreadsheets | save files, compare text or normalized content |

## Choosing cases (for APIs)

Cover, at minimum:
- Every endpoint/route at least once (list them from the router, not from memory).
- Error paths: 404, validation errors (422/400), unauthenticated (401), forbidden (403).
- Edge inputs: empty strings, `null`, missing fields, unicode/accents (`São Paulo`), very large and negative numbers, decimals, dates near midnight and DST changes, time zones.
- Pagination, sorting, filtering.
- Serialization-sensitive fields: dates, decimals/money, booleans, enums, nested associations.
- Write operations: run them against a disposable database and snapshot the response **and** the resulting rows.

## Determinism

Snapshots are only useful if the unchanged system reproduces them. Before trusting a baseline:
1. Use a **fixed, seeded database** (fixtures or a dump restored before each run).
2. Freeze or ignore time-dependent fields (`created_at`, `updated_at`, tokens, request IDs, ETags).
3. Seed random generators if the app allows it.
4. Run the baseline **twice** against the unchanged app. Anything that differs is non-deterministic: add it to `ignore` / `ignore_regex` or mark the case `unordered`.

Ignore lists must be **narrow**. Ignoring a whole body to make a comparison pass is
a workaround and goes in the ledger.

## Using scripts/snapshot.py

Standard library only, Python 3.8+. It does not follow redirects (redirects are behavior).

`cases.json`:
```json
{
  "defaults": {
    "headers": { "Authorization": "Bearer ${API_TOKEN}" },
    "ignore": ["$..created_at", "$..updated_at", "$.meta.request_id"],
    "compare_headers": ["content-type", "location"]
  },
  "cases": [
    { "name": "movies-list", "path": "/movies?page=1" },
    { "name": "movie-404", "path": "/movies/999999" },
    { "name": "rental-create-invalid", "method": "POST", "path": "/rentals",
      "body": { "movie_id": null } },
    { "name": "search-accents", "path": "/movies?q=S%C3%A3o", "unordered": true },
    { "name": "home-html", "path": "/", "ignore_regex": ["csrf-token\" content=\"[^\"]+\""] }
  ]
}
```

- `${VAR}` is replaced from environment variables, so tokens never live in the file.
- `ignore`: JSON paths. Supported syntax: `$.a.b`, `$..key` (any depth), `$.items[*].id`, `$.items[0]`, `$.*`.
- `ignore_regex`: regexes replaced in text bodies and compared header values.
- `unordered`: sort arrays before comparing (only when order truly does not matter).

Commands:
```bash
# baseline, before any change
python scripts/snapshot.py record  --base-url http://localhost:3000 --cases cases.json --out snapshots/baseline
# determinism check: run against the SAME unchanged app
python scripts/snapshot.py compare --base-url http://localhost:3000 --cases cases.json --baseline snapshots/baseline
# after each hop
python scripts/snapshot.py compare --base-url http://localhost:3000 --cases cases.json --baseline snapshots/baseline --out snapshots/hop-3 --report snapshots/hop-3.md
```
`compare` exits with code 1 if anything differs and prints a unified diff per case.

## Adding a case after the upgrade has started

You will often discover a new edge case mid-upgrade (e.g. while fixing a hop you
realize malformed input was never covered). Its baseline must come from the
**original** code, never from the current hop. Use a temporary git worktree:

```bash
git worktree add ../app-orig <original-commit>          # the commit before any upgrade change
cd ../app-orig && <create an env with the ORIGINAL dependency versions> && <start the app on another port>
python scripts/snapshot.py record --base-url http://localhost:5199 --cases <path-to>/cases.json --out /tmp/orig-rec
cp /tmp/orig-rec/<new-case>.json <project>/snapshots/baseline/   # copy only the new case
git worktree remove --force ../app-orig
```
Never re-record existing baseline files this way: copy only the new case. Note in the
report that the case was added late and how its baseline was recorded.

Commit `cases.json` and the baseline directory (minus secrets) so a human reviewer
can re-run the comparison.
