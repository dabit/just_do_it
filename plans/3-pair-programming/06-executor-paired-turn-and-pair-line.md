status: done
# 06 — Give the Executor its paired turn, and document the `Pair:` line

Depends on: 05

## Why
Driver and navigator are turn assignments inside the existing Executor role, not new agent types —
adding an `agents/driver.md` would create a way to spawn a paired role that is not in a Herdr pane
and cannot ping-pong. This task wires the Executor to accept a paired turn without adding that
route, and gives the `Pair:` metadata line the same documented, single shape the `TDD:` line
already has.

## Description
- **`agents/executor.md`**: "What it receives" gains a sixth bullet — the paired-turn assignment
  (report path, which side, the test list, the parked-notes ledger, all as resolved absolute
  paths), and the instruction to perform P2. State plainly: driver and navigator are turn
  assignments, not roles — the agent in the pane is an Executor either way. "What it returns"
  gains the five-part handoff written to the report path, with the path as the only reply. The
  staging section's five existing rules are unchanged; add a closing paragraph scoping the whole
  discipline to the turn-holder, and say why — the "read column 2" rule stops being a statement
  about *your own* work when a second agent shares the tree, and `git add` may stage a file the
  partner is mid-edit in.
- **`agents/synthesizer.md`**: carries the `- Pair:` line into the condensed `PLAN.md` on the same
  terms it already carries `- TDD:`.
- **`reference/plan-store.md`**: documents the `Pair:` line's one shape — `- Pair: on — <kind A> +
  <kind B>, first paired YYYY-MM-DD`, written once by `/jdi:pair`, never rewritten — and the one way
  it diverges from `TDD:`: there is no `off` shape, because pairing is requested by a command and
  degradation is announced in that same turn, not recorded for a later command to find. State
  explicitly that **no command reads the line to decide anything**, and that the commit-points
  table is unchanged.

## Files
- `agents/executor.md`
- `agents/synthesizer.md`
- `reference/plan-store.md`

## Verification
- **This task is entirely prose describing role behaviour; nothing in the suite reads inside a
  role file's body.** `python3 -m unittest discover -s tests -v` — expect `Ran 17 tests ... OK`,
  a regression guard confirming frontmatter and enumerations are untouched, not evidence the new
  wording is correct.
- **Under TS2 this task produces the announced skip — no testable behaviour — and the skip is the
  right answer.** Do not answer it with a fabricated test: asserting that `agents/executor.md`
  contains the phrase "turn assignment" would give a green suite and a red transcript that prove
  nothing while looking exactly like proof.
- `grep -n 'Pair:' agents/synthesizer.md reference/plan-store.md` — expect a match in both files,
  documenting the same one shape.
