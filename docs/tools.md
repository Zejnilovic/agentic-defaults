---
description: How Zejnilovic's agentic defaults works in Claude Code and in GitHub Copilot, and where the two differ.
---

# Claude Code and Copilot

Everything in the kit works in both **Claude Code** and **GitHub Copilot** (VS Code). **GitHub Copilot CLI** reads it too, once you [change the agents' `model:` lines](#model-per-agent). It's plain Markdown, shell scripts and JSON in the formats these tools read. Other tools that read `AGENTS.md`, such as Cursor, get the working agreement; the skills and agents have only been tested in Claude Code and Copilot.

## Where they differ

| | Claude Code | GitHub Copilot (VS Code) | GitHub Copilot CLI |
|---|---|---|---|
| Working agreement | `CLAUDE.md` imports `AGENTS.md` | Reads `AGENTS.md` directly | Reads `AGENTS.md` and `CLAUDE.md`, which imports it, so the text loads twice. If only Copilot uses the project, list `CLAUDE.md` in `.agd-ignore`. A subagent reads it because the kit's agents set `include-custom-instructions: true` |
| Skills | Loaded when relevant; an agent's `skills:` list preloads them | Reads `.claude/skills/` and loads them when relevant; ignores `skills:`, so each agent also names its skills and keeps a short fallback | Reads `.claude/skills/` and loads them when relevant; an agent's `skills:` list preloads them |
| Agents | Subagents, chosen by their description or by name | Modes in the agent dropdown, or subagents once **Run Subagent** is enabled under Configure Tools | Reads `.claude/agents/`. Subagents, or `--agent <name>` for a whole session |
| Model per agent | The agent's `model:` field | The model selected in the chat, or `model` in a `.github/agents/<name>.agent.md` copy | The agent's `model:` field, but [not `haiku` or `sonnet`](#model-per-agent) |
| Scripts, `make`, `gh` | Run in the terminal | The same; agent mode runs terminal commands | The same; it asks first unless you allow the tool |
| End-of-turn context check | A `Stop` hook you add to `.claude/settings.json` | `.github/hooks/context-check.json`, shipped with the kit | The same file, [in a folder you trust](context.md) |
| Web research | Built-in web search and page fetching | The fetch tool for pages; without web access, the research agents fall back to local sources and say so | Not tested |

Copilot in VS Code follows the VS Code and GitHub documentation. Everything except the Copilot hook has been used in a project; check the hook in your first VS Code session. The CLI column comes from real sessions with Copilot CLI 1.0.105 on macOS, in November 2026.

## Model per agent

"Strong" means your best reasoning model; "everyday" means a fast, inexpensive one.

=== "Claude Code"

    Claude Code reads each agent's `model` field: `sonnet` for strong roles and `haiku` for everyday ones. Change it to suit you; `inherit` uses the conversation's model. Kit updates keep your change.

=== "GitHub Copilot"

    Copilot in VS Code doesn't read `model` from `.claude/agents` files, so an agent uses whichever model is selected in the chat. Use your everyday model by default and switch to a strong one for the architect and reviewers.

    To pin a model, copy the agent to `.github/agents/<name>.agent.md` and set `model` to a name from Copilot's model picker.

=== "GitHub Copilot CLI"

    Copilot CLI reads `model` from `.claude/agents` files, but doesn't recognize `haiku` or `sonnet`. Called as a subagent, such an agent fails with `Model 'haiku' is not available`, and the main conversation then does the work itself or retries on another model. Started with `--agent`, it warns and uses the session's model.

    So change the lines to `inherit`, which both tools read, though Claude Code then uses the conversation's model too:

    ```bash
    perl -pi -e 's/^model: .*/model: inherit/' .claude/agents/*.md
    ```

    Kit updates keep these lines. If only Copilot uses the project, you can pick a tier per agent with an ID from `/model`, such as `claude-haiku-4.5`.

    To leave the project's files alone, set it for yourself with `/subagents`, or `subagents.agents.<name>.model` in `~/.copilot/settings.json`. The same setting in the repository's `.github/copilot/settings.json` has no effect.

## Where the files go

See [What's inside](inside.md#where-the-files-go) for project files and [Personal setup](paths.md#personal-setup) for your home folder.
