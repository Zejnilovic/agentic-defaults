#!/usr/bin/env bash
# Replaced by agd (github.com/Zejnilovic/agd) in agentic-defaults 0.4.0. This stub only says how to switch, and changes nothing.
# Works with bash 3.2 (macOS) and Git Bash (Windows).

project=""
for arg in "$@"; do
  case "$arg" in -*) ;; *) project=$arg ;; esac
done

cat >&2 <<EOF
scripts/sync.sh was replaced by agd in agentic-defaults 0.4.0, and changed nothing.
agd keeps a project's model choices, tools lines and "This project" sections when it updates kit files.

To switch a project that sync.sh set up:
  1. Install agd: brew install zejnilovic/tap/agd, or see https://github.com/Zejnilovic/agd.
  2. Start managing the copy, without changing a file: agd -C ${project:-<project-dir>} adopt
  3. See what an update would do, then run it: agd -C ${project:-<project-dir>} status, then agd -C ${project:-<project-dir>} update
EOF
exit 2
