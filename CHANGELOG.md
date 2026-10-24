# Changelog

What changed in the kit. The next version's changes are collected here; each released version's notes, including manual steps for existing copies, are on its GitHub release, linked below. To see how a project's copy differs from the current kit, run `bash scripts/sync.sh <project-dir>`.

Version numbers: **major** when something is renamed or removed and existing copies need manual changes, **minor** for new agents, skills or rules, **patch** for wording and fixes. Before 1.0, a minor version may also need manual changes; its notes list them under "Manual steps". Each release is a git tag (`v0.1.0`), and the first line of a project's `AGENTS.md` shows which version its copy came from.

## 0.3.0 (unreleased)

- **Project profile**: four dimensions (Stage, Audience, Team, Handles) in the project's own part of `AGENTS.md`, so the engineering fits the project instead of a large enterprise. A new `project-profile` skill defines them, says what each value adds or relaxes, and lists the signs of building for a bigger project. Costly items in skills carry a tag (`(production)`, `(external)`, `(public)`, `(teams)`, `(sensitive)`) and apply only when the profile matches; cheap correctness and safety always apply. The project scan proposes a profile from evidence, and the survey reports a contributor count (no names) as a hint for Team. The architect designs for the profile, and the reviewer flags practices the profile doesn't call for.
- **Kit files are marked and never edited**: every kit agent, skill, script and `.local_context` file starts with a "From agentic-defaults" marker. The working agreement tells agents never to edit them or tell the user to, and where project rules, facts and project-only agents go instead. `check.py` enforces the markers.

Manual steps for existing copies:

- Add a "### Profile" part to "This project" in `AGENTS.md` (see the kit's `AGENTS.md`), or ask the analyst to propose one. Sync doesn't touch that section.

## Released

- [0.2.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.2.0) (2026-10-21)
- [0.1.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.1.0) (2026-10-11)
