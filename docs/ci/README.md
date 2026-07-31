# Parked GitHub Actions workflows

The YAML files in this directory are **not running**. They are complete, valid workflow
definitions sitting one `git mv` away from being active:

```bash
git mv docs/ci/search-gates.yml     .github/workflows/search-gates.yml
git mv docs/ci/docs.yml             .github/workflows/docs.yml
git mv docs/ci/performance-test.yml .github/workflows/performance-test.yml
```

The last of those **overwrites a workflow that is already running**; check `git diff` after the move
rather than assuming it is additive.

They are parked rather than committed in place because the credential this branch was pushed with has
no `workflow` scope, and GitHub rejects a push touching `.github/workflows/` **wholesale** — not just
that file. Parking them keeps the definitions under review with the code they gate, instead of
existing only as a paragraph in a pull request description saying what CI ought to do.

Move them from a checkout with a workflow-scoped credential. Nothing else needs to change: neither
file refers to this directory, and both use paths relative to the repository root.

## `search-gates.yml`

The five gates from `scripts/check_gates.sh`, split into three jobs:

- **client** — the client's request-shaping tests on 3.8 (ubuntu-22.04) and 3.11 (ubuntu-latest),
  because the client claims `requires-python = ">=3.8"` and a claim nothing tests is a wish.
- **server** — everything under `tests/`, offline.
- **live** — schedule-only (`0 3 * * 1`), because it needs the live Solr index and a server started
  from the checkout.

## `docs.yml`

Builds the Sphinx site with `-W`, so a broken cross-reference fails the pull request rather than
appearing as a red badge on Read the Docs after the merge. A weekly `linkcheck` job runs separately;
see the comments at the top of the file for why it is not part of the gate.

## `performance-test.yml`

A replacement for the live `.github/workflows/performance-test.yml`, changing only the three `env:`
blocks so the job uses a private cache namespace on pull requests (see the *Private cache namespaces*
section of `CACHING.md`). Nothing else in the workflow moves — same steps, same thresholds, same
report.

What changes, per step:

| Step | Before | After (on pull requests) |
|---|---|---|
| Run Performance Test | read-only production cache | namespace `ci-<sha>`, fallback **on**, writable |
| Run Legacy Performance Test | read-only production cache | namespace `ci-<sha>`, fallback **on**, writable |
| Run Connectivity Tests | cache **off** entirely | namespace `ci-<sha>`, fallback **off**, writable |

Push-to-`main` and scheduled runs are untouched: no namespace, so they still write the production
cache and keep it warm for the deployed service.

The namespace is keyed on `github.sha`, not the branch. Keying on the branch would let an entry
written by a bad push be served to the run that was supposed to validate the fix — a green tick for
code that never actually ran. Per-commit keying gives up warmth *between* pushes and keeps it where
the cost concentrates: the auto-retry, which today re-pays the full cold cost of everything attempt 1
already computed.

Entries expire after 12 hours (`VFBQUERY_CACHE_TTL_HOURS`), so abandoned commits collect themselves.
There is no purge step: a namespace whose run is still in flight must not have the ground pulled out
from under it, and the TTL is shorter than the cases where that would matter.
