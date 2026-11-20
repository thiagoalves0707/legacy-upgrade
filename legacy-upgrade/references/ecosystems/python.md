# Python (Django, Flask, FastAPI, data stacks)

Sources of truth: "What's New in Python 3.x", the Django release notes and
deprecation timeline, and each library's changelog.

## Inventory
```bash
python --version; pip --version
pip list --outdated
pip-audit                       # pip install pip-audit
pipdeptree --warn silence       # dependency tree
```
Look for: `requirements.txt` without pins, `setup.py`-only projects, Python 2 code
(`print "x"`, `unicode`, `iteritems`), `six`/`future`, C extensions, `distutils`
usage, `pytz`, `nose` (dead), `mock` package instead of `unittest.mock`.

## Baseline
```bash
python -W default::DeprecationWarning -m pytest 2> deprecations.txt
python -X dev -m pytest                 # extra runtime checks
python manage.py check --deploy         # Django
python manage.py makemigrations --check --dry-run   # no pending model changes
```
**Warnings can lie.** Inside a virtualenv, setuptools installs a `distutils` shim
(`_distutils_hack`) that replaces the stdlib module, so `import distutils` emits no
DeprecationWarning even with `-W error` - yet it fails on Python 3.12+ without
setuptools. Always add a static scan:
```bash
grep -rnE "^\s*(from|import)\s+(distutils|imp|asyncore|asynchat|smtpd|aifc|cgi|cgitb|telnetlib|crypt|nntplib|pipes|sndhdr|imghdr|audioop|chunk|mailcap|msilib|nis|ossaudiodev|spwd|sunau|uu|xdrlib|lib2to3)\b" --include=*.py .
# removed in 3.12: distutils, imp, asyncore, asynchat, smtpd; removed in 3.13: the rest
vermin --no-tips .               # pip install vermin: minimum Python version per file
```
For Flask, also grep for `flask.json.JSONEncoder`, `json_encoder`, `JSON_AS_ASCII`,
`safe_str_cmp`, `attachment_filename`, `request.get_json()` - see below.

Freeze the exact environment first: `pip freeze > requirements.lock.txt` (or a lock in uv/poetry/pip-tools).

## Hop strategy
- Python 2 -> 3: first make the code run on both (`futurize`/`modernize`, `pyupgrade`), then drop 2. Never mix with a framework bump.
- Python 3.x: one minor at a time if the jump crosses removals (3.12 and 3.13 removed many old modules).
- Django: go through LTS releases: 1.11 -> 2.2 -> 3.2 -> 4.2 -> 5.2. Inside each step, fix all deprecation warnings before the next one. `django-upgrade` automates many rewrites.
- Pin and upgrade the heavy libraries (pandas, NumPy, SQLAlchemy, Celery) as separate hops.

## Useful tools
`pyupgrade`, `django-upgrade`, `ruff` (with `UP` rules), `pip-audit`, `vermin` (minimum Python version detection), `uv`/`pip-tools` for lockfiles.

## Silent behavior changes to check
- **Py2 -> Py3:** `/` becomes true division; `round()` uses banker's rounding; `str`/`bytes` split; `dict` iteration views; mixed-type comparisons raise. Money and report outputs change silently.
- **Removed stdlib modules:** `distutils`, `imp`, `asynchat`/`asyncore` (3.12); `cgi`, `telnetlib`, `crypt` and other "dead batteries" (3.13).
- **`datetime.utcnow()` deprecated (3.12)**; naive vs aware datetimes cause off-by-hours bugs.
- **Django `USE_TZ` default became True (5.0)** for projects that never set it: stored and displayed times shift.
- **Django pytz -> zoneinfo (4.0)**; `localize`/`normalize` code paths break or behave differently.
- **Django `DEFAULT_AUTO_FIELD`**: new models get BigAutoField; migrations appear for existing models if not set.
- **`CSRF_TRUSTED_ORIGINS` needs the scheme (4.0)**: POSTs fail behind proxies.
- **SQLAlchemy 2.0:** no library-level autocommit, `Query` legacy API, result row types change.
- **pandas 2.x/3.x:** copy-on-write semantics, nullable dtypes, changed default `groupby`/`concat` behaviors - numbers in exports can change.
- **NumPy 2:** type promotion rules (NEP 50) change results of mixed scalar/array arithmetic.
- **JSON serialization** of `Decimal`/`datetime` in DRF or custom encoders.
- **Flask 2.3: `app.json_encoder` removed - assigning it is silently ignored.** Custom Decimal/date formatting disappears: prices become strings (`"9.90"`), dates become HTTP dates (`"Fri, 30 Aug 2002 00:00:00 GMT"`). Migrate to a `flask.json.provider.DefaultJSONProvider` subclass in Flask 2.2, while the old encoder still works, and snapshot-compare.
- **Werkzeug 2.1: `request.get_json()` raises (400/415) for non-JSON requests** instead of returning `None`. Patterns like `request.get_json() or request.form` break form posts. Use `request.get_json() if request.is_json else None` to keep old behavior (`silent=True` also changes the malformed-JSON response).
- **Werkzeug default error pages** changed their HTML markup across 2.x; status codes are unchanged.
- **Python 3.13+ `sqlite3` emits ResourceWarning** for unclosed connections (often in test fixtures).

## Common workarounds (ledger them)
`-W ignore` / `filterwarnings = ignore` in pytest config, `USE_DEPRECATED_PYTZ`, pinning `setuptools<X` for old builds, `six` kept around, vendored copies of removed stdlib modules.
