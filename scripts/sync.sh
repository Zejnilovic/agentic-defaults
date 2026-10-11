#!/usr/bin/env bash
# Compares a project's copy of the kit with this repository's kit/ and optionally updates it.
# Works with bash 3.2 (macOS) and Git Bash (Windows).
#
# Usage: bash scripts/sync.sh <project-dir> [--diff] [--apply [--existing-only]]
#   (no flag)        report which kit files are missing, differ or are the same
#   --diff           also show the differences
#   --apply          copy missing files and overwrite differing ones; review the result with git diff
#   --existing-only  with --apply, update only files the project already has
#
# Never touched: files that aren't in the kit, a CLAUDE.md with extra content, and the
# "This project" section of AGENTS.md (only the part above it is updated).

set -u
kit="$(cd "$(dirname "$0")/../kit" && pwd)"
version=$(cat "$(dirname "$0")/../VERSION" 2>/dev/null || echo unknown)

project="" show_diff=0 apply=0 existing_only=0
for arg in "$@"; do
  case "$arg" in
    --diff) show_diff=1 ;;
    --apply) apply=1 ;;
    --existing-only) existing_only=1 ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    -*) echo "Unknown option: $arg" >&2; exit 2 ;;
    *) project="$arg" ;;
  esac
done
[ -n "$project" ] && [ -d "$project" ] || { echo "Usage: bash scripts/sync.sh <project-dir> [--diff] [--apply [--existing-only]]" >&2; exit 2; }
project="$(cd "$project" && pwd)"

marker='^## This project'
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
top() { sed "/$marker/,\$d" "$1"; }

installed=$(sed -n 's/.*agentic-defaults \([0-9][0-9.]*\).*/\1/p' "$project/AGENTS.md" 2>/dev/null | head -1)
echo "Kit $version -> $project (project AGENTS.md says: ${installed:-no version})"
echo

missing=0 differs=0 same=0 manual=0
for rel in $(cd "$kit" && find . -type f | sed 's|^\./||' | sort); do
  src="$kit/$rel" dst="$project/$rel"

  if [ ! -e "$dst" ]; then
    missing=$((missing + 1))
    if [ "$apply" = 1 ] && [ "$existing_only" = 0 ]; then
      mkdir -p "$(dirname "$dst")" && cp "$src" "$dst" && echo "added    $rel"
    else
      echo "missing  $rel"
    fi
    continue
  fi

  case "$rel" in
    AGENTS.md)
      if ! grep -q "$marker" "$dst"; then
        manual=$((manual + 1)); echo "manual   $rel (no \"## This project\" section; merge by hand)"; continue
      fi
      top "$src" > "$tmp/kit-top"; top "$dst" > "$tmp/project-top"
      if cmp -s "$tmp/kit-top" "$tmp/project-top"; then same=$((same + 1)); continue; fi
      differs=$((differs + 1))
      [ "$show_diff" = 1 ] && diff -u "$tmp/project-top" "$tmp/kit-top" | sed "s|$tmp/project-top|project/$rel|; s|$tmp/kit-top|kit/$rel|"
      if [ "$apply" = 1 ]; then
        { cat "$tmp/kit-top"; sed -n "/$marker/,\$p" "$dst"; } > "$tmp/merged" && cp "$tmp/merged" "$dst"
        echo "updated  $rel (kept \"This project\")"
      else
        echo "differs  $rel (above \"This project\")"
      fi
      continue
      ;;
    CLAUDE.md)
      if ! cmp -s "$src" "$dst"; then
        manual=$((manual + 1)); echo "manual   $rel (has its own content; merge by hand into AGENTS.md)"
      else
        same=$((same + 1))
      fi
      continue
      ;;
  esac

  if cmp -s "$src" "$dst"; then same=$((same + 1)); continue; fi
  differs=$((differs + 1))
  [ "$show_diff" = 1 ] && diff -u "$dst" "$src" | sed "s|$dst|project/$rel|; s|$src|kit/$rel|"
  if [ "$apply" = 1 ]; then
    cp "$src" "$dst" && echo "updated  $rel"
  else
    echo "differs  $rel"
  fi
done

echo
echo "$same same, $differs differ, $missing missing, $manual to merge by hand."
if [ "$apply" = 1 ]; then
  echo "Review with git diff in the project. Local tweaks to kit files (for example a changed model) were overwritten."
elif [ $((differs + missing)) -gt 0 ]; then
  echo "Run again with --diff to see changes, or --apply to update."
fi
