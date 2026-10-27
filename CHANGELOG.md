# Changelog

What changed in the kit. The next version's changes are collected here; each released version's notes, including manual steps for existing copies, are on its GitHub release, linked below. To see what an update would change in a project, run `agd status` there.

Version numbers: **major** when something is renamed or removed and existing copies need manual changes, **minor** for new agents, skills or rules, **patch** for wording and fixes. Before 1.0, a minor version may also need manual changes; its notes list them under "Manual steps". Each release is a git tag (`v0.1.0`), and the first line of a project's `AGENTS.md` shows which version its copy came from.

## 0.5.0 (unreleased)

- **`session-retro` skill** (core pack): when the user asks for a retro, the agent evaluates the session on evidence: each requirement met or not, the user's prompts labeled request, answer, correction or complaint, rework after "done", the "Done means" rules, and cost against the project's earlier retros. Fixed rules turn the misses into a verdict (went well, mixed, went badly), which the user confirms. The note in `.local_context/feedback/<date>-<task>.md` names the kit file behind each miss by its installed path, with whether its rule was missing, wrong, ignored or too long, and a project-only or generic fix; a row in `.local_context/feedback/log.tsv` builds the baseline. For a generic fix the agent suggests `agd feedback <note>`; it never sends anything itself. `.local_context/README.md` mentions the `feedback/` folder.
- **`session-retro/stats.sh`**: a read-only script that the retro runs in Claude Code for its Cost section. From Claude Code's local session files it counts time, models, tokens, prompts, interrupts, denied and failed tool calls, and subagents; from git, commits and lines since the session started and uncommitted changes; from `log.tsv`, the medians of the last 10 retros. It prints counts only, never session text, except `--prompts`, which lists the user's prompts for the agent to label locally. The session numbers need jq; without it the script says so and prints the git numbers. The session files are an undocumented format, so the numbers can break with a Claude Code update.
- **Needs agd 0.2.0**: `packs.txt` sets `min-agd 0.2.0`, the release that adds `agd feedback`.
- **`heroku` skill** (new `heroku` pack): practices for apps deployed on Heroku. The agent runs only read-only CLI commands and hands every deploy, config change, scale, rollback, add-on or `pg:` command to the user as an exact command with `-a <app>`; it never runs `heroku config` without a name, since that prints every secret. Covers `$PORT` and boot time, `SIGTERM` and daily restarts, the ephemeral filesystem, the 30-second router timeout, config vars, release-phase migrations that work with old and new code, Postgres connection caps, pipelines and review apps, Scheduler jobs that may run twice, and planning a move off Heroku.
- **The user changes live systems** (core): a new rule in the working agreement and a "Live systems" section in the `implementation` skill. Agents run plans, dry runs and read-only commands, and hand every apply, deploy, scale, rollback or resource change to the user as an exact command with its folder. They skip read-only commands that print secrets, such as `terraform output -json`. The `project-profile` skill's "Always" list, the developer's fallback essentials and the methodology's "Bound the agent" principle say the same.
- **`terraform` skill and `terraform-developer`** (new `terraform` pack): Terraform, OpenTofu and Terragrunt. Plan as often as needed, never apply, and never pass `-auto-approve`, `-lock=false` or `--non-interactive`; `terragrunt run --all apply` skips its prompt, which the handover says. Read every plan and explain each destroy or replace, `moved` and `removed` blocks, `import` blocks with generated config, `for_each` over `count`, version pins and lock-file hashes for every platform, checking arguments in the provider schema, secrets kept out of state with ephemeral resources and write-only arguments, S3 `use_lockfile` replacing deprecated DynamoDB locking, thin Terragrunt units with `root.hcl`, and `terraform test` with `command = plan` and mock providers. The agent suggests missing TFLint, scanners or pre-commit hooks and doesn't add them.
- **`aws` skill** (new `aws` pack): short-lived credentials and `aws sts get-caller-identity` before working, read-only CLI commands versus those handed to the user, never printing secrets, least-privilege IAM, no public buckets or `0.0.0.0/0` ingress, encryption, and the costs of idle resources, NAT gateways, public IPv4 and log retention.
- **Security reviewer**: also reports infrastructure code that makes storage public, opens ports to the internet, uses wildcard IAM or leaves storage unencrypted.
- **`project-scan` survey**: also lists `root.hcl`, `terragrunt.hcl`, `.terraform.lock.hcl`, `.tflint.hcl`, `.pre-commit-config.yaml` and `Procfile`.

Manual steps for existing copies:

- Upgrade agd to 0.2.0 or newer, then run `agd update`. An older agd stops and asks you to upgrade.
- Add the new packs where they fit, for example `agd add terraform` and `agd add aws`.

## Released

- [0.4.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.4.0) (2026-10-24)
- [0.3.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.3.0) (2026-10-24)
- [0.2.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.2.0) (2026-10-21)
- [0.1.0](https://github.com/Zejnilovic/agentic-defaults/releases/tag/v0.1.0) (2026-10-11)
