# Testing VFBquery

Most VFBquery tests run **live queries against the production VFB backend**
(SOLR, Neo4j, Owlery, FlyBase Chado). That makes them powerful — they catch real
regressions in query results — but also easy to write badly: a test that never
checks its query returned anything passes forever while the query is silently
broken. A whole class of such tests was found and fixed in Aug 2026; this doc
exists so they don't come back.

Read this before adding or changing a test.

## Installing the test dependencies

Test tooling is declared in `tests/requirements.txt`, separately from the
runtime dependencies in `requirements.txt`. Install both:

```bash
pip install -r requirements.txt -r tests/requirements.txt
pip install -e .
```

The split exists so that test tooling never reaches an end user: `requirements.txt`
mirrors `setup.py`'s `install_requires` and is what the `Dockerfile` copies into
the runtime image, while `tests/requirements.txt` holds pytest, `pytest-timeout`
(which enforces the 300 s per-test ceiling from `pyproject.toml`) and
`pytest-xdist` (the `-n` parallel runner). If you add a test-only dependency,
put it in
`tests/requirements.txt` — not in `requirements.txt`, and not as an ad-hoc
`pip install` inside a workflow step.

## Running the suite

```bash
export PYTHONPATH=$PYTHONPATH:$PWD/
export VFBQUERY_CACHE_ENABLED=false            # test the code, not the cache
pytest -v -ra -n 4 --dist loadscope src/test tests
```

- The whole suite runs on every PR via `.github/workflows/python-test.yml`.
  Timing/performance checks live separately in `performance-test.yml`
  (`test_query_performance.py`), because their thresholds only hold with the
  cache warm.
- `-ra` prints a summary of skips at the end; the CI job turns any skips into a
  PR **warning** so a backend outage can't hide behind a green check. A green
  check *with* that warning means the run was incomplete because the VFB backend
  was unavailable — it is a report on backend health, not on the branch. Re-run
  it once the backend is answering before treating the branch as verified.
- Every live-backend workflow sets a `concurrency` group keyed on the branch, so
  a run is cancelled when a newer commit supersedes it. Parallelism is pinned at
  `-n 4` (the hosted runner's vCPU count) rather than `-n auto`, to keep the
  number of concurrent query streams aimed at production explicit and stable.
- A separate **Test Lint** check (`test-lint.yml` → `scripts/lint_tests.py`)
  fails the PR if it introduces any of the anti-patterns below. It only inspects
  the lines your PR *adds*. For a genuine exception (a deliberate empty-result
  test, a graceful-handling test), put `# test-lint: allow` on that line. You can
  run it locally: `python scripts/lint_tests.py origin/main`.

## How the suite treats the backend (read this — it drives the rules below)

`conftest.py` enforces one policy, and every test must fit it:

| Situation | Outcome |
|---|---|
| Backend **unreachable** (connection refused / timeout / 5xx gateway) | **SKIP** (shown as a PR warning) |
| Query **reaches** the backend and returns **no rows** | **FAIL** |
| Query returns rows | assertions run normally |

So an empty result is **never** an acceptable outcome for a known-populated
term — it is a bug. A backend outage is handled *for you*; you do not need
(and must not add) your own try/except to survive it.

## The rules

### 1. Assert content, not just shape

A backend test must assert the query **did its job** — returned the rows it
should — not merely that it returned a dict/DataFrame with the right keys.

```python
# BAD — passes even when the query returns nothing
result = get_parts_of("FBbt_00003748")
self.assertIn("rows", result)

# GOOD
result = get_parts_of("FBbt_00003748")
self.assertTrue(result["rows"], "mushroom body should have parts")
```

### 2. Never suppress an empty result

Do **not** wrap assertions in a truthiness guard. When the query returns nothing
the guarded assertions silently don't run and the test passes.

```python
# BAD — every check below is skipped on an empty result
if not result.empty:
    self.assertIn("id", result.columns)

# BAD — same thing with a dict
if result["rows"]:
    self.assertEqual(result["rows"][0]["id"], expected)

# GOOD — empty is a failure; the checks always run
self.assertFalse(result.empty, "<term> should return rows")
self.assertIn("id", result.columns)
```

The only legitimate empties are **deliberate negative tests** — e.g. querying an
invalid/nonexistent id to check graceful handling. Name them clearly
(`test_..._empty_result`) and assert the empty shape on purpose.

### 3. Never swallow exceptions

Do not put a query inside `try/except` that turns a failure into a pass, a
silent skip, or a hard failure. It defeats the connection-skip policy and hides
real errors.

```python
# BAD — a connection outage becomes a hard failure; a real bug is masked
try:
    result = get_similar_morphology(neuron)
    ...
except Exception as e:
    self.fail(f"Query failed: {e}")     # or: pass  / self.skipTest(...)

# GOOD — let it propagate. conftest turns an outage into a skip; a real
# error surfaces as an error.
result = get_similar_morphology(neuron)
self.assertFalse(result.empty, "<neuron> should have NBLAST matches")
```

### 4. Verify every fixture actually returns data

Before you assert on a term/id, confirm it is real, of the right **type**, and
**populated** — then record the count in a comment so the next person can trust
it. Real bugs found this way:

- a **template** (`VFB_00101567`, `VFB_00050000`) used as an "example neuron" —
  NBLAST returned 0 for it;
- a **Channel** node (`VFBc_00050000`) used as a "template" — painted domains
  returned 0;
- a non-existent DOI-style id (`DOI_10_7554_eLife_04577`) — the real node is
  `FBrf0227179`;
- placeholder ids commented "may need to be updated with real data".

```python
# GOOD — real, typed, populated, and the count is documented
self.nblast_term = "VFB_jrchk00s"   # neuron with NBLAST matches (215)
```

Quick check while writing:

```python
print(get_similar_morphology("VFB_jrchk00s", return_dataframe=False, limit=5)["count"])
```

Prefer stable, well-known ids (classic alleles, standard templates,
long-standing anatomy classes) over incidental ones.

### 5. Assert the keys/columns the function *actually* returns

Read the query function (or run it once) — do not assume. Two vacuous tests
existed because they checked keys that never appear:

- checking `result["data"]` when the function returns `rows` (so
  `if "data" in result` was always false and nothing ran);
- asserting a `label` column when the function returns `name`.

### 6. Wire new test files into CI

`python-test.yml` runs `pytest src/test tests` — a new `test_*.py` under either
directory is picked up automatically. If you add a file that belongs to a
dedicated workflow instead (a pure-timing test, or one that duplicates live
load another job already generates), add an explicit `--ignore` there with a
comment (see the existing `test_example_queries` / `test_query_performance`
ignores).

## Checklist for a new backend test

- [ ] Uses a real, correctly-typed id, verified to return rows (count in a comment).
- [ ] Asserts the result is **non-empty** (no `if not empty:` / `if rows:` guard).
- [ ] Asserts the **real** keys/columns the function returns.
- [ ] No `try/except` around the query that swallows errors.
- [ ] Deliberate empty/negative cases are named and assert the empty shape on purpose.
- [ ] Runs under `pytest src/test tests` (picked up by CI).

See `conftest.py` for the connection-skip mechanics.
