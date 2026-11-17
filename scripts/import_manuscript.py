#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Import the toolkit manuscript (.docx) into one Markdown page per section.

Usage:
    python3 scripts/import_manuscript.py content-drafts/<draft>.docx [--out DIR]

Needs pandoc (https://pandoc.org/).

By default the pages go to private/content/ and the figures to
private/static/media/manuscript/. private/ is ignored by git, so the toolkit
text stays out of the public repository and off the public site until the team
decides to publish it. Preview it locally with:

    hugo server --config hugo.toml,hugo.private.toml

To publish at launch, run with --out content to write into the site itself.

How pages are split: SECTION_MAP below lists, in manuscript order, each
heading (or bold-only paragraph, used as a heading in the draft) that starts a
page, and the page's ID. The ID is the page's URL and matches the section IDs on
the path data sheet's Sections tab. Everything up to the next listed heading
belongs to that page. When the final manuscript renames a heading, update the
heading text here and keep the ID, so the URL doesn't change.

The glossary appendix is handled by scripts/import_glossary.py; this script
stops where the glossary begins.
"""
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (heading text, page id). Heading text is matched ignoring case, bold markers,
# curly quotes, and trailing spaces. "{phase}" means the phase being imported.
# "<phase>/_index" pages keep the front matter of the committed placeholder.
SECTION_MAP = [
    ("Digital Preservation Crash Course (LEARN)", "learn/_index"),
    ("What is digital preservation?", "learn/what-is-digital-preservation"),
    ("Why is digital preservation so important?", "learn/why-it-matters"),
    ("Digital Preservation is a strategy, not a tool", "learn/strategy-not-a-tool"),
    ("Types of digital preservation systems", "learn/types-of-systems"),
    ("The Digital Preservation Community", "learn/community"),
    ("Getting READY for Digital Preservation", "ready/_index"),
    ("Building Digital Preservation Knowledge, Skills, and Abilities", "ready/knowledge-skills"),
    ("Organizing Files Into Preservation Objects", "ready/organizing-files"),
    ("Tools and Workflows for Digital Preservation", "ready/tools-and-workflows"),
    ("Documentation and Record Keeping", "ready/documentation"),
    ("Risk Management and Prioritization", "ready/risk-management"),
    ("Disaster Recovery and Business Continuity", "ready/disaster-recovery"),
    ("Policies and Policy Frameworks", "ready/policies"),
    ("Start Doing", "curate/_index"),
    ("Prepare", "curate/prepare"),
    ("Curate", "curate/curate"),
    ("Check", "curate/check"),
    ("Transfer", "curate/transfer"),
    ("Save & Maintain", "curate/save-and-maintain"),
    ("Storage", "curate/storage"),
    ("Reviewing Learning Objectives", "curate/learning-objectives"),
    ("What's in your Toolbox?", "curate/toolbox"),
    ("Keep Doing Digital Preservation", "preserve/_index"),
    ("Reappraisal", "preserve/reappraisal"),
    ("Deaccession", "preserve/deaccession"),
    ("Future migrations", "preserve/future-migrations"),
    ("Checking Integrity Over Time", "preserve/checking-integrity"),
    ("Restoring a corrupted file", "preserve/restoring-a-file"),
    ("Program Benchmarking", "preserve/program-benchmarking"),
    ("Conclusion", "conclusion"),
    ("Works Cited", "works-cited"),
    # Appears once per phase; becomes that phase's further-resources page.
    ("Further Resources with Annotation", "{phase}/further-resources"),
]
GLOSSARY_SOURCES = {"dpc glossary", "saa dictionary", "fadgi glossary"}


def norm(s):
    s = s.replace("**", "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


MAP = {}
for heading, pid in SECTION_MAP:
    MAP[norm(heading)] = pid


def unwrap_link(m):
    text, url = m.group(1), m.group(2)
    if "zotero.org/google-docs" in url:
        return text  # Zotero citation placeholders: keep the citation text only
    if "safelinks.protection.outlook.com" in url:
        q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        url = q.get("url", [url])[0]
    return f"[{text}]({url})"


def clean(text, stats):
    stats["highlights"] += len(re.findall(r'<span class="mark">', text))
    text = re.sub(r'<span class="mark">(.*?)</span>', r"\1", text, flags=re.S)
    text = re.sub(r"</?u>", "", text)
    text = text.replace("<!-- -->", "")
    # Word soft line breaks (Shift+Enter) at the end of bold or italic text come
    # out of pandoc as "**Title\**", which Markdown reads as a literal asterisk.
    # Move the line break outside the emphasis: "**Title**\".
    text = re.sub(r"\\(\*{1,3})$", r"\1\\", text, flags=re.M)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", unwrap_link, text)

    def img(m):
        name = Path(m.group(1)).name
        stats["images"].append(name)
        return f"![](/media/manuscript/{name})"

    text = re.sub(r'<img src="([^"]+)"[^>]*/?>', img, text)
    lines = [l for l in text.split("\n") if l.strip() not in ("\\", "-")]  # Word page-break leftovers
    text = "\n".join(lines)
    text = re.sub(r"[ \t]+\n", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def split_footnotes(md):
    """Return (body, {label: definition line}). pandoc puts definitions at the end."""
    defs = {}
    body = []
    for line in md.split("\n"):
        m = re.match(r"^\[\^([^\]]+)\]: (.*)$", line)
        if m:
            defs[m.group(1)] = m.group(2)
        else:
            body.append(line)
    return "\n".join(body), defs


def front_matter_of(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else None


def yaml_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    out_root = ROOT / "private"
    if "--out" in argv:
        i = argv.index("--out")
        out_root = None
        content_dir = (ROOT / argv[i + 1]).resolve()
        args = [a for a in args if a != argv[i + 1]]
    if len(args) != 1:
        sys.exit(__doc__)
    src = Path(args[0])
    if out_root is not None:
        content_dir = out_root / "content"
        media_dir = out_root / "static" / "media" / "manuscript"
    else:
        media_dir = ROOT / "static" / "media" / "manuscript"

    with tempfile.TemporaryDirectory() as tmp:
        md = subprocess.run(["pandoc", str(src), "-t", "gfm", "--wrap=none", f"--extract-media={tmp}"],
                            check=True, capture_output=True, text=True).stdout
        md, footnotes = split_footnotes(md)
        lines = md.split("\n")

        pages = {}      # id -> {"title", "level", "lines", "order"}
        order = []
        current = None
        phase = None
        heading_level = 0
        intro, in_intro = [], True
        unmapped = []

        def next_nonblank(i):
            for j in range(i + 1, len(lines)):
                if lines[j].strip():
                    return lines[j].strip()
            return ""

        for i, line in enumerate(lines):
            h = re.match(r"^(#{1,6}) (.+?)\s*$", line)
            bold = re.match(r"^\*\*([^*]+)\*\*\s*$", line)
            text = h.group(2) if h else bold.group(1) if bold else None

            if h and len(h.group(1)) == 1 and norm(next_nonblank(i).lstrip("#")) in GLOSSARY_SOURCES:
                break  # the glossary appendix starts here

            if in_intro:
                if line.startswith("\\_\\_\\_"):
                    in_intro = False  # the rule after the introduction; working notes follow
                    continue
                if i > 0:  # line 0 is the book title
                    intro.append(line)
                continue

            pid = MAP.get(norm(text)) if text else None
            if pid:
                if pid.startswith("{phase}"):
                    if not phase:
                        continue
                    pid = pid.replace("{phase}", phase)
                if "/" in pid:
                    phase = pid.split("/")[0]
                elif pid in ("conclusion", "works-cited"):
                    phase = None
                if pid in pages:
                    print(f"warning: '{text}' starts '{pid}' a second time; appending", file=sys.stderr)
                else:
                    pages[pid] = {"title": text.replace("**", "").strip(), "lines": [], "order": len(order)}
                    order.append(pid)
                current = pid
                heading_level = len(h.group(1)) if h else 2
                continue

            if current is None:
                continue  # outline and working notes before the first section
            if h:
                lvl = max(2, len(h.group(1)) - heading_level + 1)
                if len(h.group(1)) <= 2:
                    unmapped.append(f"{current}: '{h.group(2).strip()}'")
                line = "#" * lvl + " " + h.group(2).replace("**", "").strip()
            pages[current]["lines"].append(line)

        pages["introduction"] = {"title": "Introduction", "lines": intro, "order": -1}
        order.insert(0, "introduction")

        # Fresh output each run.
        if out_root is not None and content_dir.exists():
            shutil.rmtree(content_dir)
        if media_dir.exists():
            shutil.rmtree(media_dir)

        stats = {"highlights": 0, "images": []}
        written = []
        for weight, pid in enumerate(order, start=1):
            page = pages[pid]
            body = clean("\n".join(page["lines"]), stats)
            used = []
            for label in re.findall(r"\[\^([^\]]+)\]", body):
                if label not in used:
                    used.append(label)
            missing = [l for l in used if l not in footnotes]
            if missing:
                print(f"warning: {pid} cites footnote(s) {missing} with no definition", file=sys.stderr)
            notes = "\n\n".join(f"[^{l}]: {clean(footnotes[l], stats)}" for l in used if l in footnotes)
            if pid.endswith("/_index"):
                committed = ROOT / "content" / f"{pid}.md"
                fm = front_matter_of(committed) if committed.exists() else f"title: {yaml_str(page['title'])}"
                path = content_dir / f"{pid}.md"
            else:
                fm = f"title: {yaml_str(page['title'])}\nweight: {weight}\nimported_from: {yaml_str(src.name)}"
                path = content_dir / f"{pid}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"---\n{fm}\n---\n\n{body}\n" + (f"\n{notes}\n" if notes else ""), encoding="utf-8")
            written.append(pid)

        media_dir.mkdir(parents=True, exist_ok=True)
        for name in stats["images"]:
            found = list(Path(tmp).rglob(name))
            if found:
                shutil.copy(found[0], media_dir / name)
            else:
                print(f"warning: image {name} not found in the .docx", file=sys.stderr)

    # Report
    print(f"wrote {len(written)} pages to {content_dir.relative_to(ROOT)}/ and "
          f"{len(stats['images'])} figures to {media_dir.relative_to(ROOT)}/")
    not_found = [h for h, pid in SECTION_MAP if pid not in pages and not pid.startswith("{phase}")]
    for h in not_found:
        print(f"warning: heading '{h}' wasn't found in this draft", file=sys.stderr)
    sections_yaml = ROOT / "data" / "sections.yaml"
    if sections_yaml.exists():
        ids = re.findall(r'id: "([^"]+)"', sections_yaml.read_text(encoding="utf-8"))
        for sid in ids:
            if sid not in pages:
                print(f"warning: section '{sid}' from the path data has no imported page; "
                      f"its placeholder stays", file=sys.stderr)
    if stats["highlights"]:
        print(f"note: removed Word highlighting from {stats['highlights']} passage(s)")
    if stats["images"]:
        print(f"note: {len(stats['images'])} figure(s) have no alt text yet")
    for u in unmapped:
        print(f"note: subheading kept inside {u}")


if __name__ == "__main__":
    main(sys.argv[1:])
