# Changelog

What changed in the kit, newest first. To see how a project's copy differs from the current kit, run `bash scripts/sync.sh <project-dir>`.

Version numbers: **major** when something is renamed or removed and existing copies need manual changes, **minor** for new agents, skills or rules, **patch** for wording and fixes.

## 0.1.0 (unreleased)

First version.

- **Working agreement** (`AGENTS.md`): deliver small, test first, start from written context, work economically, definition of done.
- **Agents**: analyst, architect, developer, tester, reviewer, security-reviewer, documenter.
- **Skills**: project-scan (with a survey script), task-plans, diagrams, context-md (with a freshness check script), tdd, debugging, commits-and-prs.
- **`.local_context/`**: a self-ignoring folder for private task notes.
- **Scripts**: `scripts/sync.sh` updates a project's copy of the kit.

Tested with Claude Code, including a project scan of a real application. GitHub Copilot support follows the VS Code documentation and is not yet verified.
