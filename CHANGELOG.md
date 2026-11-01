# Changelog

What changed in the kit. The next version's changes are collected here; each released version's notes, including manual steps for existing copies, are on its GitHub release, linked below. To see what an update would change in a project, run `agd status` there.

Version numbers: **major** when something is renamed or removed and existing copies need manual changes, **minor** for new agents, skills or rules, **patch** for wording and fixes. Before 1.0, a minor version may also need manual changes; its notes list them under "Manual steps". Each release is a git tag (`v0.1.0`), and the first line of a project's `AGENTS.md` shows which version its copy came from.

## 0.5.3 (unreleased)

- context-md `check.sh`: `--base` with no value no longer loops forever. A missing or empty value, or another option in its place, is a usage error (exit 2).
- context-md `check.sh`: a `--base` that git can't compare with no longer passes silently. An unknown ref, or a ref with no shared history such as a shallow clone's, now exits 2 with the reason, with or without `--strict`. `--hook` stays quiet and exits 0. **CI that runs the check on a shallow checkout starts failing here, where it used to check nothing:** check out with `fetch-depth: 0`.
- diagrams skill: the Mermaid check creates its output folder first, because `mmdc` fails when the folder doesn't exist.
- session-retro `stats.sh`: the baseline counts only retros with both numbers. A `-` in the log used to count as a retro and could print `-` or a wrong median; it stays "no baseline" until 3 retros have numbers.
- implementation skill: removing, relaxing or bypassing an existing authentication or authorization check is now listed under "Stop and report".

## Released

- [0.5.2](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.5.2) (2026-10-28)
- [0.5.1](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.5.1) (2026-10-27)
- [0.5.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.5.0) (2026-10-27)
- [0.4.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.4.0) (2026-10-24)
- [0.3.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.3.0) (2026-10-24)
- [0.2.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.2.0) (2026-10-21)
- [0.1.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.1.0) (2026-10-11)
