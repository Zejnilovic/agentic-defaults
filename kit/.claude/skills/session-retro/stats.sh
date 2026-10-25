#!/usr/bin/env bash
# From agentic-defaults. Kit updates replace this file: don't edit it. Project rules go in AGENTS.md "This project".
# Read-only numbers on a Claude Code session for a session retro: time, models, tokens, prompts, tool calls,
# subagents and git changes. Prints counts only, never text from the session.
# Reads Claude Code's local session files, an undocumented format that can change.
# Needs git and POSIX tools; the session numbers need jq. Works with bash 3.2 (macOS) and Git Bash (Windows).
# Usage: bash stats.sh [session.jsonl]
#   Without a file: the session in CLAUDE_CODE_SESSION_ID, else the newest session for this folder.

set -u
projects=${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects
has() { command -v "$1" >/dev/null 2>&1; }

session="" how=""
if [ $# -gt 0 ]; then
  session=$1 how="given"
elif [ -n "${CLAUDE_CODE_SESSION_ID:-}" ]; then
  for f in "$projects"/*/"$CLAUDE_CODE_SESSION_ID".jsonl; do
    if [ -f "$f" ]; then session=$f how="CLAUDE_CODE_SESSION_ID"; break; fi
  done
fi
if [ -z "$session" ] && [ $# -eq 0 ]; then
  # Claude Code names a project's folder after its path, with every other character than a letter or digit as "-".
  # pwd -W gives Git Bash's Windows path (C:/...), which Claude Code uses on Windows.
  for dir in "$(pwd)" "$(pwd -P)" "$(pwd -W 2>/dev/null)"; do
    [ -n "$dir" ] || continue
    newest=$(ls -t "$projects/$(printf '%s' "$dir" | sed 's/[^A-Za-z0-9]/-/g')"/*.jsonl 2>/dev/null | head -1)
    if [ -n "$newest" ]; then session=$newest how="newest for this folder; parallel sessions can mix this up"; break; fi
  done
fi

start=""
echo "Session numbers (Claude Code's local files, counts only):"
if [ -z "$session" ] || [ ! -f "$session" ]; then
  echo "- No Claude Code session found for this folder. Pass a session file: bash stats.sh <session.jsonl>"
else
  echo "- Session: $(basename "$session" .jsonl) ($how)"
  if ! has jq; then
    echo "- Numbers: not shown: install jq to read them (https://jqlang.org)"
  else
    out=$(mktemp)
    trap 'rm -f "$out"' EXIT
    # Subagents of a session keep their own files in <session>/subagents/.
    set -- "$session"
    for f in "${session%.jsonl}"/subagents/*.jsonl; do [ -f "$f" ] && set -- "$@" "$f"; done
    jq -nrR --arg main "$session" '
      def content: .message.content;
      def texts: if (content | type) == "string" then [content] else [content[]? | select(.type == "text") | .text] end;
      def results: if (content | type) == "array" then [content[] | select(.type == "tool_result")] else [] end;
      def counts: group_by(.) | map({k: .[0], n: length}) | sort_by(-.n);
      [inputs | input_filename as $f | (try fromjson catch null) | select(type == "object") | .file = $f] as $all
      | ($all | map(select(.file == $main))) as $m
      | ($all | map(select(.type == "assistant" and (.message | type) == "object"))) as $a
      # Claude Code logs one entry per content block, so an API call can appear several times with one id.
      | ($a | map(select(.message.model != "<synthetic>")) | group_by(.message.id // .uuid) | map(.[-1])) as $calls
      | ($m | map(select(.type == "user" and (.isMeta | not) and (.isCompactSummary | not) and (.isSidechain | not)
            and (results | length) == 0))) as $u
      | ($m | map(.timestamp // empty | sub("\\.[0-9]+"; "") | try fromdateiso8601 catch empty)) as $times
      | ([$a[] | content[]? | select(.type == "tool_use") | .name]) as $tools
      | def sum(f): map(.message.usage | f // 0) | add // 0;
      (if ($times | length) > 0 then
        "- Time: \((($times | max) - ($times | min)) / 60 | round) min from first to last entry, idle time included",
        "start=\($times | min)"
      else empty end),
      "- Models: \($calls | map(.message.model) | counts | map("\(.k) (\(.n) calls)") | join(", "))",
      "- Tokens: input \($calls | sum(.input_tokens)), output \($calls | sum(.output_tokens)), cache read \($calls | sum(.cache_read_input_tokens)), cache write \($calls | sum(.cache_creation_input_tokens))",
      "- Prompts: \($u | map(select(texts | map(select(test("^(<(local-command|command-|task-notification|system-reminder|ide_)|\\[Request interrupted)") | not)) | length > 0)) | length), interrupts: \($u | map(select(texts | any(startswith("[Request interrupted")))) | length), denied tool calls: \($m | map(select(.type == "user" and .permissionDecision.decision? == "reject")) | length)",
      "- Tool calls: \($tools | length), failed: \([$all[] | select(.type == "user") | results[] | select(.is_error == true)] | length)\(if ($tools | length) > 0 then " (\($tools | counts | .[:5] | map("\(.k) \(.n)") | join(", ")))" else "" end)",
      "- Subagents: \($all | map(.file) | unique | map(select(. != $main)) | length)"
    ' "$@" >"$out" 2>/dev/null || echo "- Numbers: not shown: jq couldn't read the session file"
    start=$(sed -n 's/^start=//p' "$out")
    sed '/^start=/d' "$out"
  fi
fi

if git rev-parse --git-dir >/dev/null 2>&1; then
  echo
  echo "Git:"
  if [ -n "$start" ]; then
    echo "- Commits since the session started: $(git rev-list --count --since="@$start" HEAD 2>/dev/null || echo 0)"
  fi
  base=HEAD
  git rev-parse -q --verify HEAD >/dev/null || base=$(git hash-object -t tree /dev/null)
  git diff --numstat "$base" | awk -v new="$(git ls-files --others --exclude-standard | wc -l | tr -d ' ')" '
    { files++; if ($1 != "-") added += $1; if ($2 != "-") removed += $2 }
    END { printf "- Uncommitted: %d changed files (+%d -%d), %d new files\n", files, added, removed, new }'
fi
