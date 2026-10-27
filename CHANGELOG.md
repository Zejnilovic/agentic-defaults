# Changelog

What changed in the kit. The next version's changes are collected here; each released version's notes, including manual steps for existing copies, are on its GitHub release, linked below. To see what an update would change in a project, run `agd status` there.

Version numbers: **major** when something is renamed or removed and existing copies need manual changes, **minor** for new agents, skills or rules, **patch** for wording and fixes. Before 1.0, a minor version may also need manual changes; its notes list them under "Manual steps". Each release is a git tag (`v0.1.0`), and the first line of a project's `AGENTS.md` shows which version its copy came from.

## 0.5.1 (unreleased)

- **`context-md/check.sh` skips files installed by agd** ([#12](https://github.com/Zejnilovic/agentic-defaults/issues/12)): an `agd update`, `add` or `remove` no longer asks for a `CONTEXT.md` change in `--strict` (CI) or `--hook` mode. The check skips `.agd.lock` and every path it lists, read from the working tree, from `HEAD` and, with `--base`, from where the branch started, so kit files that were deleted are skipped too. The project's own files next to kit files, such as its own skills' scripts, are still checked.
- **Project scan proposes removing unused packs** ([#13](https://github.com/Zejnilovic/agentic-defaults/issues/13)): `agd init` installs every pack, so a Python project could carry the Flask, React and Spring agents into every session. The survey now lists the packs in `.agd.lock`, and the scan compares each framework, platform or datastore pack with the stack it found and proposes `agd remove <pack>` for each one nothing uses, with its evidence. It never runs the command, and never proposes removing `core`, `research`, `copilot-hook` or a pack it isn't sure about.

## Released

- [0.5.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.5.0) (2026-10-27)
- [0.4.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.4.0) (2026-10-24)
- [0.3.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.3.0) (2026-10-24)
- [0.2.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.2.0) (2026-10-21)
- [0.1.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.1.0) (2026-10-11)
