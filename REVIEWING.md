# Reviewing translations

How the maintainer reviews what contributors send. It follows the EDRDG's
[Editorial process](https://www.edrdg.org/wiki/Editorial_Process.html): contributors propose, the reviewer decides,
and every decision, with its reason, stays in the repository's history.

## A submission

A submission arrives as a pull request, or as an issue ("Send translations") with the entries attached or pasted.
For an issue, the reviewer brings its entries into `data/<code>.json` on a branch (adding the submitter's name, if
they gave one, as `submitter`), so that it can be reviewed as a pull request like any other; the issue is linked from
the pull request and closed when it merges. Only submissions that agreed to the licence (CC BY-SA 4.0) are taken.

The Check workflow runs on every pull request. Its errors are fixed before review (by the submitter, or by the
reviewer for small things such as the layout and the `word` field:
`python tools/format.py --jmdict jmdict-eng.json.zip`). Its warnings (a leading article, a capital, a full stop) are
for the reviewer to judge: some glosses need them.

## Each entry

Every entry in the submission is reviewed on its own, against README.md's writing rules and the JMdict entry it
translates (its senses, parts of speech and tags, which the translation follows). Then:

- **Approve:** set `"status": "approved"`. Small edits (a typo, a missing accent, an article left out, a gloss split
  in two) are made in place before approving; the commit says what was changed.
- **Reject:** set `"status": "rejected"` and write the reason in `comment`, briefly and for the submitter: wrong
  meaning, built from the kanji, copied from another dictionary, not a translation of this sense... A joke, an
  offensive or a vandalised translation is rejected and not kept for later. Rejected entries stay in the file so the
  reason stays with them, until a better translation replaces them.
- **Ask:** when the entry is close but needs the submitter (a reference, a sense that is unclear), leave it
  `pending` and ask in the pull request or issue. A pending entry is never used by apps.

A substantial meaning (one that isn't simply a translation of the English: a different nuance, a regional term, an
explanation) needs a reference in `refs`; without one, ask for it or reject it.

## Machine translations

Machine translations live in `data/<code>_machine.json`, all pending. To review some, move them into the main file
on a branch, `python tools/promote.py spa 1002470 ...`, and review them there one by one like any submission: approving
one means a person checked it (it keeps `"source": "machine"`, so its origin stays on record). A player's translation
of a word that also has a machine one is reviewed as usual; once it's approved, `python tools/promote.py spa
--approved` removes the machine copy (the check warns about any left over). The machine file itself is regenerated,
not edited by hand.

## When JMdict changes

JMdict is updated continuously. When it rewords or re-splits a sense, `tools/check.py --jmdict` warns about the
approved entries whose `eng` no longer matches (apps skip them meanwhile). Each is reviewed again: update `eng` and
the translation to match the new senses and approve it again, or reject it if it no longer fits. An entry JMdict has
removed is rejected with that reason.

## Merging and releasing

Merge the pull request once every entry in it is approved, rejected, or deliberately left pending. The decisions go
out with the next release (`tools/release.sh`, see CHANGELOG.md): add a line under `## [Unreleased]` saying what the
batch added, e.g. "120 Spanish entries (common words)".
