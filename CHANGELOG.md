# Changelog

Each release is a version of the translation files (`jlangdb-v<X.Y.Z>.zip`); apps take the newest release of the major
version they read, so the major version changes only when apps must change to read it. The file format has its own
version (`"format"` in each file), which changes only when the layout does.

## [Unreleased]

## [0.2.0] - 2026-11-28

- `review/jmdict_english.json`: the 78 places where JMdict's English looked wrong or unclear while translating,
  in one file to check and report to JMdict (README, "Questionable English in JMdict"). `tools/check.py` checks it,
  and with `--jmdict` warns when a noted sense's English has changed (likely fixed); `tools/format.py` formats it.
- Spanish machine translations for 2,157 more words common in video games (2,648 senses), all waiting for
  review: every word ranked 10,001 to 20,000 in Jiten's video game frequency list that had no Spanish. Spanish now
  covers 53,215 JMdict words.
- 11 Spanish machine translations brought up to date with JMdict of 2026-11-23, which added senses to 9 of them
  and reworded 2 (いい, 方がいい, ダッシュ, 持ち出す and others): apps had been skipping them.

## [0.1.1] - 2026-11-25

- `tools/check.py` no longer reports a missing or extra newline at the end of a file as a layout error.
- `data/spa_machine.json` rewritten in the standard layout (one line; no change to the translations).
- Spanish machine translations for 1,056 words common in video games (1,395 senses), all waiting for review:
  every word in the top 10,000 of Jiten's video game frequency list that had no Spanish (see RESOURCES.md).
  Spanish now covers 51,058 JMdict words.
- RESOURCES.md: every outside source used, with its licence, and which set of machine translations chose its words
  from which list. README's Progress table brought up to date (50,000 words with Spanish).
- Spanish machine translations for 8,889 more words JMdict has no Spanish for (12,088 senses), all waiting for
  review: first the JLPT words still without Spanish (Jonathan Waller's lists, matched to JMdict by
  yomitan-jlpt-vocab), then the most frequent words in wordfreq's Japanese list, skipping spellings another word
  shares. Spanish now covers 50,000 JMdict words, JMdict's own and ours together.

## [0.1.0] - 2026-11-18

- The format (version 1), its checks and the Spanish file, still empty: `data/spa.json`.
- How to send translations (a **Send translations** issue form and a pull request template, both with the licence
  agreement) and how they are reviewed (REVIEWING.md).
- A separate file for machine translations, `data/spa_machine.json`: unreviewed, kept apart from the translations
  people wrote or approved, and moved into `data/spa.json` to be reviewed (`tools/promote.py`).
- Spanish machine translations for the 6,800 common words JMdict has no Spanish for (9,650 senses), all waiting for
  review: apps show them marked as machine translations, where there's no reviewed translation.
- Every entry names its word (`"word": "お天気【おてんき】"`), so the files can be read without looking up JMdict ids;
  `tools/format.py --jmdict` fills it in.
