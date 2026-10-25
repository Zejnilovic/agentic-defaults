---
description: Fit Zejnilovic's agentic defaults to a project with a project profile and a standard set of commands.
---

# Fit it to your project

Two things tell the kit about your project: a **profile**, which decides how much engineering it gets, and the **standard commands**, which give every agent the same way to build and test it. The project scan proposes both; you confirm them.

## Project profile

Not every project needs every practice. An internal tool for ten people shouldn't be built like a bank's payment system. Each project describes itself in the **Profile** part of "This project" in `AGENTS.md`. That section belongs to the project, and kit updates never change it:

```markdown
### Profile

- Stage: production
- Audience: internal
- Team: small
- Handles: money, personal data
```

| Dimension | Values | Decides |
|---|---|---|
| Stage | prototype, early, production, mature | How much engineering rigor: test depth, migration safety, compatibility |
| Audience | personal, internal, customer, public | Security depth, versioned API contracts, accessibility, abuse limits |
| Team | solo, small, several | Formality: decision records, contracts and contract tests between teams |
| Handles | none, or money, personal data, regulated data, safety | Risk at any size: security reviews, audit trails, backups before migrations |

Costly items in the skills carry a tag, such as `(production)`, `(external)`, `(public)`, `(teams)` or `(sensitive)`. A tagged item applies only when the profile matches. **Cheap correctness and safety always apply:** input validation, access checks, parameterized queries, tests, and stopping before data loss.

!!! example
    An internal time-tracking tool in production, run by a small team, that handles billing and employee data, gets security reviews for billing and sign-in changes and migrations that keep live data safe. It doesn't get contract tests, Testcontainers or feature switches.

The [`project-profile`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/project-profile/SKILL.md) skill defines the tags, says what each value adds or relaxes, and lists the signs of building for a bigger project than this one.

## Standard commands

Every project should offer the same commands, each wrapping the project's real tools. Then one instruction, "run `make test`", works everywhere, for agents and people alike:

| Command | Does |
|---|---|
| `make setup` | Install dependencies and prepare a local environment |
| `make run` | Start the application locally |
| `make build` | Build everything that ships |
| `make test` | Run all tests; `make test T=<path>` runs one file or test |
| `make lint` | Lint and type-check |
| `make format` | Format the code |
| `make check` | Everything that must pass before work is done |

The working agreement defines done as "`make check` passes". The project scan reports which commands are missing and proposes them, using [Makefile.template](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/project-scan/Makefile.template); it never adds them without asking.

Make is on nearly every macOS and Linux machine. On Windows, use it through WSL, or install it with a package manager.
