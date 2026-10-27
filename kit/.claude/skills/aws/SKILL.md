---
name: aws
description: Practices for working with AWS - credentials, profiles and accounts, which aws CLI commands an agent may run and which it hands to the user, least-privilege IAM, public exposure, encryption, tagging and cost traps, in Terraform or application code. Use when a change creates, configures or calls AWS resources, or before running the aws CLI.
---

<!-- From agentic-defaults. Kit updates replace this file except a "## This project" section at the end, which belongs to the project. Edit nothing else. Rules for all work go in AGENTS.md "This project". -->

# AWS

A wrong command in the wrong account changes production at once, and many AWS mistakes are either public exposure or a monthly bill. This skill covers what doesn't depend on the service; for a service's details, read its documentation.

Follow the project first. Read the infrastructure's `CONTEXT.md` for its accounts, regions, profiles, naming and tags, and reuse the modules it already has. The project's conventions win over this list, except the stop rules at the end.

## Credentials and accounts

- Use the profile or role the project names (`AWS_PROFILE` or `--profile`), with short-lived credentials from IAM Identity Center (`aws sso login`) or an assumed role. If they have expired, ask the user to log in.
- Never create access keys, never use the root user, and never write credentials into code, `.tfvars`, files or the conversation.
- Before running commands in a session, run `aws sts get-caller-identity` and check the account and role. Stop if it isn't the account the task names.
- CI assumes a role through OIDC federation (for example `aws-actions/configure-aws-credentials` in GitHub Actions), not stored keys. Application code takes credentials from the SDK's default chain (the task, function or instance role), never from its own config.

## The CLI

- **Run freely** (read-only): `describe-*`, `list-*`, most `get-*`, `aws s3 ls`, `aws logs tail` with a time limit. Add `--no-cli-pager`, the region (`--region` or the profile's), and `--query` to keep the output short.
- **Never print secrets**: no `secretsmanager get-secret-value`, no `ssm get-parameter --with-decryption`, nothing that returns keys or passwords. Refer to them by name or ARN.
- **Hand to the user**, as the exact command with `--profile` and `--region` and one line on what it does: every command that creates, changes, deletes, starts, stops or invokes something, including `aws s3 cp`, `sync` and `rm`. If the project manages the resource with Terraform, the change belongs in Terraform, not the CLI.

## IAM

- Least privilege: name the actions and the resource ARNs. No `"Action": "*"` or `"Resource": "*"`, except for actions that don't support resource-level permissions, and say which in a comment.
- One role per workload. No IAM users for applications.
- A resource policy with `"Principal": "*"` needs a condition that narrows it. When a policy trusts an AWS service, add `aws:SourceAccount` or `aws:SourceArn`.
- Trust another account only when the task says so.

## Exposure and encryption

- S3: keep Block Public Access on and ACLs disabled (object ownership "bucket owner enforced"), the defaults for new buckets. Serve public files through CloudFront with origin access control, not a public bucket.
- Security groups: no ingress from `0.0.0.0/0` or `::/0` except 80 and 443 on a load balancer. No SSH or database ports from the internet; use Session Manager for shell access.
- Databases and caches go in private subnets, not publicly accessible.
- Encrypt storage at rest (RDS, EBS, EFS, backups) and use TLS in transit. `(sensitive)`: customer-managed KMS keys, and bucket policies that deny requests without `aws:SecureTransport`.
- `(production)`: deletion protection and automated backups on databases, versioning on buckets whose data matters, and CloudTrail left on.

## Cost

- In your report, name each new resource that costs money while idle: NAT gateways (also charged per GB), load balancers, provisioned databases and caches, interface VPC endpoints, and public IPv4 addresses, which all cost money.
- Send S3 and DynamoDB traffic from private subnets through gateway endpoints, which are free, instead of a NAT gateway.
- Set a retention period on CloudWatch log groups; the default keeps logs forever.
- Tag every resource with the project's tags, in Terraform through the provider's `default_tags`.

## Tests

- Test application code that calls AWS against the project's mocks or emulator (for example moto for Python, or the SDK's stubber), never a real account.
- Check infrastructure with plans and the `terraform` skill's tests, not by creating resources to see what happens.

## Stop and report before

- any command from "Hand to the user": give the command instead,
- working in an account or region the task didn't name,
- IAM changes that add wildcards, trust another account or let a role change IAM,
- making anything public: buckets, snapshots, images, `0.0.0.0/0` ingress, database endpoints,
- turning off encryption, CloudTrail, deletion protection or backups,
- adding a resource that costs money while idle.
