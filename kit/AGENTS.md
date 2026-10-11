<!-- agentic-defaults 0.1.0. Everything above "This project" comes from the kit; update it with the kit's scripts/sync.sh. -->

# Working agreement

These rules apply to every task in this repository. Project-specific details go in the section at the end of this file, or in the nearest `CONTEXT.md`.

## Deliver

- Solve the problem that was asked. Make the smallest change that delivers it end to end.
- Match the process to the size of the change. A small change goes straight to implementation. A change that spans modules or needs a design decision gets a short plan first.
- Prefer a working, tested slice now over a complete design later. Don't add abstractions, options or extension points that no current requirement needs.
- Follow the patterns already in the codebase. Leave unrelated code alone; if you notice something worth fixing, mention it instead of fixing it.
- Add a dependency only when the task needs it. If an install fails, stop: never try a similarly named package, which may be fake or malicious.
- State the assumptions you made. Ask only when a decision is genuinely the user's and there is no sensible default.

## Test

- Change behavior test-first: write a failing test, make it pass, then tidy up. Fix bugs by reproducing them in a test first. The `tdd` skill has the full loop.
- Aim for reasonable coverage, not total coverage. Test the behavior callers rely on, the edge cases real input produces, and every bug you fix. Don't test trivial code, the framework doing its job, or states that can't happen.
- Before calling work done, run the relevant tests and report the result honestly, including failures.

## Context

- Start from what's written down. Read the root `CONTEXT.md` and the nearest one for the area you're changing. If the project has no root `CONTEXT.md`, suggest a project scan (the `project-scan` skill) before larger work.
- Work that spans several steps, sessions or agents has a plan file in the plans folder named below. Read it before starting, and keep it current as the `task-plans` skill describes.
- `.local_context/` holds a person's private notes: tickets, meeting notes, specs, logs. Read it when discovering or planning a task. It is never committed: summarize what matters into plans or docs, never copy secrets or personal data out of it, and trust the code when the notes disagree.
- `CONTEXT.md`, `AGENTS.md` and plan files are written for AI agents: dense, exact, stable facts. `README.md` and `docs/` are written for people. Link between them rather than copying.
- Updating `CONTEXT.md` is part of the change, not a follow-up. If your change makes a `CONTEXT.md` or a diagram in it wrong or incomplete, fix it in the same change. The `context-md` skill says what belongs in it.

## Work economically

- Search before you read, and read only the parts of files the task needs.
- Don't re-read files you have just read or edited, and don't repeat large outputs back.
- Run the narrowest command that answers the question: one test file before the whole suite.
- If something fails twice the same way, stop and rethink instead of retrying variations.
- Hand work to an agent only when it benefits from a separate context; small tasks are cheaper to do directly. When you do, give the agent everything it needs in the request (the goal, the plan step, relevant file paths and constraints), because it can't see this conversation.

## Done means

- The requested behavior works and is covered by tests.
- The tests pass, or the failures are reported with their output.
- Affected `CONTEXT.md` files and the plan file, if there is one, are updated. `.claude/skills/context-md/check.sh` lists the `CONTEXT.md` files to look at.
- There are no unrelated changes.

---

## This project

<!-- Replace with project specifics, or let a project scan fill this in. Commands matter most: agents use them constantly. -->

- Plans: `docs/plans/`. Finished plans are deleted once their decisions are in `CONTEXT.md`.
- Build: `...`
- Test (all): `...`
- Test (single file or test): `...`
- Lint / format: `...`
