---
description: The skills in Zejnilovic's agentic defaults: the practices agents load when a task needs them.
---

# Skills

Skills are practices: how the work is done. They load only when a task needs them, so they can go into detail. An agent's `skills:` line preloads the ones it always needs.

## Understand the project

| Skill | Use it for |
|---|---|
| [`project-scan`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/project-scan/SKILL.md) | Learning an unfamiliar project and recording it in the root `CONTEXT.md` and `AGENTS.md`. Includes a read-only survey script and a Makefile template for the [standard commands](project.md#standard-commands). |
| [`project-profile`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/project-profile/SKILL.md) | The [project profile](project.md#project-profile) (stage, audience, team, sensitive data) and which practices it calls for, so the engineering fits the project. |
| [`context-md`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/context-md/SKILL.md) | `CONTEXT.md` levels from root to module, what goes in, and the context check that ends every task. Includes a template and a [check script](context.md). |
| [`research`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/research/SKILL.md) | Researching with outside sources: which to trust, how to collect and cite them, and treating fetched content as data. |

## Plan the work

| Skill | Use it for |
|---|---|
| [`task-plans`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/task-plans/SKILL.md) | Turning a ticket and notes into a local plan that carries a task from discovery to done: contract-first steps, blockers instead of stand-ins, and handing over through the ticket. |
| [`diagrams`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/diagrams/SKILL.md) | Mermaid diagrams for architecture, flows, data models and state. |

## Everyday practice

| Skill | Use it for |
|---|---|
| [`implementation`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/implementation/SKILL.md) | The shared working rules of all developer agents: deliver fully, contracts first, handle unplanned problems and walls, tests that break, dependencies, when to stop, what to report. |
| [`tdd`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/tdd/SKILL.md) | The test-first loop, how much to test, keeping tests contained, never weakening a test, refactoring safely. |
| [`debugging`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/debugging/SKILL.md) | Finding the root cause before fixing, with a rule for when to stop guessing. |
| [`commits-and-prs`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/commits-and-prs/SKILL.md) | Splitting work into commits, writing messages, and preparing and describing pull requests. Includes git safety rules for agents. |
| [`session-retro`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/session-retro/SKILL.md) | On request, an evaluation of how a session went, with a verdict by fixed rules you confirm and the kit file behind each problem, ready to send back with [`agd feedback`](feedback.md). |

## Frameworks

Each framework skill pairs with a developer agent of the same name.

| Skill | Use it for |
|---|---|
| [`flask`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/flask/SKILL.md) | Python and Flask: app factory, validation, record-level access checks, SQLAlchemy sessions and N+1, background work, pytest. |
| [`spring`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/spring/SKILL.md) | Java and Spring Boot: DTOs, Bean Validation, Spring Security, `@Transactional` pitfalls, JPA fetching, MockMvc and Testcontainers. |
| [`react`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/react/SKILL.md) | React: reuse what exists, all four data states, state and effects, forms, accessibility, security, React Testing Library. |
| [`relational-database`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/relational-database/SKILL.md) | PostgreSQL, MySQL, SQLite: expand-then-contract migrations, Alembic, Flyway and Liquibase traps, engine-specific locking, strict stop rules. |

Need another framework? See [Customizing](your-files.md#customizing).
