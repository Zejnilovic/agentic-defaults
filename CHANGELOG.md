# Changelog

What changed in the kit. The next version's changes are collected here; each released version's notes, including manual steps for existing copies, are on its GitHub release, linked below. To see what an update would change in a project, run `agd status` there.

Version numbers: **major** when something is renamed or removed and existing copies need manual changes, **minor** for new agents, skills or rules, **patch** for wording and fixes. Before 1.0, a minor version may also need manual changes; its notes list them under "Manual steps". Each release is a git tag (`v0.1.0`), and the first line of a project's `AGENTS.md` shows which version its copy came from.

## 0.4.0 (unreleased)

- **Packs**: `packs.txt` groups the kit's files into packs that `agd` installs: `core`, `research`, `flask`, `spring`, `react`, `relational-database` and `copilot-hook`. Every pack except `core` requires `core`. `check.py` checks that every kit file is in exactly one pack, that a skill folder stays in one pack, and that each agent's preloaded skills are in its own pack or one it requires.
- **Project parts in kit files**: an agent's `model:` and `tools:` lines, and a `## This project` section at the end of an agent or skill, belong to the project, and kit updates keep them. The working agreement, the marker on each kit file, the README and the methodology's second principle say so. Everything else in kit files stays off limits.
- **agd replaces `scripts/sync.sh`**: projects install and update the kit with [agd](https://github.com/Zejnilovic/agd) (`brew install zejnilovic/tap/agd`). It installs packs, keeps the project parts of kit files, never overwrites a kit file you changed, and can add your team's setup next to this kit. `scripts/sync.sh` now only says how to switch. `.agd-ignore` replaces `.agentic-defaults-ignore`, which still works.

Manual steps for existing copies:

- Install agd, run `agd adopt` in the project and commit `.agd.lock`. `agd update` then moves the project to 0.4.0, keeping any model changes you made.
- Optionally, rename `.agentic-defaults-ignore` to `.agd-ignore`.

## Released

- [0.3.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.3.0) (2026-10-24)
- [0.2.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.2.0) (2026-10-21)
- [0.1.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.1.0) (2026-10-11)
