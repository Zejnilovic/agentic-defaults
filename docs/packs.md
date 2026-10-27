---
description: The packs Zejnilovic's agentic defaults comes in, and how to choose them.
---

# Packs

The kit comes in packs, so a project gets only the frameworks it uses. Fewer agents mean a shorter agent list in Copilot and less guessing when Claude Code picks one.

| Pack | Contents | Requires |
|---|---|---|
| `core` | The working agreement, `.local_context/`, the analyst, architect, developer, tester, reviewer, security reviewer and documenter, the skills they use, and `session-retro` | |
| `research` | The research collector and the researcher, and the `research` skill | `core` |
| `flask` | The Flask developer and the `flask` skill | `core` |
| `spring` | The Spring developer and the `spring` skill | `core` |
| `react` | The React developer and the `react` skill | `core` |
| `relational-database` | The relational database developer and the `relational-database` skill | `core` |
| `terraform` | The Terraform developer and the `terraform` skill | `core` |
| `heroku` | The `heroku` skill | `core` |
| `aws` | The `aws` skill | `core` |
| `copilot-hook` | The end-of-turn [context check](context.md) for Copilot | `core` |

The exact file list is in [`packs.txt`](https://github.com/Zejnilovic/agentic-defaults/blob/master/packs.txt).

## Choose packs

`agd init` installs every pack. To install only some, name them; `core` comes along:

```bash
agd init --with flask,react
```

Adding or removing packs later, and keeping single files out, are covered in [agd's documentation](https://zejnilovic.github.io/agd).
