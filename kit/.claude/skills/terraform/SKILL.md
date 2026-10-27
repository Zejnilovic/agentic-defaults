---
name: terraform
description: Practices for infrastructure as code with Terraform or OpenTofu, alone or with Terragrunt - modules and units, reading plans, moved blocks, state and S3 backends, secrets, version pinning, linting and terraform test. Use when writing or changing .tf or Terragrunt files, reading a plan, or reviewing such changes.
---

<!-- From agentic-defaults. Kit updates replace this file except a "## This project" section at the end, which belongs to the project. Edit nothing else. Rules for all work go in AGENTS.md "This project". -->

# Terraform

Infrastructure code changes live systems, and a destroyed database or bucket doesn't come back. You write the code and run plans; the user applies.

Follow the project first. Read the infrastructure's `CONTEXT.md`, one module or unit like the one you're changing, the backend settings and the version constraints. Use the project's wrapper (Terragrunt, make targets, scripts). The project's conventions win over this list, except the stop rules at the end. Everything here applies to OpenTofu too (`tofu` instead of `terraform`).

## Plan, never apply

- Run `terraform plan`, `terragrunt plan` or `terragrunt run --all plan` as often as you need.
- Never run `apply`, `destroy`, `import` on the command line, `state mv`, `state rm`, `state push`, `force-unlock`, `taint`, `init -migrate-state`, or `terragrunt backend bootstrap` (or `--backend-bootstrap`). They change live resources or state.
- Never pass `-auto-approve`, `-lock=false` or Terragrunt's `--non-interactive`, which answers yes to every prompt. A plan holds the state lock while it runs; if a lock is stuck, report it.
- When the change is ready, hand the user the apply command, the folder to run it from, and the plan's summary line (`N to add, N to change, N to destroy`). `terragrunt run --all apply` and `destroy` skip the confirmation prompt, and `run --all destroy` also destroys the units' dependencies: say so when you hand one over.

## Read every plan

- Read the whole plan, not only the summary. Name the reason for every destroy and every `-/+` (must be replaced). Replacing a database, bucket, volume, key or DNS zone loses what it holds.
- A rename looks like destroy plus create, like a dropped column. Keep the object with a `moved` block. To stop managing something without destroying it, use a `removed` block with `lifecycle { destroy = false }`.
- Changes your code didn't cause (drift, someone's console change, a provider upgrade) also show up. List them in your report; don't change code to absorb them unless asked.
- To bring an existing resource under management, write an `import` block for the user to apply, and draft its code with `terraform plan -generate-config-out=generated.tf`.

## Structure

- Modules hold the logic. Root configurations or Terragrunt units only wire modules together per environment.
- Every variable has a `type` and a `description`; add `validation` blocks for values with rules. Mark secrets `sensitive = true`.
- Use `for_each` for collections, not `count`: removing one item from a `count` list shifts the rest, and Terraform recreates them.
- No hard-coded account IDs, regions, ARNs or image IDs in modules. Pass them in or look them up with data sources.
- Stateful resources get `lifecycle { prevent_destroy = true }` or the provider's deletion protection.
- Run `terraform fmt`. If the project uses terraform-docs, regenerate a module's README after changing its variables or outputs.

## Versions and providers

- Constrain `required_version` and every provider (`~> 5.0`). Pin module sources to a version or tag, never a branch.
- Commit `.terraform.lock.hcl`. After changing providers, record hashes for every platform the team and CI use, for example `terraform providers lock -platform=darwin_arm64 -platform=linux_amd64`.
- Before using a resource or argument that is new to the project, check it against the provider version in the lock file: `terraform providers schema -json` (filter it with `jq`) or that version's documentation. Never guess argument names.

## State and secrets

- State is remote and locked, in the backend the project already uses. Never edit state by hand.
- State and saved plan files (`-out`) hold sensitive values in plain text. Never commit a plan file, and don't print state: no `terraform show` of state, `state pull`, `output -json` or `output -raw`. `state list` is fine.
- Keep secrets out of code and `.tfvars`. Read them from the secret store with a data source, or, from Terraform 1.10, an `ephemeral` resource, and from 1.11 pass them through write-only arguments (`*_wo`), which stay out of state.
- S3 backend: from Terraform 1.10, `use_lockfile = true` locks with a file in the bucket; DynamoDB locking (`dynamodb_table`) is deprecated. Both can be set while moving over. A backend change is the user's: propose it, don't make it.

## Terragrunt

- A unit is a folder with a `terragrunt.hcl` and its own state; a stack is a tree of units or a `terragrunt.stack.hcl`. The shared root config is `root.hcl` (a root `terragrunt.hcl` in older projects).
- Keep units thin: `include` the root, point `terraform { source = ... }` at a versioned module, and pass `inputs`. Logic goes in modules.
- Give `dependency` blocks `mock_outputs` limited to `validate` and `plan` (`mock_outputs_allowed_terraform_commands`), so plans work before the dependency exists.
- Use the syntax of the project's Terragrunt version: `run --all` replaced the deprecated `run-all`. Don't edit files that `generate` blocks write, and keep `.terragrunt-cache` in `.gitignore`.

## Tests

- Every change: run what the project has, in this order: `terraform fmt -check -recursive`, `terraform validate`, TFLint, a scanner such as Trivy or Checkov, and `terraform test`. Then a plan whose changes you can explain line by line.
- If the project lacks TFLint, a scanner, pre-commit hooks or a committed lock file, suggest them once in your report. Don't add them yourself.
- Modules with logic (conditionals, `for_each` over inputs, validations) get `terraform test` files (`tests/*.tftest.hcl`). Test what the module decides, not that an input reaches an argument.
- Tests must not create real resources: a `run` block applies unless it sets `command = plan`. Use `command = plan` with `mock_provider` (Terraform 1.7 and later) so tests need no credentials. Check validation rules with `expect_failures`.

## Stop and report before

- anything in "Plan, never apply": hand the user the command instead,
- a plan that destroys or replaces a stateful resource, or anything you didn't intend,
- changing a backend, state key, workspace or a provider's major version,
- widening IAM permissions, opening network access or making storage public,
- removing `prevent_destroy` or deletion protection.
