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

## Documentation

The documentation site at <https://vfbquery.readthedocs.io> is built by Read the
Docs from `.readthedocs.yaml` and `docs/conf.py`, and needs nothing added to the
release procedure above: RTD builds `latest` from every push to `main` and
`stable` from every tag, so cutting a release publishes the matching docs on its
own.

Two details are worth knowing when a release does something unexpected:

- **The docs version comes from `_version.py` as well.** `docs/conf.py` reads it
  the same way `setup.py` does, so the site header and the `{{ release }}`
  substitution on the landing page name the version being documented. Since the
  publish workflow rewrites `_version.py` *and* commits it back to `main`, both
  `stable` and `latest` end up correct without a second bump.
- **`stable` is what PyPI links to.** The `Documentation` URL in `setup.py`'s
  `project_urls` (and in the client's `pyproject.toml`) points at `/en/stable/`,
  because somebody arriving from PyPI has installed the released version, not
  `main`. If a documentation fix needs to reach them before the next release, it
  has to go out as a release — merging it to `main` only updates `latest`.

The build treats warnings as errors (`fail_on_warning` in `.readthedocs.yaml`,
`-W` in the docs workflow), so a broken cross-reference fails the build rather
than shipping a dead link. `.readthedocs.yaml` also asks for a PDF, which is
built by xelatex and is where the awkward cases live: the PDF drops the emoji
that the generated documents are full of, translating `✅`/`❌` in a status
column to `[OK]`/`[FAIL]`, and it elides code blocks over 80 lines because the
1,100-line JSON examples in `README.md` overflow a TeX box and stop the build
outright. Both transforms are in `docs/conf.py`, both apply to the PDF only, and
the HTML remains the complete version. `docs/_root/` is generated at build time — `conf.py`
copies the repo-root markdown into it — and is gitignored; do not commit it, and
do not fix a docs-only problem by editing `README.md`, which is itself generated
(see the note at the top of `docs/conf.py`).

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
