# jLangDB

Translations of [JMdict](https://www.edrdg.org/jmdict/j_jmdict.html)'s Japanese definitions into other languages,
starting with Spanish: for the words JMdict has no translation for yet, or a fuller one. They are written and reviewed
by [JMdict's editorial policy](https://www.edrdg.org/wiki/Editorial_policy.html), so that they can be offered to the
EDRDG, which maintains JMdict.

**JMdict comes first.** A translation added to JMdict reaches every app that uses it and is kept up to date with its
entry by JMdict's editors. jLangDB is a staging area: translations are collected and reviewed here, used now by
[Kanji Lens](https://github.com/Arsmillis/KanjiLens), offered upstream in batches, and dropped from here once JMdict has
them.

## What's here

| Path | What it is |
|---|---|
| `data/spa.json` | Spanish translations written or approved by people (one file per language, named by JMdict's language code, ISO 639-2) |
| `data/spa_machine.json` | Spanish machine translations, for the words that have no Spanish yet; all unreviewed |
| `tools/check.py` | Checks every file against the format and the rules below, and against today's JMdict |
| `tools/format.py` | Rewrites the files in the standard layout, and with `--jmdict` fills in each entry's `word` (run it after editing a file by hand) |
| `tools/promote.py` | Moves machine translations into the main file for review, and clears the ones approved there |
| `tools/fetch_jmdict.py` | Downloads the current English JMdict ([jmdict-simplified](https://github.com/scriptin/jmdict-simplified)), for the check |
| `review/jmdict_english.json` | Places where JMdict's own English looks wrong or unclear, found while translating: to check, and to report to JMdict |
| `RESOURCES.md` | Every outside source used: to translate from, to choose which words to translate, and to measure what's missing |

Releases (`jlangdb-v<X.Y.Z>.zip`: the files and the licence) are what apps download: the newest release of the major
version they read. The major version changes only when apps must change to read a release (a new format), so new
translations reach them without an app update. The maintainer publishes them with `tools/release.sh` (see CHANGELOG.md
for what each one changed).

## Progress

Spanish, against JMdict of 2026-11-23. A word (a JMdict entry) counts as having Spanish when at least one of its senses
does, so some have only part of their meanings translated.

| | Words |
|---|---|
| JMdict, in English | 219,205 |
| JMdict's own Spanish | 34,313 |
| Approved here (`data/spa.json`) | 0 |
| Machine translations, unreviewed (`data/spa_machine.json`) | 18,902 |
| **With Spanish, all together** | **53,215** (24%) |
| **Still without Spanish** | **165,990** |

## The format

A file translates JMdict's **senses** (meanings), keyed by JMdict entry id (`ent_seq`, which stays the same across
dictionary updates): one translated sense per JMdict sense, in the same order, each beside the English it was
translated from. お天気 (entry 1002470), whose senses are "weather" and "mood; temper":

```json
{
  "format": 1,
  "entries": {
    "1002470": {
      "word": "お天気【おてんき】",
      "senses": [
        {"eng": ["weather"], "spa": ["tiempo (atmosférico)"]},
        {"eng": ["mood", "temper"], "spa": ["humor", "estado de ánimo"]}
      ],
      "status": "approved",
      "source": "player",
      "refs": [],
      "comment": ""
    }
  }
}
```

- **`word`**: the entry's headword, so people can read the file: JMdict's first written form with its reading, or
  the reading alone for a word written in kana. Filled in from JMdict by `tools/format.py --jmdict`; apps go by the id.
- **`senses`**: every sense of the entry, in JMdict's order. `eng` is JMdict's English for that sense, exactly; the
  other key (the file's language) is a list of glosses. A gloss is a string, or a typed one,
  `{"type": "lit", "text": "…"}`, with JMdict's gloss types: `lit` (literal, last in its sense), `fig` (figurative),
  `expl` (explanatory) and `tm` (trademark).
- **`status`**: `pending` (submitted, not reviewed yet), `approved`, or `rejected` (the reason in `comment`). Only
  approved translations are used.
- **`source`**: `player` (sent by someone using an app), `machine` (machine-translated) or `maintainer`.
- **`refs`**: references (a dictionary, a corpus, a link) where the meaning isn't simply a translation of the English.
  Required for anything substantial.
- **`comment`**: notes for the reviewer about this entry, and a rejection's reason.
- **`submitter`** (optional): a name or pen-name to credit.

If JMdict later rewords a sense, `eng` no longer matches it: the check flags the entry for review, and apps skip it
until it's updated.

## Machine translations

`data/<code>_machine.json` (same format) holds machine translations for words that have no translation in JMdict or
in the main file, every entry `"source": "machine"`, `"status": "pending"`. They are kept apart from the main file,
which holds only what people wrote or checked: a machine translation is approved by moving it into the main file
(`tools/promote.py`) and reviewing it there like any submission. Releases include both files; an app using them
should show a machine translation marked as one, and prefer, in order: the main file's approved translations,
JMdict's own, the machine translations, then English. The check flags a machine translation whose English JMdict has
since changed (to translate again) and one the main file has since approved (to remove).

Machine translations are made from the Japanese word, its readings and parts of speech and the English senses
together, one JMdict sense at a time, following the writing rules below.

## Questionable English in JMdict

Translating sometimes turns up English in JMdict that looks wrong: a typo, a gloss that doesn't fit the word, English
too vague to translate safely, a tag that doesn't fit the glosses, or a missing meaning. Each is noted in
`review/jmdict_english.json`, so they can be checked together and the real ones reported to JMdict, as well as in the
entry's `comment`:

```json
{
  "entries": {
    "2842389": {
      "word": "可哀想に【かわいそうに】",
      "notes": [
        {"sense": 1, "eng": ["poor thing!", "pour soul!", "what a pity!"], "kind": "typo",
         "note": "\"pour soul\" for \"poor soul\".", "found": "2026-11-25"}
      ]
    }
  }
}
```

- **`sense`**: the JMdict sense (from 1), and **`eng`** its English as it was when noted.
- **`kind`**: `typo`, `wrong` (a gloss whose meaning looks wrong), `unclear`, `tags` (a part of speech or other tag
  that doesn't fit the glosses) or `missing` (a meaning JMdict doesn't have).
- **`note`**: what looks wrong, in a line; **`found`**: the date.

The file isn't part of releases. `tools/check.py --jmdict` warns when a sense's English has changed since its note,
which usually means JMdict has fixed it: check, and remove the note. A note is only a suspicion until it's checked
against the Japanese, and the translation follows JMdict's English meanwhile.

## How a translation is written

From the EDRDG's [Editorial policy](https://www.edrdg.org/wiki/Editorial_policy.html) (and Jim Breen's
[updated copy](https://www.edrdg.org/~jwb/Updated_editorial_policy.html)), applied to Spanish:

- **One gloss per meaning**, as separate items (no semicolons inside a gloss).
- **Your own words**, never copied from another dictionary. Translating JMdict's English is fine (it's CC BY-SA);
  taking from a commercial dictionary isn't.
- **The gloss matches the sense's part of speech:** verbs in the infinitive (comer for "to eat"), adjectives as plain
  adjectives (not "es…"), nouns as nouns.
- **Lowercase**, except proper nouns. **No leading article** (el, la, un, una) unless it's needed or part of a name
  (La Haya). No full stop at the end.
- **Parentheses for brief context:** "consultar (al oráculo)". Useful explanations, not vague ones; no explanation of
  words any reader knows.
- **Never build a meaning from the kanji's own meanings.**
- **Regional variants** where they differ: ordenador; computadora. Numbers and units as JMdict writes them ("100 km",
  "15°C").
- **Keep the register** the entry's tags give (honorific, humble, slang, vulgar, archaic…): a vulgar word gets a
  vulgar translation.
- **No notes of your own** in the glosses: what a reviewer should know goes in `comment`.

`tools/check.py` enforces the format and warns about the style rules that have exceptions (articles, capitals, full
stops). New entries, readings or parts of speech belong in JMdict itself (proposed through
[JMdictDB](https://www.edrdg.org/jmdictdb/index.html), with references), and kanji meanings in
[KANJIDIC](https://www.edrdg.org/wiki/KANJIDIC_Project.html), not here.

## Contributing

Send translations as a pull request changing a file in `data/`, every entry `pending`, or with the **Send
translations** issue form, attaching or pasting the same entries. By sending a translation you agree to share it under
CC BY-SA 4.0 (below). Before sending a pull request:

```
python tools/fetch_jmdict.py
python tools/format.py --jmdict jmdict-eng.json.zip
python tools/check.py --jmdict jmdict-eng.json.zip
```

The maintainer reviews each batch entry by entry, as the EDRDG's editors do: each is approved (possibly with small
edits) or rejected with its reason. The record stays in the repository's history. [REVIEWING.md](REVIEWING.md) has
the details.

## Licence

The translations are adaptations of JMdict, the property of the
[Electronic Dictionary Research and Development Group](https://www.edrdg.org/) (EDRDG), and are shared under the same
licence, [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (see
`LICENSE`): use them for anything, credit the EDRDG and jLangDB's contributors, and share what you make from them
under the same terms. The tools in `tools/` are under the same licence.
