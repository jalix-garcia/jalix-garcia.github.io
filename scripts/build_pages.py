"""Build the publication lists from data/publications.toml.

Quarto runs this before every render (see pre-render in _quarto.yml). It writes
Markdown fragments to _generated/, which the pages pull in with
{{< include >}}. Only the Python standard library is used.
"""

import html
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "publications.toml"
OUT = ROOT / "_generated"

TYPE_HEADINGS = {
    "article": "Refereed journal articles",
    "chapter": "Book chapters",
    "report": "Reports and other writing",
}

KNOWN_FIELDS = {
    "title", "with", "venue", "citation", "year", "forthcoming", "doi", "url",
    "manuscript", "links", "theme", "type", "status", "featured", "summary",
    "thumbnail", "thumbnail_alt",
}


def esc(text):
    return html.escape(str(text), quote=True)


def check(data):
    """Stop the render with a readable message if an entry is malformed."""
    themes = {t["id"] for t in data["theme"]}
    problems = []
    for t in data["theme"]:
        image = t.get("image")
        if image and not (ROOT / image).is_file():
            problems.append(f"theme {t['id']}: image file not found: {image}")
    for i, p in enumerate(data["pub"], start=1):
        label = f"entry {i} ({p.get('title', 'no title')[:50]})"
        for key in p:
            if key not in KNOWN_FIELDS:
                problems.append(f"{label}: unknown field '{key}'")
        if "title" not in p:
            problems.append(f"{label}: missing title")
        kind = p.get("type")
        if kind not in {"article", "chapter", "report", "wip"}:
            problems.append(f"{label}: type must be article, chapter, report or wip")
        if kind != "wip":
            if p.get("theme") not in themes:
                problems.append(f"{label}: theme must be one of {sorted(themes)}")
            if "year" not in p:
                problems.append(f"{label}: missing year")
        for field in ("manuscript", "thumbnail"):
            path = p.get(field)
            if path and not (ROOT / path).is_file():
                problems.append(f"{label}: {field} file not found: {path}")
    if problems:
        sys.exit("publications.toml has problems:\n  " + "\n  ".join(problems))


def newest_first(pubs):
    # sorted() is stable, so papers from the same year keep their file order.
    return sorted(pubs, key=lambda p: p.get("year", 0), reverse=True)


def main_link(p):
    if "doi" in p:
        return "https://doi.org/" + p["doi"]
    return p.get("url") or p.get("manuscript")


def meta_line(p):
    parts = []
    if p.get("with"):
        parts.append("with " + esc(p["with"]))
    kind = p["type"]
    if kind == "wip":
        if p.get("status"):
            parts.append(esc(p["status"]))
    else:
        venue = esc(p["venue"])
        if kind == "article":
            venue = f"<em>{venue}</em>"
        elif kind == "chapter":
            venue = f"In <em>{venue}</em>"
        if p.get("citation"):
            sep = ", " if kind == "chapter" else " "
            venue += sep + esc(p["citation"])
        when = "forthcoming" if p.get("forthcoming") else str(p["year"])
        parts.append(f"{venue}, {when}")
    return " · ".join(parts)


def pub_html(p, show_summary=True, show_thumbnail=False):
    title = esc(p["title"])
    href = main_link(p)
    if href:
        title = f'<a href="{esc(href)}">{title}</a>'
    thumb = ""
    if show_thumbnail and p.get("thumbnail"):
        img = (
            f'<img src="{esc(p["thumbnail"])}" '
            f'alt="{esc(p.get("thumbnail_alt", ""))}" loading="lazy">'
        )
        if href:
            img = f'<a href="{esc(href)}" tabindex="-1" aria-hidden="true">{img}</a>'
        thumb = f'<div class="pub-thumb">{img}</div>'
    if thumb:
        out = ['<div class="pub has-thumb">', thumb, '<div class="pub-body">']
    else:
        out = ['<div class="pub">']
    out.append(f'<div class="pub-title">{title}</div>')
    meta = meta_line(p)
    if meta:
        out.append(f'<div class="pub-meta">{meta}</div>')
    if show_summary and p.get("summary"):
        out.append(f'<p class="pub-summary">{esc(p["summary"])}</p>')
    links = []
    if p.get("manuscript"):
        if p["type"] == "wip":
            label = "Paper (PDF)"
        elif p["type"] == "report":
            label = "PDF"
        else:
            label = "Manuscript (PDF)"
        links.append((label, p["manuscript"]))
    links += [(link["label"], link["url"]) for link in p.get("links", [])]
    if links:
        anchors = " ".join(f'<a href="{esc(u)}">{esc(t)}</a>' for t, u in links)
        out.append(f'<div class="pub-links">{anchors}</div>')
    if thumb:
        out.append("</div>")
    out.append("</div>")
    return "\n".join(out)


def html_block(fragments, css_class="pub-list"):
    body = "\n".join(fragments)
    return f'```{{=html}}\n<div class="{css_class}">\n{body}\n</div>\n```\n'


def theme_image(theme, css_class):
    if not theme.get("image"):
        return ""
    focus = theme.get("image_focus", "center")
    return (
        f'<img class="{css_class}" src="{esc(theme["image"])}" '
        f'alt="{esc(theme.get("image_alt", ""))}" loading="lazy" '
        f'style="object-position: {esc(focus)}">'
    )


def build_publications(data):
    pubs = [p for p in data["pub"] if p["type"] != "wip"]
    sections = []
    for theme in data["theme"]:
        in_theme = [p for p in pubs if p["theme"] == theme["id"]]
        sections.append(f'## {theme["name"]} {{#{theme["id"]}}}\n')
        banner = theme_image(theme, "theme-banner")
        if banner:
            sections.append(f"```{{=html}}\n{banner}\n```\n")
        sections.append(f'[{theme["question"]}]{{.theme-question}}\n')
        for kind, heading in TYPE_HEADINGS.items():
            group = newest_first([p for p in in_theme if p["type"] == kind])
            if group:
                sections.append(f"### {heading}\n")
                sections.append(html_block([pub_html(p) for p in group]))
    return "\n".join(sections)


def build_recent(data):
    featured = newest_first([p for p in data["pub"] if p.get("featured")])
    return html_block([pub_html(p, show_thumbnail=True) for p in featured])


def build_themes(data):
    cards = []
    for theme in data["theme"]:
        count = sum(1 for p in data["pub"] if p.get("theme") == theme["id"])
        cards.append(
            f'<a class="theme-card" href="publications.html#{esc(theme["id"])}">'
            + theme_image(theme, "theme-card-img")
            + '<span class="theme-card-body">'
            f'<span class="theme-name">{esc(theme["name"])}</span>'
            f'<span class="theme-question">{esc(theme["question"])}</span>'
            f'<span class="theme-count">{count} publications</span></span></a>'
        )
    return html_block(cards, css_class="theme-grid")


def build_wip(data):
    wip = [p for p in data["pub"] if p["type"] == "wip"]
    return html_block([pub_html(p) for p in wip])


def main():
    with open(DATA, "rb") as f:
        data = tomllib.load(f)
    check(data)
    OUT.mkdir(exist_ok=True)
    pages = {
        "publications.md": build_publications(data),
        "recent.md": build_recent(data),
        "themes.md": build_themes(data),
        "work-in-progress.md": build_wip(data),
    }
    for name, text in pages.items():
        (OUT / name).write_text(text, encoding="utf-8")
    n = sum(1 for p in data["pub"] if p["type"] != "wip")
    print(f"build_pages.py: {n} publications written to _generated/")


if __name__ == "__main__":
    main()
