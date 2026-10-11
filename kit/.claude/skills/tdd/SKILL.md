---
name: tdd
description: Test-driven development loop and how much to test. Use when adding or changing behavior, fixing a bug, or deciding which tests a change needs.
---

# Test-driven development

## The loop

1. **Pick one behavior**: the next smallest thing the code should do that it doesn't do yet.
2. **Write one failing test** for it. Name it after the behavior ("rejects expired tokens"), not the method.
3. **Run it and watch it fail for the expected reason.** A test that fails for the wrong reason (import error, typo) or passes straight away proves nothing. Fix the test first.
4. **Write the simplest code that makes it pass.**
5. **Run the tests.** While looping, run only the narrow set around your change.
6. **Refactor while green**: remove duplication, improve names, then rerun.
7. Repeat until the requested behavior is complete, then run the full relevant suite.

## Bug fixes

Reproduce first: write a test that fails because of the bug, then fix it. The test stays as the regression guard.

## How much to test

Test where a break would hurt and is plausible. For each change, cover:

- the main behavior (the happy path),
- edge cases real input produces: empty, missing, and boundary values the domain actually has,
- error paths a caller handles or a user sees,
- the bug, if you're fixing one.

Skip:

- trivial code: getters, pass-throughs, constants, plain mapping,
- the framework or library doing its job,
- every combination of inputs; pick representative cases,
- states that types or validation already rule out.

Stop when the next test would only re-prove what an existing test already covers. Solid coverage of what matters beats a high percentage.

## Choosing the level

- Unit tests for logic with branches.
- An integration test for wiring: one test that the pieces connect beats mocks asserting each call.
- Mock at the boundaries (network, clock, external services), not the code you own when the real thing is fast.
- Follow the project's existing test style, file locations and helpers.

## When test-first doesn't fit

Spikes, throwaway prototypes, pure configuration and visual layout. Say that you're skipping test-first and why, and add tests for whatever survives the spike before calling it done.

## Refactoring

Tests must pass before you start and after every step. In each step change either structure or behavior, never both. If the code has no tests, first add a few that pin its current behavior.

## No test setup yet

If the project has no tests or test runner, say so and propose the smallest setup that fits its stack. Don't build test infrastructure until the user agrees.
