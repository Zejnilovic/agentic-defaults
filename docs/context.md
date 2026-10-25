---
description: How Zejnilovic's agentic defaults keeps CONTEXT.md files true to the code, and how to run the context check automatically.
---

# Keep CONTEXT.md current

`CONTEXT.md` files are for agents, so agents keep them current: every task ends with a **context check**. Any single layer can slip, so the kit enforces it in several: the working agreement's definition of done, the developers' last step, the reviewer's checklist, and a check script in the [`context-md`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.claude/skills/context-md/SKILL.md) skill.

The script lists every `CONTEXT.md` whose area has code changes while the file itself didn't change:

```bash
bash .claude/skills/context-md/check.sh
```

It flags candidates; it can't tell whether an update is needed. Internal refactors and bug fixes that restore documented behavior need none.

## Run it automatically

Agents run the script themselves. You can also run it at three points.

### At the end of each agent turn

When code changed and a `CONTEXT.md` didn't, the agent gets one reminder and either updates the file or says why none is needed. The same finding is never raised twice.

=== "GitHub Copilot"

    The kit ships [`.github/hooks/context-check.json`](https://github.com/Zejnilovic/agentic-defaults/blob/master/kit/.github/hooks/context-check.json) in the `copilot-hook` pack, so it's on as soon as that pack is installed. It works in VS Code, the CLI and the cloud agent.

    - Copilot hooks are in preview in VS Code, and an organization can restrict them.
    - The cloud agent only reads hooks from the default branch.
    - The file follows GitHub's documentation but hasn't been tested in a real Copilot session yet.

    To turn it off, remove the `copilot-hook` pack.

=== "Claude Code"

    Add a Stop hook to `.claude/settings.json` (shared with the team) or `.claude/settings.local.json` (just you), merged with what's already there. The kit doesn't ship this file, because updating it would overwrite a project's own settings.

    ```json
    {
      "hooks": {
        "Stop": [
          {
            "hooks": [
              { "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/skills/context-md/check.sh\" --hook" }
            ]
          }
        ]
      }
    }
    ```

    Copilot in VS Code also reads `.claude/settings.json`. If both hooks are set up, the second call finds the same finding and stays silent.

### Before each commit

A reminder that doesn't block. Save this as `.git/hooks/pre-commit` and make it executable:

```bash
#!/usr/bin/env bash
bash .claude/skills/context-md/check.sh || true
```

### On pull requests

In GitHub Actions, check out with `fetch-depth: 0`, then add a step:

```yaml
- run: bash .claude/skills/context-md/check.sh --base origin/${{ github.base_ref }}
```

Add `--strict` to fail the build when there is something to check.
