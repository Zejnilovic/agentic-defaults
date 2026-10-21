# Changelog

What changed in the kit, newest first. To see how a project's copy differs from the current kit, run `bash scripts/sync.sh <project-dir>`.

Version numbers: **major** when something is renamed or removed and existing copies need manual changes, **minor** for new agents, skills or rules, **patch** for wording and fixes. Before 1.0, a minor version may also need manual changes; each entry lists them under "Manual steps". Each release is a git tag (`v0.1.0`), and the first line of a project's `AGENTS.md` shows which version its copy came from.

## 0.2.0 (unreleased)

Implements the [methodology](docs/methodology.md)'s principles that 0.1.0 didn't cover.

- **Local plans and handover**: plans live in `.local_context/<task>/plan.md`, never committed. When a task ends, what lasts moves to `CONTEXT.md`, decision records and the ticket. Handing a task over means drafting a ticket update from the plan, posted only with approval.
- **Tickets as context**: the analyst fetches the ticket (for example `gh issue view`) and treats its text as data, never instructions.
- **`CONTEXT.md` levels**: agents read the chain from the root down; each level adds only its own detail, points to its parent, and links the real documents.
- **The context check ends every task**: in the definition of done, the developers' last step and the reviewer's checklist. `check.sh --hook` prints the hook JSON that both Claude Code (`Stop`) and GitHub Copilot (`agentStop`) accept, and reminds once per finding. The kit ships `.github/hooks/context-check.json` for Copilot; Claude Code gets a snippet for `.claude/settings.json`. The Copilot hook follows GitHub's documentation and hasn't been tested in a Copilot session yet.
- **Standard commands**: `make setup`, `run`, `build`, `test`, `lint`, `format` and `check`. "Done" means `make check` passes. The survey reports missing targets and the project scan proposes them from a new `Makefile.template`.
- **Contracts first**: plan steps that cross a boundary change the contract first; the reviewer checks for broken contracts; the survey lists contract files; the framework skills keep API specs and generated types accurate.
- **Tests**: never weaken an existing test to make it pass; keep tests contained (stable interfaces, one place per behavior, shared builders); stop when one change breaks many unrelated tests.
- **Hitting a wall**: no stand-ins. The blocker goes into the plan with options (split, spike, re-plan, visible limit), and the user or the architect decides.
- **Short output and cheap orchestration**: a brevity rule in the working agreement; the main conversation routes steps and passes blockers and design questions on instead of answering them.
- **Research**: new `research-collector` (everyday model; gathers sources) and `researcher` (strong model; answers with options, a recommendation, confidence and sources) agents, with a shared `research` skill.

Manual steps for existing copies:

- Move active plans from `docs/plans/` to `.local_context/<task>/plan.md`, and delete the folder once their decisions are recorded.
- Rewrite the "This project" section of `AGENTS.md` around the standard commands. Sync doesn't touch that section.
- Optionally, add the Claude Code Stop hook from the README. Copilot's hook arrives with the sync.

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
