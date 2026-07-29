"""Single source of truth for the VFBquery package version.

Both ``setup.py`` (read at build time) and ``vfbquery.__init__`` (imported at
runtime) take ``__version__`` from here, and the release workflow bumps only
this file, so the packaging metadata, ``vfbquery.__version__`` and the SOLR
cache's version stamp can never drift apart.
"""

# 1.23.0, not 1.22.34: query_connectivity now expands a neuron type over its
# subclasses, so the same call returns different (correct) rows than it did.
# Cached entries are namespaced by major.minor precisely so an output change
# leaves the old ones behind instead of serving them. See RELEASING.md.
__version__ = "1.23.0"
