---
description: Install Zejnilovic's agentic defaults in a project, scan it, and start working, in four steps.
---

# Quick start

Four steps from nothing to your first task. This page assumes a project in git and either Claude Code or GitHub Copilot in VS Code. If your situation is different, [choose your path](paths.md) first.

## 1. Install agd

The kit is installed with [agd](https://zejnilovic.github.io/agd), a small installer that copies it into a project and updates it later.

=== "Homebrew"

    ```bash
    brew install zejnilovic/tap/agd
    ```

=== "Install script"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/Zejnilovic/agd/main/install.sh | bash
    ```

## 2. Add the kit

In your project's root:

```bash
agd init
```

That installs every [pack](packs.md). To install only some, name them; the packs they need come along:

```bash
agd init --with flask,react
```

!!! tip "Using Copilot?"
    Add `copilot-hook` to the list, for example `agd init --with react,copilot-hook`. It runs the [context check](context.md) at the end of every agent turn.

Commit the new files together with `.agd.lock`.

## 3. Scan the project

Ask your assistant:

> Use the analyst to scan this project.

The analyst writes the root `CONTEXT.md`, proposes a [project profile](project.md#project-profile), and fills in the [standard commands](project.md#standard-commands) in `AGENTS.md`, proposing any that are missing. Review what it wrote and confirm it.

## 4. Work

- **Small changes:** just chat. The working agreement applies on its own.
- **Bigger changes:** give it the ticket number, or put your notes in `.local_context/<task>/`, and follow [How work flows](workflow.md).

## Recommended tools

The skills use these when they're installed and fall back to git and plain searches when they're not.

=== "macOS"

    ```bash
    brew install ripgrep fd tree ast-grep jq yq scc
    ```

=== "Mermaid CLI"

    Lets agents check that a diagram renders.

    ```bash
    npm install -g @mermaid-js/mermaid-cli
    ```
