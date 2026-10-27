---
description: The agents in Zejnilovic's agentic defaults, what each one does, what it may edit and which model tier it uses.
---

# Agents

Agents are roles: who does the work. Each one returns its result to you, or to the main conversation; roles never call each other, which keeps cost predictable.

**Model tiers.** "Strong" means your best reasoning model; "everyday" means a fast, inexpensive one. See [model tiers per tool](tools.md#model-per-agent).

## Plan and design

| Role | Does | Edits | Tier |
|---|---|---|---|
| [`analyst`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/agents/analyst.md) | Scans the project, and turns a ticket and notes into the discovery part of a plan. | Docs and plans | Everyday |
| [`research-collector`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/agents/research-collector.md) | Gathers sources on a question into notes, for the researcher or a person. Doesn't judge. | Research notes | Everyday |
| [`researcher`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/agents/researcher.md) | Answers a question that needs outside knowledge: options, a recommendation, confidence and sources. | Research notes | Strong |
| [`architect`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/agents/architect.md) | Designs the approach, contract first, writes steps, diagrams and decisions into the plan, and decides blockers. | Plans and design docs | Strong |

## Build

| Role | Does | Edits | Tier |
|---|---|---|---|
| [`relational-database-developer`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/agents/relational-database-developer.md) | Schema changes, migrations, indexes, queries and data fixes, with strict stop rules for anything irreversible. | Migrations, queries, tests | Everyday |
| [`terraform-developer`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/agents/terraform-developer.md) | Terraform, OpenTofu and Terragrunt modules and units, checked with plans. Never applies: hands you the command. | Infrastructure code, tests, docs | Everyday |
| [`flask-developer`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/agents/flask-developer.md) | Python Flask endpoints, services, jobs and integrations. | Server code, tests, docs | Everyday |
| [`spring-developer`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/agents/spring-developer.md) | Java Spring Boot controllers, services, repositories and configuration. | Server code, tests, docs | Everyday |
| [`react-developer`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/agents/react-developer.md) | React pages, components, hooks, forms and API calls. | UI code, tests, docs | Everyday |
| [`developer`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/agents/developer.md) | Anything no framework developer covers: scripts, tools, libraries, infrastructure, other stacks. | Code, tests, docs | Everyday |

All developers share the [`implementation`](skills.md#everyday-practice) skill's rules, and each framework developer adds its framework's skill.

## Check and finish

| Role | Does | Edits | Tier |
|---|---|---|---|
| [`tester`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/agents/tester.md) | Finds untested behavior that matters, writes the tests, reports bugs. | Tests only | Everyday |
| [`reviewer`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/agents/reviewer.md) | Checks that a plan's goal was actually met, and reviews a change for bugs, broken contracts, weakened tests, stand-ins, stale docs and over-engineering. | Nothing | Strong |
| [`security-reviewer`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/agents/security-reviewer.md) | Reviews a change for exploitable security problems, reporting only those with a plausible attack path. | Nothing | Strong |
| [`documenter`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/agents/documenter.md) | Keeps `CONTEXT.md` and docs true to the code, closes finished plans, and drafts ticket updates for handover. | Docs only | Everyday |

!!! note "Restrictions are instructions, not enforcement"
    "Edits tests only" is written in the agent's text. To enforce it, add a `tools` line to the agent. See [Customizing](your-files.md#customizing).
