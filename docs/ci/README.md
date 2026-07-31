# Parked GitHub Actions workflows

The YAML files in this directory are **not running**. They are complete, valid workflow
definitions sitting one `git mv` away from being active:

```bash
git mv docs/ci/search-gates.yml     .github/workflows/search-gates.yml
git mv docs/ci/docs.yml             .github/workflows/docs.yml
git mv docs/ci/performance-test.yml .github/workflows/performance-test.yml
git mv docs/ci/docker.yml           .github/workflows/docker.yml
```

The last **two** of those **overwrite workflows that are already running**; check `git diff` after
the move rather than assuming it is additive.

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

A replacement for the live `.github/workflows/performance-test.yml`, changing the three `env:`
blocks so the job uses a private cache namespace on pull requests (see the *Private cache namespaces*
section of `CACHING.md`), plus the report push described at the end of this section. Nothing else in
the workflow moves — same steps, same thresholds, same report.

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

### The report push retries

`Commit and Push Performance Report` now rebases and retries up to three times instead of pushing
once. The job takes about twenty minutes and is not the only thing that pushes to `main`: the PyPI
publish workflow commits `Bump version to X.Y.Z [skip ci]` when a release is cut, so cutting a release
shortly after a merge lands that bump while the measurement is still running and the push is rejected
as non-fast-forward. That is exactly what happened on the v1.22.36 release — every test step passed
and the job still went red, which is the worst kind of red because it looks like a test failure.

Rebasing is safe here because the commit only ever touches `performance.md`, so it cannot conflict
with a version bump. A fourth failure is not a race and is left to fail.

`actions/checkout` clones at depth 1, which is the obvious thing to doubt about a rebase, so the loop
was rehearsed against a depth-1 detached checkout with two version bumps landing on `main` mid-run:
`git pull --rebase` fetches the missing commits, replays the report commit on top, and the second
push succeeds. No history is lost and nothing is force-pushed — the bumps stay, the report lands
above them.

## `docker.yml`

A replacement for the live `.github/workflows/docker.yml`, changing one step: `Extract metadata` now
sanitises the git ref before using it as a docker tag.

A git ref is not a docker tag. Docker accepts `[A-Za-z0-9_][A-Za-z0-9._-]{0,127}`; branch names
accept a good deal more, most importantly the slash in `fix/whatever`. Handed one unchanged, the
build fails outright:

```
ERROR: failed to build: invalid tag "virtualflybrain/vfbquery:fix/perf-report-push-race":
invalid reference format
```

That is a red X on nearly every pull request, and it lands *after* the image has already built,
started, answered `/health` and confirmed its own version — so the failing step tells you nothing
about the image and everything about the branch name. `main`, `dev` and `vX.Y.Z` are already valid
tags and pass through untouched, which is why releases have never hit it and why no published tag
moves when this lands.

### A note on `[skip ci]` in commit messages

GitHub matches that marker anywhere in the head commit message, body included. A commit whose message
*quotes* it — describing the version-bump commit, say — silently skips every workflow on the push and
on the pull request, and the pull request shows "Checks 0" with no explanation of why. Paraphrase it
in prose rather than quoting it verbatim.
