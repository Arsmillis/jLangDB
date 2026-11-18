# jLangDB

Translations of JMdict's definitions (Spanish first), reviewed by JMdict's editorial policy, staged here before being
offered upstream to the EDRDG. Used by Kanji Lens (github.com/Arsmillis/KanjiLens: `build_dict.py` downloads a pinned
release). README.md has the format, the writing rules and the review process; Kanji Lens's `docs/spanish.md` has the
full plan and the reasoning behind it.

## Layout and commands

- `data/<code>_machine.json`: machine translations, all `source: machine`, `status: pending`; approval is moving one
  into `<code>.json` (`tools/promote.py`). Apps prefer: approved in `<code>.json` > JMdict's own > machine > English.
- `data/<code>.json`: one file per language (JMdict's ISO 639-2 code: `spa`). Format version in `"format"`; a format
  change needs a new version, a matching change in Kanji Lens's `build_dict.py`, and a note in README.md.
- `tools/check.py` (the format and editorial rules; `--jmdict` adds the comparison with today's JMdict),
  `tools/format.py` (the standard layout; `--jmdict` fills each entry's readable `word`), `tools/fetch_jmdict.py`.
  Standard library only: no dependencies.
- `tests/`: `python -m unittest discover -s tests`.
- Contributions: `.github/ISSUE_TEMPLATE/translations.yml` (the Send translations form) and
  `.github/pull_request_template.md` both carry the CC BY-SA 4.0 agreement; keep their wording in step with
  README.md's. REVIEWING.md is the maintainer's review process.

```
python tools/fetch_jmdict.py
python tools/format.py --jmdict jmdict-eng.json.zip
python tools/check.py --jmdict jmdict-eng.json.zip
```

## Conventions

- Match the style: comments are full sentences explaining why, functions preceded by a `#` comment, lines within 120
  characters.
- Only approved entries are used by apps. A pending entry must match today's JMdict (an error); an approved one whose
  English changed is a warning (apps skip it until it's re-reviewed).
- Reviewing is the maintainer's: never mark an entry approved or rejected on your own; a machine translation is
  `"source": "machine"`, `"status": "pending"`.
- Releases are deliberate and by hand, not by a workflow: `VERSION` holds the version X.Y.Z; a release PR moves
  CHANGELOG.md's `## [Unreleased]` entries under `## [X.Y.Z] - date` and bumps `VERSION` (patch for fixes, minor for new
  translations or tools, major when the format changes in a way apps must follow); once merged, the maintainer runs
  `tools/release.sh` on main (`--dry-run` first, on any branch), which tests, checks against today's JMdict, tags
  `vX.Y.Z`, publishes `jlangdb-vX.Y.Z.zip` and verifies the upload. Never run it, tag or create releases unless asked. A
  PR that changes the data or tools adds its entry under `## [Unreleased]`.
- Work on a branch per change and open a PR; the maintainer reviews and merges. Never push to main. Stage files by
  name, never `git add -A`.
- Everything here is CC BY-SA 4.0 (credit the EDRDG); never add text from other dictionaries.
