status: done
# 04 — Give the Executor and Planner their TDD responsibilities

Depends on: 03

## Why
TS1 and TS2 (task 03) are defined but nothing performs them yet. This task makes test-first
discipline part of the Executor's standing behaviour (it performs TS2, never fabricates a test,
and is not done at red) and makes the Planner responsible for saying, per implementation step,
which test proves it — so the "does this task have testable behaviour" judgement is a two-party
call rather than the Executor deciding alone.

## Description
`agents/executor.md`, three edits:
- **Responsibilities** — a new bullet after `:38-42`: perform TS2 when the Butler hands over "TDD
  on". An untestable task is an announced skip, never a fabricated test. Not complete at red.
- **"What it receives"** (`:54-59`) — insert before "The codebase": the TDD decision, already
  resolved — either "TDD off" or "TDD on, and the proven invocation is `<command>`". The Executor
  never reads `.jdi/config.yml` directly (`roles/butler.md:14-15`).
- **"What it returns"** (`:61-65`) — insert after "Verification results": under TDD, the red-run
  evidence (exact command, failing output captured before the implementation existed, the assertion
  line showing it failed for the intended reason), then the same command's green output. Where the
  task had no testable behaviour, that judgement and its reason instead.

`agents/planner.md` — append to the existing testing-strategy bullet at `:33-41` (extending the
existing responsibility, not adding a new one): attribute the strategy to the implementation
steps — say which test proves which step — and name explicitly any step whose behaviour no test can
observe, with what proves it instead. It needs no knowledge of the `tdd` key itself.

## Files
- `agents/executor.md`
- `agents/planner.md`

## Verification
1. `python3 -m unittest discover -s tests -v` — expect `OK`. No test in the suite observes role
   body content directly; this run is a regression guard confirming these prose edits did not
   break frontmatter well-formedness (`test_frontmatter.py` still passes on both files), not proof
   the new prose is correct.
2. `grep -n "TS2\|not complete at red" agents/executor.md` — expect matches in Responsibilities,
   "What it receives", and "What it returns".
3. `grep -n "which test proves which step\|no test can observe" agents/planner.md` — expect a match
   in the testing-strategy bullet.
