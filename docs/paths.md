---
description: The ways to use Zejnilovic's agentic defaults, from a fresh install to copying single files or building your team's setup on top.
---

# Choose your path

Pick the situation closest to yours.

<div class="grid cards" markdown>

-   :material-rocket-launch-outline:{ .lg .middle } **A project with no AI setup yet**

    ---

    The usual path: install the whole kit with the installer.

    [:octicons-arrow-right-24: Fresh install](#fresh-install)

-   :material-puzzle-outline:{ .lg .middle } **Only the frameworks I use**

    ---

    Install the core and only the framework packs your project needs.

    [:octicons-arrow-right-24: Pick packs](#pick-packs)

-   :material-folder-sync-outline:{ .lg .middle } **My project already has AI files**

    ---

    A `CLAUDE.md`, Copilot instructions, notes or an older copy of this kit.

    [:octicons-arrow-right-24: Existing AI files](#existing-ai-files)

-   :material-content-copy:{ .lg .middle } **No tools, just the files**

    ---

    Copy what you need by hand, all of it or a single skill.

    [:octicons-arrow-right-24: Copy by hand](#copy-by-hand)

-   :material-account-outline:{ .lg .middle } **For me, in every project**

    ---

    Personal instructions, skills and agents in your home folder.

    [:octicons-arrow-right-24: Personal setup](#personal-setup)

-   :material-office-building-outline:{ .lg .middle } **My team's setup on top**

    ---

    Publish your team's agents and rules, and install them with this kit.

    [:octicons-arrow-right-24: Team setup](#team-setup)

</div>

Only want the ideas? Read [the method](#only-the-ideas) and apply it in your own setup, with any tool.

## Fresh install

1. Install [agd](https://zejnilovic.github.io/agd) and run `agd init` in the project's root.
2. Commit the new files together with `.agd.lock`.
3. Ask your assistant to "use the analyst to scan this project", and confirm what it proposes.

The [quick start](start.md) has the commands.

## Pick packs

The kit comes in [packs](packs.md), so a project gets only the frameworks it uses. Fewer agents mean a shorter agent list in Copilot and less guessing when Claude Code picks one.

```bash
agd init --with spring,react
```

The [packs page](packs.md) lists what each one contains.

## Existing AI files

| You have | Do this |
|---|---|
| A copy of this kit, made by hand or with the old `scripts/sync.sh` | Run `agd adopt` to start updating it with the installer ([how](https://zejnilovic.github.io/agd)). |
| `CLAUDE.md` or `.github/copilot-instructions.md` with content | Move the project-specific parts (commands, done checks, conventions) into the **This project** section of `AGENTS.md`, then replace `CLAUDE.md` with the one-line import. Both tools then read the same rules. |
| A `CONTEXT.md` or architecture notes | Keep them. The project scan keeps their stable facts, splits them by area and drops volatile parts such as test counts and issue lists. |
| Decision records, such as `docs/adr/` | Keep them. The kit uses them instead of repeating decisions in `CONTEXT.md`. |
| Folders of private notes, such as exported specs | Move them into `.local_context/` so they can't be committed by accident. |
| A `docs/plans/` folder from kit 0.1.0 | Move each active plan to `.local_context/<task>/plan.md`, move finished plans' decisions into decision records or `CONTEXT.md`, and delete the folder. Remove the "Plans" line from **This project**. |

## Copy by hand

Copy the contents of [`kit/`](https://github.com/Zejnilovic/agentic-defaults/tree/master/kit) into the project's root. To take only part of it:

- Copy each skill as a **whole folder**, since it may contain a template or script.
- Copy the skills an agent lists in its `skills:` line along with the agent.
- Then fill in the **This project** section of `AGENTS.md`, by hand or with a project scan.

You'll update by hand, using the [releases](https://github.com/Zejnilovic/agentic-defaults/releases) to see what changed.

## Personal setup

The installer works per project, so copy personal files by hand:

| Kind | Claude Code | GitHub Copilot (VS Code) |
|---|---|---|
| Instructions | Import from `~/.claude/CLAUDE.md`, for example `@path/to/AGENTS.md` | `~/.copilot/copilot-instructions.md` |
| Skills | `~/.claude/skills/<name>/` | `~/.copilot/skills/<name>/` |
| Agents | `~/.claude/agents/<name>.md` | `~/.claude/agents/<name>.md` or `~/.copilot/agents/<name>.agent.md` |

## Team setup

Your team's agents, skills and rules can be installed on top of this kit with the same installer. [agd's guide to publishing a setup](https://github.com/Zejnilovic/agd/blob/main/docs/sources.md) shows how. Inside the project, the [kit-file rules](your-files.md) still apply.

## Only the ideas

[Working with coding agents](https://zejnilovic.eu/guides/working-with-coding-agents) is the method behind the kit, with principles, anti-patterns and nine exercises. It names no model or product, so it applies to whatever setup you use.
