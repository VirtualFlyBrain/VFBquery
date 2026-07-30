"""Regression tests: the term-info preview warm could never fill anything.

Two defects, one symptom. The symptom is that a rich term's query previews
report ``count = -1`` -- "not counted yet" -- forever. A probe against the live
service caught ``VFB_00101567`` (JRC2018Unisex) returning
``[('PaintedDomains', -1), ('AllAlignedImages', -1), ('AlignedDatasets', -1),
('AllDatasets', -1)]`` on all eight rounds across eight minutes, while
``VFB_00017894`` -- whose complete entry predates the regression -- served real
counts the whole time. Asking the endpoint for ``force_refresh=true`` came back
in 2.0s with the same blanks, which is the tell: the synchronous fill takes
minutes, so 2.0s means it never ran.

Defect one, in ``with_solr_cache``: the wrapper did
``force_refresh = kwargs.pop('force_refresh', False)`` and never handed it to
the wrapped function. So the decorator's own documented contract -- "the
decorated function can accept a 'force_refresh' parameter" -- was false for
every caller. ``get_term_info`` reads ``force_refresh`` to decide whether to
compute previews synchronously, so the background warm (which called back in
with ``force_refresh=True``) took the *blank* fast path, and the blank is
refused by the cache's completeness check. Nothing was poisoned; nothing
progressed either. The fast path simply re-ran on every request, forever.

Defect two, latent until defect one was fixed: with forwarding restored, the
warm's ``force_refresh=True`` would cascade into
``fill_query_results(force_refresh=True)``, busting every sub-query cache
underneath it -- 74.6s measured locally against 3.9s for the shallow fill. The
warm never needs that: it only runs when there is no complete cached entry, so
it has nothing to invalidate. "Fill synchronously" and "ignore all caches" are
now separate signals, the first being a thread-local set by the warm.

Why a thread-local and not a keyword on ``get_term_info``: ``kwargs`` is copied
into ``full_params``, which generates the cache field names, so a new keyword
would split the term_info cache namespace between warmed and unwarmed callers --
and the only sanctioned invalidation here is a major.minor version bump.

The tests reach the undecorated ``get_term_info`` body directly (see
``_raw_get_term_info``) where the branch itself is under test, so no cache and no
Solr are involved; the decorator tests drive the real wrapper with a fake cache
object.
"""
import threading
import time

import pytest

from vfbquery import solr_result_cache as src
from vfbquery import vfb_queries as vq


def _raw_get_term_info():
    """The undecorated ``get_term_info`` body, whatever the import order was.

    Not simply ``vq.get_term_info.__wrapped__``: when caching is enabled --
    the default, and so the state of a plain ``pytest tests/`` run --
    ``cached_functions.patch_vfbquery_functions`` rebinds
    ``vfb_queries.get_term_info`` to ``get_term_info_cached`` and stashes the
    decorated original as ``_original_get_term_info``. With
    ``VFBQUERY_CACHE_ENABLED=false`` no patching happens and the attribute is
    absent. Resolving both keeps these tests from passing or failing on an
    environment variable rather than on the code they are about.
    """
    fn = getattr(vq, '_original_get_term_info', vq.get_term_info)
    return getattr(fn, '__wrapped__', fn)


# ---------------------------------------------------------------------------
# 1. The decorator forwards force_refresh (defect one)
# ---------------------------------------------------------------------------

def test_force_refresh_reaches_a_function_that_declares_it(monkeypatch):
    """The contract in the decorator's docstring, asserted.

    Cache disabled, so this is the shortest path through the wrapper -- and the
    one the test suite itself uses. Before the fix ``seen`` was ``[False]``.
    """
    monkeypatch.setattr(src, "solr_caching_disabled", lambda: True)
    seen = []

    @src.with_solr_cache('term_info')
    def f(short_form, preview=True, force_refresh=False):
        seen.append(force_refresh)
        return {'Id': short_form}

    f('VFB_1', force_refresh=True)
    f('VFB_1', force_refresh=False)
    f('VFB_1')
    assert seen == [True, False, False]


def test_force_refresh_is_not_pushed_into_functions_that_do_not_declare_it(monkeypatch):
    """Forwarding is by signature, not blanket.

    A ``**kwargs`` function would swallow it silently and -- worse for the
    decorated functions that pass their kwargs onward -- relay it to callees
    that raise on an unexpected keyword. ``inspect.signature`` reports
    ``kwargs`` as VAR_KEYWORD, not as ``force_refresh``, so this stays out.
    """
    monkeypatch.setattr(src, "solr_caching_disabled", lambda: True)
    seen = []

    @src.with_solr_cache('term_info')
    def f(short_form, **kwargs):
        seen.append(dict(kwargs))
        return {'Id': short_form}

    f('VFB_1', force_refresh=True, preview=True)
    assert seen == [{'preview': True}]


def test_a_builtin_signature_does_not_break_the_wrapper(monkeypatch):
    """``inspect.signature`` raises ValueError for some C callables.

    The wrapper has to degrade to "does not take it" rather than propagate,
    because the alternative is a decorator that works only on pure-Python
    targets.
    """
    monkeypatch.setattr(src, "solr_caching_disabled", lambda: True)
    wrapped = src.with_solr_cache('term_info')(len)
    assert wrapped([1, 2, 3]) == 3
    assert wrapped([1, 2, 3], force_refresh=True) == 3


class _FakeCache:
    """Records the parameter dicts the wrapper uses to name cache fields."""

    def __init__(self, stored=None):
        self.stored = stored
        self.lookups = []
        self.writes = []
        self.cleared = []

    def get_cached_result(self, query_type, term_id, **params):
        self.lookups.append(params)
        return self.stored

    def cache_result(self, query_type, term_id, result, **params):
        self.writes.append(params)

    def clear_cache_entry(self, query_type, term_id):
        self.cleared.append(term_id)


def test_force_refresh_stays_out_of_the_cache_field_names(monkeypatch):
    """The reason forwarding happens at the call site, not via ``kwargs``.

    ``kwargs`` is copied into the params that generate cache field names. Put
    ``force_refresh`` back in there and ``get_term_info(x)`` and
    ``get_term_info(x, force_refresh=True)`` write to two different fields, so
    a refresh would populate an entry no ordinary caller ever reads -- a cache
    split with no version bump behind it. The function must see the flag while
    the cache must not.
    """
    cache = _FakeCache()
    monkeypatch.setattr(src, "solr_caching_disabled", lambda: False)
    monkeypatch.setattr(src, "get_solr_cache", lambda: cache)
    seen = []

    @src.with_solr_cache('term_info')
    def f(short_form, preview=True, force_refresh=False):
        seen.append(force_refresh)
        return {'Id': short_form, 'Name': 'x'}

    f('VFB_1', force_refresh=True)
    assert seen == [True]
    assert cache.cleared == ['VFB_1_preview_True']      # the refresh did happen
    for params in cache.lookups + cache.writes:
        assert 'force_refresh' not in params, params
    # And the un-refreshed caller names exactly the same field.
    cache.writes.clear()
    f('VFB_1')
    assert cache.writes and all(
        'force_refresh' not in p for p in cache.writes)


def test_force_refresh_skips_the_cache_read(monkeypatch):
    """A refresh must not be answered from the entry it just cleared."""
    cache = _FakeCache(stored={'Id': 'VFB_1', 'Name': 'cached'})
    monkeypatch.setattr(src, "solr_caching_disabled", lambda: False)
    monkeypatch.setattr(src, "get_solr_cache", lambda: cache)

    @src.with_solr_cache('term_info')
    def f(short_form, preview=True, force_refresh=False):
        return {'Id': short_form, 'Name': 'fresh'}

    assert f('VFB_1')['Name'] == 'cached'
    assert f('VFB_1', force_refresh=True)['Name'] == 'fresh'


# ---------------------------------------------------------------------------
# 2. get_term_info's two-phase branch (defect two)
# ---------------------------------------------------------------------------

@pytest.fixture
def term_info_stub(monkeypatch):
    """Drive ``get_term_info.__wrapped__`` with no Solr and no cache.

    Returns a dict of call recorders. ``fill_query_results`` is the thing under
    observation: reaching it means "filled synchronously", not reaching it
    means "returned a blank and deferred".
    """
    calls = {'filled': [], 'scheduled': []}

    monkeypatch.setattr(vq, "vfb_solr",
                        type('S', (), {'search': staticmethod(lambda q: [])})())
    monkeypatch.setattr(
        vq, "term_info_parse_object",
        lambda results, short_form: {
            'Id': short_form, 'Name': short_form,
            'Queries': [{'query': 'PaintedDomains',
                         'preview_columns': ['id', 'label']}]})

    def fake_fill(term_info, force_refresh=False):
        calls['filled'].append(force_refresh)
        for q in term_info['Queries']:
            q['count'] = 58
            q['preview_results'] = {'headers': ['id', 'label'], 'rows': [['a', 'b']]}
        return term_info

    monkeypatch.setattr(vq, "fill_query_results", fake_fill)
    monkeypatch.setattr(vq, "_schedule_preview_warm",
                        lambda sf: calls['scheduled'].append(sf))
    monkeypatch.setattr(vq, "solr_caching_disabled", lambda: False)
    return calls


def _counts(term_info):
    return [q.get('count') for q in term_info['Queries']]


def test_foreground_call_defers_and_schedules(term_info_stub):
    """The fast path, which is correct and stays: blank now, warm behind it."""
    out = _raw_get_term_info()('VFB_00101567', preview=True)
    assert _counts(out) == [-1]
    assert term_info_stub['filled'] == []
    assert term_info_stub['scheduled'] == ['VFB_00101567']


def test_a_warming_thread_fills_synchronously(term_info_stub):
    """THE regression test. Remove ``not _warming_previews()`` from the branch
    and this fails: the warm returns the same blank the foreground call already
    returned, so nothing is ever computed and every preview stays at -1.
    """
    vq._bg_preview_state.warming = True
    try:
        out = _raw_get_term_info()('VFB_00101567', preview=True)
    finally:
        vq._bg_preview_state.warming = False
    assert _counts(out) == [58]
    # It filled, and it did not recurse into scheduling another warm.
    assert term_info_stub['filled'] == [False]
    assert term_info_stub['scheduled'] == []


def test_the_warm_fills_shallowly(term_info_stub):
    """``force_refresh=False`` inside the fill is the 3.9s path; ``True`` is the
    74.6s one, because it discards every sub-query cache the fill would reuse.
    The warm has nothing to invalidate -- it only runs when no complete entry
    exists -- so the cheap path is also the correct one.
    """
    vq._bg_preview_state.warming = True
    try:
        _raw_get_term_info()('VFB_00101567', preview=True)
    finally:
        vq._bg_preview_state.warming = False
    assert term_info_stub['filled'] == [False]


def test_explicit_force_refresh_still_fills_synchronously(term_info_stub):
    """A caller who asked for a refresh gets a computed answer, not a blank in
    two seconds -- and the deep fill, because they did ask to ignore caches.
    """
    out = _raw_get_term_info()('VFB_00101567', preview=True,
                                       force_refresh=True)
    assert _counts(out) == [58]
    assert term_info_stub['filled'] == [True]
    assert term_info_stub['scheduled'] == []


def test_cache_disabled_fills_synchronously(term_info_stub, monkeypatch):
    """The test suite validates live data; it must not be handed blanks."""
    monkeypatch.setattr(vq, "solr_caching_disabled", lambda: True)
    out = _raw_get_term_info()('VFB_00101567', preview=True)
    assert _counts(out) == [58]
    assert term_info_stub['filled'] == [False]


def test_warming_flag_is_thread_local(term_info_stub):
    """One warm must not put every concurrent foreground request onto the slow
    path -- four warm threads and 80 peak users share this process.
    """
    vq._bg_preview_state.warming = True
    other = {}

    def in_another_thread():
        other['warming'] = vq._warming_previews()
        other['counts'] = _counts(
            _raw_get_term_info()('VFB_x', preview=True))

    t = threading.Thread(target=in_another_thread)
    t.start()
    t.join()
    vq._bg_preview_state.warming = False
    assert other['warming'] is False
    assert other['counts'] == [-1]


# ---------------------------------------------------------------------------
# 3. _schedule_preview_warm: what it asks for, and how often
# ---------------------------------------------------------------------------

@pytest.fixture
def warm_harness(monkeypatch):
    """Replace ``vfbquery.get_term_info`` and run real warms to completion."""
    import vfbquery

    state = {'calls': [], 'warming': [], 'complete': True}
    done = threading.Event()

    def fake_get_term_info(short_form, **kwargs):
        state['calls'].append((short_form, kwargs))
        state['warming'].append(vq._warming_previews())
        done.set()
        count = 58 if state['complete'] else -1
        return {'Id': short_form, 'Name': short_form,
                'Queries': [{'count': count}]}

    monkeypatch.setattr(vfbquery, "get_term_info", fake_get_term_info)
    vq._bg_preview_inflight.clear()
    vq._bg_preview_cooldown.clear()

    def warm(short_form):
        done.clear()
        vq._schedule_preview_warm(short_form)
        return done.wait(timeout=5)

    state['warm'] = warm
    state['done'] = done
    yield state
    vq._bg_preview_inflight.clear()
    vq._bg_preview_cooldown.clear()


def _settle(short_form, timeout=5.0):
    """Wait for the warm thread to leave its ``finally`` block."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        with vq._bg_preview_lock:
            if short_form not in vq._bg_preview_inflight:
                return True
        time.sleep(0.01)
    return False


def test_the_warm_does_not_ask_for_force_refresh(warm_harness):
    """It sets the thread-local instead. Passing ``force_refresh=True`` here is
    what turned a 3.9s job into a 74.6s one once forwarding was fixed.
    """
    assert warm_harness['warm']('VFB_1')
    assert _settle('VFB_1')
    (short_form, kwargs), = warm_harness['calls']
    assert short_form == 'VFB_1'
    assert 'force_refresh' not in kwargs
    assert kwargs == {'preview': True}
    assert warm_harness['warming'] == [True]


def test_the_warming_flag_is_cleared_afterwards(warm_harness):
    """The executor's threads are reused, so a leaked flag would put the next
    term's *foreground* call onto the synchronous path.
    """
    assert warm_harness['warm']('VFB_1')
    assert _settle('VFB_1')
    leaked = {}
    ev = threading.Event()

    def check():
        leaked['warming'] = vq._warming_previews()
        ev.set()

    vq._bg_preview_executor.submit(check)
    assert ev.wait(timeout=5)
    assert leaked['warming'] is False


def test_an_incomplete_warm_sets_a_cooldown(warm_harness):
    """Backpressure. A term whose previews cannot be computed -- a dead
    sub-query, a Solr timeout -- would otherwise queue one warm per request,
    forever, four at a time, and starve the terms that *can* be warmed.
    """
    warm_harness['complete'] = False
    assert warm_harness['warm']('VFB_bad')
    assert _settle('VFB_bad')
    assert 'VFB_bad' in vq._bg_preview_cooldown

    before = len(warm_harness['calls'])
    vq._schedule_preview_warm('VFB_bad')
    time.sleep(0.15)
    assert len(warm_harness['calls']) == before, "cooled-down term re-warmed"


def test_the_cooldown_expires(warm_harness):
    """It is backpressure, not a blocklist: the term has to become eligible
    again, or a transient Solr outage would freeze it out until a restart.
    """
    warm_harness['complete'] = False
    assert warm_harness['warm']('VFB_bad')
    assert _settle('VFB_bad')
    with vq._bg_preview_lock:
        vq._bg_preview_cooldown['VFB_bad'] = time.time() - 1
    assert warm_harness['warm']('VFB_bad')
    assert _settle('VFB_bad')
    assert len(warm_harness['calls']) == 2


def test_a_complete_warm_leaves_no_cooldown(warm_harness):
    """A successful warm caches a complete entry, so later requests never reach
    the scheduler at all -- but if the entry is later evicted, the retry must
    not be blocked by a stale cooldown from a run that succeeded.
    """
    warm_harness['complete'] = True
    assert warm_harness['warm']('VFB_ok')
    assert _settle('VFB_ok')
    assert 'VFB_ok' not in vq._bg_preview_cooldown


def test_a_raising_warm_is_contained_and_cooled(warm_harness, monkeypatch):
    """An exception must clear the in-flight marker (or the term can never be
    warmed again) and must count as incomplete (or a hard failure retries on
    every request).
    """
    import vfbquery

    def boom(short_form, **kwargs):
        warm_harness['calls'].append((short_form, kwargs))
        warm_harness['done'].set()
        raise RuntimeError("solr down")

    monkeypatch.setattr(vfbquery, "get_term_info", boom)
    assert warm_harness['warm']('VFB_boom')
    assert _settle('VFB_boom')
    assert 'VFB_boom' in vq._bg_preview_cooldown
    assert not vq._warming_previews()


def test_an_inflight_warm_is_not_duplicated(monkeypatch):
    """Concurrent openers of the same cold term must produce one warm, not N."""
    import vfbquery

    started = threading.Event()
    release = threading.Event()
    calls = []

    def slow(short_form, **kwargs):
        calls.append(short_form)
        started.set()
        release.wait(timeout=5)
        return {'Id': short_form, 'Name': short_form, 'Queries': [{'count': 1}]}

    monkeypatch.setattr(vfbquery, "get_term_info", slow)
    vq._bg_preview_inflight.clear()
    vq._bg_preview_cooldown.clear()
    try:
        vq._schedule_preview_warm('VFB_dup')
        assert started.wait(timeout=5)
        for _ in range(5):
            vq._schedule_preview_warm('VFB_dup')
        assert calls == ['VFB_dup']
    finally:
        release.set()
        _settle('VFB_dup')
        vq._bg_preview_inflight.clear()
        vq._bg_preview_cooldown.clear()


def test_expired_cooldowns_are_dropped_before_live_ones():
    """The map is keyed by term id, so unbounded growth is a slow leak in a
    long-lived service -- but eviction must not throw away backpressure that is
    still doing work while expired junk sits next to it.
    """
    vq._bg_preview_cooldown.clear()
    try:
        now = time.time()
        for i in range(60):
            vq._bg_preview_cooldown[f"expired{i}"] = now - 1
        for i in range(vq._BG_PREVIEW_COOLDOWN_MAX):
            vq._bg_preview_cooldown[f"live{i}"] = now + 300
        vq._trim_preview_cooldowns()
        assert len(vq._bg_preview_cooldown) == vq._BG_PREVIEW_COOLDOWN_MAX
        assert not any(k.startswith("expired") for k in vq._bg_preview_cooldown)
    finally:
        vq._bg_preview_cooldown.clear()


def test_trimming_falls_back_to_soonest_to_expire():
    """All-live and over the cap: something has to go, and the least costly
    choice is the entry closest to expiring, because it was about to become
    eligible for a re-warm anyway.
    """
    vq._bg_preview_cooldown.clear()
    try:
        now = time.time()
        for i in range(vq._BG_PREVIEW_COOLDOWN_MAX + 3):
            vq._bg_preview_cooldown[f"t{i}"] = now + 100 + i
        vq._trim_preview_cooldowns()
        assert len(vq._bg_preview_cooldown) == vq._BG_PREVIEW_COOLDOWN_MAX
        for i in range(3):
            assert f"t{i}" not in vq._bg_preview_cooldown
        assert f"t{vq._BG_PREVIEW_COOLDOWN_MAX + 2}" in vq._bg_preview_cooldown
    finally:
        vq._bg_preview_cooldown.clear()


def test_trimming_is_a_no_op_under_the_cap():
    """Eviction is O(n) per call; it must not run on the common path."""
    vq._bg_preview_cooldown.clear()
    try:
        now = time.time()
        vq._bg_preview_cooldown.update({"a": now - 1, "b": now + 300})
        vq._trim_preview_cooldowns()
        # The expired entry survives: `_schedule_preview_warm` already ignores
        # it by comparing the timestamp, so sweeping it here would be work for
        # nothing on every single warm.
        assert set(vq._bg_preview_cooldown) == {"a", "b"}
    finally:
        vq._bg_preview_cooldown.clear()


def test_the_cooldown_is_configurable():
    """Operations lever: the default is five minutes, and a deployment fighting
    a slow sub-query needs to widen (or zero) it without waiting for a release.
    """
    assert vq._BG_PREVIEW_COOLDOWN > 0
    with open(vq.__file__) as fh:
        assert "VFBQUERY_PREVIEW_WARM_COOLDOWN" in fh.read(), (
            "the cooldown must stay env-tunable")


def test_the_public_entry_point_reaches_the_decorated_original():
    """The warm calls ``vfbquery.get_term_info``, which is not the function in
    this module: with caching enabled, ``cached_functions`` rebinds it to
    ``get_term_info_cached``, a thin delegate. The fix depends on that whole
    chain -- public name, delegate, ``with_solr_cache``, body -- so the chain is
    asserted rather than assumed.

    Skipped when caching is disabled, because then no patching happens and
    there is no delegation to check.
    """
    import vfbquery
    from vfbquery import cached_functions

    if not hasattr(vq, '_original_get_term_info'):
        pytest.skip("caching disabled: no patch layer to verify")

    assert vfbquery.get_term_info is cached_functions.get_term_info_cached
    assert vq.get_term_info is cached_functions.get_term_info_cached
    # The delegate declares force_refresh and hands it on explicitly, so a
    # refresh survives the extra hop rather than being defaulted away.
    import inspect
    params = inspect.signature(cached_functions.get_term_info_cached).parameters
    assert 'force_refresh' in params and params['force_refresh'].default is False
    src_text = inspect.getsource(cached_functions.get_term_info_cached)
    assert 'force_refresh=force_refresh' in src_text
    # And what it delegates to is the decorated original, not a second cache
    # layer -- double-decorating was its own bug (two Solr reads per request).
    original = vq._original_get_term_info
    assert hasattr(original, '__wrapped__')
    assert '_original_get_term_info' in src_text


def test_the_stale_self_healing_claim_is_gone():
    """The module comment used to promise that an incomplete cached entry was
    "re-executed" until the full result landed. It was re-executed -- into the
    same blank fast path. The probe log is the counter-evidence, and a comment
    that describes a mechanism the code does not have is how this survived.
    """
    source = open(vq.__file__).read()
    assert "Self-healing falls out of the existing cache validation" not in source
    assert "_warming_previews" in source
