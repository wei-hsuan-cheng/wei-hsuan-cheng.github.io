#!/usr/bin/env python3
"""Render the robotics_notes repository into the website's Robotics Notes section.

usage: python3 scripts/sync_robotics_notes.py [NOTES_REPO] [--github OWNER/REPO] [--branch main]

NOTES_REPO is a local clone of https://github.com/wei-hsuan-cheng/robotics_notes (default ~/src/robotics_notes).
Its README's "Repository Layout" list is the index: every .md note it links becomes a page in _robotics_notes/
(/robotics-notes/<note>/), and /robotics-notes/ (_pages/robotics-notes.md) shows the README's introduction and that
same tree as its table of contents, linking to the pages.

The notes are written for GitHub's Markdown (CommonMark, GitHub tables, $ and $$ math, Markdown inside <details>).
kramdown, the site's Markdown engine, reads several of these differently, so the notes are rendered here with
markdown-it-py, which follows the same CommonMark rules as GitHub, and the pages hold the resulting HTML. Math is
written as \\( \\) and \\[ \\] for the site's MathJax. Images and links to other files of the repository point at
GitHub; links between notes stay on the site.

Needs: pip install markdown-it-py mdit-py-plugins
Rerun after changing the notes, then build the site and commit _robotics_notes/ and _pages/robotics-notes.md.
"""
import argparse
import html
import json
import posixpath
import re
import shutil
from pathlib import Path

from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin

SITE = Path(__file__).resolve().parents[1]
OUT_DIR = SITE / "_robotics_notes"
INDEX_PAGE = SITE / "_pages" / "robotics-notes.md"
URL = "/robotics-notes/"

# One-line descriptions for the index where the note's opening paragraph does not summarize it.
DESCRIPTIONS = {
    "mpc/solver/slq_mpc.md": (
        "Discrete-time nonlinear optimal control solved by repeated linearization, a Riccati-style backward pass "
        "and a line-searched forward rollout, run in a receding-horizon MPC loop."
    ),
}


def github_slug(text):
    """GitHub's heading anchors: lowercase, punctuation dropped (letters, digits, '_' and '-' kept), spaces to '-'."""
    return re.sub(r"[^\w\- ]", "", text.strip().lower()).replace(" ", "-")


def parse_index(readme):
    """[(categories, title, path)] in README order from the "Repository Layout" nested list."""
    lines = readme.splitlines()
    start = next(i for i, line in enumerate(lines) if re.match(r"#+\s+Repository Layout", line))
    notes, stack = [], []
    for line in lines[start + 1:]:
        if re.match(r"#+\s", line):
            break
        item = re.match(r"^(\s*)[-*+]\s+(.*)$", line)
        if not item:
            continue
        depth = len(item.group(1).expandtabs(4)) // 2
        text = item.group(2).strip()
        link = re.match(r"\[([^\]]+)\]\(([^)]+\.md)\)", text)
        stack = stack[:depth]
        if link:
            notes.append((list(stack), link.group(1), link.group(2)))
        else:
            stack.append(text)
    return notes


def make_renderer():
    md = MarkdownIt("commonmark", {"html": True}).enable(["table", "strikethrough"])
    md.use(dollarmath_plugin, allow_space=True, allow_digits=True, double_inline=True)
    md.use(anchors_plugin, min_level=1, max_level=6, slug_func=github_slug)

    def inline(self, tokens, idx, options, env):
        return '<span class="math inline">\\(' + html.escape(tokens[idx].content) + "\\)</span>"

    def display(self, tokens, idx, options, env):
        return '<span class="math display">\\[' + html.escape(tokens[idx].content) + "\\]</span>"

    def block(self, tokens, idx, options, env):
        return '<div class="math display">\\[' + html.escape(tokens[idx].content) + "\\]</div>\n"

    md.add_render_rule("math_inline", inline)
    md.add_render_rule("math_inline_double", display)
    md.add_render_rule("math_block", block)
    md.add_render_rule("math_block_label", block)
    return md


def rewrite(url, note_path, notes_by_path, github, branch, image):
    """Site URL for a link or image of the note at note_path."""
    if not url or re.match(r"^([a-z][a-z0-9+.-]*:|#)", url, re.I):
        return url
    target, _, fragment = url.partition("#")
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(note_path), target.lstrip("/")))
    fragment = "#" + fragment if fragment else ""
    if resolved in notes_by_path:
        return URL + notes_by_path[resolved] + "/" + fragment
    if image:
        return f"https://raw.githubusercontent.com/{github}/{branch}/{resolved}"
    return f"https://github.com/{github}/blob/{branch}/{resolved}{fragment}"


def inline_text(token):
    return "".join(child.content for child in (token.children or []) if child.type in ("text", "code_inline"))


def description(tokens, md):
    """The first sentence of the note's first prose paragraph, as kramdown Markdown (math as $$ $$)."""
    depth = 0
    for i, token in enumerate(tokens):
        if token.type in ("bullet_list_open", "ordered_list_open", "blockquote_open"):
            depth += 1
        elif token.type in ("bullet_list_close", "ordered_list_close", "blockquote_close"):
            depth -= 1
        elif token.type == "inline" and depth == 0 and tokens[i - 1].type == "paragraph_open":
            parts = []
            for child in token.children:
                if child.type == "text":
                    parts.append(child.content)
                elif child.type == "code_inline":
                    parts.append("`" + child.content + "`")
                elif child.type in ("math_inline", "math_inline_double"):
                    parts.append("$$" + child.content + "$$")
                elif child.type in ("strong_open", "strong_close"):
                    parts.append("**")
                elif child.type in ("softbreak", "hardbreak"):
                    parts.append(" ")
            text = re.sub(r"\s*\[\d+\]\s*", " ", "".join(parts))  # citation markers left by <a> tags
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) < 40:
                continue
            sentence = re.match(r"^(.+?[.!?])(\s|$)", text)
            text = sentence.group(1) if sentence else text
            return text[:-1] + "." if text.endswith(":") else text
    return ""


def render_note(path, title, repo, notes_by_path, github, branch, md):
    source = (repo / path).read_text()
    source = re.sub(r"\A\s*#\s+.*\n", "", source, count=1)  # the title is the page's
    # \( \) and \[ \] are Markdown escapes (GitHub shows them as plain brackets); outside code they mean math here.
    parts = re.split(r"(^\s*```.*?^\s*```[^\n]*$|`[^`\n]*`)", source, flags=re.M | re.S)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"\\\[(.+?)\\\]", lambda m: "$$" + m.group(1) + "$$", parts[i], flags=re.S)
        parts[i] = re.sub(r"\\\((.+?)\\\)", lambda m: "$" + m.group(1).strip() + "$", parts[i], flags=re.S)
    source = "".join(parts)
    env = {}
    tokens = md.parse(source, env)
    for token in tokens:
        for child in token.children or []:
            if child.type == "image":
                child.attrSet("src", rewrite(child.attrGet("src"), path, notes_by_path, github, branch, True))
            elif child.type == "link_open":
                child.attrSet("href", rewrite(child.attrGet("href"), path, notes_by_path, github, branch, False))
    body = md.renderer.render(tokens, md.options, env)

    # Contents: the note's sections (h1 after the title, and h2) with their GitHub-style anchors.
    toc = []
    for i, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag in ("h1", "h2"):
            label = md.renderer.renderInline(tokens[i + 1].children, md.options, env)
            label = re.sub(r"<a [^>]*>(.*?)</a>", r"\1", label)
            toc.append(f'<li><a href="#{token.attrGet("id")}">{label}</a></li>')
    toc_html = ""
    if len(toc) >= 3:
        toc_html = "<p><strong>Contents</strong></p>\n<ul>\n" + "\n".join(toc) + "\n</ul>\n<hr />\n"
    return body, toc_html, description(tokens, md)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("repo", nargs="?", type=Path, default=Path.home() / "src" / "robotics_notes")
    parser.add_argument("--github", default="wei-hsuan-cheng/robotics_notes", help="OWNER/REPO for image and file links")
    parser.add_argument("--branch", default="main")
    args = parser.parse_args()
    repo = args.repo.expanduser().resolve()
    readme = (repo / "README.md").read_text()
    index = parse_index(readme)
    if not index:
        raise SystemExit(f"no notes listed under 'Repository Layout' in {repo / 'README.md'}")
    notes_by_path = {posixpath.normpath(path): Path(path).stem.replace("_", "-") for _, _, path in index}
    md = make_renderer()

    shutil.rmtree(OUT_DIR, ignore_errors=True)
    OUT_DIR.mkdir()
    entries = []
    for order, (categories, short_title, path) in enumerate(index, start=1):
        path = posixpath.normpath(path)
        name = notes_by_path[path]
        first_line = next((line for line in (repo / path).read_text().splitlines() if line.strip()), "")
        title = first_line[2:].strip() if first_line.startswith("# ") else short_title
        body, toc, summary = render_note(path, title, repo, notes_by_path, args.github, args.branch, md)
        summary = DESCRIPTIONS.get(path, summary)
        source_url = f"https://github.com/{args.github}/blob/{args.branch}/{path}"
        front = {
            "title": title,
            "collection": "robotics_notes",
            "permalink": URL + name + "/",
            "excerpt": summary,
            "categories_path": " / ".join(categories),
            "order": order,
            "source": source_url,
        }
        page = ["---"] + [f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in front.items()] + ["---", ""]
        page += [
            "{% raw %}",
            f'<p class="notice--info">Rendered from <a href="{source_url}"><i class="fab fa-github" aria-hidden="true"></i> '
            f'{args.github.split("/")[-1]}/{path}</a>.</p>',
            "",
            toc,
            body,
            "{% endraw %}",
            "",
        ]
        (OUT_DIR / f"{name}.html").write_text("\n".join(page))
        entries.append((categories, title, name, summary))
        print(f"{URL}{name}/  <-  {path}")

    # The index page: the README's introduction and its tree as the table of contents, linking to the pages.
    intro = readme.split("## Repository Layout")[0].split("\n", 1)[1].strip()
    layout = readme.split("## Repository Layout", 1)[1]
    layout = re.split(r"^#+\s", layout, maxsplit=1, flags=re.M)[0].strip("\n")

    def site_link(match):
        path = posixpath.normpath(match.group(2))
        return f"[{match.group(1)}]({URL}{notes_by_path[path]}/)" if path in notes_by_path else match.group(0)

    toc = re.sub(r"\[([^\]]+)\]\(([^)]+\.md)\)", site_link, layout)
    lines = ["---", 'title: "Robotics Notes"', f"permalink: {URL}", "author_profile: true", "---", "",
             "<!-- Generated by scripts/sync_robotics_notes.py from the robotics_notes README; edit there and rerun. -->", "",
             ("These notes document my robotics learning journey. While AI steals the spotlight, I still believe in embracing "
              "the math behind robotics: a solid theoretical foundation is what points research in the right direction, "
              "and what builds real insight and taste."), "",
             intro, "", f"The notes live in [{args.github.split('/')[-1]}](https://github.com/{args.github}).", "",
             "## Table of Contents", "", toc]
    INDEX_PAGE.write_text("\n".join(lines) + "\n")
    print(f"{URL}  <-  {len(entries)} notes")


if __name__ == "__main__":
    main()
