#!/usr/bin/env python3
"""Restore source files from Velqora's FILE-delimited plain-text export.

The export is a reference snapshot, not a complete buildable distribution: binary
assets are not included. This utility only restores text sections with explicit
FILE: path markers; it does not decode embedded archives or create missing assets.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path, PurePosixPath

FILE_MARKER = re.compile(r"^\s*(?:\d+\|\s*)?FILE:\s*(.*?)\s*$")
SEPARATOR = re.compile(r"^\s*(?:\d+\|\s*)?={20,}\s*$")
LINE_NUMBER = re.compile(r"^\s*\d+\| ?")
EXPORT_ROOT = "Velqora-PDF-10.3/"


def clean_line(line: str) -> str:
    """Remove line-number prefixes if the export was copied from a numbered view."""
    return LINE_NUMBER.sub("", line, count=1)


def parse_export(source: Path) -> list[tuple[Path, str]]:
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    markers: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        match = FILE_MARKER.match(line)
        if match:
            markers.append((index, match.group(1).strip()))

    if not markers:
        raise ValueError("No 'FILE: path' sections found in the export.")

    restored: list[tuple[Path, str]] = []
    seen: set[Path] = set()
    for marker_index, (start, name) in enumerate(markers):
        if not name:
            raise ValueError(f"Empty filename at export line {start + 1}.")
        relative_name = name.removeprefix(EXPORT_ROOT)
        posix_path = PurePosixPath(relative_name)
        if posix_path.is_absolute() or ".." in posix_path.parts or not posix_path.parts:
            raise ValueError(f"Unsafe path in export: {name!r}")
        if posix_path.parts[0] == ".git":
            raise ValueError(f"Refusing to write into .git/: {name!r}")
        relative_path = Path(*posix_path.parts)
        if relative_path in seen:
            raise ValueError(f"Duplicate FILE section for {relative_path}.")
        seen.add(relative_path)

        end = markers[marker_index + 1][0] if marker_index + 1 < len(markers) else len(lines)
        body = [clean_line(line) for line in lines[start + 1 : end]]
        while body and (not body[0].strip() or SEPARATOR.match(body[0])):
            body.pop(0)
        while body and (not body[-1].strip() or SEPARATOR.match(body[-1])):
            body.pop()
        restored.append((relative_path, "\n".join(body) + "\n"))

    return restored


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("Velqora-PDF-10.3-Broncode-Platte-Tekst.txt"),
        help="path to the plain-text source export (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("."),
        help="repository/project root where recorded paths will be created (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="list the files that would be restored without writing anything",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="allow replacing existing files (use only after reviewing the diff)",
    )
    args = parser.parse_args()

    if not args.source.is_file():
        print(f"Source export not found: {args.source}", file=sys.stderr)
        return 2

    try:
        files = parse_export(args.source)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Cannot parse source export: {error}", file=sys.stderr)
        return 2

    root = args.output.resolve()
    targets = [(root / relative, content) for relative, content in files]
    conflicts = [target for target, _ in targets if target.exists()]
    if conflicts and not args.force and not args.dry_run:
        print("Refusing to overwrite existing files. Review them, then rerun with --force:", file=sys.stderr)
        for target in conflicts:
            print(f"  {target.relative_to(root)}", file=sys.stderr)
        return 1

    for target, _ in targets:
        print(f"{'Would restore' if args.dry_run else 'Restore'} {target.relative_to(root)}")

    if args.dry_run:
        print(f"\nDry run: {len(targets)} file(s); nothing written.")
        return 0

    for target, content in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")

    print(f"\nRestored {len(targets)} text file(s) under {root}.")
    print("The export excludes binary assets; this does not by itself make the project buildable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
