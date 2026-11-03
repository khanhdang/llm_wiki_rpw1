#!/usr/bin/env bash
# Check that raw/ is in place before touching raw files.
# Exit 0 if usable; otherwise print the reason and exit 1.
# Never scans raw/: one listing of raw/open/ only, no recursion.

set -u

fail() {
  echo "check_raw: $1" >&2
  exit 1
}

root="$(cd "$(dirname "$0")/.." && pwd)/raw"

[ -e "$root" ] || fail "$root does not exist. Create raw/open/, raw/internal/ and raw/restricted/."
[ -L "$root" ] && fail "$root is a symlink; raw/ must be a real folder inside the wiki folder."
[ -d "$root" ] || fail "$root is not a directory."

for access in open internal restricted; do
  [ -L "$root/$access" ] && fail "$root/$access is a symlink; not followed."
done

[ -d "$root/open" ] || fail "$root/open does not exist."
ls "$root/open" >/dev/null 2>&1 || fail "$root/open is not listable."

echo "check_raw: OK ($root)"
exit 0
