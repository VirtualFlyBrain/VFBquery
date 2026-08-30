"""Sphinx configuration for the VFBquery documentation site.

Two things about this repo shape the config, and both are deliberate:

1. **Most of the documentation predates the site.** `README.md`, `CACHING.md`,
   `RELEASING.md`, `schema.md`, `performance.md` and `VFB_QUERIES_REFERENCE.md`
   live at the repo root and are read there, on GitHub, by people who never
   open the docs site. (`README.md` used to be *generated*; the worked
   examples are now a real test, `src/test/test_example_queries.py`, and
   the README is hand-written.) `_sync_root_docs` copies the root
   documents into `docs/_root/` at build time. Copying rather than `{include}`-ing keeps the links *between*
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
import re
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

# -- PDF output --------------------------------------------------------------

# `.readthedocs.yaml` asks for the `pdf` format, so this build runs on RTD
# whether anyone reads the result or not — and with the default pdflatex engine
# it does not merely warn, it stops. These documents are full of characters
# pdflatex has no glyph for and treats as *fatal*:
#
#   * the set-theory notation the /combine reference is written in — ∪ ∩ ⊕ ↔ ≡,
#     and the α/β used for the operand placeholders;
#   * the emoji in the root documents — a few in `README.md`, and 🎉 ✅ ✨ 🔶
#     in `performance.md`, which the `performance-test` workflow regenerates.
#
# Neither source can be cleaned up at the source: the notation is the subject
# matter, and the emoji are rewritten by a workflow on every run. xelatex reads
# UTF-8 natively, so an unrepresentable character degrades to a "Missing
# character" warning and a gap in the page rather than an `Emergency stop`.
latex_engine = "xelatex"

# A gap in the page is still wrong, though, so the two categories are handled
# rather than merely survived: the font choice below covers the notation, and
# `_replace_pictographs` (LaTeX only) rewrites the emoji, which no font shipped
# with TeX Live can set.
latex_elements = {
    # DejaVu where it exists. The default (Latin Modern) and the obvious
    # alternative (TeX Gyre Termes/Heros/Cursor, the URW Times/Helvetica/Courier
    # clones) are typographically nicer and cover none of ∪ ∩ ⊕ ↔ ≡ α β — every
    # one of which is load-bearing in the /combine reference, where "A ∪ B"
    # silently losing its operator turns a definition into a typo. DejaVu has
    # the lot, in all three families, so the symbols come from the running text
    # font rather than needing per-character math escapes in the markdown.
    #
    # Guarded with \IfFontExistsTF because the font is a system font, not a TeX
    # one: RTD's build image has it, a minimal TeX Live may not, and falling
    # back to TeX Gyre gives a PDF with some missing glyphs instead of a build
    # that dies on a font it cannot find.
    "fontpkg": r"""
\usepackage{fontspec}
\IfFontExistsTF{DejaVu Serif}{
  \setmainfont{DejaVu Serif}[Scale=0.9]
  \setsansfont{DejaVu Sans}[Scale=0.9]
  \setmonofont{DejaVu Sans Mono}[Scale=MatchLowercase]
}{
  \setmainfont{TeX Gyre Termes}
  \setsansfont{TeX Gyre Heros}
  \setmonofont{TeX Gyre Cursor}[Scale=MatchLowercase]
}
""",
}

latex_documents = [
    (root_doc, "vfbquery.tex", "VFBquery Documentation", author, "manual"),
]

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
    directly on GitHub and one of them (`performance.md`) is regenerated by a
    workflow — a fix applied there would be overwritten.
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


def _fill_empty_tables(text):
    """Give a header-only markdown table one placeholder row.

    `performance.md` is written by the `performance-test` workflow, and a run
    that records no per-query timings still emits the "Query Performance
    Details" table — header, separator, nothing under it. HTML renders that
    without complaint. The LaTeX builder does not: Sphinx's table writer does
    ``next(node.findall(nodes.tbody))``, and a bodyless table raises
    ``StopIteration``, aborting the whole PDF build with a traceback rather than
    a warning naming the file. Since `.readthedocs.yaml` asks for the PDF
    format, that is a red docs build caused by a workflow run nobody would
    connect to the documentation.

    A row of em dashes rather than dropping the table: the column names are the
    informative part — this run measured Query, Duration and Status and found
    none — and a heading with nothing under it reads as content gone missing.
    """
    lines = text.split("\n")
    out = []
    for index, line in enumerate(lines):
        out.append(line)
        stripped = line.strip()
        # A separator row is pipes, dashes, colons and spaces, nothing else.
        if not (stripped.startswith("|") and "-" in stripped
                and set(stripped) <= set("|-: ")):
            continue
        # It is only a table if a header row precedes it and no row follows.
        if index == 0 or "|" not in lines[index - 1]:
            continue
        following = lines[index + 1] if index + 1 < len(lines) else ""
        if "|" in following:
            continue
        columns = len(stripped.strip("|").split("|"))
        out.append("|" + "|".join(" — " for _ in range(columns)) + "|")
    return "\n".join(out)


# A literal block longer than this is elided in the PDF only — see
# `_elide_long_code_blocks`. 80 lines is about a page and a half of monospace,
# which is already past the point where anybody reads a code block rather than
# skims it, and it leaves an enormous margin under the hard limit that forces
# the elision in the first place.
_LATEX_MAX_CODE_LINES = 80
_LATEX_HEAD_LINES = 55
_LATEX_TAIL_LINES = 10


def _elide_long_code_blocks(text, docname):
    """Shorten very long fenced code blocks. **LaTeX builder only.**

    `README.md` is generated: `update_readme.py` replaces its ```json fences
    with the *actual* output of the examples, and `get_term_info` on a template
    returns every painted domain, so two of those blocks are ~1,100 lines of
    JSON. HTML renders them fine — scrollable, searchable, and skipping them
    costs a flick of the wrist.

    LaTeX does not. Sphinx typesets a literal block inside `framed`, which
    collects the whole thing into a single box so it can be split across pages,
    and a box taller than TeX's `\\maxdimen` (16383.99998pt, about 5.7 metres) is
    a fatal "Dimension too large" — not a warning naming the file, an
    `Emergency stop` partway through the run. At ~11pt a line, and with the long
    URLs in that JSON wrapping to two or three lines each, 1,100 lines clears
    the limit comfortably.

    So the PDF gets the head and tail with a marked gap. This is the one place
    the PDF deliberately differs from the HTML, and it differs where the
    difference costs nothing: 25 pages of `"thumbnail": "https://..."` repeated
    per domain is not something a PDF reader was going to read, and the marker
    says where the whole thing lives. Doing it here, in `source-read`, rather
    than in `_sync_root_docs`, is what keeps it PDF-only — the builder is not
    known yet when the root documents are copied.
    """
    lines = text.split("\n")
    out = []
    fence = None            # the exact opening fence, or None outside a block
    body = []
    for line in lines:
        stripped = line.strip()
        if fence is None:
            # An opening fence: three or more backticks or tildes. The info
            # string may name a language; it never contains the fence char.
            if stripped.startswith("```") or stripped.startswith("~~~"):
                char = stripped[0]
                run = len(stripped) - len(stripped.lstrip(char))
                if char not in stripped[run:]:
                    fence = char * run
                    out.append(line)
                    body = []
                    continue
            out.append(line)
            continue
        # Inside a block: a closing fence is the same char, at least as long,
        # and nothing else on the line.
        if stripped.startswith(fence) and set(stripped) == {fence[0]}:
            if len(body) > _LATEX_MAX_CODE_LINES:
                dropped = len(body) - _LATEX_HEAD_LINES - _LATEX_TAIL_LINES
                out.extend(body[:_LATEX_HEAD_LINES])
                out.append("")
                out.append(
                    f"... [{dropped} lines omitted from the PDF - this block is "
                    f"shown in full in the HTML documentation and in {docname.split('/')[-1]}] ..."
                )
                out.append("")
                out.extend(body[-_LATEX_TAIL_LINES:])
            else:
                out.extend(body)
            out.append(line)
            fence = None
            body = []
            continue
        body.append(line)
    # An unterminated fence is a malformed source file, not something to repair
    # silently — emit it as it was and let the parser report it.
    out.extend(body)
    return "\n".join(out)


# Emoji that carry information rather than decoration, and what they mean in a
# document that cannot show them. `performance.md` is a table of ✅ and ❌ in a
# Status column — dropped rather than translated, that column would come out
# blank and the table would say the opposite of nothing at all.
_PICTOGRAPH_SUBS = {
    "✅": "[OK]",       # ✅
    "✔": "[OK]",       # ✔
    "✓": "[OK]",       # ✓
    "❌": "[FAIL]",     # ❌
    "✗": "[FAIL]",     # ✗
    "⚠": "[!]",        # ⚠
    "⏳": "[...]",      # ⏳
    "⭐": "[*]",        # ⭐
}

# Everything else in the pictograph blocks is decoration — the 🎉 that ends a
# passing perf run, the 🐍 📦 in a heading — and reads better gone than as a
# gap. Ranges rather than a list because these files are generated: a workflow
# can introduce a new emoji at any time, and a list would go stale silently
# while a range keeps working. Deliberately *not* included: U+2190–U+21FF
# (arrows) and U+2200–U+22FF (mathematical operators), which is where ↔ ∪ ∩ ⊕ ≡
# live and which the font above sets properly.
_PICTOGRAPH_RE = re.compile(
    "[" + "".join((
        "☀-➿",        # miscellaneous symbols and dingbats
        "⬀-⯿",        # miscellaneous symbols and arrows
        "\U0001F000-\U0001FAFF",  # emoji proper
    )) + "]"
    # Eat one following space as well, so a dropped leading emoji does not leave
    # a heading indented by a space.
    r" ?"
)

# Stripped first and separately, because they are modifiers rather than
# characters: `⚠️` is `⚠` followed by U+FE0F, and if the selector were dropped by
# the rule above — which also eats a following space — the substitution would
# come out as `[!]warn` instead of `[!] warn`.
_MODIFIER_RE = re.compile("[︎️‍]")

# ATX headings, which are exempt — see `_replace_pictographs`.
_HEADING_RE = re.compile(r"\s{0,3}#{1,6}(\s|$)")


def _replace_pictographs(text):
    """Make emoji printable. **LaTeX builder only.**

    No font shipped with TeX Live has a glyph for ✅ or 🎉 — they are colour
    emoji, which is a different rendering technology, not a missing character
    set. xelatex therefore drops them with a "Missing character" warning, and
    `performance.md` alone accounts for 224 of those: its Status column is
    nothing but ✅. Translating the meaningful ones and deleting the decorative
    ones is the difference between a status table and an empty column.
    """
    out = []
    for line in text.split("\n"):
        # Headings are left exactly as they are. MyST derives a heading's anchor
        # from its text, so `## 🎉 MAJOR MILESTONE` anchors as
        # `#-major-milestone` — with the leading dash the emoji left behind —
        # and `VFB_QUERIES_REFERENCE.md` links to precisely that from its
        # hand-written table of contents. Rewriting the heading moves the anchor
        # and breaks the link, which under `-W` is a failed build; and since the
        # anchor is in the *link*, not the heading, fixing one file is not
        # enough. The cost of the exception is a gap where the emoji was in a
        # heading, against a status column full of them in the body.
        if _HEADING_RE.match(line):
            out.append(line)
            continue
        line = _MODIFIER_RE.sub("", line)
        for char, replacement in _PICTOGRAPH_SUBS.items():
            line = line.replace(char, replacement)
        out.append(_PICTOGRAPH_RE.sub("", line))
    return "\n".join(out)


def _on_source_read(app, docname, source):
    """Apply the PDF-only source transforms.

    `source-read` is the earliest event at which ``app.builder`` exists, which
    is the whole reason these two live here rather than in `_sync_root_docs`:
    both of them make the PDF differ from the HTML, and the HTML is the version
    that should be complete.
    """
    if app.builder.name != "latex":
        return
    text = _elide_long_code_blocks(source[0], docname)
    source[0] = _replace_pictographs(text)


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
        text = _fill_empty_tables(text)
        with open(os.path.join(dest_dir, dest_name), "w", encoding="utf-8") as handle:
            handle.write(text)


def setup(app):
    # `config-inited` fires before Sphinx enumerates the source files, so the
    # copies exist by the time the toctree is resolved.
    app.connect("config-inited", _sync_root_docs)
    # `source-read` rather than `config-inited` for the elision: it is the first
    # point at which `app.builder` exists, and the whole point of that transform
    # is that it applies to one builder.
    app.connect("source-read", _on_source_read)
    return {"parallel_read_safe": True, "parallel_write_safe": True}


# Also run at import time, so `sphinx-build` invoked oddly (or a tool that only
# imports conf.py to read metadata) still sees a populated `_root/`.
_sync_root_docs()
