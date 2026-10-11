# Changelog

What changed in the kit, newest first. To see how a project's copy differs from the current kit, run `bash scripts/sync.sh <project-dir>`.

Version numbers: **major** when something is renamed or removed and existing copies need manual changes, **minor** for new agents, skills or rules, **patch** for wording and fixes. Each release is a git tag (`v0.1.0`), and the first line of a project's `AGENTS.md` shows which version its copy came from.

## 0.1.0 (2026-10-11)

First release.

- **Framework developers**, each an agent and skill pair: `flask-developer` (Python, Flask), `spring-developer` (Java, Spring Boot), `react-developer` (React) and `relational-database-developer` (PostgreSQL, MySQL, SQLite; Alembic, Flyway, Liquibase). The reviewer uses the framework skills as checklists. The architect names an agent for each plan step and orders layers database, backend, frontend. The developer's working rules moved into a shared `implementation` skill that every developer preloads; `developer` covers work no framework developer does.

- **Working agreement** (`AGENTS.md`): deliver small, test first, start from written context, work economically, definition of done.
- **Agents**: analyst, architect, developer, tester, reviewer, security-reviewer, documenter.
- **Skills**: project-scan (with a survey script), task-plans, diagrams, context-md (with a freshness check script), tdd, debugging, commits-and-prs.
- **`.local_context/`**: a self-ignoring folder for private task notes.
- **Scripts**: `scripts/sync.sh` updates a project's copy of the kit.
- **Delivery safeguards**, adapted from [GSD Core](https://github.com/open-gsd/gsd-core) (MIT):
  - the reviewer checks that a plan's goal was met (true, real, connected), not just that steps were ticked,
  - the developer has rules for fixing unplanned problems versus stopping to ask, and a guard against reading without acting,
  - requirements are never watered down to fit ("for now", "placeholder"); work is split instead,
  - every plan step names a Verify command,
  - packages are installed only when named, never swapped for a similar name, and the security reviewer checks new ones for typosquatting.

Tested with Claude Code, including a project scan of a real application. GitHub Copilot support follows the VS Code documentation and is not yet verified.
