"""Check jLangDB's translation files against the format and the editorial rules (see README.md).

    python tools/check.py                         the format and style of every file in data/
    python tools/check.py --jmdict jmdict-eng.json.zip
                                                  also against JMdict: every entry and sense exists, and the English
                                                  each translation was made from is still JMdict's

The JMdict file is jmdict-simplified's English edition (jmdict-eng-*.json.zip, or its .json). Errors make the check
fail; warnings are for the reviewer (a style rule with exceptions, or an approved translation whose English has
changed since). Uses only Python's standard library.

data/<code>.json holds the translations people wrote or approved; data/<code>_machine.json the machine translations,
all pending until one is moved into <code>.json for review (tools/promote.py).
"""
import json
import re
import sys
import zipfile
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
FORMAT = 1
STATUSES = ("pending", "approved", "rejected")
SOURCES = ("player", "machine", "maintainer")
GLOSS_TYPES = ("lit", "fig", "expl", "tm")
# An entry's fields, in the order the standard layout writes them. "word" is JMdict's headword, for people reading the
# file (apps go by the id): its first written form and reading, as tools/format.py --jmdict writes it
ENTRY_KEYS = ("word", "senses", "status", "source", "refs", "comment", "submitter")
# Leading articles, which a gloss leaves out unless it needs one (Spanish; a file for another language would add its
# own)
ARTICLES = {"spa": ("el", "la", "los", "las", "un", "una", "unos", "unas")}


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, where, text):
        self.errors.append(f"{where}: {text}")

    def warn(self, where, text):
        self.warnings.append(f"{where}: {text}")


# The text of a gloss: a plain string, or {"type": ..., "text": ...} for a typed one
def gloss_text(gloss):
    return gloss["text"] if isinstance(gloss, dict) else gloss


# Check one gloss of language `lang`; where: "spa.json 1002470 sense 1"
def check_gloss(report, where, lang, gloss, last):
    if isinstance(gloss, dict):
        if set(gloss) != {"type", "text"} or gloss["type"] not in GLOSS_TYPES:
            report.error(where, f"a typed gloss is {{\"type\": one of {', '.join(GLOSS_TYPES)}, \"text\": ...}}")
            return
        if gloss["type"] == "lit" and not last:
            report.error(where, "a literal (lit) gloss comes last in its sense")
    text = gloss_text(gloss)
    if not isinstance(text, str) or not text.strip():
        report.error(where, "a gloss is a non-empty string")
        return
    if text != text.strip() or "  " in text:
        report.error(where, f"extra spaces in {text!r}")
    if ";" in text:
        report.error(where, f"{text!r}: one meaning per gloss (a semicolon separates glosses, so list them instead)")
    first = text.split()[0].casefold()
    if first in ARTICLES.get(lang, ()):
        report.warn(where, f"{text!r} starts with an article: leave it out unless it's needed")
    if text[0].isupper():
        report.warn(where, f"{text!r} starts with a capital: lowercase unless it's a proper noun")
    if text.endswith(".") and not text.endswith("..."):    # "..." stands for a missing word, as in JMdict
        report.warn(where, f"{text!r} ends with a full stop")


# Check one entry of a file in language `lang`; machine: the file is <code>_machine.json
def check_entry(report, name, lang, eid, entry, machine=False):
    where = f"{name} {eid}"
    if not re.fullmatch(r"[1-9][0-9]*", eid):
        report.error(where, "an entry's key is its JMdict entry id (ent_seq)")
    if not isinstance(entry, dict):
        report.error(where, "an entry is an object")
        return
    for key in set(entry) - set(ENTRY_KEYS):
        report.error(where, f"unknown field {key!r}")
    for key in ("word", "senses", "status", "source"):
        if key not in entry:
            report.error(where, f"missing {key!r}" + (" (python tools/format.py --jmdict ... fills it)"
                                                       if key == "word" else ""))
    if not isinstance(entry.get("word", ""), str):
        report.error(where, "word is a string: JMdict's headword")
    if entry.get("status") not in STATUSES:
        report.error(where, f"status is one of {', '.join(STATUSES)}")
    if entry.get("source") not in SOURCES:
        report.error(where, f"source is one of {', '.join(SOURCES)}")
    refs = entry.get("refs", [])
    if not isinstance(refs, list) or not all(isinstance(r, str) and r.strip() for r in refs):
        report.error(where, "refs is a list of references (strings)")
    for key in ("comment", "submitter"):
        if not isinstance(entry.get(key, ""), str):
            report.error(where, f"{key} is a string")
    if machine and (entry.get("source"), entry.get("status")) != ("machine", "pending"):
        report.error(where, "a machine translation is \"source\": \"machine\", \"status\": \"pending\" (approve it by"
                            " moving it into the main file: tools/promote.py)")
    if entry.get("status") == "rejected" and not entry.get("comment", "").strip():
        report.error(where, "a rejected entry gives the reason in its comment")
    senses = entry.get("senses")
    if not isinstance(senses, list) or not senses:
        report.error(where, "senses is a list with one item per JMdict sense, in order")
        return
    for n, sense in enumerate(senses, start=1):
        at = f"{where} sense {n}"
        if not isinstance(sense, dict) or set(sense) != {"eng", lang}:
            report.error(at, f"a sense has \"eng\" (the English translated) and {lang!r} (the translation)")
            continue
        eng = sense["eng"]
        if not isinstance(eng, list) or not eng or not all(isinstance(g, str) and g for g in eng):
            report.error(at, "eng is the sense's English glosses, as JMdict has them")
        glosses = sense[lang]
        if not isinstance(glosses, list) or not glosses:
            report.error(at, f"{lang} is a list of glosses")
            continue
        for i, gloss in enumerate(glosses):
            check_gloss(report, at, lang, gloss, i == len(glosses) - 1)


# An entry's headword as people read it: its first written form with the first reading that applies to it,
# "お天気【おてんき】", or its first reading alone for a word written in kana
def headword(w):
    if not w["kanji"]:
        return w["kana"][0]["text"]
    form = w["kanji"][0]["text"]
    reading = next((k["text"] for k in w["kana"] if "*" in k["appliesToKanji"] or form in k["appliesToKanji"]),
                   w["kana"][0]["text"])
    return f"{form}【{reading}】"


# JMdict by entry id: {"word": headword, "senses": [[English glosses of sense 1], [sense 2]...]}, from
# jmdict-simplified's English edition
def load_jmdict(path):
    path = Path(path)
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as z:
            data = json.loads(z.read(z.namelist()[0]))
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
    return {w["id"]: {"word": headword(w),
                      "senses": [[g["text"] for g in s["gloss"] if g["lang"] == "eng"] for s in w["sense"]]}
            for w in data["words"]}


# Compare a file's entries with JMdict. A pending entry (a submission) must match today's JMdict; an approved one whose
# English has changed since is flagged for review, and so is a machine translation (to translate again): apps skip
# them until they are updated
def check_against_jmdict(report, name, entries, jmdict, machine=False):
    for eid, entry in entries.items():
        if not isinstance(entry, dict) or not isinstance(entry.get("senses"), list):
            continue
        flag = report.error if entry.get("status") == "pending" and not machine else report.warn
        where = f"{name} {eid}"
        found = jmdict.get(eid)
        if found is None:
            flag(where, "not in JMdict (removed or merged?)")
            continue
        english = found["senses"]
        if entry.get("word") != found["word"]:
            report.warn(where, f"JMdict's headword is {found['word']} (python tools/format.py --jmdict ... updates it)")
        if len(entry["senses"]) != len(english):
            flag(where, f"{len(entry['senses'])} senses, JMdict has {len(english)}")
        else:
            for n, (sense, eng) in enumerate(zip(entry["senses"], english), start=1):
                if isinstance(sense, dict) and sense.get("eng") != eng:
                    flag(f"{where} sense {n}", f"JMdict's English is now {eng}, not {sense.get('eng')}")


# Check one translation file (data/<code>.json or data/<code>_machine.json); returns its entries
def check_file(report, path):
    name, lang, machine = path.name, path.stem.split("_")[0], path.stem.endswith("_machine")
    if not re.fullmatch(r"[a-z]{3}(_machine)?", path.stem):
        report.error(name, "a file is named by JMdict's language code: <code>.json, or <code>_machine.json")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        report.error(name, f"not valid UTF-8 JSON: {e}")
        return {}
    if not isinstance(data, dict) or data.get("format") != FORMAT or not isinstance(data.get("entries"), dict):
        report.error(name, f"a file is {{\"format\": {FORMAT}, \"entries\": {{...}}}}")
        return {}
    for key in set(data) - {"format", "entries"}:
        report.error(name, f"unknown field {key!r}")
    # Written as the tools write it, so a change shows as a small diff: sorted ids, two-space indent, real characters
    if path.read_text(encoding="utf-8") != dump(data):
        report.error(name, "not in the standard layout: run python tools/format.py")
    for eid, entry in data["entries"].items():
        check_entry(report, name, lang, eid, entry, machine)
    return data["entries"]


# A machine translation whose entry <code>.json has approved since is left over: flag it, to remove
def check_leftovers(report, files):
    for name, entries in files.items():
        if name.endswith("_machine.json"):
            main = files.get(name.replace("_machine", ""), {})
            for eid in entries:
                if isinstance(main.get(eid), dict) and main[eid].get("status") == "approved":
                    report.warn(f"{name} {eid}", "approved in the main file: remove it here"
                                                 " (python tools/promote.py --approved)")


# A file's text in the standard layout
def dump(data):
    def ordered(entry):    # the known fields in ENTRY_KEYS' order, then any others (which the check reports)
        if not isinstance(entry, dict):
            return entry
        known = {k: entry[k] for k in ENTRY_KEYS if k in entry}
        return {**known, **{k: v for k, v in entry.items() if k not in ENTRY_KEYS}}
    entries = dict(sorted(data["entries"].items(), key=lambda item: int(item[0]) if item[0].isdigit() else -1))
    entries = {eid: ordered(entry) for eid, entry in entries.items()}
    return json.dumps({"format": data["format"], "entries": entries}, ensure_ascii=False, indent=2) + "\n"


def main(argv):
    jmdict = None
    if "--jmdict" in argv:
        jmdict = load_jmdict(argv[argv.index("--jmdict") + 1])
    report = Report()
    files = sorted(DATA.glob("*.json"))
    found = {}
    for path in files:
        found[path.name] = entries = check_file(report, path)
        if jmdict is not None:
            check_against_jmdict(report, path.name, entries, jmdict, path.stem.endswith("_machine"))
    check_leftovers(report, found)
    for line in report.warnings:
        print("warning:", line)
    for line in report.errors:
        print("error:", line)
    print(f"{len(files)} files: {len(report.errors)} errors, {len(report.warnings)} warnings")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
