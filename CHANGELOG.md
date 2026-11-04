# Changelog

What changed in the kit. The next version's changes are collected here; each released version's notes, including manual steps for existing copies, are on its GitHub release, linked below. To see what an update would change in a project, run `agd status` there.

Version numbers: **major** when something is renamed or removed and existing copies need manual changes, **minor** for new agents, skills or rules, **patch** for wording and fixes. Before 1.0, a minor version may also need manual changes; its notes list them under "Manual steps". A bullet can end with issue markers: `(#12)` closes #12 when the version is released, and `(ref #20, #12)` also comments on #20 and leaves it open. Each release is a git tag (`v0.1.0`), and the first line of a project's `AGENTS.md` shows which version its copy came from.

## 0.5.4 (unreleased)

- Agents read the working agreement as Copilot CLI subagents. Each agent now sets `include-custom-instructions: true`; without it, a subagent got only its own file and the skills it lists. Claude Code ignores the line, and `check.py` requires it.
- The README and the site now cover Copilot CLI, from real sessions with 1.0.105 on macOS. It finds the kit's skills and agents and runs the `copilot-hook` pack in a folder you trust. It doesn't recognize the agents' `haiku` and `sonnet`, so a subagent fails until you change its `model:` line to `inherit` or a Copilot model ID; the docs show how.
- The README no longer says agd can't install into your home folder, and says how to reach Copilot CLI from there.
- Company knowledge has a place: "This project" in `AGENTS.md` gets a "Company knowledge" heading for one-line pointers, `docs/your-files.md` shows how, and the project scan asks about it. Updates keep a project's existing "This project", so existing copies add the heading by hand.
- The `aws` skill makes querying with read-only commands the default.
- The `terraform` skill runs `terragrunt hcl fmt --check` and `terragrunt hcl validate`, because `terraform fmt` doesn't check `terragrunt.hcl` files. At handover it names the role or profile and says a plan can't prove the apply is allowed. `terraform-developer` does the same.
- The security reviewer checks security requirements that `AGENTS.md` or `CONTEXT.md` link to, and the `aws` and `terraform` stop rules.

## Released

- [0.5.3](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.5.3) (2026-11-01)
- [0.5.2](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.5.2) (2026-10-28)
- [0.5.1](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.5.1) (2026-10-27)
- [0.5.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.5.0) (2026-10-27)
- [0.4.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.4.0) (2026-10-24)
- [0.3.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.3.0) (2026-10-24)
- [0.2.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.2.0) (2026-10-21)
- [0.1.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.1.0) (2026-10-11)
