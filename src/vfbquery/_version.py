"""Single source of truth for the VFBquery package version.

Both ``setup.py`` (read at build time) and ``vfbquery.__init__`` (imported at
runtime) take ``__version__`` from here, and the release workflow bumps only
this file, so the packaging metadata, ``vfbquery.__version__`` and the SOLR
cache's version stamp can never drift apart.
"""

# 1.22.34, not 1.23.0 — deliberately, having first gone the other way.
#
# query_connectivity now expands a neuron type over its subclasses, so the same
# call returns different (correct) rows than it did, and the reflex for that is
# a minor bump: cached entries are namespaced by major.minor, so moving to 1.23
# leaves every stale answer behind instead of serving it. See RELEASING.md.
#
# But that namespace is all-or-nothing, and the blast radius is asymmetric. The
# vfb_json cache holds ~11.2M docs, including the AllAlignedImages entries that
# were expensive enough to need their own gzip work to fit at all (CACHING.md).
# Only 34 of those docs are query_type:query_connectivity — the ones this change
# actually invalidates. Bumping to 1.23 to retire 34 docs orphans the other
# ~11.2M and makes every cold path recompute, which costs far more than it fixes.
#
# So: stay on the 1.22 namespace and retire those 34 entries directly, with a
# delete-by-query on query_type:query_connectivity against the cache collection.
# Targeted invalidation, not a namespace flip. This is the documented exception,
# not a licence to hand-manage the cache in general — the standing rule remains
# force_refresh per call or a major.minor bump, never renaming buckets.
__version__ = "1.22.43"
