"""Sphinx configuration for the VFBquery documentation site.

Two things about this repo shape the config, and both are deliberate:

1. **Most of the documentation predates the site.** `README.md`, `CACHING.md`,
   `RELEASING.md`, `schema.md`, `performance.md` and `VFB_QUERIES_REFERENCE.md`
   live at the repo root and are read there, on GitHub, by people who never
   open the docs site. `README.md` in particular is *generated* — the
   `examples` workflow executes its ```python blocks and `update_readme.py`
   rewrites its ```json blocks — so it cannot be moved, renamed or edited to
   suit Sphinx. Instead `_sync_root_docs` copies them into `docs/_root/` at
   build time. Copying rather than `{include}`-ing keeps the links *between*
   them working: `CACHING.md` links to `RELEASING.md` as a sibling, and in
   `_root/` they still are siblings. `docs/_root/` is generated and gitignored.

2. **The server package is heavy, the interesting parts are not.** Installing
   `vfbquery` on the docs builder means navis, psycopg, vfb_connect and a
   `setuptools<58` pin — the exact weight the HTTP API exists to remove. So the
   builder installs only `vfbquery-client` (requests + pandas) for real, and
   reaches `vfbquery.combine` — which imports nothing outside the stdlib — by
   putting `src/` on the path with the heavy siblings mocked. If autodoc ever
   needs a module that genuinely requires a runtime dependency, that is a signal
   the module belongs on the other side of that split, not a reason to install
   the world here.
"""

import os
import shutil
import sys

_DOCS = os.path.abspath(os.path.dirname(__file__))
_REPO = os.path.dirname(_DOCS)

# `vfbquery.combine` (stdlib-only) and the client, so autodoc reads the real
# signatures. The client is normally pip-installed by the builder as well; the
# path entry makes a local `sphinx-build` work in a bare checkout too.
sys.path.insert(0, os.path.join(_REPO, "src"))
sys.path.insert(0, os.path.join(_REPO, "clients", "vfbquery-client", "src"))

# -- Project information -----------------------------------------------------

project = "VFBquery"
author = "Virtual Fly Brain"
copyright = "Virtual Fly Brain, GPL-3.0"

# Single source of truth, same file `setup.py` and `vfbquery.__init__` read —
# see RELEASING.md. Read rather than imported, so the docs version is right
# without importing the package's runtime dependencies.
_version_ns = {}
with open(os.path.join(_REPO, "src", "vfbquery", "_version.py")) as _vf:
    exec(_vf.read(), _version_ns)
release = _version_ns["__version__"]
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]

source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
root_doc = "index"

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    # Parked CI workflow files — see docs/ci/README-ci.md. Not prose.
    "ci/**",
    # Parity/recall harnesses: Python and JS, no prose to render.
    "search-parity/**",
]

# `#some-heading` links inside the copied root documents (schema.md and
# VFB_QUERIES_REFERENCE.md both carry hand-written tables of contents) only
# resolve if MyST generates anchors for those headings.
myst_heading_anchors = 4

# `fail_on_warning` is on, so anything left warning has to be either fixed or
# named here with a reason. There is exactly one:
#
#   misc.highlighting_failure — several of the copied root documents contain
#   ```json fences holding *illustrative* JSON: `"...": "other fields"`,
#   `// same structure as above`, elided arrays. Pygments cannot lex those,
#   which is correct — they are not JSON, they are a description of JSON shaped
#   like it for a human reader. Rewriting them to lex would make them worse
#   documents. The block still renders, unhighlighted.
#
# Note what is deliberately NOT suppressed: broken references and missing
# toctree entries. Those are the warnings the gate exists for.
suppress_warnings = ["misc.highlighting_failure"]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "tasklist",
    "attrs_inline",
    "substitution",
]

myst_substitutions = {
    "release": release,
}

# -- Autodoc -----------------------------------------------------------------

autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

# See the module docstring: the docs builder deliberately does not install the
# server package's runtime dependencies. Anything autodoc'd here must be
# importable with these mocked out.
autodoc_mock_imports = [
    "pysolr",
    "marshmallow",
    "vfb_connect",
    "dataclasses_json",
    "dacite",
    "psycopg",
    "aiohttp",
    "navis",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
}

# -- HTML output -------------------------------------------------------------

html_theme = "furo"
html_title = f"VFBquery {version}"
html_static_path = []

# Furo rather than sphinx-rtd-theme for one concrete reason: several of these
# pages are long single-page references — the /combine reference is ~600 lines
# with a dozen worked examples — and Furo puts the in-page section list in a
# right-hand sidebar that stays visible while you scroll. In rtd-theme the
# in-page headings are folded into the left nav, which is where you go to find
# a *different* page, so on a long reference you lose your place.
html_theme_options = {
    "source_repository": "https://github.com/VirtualFlyBrain/VFBquery/",
    "source_branch": "main",
    "source_directory": "docs/",
}

# -- Copy the repo-root markdown into the source tree ------------------------

# Kept in the order they appear in the toctree, with the destination name
# lower-cased because URLs are nicer that way and nothing links to these by
# path from inside the site — the toctree names them.
_ROOT_DOCS = {
    "README.md": "readme.md",
    "CACHING.md": "caching.md",
    "RELEASING.md": "releasing.md",
    "VFB_QUERIES_REFERENCE.md": "queries-reference.md",
    "schema.md": "schema.md",
    "performance.md": "performance.md",
}

# Links between the copied files, rewritten to the new sibling names. Only
# sibling links exist today (README → CACHING, CACHING → RELEASING,
# RELEASING → CACHING); this dict is what keeps them working after the rename
# and is the one place to extend if a new root document is added.
_LINK_REWRITES = {f"({src}": f"({dst}" for src, dst in _ROOT_DOCS.items()}
_LINK_REWRITES.update({f"({src}#": f"({dst}#" for src, dst in _ROOT_DOCS.items()})


def _drop_leading_transitions(text):
    """Remove a thematic break that sits directly under a heading.

    `VFB_QUERIES_REFERENCE.md` writes several sections as a heading followed
    immediately by `---`. On GitHub that renders as a rule under the heading;
    docutils reads it as a section beginning with a transition, which is not a
    legal document structure, and warns. The rule carries no information a
    heading does not already carry, so the copy drops it.

    Done here rather than by editing the source, because these files are read
    directly on GitHub and one of them (`README.md`) is regenerated by the
    `examples` workflow — a fix applied there would be overwritten.
    """
    lines = text.split("\n")
    out = []
    for index, line in enumerate(lines):
        if line.strip() in ("---", "***", "___"):
            # Look back past blank lines for a heading.
            back = index - 1
            while back >= 0 and not lines[back].strip():
                back -= 1
            if back >= 0 and lines[back].lstrip().startswith("#"):
                continue
        out.append(line)
    return "\n".join(out)


def _sync_root_docs(app=None, config=None):
    """Copy the repo-root markdown files into ``docs/_root/`` for the build.

    Rewrites the links between them to the copied names. Runs on every build so
    a stale copy cannot outlive its source — the destination is wiped first,
    which is safe because nothing but this function ever writes there.
    """
    dest_dir = os.path.join(_DOCS, "_root")
    shutil.rmtree(dest_dir, ignore_errors=True)
    os.makedirs(dest_dir, exist_ok=True)
    for src_name, dest_name in _ROOT_DOCS.items():
        src_path = os.path.join(_REPO, src_name)
        if not os.path.exists(src_path):
            # A missing root document is a real problem (they are all committed),
            # but failing the whole docs build over it would hide which one.
            # Sphinx will report the toctree entry as missing, which names it.
            continue
        with open(src_path, encoding="utf-8") as handle:
            text = handle.read()
        for old, new in _LINK_REWRITES.items():
            text = text.replace(old, new)
        text = _drop_leading_transitions(text)
        with open(os.path.join(dest_dir, dest_name), "w", encoding="utf-8") as handle:
            handle.write(text)


def setup(app):
    # `config-inited` fires before Sphinx enumerates the source files, so the
    # copies exist by the time the toctree is resolved.
    app.connect("config-inited", _sync_root_docs)
    return {"parallel_read_safe": True, "parallel_write_safe": True}


# Also run at import time, so `sphinx-build` invoked oddly (or a tool that only
# imports conf.py to read metadata) still sees a populated `_root/`.
_sync_root_docs()
