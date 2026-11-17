#!/usr/bin/env python3
"""Convert the path data workbook (.xlsx) into the site's data files.

Usage:
    python3 scripts/convert_path_data.py path/to/path-data.xlsx [--stubs]

Download the team's Google Sheet as .xlsx (File > Download > Microsoft Excel)
and run this from the repository root. It rewrites, from scratch:

    data/paths.yaml     levels, situations with their steps, framing copy
    data/tools.yaml     the Tools tab
    data/storage.yaml   the Storage options tab
    data/sections.yaml  the Sections tab

Re-run it whenever the sheet changes; rows added, edited, or deleted in the
sheet are added, edited, or deleted on the site. Before writing anything it
checks every cross-reference (situation, level, section, tool, and storage IDs)
and stops with a list of problems, naming the tab and row, if any are wrong.

--stubs also creates a placeholder page in content/ for any section on the
Sections tab that doesn't have a page yet, so path links always resolve.
Existing pages are never touched.

Uses only the Python standard library.
"""
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SECTION_RE = re.compile(r"^(learn|ready|curate|preserve)/[a-z0-9]+(-[a-z0-9]+)*$")
ROOT = Path(__file__).resolve().parent.parent

errors = []


def err(tab, row, msg):
    errors.append(f"{tab}, row {row}: {msg}")


# ---------------------------------------------------------------- reading xlsx

def col_index(ref):
    """'C12' -> 2"""
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group():
        n = n * 26 + ord(ch) - 64
    return n - 1


def text_of(el):
    """All <t> text under an element (handles rich-text runs)."""
    return "".join(t.text or "" for t in el.iter(f"{{{NS['m']}}}t"))


def read_workbook(path):
    """Return {sheet title: [[cell values as strings], ...]}."""
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
                shared.append(text_of(si))
        rels = {
            r.get("Id"): r.get("Target")
            for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels")).findall("rel:Relationship", NS)
        }
        sheets = {}
        for s in ET.fromstring(z.read("xl/workbook.xml")).find("m:sheets", NS):
            target = rels[s.get(f"{{{NS['r']}}}id")].lstrip("/")
            target = target if target.startswith("xl/") else "xl/" + target
            rows = []
            for row in ET.fromstring(z.read(target)).iter(f"{{{NS['m']}}}row"):
                rnum = int(row.get("r"))
                while len(rows) < rnum - 1:
                    rows.append([])
                vals = []
                for c in row.findall("m:c", NS):
                    i = col_index(c.get("r"))
                    t = c.get("t")
                    v = c.find("m:v", NS)
                    if t == "s":
                        val = shared[int(v.text)] if v is not None else ""
                    elif t == "inlineStr":
                        val = text_of(c)
                    elif t == "b":
                        val = "TRUE" if v is not None and v.text == "1" else "FALSE"
                    else:
                        val = v.text if v is not None else ""
                    while len(vals) <= i:
                        vals.append("")
                    vals[i] = (val or "").strip()
                rows.append(vals)
            sheets[s.get("name")] = rows
    return sheets


def records(sheets, tab, columns):
    """Rows of a tab as dicts keyed by our names, looked up by header text.
    `columns` maps our key -> the header's leading text in the sheet.
    Fully blank rows are skipped. Each record carries its sheet row number."""
    if tab not in sheets:
        errors.append(f"The workbook has no '{tab}' tab.")
        return []
    rows = sheets[tab]
    header = [h.strip().lower() for h in (rows[0] if rows else [])]
    idx = {}
    for key, label in columns.items():
        found = [i for i, h in enumerate(header) if h.startswith(label.lower())]
        if not found:
            errors.append(f"{tab}: no column whose header starts with '{label}'.")
            return []
        idx[key] = found[0]
    out = []
    for n, row in enumerate(rows[1:], start=2):
        rec = {k: (row[i] if i < len(row) else "") for k, i in idx.items()}
        if not any(rec.values()):
            continue
        rec["_row"] = n
        out.append(rec)
    return out


def split_ids(s):
    return [x.strip() for x in s.split(",") if x.strip()]


def as_int(tab, row, s):
    try:
        f = float(s)
        if f.is_integer():
            return int(f)
    except ValueError:
        pass
    err(tab, row, f"Step # must be a whole number, not '{s}'.")
    return None


def check_id(tab, row, value, label, pattern=ID_RE):
    if not value:
        err(tab, row, f"{label} is empty.")
    elif not pattern.match(value):
        err(tab, row, f"{label} '{value}' must use only lowercase letters, numbers, and hyphens.")


def unique(tab, recs, key, label):
    seen = {}
    for r in recs:
        v = r[key]
        if v and v in seen:
            err(tab, r["_row"], f"{label} '{v}' is already used on row {seen[v]}.")
        seen.setdefault(v, r["_row"])


# ---------------------------------------------------------------- converting

def convert(sheets):
    levels = records(sheets, "Levels", {
        "id": "level_id", "title": "Title", "budget": "Budget", "staff_time": "Staff time",
        "it_access": "IT access", "copies_goal": "Copies goal"})
    situations = records(sheets, "Situations", {
        "id": "situation_id", "title": "Title", "description": "One-line description",
        "owner": "Owner", "status": "Status", "effort": "Rough effort"})
    steps = records(sheets, "Steps", {
        "situation": "situation_id", "n": "Step #", "title": "Step title", "blurb": "Blurb",
        "section": "Toolkit section", "tools": "Tools", "varies": "Varies by level"})
    variations = records(sheets, "Level variations", {
        "situation": "situation_id", "n": "Step #", "level": "level_id",
        "text": "What the reader sees", "storage": "Storage"})
    framing = records(sheets, "Framing copy", {"id": "copy_id", "where": "Where it appears", "text": "Text"})
    storage = records(sheets, "Storage options", {
        "id": "storage_id", "name": "Name", "what": "What it is", "cost": "Cost",
        "offsite": "Off-site", "examples": "Examples"})
    tools = records(sheets, "Tools", {
        "id": "tool_id", "name": "Name", "url": "URL", "platform": "Platform", "cost": "Cost",
        "used_for": "Used for", "note": "One-line note"})
    sections = records(sheets, "Sections", {"id": "section_id", "phase": "Phase", "title": "Section title"})
    if errors:
        return None

    for tab, recs, label in [("Levels", levels, "level_id"), ("Situations", situations, "situation_id"),
                             ("Storage options", storage, "storage_id"), ("Tools", tools, "tool_id"),
                             ("Framing copy", framing, "copy_id")]:
        for r in recs:
            check_id(tab, r["_row"], r["id"], label)
            if tab != "Framing copy" and not (r.get("title") or r.get("name")):
                err(tab, r["_row"], f"'{r['id']}' has no title or name.")
        unique(tab, recs, "id", label)
    for r in sections:
        check_id("Sections", r["_row"], r["id"], "section_id", SECTION_RE)
    unique("Sections", sections, "id", "section_id")

    level_ids = [r["id"] for r in levels]
    sit_ids = {r["id"] for r in situations}
    sec_ids = {r["id"] for r in sections}
    tool_ids = {r["id"] for r in tools}
    stor_ids = {r["id"] for r in storage}

    by_sit = {}
    for s in steps:
        row = s["_row"]
        if s["situation"] not in sit_ids:
            err("Steps", row, f"situation_id '{s['situation']}' isn't on the Situations tab.")
            continue
        n = as_int("Steps", row, s["n"])
        if n is None:
            continue
        if not s["title"]:
            err("Steps", row, "Step title is empty.")
        if s["section"] and s["section"] not in sec_ids:
            err("Steps", row, f"section '{s['section']}' isn't on the Sections tab.")
        for t in split_ids(s["tools"]):
            if t not in tool_ids:
                err("Steps", row, f"tool '{t}' isn't on the Tools tab.")
        varies = s["varies"].lower()
        if varies not in ("yes", "no", ""):
            err("Steps", row, f"'Varies by level?' must be Yes or No, not '{s['varies']}'.")
        lst = by_sit.setdefault(s["situation"], {})
        if n in lst:
            err("Steps", row, f"{s['situation']} already has a step {n} (row {lst[n]['_row']}).")
            continue
        lst[n] = dict(s, n=n, varies=varies == "yes", levels={})

    for v in variations:
        row = v["_row"]
        n = as_int("Level variations", row, v["n"])
        step = by_sit.get(v["situation"], {}).get(n)
        if step is None:
            err("Level variations", row, f"there's no step {v['n']} for situation '{v['situation']}' on the Steps tab.")
            continue
        if not step["varies"]:
            err("Level variations", row, f"step {n} of '{v['situation']}' isn't marked 'Varies by level? Yes'.")
        if v["level"] not in level_ids:
            err("Level variations", row, f"level_id '{v['level']}' isn't on the Levels tab.")
            continue
        if v["level"] in step["levels"]:
            err("Level variations", row, f"step {n} of '{v['situation']}' already has a '{v['level']}' row.")
        for st in split_ids(v["storage"]):
            if st not in stor_ids:
                err("Level variations", row, f"storage '{st}' isn't on the Storage options tab.")
        step["levels"][v["level"]] = {"text": v["text"], "storage": split_ids(v["storage"])}

    for sid, lst in by_sit.items():
        for n, step in lst.items():
            if step["varies"]:
                missing = [l for l in level_ids if l not in step["levels"]]
                if missing:
                    err("Steps", step["_row"], f"step {n} of '{sid}' varies by level but has no Level variations row for: {', '.join(missing)}.")

    if errors:
        return None

    paths = {
        "levels": [{k: r[k] for k in ("id", "title", "budget", "staff_time", "it_access", "copies_goal")} for r in levels],
        "situations": [],
        "framing": {r["id"]: r["text"] for r in framing},
    }
    for r in situations:
        st = [by_sit.get(r["id"], {})[n] for n in sorted(by_sit.get(r["id"], {}))]
        paths["situations"].append({
            "id": r["id"], "title": r["title"], "description": r["description"],
            "status": r["status"] or "Not started", "effort": r["effort"],
            "steps": [{
                "n": s["n"], "title": s["title"], "blurb": s["blurb"], "section": s["section"],
                "tools": split_ids(s["tools"]), "varies": s["varies"],
                **({"levels": s["levels"]} if s["varies"] else {}),
            } for s in st],
        })
    return {
        "paths": paths,
        "tools": [{k: r[k] for k in ("id", "name", "url", "platform", "cost", "used_for", "note")} for r in tools],
        "storage": [{k: r[k] for k in ("id", "name", "what", "cost", "offsite", "examples")} for r in storage],
        "sections": [{k: r[k] for k in ("id", "phase", "title")} for r in sections],
    }


# ---------------------------------------------------------------- writing YAML

def scalar(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    return json.dumps(v, ensure_ascii=False)  # a JSON string is a valid YAML double-quoted scalar


def to_yaml(v, indent=0):
    pad = "  " * indent
    if isinstance(v, dict):
        if not v:
            return " {}"
        out = []
        for k, x in v.items():
            key = k if ID_RE.match(k) or re.match(r"^[a-z_]+$", k) else json.dumps(k)
            if isinstance(x, (dict, list)) and x:
                out.append(f"{pad}{key}:" + "\n" + to_yaml(x, indent + 1))
            else:
                out.append(f"{pad}{key}:" + (to_yaml(x) if isinstance(x, (dict, list)) else " " + scalar(x)))
        return "\n".join(out)
    if isinstance(v, list):
        if not v:
            return " []"
        if all(not isinstance(x, (dict, list)) for x in v):
            return " [" + ", ".join(scalar(x) for x in v) + "]" if indent == 0 else \
                "\n".join(f"{pad}- {scalar(x)}" for x in v)
        out = []
        for x in v:
            body = to_yaml(x, indent + 1).split("\n")
            body[0] = pad + "- " + body[0].lstrip()
            out.append("\n".join(body))
        return "\n".join(out)
    return " " + scalar(v)


def write_yaml(name, data, source):
    text = (f"# Generated by scripts/convert_path_data.py from {source}.\n"
            f"# Don't edit by hand: change the sheet and re-run the converter.\n")
    text += to_yaml(data).lstrip("\n") + "\n"
    path = ROOT / "data" / name
    path.parent.mkdir(exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_stubs(sections):
    made = []
    for s in sections:
        phase, slug = s["id"].split("/")
        page = ROOT / "content" / phase / f"{slug}.md"
        if page.exists():
            continue
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(
            "---\n"
            f"title: {json.dumps(s['title'], ensure_ascii=False)}\n"
            "stub: true\n"
            "---\n\n"
            "This section is coming soon. It will be imported from the final manuscript in January 2027.\n",
            encoding="utf-8")
        made.append(page.relative_to(ROOT))
    return made


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    src = Path(args[0])
    data = convert(read_workbook(src))
    if errors:
        print(f"Found {len(errors)} problem(s) in {src.name}; no files were changed:\n", file=sys.stderr)
        for e in errors:
            print("  - " + e, file=sys.stderr)
        sys.exit(1)
    for name in ("paths", "tools", "storage", "sections"):
        print("wrote", write_yaml(f"{name}.yaml", data[name], src.name).relative_to(ROOT))
    if "--stubs" in argv:
        for p in write_stubs(data["sections"]):
            print("stub ", p)
    p = data["paths"]
    print(f"{len(p['situations'])} situations x {len(p['levels'])} levels = "
          f"{len(p['situations']) * len(p['levels'])} paths, "
          f"{sum(len(s['steps']) for s in p['situations'])} steps, {len(data['tools'])} tools")


if __name__ == "__main__":
    main(sys.argv[1:])
