---
description: Which parts of Zejnilovic's agentic defaults belong to the kit and which to your project, and how to customize the kit without losing updates.
---

# Kit files and your files

Kit files are replaced when the kit updates. Each one says so at the top with a "From agentic-defaults" marker, and in `AGENTS.md` everything above **This project** belongs to the kit.

Three parts of kit files belong to your project, and updates keep them:

- an agent's `model:` line,
- an agent's `tools:` line,
- a `## This project` section at the end of an agent or skill.

Agents are told never to edit anything else in kit files, and never to tell you to. When you ask for something specific to your project, they put it here instead:

| You ask for | It goes in |
|---|---|
| A rule or command for this project | "This project" in `AGENTS.md`, which every agent reads |
| A different model for an agent | That agent's `model:` line |
| Limits on what an agent may use | A `tools:` line in that agent |
| Extra instructions for one agent or skill | A `## This project` section at the end of that file |
| A fact or convention about part of the code | That area's `CONTEXT.md` |
| A project-only role or practice | A new agent or skill file with its own name; kit updates never touch it |
| Different behavior from a kit file | A copy under a new name, with the original listed in `.agd-ignore` |
| A change every project would benefit from | A [suggestion for this repository](feedback.md) |

## Updating

Updates replace kit files you haven't changed, keep the parts listed above, and never touch files that aren't the kit's. A kit file you changed elsewhere is left for you to review. Run:

```bash
agd update
```

The [releases](https://github.com/Zejnilovic/agentic-defaults/releases) list what changed, with manual steps where a project needs them, and [CHANGELOG.md](https://github.com/Zejnilovic/agentic-defaults/blob/master/CHANGELOG.md) has what's coming next. Reviewing and merging your changed files is covered in [agd's documentation](https://zejnilovic.github.io/agd).

## Customizing

**Restrictions are instructions, not enforcement.**
:   "Edits tests only" is written in the agent's text. To enforce it, add a `tools` list to the agent, for example `tools: Read, Grep, Glob, Bash` for a read-only reviewer. Claude Code uses these names directly, and VS Code maps them for files in `.claude/agents`. Check that the agent can still do its job afterwards. Kit updates keep the line, as they keep `model:`.

**`skills` in an agent's frontmatter**
:   Preloads those skills in Claude Code. Copilot ignores the field and loads skills when they're relevant.

**Another framework** (FastAPI, Django, Angular, Vue and so on)
:   Is a pair: a `<framework>` skill and a `<framework>-developer` agent. Copy the closest existing pair, keep the skill's sections (follow the project first, structure, the framework's own concerns, tests, stop and report before), and keep `implementation` in the agent's `skills` list so it follows the shared rules. Project-specific conventions go in the area's `CONTEXT.md`, not in the skill.
