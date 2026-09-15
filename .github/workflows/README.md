# CI workflows

What each GitHub Actions workflow in this directory is for, when it runs, and
whether it can block a PR. For *how to write* a test that fits the CI policy
(assert content, never suppress empty results, fixture vs `data_health`), see
[`TESTING.md`](../../TESTING.md).

## Runs on every PR (to `main` / `dev`)

| Workflow (name) | File | Purpose | Backend? |
|---|---|---|---|
| **Tests** | `python-test.yml` | The correctness gate: the full pytest suite (`src/test` + `tests`) with the SOLR result cache disabled, parallel via xdist. On PRs it runs `-m "not data_health"`, so it excludes the live-content audit tests (see below), and it excludes the perf/examples suites (their own workflows). A real code failure is red here; an upstream **outage skips** the affected tests (surfaced as a PR warning + a neutral "Run completeness" check) rather than failing. | live |
| **Lint tests** | `test-lint.yml` | Test-quality gate: `scripts/lint_tests.py` over **only the test lines the PR adds**, failing on the anti-patterns in `TESTING.md` (empty-result guards, swallowed exceptions, shape-only assertions, …). | none (static) |
| **Test VFBquery Examples** | `examples.yml` | Executes the repo's canonical worked examples against live data, so a documented query shape that stops returning results is caught. Separate from *Tests* to isolate its live load. | live |
| **Performance Test** | `performance-test.yml` | Query-latency thresholds (`test_query_performance.py`), split out because those thresholds only hold with a warm cache and would flap inside the parallel correctness run. | live |

## Scheduled

| Workflow | Cadence | Cron (UTC) | What the scheduled run adds |
|---|---|---|---|
| **Performance Test** | daily | `0 2 * * *` | Runs the thresholds and **commits a refreshed `performance.md` to `main`** (the only scheduled job that writes to the repo; its `cancel-in-progress` is therefore PR-only). |
| **Tests** | weekly (Sun) | `0 0 * * 0` | Runs the **full suite *including* `data_health`** — the live-content audit. The term_info `_live` tests run here and fail loudly if the production `vfb_json` documents (built by [`VFB_json_schema_indexer`](https://github.com/VirtualFlyBrain/VFB_json_schema_indexer)) are stale or incomplete. This is a data/pipeline health signal, **not** a code gate. |
| **Test VFBquery Examples** | monthly (1st) | `0 0 1 * *` | Re-checks the worked examples against live data. |

> The weekly **Tests** `data_health` run can be red purely because a production
> document is incomplete, with nothing wrong in this repo. `main` is not a
> protected branch and this is not a PR gate, so that red blocks nothing — treat
> it as an alarm for the data pipeline, not a build failure.

## Not on PRs

| Workflow | File | Trigger | Purpose |
|---|---|---|---|
| **Docker Image CI** | `docker.yml` | push, release | Builds the runtime image, syncs `_version.py` to the tag, smoke-tests container startup and version. |
| **Publish 🐍 📦 to PyPI** | `publish_to_pypi.yaml` | release | Builds and publishes the package to PyPI. |

## Notes

- Three PR workflows (**Tests**, **Examples**, **Performance Test**) hit the live
  production data sources. Each sets a `concurrency` group so a newer commit
  cancels a superseded run; **Lint tests** is the only purely static PR check.
- "Upstream data source" across these runs means VFB's Neo4j / SOLR / Owlery or
  FlyBase's Chado; `conftest.py` turns a connection failure into a **skip** (not a
  failure) and writes a `skipped_tests_report.md` the PR comment embeds.
