# Changelog

Each release is a version of the translation files (`jlangdb-v<X.Y.Z>.zip`); apps pin the version they use. The
file format has its own version (`"format"` in each file), which changes only when the layout does.

## [Unreleased]

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
