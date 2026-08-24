#!/usr/bin/env python3
"""Lint test files for the silently-passing anti-patterns documented in TESTING.md.

Operates on the lines a change ADDS (diffs ``<base>...HEAD``), so it flags what a
PR introduces rather than pre-existing code. For a genuine exception (a
deliberate empty-result test, a graceful-handling test), put ``# test-lint: allow``
on the offending line.

Usage:
    python scripts/lint_tests.py [<base-ref>]
    LINT_BASE=origin/main python scripts/lint_tests.py

Exit code 1 if any new violations are found.
"""
import os
import re
import subprocess
import sys

TESTING_DOC = "TESTING.md"
ALLOW = "test-lint: allow"

# Single-line guards that hide an empty result. Matched against the stripped line.
LINE_RULES = [
    (re.compile(r"^if\s+not\s+[\w.]+\.empty\s*:"),
     "empty-guard",
     "`if not X.empty:` around assertions lets an empty result pass silently — "
     "use `self.assertFalse(X.empty, ...)` instead"),
    (re.compile(r"^if\s+[\w.]+\[['\"]rows['\"]\]\s*:"),
     "rows-guard",
     "`if result['rows']:` around assertions lets an empty result pass silently — "
     "assert `self.assertTrue(result['rows'], ...)` first"),
    (re.compile(r"^if\s+[\w.]+\.get\(['\"](?:rows|data)['\"]\)\s*:"),
     "rows-guard",
     "`if result.get('rows'):` around assertions lets an empty result pass "
     "silently — assert non-empty first"),
    (re.compile(r"^if\s+['\"]data['\"]\s+in\s+\w+"),
     "stale-data-key",
     "VFBquery query results use the 'rows' key, not 'data' — this guard is "
     "always false; use 'rows' and assert non-empty"),
    (re.compile(r"^if\s+.*\blen\([^)]*\)\s*>\s*0\s*:"),
     "len-guard",
     "`if len(...) > 0:` around assertions lets an empty result pass silently — "
     "assert non-empty first"),
    (re.compile(r"^if\s+[\w.]+\[['\"]count['\"]\]\s*>\s*0\s*:"),
     "count-guard",
     "`if result['count'] > 0:` around assertions lets an empty result pass "
     "silently — assert `self.assertGreater(result['count'], 0, ...)`"),
]

# Error-hiding handler bodies (flagged only inside an `except`).
SWALLOW_BODY = re.compile(r"self\.(fail|skipTest)\(")

_TEST_FILE = re.compile(r"(^|/)test_[^/]*\.py$")


def changed_test_lines(base):
    """{path: set(added line numbers)} for changed test files under src/test, tests."""
    diff = subprocess.run(
        ["git", "diff", "--unified=0", f"{base}...HEAD", "--", "src/test", "tests"],
        capture_output=True, text=True, check=True).stdout
    files, path = {}, None
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            candidate = line[6:]
            path = candidate if _TEST_FILE.search(candidate) else None
            if path:
                files.setdefault(path, set())
        elif path and line.startswith("@@"):
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if m:
                start, count = int(m.group(1)), int(m.group(2) or 1)
                files[path].update(range(start, start + count))
    return files


def _indent(line):
    return len(line) - len(line.lstrip())


def enclosing_is_except(lines, idx):
    """True if the block directly containing line ``idx`` (0-based) is an `except`."""
    body_indent = _indent(lines[idx])
    for j in range(idx - 1, -1, -1):
        s = lines[j].strip()
        if not s or s.startswith("#"):
            continue
        if _indent(lines[j]) < body_indent:
            return s.startswith("except")
    return False


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("LINT_BASE", "origin/main")
    violations = []
    for path, added in changed_test_lines(base).items():
        try:
            lines = open(path, encoding="utf-8").read().splitlines()
        except OSError:
            continue
        for n in sorted(added):
            if n - 1 >= len(lines):
                continue
            raw = lines[n - 1]
            if ALLOW in raw:
                continue
            stripped = raw.strip()
            for rx, rule, msg in LINE_RULES:
                if rx.search(stripped):
                    violations.append((path, n, rule, msg, stripped))
                    break
            else:
                if SWALLOW_BODY.search(stripped) and enclosing_is_except(lines, n - 1):
                    violations.append((
                        path, n, "swallow-in-except",
                        "swallowing a query error in `except` hides real failures and "
                        "defeats the connection-skip policy — let it propagate",
                        stripped))

    if violations:
        print(f"\n✗ Test-lint found {len(violations)} issue(s) — see {TESTING_DOC}:\n")
        for path, n, rule, msg, stripped in violations:
            print(f"  {path}:{n}  [{rule}]")
            print(f"      {msg}")
            print(f"      | {stripped}\n")
        print(f"Fix per {TESTING_DOC}, or add `# {ALLOW}` on the line for a genuine "
              f"exception (e.g. a deliberate empty-result test).")
        return 1

    print("✓ Test-lint: no new silently-passing patterns in changed test lines.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
