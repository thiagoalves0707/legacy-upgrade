#!/usr/bin/env python3
"""Record and compare HTTP behavior snapshots ("golden master") for legacy upgrades.

Standard library only. Python 3.8+.

    python snapshot.py record  --base-url URL --cases cases.json --out DIR
    python snapshot.py compare --base-url URL --cases cases.json --baseline DIR [--out DIR] [--report FILE]

Snapshots are stored raw; ignore rules are applied at compare time to both sides,
so you can refine ignore rules without re-recording the baseline.
See references/behavior-snapshots.md for the cases.json format.
"""
import argparse
import difflib
import json
import os
import re
import string
import sys
import urllib.error
import urllib.request
from pathlib import Path

IGNORED = "<ignored>"
DEFAULT_COMPARE_HEADERS = ["content-type"]


# ---------------------------------------------------------------- cases
def load_cases(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        sys.exit(f"error: cannot read cases file {path}: {exc}")
    defaults = data.get("defaults", {})
    cases = data.get("cases", [])
    if not cases:
        sys.exit("error: cases file has no 'cases'")
    seen = set()
    for case in cases:
        if "name" not in case or "path" not in case:
            sys.exit(f"error: every case needs 'name' and 'path': {case}")
        if case["name"] in seen:
            sys.exit(f"error: duplicate case name: {case['name']}")
        seen.add(case["name"])
    return defaults, cases


def setting(defaults, case, key, fallback):
    """List settings are merged (defaults + case); scalars: case wins."""
    if isinstance(fallback, list):
        return list(defaults.get(key, fallback)) + list(case.get(key, []))
    return case.get(key, defaults.get(key, fallback))


def expand(value):
    if isinstance(value, str):
        return string.Template(value).safe_substitute(os.environ)
    if isinstance(value, dict):
        return {k: expand(v) for k, v in value.items()}
    if isinstance(value, list):
        return [expand(v) for v in value]
    return value


def file_name(name):
    return re.sub(r"[^A-Za-z0-9._-]", "_", name) + ".json"


# ---------------------------------------------------------------- JSON path ignore
def parse_pattern(pattern):
    if not pattern.startswith("$"):
        raise ValueError(f"ignore pattern must start with '$': {pattern}")
    tokens, i = [], 1
    name_re = re.compile(r"[^.\[]+")
    while i < len(pattern):
        if pattern.startswith("..", i):
            m = name_re.match(pattern, i + 2)
            if not m:
                raise ValueError(f"bad pattern: {pattern}")
            tokens.append(("deep", m.group(0)))
            i = m.end()
        elif pattern[i] == ".":
            m = name_re.match(pattern, i + 1)
            if not m:
                raise ValueError(f"bad pattern: {pattern}")
            name = m.group(0)
            tokens.append(("any", None) if name == "*" else ("key", name))
            i = m.end()
        elif pattern[i] == "[":
            j = pattern.find("]", i)
            if j < 0:
                raise ValueError(f"bad pattern: {pattern}")
            inner = pattern[i + 1:j]
            if inner == "*":
                tokens.append(("any", None))
            elif inner.isdigit():
                tokens.append(("idx", int(inner)))
            else:
                tokens.append(("key", inner.strip("'\"")))
            i = j + 1
        else:
            raise ValueError(f"bad pattern: {pattern}")
    return tokens


def path_matches(tokens, path):
    if not tokens:
        return not path
    kind, value = tokens[0]
    if kind == "deep":
        return any(
            isinstance(path[k], str) and path[k] == value and path_matches(tokens[1:], path[k + 1:])
            for k in range(len(path))
        )
    if not path:
        return False
    head = path[0]
    if kind == "key":
        ok = isinstance(head, str) and head == value
    elif kind == "idx":
        ok = isinstance(head, int) and head == value
    else:
        ok = True
    return ok and path_matches(tokens[1:], path[1:])


def normalize(obj, patterns, unordered, path=()):
    if path and any(path_matches(p, path) for p in patterns):
        return IGNORED
    if isinstance(obj, dict):
        return {k: normalize(v, patterns, unordered, path + (k,)) for k, v in obj.items()}
    if isinstance(obj, list):
        items = [normalize(v, patterns, unordered, path + (i,)) for i, v in enumerate(obj)]
        if unordered:
            items.sort(key=lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False))
        return items
    return obj


def apply_regex(text, regexes):
    for rx in regexes:
        text = re.sub(rx, IGNORED, text)
    return text


# ---------------------------------------------------------------- HTTP
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None  # redirects are behavior: record them, do not follow


OPENER = urllib.request.build_opener(_NoRedirect)


def fetch(base_url, case, defaults, timeout):
    method = case.get("method", "GET").upper()
    url = base_url.rstrip("/") + expand(case["path"])
    headers = expand({**defaults.get("headers", {}), **case.get("headers", {})})
    data = None
    body = case.get("body")
    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(expand(body)).encode("utf-8")
            if not any(h.lower() == "content-type" for h in headers):
                headers["Content-Type"] = "application/json"
        else:
            data = expand(str(body)).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = OPENER.open(req, timeout=timeout)
        status, resp_headers, raw = resp.status, resp.headers, resp.read()
    except urllib.error.HTTPError as exc:
        status, resp_headers, raw = exc.code, exc.headers, exc.read()
    except (urllib.error.URLError, OSError) as exc:
        return {"error": str(getattr(exc, "reason", exc))}

    compare_headers = [h.lower() for h in setting(defaults, case, "compare_headers", [])] or DEFAULT_COMPARE_HEADERS
    text = raw.decode("utf-8", errors="replace")
    try:
        parsed, kind = json.loads(text), "json"
    except ValueError:
        parsed, kind = text, "text"
    return {
        "request": {"method": method, "path": case["path"]},
        "status": status,
        "headers": {h: resp_headers.get(h) for h in sorted(set(compare_headers))},
        "body_kind": kind,
        "body": parsed,
    }


# ---------------------------------------------------------------- compare
def comparable(snapshot, case, defaults):
    if "error" in snapshot:
        return snapshot
    regexes = setting(defaults, case, "ignore_regex", [])
    patterns = [parse_pattern(p) for p in setting(defaults, case, "ignore", [])]
    unordered = bool(setting(defaults, case, "unordered", False))
    body = snapshot["body"]
    if snapshot["body_kind"] == "json":
        body = normalize(body, patterns, unordered)
    else:
        body = apply_regex(body, regexes)
    headers = {k: (apply_regex(v, regexes) if isinstance(v, str) else v) for k, v in snapshot["headers"].items()}
    return {"status": snapshot["status"], "headers": headers, "body_kind": snapshot["body_kind"], "body": body}


def dump(obj):
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)


def write_snapshot(out_dir, name, snapshot):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / file_name(name)).write_text(dump(snapshot) + "\n", encoding="utf-8")


def cmd_record(args):
    defaults, cases = load_cases(args.cases)
    out = Path(args.out)
    errors = 0
    for case in cases:
        snap = fetch(args.base_url, case, defaults, args.timeout)
        if "error" in snap:
            errors += 1
            print(f"ERROR  {case['name']}: {snap['error']}")
            continue
        write_snapshot(out, case["name"], snap)
        print(f"saved  {case['name']}  ({snap['status']})")
    print(f"\n{len(cases) - errors}/{len(cases)} recorded in {out}")
    return 1 if errors else 0


def cmd_compare(args):
    defaults, cases = load_cases(args.cases)
    baseline_dir = Path(args.baseline)
    out = Path(args.out) if args.out else None
    results, report = {"same": 0, "diff": 0, "missing": 0, "error": 0}, []
    for case in cases:
        name = case["name"]
        current = fetch(args.base_url, case, defaults, args.timeout)
        if out and "error" not in current:
            write_snapshot(out, name, current)
        if "error" in current:
            results["error"] += 1
            line = f"ERROR    {name}: {current['error']}"
            print(line)
            report.append(f"- **ERROR** `{name}`: {current['error']}")
            continue
        base_file = baseline_dir / file_name(name)
        if not base_file.exists():
            results["missing"] += 1
            print(f"NO BASE  {name}")
            report.append(f"- **NO BASELINE** `{name}`")
            continue
        baseline = json.loads(base_file.read_text(encoding="utf-8"))
        a = dump(comparable(baseline, case, defaults)).splitlines()
        b = dump(comparable(current, case, defaults)).splitlines()
        if a == b:
            results["same"] += 1
            print(f"same     {name}")
            continue
        results["diff"] += 1
        diff = "\n".join(difflib.unified_diff(a, b, "baseline", "current", lineterm=""))
        print(f"DIFF     {name}\n{diff}\n")
        report.append(f"- **DIFF** `{name}`\n\n```diff\n{diff}\n```")
    summary = ", ".join(f"{k}: {v}" for k, v in results.items())
    print(f"\n{summary}")
    if args.report:
        Path(args.report).write_text(
            "# Snapshot comparison\n\n" + summary + "\n\n" + "\n".join(report) + "\n", encoding="utf-8"
        )
    return 0 if results["diff"] == results["missing"] == results["error"] == 0 else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("record", "compare"):
        p = sub.add_parser(name)
        p.add_argument("--base-url", required=True)
        p.add_argument("--cases", required=True)
        p.add_argument("--timeout", type=float, default=30)
        if name == "record":
            p.add_argument("--out", required=True)
        else:
            p.add_argument("--baseline", required=True)
            p.add_argument("--out", help="also save current snapshots here")
            p.add_argument("--report", help="write a Markdown diff report to this file")
    args = parser.parse_args()
    try:
        sys.exit(cmd_record(args) if args.command == "record" else cmd_compare(args))
    except ValueError as exc:
        sys.exit(f"error: {exc}")


if __name__ == "__main__":
    main()
