# Migration report: locadora-api

**Status:** Ready for human verification
**Branch:** upgrade/flask3-py314   **Date:** 2026-11-19
**Operating mode:** A (autonomous)

## Goal
- From: Python 3.11.0, Flask 1.1.4 (Werkzeug 1.0.1, Jinja2 2.11.3)
- To:   Python 3.14.4, Flask 3.1.3 (Werkzeug 3.1.9, Jinja2 3.1.6)
- Reason: known vulnerabilities in Werkzeug 1.0.1 and Jinja2 2.11.3; Python and Flask versions far behind.
- Constraints: **API contract with the mobile app must not change** (prices as JSON numbers, dates as `dd/mm/YYYY`).
- Target support status: Flask 3.1.3 and Werkzeug 3.1.9 are the latest releases on PyPI (checked 2026-11-19); Python 3.14 is a supported release.

## Inventory (before)
| Component | Version | Notes |
|---|---|---|
| Python | 3.11.0 | |
| Flask | 1.1.4 | pinned |
| Werkzeug | 1.0.1 | pinned, **multiple PYSEC advisories** |
| Jinja2 | 2.11.3 | pinned, **multiple PYSEC advisories** |
| MarkupSafe | 1.1.1 | no wheel, builds via legacy `setup.py install` |
| itsdangerous | 1.1.0 | pinned |
| click | 7.1.2 | pinned |
| pytest | unpinned | risk: version drifts between installs |
| Database | SQLite in-memory, seeded at start | |

Risks found:
- `distutils.util.strtobool` - `distutils` removed in Python 3.12.
- `flask.json.JSONEncoder` + `app.json_encoder` - removed in Flask 2.3 (**silent**: the attribute is just ignored).
- `request.get_json() or request.form` - Werkzeug 2.1+ raises for non-JSON requests instead of returning `None`.
- Deprecation warnings did **not** reveal the `distutils` problem: setuptools' distutils shim in the venv hid it. It was found by a static scan for removed modules.

## Baseline (before any change)
- Tests: 7/7 passed, 0 skipped, ~0.5 s.
- Deprecation warnings: none reported (see note above - misleading).
- Snapshots: 14 cases in `snapshots/cases.json` (13 recorded first, `rental-malformed-json` added during H3 and recorded against the **original** commit via a temporary git worktree).
- Determinism check: rental `id` differs between runs (in-memory autoincrement) - `$.id` ignored on the 4 rental-creation cases only.
- Suspicious current behavior (**not fixed**, preserved on purpose):
  - `GET /movies?available=talvez` returns **500** (unhandled `ValueError`). Probably should be 400.
  - Tests only check status codes and titles; **no test covers prices, dates, totals or form-encoded posts**.

## Upgrade path
| # | Hop | Commit | Tests | Snapshot diffs vs original baseline |
|---|---|---|---|---|
| H1 | Replace `distutils.strtobool` with identical local function | 3cc1f98 | 7/7 | 0 |
| H2 | Flask 1.1.4 -> 2.0.3 | e0c298e | 7/7 | 0 |
| H3 | Flask 2.0.3 -> 2.2.5 (+2 fixes, see below) | 0239a31 | 7/7 | 2 (error page HTML only) |
| H4 | Flask 2.2.5 -> 2.3.3 | 79a9c79 | 7/7 | 2 (same) |
| H5 | Flask 2.3.3 -> 3.1.3 | d2aebfa | 7/7 | 2 (same) |
| H6 | Python 3.11 -> 3.14 | 7bba15b | 7/7 | 2 (same) |

H3 initially had **7/7 tests green but a broken contract**: `rental-form-encoded` went from 201 to 400. Fixed with
`(request.get_json() if request.is_json else None) or request.form`, which keeps Flask 1 behavior exactly (malformed JSON still 400; `get_json(silent=True)` would have changed it to 422).
Also in H3, `app.json_encoder` was migrated to a `DefaultJSONProvider` subclass producing identical output, before Flask 2.3 removed it.

### Counterfactual: the naive path
`snapshots/counterfactual-naive.md`: the H2 code on Flask 2.3 with the typical "make it boot" fix
(`from json import JSONEncoder`). Result: **7/7 tests green, 10 of 14 endpoints changed**:
`daily_price 9.9 -> "9.90"`, `released "30/08/2002" -> "Fri, 30 Aug 2002 00:00:00 GMT"`, form posts 400.
This is what would have shipped without behavior snapshots.

## Workaround ledger
| # | Hop | What | Why | Risk | How to remove later |
|---|---|---|---|---|---|
| 1 | H1 | Local copy of `strtobool` | `distutils` removed in 3.12 | Low | Keep, or replace with explicit parsing + 400 for invalid values (behavior change - needs product OK) |
| 2 | H3 | `LegacyJSONProvider` keeps Decimal -> float and `dd/mm/YYYY` dates | Mobile app contract | Decimal -> float can lose precision for large values (same as before) | Version the API and move to string decimals + ISO dates |
| 3 | H3 | `is_json` check to keep form-encoded fallback | Old web form | Low | Remove when the web form posts JSON |
| 4 | H6 | Python jumped 3.11 -> 3.14 in one hop | 3.12/3.13 not installed on this machine | Low here (no other removed modules used), but violates the one-minor-per-hop guidance | Run the suite on 3.12 and 3.13 in CI |

## Test changes
| Test | Before | After | Reason |
|---|---|---|---|
| `client` fixture | `del app._db` | `app._db.close(); del app._db` | ResourceWarning for unclosed sqlite3 connections on Python 3.13+. No assertion changed. |

## Accepted behavior differences (pending user acceptance)
| Case | Difference | Reason |
|---|---|---|
| `movies-available-invalid` (500), `rental-malformed-json` (400) | HTML of Werkzeug's default error page changed (`HTML 3.2` doctype -> `<!doctype html><html lang=en>`). Status code and content-type unchanged. | Werkzeug template change. Clients should not parse this body. **Needs explicit OK from the product owner.** |

## Final state
- Versions: Python 3.14.4, Flask 3.1.3, Werkzeug 3.1.9, Jinja2 3.1.6, MarkupSafe 3.0.4, itsdangerous 2.2.0, click 8.5.1, blinker 1.9.0.
- Tests: 7/7, no warnings (also with `-W error::DeprecationWarning`).
- Snapshots vs original baseline: 12/14 identical, 2 cosmetic error-page differences (above).
- Security audit (pip-audit): **no known vulnerabilities** (before: 15+ advisories in Werkzeug and Jinja2).

## Not verified
- Production server (gunicorn/waitress/uWSGI) - only Flask's dev server was used.
- Real database - the app uses a seeded in-memory SQLite.
- The real mobile app and the real web form (only simulated with HTTP calls).
- Python 3.12 and 3.13 (skipped, see ledger #4).
- `pytest` is still unpinned in `requirements.txt`.

## Human verification checklist
- [ ] Mobile app: list movies, open a movie, create a rental - prices and dates display correctly
- [ ] Old web form: create a rental (form-encoded POST)
- [ ] 7+ day rental shows the 10% discount (e.g. movie 4, 7 days = 51.98)
- [ ] Leap-year due date (start 2024-02-28, 2 days -> 01/03/2024)
- [ ] Error responses (404, 409, 422) look right in both clients
- [ ] Accept or reject the error-page HTML difference
- [ ] Decide on `?available=<invalid>` returning 500 (separate ticket, not part of this upgrade)
- [ ] Run under the production WSGI server in staging, check logs
- [ ] Rollback plan: previous image / `requirements.txt` from commit 1d97932
