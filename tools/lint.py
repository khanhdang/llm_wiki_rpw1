#!/usr/bin/env python3
"""Lint the wiki and print a markdown report.

Reports broken [[links]], orphan pages (no inbound links), frontmatter
problems, [src:...] citations (and frontmatter `sources`) naming ids with no
manifest, ambiguous page names, and counts of [unsourced] and [location?].

Exits 1 if there are broken links or unknown citation ids, else 0.

Source ids are the folder names of manifests under sources/open/ and
sources/internal/; manifests are not opened and sources/restricted/ is
never listed.

Usage:
  python tools/lint.py [--root DIR]
"""

import argparse
import datetime
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wikipaths  # noqa: E402

# Files in wiki/ that are not content pages: no frontmatter, never orphans.
SPECIAL = {"index.md", "log.md"}

FOLDER_TYPES = {
    "concepts": "concept",
    "methods": "method",
    "hardware": "hardware",
    "papers": "paper",
    "projects": "project",
    "people": "person",
    "questions": "question",
}
REQUIRED = ["title", "type", "sources", "tags", "updated", "status"]
STATUSES = {"draft", "reviewed"}

FENCE_RE = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.M | re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
LINK_RE = re.compile(r"\[\[([^\]\n]+)\]\]")
CITE_RE = re.compile(r"\[src:([^\]\s]+)(?:\s[^\]]*)?\]")
FILENAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*\.md$")


def split_frontmatter(text):
    """Return (frontmatter dict or None, error or None, body)."""
    if not text.startswith("---\n"):
        return None, "no frontmatter (page must start with '---')", text
    end = text.find("\n---", 4)
    if end == -1:
        return None, "frontmatter not closed with '---'", text
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError as e:
        return None, f"frontmatter is not valid YAML: {e}", text[end + 4:]
    if not isinstance(data, dict):
        return None, "frontmatter is not a YAML mapping", text[end + 4:]
    return data, None, text[end + 4:]


def strip_code(text):
    return INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))


def link_target(raw):
    """[[target#heading|alias]] -> target"""
    return raw.split("|", 1)[0].split("#", 1)[0].strip()


def check_frontmatter(fm, folder, errors):
    for key in REQUIRED:
        if key not in fm or fm[key] is None:
            errors.append(f"frontmatter: `{key}` missing")
    t = fm.get("type")
    if t is not None:
        if t not in FOLDER_TYPES.values():
            errors.append(f"frontmatter: type `{t}` is not a known page type")
        elif folder in FOLDER_TYPES and t != FOLDER_TYPES[folder]:
            errors.append(f"frontmatter: type `{t}` but page is in {folder}/")
    s = fm.get("status")
    if s is not None and s not in STATUSES:
        errors.append(f"frontmatter: status `{s}` is not draft or reviewed")
    for key in ("sources", "tags"):
        if key in fm and fm[key] is not None and not isinstance(fm[key], list):
            errors.append(f"frontmatter: `{key}` must be a list")
    u = fm.get("updated")
    if u is not None and not isinstance(u, datetime.date):
        errors.append("frontmatter: `updated` must be a date (YYYY-MM-DD)")
    if "title" in fm and not isinstance(fm["title"], str):
        errors.append("frontmatter: `title` must be a string")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=str(wikipaths.TOOLS_DIR.parent), help="wiki root folder (default: this folder)")
    args = ap.parse_args()

    root = Path(args.root)
    wiki = root / "wiki"
    if not wiki.is_dir():
        print(f"lint: {wiki} not found", file=sys.stderr)
        return 2

    known_ids = wikipaths.manifest_ids(root, wikipaths.ACCESS_ROOTS)
    pages = sorted(p for p in wiki.rglob("*.md") if not p.is_symlink())

    stems = defaultdict(list)
    for p in pages:
        stems[p.stem].append(p)

    broken = []          # (page, target)
    bad_cites = []       # (page, id, where)
    page_errors = defaultdict(list)
    inbound = defaultdict(set)
    markers = {}         # page -> (unsourced, location?)

    for p in pages:
        rel = p.relative_to(root).as_posix()
        text = p.read_text(encoding="utf-8")
        sub = p.relative_to(wiki).parts
        folder = sub[0] if len(sub) > 1 else ""
        special = len(sub) == 1 and p.name in SPECIAL

        if not special:
            if len(sub) == 1:
                page_errors[rel].append("page is outside the type folders")
            elif folder not in FOLDER_TYPES:
                page_errors[rel].append(f"unknown folder {folder}/")
            if not FILENAME_RE.match(p.name):
                page_errors[rel].append("file name must be lowercase ASCII words joined by hyphens")
            fm, err, body = split_frontmatter(text)
            if err:
                page_errors[rel].append(err)
            else:
                check_frontmatter(fm, folder, page_errors[rel])
                for sid in fm.get("sources") or []:
                    if str(sid) not in known_ids:
                        bad_cites.append((rel, str(sid), "frontmatter"))
        else:
            body = text

        scan = strip_code(body)
        # log.md records ids and page names as plain text; only check pages and index.
        if not (special and p.name == "log.md"):
            for m in LINK_RE.finditer(scan):
                target = link_target(m.group(1))
                if target in stems:
                    for q in stems[target]:
                        if q != p:
                            inbound[q].add(p)
                else:
                    broken.append((rel, target))
            for m in CITE_RE.finditer(scan):
                if m.group(1) not in known_ids:
                    bad_cites.append((rel, m.group(1), "inline"))

        u, loc = scan.count("[unsourced]"), scan.count("[location?]")
        if u or loc:
            markers[rel] = (u, loc)

    orphans = [p.relative_to(root).as_posix() for p in pages
               if not (p.parent == wiki and p.name in SPECIAL) and not inbound[p]]
    dupes = {s: ps for s, ps in stems.items() if len(ps) > 1}

    content_pages = sum(1 for p in pages if not (p.parent == wiki and p.name in SPECIAL))
    print("# Wiki lint report\n")
    print(f"- Pages: {content_pages}")
    print(f"- Known source ids: {len(known_ids)}")
    print(f"- Broken links: {len(broken)}")
    print(f"- Unknown citation ids: {len(bad_cites)}")
    print(f"- Pages with frontmatter or naming problems: {sum(1 for v in page_errors.values() if v)}")
    print(f"- Orphan pages: {len(orphans)}")
    print(f"- Ambiguous page names: {len(dupes)}")
    print(f"- `[unsourced]` markers: {sum(u for u, _ in markers.values())}")
    print(f"- `[location?]` markers: {sum(l for _, l in markers.values())}")

    if broken:
        print("\n## Broken links\n")
        for rel, target in broken:
            print(f"- {rel}: [[{target}]]")
    if bad_cites:
        print("\n## Citations to ids with no manifest\n")
        for rel, sid, where in bad_cites:
            print(f"- {rel}: `{sid}` ({where})")
    if any(page_errors.values()):
        print("\n## Frontmatter and naming problems\n")
        for rel, errs in sorted(page_errors.items()):
            for e in errs:
                print(f"- {rel}: {e}")
    if orphans:
        print("\n## Orphan pages (no inbound links)\n")
        for rel in orphans:
            print(f"- {rel}")
    if dupes:
        print("\n## Ambiguous page names (same stem in several folders)\n")
        for s, ps in sorted(dupes.items()):
            print(f"- `{s}`: " + ", ".join(q.relative_to(root).as_posix() for q in ps))
    if markers:
        print("\n## Markers to resolve\n")
        print("| Page | `[unsourced]` | `[location?]` |")
        print("|------|---------------|---------------|")
        for rel, (u, loc) in sorted(markers.items()):
            print(f"| {rel} | {u} | {loc} |")

    return 1 if broken or bad_cites else 0


if __name__ == "__main__":
    sys.exit(main())
