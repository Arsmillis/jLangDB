#!/usr/bin/env bash
# SPDX-License-Identifier: CC-BY-SA-4.0
# Copyright (C) 2026 Arsmillis (https://github.com/Arsmillis/jLangDB)
# Publish, or republish, the GitHub release for the version in VERSION (X.Y.Z, e.g. 0.1.0).
#   tools/release.sh            test + check against today's JMdict, tag vX.Y.Z if needed, create or update the release
#   tools/release.sh --dry-run  the same tests and checks, and write build/; change nothing on GitHub
# Needs Python 3 and the GitHub CLI (gh), with push access. Apps take the newest release of their major version.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1

die() { echo "release: $*" >&2; exit 1; }
check() {  # a failed check stops a real release; a dry run only warns
  if [ "$DRY" = 1 ]; then echo "release: warning: $*" >&2; else die "$*"; fi
}

# Releases only ever come from main: a branch must never publish.
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != main ]; then
  WHERE=${BRANCH:+"branch '$BRANCH'"}
  WHERE=${WHERE:-"a detached HEAD ($(git rev-parse --short HEAD))"}
  [ "$DRY" = 1 ] ||
    die "releases are only made from main, but you're on $WHERE. Switch with 'git switch main' (a --dry-run works on any branch)."
  echo "release: note: dry run on $WHERE; a real release has to run on main." >&2
fi
START=$(git rev-parse HEAD)

VERSION=$(tr -d '[:space:]' < VERSION)
TAG="v$VERSION"
[[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "VERSION must be a version number X.Y.Z (e.g. 0.1.0), got '$VERSION'."
grep -q "^## \[$VERSION\]" CHANGELOG.md ||
  die "CHANGELOG.md has no '## [$VERSION]' section. Move the Unreleased entries under it first."
command -v gh >/dev/null || die "the GitHub CLI (gh) is needed: https://cli.github.com"
command -v python3 >/dev/null || die "Python 3 is needed."
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

[ -z "$(git status --porcelain)" ] || check "there are uncommitted changes; commit them first."
git fetch -q origin main --tags
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] ||
  check "main isn't in sync with origin/main; push (or pull) first."
NEW_TAG=1
if git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
  NEW_TAG=0
  [ "$(git rev-list -n1 "$TAG")" = "$(git rev-parse HEAD)" ] ||
    check "$TAG already exists on a different commit. A published version shouldn't change; bump VERSION instead."
fi

echo "== Testing and checking jLangDB $VERSION against today's JMdict"
mkdir -p build
python3 -m unittest discover -s tests || die "the checker's tests failed."
python3 tools/fetch_jmdict.py build/jmdict-eng.json.zip || die "couldn't download JMdict."
python3 tools/check.py --jmdict build/jmdict-eng.json.zip || die "the check failed: fix the errors above first."
PACKAGE="build/jlangdb-$TAG.zip"
NOTES="build/release-notes.md"
python3 tools/release_files.py "$VERSION" "$PACKAGE" "$NOTES"

if [ "$DRY" = 1 ]; then
  echo "== Dry run: nothing published. Package: $PACKAGE, notes: $NOTES"
  ACTION="update the existing $TAG release"
  [ "$NEW_TAG" = 1 ] && ACTION="create tag $TAG and the release"
  echo "   Would $ACTION on $REPO."
  exit 0
fi

# The download and checks take a while: make sure the branch and commit didn't change meanwhile.
[ "$(git branch --show-current)" = main ] && [ "$(git rev-parse HEAD)" = "$START" ] ||
  die "the branch or commit changed during the checks; nothing was published. Run the release again."

if [ "$NEW_TAG" = 1 ]; then
  echo "== Tagging $TAG"
  git tag -a "$TAG" -m "jLangDB $VERSION"
  git push origin "$TAG"
fi
if gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
  echo "== Updating the $TAG release (republish)"
  gh release edit "$TAG" --repo "$REPO" --title "jLangDB $VERSION" --notes-file "$NOTES"
  gh release upload "$TAG" --repo "$REPO" --clobber "$PACKAGE"
else
  echo "== Creating the $TAG release"
  gh release create "$TAG" --repo "$REPO" --verify-tag --title "jLangDB $VERSION" --notes-file "$NOTES" "$PACKAGE"
fi

echo "== Verifying the published file"
CHECK=$(mktemp -d)
trap 'rm -rf "$CHECK"' EXIT
gh release download "$TAG" --repo "$REPO" --dir "$CHECK" --pattern "$(basename "$PACKAGE")"
[ "$(sha256sum < "$PACKAGE")" = "$(sha256sum < "$CHECK/$(basename "$PACKAGE")")" ] ||
  die "$(basename "$PACKAGE") on GitHub doesn't match the local one."
echo "== Published: https://github.com/$REPO/releases/tag/$TAG"
