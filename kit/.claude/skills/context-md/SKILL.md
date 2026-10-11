---
name: context-md
description: Write and maintain CONTEXT.md files, the per-directory notes that give AI agents the facts, conventions, decisions and gotchas they can't quickly get from the code. Use when creating a module, when a change makes a CONTEXT.md wrong or incomplete, or when asked to document a directory for agents.
---

# CONTEXT.md files

A `CONTEXT.md` gives an AI agent what it can't quickly learn from the code: what this part is for, how it is meant to be used, the rules it relies on, and what will bite. People can read it too, but agents are the audience.

- **For agents:** `CONTEXT.md` (what the code is), `AGENTS.md` (how to work), plan files (what is being done).
- **For people:** `README.md` and guides under `docs/`. Don't copy content between the two kinds; link instead.

## Write for an agent

- Dense and scannable: short lines, lists and tables, no narrative, no marketing, no emojis.
- Exact names: file paths, classes, functions, endpoints, environment variables, commands. Agents search for them.
- State rules as rules: "Never expose integer primary keys; use `public_id`."
- Only stable facts. Leave out what goes stale on its own: test counts, coverage numbers, open issues, current status, "last updated" dates. The test run, the issue tracker and git hold those.
- No content a quick read of the code gives: lists of every function, file-by-file descriptions.

## Where

- One at the repository root: an index of the system that points to the rest. The `project-scan` skill describes its shape.
- One in each area whose design isn't obvious from the code, typically a module, package, service, or the backend and frontend of an app.
- Not every folder needs one. No `CONTEXT.md` is better than one that restates the file list.
- Agents read the nearest one, walking up from the file they're changing, so put detail where it's used: backend detail in `backend/CONTEXT.md`, not the root.

## Size

Every line costs tokens each time an agent reads the file. Aim for about 150 lines at the root and 80 in an area. When a file grows past that, move area detail down into that area's `CONTEXT.md` rather than cutting facts agents need.

## What goes in

Start from [template.md](template.md).

- **Purpose**: what this part is responsible for, and what it deliberately isn't.
- **How it fits**: entry points, who calls it, what it depends on. Add a diagram when the flow or structure is easier to show than to list (see the `diagrams` skill).
- **Conventions**: patterns code here must follow.
- **Key decisions**: choices a reader might question, one line each with the reason. If the project keeps decision records (for example `docs/adr/`), link the record instead of repeating it.
- **Invariants and gotchas**: rules the code relies on, traps, non-obvious behavior.

Record a decision's reason only if you actually know it, from the user, a decision record, code comments, commit messages or existing docs. Never invent a rationale. If the reason is unknown, write "reason unknown" so agents know to ask before changing it.

## When to update

Update it in the same change when you:

- add, remove, rename or move a module, or change what it's responsible for,
- change an interface, data model or behavior that other code depends on,
- make or reverse a design decision, or add a constraint,
- discover a gotcha the hard way.

No update is needed for internal refactors, bug fixes that restore documented behavior, or test-only changes.

## How to update

1. Find the affected files: the nearest `CONTEXT.md` above each changed file, plus the root one if the change crosses areas. [check.sh](check.sh) lists them: `bash <this skill's folder>/check.sh` for uncommitted changes, add `--base origin/main` for a branch. It flags candidates; you decide whether each needs an update.
2. Edit only what is now wrong or missing. Don't rewrite whole files.
3. Delete statements that are no longer true. Stale context is worse than none.
4. If a directory has gained non-obvious design and has no `CONTEXT.md`, create one from the template.

## Adding CONTEXT.md to an existing project

1. Write the root `CONTEXT.md` first, as an index: what the system does, its main parts and how they connect, and where to read next.
2. Add one to an area only where reading the code turned up something non-obvious: a convention, a decision, a constraint or a trap.
3. If an existing `CONTEXT.md` or similar file is too long or mixes in volatile facts, split it by area and drop the volatile parts. Keep every stable fact somewhere.
4. Mark anything you inferred rather than confirmed with "(unverified)".
5. List the files you created and the "(unverified)" points, so a person can review them.
