"""Write a release's files (tools/release.sh runs it): the package apps download, and the release notes.

    python tools/release_files.py VERSION PACKAGE NOTES

The package is a zip of data/*.json and LICENSE, with fixed timestamps so the same files always give the same zip. The
notes are VERSION's section of CHANGELOG.md, then how many entries each file has, by status."""
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def package(path):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted((ROOT / "data").glob("*.json")) + [ROOT / "LICENSE"]:
            info = zipfile.ZipInfo(f.name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, f.read_bytes())


def notes(version):
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    section = re.search(rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## |\Z)", changelog, re.S | re.M)
    lines = [section.group(1).strip() if section else "", "", "| File | Approved | Pending | Rejected |",
             "|---|---|---|---|"]
    for f in sorted((ROOT / "data").glob("*.json")):
        statuses = [e.get("status") for e in json.loads(f.read_text(encoding="utf-8"))["entries"].values()]
        counts = " | ".join(str(statuses.count(s)) for s in ("approved", "pending", "rejected"))
        lines.append(f"| `{f.name}` | {counts} |")
    lines += ["", "Apps use only the approved entries. Licence: CC BY-SA 4.0, adapted from JMdict (© EDRDG)."]
    return "\n".join(lines).strip() + "\n"


def main(argv):
    version, package_path, notes_path = argv
    package(package_path)
    Path(notes_path).write_text(notes(version), encoding="utf-8")
    print("wrote", package_path, "and", notes_path)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
