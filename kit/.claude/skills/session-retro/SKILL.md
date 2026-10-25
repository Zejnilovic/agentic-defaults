---
name: session-retro
description: Write a short retrospective note on how the current chat session went (outcome, corrections, rework, cost, the kit file behind a problem, and a fix) in .local_context/feedback/. Use only when the user asks for it, for example "retro this session" or "write a session note".
---

<!-- From agentic-defaults. Kit updates replace this file except a "## This project" section at the end, which belongs to the project. Edit nothing else. Rules for all work go in AGENTS.md "This project". -->

# Session retro

A retro turns one session into a short note: did the work get done, what had to be corrected, and which rule caused it. A generic problem goes back to the kit, a project problem into the project's own files. Write one only when the user asks.

## Steps

1. **Collect** from this conversation. Don't re-run the session's commands or re-read files.
   - Outcome: done, partly done or failed, against what the user asked for.
   - Corrections: each time the user redirected you, and why.
   - Rework: what tests, the reviewer or the user caught after you said a step was done.
   - Cost: in Claude Code, run `bash .claude/skills/session-retro/stats.sh` and use its numbers. It prints counts only: time, models, tokens, prompts, tool calls, subagents and git changes. In other tools, use only numbers the tool showed in this conversation. Otherwise write "not shown". Never estimate.
2. **Find the cause.** For each problem, name the kit file whose rule was involved by its installed path, such as `.claude/skills/tdd/SKILL.md` or `AGENTS.md`, and say whether the rule was **missing**, **wrong**, **ignored** or **too long**. Kit files carry the "From agentic-defaults" marker. If no kit file was involved, write "not a kit problem".
3. **Propose a fix.**
   - **Project-only**: it fits only this project. Name where it goes: a `## This project` section at the end of that agent or skill, "This project" in `AGENTS.md`, or a `CONTEXT.md`.
   - **Generic**: every project using the kit would benefit. Describe the change to the kit file.
4. **Confirm.** Show the user the Outcome and Corrections you drafted and ask one question: are they right? Apply their answer.
5. **Write** the note to `.local_context/feedback/<YYYY-MM-DD>-<task>.md`, with today's date and a short slug for the task, in the format below. Keep it under 40 lines.
6. **Report** the path in one line. For a generic fix, add: "To send it to the kit's maintainers, run `agd feedback .local_context/feedback/<file>.md`. It opens a pre-filled issue for you to review, and posts nothing by itself." Then stop.

## Format

```markdown
# <What went wrong, as an issue title, e.g. "Tester wrote 40 tests for one small function">

Kit: agentic-defaults <version from the first line of AGENTS.md>
Tool and models: <e.g. Claude Code, sonnet and haiku>

## Outcome
done | partly done | failed: <one line>

## Corrections
- <what the user redirected, and why> (or "none")

## Rework
- <what was caught afterwards, and by whom> (or "none")

## Cost
<the lines stats.sh printed, numbers the tool showed, or "not shown">

## Cause
- `<installed path>`: missing | wrong | ignored | too long. <which rule, one line>

## Fix
project-only | generic: <the change, and where it goes>
```

## Rules

- Write the kit file's installed path exactly, on its own, in backticks. `agd feedback` finds the kit's maintainers from these paths.
- Summarize. Never put secrets, credentials, customer data, personal data or private code in the note. If the problem can't be explained without some of it, say so to the user and leave it out unless they agree.
- Never run `agd feedback`, open an issue or post anything yourself. The user decides whether to send the note.
- Skip a retro when the user didn't ask for one, and don't write more than one note per session.
