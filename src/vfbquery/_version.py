"""Single source of truth for the VFBquery package version.

Both ``setup.py`` (read at build time) and ``vfbquery.__init__`` (imported at
runtime) take ``__version__`` from here, and the release workflow bumps only
this file, so the packaging metadata, ``vfbquery.__version__`` and the SOLR
cache's version stamp can never drift apart.
"""

__version__ = "1.22.14"
