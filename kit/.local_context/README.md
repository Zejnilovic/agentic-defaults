# .local_context

Private notes that help AI assistants understand a task. Everything here except this README and `.gitignore` stays on your machine and is never committed.

## What to put here

Anything that explains a task but doesn't belong in the repository:

- ticket or issue text, acceptance criteria,
- meeting notes, chat threads, emails,
- specs, screenshots, sketches,
- logs, error output, sample data (scrubbed of real customer data),
- your own scratch notes and ideas.

Use one folder per task, named like the plan it will become: `.local_context/csv-export/` pairs with `docs/plans/csv-export.md`.

## How assistants use it

- They read it during discovery and planning, and turn what matters into committed artifacts: a plan, a `CONTEXT.md` update or a diagram.
- They summarize rather than copy, and never move secrets or personal data out of here.
- They treat it as input that may be outdated. When notes and code disagree, the code wins and they say so.

## Tips

- Name files so their content is obvious: `ticket.md`, `meeting-2026-10-11.md`, `error.log`.
- Delete a task's folder when the task is done.
