status: pending
# 05 — Add `commands/pair.md`, and its four enumerations

Depends on: 01, 02, 03, 04

## Why
This is the command a user actually types to get a paired run: `/jdi:pair`. It has to exist, be
discoverable in every list that names a command, and be written so it does not become a fourth copy
of the Executor hand-off that `/jdi:yolo` already carries.

## Description
Add `commands/pair.md` with frontmatter (`description:`, `argument-hint: "[plan slug]"`) and the
Butler role line, written as **"Follow `/jdi:yolo` in full, with seven differences"** — the same
"whole command by name, with N differences" shape `commands/replan.md` and `commands/reresearch.md`
already use, sanctioned by `docs/config-key-lifecycle.md` as one of the two allowed exceptions to
repeat-in-place:

1. **A preflight** after yolo's pre-loop steps: P1, from `reference/pairing.md`, run after yolo's
   TDD step (P1 rung 1 reads the `TDD:` line that step writes). Degraded → announce which rung and
   ask single-agent (`/jdi:yolo`, with zero differences) or stop.
2. **Step 2's hand-off is replaced**: drive the task as exchanges across two panes — P3 every turn
   while the two agents perform P2. Same inputs yolo hands the Executor, as resolved absolute
   paths, plus the turn assignment, the report path, and the single-writer rule.
3. **Self-verification runs once per task, after the final green — not per turn.** Between turns
   the tree is legitimately red by design; that red is the handoff, per task 04's edit to
   `reference/testing.md`.
4. **The failure checked is your own run after the last exchange**, in yolo's existing positive
   voice. Three new stops, additive to yolo's existing ones: a blocked pane; six exchanges; two
   consecutive turn-backs.
5. **Step 1's commit runs only when neither pane holds the turn** — the turn-holder staged and
   released, so column 2 of `git status --short` is trustworthy again.
6. **Teardown** per task and per run: surface the parked-notes ledger, carry `defer` items forward,
   release the panes, say what was left behind.
7. **The closing summary says the run was paired**, naming both agent kinds and each one's
   lifecycle source, so a reader knows which state readings were a terminal-title scrape.

Then, in the same commit, the four enumerations that must land with the file that makes them true:
`AGENTS.md`'s command table gains a `/jdi:pair` row; `README.md`'s workflow-command count moves
16 → 17; `commands/help.md`'s command table gains a `/jdi:pair` row; `roles/butler.md`'s ownership
table gains a `/jdi:pair` row (or is added to an existing grouped row).

## Files
- `commands/pair.md` (new)
- `AGENTS.md`
- `README.md`
- `commands/help.md`
- `roles/butler.md`

## Verification
- `python3 -m unittest discover -s tests -v`, run with `commands/pair.md` added but before any of
  the four enumerations — expect **four failures**: `CommandTableTest` naming `commands/pair.md`
  missing from `AGENTS.md`'s table; `ReadmeCountTest` reporting README says 16 workflow commands
  while `commands/` holds 17; and task 01's two new guards, each naming `pair` missing from
  `commands/help.md`'s table and `roles/butler.md`'s ownership table respectively.
- After all four enumerations are added — expect `Ran 17 tests ... OK`. This is also the proof that
  task 01's two guards earn their place: two of the four reds above exist only because that task
  added them.
