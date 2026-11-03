#!/usr/bin/env python3
"""Find PDFs in raw/ that have no manifest in sources/, and draft manifests for them.

Walks raw/open/ and, with --include-internal (after group-lead approval),
raw/internal/. Never lists raw/ itself and never enters raw/restricted/.
Symlinked folders and files are reported and never followed or opened.

Expected layout: raw/<access>/<category>/<source-id>/<file>.pdf (no year
folder), where the folder holding the PDF is named after the source id. A PDF whose folder is not
a valid id, or is a category or year folder, is reported; move it into its own
folder (this script never writes to raw/).

With --write-manifests, writes sources/<same path>/manifest.yaml for each new
source with id, access, files (path, sha256, size) and placeholder metadata.
Fill in title, authors, date and tags, then run
`python tools/validate_manifests.py --check-files`. Existing manifests are
never overwritten.

Usage:
  python tools/scan_raw.py [--include-internal] [--write-manifests] [--added-by NAME]
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wikipaths  # noqa: E402

REPO = wikipaths.TOOLS_DIR.parent
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
NOT_IDS = {"papers", "code", "media", "theses", "thesis", "reports", "report", "meetings", "talks"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_pdfs(allowed):
    """Yield (rel_path, error) for each PDF under raw/<access>/ for the allowed roots."""
    for access in allowed:
        top = wikipaths.RAW_DIR / access
        if top.is_symlink():
            yield f"{access}/", "access root is a symlink; not followed"
            continue
        if not top.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(top, followlinks=False):
            for d in list(dirnames):
                p = Path(dirpath) / d
                if p.is_symlink():
                    dirnames.remove(d)
                    yield str(p.relative_to(wikipaths.RAW_DIR)), "symlinked folder; not followed"
            dirnames.sort()
            for name in sorted(filenames):
                if not name.lower().endswith(".pdf"):
                    continue
                p = Path(dirpath) / name
                rel = p.relative_to(wikipaths.RAW_DIR).as_posix()
                if p.is_symlink():
                    yield rel, "symlinked file; not opened"
                else:
                    yield rel, None


def known_files(allowed):
    """Raw paths already listed in a manifest, and existing source ids."""
    paths, ids = set(), set()
    for mpath, _, err in wikipaths.iter_manifests(REPO, allowed):
        if err:
            continue
        ids.add(mpath.parent.name)
        try:
            with open(mpath, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError):
            continue
        for entry in data.get("files") or []:
            if isinstance(entry, dict) and entry.get("path"):
                paths.add(entry["path"])
    return paths, ids


def id_problem(folder):
    if not ID_RE.match(folder):
        return f"folder '{folder}' is not a valid source id (lowercase, digits, . _ -)"
    if folder in NOT_IDS or re.fullmatch(r"\d{4}", folder) or folder in wikipaths.ACCESS_ROOTS:
        return f"PDF sits directly in '{folder}/'; move it into a folder named after its source id"
    return None


def git_user():
    try:
        out = subprocess.run(["git", "config", "user.name"], cwd=REPO, capture_output=True, text=True)
        return out.stdout.strip() or None
    except OSError:
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--include-internal", action="store_true",
                    help="also scan raw/internal/ (only after group-lead approval)")
    ap.add_argument("--write-manifests", action="store_true",
                    help="write draft manifests for new sources")
    ap.add_argument("--added-by", help="value for added_by (default: git user.name)")
    args = ap.parse_args()

    if not wikipaths.run_check_raw():
        return 1
    allowed = wikipaths.allowed_roots(args.include_internal)
    listed, ids = known_files(allowed)

    new = {}  # source dir rel path -> list of pdf rel paths
    problems = []
    for rel, err in iter_pdfs(allowed):
        if err:
            problems.append(f"raw/{rel}: {err}")
            continue
        if rel in listed:
            continue
        perr = wikipaths.check_rel_path(rel, allowed)
        if perr:
            problems.append(f"raw/{rel}: {perr}")
            continue
        folder = rel.split("/")[-2]
        perr = id_problem(folder)
        if perr:
            problems.append(f"raw/{rel}: {perr}")
            continue
        new.setdefault(rel.rsplit("/", 1)[0], []).append(rel)

    if not new and not problems:
        print("scan_raw: no new PDFs; every PDF is listed in a manifest.")
        return 0

    added_by = args.added_by or git_user() or "TODO"
    for src_dir, pdfs in sorted(new.items()):
        sid = src_dir.rsplit("/", 1)[-1]
        access = src_dir.split("/", 1)[0]
        mpath = REPO / "sources" / src_dir / "manifest.yaml"
        status = "new"
        if sid in ids and not mpath.exists():
            problems.append(f"raw/{src_dir}/: id '{sid}' is already used by another manifest")
            continue
        if mpath.exists():
            status = "manifest exists but does not list these files"
        print(f"{sid} ({status})")
        for rel in pdfs:
            print(f"  raw/{rel}")
        if args.write_manifests and not mpath.exists():
            manifest = {
                "id": sid,
                "type": "paper",
                "title": "TODO",
                "authors": ["TODO"],
                "date": "TODO",
                "added_by": added_by,
                "tags": [],
                "access": access,
                "files": [
                    {"path": rel, "sha256": sha256(wikipaths.RAW_DIR / rel),
                     "size": (wikipaths.RAW_DIR / rel).stat().st_size}
                    for rel in pdfs
                ],
                "source_url": None,
                "doi": None,
                "derived": {"extracted": f"extracted/{access}/{sid}.md"},
            }
            mpath.parent.mkdir(parents=True, exist_ok=True)
            with open(mpath, "w", encoding="utf-8") as f:
                yaml.safe_dump(manifest, f, sort_keys=False, allow_unicode=True)
            print(f"  wrote {mpath.relative_to(REPO)} (fill in title, authors, date, tags)")

    if problems:
        print("\nproblems:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
