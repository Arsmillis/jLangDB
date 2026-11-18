# Changelog

Each release is a numbered version of the translation files (`jlangdb-v<N>.zip`); apps pin the number they use. The
file format has its own version (`"format"` in each file), which changes only when the layout does.

## [Unreleased]

- The format (version 1), its checks and the Spanish file, still empty: `data/spa.json`.
- How to send translations (a **Send translations** issue form and a pull request template, both with the licence
  agreement) and how they are reviewed (REVIEWING.md).
- A separate file for machine translations, `data/spa_machine.json` (empty for now): unreviewed, kept apart from the
  translations people wrote or approved, and moved into `data/spa.json` to be reviewed (`tools/promote.py`).
- Every entry names its word (`"word": "お天気【おてんき】"`), so the files can be read without looking up JMdict ids;
  `tools/format.py --jmdict` fills it in.
