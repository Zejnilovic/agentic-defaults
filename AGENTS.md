# Maintaining this repository

This repo publishes reusable instructions, skills and agents. Everything under `kit/` is meant to be copied into other projects, so it must work there on its own.

**`kit/` is the product, not your instructions.** When you read files under `kit/`, Claude Code also loads `kit/CLAUDE.md`, which imports the kit's working agreement, and it may offer the kit's skills. Treat them as content you are editing. The rules in this file are the ones that apply to work on this repo.

## Before committing

- Run `python3 scripts/check.py` and `python3 -m unittest discover -s tests`. CI runs both on Linux and macOS.
- Script changes are test-first: add or change a test in `tests/test_scripts.py`, watch it fail, then change the script.

## Versions and releases

- **Every change to `kit/` belongs to a version.** If the current version is already released (tagged), start a new one before or with the change: `bash scripts/bump.sh <version>`. It updates `VERSION`, the marker on the first line of `kit/AGENTS.md`, and adds an "(unreleased)" `CHANGELOG.md` heading with a TODO. Replace the TODO with what changed.
- **Pick the number by impact on project copies:** patch for wording and fixes, minor for new agents, skills or rules, major for renames or removals that need manual changes in copies.
- **Several changes can share one unreleased version.** Add a bullet to its `CHANGELOG.md` entry for each.
- **To release:** replace "(unreleased)" with today's date, commit, then tag that commit `v<version>` and push the tag.
- **`check.py` enforces this.** It fails when `kit/` differs from the tag of a released `VERSION`, when a released version's heading has no date, and while the newest entry has no bullets or still says TODO. Changes outside `kit/` (README, scripts, tests) don't need a new version.

## Compatibility: Claude Code and GitHub Copilot

- **Agents**: `name` and `description` are required and read by both tools. `model` (a Claude alias such as `haiku` or `sonnet`) and `skills` (skills to preload) are read by Claude Code only; VS Code doesn't read them from `.claude/agents` files. Don't set `tools`: tool names differ between products, and an agent with a wrong tool list silently loses abilities. Write restrictions such as "don't modify files" in the body.
- **Skills**: follow the Agent Skills format. One folder per skill containing `SKILL.md`; `name` is lowercase with hyphens and matches the folder; `description` says what the skill does and when to use it.
- **Bodies**: describe actions ("search the code", "run the tests") rather than naming a product's tools.
- **Instructions**: `kit/AGENTS.md` is the single source. `kit/CLAUDE.md` only imports it.
- **Scripts in skills and `scripts/`**: read-only unless their purpose is to write (like `scripts/sync.sh --apply`). They must run with bash 3.2 (macOS) and Git Bash (Windows), need only git and POSIX tools, and detect optional tools with `command -v`. Cover their behavior in `tests/test_scripts.py`, and try a new script on at least two real projects of different kinds.

## Write for everyday models

The kit must work well on fast, inexpensive models, not only the strongest ones.

- Use numbered steps, an explicit output format and explicit stop conditions ("stop and report when ...").
- Say what to skip as well as what to do. Prefer concrete limits to judgment calls: "at most 10 findings" rather than "keep it brief".
- Keep files short. `kit/AGENTS.md` is loaded into every conversation (`check.py` enforces a 700-word budget), and skills listed in an agent's `skills` are loaded in full.
- Write agent descriptions so they trigger only when the role is worth its cost. Claude Code delegates automatically based on the description, and a discovery run can cost hundreds of thousands of tokens.
- Set `model: sonnet` only for roles that mainly reason (architect, reviewers) and `model: haiku` for roles that mainly read or execute (analyst, the developers, tester, documenter).
- Framework developers come in pairs: a `<name>` skill with the framework's practices and a thin `<name>-developer` agent that preloads `implementation` and `<name>`, plus a short "essentials" fallback for tools that don't preload skills. Change shared developer behavior in the `implementation` skill, not in each agent. Framework skills keep the same sections (follow the project first, structure, the framework's own concerns, `## Tests`, `## Stop and report before`); `check.py` enforces the pairing and the last two sections.
- Framework skills hold the framework's practices, not any one project's conventions. Write only what you're sure is current for the framework; leave out version-specific details unless they matter.

## Content rules

- Two audiences. `CONTEXT.md`, `AGENTS.md`, plans and agent and skill files are for AI agents: dense, exact, stable. `README.md` and `docs/` are for people. The kit's own guidance must keep that split.

- Generic only. Something belongs here once it has proved useful in more than one project; project-specific material stays in that project.
- Keep `kit/AGENTS.md` short. Move procedures into skills.
- Agents are roles (who does the work); skills are practices (how it's done). An agent names the skills it uses and keeps a one-line version of their essential rule, so it still behaves sensibly if a skill wasn't copied. Don't paste a skill's content into an agent.
- Roles don't delegate to other agents. Each one returns its result to whoever called it.
- When adding, renaming or removing anything in `kit/`, update the tables in `README.md`.
