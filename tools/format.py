"""Rewrite every file in data/ in the standard layout: entries sorted by id, two-space indent, characters as they are
(not \\u escapes). Run it after editing a file by hand; tools/check.py fails on a file that isn't in this layout."""
import json
import sys

from check import DATA, dump


def main():
    for path in sorted(DATA.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        path.write_text(dump(data), encoding="utf-8", newline="\n")
        print("formatted", path.name)


if __name__ == "__main__":
    sys.exit(main())
