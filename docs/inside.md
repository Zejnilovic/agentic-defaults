---
description: The four kinds of files in Zejnilovic's agentic defaults: instructions, skills, agents and working files.
---

# What's inside

The kit has four kinds of files. Instructions, skills and agents are generic: nothing in them is about one project. What makes them work in your project is its **context**: `CONTEXT.md`, docs, decision records, tickets and plans. A new project gets new context, not new instructions.

<div class="grid cards" markdown>

-   :material-file-document-outline:{ .lg .middle } **Instructions**

    ---

    Loaded into every conversation, so they stay short. They hold the working agreement.

-   :material-book-open-variant:{ .lg .middle } **Skills**

    ---

    Practices, such as TDD, debugging, diagrams and project scans. They load only when a task needs them, so they can go into detail.

    [:octicons-arrow-right-24: All skills](skills.md)

-   :material-account-group-outline:{ .lg .middle } **Agents**

    ---

    Roles: who does the work. Pick one from Copilot's agent dropdown, or let Claude Code delegate to it.

    [:octicons-arrow-right-24: All agents](agents.md)

-   :material-folder-outline:{ .lg .middle } **Working files**

    ---

    Carry knowledge between sessions and agents: `CONTEXT.md` files for the system, `.local_context/` for private notes and plans.

</div>

## Instructions and working files

| Path | What it does |
|---|---|
| [`AGENTS.md`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/AGENTS.md) | The working agreement: deliver small, test first, start from written context, work economically, definition of done. Its **This project** section is yours. |
| [`CLAUDE.md`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/CLAUDE.md) | One line that makes Claude Code load `AGENTS.md`. |
| [`.local_context/`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.local_context/README.md) | A folder for private task notes, plans and research notes. It ignores itself in git, so nothing in it is committed. |
| `CONTEXT.md` | Not shipped: the project scan writes it. One per level, from the root down to modules, each more concrete than the one above. See [Keep CONTEXT.md current](context.md). |

## Where the files go

agd installs into the project paths below, which give both tools everything.

| Kind | Claude Code | GitHub Copilot (VS Code) |
|---|---|---|
| Instructions | `AGENTS.md` and `CLAUDE.md` at the project root | `AGENTS.md` at the project root, or merged into `.github/copilot-instructions.md` |
| Skills | `.claude/skills/<name>/` | `.claude/skills/<name>/` or `.github/skills/<name>/` |
| Agents | `.claude/agents/<name>.md` | `.claude/agents/<name>.md`, or `.github/agents/<name>.agent.md` |
| Local notes | `.local_context/` at the project root | Same |
| End-of-turn context check | A Stop hook you add to `.claude/settings.json` | `.github/hooks/context-check.json`, shipped with the kit |

For files in your home folder, see [Personal setup](paths.md#personal-setup).
