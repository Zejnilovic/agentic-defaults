#!/usr/bin/env bash
# Lists CONTEXT.md files that may need an update: code under them changed, but they didn't.
# A nudge, not a verdict: internal refactors and bug fixes that restore documented behavior need no update.
# Read-only. Works with bash 3.2 (macOS) and Git Bash (Windows).
#
# Usage: bash check.sh [--base <ref>] [--strict]
#   default       uncommitted changes (staged, unstaged, untracked) against HEAD
#   --base <ref>  also include commits since <ref>, e.g. --base origin/main for a branch or pull request
#   --strict      exit 1 when there is something to check (for CI, pre-commit or agent hooks)

set -u
base=""
strict=0
while [ $# -gt 0 ]; do
  case "$1" in
    --base) base="${2:-}"; shift 2 ;;
    --strict) strict=1; shift ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

root=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "Not a git repository." >&2; exit 2; }
cd "$root" || exit 2

changed=$(mktemp); owners=$(mktemp)
trap 'rm -f "$changed" "$owners"' EXIT

{
  if git rev-parse --verify -q HEAD >/dev/null; then
    git diff --name-only HEAD
  else
    git ls-files
  fi
  git ls-files --others --exclude-standard
  if [ -n "$base" ]; then
    git diff --name-only "$base"...HEAD || exit 2
  fi
} | sort -u > "$changed"

# Changes that never require a CONTEXT.md update: docs, private notes, housekeeping files, tests, lock files.
skip='(^|/)CONTEXT\.md$|\.md$|^docs?/|^\.local_context/|(^|/)(LICENSE|COPYING|NOTICE|CHANGELOG|VERSION)[^/]*$|(^|/)\.(gitignore|gitattributes|editorconfig|mailmap)$|(^|/)(test|tests|__tests__|spec|specs|e2e)/|(^|/)test_[^/]+\.py$|_test\.[a-z]+$|\.(test|spec)\.[a-z]+$|Tests?\.(java|kt|cs|swift|scala)$|(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|poetry\.lock|uv\.lock|Cargo\.lock|go\.sum|Gemfile\.lock|composer\.lock)$'

# Pair each changed code file with the nearest CONTEXT.md above it.
grep -Ev "$skip" "$changed" | while IFS= read -r file; do
  [ -n "$file" ] || continue
  dir=$(dirname "$file")
  owner="-"
  while :; do
    if [ "$dir" = "." ]; then
      [ -f CONTEXT.md ] && owner="CONTEXT.md"
      break
    fi
    if [ -f "$dir/CONTEXT.md" ]; then owner="$dir/CONTEXT.md"; break; fi
    dir=$(dirname "$dir")
  done
  printf '%s\t%s\n' "$owner" "$file"
done > "$owners"

# Keep owners whose CONTEXT.md was not itself changed, grouped, with up to three example files each.
report=$(awk -F'\t' -v changed="$changed" '
  BEGIN { while ((getline line < changed) > 0) touched[line] = 1 }
  $1 != "-" && !($1 in touched) {
    n[$1]++
    if (n[$1] <= 3) ex[$1] = ex[$1] (n[$1] > 1 ? ", " : "") $2
  }
  END { for (o in n) printf "- %s: %s%s\n", o, ex[o], (n[o] > 3 ? " (+" n[o] - 3 " more)" : "") }
' "$owners" | sort)
uncovered=$(awk -F'\t' '$1 == "-" { print $2 }' "$owners" | head -5)

if [ -n "$report" ]; then
  echo "CONTEXT.md files to check (code under them changed, they did not):"
  echo
  printf '%s\n' "$report"
  echo
  echo "Update each one the change made wrong or incomplete (see the context-md skill)."
  echo "No update is needed for internal refactors or bug fixes that restore documented behavior."
fi
if [ -n "$uncovered" ]; then
  [ -n "$report" ] && echo
  echo "No CONTEXT.md covers these changed files (consider a project scan):"
  printf '%s\n' "$uncovered" | sed 's/^/- /'
fi
if [ -z "$report" ] && [ -z "$uncovered" ]; then
  echo "Nothing to check: no code changed, or every CONTEXT.md covering it was updated."
fi

[ "$strict" = 1 ] && [ -n "$report" ] && exit 1
exit 0
