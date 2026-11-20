# Example: locadora-api (Flask 1.1 / Python 3.11 → Flask 3.1 / Python 3.14)

A small rental-store ("locadora") API written as a realistic legacy project to test
the `legacy-upgrade` skill. It has weak tests (status codes only) and three hidden traps:

1. `from distutils.util import strtobool` - `distutils` is removed in Python 3.12, and the deprecation warning is hidden by setuptools' shim.
2. A custom `app.json_encoder` that formats prices as numbers and dates as `dd/mm/YYYY` - Flask 2.3 **silently ignores** it.
3. `request.get_json() or request.form` - Werkzeug 2.1+ rejects non-JSON requests, breaking the old web form.

The code in this folder is the **final, upgraded** version. The original legacy code
(Flask 1.1.4 pins, untouched tests) is in [`original/`](original/), so you can run the
whole upgrade yourself with the skill and compare your result with this one.

## Files

- `MIGRATION_REPORT.md` - the full report produced while following the skill. Commit hashes in it refer to the original demo repository's history (one commit per hop), not to this repository.
- `snapshots/cases.json` - the 14 behavior snapshot cases.
- `snapshots/baseline/` - responses of the original Flask 1.1 app.
- `snapshots/h*.md` - comparison report after each hop (`h3-flask22.md` shows the broken form post caught by snapshots while tests were green).
- `snapshots/counterfactual-naive.md` - what a naive "make it boot" upgrade would have shipped: 7/7 tests green, 10 of 14 endpoints changed.

## Re-run the comparison

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt     # Windows: .venv\Scripts\...
.venv/bin/python -m pytest -q
.venv/bin/python app.py 5102 &
python ../../legacy-upgrade/scripts/snapshot.py compare --base-url http://127.0.0.1:5102 \
  --cases snapshots/cases.json --baseline snapshots/baseline
```
Expected: 12 identical, 2 differences that are only the HTML of Werkzeug's default error pages (status codes unchanged).
