#!/usr/bin/env python3
"""Validate source manifests against tools/manifest_schema.yaml.

Reads only sources/open/ and, with --include-internal (after group-lead
approval for cloud processing), sources/internal/. Never lists or opens
sources/restricted/.

Checks each manifest against the schema, that `access` matches its folder,
that `id` matches its folder name, that ids are unique, and that every file
path is relative, has no `..`, and sits under the manifest's access root.

With --check-files, runs tools/check_raw.sh and then confirms each file
exists under raw/ with the listed size: one lstat per path component,
never listing directories.

Usage:
  python tools/validate_manifests.py [--root DIR] [--include-internal] [--check-files]
"""

import argparse
import datetime
import os
import re
import stat
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wikipaths  # noqa: E402

DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


def load_schema():
    with open(wikipaths.TOOLS_DIR / "manifest_schema.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)["fields"]


def empty(value):
    return value is None or value == "" or value == [] or value == {}


def check_value(name, value, spec, errors):
    kind = spec.get("type", "any")
    if kind == "string":
        if not isinstance(value, str):
            hint = " (quote it, or YAML reads it as a number)" if isinstance(value, (int, float)) else ""
            errors.append(f"{name}: expected a string{hint}")
            return
    elif kind == "int":
        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(f"{name}: expected an integer")
            return
        if "minimum" in spec and value < spec["minimum"]:
            errors.append(f"{name}: must be >= {spec['minimum']}")
    elif kind == "date":
        # YAML turns 2024-03-12 into a date; YYYY and YYYY-MM stay int/str.
        if isinstance(value, (datetime.date, datetime.datetime)):
            return
        if not DATE_RE.match(str(value)):
            errors.append(f"{name}: expected YYYY, YYYY-MM or YYYY-MM-DD")
        return
    elif kind == "list":
        if not isinstance(value, list):
            errors.append(f"{name}: expected a list")
            return
        for i, item in enumerate(value):
            check_value(f"{name}[{i}]", item, spec.get("items", {}), errors)
        return
    elif kind == "mapping":
        if not isinstance(value, dict):
            errors.append(f"{name}: expected a mapping")
            return
        check_fields(value, spec.get("fields", {}), errors, prefix=f"{name}.")
        return
    if "enum" in spec and value not in spec["enum"]:
        errors.append(f"{name}: {value!r} not one of {spec['enum']}")
    if "pattern" in spec and isinstance(value, str) and not re.fullmatch(spec["pattern"], value):
        errors.append(f"{name}: {value!r} does not match {spec['pattern']}")


def check_fields(data, fields, errors, prefix=""):
    for key in data:
        if key not in fields:
            errors.append(f"{prefix}{key}: unknown field")
    for key, spec in fields.items():
        if key not in data:
            if spec.get("required"):
                errors.append(f"{prefix}{key}: missing")
            continue
        value = data[key]
        if empty(value):
            if spec.get("required"):
                errors.append(f"{prefix}{key}: empty")
            elif not spec.get("nullable") and value is None:
                errors.append(f"{prefix}{key}: empty")
            continue
        check_value(prefix + key, value, spec, errors)


def check_raw_file(raw_root, entry, errors):
    rel = entry["path"]
    link = wikipaths.symlink_in_path(raw_root, rel)
    if link:
        errors.append(f"files: {rel}: symlink under raw/ ({link}); not followed")
        return
    try:
        st = os.lstat(Path(raw_root) / rel)
    except FileNotFoundError:
        errors.append(f"files: {rel}: not found under raw/")
        return
    except OSError as e:
        errors.append(f"files: {rel}: cannot stat ({e.strerror})")
        return
    if not stat.S_ISREG(st.st_mode):
        errors.append(f"files: {rel}: not a regular file")
    elif isinstance(entry.get("size"), int) and st.st_size != entry["size"]:
        errors.append(f"files: {rel}: size {st.st_size} under raw/, {entry['size']} in the manifest")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=str(wikipaths.TOOLS_DIR.parent), help="wiki root folder (default: this folder)")
    ap.add_argument("--include-internal", action="store_true",
                    help="also validate sources/internal/ (only after group-lead approval)")
    ap.add_argument("--check-files", action="store_true", help="confirm each listed file exists under raw/")
    args = ap.parse_args()

    root = Path(args.root)
    allowed = wikipaths.allowed_roots(args.include_internal)
    schema = load_schema()

    raw_root = None
    if args.check_files:
        if not wikipaths.run_check_raw():
            return 1
        raw_root = root / "raw"

    problems = {}
    seen_ids = {}
    count = 0
    for path, access, err in wikipaths.iter_manifests(root, allowed):
        rel = path.relative_to(root).as_posix()
        if err:
            problems.setdefault(rel, []).append(err)
            continue
        count += 1
        errors = []
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except (yaml.YAMLError, UnicodeDecodeError) as e:
            problems[rel] = [f"not valid YAML: {e}"]
            continue
        if not isinstance(data, dict):
            problems[rel] = ["not a YAML mapping"]
            continue

        check_fields(data, schema, errors)

        folder = path.parent.name
        if data.get("id") != folder:
            errors.append(f"id: {data.get('id')!r} does not match folder name {folder!r}")
        if data.get("access") != access:
            errors.append(f"access: {data.get('access')!r} but manifest is under sources/{access}/")
        if folder in seen_ids:
            errors.append(f"id: duplicate of {seen_ids[folder]}")
        else:
            seen_ids[folder] = rel

        for entry in data.get("files") or []:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                continue  # already reported by the schema check
            bad = wikipaths.check_rel_path(entry["path"], (access,))
            if bad:
                errors.append(f"files: {entry['path']!r}: {bad} (must be under {access}/)")
            elif raw_root:
                check_raw_file(raw_root, entry, errors)

        if errors:
            problems[rel] = errors

    print("# Manifest validation\n")
    print(f"- Access roots checked: {', '.join(a + '/' for a in allowed)}")
    if not args.include_internal:
        print("- internal/ skipped (pass --include-internal only after group-lead approval)")
    print(f"- Manifests read: {count}")
    print(f"- Manifests with problems: {len(problems)}")
    if args.check_files:
        print("- Files checked under raw/: yes")
    for rel, errs in sorted(problems.items()):
        print(f"\n## {rel}\n")
        for e in errs:
            print(f"- {e}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
