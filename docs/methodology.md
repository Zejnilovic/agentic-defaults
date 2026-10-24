# Working with coding agents

*The methodology behind agentic-defaults.*

This is a method for getting reliable, affordable work out of AI coding agents. It is written to outlast any particular model or tool: it rests on how agents work, not on what today's products can do. The [kit](../kit/) is one way to put it into practice. When tools change, the kit's files change; the method doesn't.

The method in one line: **writing code is cheap now; knowing what is correct is not.** The lasting assets are the ones that carry knowledge and define what correct means: context files, contracts and tests. Most of what follows is about building those, and spending the expensive models only where judgment is needed.

## Six facts that don't change

Everything below follows from these.

1. **An agent knows only what is in front of it.** Each session starts empty. Yesterday's conversation, the decision you explained last week, the bug you found together: gone, unless it is written somewhere the agent reads.
2. **Attention is finite, and every token costs.** Reading more costs money and time, and past a point it makes the work worse: the one instruction that matters competes with everything else in view. More context is not better context.
3. **Agents sound sure whether or not they are right.** They report "done" when the steps are finished, not when the goal is met. They fill gaps with plausible guesses, including made-up reasons for decisions.
4. **Most work is routine.** Reading code, following a clear plan, writing a test for a known behavior, passing work along: an inexpensive model does these well. Only a small share of the work needs the strongest model.
5. **Writing code is cheap; knowing what is correct is not.** Agents produce code faster than anyone can read it. The hard part has moved from writing code to saying precisely what it must do, and checking that it does.
6. **Tools and models change constantly.** What lasts is what you write down: knowledge about your system, how you work, the contracts between its parts, and the tests that pin its behavior. Tool-specific setup should be a thin layer that is easy to replace.

## 1. Memory lives in files

If knowledge matters, put it in a file the agent will read. A chat is a scratchpad, not a memory.

Different knowledge lives for different lengths of time and serves different readers, so it belongs in different places:

| What | Where | Read by | Lives | In git |
|---|---|---|---|---|
| How to work here: commands, checks, rules | `AGENTS.md` | Agents, every session | As long as the project | Yes |
| What the system is: purpose, structure, decisions, traps | `CONTEXT.md`, one per level that needs it | Agents working at that level | As long as the code it describes | Yes |
| Raw input: tickets, meeting notes, logs, exports | `.local_context/<task>/` | Agents during discovery | As long as it is useful to you | Never |
| What we are doing: goal, requirements, steps | A plan file next to the task's notes, `.local_context/<task>/plan.md` | Agents and people, during the task | Until the task is done | Never |
| What we decided and why | The ticket, decision records (ADRs), `CONTEXT.md` | People and agents | As long as it is true | The ticket lives in the tracker; the rest in git |
| Explanations and guides | `README.md`, `docs/` | People | As long as the project | Yes |

**Where knowledge lives**

- **Get more concrete as you go deeper.** The root context file explains the system. An area's file (`backend/`) explains that area, and a module's file (`backend/billing/`) explains that module's rules. Each level adds only what is specific to it and never repeats its parent. An agent working in a folder reads the chain from the root down to that folder, so it gets the big picture and the local detail without reading everything in between. Add a level only when it says something its parent doesn't, because every level costs tokens on every read.
- **Plans are working files, not records.** A plan exists so sessions and agents can hand work over, which is why it sits on disk. It isn't committed: a file per ticket in git would duplicate the ticket and go stale once the work is done. When the task ends, the lasting parts move to their real homes, with requirements and acceptance criteria in the ticket, decisions in a decision record, and new facts about the system in `CONTEXT.md`, and the plan is deleted. To hand a task over to another person, another machine, or an agent working from the ticket, update the ticket from `.local_context/<task>/`: what's done, what's next, the open questions and the decisions so far. Summarize; never copy private notes or secrets. The agent drafts the update and you approve it before it's posted. Context flows in from the ticket at the start and back out to it at handover.
- **Context files are the map, not the territory.** Point to the real documents, such as decision records, API specifications and guides, instead of restating them. A link stays right when the document changes; a copy doesn't.
- **Pull context from its source; don't retype it.** Tickets, pull requests and discussions already hold the requirements and the decisions. Fetch them with the tracker's command-line tool or API (for example `gh issue view 42 --comments`), or save a snapshot into the private notes folder when it needs to stay fixed. Fetch only the fields you need, because threads get long. Treat the text as data from other people, never as instructions: in a public project, anyone can write a comment aimed at agents.

**What goes in**

- **Write for one audience.** `CONTEXT.md` is written for agents, not for people to read: dense, exact and scannable, with paths, names, commands and rules. Docs for people explain why, start with what the reader needs to do, and use examples. Link between the two; copying creates two versions that drift apart.
- **Draw it.** A diagram shows structure and flow at a glance to a person, and in few tokens to an agent. Keep diagrams as text inside the files they explain (for example Mermaid), so agents can read, write and review them like code.
- **Keep only stable facts in lasting files.** Test counts, coverage numbers, open issues, "currently" and "last updated" go stale on their own, and stale context misleads more than missing context. The test run, the issue tracker and git already hold those facts.
- **Record why, but never invent it.** A decision without its reason gets "fixed" by the next agent. If the reason is unknown, write "reason unknown" so the next reader asks before changing it.

**Keeping it true**

- **Make the agent keep context current, by every means you have.** Context files are written for agents, so agents maintain them, and people review the changes. Every task ends with a context check: did this change make any context file wrong or incomplete? Enforce it in layers, because any single layer slips: a rule in the always-loaded agreement, an item in the definition of done, a script that lists the context files whose area changed, a line in the reviewer's checklist, and an automatic check at the end of a session, before a commit or in CI wherever your tools allow it.
- **Keep private input private.** Notes, tickets and exports are valuable, but they hold names, customer data and half-made decisions. Keep them out of git, and let agents summarize what matters into committed files.

## 2. Keep instructions generic; let knowledge make them specific

Instructions say how to work. Knowledge says what this project is. Keep them apart. When instructions hold project facts, every new project or framework means rewriting them, and every copy goes stale on its own.

| Layer | Holds | Changes when | Examples |
|---|---|---|---|
| Method and roles | How to work, who does what, when to stop | You improve the method | The working agreement; instructions for each role and practice |
| Framework practices | How to work well with one framework or database | The framework changes | Practice files for Flask, Spring, React or relational databases |
| Project knowledge | What this system is, and what you are doing in it | The project changes, every day | `CONTEXT.md`, docs, decision records, plans, tickets, the project's commands |

- **Never put project facts in instructions.** Names of services, tables and commands, conventions and decisions all go in the project's context files. An instruction says "read the nearest context file and follow its conventions"; the context file says what they are.
- **A new project gets new context, not new instructions.** Copy the same instructions, then write the project's context. A new framework means adding or swapping one framework layer, never editing the method.
- **Change shared instructions inside a project only in their marked project parts.** An edit anywhere else is lost at the next update or blocks it, and the copies drift apart. Mark shared files as shared, so agents know too, and give them a few marked places that updates keep, such as a closing project section, the choice of model or the tools an agent may use. Project rules go in the project's own files; a change that would help every project goes back to the shared source.
- **Give every project the same front door.** Use a small set of standard commands, such as `make setup`, `make build`, `make test`, `make lint` and `make run`, wrapping whatever each project really uses underneath. Then one instruction, "run `make test`", works in every project, and people get the same benefit. Make is decades old and available on nearly every developer machine. Any task runner works, as long as every project uses the same command names.

## 3. Context is a budget

Treat what the agent reads and writes like money: spend it where it pays off.

- **Keep the always-loaded layer small.** Whatever is loaded into every conversation is paid for in every conversation. Give it a word budget and defend it. Move procedures into files that load only when a task needs them.
- **Search before reading, and read only what the task needs.** A good instruction says how much to read and when to stop reading and act.
- **Keep output short, and give it a shape.** Output costs tokens too, and it costs the reader's attention. Agents tend to over-explain: they restate the question, narrate what they are about to do, and summarize what they just did. Ask for the result first, one line per item, and nothing else. With several agents the cost compounds, because each wordy report lands in the next agent's context. Short doesn't mean vague: test results and exact file references stay.
- **Give separable work a fresh context.** Exploration, review and independent steps can run in a separate session that starts clean and returns a short result. The main conversation stays small, and the noisy work doesn't pile up in it.
- **Hand work over through files, not chat.** A fresh context can't see your conversation. Point it at the plan file and the step number instead of pasting the plan.

## 4. Size the process and the engineering

Process and engineering practices have a cost. Spend them only when they buy something, for this task and for this project.

### Size the process to the task

- **A small, local change:** just ask. The working agreement is enough.
- **Several steps or sessions:** write a plan file first, so the work survives a fresh session.
- **Several parts of the system, or a design decision:** separate the roles. Discover, design, implement, verify.

### Size the engineering to the project

An internal tool for ten people shouldn't be built like a bank's payment system, and agents left alone tend to reach for the heavyweight version of every practice. Write down what kind of project this is, in a few dimensions that each decide something different:

| Dimension | For example | Decides |
|---|---|---|
| Stage | prototype, early, production, mature | How much rigor: test depth, migration safety, compatibility |
| Audience | personal, internal, customer, public | Security depth, versioned contracts, accessibility, abuse limits |
| Team | solo, one team, several teams | Formality: decision records, contracts between teams |
| What it handles | money, personal data, regulated data, safety | Risk at any size: security reviews, audit trails, backups |

- **Cheap correctness and safety always apply.** Validate input, check access, never build queries from strings, test behavior, and stop before losing data, whatever the profile.
- **Costly practices apply when the profile calls for them.** Contract tests, zero-downtime migrations, feature switches, decision records and formal reviews earn their cost at some profiles and are waste at others. Mark them with the profile that needs them, so an agent can check rather than guess.
- **A practice is worth it when the failure it prevents is likely and expensive here.** Skip one whose cost outweighs what it prevents, and say so.
- **Watch for building for a bigger project:** layers with one implementation, generic frameworks, event buses, separate services, infrastructure no requirement asks for.
- **What it handles can outweigh size.** A small internal tool that handles money or personal data needs targeted rigor where that data flows, not everywhere.

### Whatever the size

- **Make the smallest change that fully delivers.** No abstractions, options or layers that no current requirement needs.
- **Never water a requirement down to make it fit.** "For now", "placeholder" and "v1" quietly drop a requirement. When something doesn't fit, pivot as described below.

### When you hit a wall

Sometimes a step can't be done as planned: an API doesn't exist yet, a library doesn't behave, a requirement turns out to conflict with another. That is when agents reach for "for now", a placeholder or a hard-coded value, and it is the moment to pivot instead.

1. **Stop at the wall.** Don't let the agent paper over it. A hidden stand-in looks finished and fails later, far from its cause.
2. **Write the wall down** in the plan, next to the step: what blocks it, what was tried, the evidence, and what is still unknown. That is what lets you, or a fresh session, pick it up without starting over.
3. **Choose a way around it, with a person deciding:**
   - **Split.** Finish what can be finished, fully, and move the blocked part into a task of its own, with its notes. Two complete pieces beat one fake whole.
   - **Spike.** When you don't know enough to plan, run a short, throwaway experiment on a separate branch, in a fresh session. Keep what you learned in the notes, and discard the code.
   - **Re-plan.** If the wall shows the design is wrong, take it back to the design step instead of patching around it.
   - **Make a limit visible.** If something must ship before the wall is gone, make the gap explicit: behind a switch that is off, and recorded in the ticket and the docs. Never a silent stand-in.
4. **Tell the agent exactly that.** For example: "Step 3 is blocked by the missing export API. Don't work around it. Record the blocker in the plan, list two or three options with their cost, and stop." Then, once you have decided: "Finish steps 1 and 2 fully, and move step 3 into a new task with what we know."

## 5. Think once with a strong model, execute with an everyday one

The strongest models cost many times more than everyday ones. Use them where judgment matters, and make their output reusable.

- **Strong models design, review and decide. Everyday models read, execute and orchestrate.** Discovery reads a lot and writes little. Carrying out a clear step needs care, not brilliance. Orchestrating (giving each step to the right agent, passing file paths, collecting reports) is mechanical when the handoffs go through files.
- **A cheap orchestrator escalates; it doesn't solve.** When an agent reports a blocker or a design question, the orchestrator passes it to a strong model or a person instead of answering it itself.
- **The plan is the handoff.** A plan that names the files, the behavior to test and the command that proves each step is done lets an everyday model carry it out without redoing the design.
- **Let the inexpensive model read the bulk.** Have it digest notes and code into a short brief, and let the strong model design from the brief.
- **Write instructions for the weakest model you will use.** Numbered steps, an explicit output format, concrete limits ("at most 10 findings") and what to skip. Strong models follow such instructions just as well; weak models need them.

## 6. Make the specification executable

Agents produce code quickly. What makes that code trustworthy is a definition of correct that a machine can check: contracts for the boundaries, tests for the behavior, and requirements written as outcomes.

- **Write requirements as observable behavior.** "An approver sees only entries from their own projects", not "permission support". If nobody can check it, it isn't a requirement yet.
- **Agree on the contract first.** Where parts of a system meet (an API, a message format, a database schema, a shared type), write or change the contract before the code on either side. Agents working on each side in separate contexts never see each other's code; the contract is their shared context. It is also compact, since a schema says more in fewer tokens than the code behind it, and checkable: a contract test fails the moment one side drifts. Generate types and clients from the contract where you can.
- **Test first, now more than ever.** Tests are the only feedback an agent gets that doesn't depend on its own judgment. A failing test is the clearest specification you can hand an inexpensive model. And agents write code faster than anyone can review it, so cheap, repeatable checks are what keep up. Fix a bug by reproducing it in a test first. The strongest form: a person writes or approves the tests, and the agent writes the code.
- **Never weaken a test to make it pass.** When a test stands between an agent and "done", agents tend to edit or delete the test instead of fixing the code. Changing an existing test changes a requirement: it needs a reason and a person's approval.
- **Test what matters, not everything.** Cover the main behavior, the edge cases real input produces, the errors users see, and every bug you fix. Skip trivial code, the framework doing its job, and states that can't happen. Stop when the next test would only re-prove an existing one.
- **Keep tests contained.** A small change should break the tests for that behavior, not thirty tests in twenty files. Test through stable interfaces (the public function, the endpoint, what the user sees) rather than internals. Test each behavior in one place, at the lowest level that can show it, and let a contract test cover a boundary instead of repeating the same check in every layer. Build test data with shared builders, so a changed data shape is a single edit. Mock only what you don't own. When one change breaks many unrelated tests, the tests are coupled to the implementation: stop and report it, and fix how the tests are built rather than editing each one by hand.

## 7. Verify outcomes, not reports

An agent's "done" is a claim. Check it against the specification and the evidence.

- **Check the goal, not the task list.** For each requirement, ask three questions. Is it true: does a test or code path show it happens? Is it real, rather than a stub or placeholder? Is it connected, actually wired into the system? Ticked checkboxes prove nothing.
- **Review with fresh eyes.** A reviewer that didn't write the code doesn't share its author's assumptions. Ask only for real problems (bugs, missing tests for important behavior, broken contracts, stale context, needless complexity), and accept an empty review.
- **Ask for a picture before the change.** Before an agent changes a flow, have it draw the flow as it understands it. A wrong diagram exposes a misunderstanding in seconds, before any code exists.
- **Trust the code over the notes.** Notes and docs go out of date. When they disagree with the code, the code wins, and the conflict is reported rather than quietly resolved.

## 8. Bound the agent

An agent that keeps going in the wrong direction costs more than one that stops and asks.

- **Give explicit stop conditions.** Stop and report after two failed attempts at the same problem, after several reads in a row without any change, before any design decision, and when the plan turns out to be wrong. Stopping beats improvising.
- **Say what it may fix on its own.** Problems its own change caused, or that block its step: fix them. Problems that were already there: list them, don't fix them. Anything that changes the design or a contract: ask.
- **Put hard limits on what can't be undone.** Deleting data, dropping columns, touching any database other than a test one, rewriting shared history: always stop and ask, whatever else the instructions say.
- **Treat dependencies as a risk.** Add a package only when the task needs it. If an install fails, never try a similar-looking name: look-alike package names are a known attack.
- **Commit and publish only on request.** Agents prepare changes, comments and descriptions; people decide what gets recorded and shared.

## 9. Improve the system, not just the output

- **When an agent gets something wrong, fix the rule that allowed it.** Correcting the output fixes one task; correcting the rule fixes every task after it. Note misbehavior as you work, and turn the notes into rule changes.
- **Keep the setup plain and portable.** Markdown files and small scripts work across tools. Keep tool-specific configuration thin, so a tool change means editing a few lines, not rethinking the method.
- **Version what you copy.** When projects copy a shared setup, give it a version and a way to see what changed, or the copies drift apart unnoticed.
- **Check the setup like code.** Consistency checks, and tests for the setup's own scripts, catch broken references and stale versions before they reach a project.

## Anti-patterns

| Instead of | Do this |
|---|---|
| One huge instruction file loaded every time | A short always-loaded agreement, with detailed procedures loaded on demand |
| Project facts written into agents and prompts | Generic instructions, with project facts in context files |
| Different commands in every project | The same front door everywhere: `make test`, `make lint`, `make build` |
| One flat context file for the whole system | A chain of context files, more concrete at each level |
| The chat as the project's memory | Context files, plan files and notes on disk |
| Retyping tickets and threads into the chat | Fetching them from the tracker, as data |
| A committed plan file for every ticket | A local plan next to the notes; outcomes go to the ticket, decision records and `CONTEXT.md` |
| Status, counts and dates in context files | Stable facts only; status lives in the tracker and the test run |
| Paragraphs describing a flow | A diagram kept as text next to the code |
| Long, chatty agent reports | Short output with a defined shape |
| The strongest model for everything, including passing work around | Strong models to design, review and decide; everyday models for the rest |
| "For now", a placeholder or a hard-coded value when stuck | Stop, write the wall down, then split, spike, re-plan or make the limit visible |
| Two agents building both sides of an interface at once | The contract first, then each side against it |
| Tests coupled to internals, breaking by the dozen | Tests through stable interfaces, one place per behavior, shared builders |
| Accepting "done" | Checking each requirement against the code and the tests |
| Letting the agent "fix" a failing test | Fixing the code; changing a test needs approval |
| Letting the agent "try another approach" indefinitely | Stop conditions, and a report of what was ruled out |
| Full process for every change | Process sized to the task |
| Enterprise practices in a small internal tool | Practices chosen by the project's profile |
| Fixing the agent's output by hand, again and again | Fixing the rule that produced it |

## Learning it: nine exercises

Each takes under an hour on a real repository. Do them in order; each builds on the one before.

1. **Build the front door and the working agreement.** If your project has no standard commands, add `make build`, `make test` and `make lint` first. Put them, and the checks that must pass before work counts as done, into `AGENTS.md`. Then, in a fresh session, ask: "What must pass before you report a task as done?" If the agent can't answer, the file is not being read or not clear enough.
2. **Map the system, then audit the map.** Have an agent write a root `CONTEXT.md` and one for a single area. Remove every volatile fact, mark what was inferred as unverified, and check three of its claims against the code yourself. You'll learn what agents tend to get wrong about systems.
3. **Draw before you change.** Before a change to a flow you know well, ask the agent to draw that flow as a diagram. Correct the diagram, then let it make the change. Note how often the diagram showed a misunderstanding the code would have hidden.
4. **Make a change and watch the context.** Ask for a change that makes something in a context file untrue. Does the agent update the file without being asked? If not, add another layer: a check script, a reviewer step or an automatic check.
5. **Survive a fresh session.** Start a multi-step task with a plan file, with the ticket fetched from your tracker rather than retyped. Halfway through, end the session and continue in a new one with only "Continue `.local_context/<task>/plan.md`". If the new session stalls or guesses, the plan is missing something. Find out what.
6. **Contract first.** Pick a change that crosses a boundary, such as a new API field shown in the UI. Make the first step change only the contract, then implement each side in a separate session against it. Did either side need to see the other's code? If so, the contract was incomplete.
7. **Plant a stub, and tempt a test.** After an agent implements a step, replace part of it with a placeholder and ask for a review against the plan's requirements. Does the review catch it? Then break the code so an existing test fails, and ask an agent to make the tests pass. Does it fix the code, or the test?
8. **Hit a wall on purpose.** Give an agent a step it can't finish as written, such as one that needs an endpoint that doesn't exist yet. Does it stop and write the wall down, or invent a stand-in? Then practice the pivot: split the step, and continue with the part that can be finished.
9. **Measure the split.** Run the same well-planned step once with your strongest model and once with an everyday one, and compare cost and result. Then run the orchestration on an everyday model and check that it hands decisions up instead of making them. If the everyday model struggles, look at the step before blaming the model: vague steps fail on inexpensive models first.

## How agentic-defaults implements this

The principles above are meant to stay stable. This table follows the kit's current version.

| Principle | In the kit |
|---|---|
| Memory lives in files | `AGENTS.md`; `CONTEXT.md` levels from root to module with the `context-md` skill; local plans and notes in `.local_context/<task>/` with the `task-plans` skill; tickets fetched by the analyst and updated at handover; the `diagrams` skill |
| Generic instructions: kit files and project files | A "From agentic-defaults" marker on every kit file; a rule that agents edit kit files only in their project parts, an agent's `model:` and `tools:` lines and a closing `## This project` section, and put project rules in "This project" of `AGENTS.md` |
| Memory lives in files: keeping it true | The context check as the last step of every task, in the definition of done, the `implementation` skill and the reviewer; `check.sh`, also as an end-of-turn hook in both Claude Code and Copilot, a pre-commit reminder or a CI step |
| Generic instructions, specific knowledge | Roles and practices with no project facts; framework pairs such as `flask` and `flask-developer`; the standard `make` commands, with project specifics only in the "This project" section of `AGENTS.md` |
| Context is a budget | A word budget for `AGENTS.md`; skills loaded on demand; `CONTEXT.md` levels; the "Work economically" rules, including short output; defined output formats in every agent |
| Size the process and the engineering | The project profile and its tags, with the `project-profile` skill; "Match the process to the size of the change"; plans only for multi-step work; blockers in the plan, and split, spike, re-plan or a visible limit instead of stand-ins |
| Strong models decide, everyday models do the rest | A model tier per agent; analyst and research collector read, architect and researcher judge, framework developers execute; routing that escalates blockers; a Verify command in every plan step |
| Make the specification executable | Requirements written as observable behavior; contract-first plan steps; the `tdd` skill, with contained tests and never weakening a test; test-first framework developers |
| Verify outcomes | The reviewer's goal check, contract and weakened-test checks; the security reviewer |
| Bound the agent | The `implementation` skill's rules for unplanned work, walls and stopping; the database skill's hard stops; the dependency rules |
| Improve the system | A versioned kit in packs, installed and updated by [agd](https://github.com/Zejnilovic/agd), which keeps each project's own parts; `scripts/check.py` and tests |
