# Changelog

What changed in the kit. The next version's changes are collected here; each released version's notes, including manual steps for existing copies, are on its GitHub release, linked below. To see what an update would change in a project, run `agd status` there.

Version numbers: **major** when something is renamed or removed and existing copies need manual changes, **minor** for new agents, skills or rules, **patch** for wording and fixes. Before 1.0, a minor version may also need manual changes; its notes list them under "Manual steps". Each release is a git tag (`v0.1.0`), and the first line of a project's `AGENTS.md` shows which version its copy came from.

## 0.5.2 (unreleased)

- context-md `check.sh`: dependency bumps no longer ask for a CONTEXT.md update. A dependency manifest (`requirements*.txt`, `pyproject.toml`, `package.json`, `go.mod`, `pom.xml`, Dockerfiles, GitHub workflows and similar) whose change only moves version numbers or pinned digests is skipped, so Renovate and Dependabot pull requests pass `--strict`. Adding or removing a dependency, or any other edit to the manifest, still counts. Projects that skip the CI check for bot pull requests can drop that workaround.

## Released

- [0.5.1](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.5.1) (2026-10-27)
- [0.5.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.5.0) (2026-10-27)
- [0.4.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.4.0) (2026-10-24)
- [0.3.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.3.0) (2026-10-24)
- [0.2.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.2.0) (2026-10-21)
- [0.1.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.1.0) (2026-10-11)
