# Changelog

What changed in the kit. The next version's changes are collected here; each released version's notes, including manual steps for existing copies, are on its GitHub release, linked below. To see what an update would change in a project, run `agd status` there.

Version numbers: **major** when something is renamed or removed and existing copies need manual changes, **minor** for new agents, skills or rules, **patch** for wording and fixes. Before 1.0, a minor version may also need manual changes; its notes list them under "Manual steps". Each release is a git tag (`v0.1.0`), and the first line of a project's `AGENTS.md` shows which version its copy came from.

## 0.5.0 (unreleased)

- **`session-retro` skill** (core pack): when the user asks for a retro, the agent evaluates the session on evidence: each requirement met or not, the user's prompts labeled request, answer, correction or complaint, rework after "done", the "Done means" rules, and cost against the project's earlier retros. Fixed rules turn the misses into a verdict (went well, mixed, went badly), which the user confirms. The note in `.local_context/feedback/<date>-<task>.md` names the kit file behind each miss by its installed path, with whether its rule was missing, wrong, ignored or too long, and a project-only or generic fix; a row in `.local_context/feedback/log.tsv` builds the baseline. For a generic fix the agent suggests `agd feedback <note>`; it never sends anything itself. `.local_context/README.md` mentions the `feedback/` folder.
- **`session-retro/stats.sh`**: a read-only script that the retro runs in Claude Code for its Cost section. From Claude Code's local session files it counts time, models, tokens, prompts, interrupts, denied and failed tool calls, and subagents; from git, commits and lines since the session started and uncommitted changes; from `log.tsv`, the medians of the last 10 retros. It prints counts only, never session text, except `--prompts`, which lists the user's prompts for the agent to label locally. The session numbers need jq; without it the script says so and prints the git numbers. The session files are an undocumented format, so the numbers can break with a Claude Code update.
- **Needs agd 0.2.0**: `packs.txt` sets `min-agd 0.2.0`, the release that adds `agd feedback`.

Manual steps for existing copies:

- Upgrade agd to 0.2.0 or newer, then run `agd update`. An older agd stops and asks you to upgrade.

## Released

- [0.4.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.4.0) (2026-10-24)
- [0.3.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.3.0) (2026-10-24)
- [0.2.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.2.0) (2026-10-21)
- [0.1.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.1.0) (2026-10-11)
