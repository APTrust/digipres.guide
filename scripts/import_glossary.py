#!/usr/bin/env python3
"""Import the glossary appendix from a manuscript draft into data/glossary.yaml.

Usage:
    python3 scripts/import_glossary.py content-drafts/<draft>.docx

Needs pandoc (https://pandoc.org/). Re-run it on each new draft; it rewrites
data/glossary.yaml from scratch.

How it finds the glossary: each term is a Heading 1, followed by one Heading 2
per source ("DPC Glossary", "SAA Dictionary", or "FADGI Glossary") with that
source's definition under it. A "Notes" Heading 3 is folded into the
definition. The glossary ends at the first Heading 1 that isn't followed by a
source heading, or at an editorial note in [square brackets].
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from convert_path_data import write_yaml  # noqa: E402  (shared YAML writer)

SOURCES = {
    "DPC Glossary": "dpc",
    "SAA Dictionary": "saa",
    "FADGI Glossary": "fadgi",
}
SOURCE_INFO = {
    "dpc": {"name": "Digital Preservation Coalition, Digital Preservation Handbook glossary",
            "short": "DPC", "url": "https://www.dpconline.org/handbook/glossary"},
    "saa": {"name": "Society of American Archivists, Dictionary of Archives Terminology",
            "short": "SAA", "url": "https://dictionary.archivists.org/"},
    "fadgi": {"name": "Federal Agencies Digital Guidelines Initiative glossary",
              "short": "FADGI", "url": "https://www.digitizationguidelines.gov/glossary.php"},
}
# SAA Dictionary entries live at /entry/<slug>.html. Where the SAA entry's name
# differs from our term, map our term's id to the SAA slug here.
SAA_SLUGS = {"digitization": "digitize"}


def slug(term):
    return re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")


def clean(text):
    text = re.sub(r'<span class="mark">(.*?)</span>', r"\1", text, flags=re.S)  # Word highlighting
    text = re.sub(r"</?u>", "", text)                                          # underlined links
    text = text.replace("(View Citations)", "")                                 # pasted from SAA site
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse(markdown):
    lines = markdown.split("\n")

    def next_nonblank(i):
        for j in range(i + 1, len(lines)):
            if lines[j].strip():
                return lines[j].strip()
        return ""

    terms, term, source, buf = [], None, None, []

    def flush():
        if term is not None and source is not None:
            text = clean("\n".join(buf))
            if text:
                term["definitions"].append({"source": source, "text": text})

    started = False
    for i, line in enumerate(lines):
        h1 = re.match(r"^# (?!#)(.+)$", line)
        h2 = re.match(r"^## (?!#)(.+?)\s*$", line)
        if h1:
            nxt = re.match(r"^## (.+?)\s*$", next_nonblank(i))
            if nxt and nxt.group(1) in SOURCES:
                flush()
                name = clean(h1.group(1)).strip("*")
                term = {"id": slug(name), "term": name, "definitions": []}
                terms.append(term)
                source, buf, started = None, [], True
                continue
            if started:
                break
        if not started:
            continue
        if h2 and h2.group(1) in SOURCES:
            flush()
            source, buf = SOURCES[h2.group(1)], []
        elif re.match(r"^### Notes\s*$", line):
            buf.append("")  # notes run on as more paragraphs of the same definition
        elif line.startswith("\\[") or line.startswith(">"):
            break  # editorial note or block quote after the last term
        else:
            buf.append(line)
    flush()
    return terms


def main(argv):
    if len(argv) != 1:
        sys.exit(__doc__)
    src = Path(argv[0])
    md = subprocess.run(["pandoc", str(src), "-t", "gfm", "--wrap=none"],
                        check=True, capture_output=True, text=True).stdout
    terms = parse(md)
    problems = []
    ids = set()
    for t in terms:
        if t["id"] in ids:
            problems.append(f"'{t['term']}' appears twice.")
        ids.add(t["id"])
        if not t["definitions"]:
            problems.append(f"'{t['term']}' has no definitions.")
        for d in t["definitions"]:
            if d["source"] == "saa":
                d["url"] = f"https://dictionary.archivists.org/entry/{SAA_SLUGS.get(t['id'], t['id'])}.html"
    if not terms:
        problems.append("No glossary found (a Heading 1 term followed by a source Heading 2).")
    if problems:
        print("Problems; no files were changed:\n  - " + "\n  - ".join(problems), file=sys.stderr)
        sys.exit(1)
    terms.sort(key=lambda t: t["term"].lower())
    out = write_yaml("glossary.yaml", {"sources": SOURCE_INFO, "terms": terms}, src.name)
    print(f"wrote {out.relative_to(out.parent.parent)}: {len(terms)} terms, "
          f"{sum(len(t['definitions']) for t in terms)} definitions")


if __name__ == "__main__":
    main(sys.argv[1:])
