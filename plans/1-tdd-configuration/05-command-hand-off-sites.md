status: done
# 05 — Wire TS1/TS2 into execute, next, and yolo

Depends on: 03, 04

## Why
This is where the TDD setting actually changes what a plan run does. `execute.md`, `next.md`, and
`yolo.md` are each independently followable files (an agent may be told to read only one of them —
`AGENTS.md:9-16`), so the instruction is written out in full at every site rather than
cross-referenced. All nine sites are covered here in one task because they are mutually
consistent restatements of the same hand-off contract — `next.md`'s and `yolo.md`'s hand-off text
are meant to be byte-identical to each other apart from a step number and one capital letter, and
that invariant can only be checked once both are written, in the same diff.

## Description
**`commands/execute.md` — three sites**
- Step 2, new sub-step `c`, after the plan-approval commit (`:33-40`): if `tdd.enabled` is not
  true, do nothing and say nothing; otherwise perform TS1 and record the `- TDD:` line after
  `- Started:`.
- Step 5, the hand-off (`:48-57`): a fourth input bullet — read the `TDD:` line. `on` means pass
  the proven invocation and instruct TS2. Missing or `off` means pass nothing and say nothing.
- Step 6, "Verify independently" (`:59-61`): when TDD is on, confirm the tests are in
  `git diff --staged` and that your own run is green. Do not reproduce the red — read the
  Executor's captured red and check it names the new assertion, not an import or syntax error. If
  a task touching executable code carries no red evidence and no stated reason, lead with that the
  way a failed verification is led with, and ask whether to accept or send back.

**`commands/next.md` — two sites**
- Step 9, the hand-off (`:53-58`): as execute's step 5, compressed. **`/jdi:next` reads the `TDD:`
  line and never runs TS1.** Do not add a lazy-detect here: under the silence rule a TDD-off plan
  writes no line either, so "no line" cannot distinguish "predates the key" from "started with TDD
  off", and detecting here would let a mid-plan config flip turn TDD on — which the
  never-rewritten invariant forbids — and would make `/jdi:next` and `/jdi:execute` disagree on the
  same plan. **No line means no TDD, for every command, always.**
- Step 10, "Verify independently" (`:60-61`): as execute's step 6, compressed.

**`commands/yolo.md` — four sites**
- Before the loop (`:21-27`): perform TS1 once and write the line, as execute's sub-step `c`, **and
  gate it on the same condition — every task still unchecked.** A resumed `/jdi:yolo` reads the
  existing state rather than re-detecting; otherwise resuming a plan that began with TDD off would
  silently turn it on. This is the only place yolo resolves TDD — one detection per run, not one
  per task.
- Step 2 item 3, the hand-off (`:60-65`): as next's step 9. This site and `next.md:53-58` must be
  byte-identical apart from the step number and one capital letter — keep them so.
- Step 2 item 4, "Self-verify" (`:66-68`): as execute's step 6 / next's step 10.
- Step 2 item 5, "Check for failure" (`:69-72`) — the sharpest edit in this plan. The existing stop
  is not weakened. Add a scoping sentence naming which run the stop is about, plus one new stop:

  > The failure being checked is the outcome of *your own* run in item 4, against the tree as it
  > stands now. Under TDD the Executor's report will contain a failing test run: that red is
  > required evidence, captured before the implementation existed, and it is a record of a past
  > state, not a verification result. Do not treat it as one. If your own item-4 run is green, the
  > task passed, whatever red the report contains; if your own run is red, stop, whatever the
  > report says.
  >
  > One new stop: TDD is on, the task touched executable code, and the report carries neither
  > red-run evidence nor a stated reason there was nothing to test. Stop the loop and show the
  > report — that is the same class of failure as a verification that was never run.

  The discriminator is structural: the Butler's own post-Executor run is the sole arbiter of
  pass/fail, and it happens after both halves of the cycle. An expected red only ever appears
  inside a delegated report; a real failure only ever appears in the Butler's own output. They
  never occupy the same channel.

## Files
- `commands/execute.md`
- `commands/next.md`
- `commands/yolo.md`

## Verification
1. `python3 -m unittest discover -s tests -v` — expect `OK`. No test in the suite observes command
   body prose; this run is a regression guard (frontmatter on all three files stays well-formed),
   not proof the new instructions are correct or complete.
2. `grep -c "TS1\|TS2\|TDD" commands/execute.md commands/next.md commands/yolo.md` — expect a
   nonzero count in each file (three sites in `execute.md`, two in `next.md`, four in `yolo.md`).
3. Manual check, not scriptable by line number until the edit lands: open `commands/next.md`'s
   hand-off step and `commands/yolo.md`'s hand-off item side by side and confirm they read
   identically apart from the step reference and one capital letter — this is the control for the
   byte-identical invariant this task exists to preserve.
4. `grep -n "your own" commands/yolo.md` — expect the scoping sentence present in the
   "Check for failure" item, confirming the existing safety stop was not diluted.
