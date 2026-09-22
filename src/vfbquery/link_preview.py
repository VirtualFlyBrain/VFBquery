"""Link-preview page for a VFB term: the HTML an unfurler sees.

Slack, Bluesky, Teams, Discord and the rest build a link card from the
``og:*`` / ``twitter:*`` tags in a page's raw HTML; none of them run
JavaScript. The Geppetto viewer sets those tags per term only from JS, so a
pasted viewer link unfurls as the site logo. This renders the same tags
server-side from ``get_term_info`` so a proxy can hand them to an unfurler
instead -- and a human who lands here anyway is sent on to the viewer.

The title and description logic mirrors ``pageMetadata.js`` in geppetto-vfb
so a term reads the same wherever its preview is built.
"""

import html
import re

SITE_NAME = "Virtual Fly Brain"
VIEWER_BASE = "https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto"
REPORTS_BASE = "https://virtualflybrain.org/reports/"
DEFAULT_IMAGE = "https://www.virtualflybrain.org/favicons/vfb-logo-512.png"
MAX_DESCRIPTION = 300

_MARKDOWN_LINK = re.compile(r"\[([^\]]*)\]\([^)\s]*\)")
_ID_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+$")


def is_term_id(value):
    """True for the id shapes VFB uses (FBbt_00003748, VFB_jrchjrch, ...)."""
    return bool(value) and bool(_ID_PATTERN.match(value))


def strip_markdown(text):
    if not isinstance(text, str):
        return ""
    text = _MARKDOWN_LINK.sub(r"\1", text)
    text = re.sub(r"[*`]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def truncate(text, limit=MAX_DESCRIPTION):
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    space = cut.rfind(" ")
    return (cut[:space] if space > limit * 0.6 else cut) + "…"


def first_thumbnail(info):
    """First thumbnail across Images then Examples, whatever the template."""
    for group in (info.get("Images"), info.get("Examples")):
        if not isinstance(group, dict):
            continue
        for images in group.values():
            if isinstance(images, list) and images and isinstance(images[0], dict):
                thumbnail = images[0].get("thumbnail")
                if thumbnail:
                    return thumbnail
    return None


def kind_of(info):
    if info.get("IsTemplate"):
        return "template"
    if info.get("IsIndividual"):
        return "image"
    if info.get("IsClass"):
        return "class"
    return "term"


def build_title(info):
    return f"{info.get('Name', '')} [{info.get('Id', '')}] - {SITE_NAME}"


def build_description(info):
    meta = info.get("Meta") or {}
    name = info.get("Name", "")
    parts = []
    description = strip_markdown(meta.get("Description"))
    if description:
        parts.append(description)
    # Types is ';'-separated; ", " (not ",") so the sentence reads as a list.
    # pageMetadata.js still uses "," here -- worth aligning on its next release.
    types = strip_markdown((meta.get("Types") or "").replace(";", ", "))
    if types and info.get("IsIndividual"):
        parts.append(f"{name} is an instance of {types}.")
    if not description:
        comment = strip_markdown(meta.get("Comment"))
        if comment:
            parts.append(comment + ".")
        technique = info.get("Technique")
        if isinstance(technique, list) and technique:
            parts.append("Imaged by " + ", ".join(technique) + ".")
        tags = info.get("Tags")
        if not parts and isinstance(tags, list) and tags:
            parts.append(f"{name} (" + ", ".join(tags).replace("_", " ") + ").")
        parts.append(
            f"View the 3D image, annotations and queries for this {kind_of(info)} on {SITE_NAME}."
        )
    return truncate(" ".join(parts))


def preview_metadata(info):
    """The fields a preview page or card needs, as plain strings."""
    term_id = info.get("Id", "")
    return {
        "id": term_id,
        "title": build_title(info),
        "description": build_description(info),
        "image": first_thumbnail(info) or DEFAULT_IMAGE,
        "url": REPORTS_BASE + term_id,
        "viewer_url": f"{VIEWER_BASE}?id={term_id}",
    }


def render_preview_html(info):
    """A self-contained page carrying the term's link-preview tags.

    Everything an unfurler reads is in the head; the body is a one-line
    fallback for the odd human, with a meta-refresh into the viewer so they
    still land where the link pointed. Values are HTML-escaped: names and
    descriptions come from ontology text and can contain anything.
    """
    m = {key: html.escape(str(value), quote=True) for key, value in preview_metadata(info).items()}
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{m['title']}</title>
<meta name="description" content="{m['description']}">
<link rel="canonical" href="{m['url']}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{html.escape(SITE_NAME)}">
<meta property="og:title" content="{m['title']}">
<meta property="og:description" content="{m['description']}">
<meta property="og:url" content="{m['url']}">
<meta property="og:image" content="{m['image']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{m['title']}">
<meta name="twitter:description" content="{m['description']}">
<meta name="twitter:image" content="{m['image']}">
<meta http-equiv="refresh" content="0; url={m['viewer_url']}">
</head>
<body>
<p><a href="{m['viewer_url']}">{m['title']}</a></p>
</body>
</html>
"""
