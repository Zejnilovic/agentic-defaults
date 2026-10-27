---
name: heroku
description: Practices for apps deployed on Heroku - Procfile and dynos, config vars, release phase migrations, Heroku Postgres, pipelines and review apps, Scheduler, logs, which heroku CLI commands an agent may run and which it hands to the user. Use when changing an app that runs on Heroku, its Procfile, app.json or runtime settings, when investigating a Heroku error or log, or when planning a move off Heroku.
---

<!-- From agentic-defaults. Kit updates replace this file except a "## This project" section at the end, which belongs to the project. Edit nothing else. Rules for all work go in AGENTS.md "This project". -->

# Heroku

Heroku runs the code you push, with settings from config vars and services from add-ons. A wrong command changes a live app at once, so this skill splits the CLI into what you may run and what you hand to the user.

Follow the project first. Read the root `CONTEXT.md`, the `Procfile`, `app.json` if there is one, and the runtime version file. The project's conventions win over this list, except the stop rules at the end.

## Commands you may run and commands you hand over

- **Run freely** (read-only): `heroku apps:info`, `heroku ps`, `heroku releases`, `heroku addons`, `heroku pg:info`, `heroku domains`, `heroku pipelines:info`, `heroku logs -n 200 --source app` (narrow it with `--dyno`), and `heroku local`.
- **Never run `heroku config` without a name.** It prints every secret into the conversation. Use `heroku config:get NAME` only for a value that isn't a secret, and refer to secrets by name only.
- **Hand to the user**, as the exact command with the app name (`-a <app>`) and one line on what it does: anything that deploys, changes config, scales, restarts, rolls back, or touches add-ons or data. That covers `git push heroku`, `config:set` and `config:unset`, `ps:scale`, `ps:restart`, `releases:rollback`, `pipelines:promote`, `stack:set`, `addons:create` and `addons:destroy`, `maintenance:on`, every `pg:` command except `pg:info`, and `heroku run` on anything but a review app. Never run them yourself, even when asked to "just deploy".
- Name the app in every command. Without `-a`, the CLI picks the app from the git remote, which may be production.

## Processes and dynos

- Every process type is a line in the `Procfile`. A `web` process must bind to `$PORT` within 60 seconds of starting (error R10).
- Dynos restart at least once a day and on every deploy or config change. On restart they get `SIGTERM` and 30 seconds to finish, then `SIGKILL`. Stop taking new work on `SIGTERM` and make jobs safe to run again.
- The filesystem is ephemeral and not shared between dynos. Uploads, generated files and caches go to object storage or an add-on, never to local disk.
- The router ends a request after 30 seconds (H12). Anything slower goes to a `worker` process through the project's queue.
- Memory over the dyno's quota shows as R14 and then R15. Fix the leak or the worker count before proposing a bigger dyno.

## Config vars

- All configuration comes from environment variables at boot. No per-environment config files, and no secrets in the repository or `app.json`.
- Changing a config var creates a release and restarts the app.
- Add-ons set and rotate their own variables (`DATABASE_URL`, `REDIS_URL` and so on). Read them from the environment at boot; never copy a value into another variable or file.
- A new variable the code needs ships with a safe default, or the user sets it before the deploy. Name it in your report with the command for them to run.

## Release phase and migrations

- The `release:` line in the `Procfile` runs after the build and before the new code starts. If it fails, the release doesn't happen. Put database migrations there, not in the `web` command.
- The old code keeps serving while the release command runs and until the new dynos are up, so every migration must work with the old code and the new code at once: expand, then contract (the `relational-database` skill, if installed).
- The release command must be safe to run twice, finish well within the release timeout, and print enough to diagnose a failure in `heroku releases:output`.
- Before a release that changes data, hand the user `heroku pg:backups:capture -a <app>`.

## Heroku Postgres and other add-ons

- Each plan caps connections. Size the pool as dynos × processes × threads per process, and stay under the cap; use the project's pooler if it has one.
- Production data stays in production. Don't propose copying it to review apps or local machines unless the user decides to, with personal data removed.
- Add an add-on only when the task needs it; it is a dependency and a cost. Write it into `app.json` for review apps too.

## Pipelines, review apps and Scheduler

- A pipeline promotes the same build from staging to production. Config vars aren't promoted: a new variable must be set on each app.
- Review apps are built from `app.json`: its `env`, `addons`, `formation` and `scripts.postdeploy`. Keep `app.json` in step with what the app needs to boot.
- Heroku Scheduler is best effort: a job can be skipped or run twice. Jobs must be safe to repeat, and anything that must run exactly once needs a lock or a record of what was done.

## Runtime and stack

- Pin the language version the way the buildpack reads it (for example `.python-version`, `engines` in `package.json`, `system.properties`) and keep it equal to local and CI.
- Check the app's stack and generation with `heroku apps:info` before relying on buildpack behavior, and read Heroku's documentation for that stack. Changing the stack is the user's call.

## Moving off Heroku

Heroku moved to maintenance-only development in 2026: no shutdown, but no new features. A move is a project of its own, not a side effect of another task.

- Inventory first: process types and their dyno sizes and counts, add-ons and their plans, config var names (not values), Scheduler jobs, domains and certificates, log drains, and the release command.
- Keep the app twelve-factor (config from the environment, stateless processes, logs to stdout) so it runs the same on Heroku and the target. Changes that do this help both.
- Plan the move with the architect: each Heroku piece mapped to the target, the data migration and the cut-over, with a way back. Don't move parts piece by piece inside unrelated tasks.

## Tests

- Run the app with `heroku local` and a local `.env` (never committed) before reporting done: every process type starts, `web` answers on `$PORT`, and no config comes from files.
- Run the release command against a local database that has data, twice.
- Test that workers stop cleanly on `SIGTERM` and that Scheduler jobs are safe to repeat.

## Stop and report before

- running any command from the "hand to the user" list: give the command instead,
- reading or printing secrets, or production data and logs beyond what the task needs,
- a migration in the release phase that the old code can't run with, or one that changes data without a backup,
- adding, changing or removing an add-on, dyno type or stack,
- copying production data anywhere.
