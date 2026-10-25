---
description: How Zejnilovic's agentic defaults works in Claude Code and in GitHub Copilot, and where the two differ.
---

# Claude Code and Copilot

Everything in the kit works in both **Claude Code** and **GitHub Copilot** (VS Code). It's plain Markdown, shell scripts and JSON in the formats both tools read. Other tools that read `AGENTS.md`, such as Cursor, get the working agreement; the skills and agents have only been tested in Claude Code and Copilot.

## Where they differ

| | Claude Code | GitHub Copilot (VS Code) |
|---|---|---|
| Working agreement | `CLAUDE.md` imports `AGENTS.md` | Reads `AGENTS.md` directly |
| Skills | Loaded when relevant; an agent's `skills:` list preloads them | Reads `.claude/skills/` and loads them when relevant; ignores `skills:`, so each agent also names its skills and keeps a short fallback |
| Agents | Subagents, chosen by their description or by name | Modes in the agent dropdown, or subagents once **Run Subagent** is enabled under Configure Tools |
| Model per agent | The agent's `model:` field | The model selected in the chat, or `model` in a `.github/agents/<name>.agent.md` copy |
| Scripts, `make`, `gh` | Run in the terminal | The same; agent mode runs terminal commands |
| End-of-turn context check | A `Stop` hook you add to `.claude/settings.json` | `.github/hooks/context-check.json`, shipped with the kit |
| Web research | Built-in web search and page fetching | The fetch tool for pages; without web access, the research agents fall back to local sources and say so |

Copilot support follows the VS Code and GitHub documentation. Everything except the Copilot hook has been used in a project; check the hook in your first Copilot session.

## Model per agent

"Strong" means your best reasoning model; "everyday" means a fast, inexpensive one.

=== "Claude Code"

    Claude Code reads each agent's `model` field: `sonnet` for strong roles and `haiku` for everyday ones. Change it to suit you; `inherit` uses the conversation's model. Kit updates keep your change.

=== "GitHub Copilot"

    Copilot in VS Code doesn't read `model` from `.claude/agents` files, so an agent uses whichever model is selected in the chat. Use your everyday model by default and switch to a strong one for the architect and reviewers.

    To pin a model, copy the agent to `.github/agents/<name>.agent.md` and set `model` to a name from Copilot's model picker.

## Where the files go

See [What's inside](inside.md#where-the-files-go) for project files and [Personal setup](paths.md#personal-setup) for your home folder.
