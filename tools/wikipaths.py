"""Path-safety helpers shared by the wiki tools.

Rules (AGENTS.md):
- Select allowed access roots before reading anything. `open` is always allowed;
  `internal` only when the caller opts in after group-lead approval.
- Never traverse or open anything under `restricted/`.
- Reject absolute paths, `..` components, symlinks, and paths outside the
  allowed roots before opening an indexed file.
"""

import os
import stat
import subprocess
import sys
from pathlib import Path

ACCESS_ROOTS = ("open", "internal")
TOOLS_DIR = Path(__file__).resolve().parent
RAW_DIR = TOOLS_DIR.parent / "raw"


def allowed_roots(include_internal):
    return ("open", "internal") if include_internal else ("open",)


def check_rel_path(rel, allowed):
    """Return an error message if `rel` is not a safe path under an allowed root, else None.

    Pure string check: touches no files.
    """
    if not isinstance(rel, str) or not rel.strip():
        return "empty path"
    if rel != rel.strip():
        return "leading or trailing whitespace"
    if "\\" in rel:
        return "backslash in path"
    if rel.startswith("/") or (len(rel) >= 2 and rel[1] == ":"):
        return "absolute path"
    parts = rel.split("/")
    if any(p in ("", ".", "..") for p in parts):
        return "empty, '.' or '..' component"
    if parts[0] == "restricted":
        return "path under restricted/"
    if parts[0] not in allowed:
        if parts[0] in ACCESS_ROOTS:
            return f"path under {parts[0]}/, which is not enabled (internal needs --include-internal after group-lead approval)"
        return f"path outside the access roots ({', '.join(allowed)})"
    return None


def symlink_in_path(base, rel):
    """Return the first component of base/rel that is a symlink, or None.

    One lstat per component; never lists directories. A missing component
    returns None (the caller reports missing files itself).
    """
    cur = Path(base)
    for part in rel.split("/"):
        cur = cur / part
        try:
            st = os.lstat(cur)
        except FileNotFoundError:
            return None
        if stat.S_ISLNK(st.st_mode):
            return str(cur)
    return None


def iter_manifests(repo_root, allowed):
    """Yield (manifest_path, access, error) for each sources/<access>/**/manifest.yaml.

    Walks only the allowed access roots, never sources/ itself, so
    sources/restricted/ is never listed. Symlinked folders and files are
    reported as errors and never followed or opened.
    """
    sources = Path(repo_root) / "sources"
    for access in allowed:
        top = sources / access
        if top.is_symlink():
            yield top, access, "access root is a symlink; not followed"
            continue
        if not top.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(top, followlinks=False):
            for d in list(dirnames):
                p = Path(dirpath) / d
                if p.is_symlink():
                    dirnames.remove(d)
                    yield p, access, "symlinked folder; not followed"
            dirnames.sort()
            if "manifest.yaml" in filenames:
                p = Path(dirpath) / "manifest.yaml"
                if p.is_symlink():
                    yield p, access, "manifest is a symlink; not opened"
                else:
                    yield p, access, None


def manifest_ids(repo_root, allowed):
    """Source ids (manifest folder names) under the allowed roots, without opening manifests."""
    return {p.parent.name for p, _, err in iter_manifests(repo_root, allowed) if err is None}


def run_check_raw():
    """Run tools/check_raw.sh. Return True if raw/ is usable."""
    script = TOOLS_DIR / "check_raw.sh"
    result = subprocess.run(["bash", str(script)])
    if result.returncode != 0:
        print("raw/ check failed; not touching raw files.", file=sys.stderr)
        return False
    return True
