# Releasing VFBquery

## Version: single source of truth

The package version lives in exactly one place:

```
src/vfbquery/_version.py   ->   __version__ = "X.Y.Z"
```

Everything else derives from it, so the fields can never drift apart:

- **`setup.py`** reads `_version.py` at build time (via `exec`, without importing
  the package), so the wheel/sdist metadata matches.
- **`vfbquery/__init__.py`** does `from ._version import __version__`, so
  `vfbquery.__version__` (and `ha_api.py`'s version reporting) matches.
- **The SOLR result cache** stamps entries with this version (major.minor) and
  uses it for invalidation — see [CACHING.md](CACHING.md#cache-versioning-and-invalidation).

Do **not** hard-code the version anywhere else.

## Cutting a release

1. Create a **GitHub Release** with a tag of the form `vX.Y.Z` (e.g. `v1.21.0`).

That's it — the `Publish 🐍 📦 to PyPI` workflow
(`.github/workflows/publish_to_pypi.yaml`) does the rest:

1. Checks out the tag, extracts `X.Y.Z` from `refs/tags/vX.Y.Z`, and writes it
   into `_version.py` (`sed`).
2. Builds the sdist/wheel (version comes from `_version.py`) and verifies the
   metadata matches the tag.
3. **Publishes to PyPI** via trusted publishing.
4. **Commits the bump back to `main`** — switches from the detached tag checkout
   to live `main`, re-applies `X.Y.Z` to `_version.py`, and pushes
   `Bump version to X.Y.Z [skip ci]`.

So after a release, **`main` reflects the released version** too — you don't have
to bump it by hand.

## Cache warming after a release

A minor/major bump invalidates the previous version's cache entries
(see [CACHING.md](CACHING.md#cache-versioning-and-invalidation)), so they're
refilled with the new version's output. That happens two ways, with no dedicated
release-triggered step:

- **Lazily**, by the deployed production service as it serves traffic (the
  primary path — each query refreshes on first read).
- **By the `performance-test` workflow on `main`** — its perf steps are writable
  on push-to-`main` and scheduled (daily) runs (read-only only on PRs), so they
  recompute and re-cache the perf-test query set under the current `main`
  version. The daily schedule guarantees the new version's entries are warmed
  within a day of a release, so later PR runs read a warm cache.

### Notes & guarantees

- The commit-back step runs **only after a successful publish** and only for
  `refs/tags/v*` (`if: success() && startsWith(github.ref, 'refs/tags/v')`).
- It's a **no-op if `main` is already at that version** (guarded by
  `git diff --staged --quiet`), so you can also bump `_version.py` in a PR before
  tagging and the workflow won't create an empty commit.
- The push needs `contents: write`, which is declared in the workflow's job
  `permissions` alongside the `id-token: write` used for PyPI.
- `[skip ci]` keeps the housekeeping commit from retriggering the test/perf
  workflows.

### Choosing the version bump

Because the cache namespace is keyed on **major.minor**
(see [CACHING.md](CACHING.md#cache-versioning-and-invalidation)):

- Bump the **patch** for changes that don't alter query *output* — cached results
  stay valid (no invalidation).
- Bump **minor/major** when query output changes — older cache entries are then
  invalidated on read, so users get refreshed results.
