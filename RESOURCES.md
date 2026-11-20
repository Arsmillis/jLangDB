# Resources

Every outside source jLangDB has drawn on, what it was used for, and its licence. Only JMdict's own text goes into the
translation files. The other sources are used to choose which words to translate next, or to measure what is still
missing, and none of their text is copied into the files.

When a new source is used, add it here, with its licence and the date it was downloaded.

## The dictionary

| Source | Licence | Used for |
|---|---|---|
| [JMdict](https://www.edrdg.org/jmdict/j_jmdict.html), by the [EDRDG](https://www.edrdg.org/) | [CC BY-SA 4.0](https://www.edrdg.org/edrdg/licence.html) | What every translation is made from: the words, their readings, parts of speech and English senses. Also the source of JMdict's own Spanish, which tells us which words already have it |
| [jmdict-simplified](https://github.com/scriptin/jmdict-simplified) (`jmdict-eng`, `jmdict-spa`) | CC BY-SA 4.0 (JMdict's) | The JSON edition of JMdict that `tools/fetch_jmdict.py` downloads, and that Kanji Lens builds its dictionary from |

## Choosing which words to translate

Each set of machine translations (see CHANGELOG.md) chose its words from one or more of these lists. A list is matched to
JMdict entries, and words that already have Spanish (JMdict's own, approved here, or a machine translation) are left
out. From the second set on, so are entries whose every sense is archaic, obsolete or rare.

| Set | Source | Licence | How it was used |
|---|---|---|---|
| First (0.1.0, 6,800 words) | JMdict's own "common" markers (`news1`, `ichi1`, `spec1`/`spec2`, `gai1`) | CC BY-SA 4.0 | Every common word with no Spanish |
| Second (8,889 words) | JLPT vocabulary lists by [Jonathan Waller](http://www.tanos.co.uk/jlpt/), matched to JMdict ids by [yomitan-jlpt-vocab](https://github.com/stephenmk/yomitan-jlpt-vocab) (`original_data/n1.csv` to `n5.csv`, downloaded 2026-11-19) | CC BY (lists), CC BY-SA 4.0 (matching) | First, every JLPT word, N5 to N1, still without Spanish: 161 words |
| Second | [wordfreq](https://github.com/rspeer/wordfreq)'s Japanese list (`wordfreq/data/large_ja.msgpack.gz`, downloaded 2026-11-19) | [CC BY-SA 4.0](https://github.com/rspeer/wordfreq#license) (data) | Then, the most frequent words in general text, down to about rank 49,000: 8,728 words. A spelling that more than one JMdict entry shares is skipped, since its frequency may belong to the other word |
| Third (planned) | [Jiten](https://jiten.moe/frequency-dictionaries)'s video game frequency list, built from the scripts of 406 games (CSV: `Word,Form,Rank`, from `https://api.jiten.moe/api/frequency-list/download?downloadType=csv&mediaType=VideoGame`, downloaded 2026-11-19, 195,112 rows) | CC BY-SA 4.0 | Game vocabulary that general-text frequency ranks low: menus, stats, combat. Each row is matched to the JMdict entry with that spelling and reading; a pair that more than one entry shares is skipped |

Jiten also publishes lists for visual novels, anime, manga, novels and other media, under the same licence, if a later
set needs them.

## Measuring what is still missing

| Source | Used for |
|---|---|
| Kanji Lens's 52 test screens (`ocr_cases/` in Kanji Lens, not public: the screenshots are from games), read with its own word analyzer | How much of what a player actually reads has Spanish (Kanji Lens's `docs/spanish.md`) |

## Looked at and not used

- **The JPDB frequency list** (scraped from jpdb.io: anime, dramas, novels, visual novels): no licence found.
- **Commercial Japanese–Spanish dictionaries and apps**: not openly licensed. Text from other dictionaries is never
  added here.
- **Spanish Wiktionary, JSPANISH/HISPADIC, the 2004 Spanish KANJIDIC**: checked for Kanji Lens (see its
  `docs/spanish.md`); too small, or already part of JMdict.
