# VFBquery Caching Guide

VFBquery includes intelligent SOLR-based caching for optimal performance. Caching is **enabled by default** with production-ready settings.

## Default Behavior

VFBquery automatically enables SOLR caching when imported:

```python
import vfbquery as vfb

# SOLR caching is already active with optimal settings:
# - 3-month cache duration
# - Persistent across sessions
# - Zero configuration required

result = vfb.get_term_info('FBbt_00003748')  # Cached automatically
```

## How It Works

VFBquery uses a single-layer caching approach with SOLR:

1. **First query**: Fetches data from Neo4j/Owlery and caches in SOLR
2. **Subsequent queries**: Served directly from SOLR cache
3. **Cache persistence**: Survives Python restarts and server reboots
4. **Automatic expiration**: 3-month TTL matches VFB_connect behavior

## Cache coverage (v1.19.0)

As of v1.19.0 every query-result function reachable from the HA API handlers
(`ha_api.py`) is served by the persistent SOLR cache, except a small set that
are deliberately excluded (see below). Coverage is verified by a static sweep
that traces each handler entry point through the `QUERY_TYPE_MAP` dispatch and
the FlyBase/connectivity/hierarchy handlers — see `coverage_sweep.py`.

Caching is applied in one of two layers, both of which the handler path goes
through (`handler -> vfbquery.<fn> (patched to *_cached) -> _original`):

- `@with_solr_cache('<bucket>')` on the original in `vfb_queries.py` (most
  hierarchy / neuron-in-region / connectivity / image queries), or
- `@with_solr_cache('<bucket>')` on the `*_cached` wrapper in
  `cached_functions.py` (term_info, similarity, transcriptomics, datasets).

A function counts as cached if either layer carries the decorator; do not add
the decorator at both layers for the same function (double round-trips).

New buckets added in v1.19.0: `cluster_expression`, `expression_cluster`,
`scrnaseq_dataset_data`, `individual_neuron_inputs`, `similar_morphology`,
`similar_morphology_part_of`, `similar_morphology_part_of_exp`,
`similar_morphology_nb`, `similar_morphology_nb_exp`, `dataset_images`,
`all_aligned_images`, `all_datasets`, `transgene_expression_here`,
`related_anatomy`. The five genuinely new buckets (`dataset_images`,
`all_aligned_images`, `all_datasets`, `transgene_expression_here`,
`related_anatomy`) are also listed in the wrapper's `expensive_query_types`
and `dataframe_query_types`, so a limited request computes the full result
once, caches it, and serves later limited requests by slicing the cached full
result.

### Cross-dataset connectivity (`query_connectivity`)

`query_connectivity` takes five parameters (`upstream_type`,
`downstream_type`, `weight`, `group_by_class`, `exclude_dbs`), so the default
single-id `@with_solr_cache` key does not fit. It is persisted directly in
`vfb_connectivity.py` under a composite key
(`query_connectivity:{upstream}:{downstream}:{weight}:{group_by_class}:{exclude_dbs}`,
hashed for a Solr-safe document id). The in-memory `ResultCache` and request
coalescer in `ha_api.py` sit in front; this SOLR layer sits behind so a cold
miss survives restarts and reaches the other containers. Graph
post-processing (`post_fn`) stays in the handler and is never part of the
cached payload. `force_refresh=true` on `/query_connectivity` drops both the
in-memory entry and the SOLR document and recomputes.

### Term-info query previews (two-phase loading)

A rich term — a template or a painted-domain individual — carries several
preview queries (`PaintedDomains`, `AllAlignedImages`, `AlignedDatasets`,
`AllDatasets`, …) whose counts and first ten rows `fill_query_results` computes
serially. On a cold cache that is tens of seconds, so `get_term_info` does not
make the caller wait for it: it returns immediately with every preview's `count`
set to **-1**, meaning *not counted yet* (as distinct from `0`, "no matches"),
and warms the full previews on a background thread pool.

`-1` is also what makes the deferral safe. The cache refuses to *write* a
term_info whose previews are unresolved, and treats one as a miss on read, so a
blank is never promoted to the final answer — the request simply takes the fast
path again while the warm works.

**Fixed in v1.22.35:** the warm could not make progress. It signalled "fill
synchronously" by calling `get_term_info(force_refresh=True)`, and
`with_solr_cache` popped `force_refresh` off the kwargs without forwarding it to
the wrapped function — so the warm took the same fast path and produced the same
blank, forever. A live probe caught `VFB_00101567` returning `-1` for all four
previews on eight consecutive rounds over eight minutes, and
`force_refresh=true` on `/get_term_info` answered in 2.0s with blanks, which is
the tell: the synchronous fill takes far longer than that, so it never ran.

Two things changed. The decorator now forwards `force_refresh` to any wrapped
function that declares it (at the call site, deliberately not by putting it back
into `kwargs` — those keys generate the cache field names, so re-inserting it
would split the term_info namespace between refreshed and unrefreshed callers).
And the warm no longer uses `force_refresh` at all: it only ever runs when there
is no complete entry, so it has nothing to invalidate, and `force_refresh` would
additionally discard every sub-query cache underneath the fill — 74.6s measured
against 3.9s for the shallow fill. "Fill previews synchronously" is now its own
signal, a thread-local the warm sets.

A warm that finishes without a complete result puts the term on a cooldown
(`VFBQUERY_PREVIEW_WARM_COOLDOWN`, default 300s) so a term whose previews cannot
be computed does not queue one warm per request and starve the terms that can.

### Deliberately not cached

- `get_similar_morphology_userdata` — keyed on a per-session user upload id;
  the result is user/session-specific, so it is left to the in-memory L1
  cache only.
- `get_flybase_stocks`, `get_flybase_combo_pubs`, `find_stocks`,
  `find_combo_publications` — backed by the FlyBase RDBMS, not Neo4j/Owlery;
  out of scope for this offload.
- `resolve_entity`, `resolve_combination` — thin resolvers over the already
  cached `term_info`.
- `list_connectome_datasets` — tiny static list; L1 cache is sufficient.
- `get_hierarchy` — delegates its heavy work to the SOLR-cached
  `get_parts_of` / `get_subclasses_of` and relies on Owlery's own
  server-side cache, with the handler holding an in-memory composite-key
  entry; persistent composite caching is a sensible follow-up but was left
  out to keep this change focused.

### Cache server

The cache reads and writes `cache_url`, which defaults to the dedicated
query-cache Solr:

```
http://vfbquerycache.virtualflybrain.org:80/solr/vfb_json
```

(`SolrResultCache.DEFAULT_CACHE_URL`). This is a separate, lightly-loaded host
from the ontology Solr (`solr.virtualflybrain.org`); it is reached on port 80
because the Solr native port is firewalled externally. Override with the
`VFBQUERY_SOLR_URL` environment variable (e.g. to point at a staging core for
testing):

```bash
export VFBQUERY_SOLR_URL=http://localhost:8983/solr/vfb_json
```

Note: data reads in `vfb_queries.py` (term_info, painted domains, ontology
label lookups, etc.) still go to `solr.virtualflybrain.org` — only the result
*cache* moved. The two are independent.

## Cache versioning and invalidation

Every cache entry is stamped with the VFBquery package version (major.minor) that
wrote it, so results from an old code version aren't served after an upgrade.

The **running** version is resolved (in `solr_result_cache.py`) as:

1. the `VFBQUERY_VERSION` environment variable if set, otherwise
2. the installed package version (`importlib.metadata.version('vfbquery')`),

normalized to **major.minor**. That value comes from the single source of truth,
`src/vfbquery/_version.py` (see [RELEASING.md](RELEASING.md)).

On read, if an entry's stamp differs from the running version, invalidation is
**monotonic** — it only discards entries written by an *older* version:

- **Older (or unversioned) entry** → invalidated, deleted, and recomputed by the
  current code.
- **Newer entry** (seen by a stale/older install, or by an older deploy running
  alongside a newer one) → treated as a miss but **not deleted**. An older client
  must never purge a fresher entry; the previous `!=` check did, which let
  downgrades wipe live entries and made concurrent versions thrash each other.

Consequences for the major.minor namespace:

- **Patch bumps** (`1.20.0 → 1.20.3`) share the cache — no invalidation.
- **Minor/major bumps** (`1.20 → 1.21`) invalidate older entries on read, so a
  release that changes query output naturally refreshes the cache.

## Runtime Configuration

Control caching behavior:

```python
import vfbquery as vfb

# Clear specific cache entries
vfb.clear_solr_cache('term_info', 'FBbt_00003748')

# Get SOLR cache statistics
stats = vfb.get_solr_cache().get_cache_stats()
```

### Environment Control

Disable caching globally if needed:

```bash
export VFBQUERY_CACHE_ENABLED=false
```

When disabled, the cache layer is **fully bypassed** — every query runs live
against Neo4j/Owlery/Solr with **no read, no write, no version-invalidation, and
no contact with the cache server** (`solr_caching_disabled()` in
`solr_result_cache.py`; mirrored in `vfb_connectivity.query_connectivity`).

This is how the **integration tests** run in CI. The test steps that assert on
query *results* (`test_neuron_neuron_connectivity`, `test_neuron_region_connectivity`,
`test_vfb_connectivity`, the unit tests in `python-test.yml`, and `examples.yml`)
set `VFBQUERY_CACHE_ENABLED=false` so they:

- validate the **live** query for the branch under test, not a (possibly stale)
  cached result, and
- never write a PR/branch's output back into the **shared production cache**.

The performance workflow's perf-timing steps keep caching enabled on purpose
(they measure warm-cache latency); only the result-asserting steps disable it.

#### Read-only mode

```bash
export VFBQUERY_CACHE_READONLY=true
```

Read-only mode still **reads** the cache (warm results are served), but
suppresses every **mutation** — no writes, no force-refresh clears, and no
version/expiry purges (`solr_caching_readonly()`, gating `cache_result`,
`clear_cache_entry` and `_clear_expired_cache_document`).

This is used by the **performance-test workflow's perf-timing steps**, but only
on **pull requests** — `VFBQUERY_CACHE_READONLY` is set from
`github.event_name == 'pull_request'`. So:

- **On PRs** the perf steps read warm entries for representative timings but
  never write or purge. Combined with `VFBQUERY_CACHE_ENABLED=false` on the
  result-asserting steps, **no PR run can modify the production cache**.
- **On push-to-`main` and scheduled runs** those perf steps are *writable*, so
  they refresh/warm the cache under the current `main` version.

That post-merge + daily-scheduled warming (plus lazy refresh by production
traffic) is what keeps the cache populated for the version on `main`, including
after a release bumps it. There's no dedicated release-triggered warm.

Caveat: a PR that bumps the **minor/major** version reads cold in read-only mode
(its version's entries don't exist yet — see version invalidation below);
same-version PRs read the already-warm production entries.

Read-only mode's limitation is that it is read-only. A branch that *changes what
a query returns* can never observe its own results warm, so those steps run with
`VFBQUERY_CACHE_ENABLED=false` and pay the full cold cost on every job. Cache
namespaces (next section) exist for that case.

#### Private cache namespaces

```bash
export VFBQUERY_CACHE_NAMESPACE=ci-my-branch
export VFBQUERY_CACHE_NAMESPACE_FALLBACK=true   # optional
```

A namespace moves **every** read, write and delete this process performs into a
private id prefix. Cache document ids go from

```
vfb_query_term_info_FBbt_00003748
ns_ci_my_branch__vfb_query_term_info_FBbt_00003748
```

so a namespaced process is not merely forbidden from touching production
entries, it is *incapable of addressing them* — there is no id it can construct
that names one. That is a stronger guarantee than read-only mode, and it is what
makes it safe to let experimental code write.

The isolation runs both ways. The production sweep and stats report query
`id:vfb_query_*`, which does not match `ns_…` ids, and a namespaced sweep queries
`id:ns_<ns>__vfb_query_*`, which does not match production ids. Neither sees the
other's documents.

**Why a prefix and not a separate Solr collection.** A collection would need
provisioning, credentials and its own capacity planning for something that lives
for the length of a branch. A prefix needs one environment variable, and — the
part a separate collection cannot do — it can fall back.

**Read-through fallback.** With `VFBQUERY_CACHE_NAMESPACE_FALLBACK=true`, a
namespace miss is retried against the production document, strictly read-only:
the fallback path never writes, never purges and never expires what it reads,
even if it finds the entry corrupt or stale. A brand-new namespace is therefore
warm on its *first* run rather than after its first run.

Turn fallback **on** for timing work, where a production entry is a fair stand-in
for what the branch would have computed. Leave it **off** for anything asserting
on result *content*, where reading production would hide the branch's own
behaviour behind an entry some other code wrote.

**Naming.** The value is lowercased and everything outside `[a-z0-9]` becomes
`_`, capped at 48 characters, because the id is interpolated unescaped into a
Solr `q=id:` term where `-`, `:` and whitespace would change the query's meaning.
Passing a raw branch name is safe: `fix/silent-noop` becomes `fix_silent_noop`.
Use one namespace per branch — sharing one between branches reintroduces exactly
the cross-contamination the namespace is there to prevent.

**Lifetime.** Namespaced entries default to a **48-hour** TTL rather than
production's 2160 hours (override with `VFBQUERY_CACHE_TTL_HOURS`), so an
abandoned branch's scratch entries evaporate on their own. To reclaim the space
immediately:

```python
from vfbquery.solr_result_cache import get_solr_cache
get_solr_cache().purge_namespace()
```

`purge_namespace()` refuses to run when no namespace is set, and refuses an
explicit empty one: without that guard its delete query would expand to
`id:vfb_query_*` and wipe the production cache — the precise accident this
mechanism exists to make impossible.

**Interaction with the other two switches.** `VFBQUERY_CACHE_ENABLED=false` wins
over everything (the cache layer is bypassed entirely; no server contact at all).
`VFBQUERY_CACHE_READONLY=true` still suppresses all writes, so setting it
alongside a namespace gives you a namespace you can only read — rarely what you
want. Pick one: read-only for "warm production timings, touch nothing", a
namespace for "write freely, in a sandbox".

A namespace is announced with a `WARNING` at cache construction, naming the
prefix, whether fallback is on, and the TTL. Set one by accident on a production
deploy and every lookup misses; the warning is there so the logs say why rather
than leaving you to infer a total cache wipe.

#### Other environment variables

| Variable | Default | Effect |
|---|---|---|
| `VFBQUERY_SOLR_URL` | the shared cache collection | Point the persistent cache at a different Solr core. |
| `VFBQUERY_VERSION` | installed package version | Override the major.minor cache namespace. |
| `VFBQUERY_MAX_RESULT_MB` | 100 | Refuse to cache a payload larger than this. |
| `VFBQUERY_FACET_VOCAB_TTL` | 3600 | How long `/facets` and the type-name validator hold the vocabulary. |
| `VFBQUERY_PREVIEW_WARM_COOLDOWN` | 300 | How long before re-warming a term whose previews came back incomplete. |
| `VFBQUERY_CACHE_NAMESPACE` | *(empty = production)* | Move all cache reads/writes/deletes into a private id prefix. |
| `VFBQUERY_CACHE_NAMESPACE_FALLBACK` | `false` | On a namespace miss, read (never write) the production entry. |
| `VFBQUERY_CACHE_TTL_HOURS` | 2160 (48 when namespaced) | Lifetime of entries written by this process. |
| `VFBQUERY_COMPUTE_BUDGET` | 180 | How long an HTTP handler waits for a computation before answering `503 status:"computing"`. The computation is **not** cancelled — it keeps running and writes to the cache, so the retry the 503 asks for is the cheap one. Set to `0` to wait indefinitely (the pre-1.22.36 behaviour, minus the cancellation). |

### The compute budget and the cache

`VFBQUERY_COMPUTE_BUDGET` is a caching setting more than a timeout one, which is why it is documented
here. Before 1.22.36 the worker ran inline in the request coroutine, so anything that cancelled the
request — a client hanging up, a proxy giving up, a handler timing out — killed the computation
mid-flight with nothing written to the cache. The next caller started the same minutes-long query from
scratch, and so did the one after that; a query slow enough to lose one client was a query that could
never finish for anybody. Every request coalesced onto the same key was woken with "Request aborted,
please retry" and pointed back at exactly that query.

The computation now runs as a detached task that owns the coalescing future and the cache write, and
the handler keeps only the *waiting*, which is the part that should be cancellable. So the budget
bounds how long a caller waits, not how long the work runs, and the first slow request is what warms
the entry for everyone behind it.

## Performance Benefits

VFBquery SOLR caching provides significant performance improvements:

```python
import vfbquery as vfb

# First query: builds SOLR cache (~1-2 seconds)  
result1 = vfb.get_term_info('FBbt_00003748')

# Subsequent queries: served from SOLR cache (<0.1 seconds)
result2 = vfb.get_term_info('FBbt_00003748')  # 54,000x faster!

# Similarity queries are also cached
similar = vfb.get_similar_neurons('VFB_jrchk00s')  # Cached after first run
```

**Typical Performance:**

- First query: 1-2 seconds  
- Cached queries: <0.1 seconds
- Speedup: Up to 54,000x for complex queries
- **NBLAST similarity queries**: 10+ seconds → <0.1 seconds (cached)

## Monitoring Cache Performance

```python
import vfbquery as vfb

# Get SOLR cache statistics
cache = vfb.get_solr_cache()
stats = cache.get_cache_stats()
print(f"Total cached items: {stats['total_documents']}")
print(f"Cache size: {stats['total_size_mb']:.1f}MB")
```

## Usage Examples

### Production Applications

```python
import vfbquery as vfb

# SOLR caching is enabled automatically with optimal defaults
# Cache persists across application restarts

# Example: Long-running server
result = vfb.get_term_info('FBbt_00003748')     # Fast on repeated runs
instances = vfb.get_instances('FBbt_00003748')  # Cached automatically
```

### Jupyter Notebooks

```python
import vfbquery as vfb

# SOLR caching works automatically in notebooks
# Data persists between kernel restarts and notebook sessions

result = vfb.get_term_info('FBbt_00003748')     # Fast on repeated runs
instances = vfb.get_instances('FBbt_00003748')  # Cached automatically
```

## Benefits

- **Dramatic Performance**: 54,000x speedup for repeated queries
- **Zero Configuration**: Works out of the box with optimal settings
- **Persistent Storage**: SOLR cache survives Python restarts and server reboots
- **Server-side Caching**: Shared across multiple processes/instances
- **Similarity Queries**: NBLAST and morphological similarity searches are cached
- **Production Ready**: 3-month TTL matches VFB_connect behavior

## Best Practices

- **Monitor performance**: Use SOLR cache statistics regularly
- **Clear when needed**: Use `clear_solr_cache()` to force fresh data
- **Consider data freshness**: SOLR cache TTL ensures data doesn't become stale
- **Disable when needed**: Use environment variable if caching isn't desired
