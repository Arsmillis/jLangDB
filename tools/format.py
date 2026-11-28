"""Rewrite every file in data/ (and review/jmdict_english.json) in the standard layout: entries sorted by id, their
fields in a fixed order, two-space indent, characters as they are (not \\u escapes). Run it after editing a file by
hand; tools/check.py fails on a file that isn't in this layout.

    python tools/format.py                                   the layout only
    python tools/format.py --jmdict jmdict-eng.json.zip      also set each entry's "word" to JMdict's headword
"""
import json
import sys

from check import DATA, REVIEW, dump, dump_review, load_jmdict


def main(argv):
    jmdict = load_jmdict(argv[argv.index("--jmdict") + 1]) if "--jmdict" in argv else None
    for path in sorted(DATA.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if jmdict is not None:
            for eid, entry in data["entries"].items():
                if isinstance(entry, dict) and eid in jmdict:
                    entry["word"] = jmdict[eid]["word"]
        path.write_text(dump(data), encoding="utf-8", newline="\n")
        print("formatted", path.name)
    # The list of questionable English in JMdict, in its own layout
    if REVIEW.exists():
        data = json.loads(REVIEW.read_text(encoding="utf-8"))
        if jmdict is not None:
            for eid, entry in data["entries"].items():
                if isinstance(entry, dict) and eid in jmdict:
                    entry["word"] = jmdict[eid]["word"]
        REVIEW.write_text(dump_review(data), encoding="utf-8", newline="\n")
        print("formatted", "review/" + REVIEW.name)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
