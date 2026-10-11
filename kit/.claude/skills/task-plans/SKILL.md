---
name: task-plans
description: Turn notes about a task into a plan file that carries the goal, design and step checklist from discovery to done, and that agents use to hand work over. Use when starting work that spans several steps, sessions or agents, when turning .local_context notes into a plan, or when updating or closing a plan.
---

# Task plans

A plan file holds one task's goal, design and steps. It is the shared memory between sessions and agents: pass its path instead of re-explaining the task.

Small changes don't need one. Use a plan when the work spans several steps, more than one session, or more than one agent.

## Where

- In the plans folder named in `AGENTS.md` ("This project"), by default `docs/plans/`.
- One file per task, named with a short slug: `docs/plans/csv-export.md`.
- Raw notes for the same task live in `.local_context/<slug>/`, which is never committed.

## Format

Start from [template.md](template.md). Fill in only the sections the current stage needs, and keep the whole plan to about one page.

## Lifecycle

1. **Discovery** (status `discovery`). Read the notes in `.local_context/<slug>/`, the relevant `CONTEXT.md` files and only the code needed. Fill in Goal, Context, Requirements and Open questions.
   - Summarize the notes; don't paste them. Never copy secrets, credentials, personal data or customer data into the plan.
   - Notes can be outdated. When they disagree with the code, trust the code and add an open question.
2. **Planning** (status `planned`). Fill in Approach, Steps and Decisions. Resolve every open question, or record it under Risks as accepted.
   - Each step delivers a working, tested increment and names files, the test and a "done when".
   - Write steps concretely enough that a developer on a smaller model can do one without re-reading the whole design.
3. **Delivery** (status `in progress`). Work one step at a time and tick it off (`- [x]`) when its test passes. If a step turns out to be wrong, stop and update the plan before continuing, so the file stays true.
4. **Close** (status `done`). Move lasting decisions into the relevant `CONTEXT.md` files. Then delete the plan, unless `AGENTS.md` says to keep finished plans. Git keeps the history.

## Handing work to an agent

Pass the plan path and the step numbers, for example: "Implement steps 2–3 of `docs/plans/csv-export.md`." The agent reads the plan itself, so you don't need to repeat it.
