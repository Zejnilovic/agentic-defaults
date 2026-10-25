---
description: Report problems with Zejnilovic's agentic defaults, suggest changes, and work on the repository.
---

# Feedback and contributing

It's early days. If something works well for you, breaks, or is missing, [open an issue](https://github.com/Zejnilovic/agentic-defaults/issues) or start a [discussion](https://github.com/Zejnilovic/agentic-defaults/discussions). Problems with installing or updating belong in [agd's issues](https://github.com/Zejnilovic/agd/issues).

## A kit file made an agent go wrong?

Report it from the project:

```bash
agd feedback
```

It asks what went wrong and opens a pre-filled issue for you to review. **Nothing is posted until you submit it.**

!!! tip "Let the agent write the note"
    Ask your assistant to "retro this session". The [`session-retro`](skills.md#everyday-practice) skill evaluates the session and writes a note; pass it along:

    ```bash
    agd feedback .local_context/feedback/<note>.md
    ```

Or use the [session feedback form](https://github.com/Zejnilovic/agentic-defaults/issues/new?template=session-feedback.yml).

## Working on this repository

Rules for maintainers and AI assistants are in [AGENTS.md](https://github.com/Zejnilovic/agentic-defaults/blob/master/AGENTS.md). Before committing, run:

```bash
python3 scripts/check.py
```

```bash
python3 -m unittest discover -s tests
```

`check.py` verifies frontmatter, skill references, links, the README's tables, version markers, the packs in `packs.txt`, the word budget of the working agreement and script syntax. The tests cover the scripts' behavior. CI runs both on Linux and macOS.

To preview this site, install its tools and serve it:

```bash
pip install -r docs/requirements.txt
```

```bash
mkdocs serve
```

## Credits

Several delivery safeguards are adapted from [GSD Core](https://github.com/open-gsd/gsd-core) (MIT): goal checks in review, the developer's rules for unplanned work, the ban on watered-down requirements, and dependency safety.
