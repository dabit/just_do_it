status: done
# 04 - Command step-0 lines and hand-off sites

Depends on: 02, 03, 06

## Why

Every command that loads the config has to resolve `delegation.transport` once, at step 0, exactly
the way it already resolves Jev - otherwise a role could re-probe H1 mid-command and get a different
answer than its siblings. Waves now use the transport too (one pane per task under `auto` or
`herdr`), so the three wave commands get the line as well. This task needs the `delegation` key
(Task 02) and the rung-2 transport choice plus `## Choosing the transport` (Task 03) to exist before
it can point at them.

The dependency on Task 06 is declared only because both tasks edit `tests/test_delegation_transport.py`
- this task adds one assertion to the `FeedbackerIndependenceTest` class Task 03 created (the plan's
Testing Strategy is explicit that this assertion belongs with the task that edits `commands/feedback.md`,
not with Task 03), while Task 06 adds a separate `ArchitectureDocTest` class to the same file. Neither
edit needs the other's content; they cannot run in the same wave only because they share a path. This
task runs after Task 06 rather than the reverse because it keeps the overall critical path shorter (Task
06 would otherwise need to wait on this task's much larger command-file surface).

Rests on: the Design summary's "What `auto` and `herdr` do" decision ("Step 0 performs H1 once...
`auto` stays silent when `HERDR_ENV` is unset... `herdr` announces any failed check once. In both
modes, a failure hands the role back to native resolution. The phase always runs.") and the plan's
`### Revision (2026-09-24)`: the transport applies to every role on another CLI, Executor waves
included, with no role-file changes.

## Description

Write `tests/test_step_zero_transport.py` first:

- `StepZeroTransportTest`: for each of `prep`, `research`, `plan`, `split`, `feedback`, `pr`,
  `execute`, `next` and `yolo` (nine files), the
  normalized file (`" ".join(text.split())`) contains "**Then resolve the delegation transport,
  once**", "perform **H1** from JDI's `reference/herdr.md`", and "With `delegation.transport` `native`
  or absent, say nothing at all".
- `prep.md` contains "`models`, `harnesses`, and `delegation` from it".
- `research.md` contains "`models`, `harnesses`, and `delegation` from that config".
- `WaveTransportTest`: `execute.md`, `next.md` and `yolo.md` each contain "including the transport
  `delegation.transport` selects", and none contains "does not apply to a wave" or the word "Herdr"
  (the bodies stay provider-neutral).
- `ValidationGateTest`: `prep.md` and `research.md` each contain "the result file the transport
  validated".
- `FeedbackerIndependenceTest`'s third assertion, added to the class Task 03 already wrote in
  `tests/test_delegation_transport.py`: `commands/feedback.md` contains "a different model or a
  different harness". Add this one assertion to that existing class in that file; do not create a
  second class of the same name.

Confirm all of the above fail, then make the edits.

**The step-0 line, inserted as a new paragraph at the end of step 0 in each of nine files.** In six
files it goes right after the Jev paragraph's last sentence, "With `jev.enabled` false or absent,
say nothing at all — nothing was skipped." (the last line of step 0 at `prep.md:39`,
`research.md:33`, `plan.md:32`, `split.md:32`, `feedback.md:36`, `pr.md:33`, verified at base
`94912b3`). The three wave commands have no Jev paragraph: there it goes right after the config-load
step's last sentence, "...and say so if git tracks it, because it is meant to be ignored."
(`execute.md:23`, `next.md:21`, `yolo.md:21`, verified at base `94912b3`), as a new paragraph still
inside step 0. The text is literal apart from its own line wrap:

> **Then resolve the delegation transport, once** - If `delegation.transport` is `auto` or `herdr`,
> perform **H1** from JDI's `reference/herdr.md` here and nowhere else, and use its answer for every
> delegation in this run; no role re-probes. With `herdr`, a failed check is announced once, with the
> check and what came back, and this run delegates as `native`. With `auto`, say nothing when this
> session is not inside Herdr, and announce once when it is but a later check fails. With any other
> value, say so once and delegate as `native`. **With `delegation.transport` `native` or absent, say
> nothing at all** - nothing was skipped.

Other edits:
- `prep.md`, currently "Everything below refers to `tracker`, `split`, `plans`, `docs`, `consumers`,
  `jev`, `models`, and `harnesses` from it." becomes "...`jev`, `models`, `harnesses`, and
  `delegation` from it."
- `research.md`, currently "Everything below refers to `tracker`, `plans`, `docs`, `consumers`,
  `jev`, `models`, and `harnesses` from that config." becomes "...`jev`, `models`, `harnesses`, and
  `delegation` from that config."
- `prep.md` step 9 (currently "**Update the references** — Merge the findings into `##
  References`..."): prepend "When the Researcher ran as a separate process, its findings are the
  result file the transport validated (`reference/delegation.md`), never a terminal transcript; a
  result that failed validation was already announced and the role re-run another way."
- `research.md` step 4 (currently "**Present the findings** — Show the user what the Researcher
  found..."): add the same sentence.
- `prep.md` step 10 (currently "**Draft a missing architecture doc when one is needed**...") and
  `research.md` step 5 (currently "**Write the missing doc (if approved)**..."): add "delegated
  exactly as in step 8" to `prep.md`'s step 10 and "delegated exactly as in step 3" to `research.md`'s
  step 5. These are within-file references (step 8 in `prep.md` is "Delegate to the Researcher"; step
  3 in `research.md` is "Delegate to the Researcher").
- `feedback.md` step 3 (currently "**Delegate to the Feedbacker** — ... pick a different model from
  the one that produced the output... If only one is available, run the review anyway and say that
  producer and reviewer were the same model."): change to "pick a different model or a different
  harness from the one that produced the output" and "If neither differs, run the review anyway and
  say that producer and reviewer were the same." Then, after the paragraph currently ending
  "...if it does not return promptly, run the review inline yourself, say the fallback ran, and
  proceed." (feedback.md's step 3, final paragraph), append: "When the transport waits on a separate
  process, that wait is this active turn, and its timeout handling replaces 'promptly'."
- `execute.md`, `next.md`, `yolo.md`: at each site currently reading "...see *Delegating several
  roles at once* in JDI's `reference/delegation.md`..." (the Executor hand-off step in each file),
  add one sentence: "Each Executor is resolved per *Delegating several roles at once*, including the
  transport `delegation.transport` selects; a worker waiting on the user is answered where it runs,
  and the wave settles before anything is verified or committed." No transport name, vendor, or
  Herdr term appears in these bodies. Keep the exact phrase
  "*Delegating several", which `tests/test_parallel_waves.py` pins in
  `test_every_command_that_runs_a_wave_cites_concurrent_delegation`.
- `commands/reresearch.md` and `commands/replan.md`: leave unchanged. They inherit the new step-0 line
  through their sibling command's step 0, by name (`reresearch.md:16` says "follow `/jdi:research`
  fully" or similar - verify the exact wording when editing and do not add a duplicate step-0 line).
  Say in the commit body that these two are deliberately unchanged.
- `commands/status.md`, `commands/done.md`, `commands/start.md`: these do not delegate. Leave them
  unchanged and say so in the commit body.

## Files

- `commands/prep.md`
- `commands/research.md`
- `commands/plan.md`
- `commands/split.md`
- `commands/feedback.md`
- `commands/pr.md`
- `commands/execute.md`
- `commands/next.md`
- `commands/yolo.md`
- `tests/test_step_zero_transport.py` (new)
- `tests/test_delegation_transport.py` (adds one assertion to the existing `FeedbackerIndependenceTest`
  class)

## Verification

- `python3 -m unittest tests.test_step_zero_transport -v` - fails before the nine step-0 insertions,
  the three wave-command sentences and the two validation-gate sentences, passes after all are in
  place.
- `python3 -m unittest tests.test_delegation_transport.FeedbackerIndependenceTest -v` - fails before
  `feedback.md`'s wording change, passes after (it also still checks the two assertions Task 03 wrote
  against `agents/feedbacker.md` and `reference/delegation.md`, which do not change in this task).
- `python3 -m unittest tests.test_parallel_waves -v` - stays green; confirms the added sentence in
  `execute.md`, `next.md`, `yolo.md` did not disturb the pinned "*Delegating several" phrase or the
  `*Waves*` citation.
- `grep -n "delegation.transport" commands/prep.md commands/research.md commands/plan.md \
  commands/split.md commands/feedback.md commands/pr.md commands/execute.md commands/next.md \
  commands/yolo.md` - each of the nine files shows at least one hit.
- `python3 -m unittest discover -s tests -v` - no new failures.
