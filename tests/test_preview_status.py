"""Regression tests: a cache write nobody can read makes "pending" permanent.

Three defects sat on top of each other, and each one hid the next.

The first is the one users saw. ``cache_result`` posted to Solr with
``commit=false`` and relied on an ``autoSoftCommit`` that the cache core does
not have (``autoSoftCommit.maxTime: -1``, ``autoCommit.openSearcher: false``).
The write was accepted, durable, and returned HTTP 200 — and never became
searchable. So every read-back missed, every ``get_term_info`` was cold, every
cold call took the two-phase fast path that blanks the previews and warms them
in the background, and the warmed answer went into the same invisible hole.
``count: -1`` — a state designed to last seconds — became the permanent answer
for every term.

The second is what that exposed about ``-1`` itself. It has always meant "not
counted yet", which is emphatically *not* ``0`` ("no matches"); the contract is
documented in CACHING.md and honoured by the v2 frontend. But nothing in the
payload said so, so a consumer had to know. ``status`` and ``message`` make the
distinction explicit without changing what ``-1`` means.

The third only became visible once ``status`` was load-bearing. Three validators
tested ``count >= 0`` to decide whether a result was worth caching. Read
literally that also condemns a *complete* preview whose exact total exceeded
``COUNT_CAP`` — there ``-1`` means "many", the rows are final, and there is
nothing to wait for. Any term with a large query was therefore rejected from the
cache and recomputed on every single request, forever, silently.

The tests are grouped in that order. The first group would fail against the old
``commit=false`` write; the second and third against the old ``count >= 0``
comparison and the missing ``status``.
"""
import json

import pytest

from vfbquery import solr_result_cache as src
from vfbquery import vfb_queries as vq
from vfbquery.solr_result_cache import (PREVIEW_STATUS_COMPLETE,
                                        PREVIEW_STATUS_PENDING,
                                        preview_is_resolved,
                                        solr_write_params)


# ---------------------------------------------------------------------------
# 1. The write has to become visible
# ---------------------------------------------------------------------------

def _clear_write_env(monkeypatch):
    monkeypatch.delenv('VFBQUERY_SOLR_WRITE_COMMIT', raising=False)
    monkeypatch.delenv('VFBQUERY_SOLR_COMMIT_WITHIN_MS', raising=False)


def test_default_write_is_non_blocking_but_visible(monkeypatch):
    """The default must carry ``commitWithin`` — that is the whole fix.

    ``commit=false`` alone is what broke: it defers to a soft commit that never
    happens on this core. ``commitWithin`` is honoured (the core's updateHandler
    sets ``commitWithin: {softCommit: true}``), so the POST still returns
    immediately while a searcher reopens inside the window.
    """
    _clear_write_env(monkeypatch)
    params = solr_write_params()
    assert params['commit'] == 'false'
    assert params['commitWithin'] == '10000'


def test_commit_within_window_is_configurable(monkeypatch):
    _clear_write_env(monkeypatch)
    monkeypatch.setenv('VFBQUERY_SOLR_COMMIT_WITHIN_MS', '2500')
    assert solr_write_params()['commitWithin'] == '2500'


@pytest.mark.parametrize('bad', ['0', '-1', 'soon', ''])
def test_a_useless_window_falls_back_rather_than_disabling_visibility(monkeypatch, bad):
    """A non-positive or unparseable window must not mean "never".

    ``commitWithin=0`` is not "commit now" — Solr reads a non-positive value as
    no commitWithin at all, which is exactly the invisible write this change
    exists to remove. Misconfiguration should cost a slightly different latency,
    not reinstate the bug.
    """
    _clear_write_env(monkeypatch)
    monkeypatch.setenv('VFBQUERY_SOLR_COMMIT_WITHIN_MS', bad)
    assert solr_write_params()['commitWithin'] == '10000'


def test_blocking_commit_is_still_available_as_an_escape_hatch(monkeypatch):
    """Bulk warming wants the old behaviour; everything else should not have it.

    ``commit=true`` is a blocking hard flush, and on this deployment it can wedge
    on the write.lock EIO failure mode and surface as a 503 — which is why it is
    opt-in rather than the default.
    """
    _clear_write_env(monkeypatch)
    monkeypatch.setenv('VFBQUERY_SOLR_WRITE_COMMIT', 'true')
    params = solr_write_params()
    assert params == {'commit': 'true'}
    assert 'commitWithin' not in params


class _Recorder:
    """Stands in for ``requests.post`` and keeps what was sent."""

    def __init__(self):
        self.calls = []

    def __call__(self, url, data=None, headers=None, params=None, timeout=None):
        self.calls.append({'url': url, 'data': data, 'params': params})

        class _Response:
            status_code = 200
            text = ''
        return _Response()


def _cache_for_test(monkeypatch):
    _clear_write_env(monkeypatch)
    monkeypatch.delenv('VFBQUERY_CACHE_READONLY', raising=False)
    return src.SolrResultCache(cache_url='http://solr.invalid/cache')


def test_cache_result_actually_posts_commit_within(monkeypatch):
    """Asserting on ``solr_write_params()`` alone would not catch the real bug.

    The defect was never in a helper — it was in the params the write path
    passed. This drives ``cache_result`` and reads what went over the wire.
    """
    cache = _cache_for_test(monkeypatch)
    recorder = _Recorder()
    monkeypatch.setattr(src.requests, 'post', recorder, raising=True)

    assert cache.cache_result('term_info', 'VFB_00000001',
                              {'Name': 'a term', 'count': 3}) is True

    assert len(recorder.calls) == 1
    call = recorder.calls[0]
    assert call['url'] == 'http://solr.invalid/cache/update'
    assert call['params']['commitWithin'] == '10000'
    # And the document really is the one we asked to store.
    assert json.loads(call['data'])[0]['original_term_id'] == 'VFB_00000001'


def test_the_expiry_delete_is_visible_too(monkeypatch):
    """The same bug, on the other write path, with a nastier shape.

    An invisible delete leaves the expired document in place, so it is read back
    and re-expired on every subsequent lookup: the entry can never be replaced,
    only re-condemned.
    """
    cache = _cache_for_test(monkeypatch)
    recorder = _Recorder()
    monkeypatch.setattr(src.requests, 'post', recorder, raising=True)

    cache._clear_expired_cache_document('vfb_query_term_info_VFB_00000001')

    assert len(recorder.calls) == 1
    assert recorder.calls[0]['params']['commitWithin'] == '10000'


# ---------------------------------------------------------------------------
# 2. "Resolved" is not the same question as "count >= 0"
# ---------------------------------------------------------------------------

def _query(count, status=None, **extra):
    preview = dict(extra)
    if status is not None:
        preview['status'] = status
    return {'count': count, 'preview_results': preview}


def test_a_finished_preview_is_resolved():
    assert preview_is_resolved(_query(5, PREVIEW_STATUS_COMPLETE)) is True


def test_zero_matches_is_an_answer():
    """0 is a real result — "we looked, there are none" — and must be cached."""
    assert preview_is_resolved(_query(0, PREVIEW_STATUS_COMPLETE)) is True


def test_a_pending_preview_is_not_resolved():
    assert preview_is_resolved(_query(-1, PREVIEW_STATUS_PENDING)) is False


def test_a_complete_but_uncounted_preview_is_resolved():
    """The third defect, in one line.

    ``count: -1`` here means "more than COUNT_CAP", not "unknown": the rows are
    final. Under the old ``count >= 0`` test this term was refused by the cache
    validator on write *and* on read, so it was recomputed from scratch on every
    request and could never settle.
    """
    assert preview_is_resolved(_query(-1, PREVIEW_STATUS_COMPLETE)) is True


def test_entries_written_before_status_existed_still_read_as_complete():
    """Absence of ``status`` has to keep meaning complete.

    The cache holds three months of entries written before this key existed. If
    a missing ``status`` were read as pending, shipping this would invalidate
    every one of them at once and stampede the whole corpus through a cold
    recompute — turning a correctness fix into an outage.
    """
    assert preview_is_resolved({'count': 7, 'preview_results': {'rows': []}}) is True
    assert preview_is_resolved({'count': -1, 'preview_results': {'rows': []}}) is False


def test_a_query_with_no_preview_block_is_not_resolved():
    assert preview_is_resolved({'count': 5}) is False
    assert preview_is_resolved({'count': 5, 'preview_results': None}) is False


# ---------------------------------------------------------------------------
# 3. The pending state has to say what it is
# ---------------------------------------------------------------------------

def test_blank_previews_are_labelled_pending_and_stay_uncounted():
    """The fast path still blanks previews — it just no longer lies about it.

    ``count`` must remain -1: it is the documented "not counted yet" sentinel and
    the v2 frontend depends on it. What is new is that the payload now *says*
    pending rather than leaving a bare -1 for the consumer to interpret.
    """
    term_info = {'Queries': [
        {'query': 'ListAllAvailableImages',
         'preview_columns': ['id', 'label', 'thumbnail']},
        {'query': 'SimilarNeurons'},
    ]}

    out = vq._blank_query_previews(term_info)

    for query in out['Queries']:
        preview = query['preview_results']
        assert query['count'] == vq.PREVIEW_COUNT_UNKNOWN == -1
        assert preview['status'] == PREVIEW_STATUS_PENDING
        assert preview['rows'] == []
        # The message has to distinguish -1 from 0 in words, because that is
        # precisely the confusion it exists to prevent.
        assert 'not counted' in preview['message']
        assert 'no matches' in preview['message']
        assert preview_is_resolved(query) is False

    # Declared preview columns survive, so a client can render the empty table
    # with its real headers rather than guessing.
    assert out['Queries'][0]['preview_results']['headers'] == \
        ['id', 'label', 'thumbnail']
    assert out['Queries'][1]['preview_results']['headers'] == \
        ['id', 'label', 'tags', 'thumbnail']


def test_the_pending_messages_all_name_the_way_out():
    """Each pending reason points at running the query directly.

    A pending preview is not an error and not a dead end: the number is unknown
    because the query has not been run, and running it is the answer. A message
    that only described the state would leave the caller stuck.
    """
    for message in (vq.PREVIEW_PENDING_NOT_RUN,
                    vq.PREVIEW_PENDING_TIMEOUT,
                    vq.PREVIEW_PENDING_ERROR):
        assert 'not counted' in message
        assert 'no matches' in message
        assert 'run the query' in message.lower()


def test_the_uncounted_complete_message_names_the_cap():
    """"Many" is only useful if the reader knows how many is many."""
    rendered = vq.PREVIEW_COMPLETE_UNCOUNTED.format(cap=vq.COUNT_CAP)
    assert str(vq.COUNT_CAP) in rendered
    assert 'complete' in rendered.lower()
