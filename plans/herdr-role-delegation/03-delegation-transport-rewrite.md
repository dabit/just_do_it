status: pending
# 03 - Rewrite the transport in `reference/delegation.md`, the Butler and the Feedbacker

Depends on: None

## Why

`reference/delegation.md` still tells the Butler to drive Herdr with `pane split` → `pane run` →
`wait-output` and explicitly bans `herdr agent start`, which is the opposite of the agent-surface
mechanism this plan adopts, so the transport choice inside rung 2, the wave rules and the
confinement rule all have to land in one change before any command can point at "Choosing the
transport" or before Task 01's operations have a caller.

Rests on: the plan's `### Revision (2026-09-24)` (Herdr only when the harness differs, as a second
way to run rung 2; waves in scope; the idle-without-result case; no watch trigger), the Design
summary's "How blocked states reconcile" decision (`agent prompt` rejects a blocked agent before
sending input, so content questions travel through `result.json` `needs_input` or are answered by
the user in the pane), "\"Validate, never repair\" versus \"detect, never repair\"" (role delegation
"becomes 'detect, never repair, then fall down the ladder'... it always continues natively"), and
"Model flag and authority" (the model flag is the one flag JDI composes on every separate-process
path).

## Description

Write the new test file `tests/test_delegation_transport.py` first (this task creates it; Task 06
later adds a second class to the same file - do not remove or rename what this task writes).

Class `TransportSelectionTest`, over normalized `reference/delegation.md`:
- Present: `## Choosing the transport`, `` `delegation.transport` ``, `` `reference/herdr.md` ``,
  "A role on this session's own CLI never runs under Herdr", "rung 2 runs the other CLI as its
  interactive agent in a Herdr pane", "one pane per task", "A Butler runs one phase at a time.",
  "Herdr's `kinds:` line lists the kinds it supports".
- The three rung openings still appear in order: `**1. The harness has first-class subagents**`,
  `**2. A second non-interactive session**`, `**3. Neither.**`.
- `assertNotIn` for "**0. A separate agent", "asked to watch the run", "Herdr does not report the
  kind installed", "Not `herdr agent start`", and "herdr pane run".

Class `HerdrConfinementTest`:
- For every `*.md` in `commands/`, `agents/`, `roles/` and `reference/` except `reference/herdr.md`,
  plus `skills/run/SKILL.md`, no line matches
  `\bherdr (agent|pane|workspace|worktree|tab|status|integration|server|session|notification|terminal)\b`,
  `HERDR_`, or `AskUserQuestion`.
- This class is red before this task's edit, because `reference/delegation.md:137-141` currently
  holds `herdr pane split` and `herdr agent read`. It stays green through later tasks; Task 08
  confirms `commands/herd.md` is clean too, once it exists.

Class `ButlerSequentialTest`: `roles/butler.md` contains "one phase at a time" and "a delegation
transport".

Note: `FeedbackerIndependenceTest` (checking `agents/feedbacker.md` and `reference/delegation.md` for
"same model and harness") belongs in this task's test file, but its third assertion - that
`commands/feedback.md` contains "a different model or a different harness" - is added by Task 04,
which is the task that edits `feedback.md`. Write the class here with only the two assertions this
task's files satisfy; do not assert on `commands/feedback.md` from this task.

Confirm the new classes fail, then make the edits.

`reference/delegation.md`, in file order:

- Currently at "One rule survives every mapping: **the Feedbacker should not be the same model as the
  agent whose output it is reviewing**...": change the bold clause to "**the Feedbacker should not
  run on the same model and harness as the agent whose output it is reviewing**". The same-model note
  stays, extended to "same model on the same harness".
- Insert a new section, `## Choosing the transport`, before `## How to delegate` (currently the
  heading right after the roles-wanting-a-model table), containing:
  - The literal sentence "A role on this session's own CLI never runs under Herdr." A role with no
    `models.<role>.harness`, or one naming the Butler's own kind, is delegated by rung 1 (or rung 3)
    exactly as before; its progress is watchable in the harness itself.
  - A table, for a role whose `models.<role>.harness` names another CLI (rung 2):

    | `delegation.transport` | What happens |
    |---|---|
    | `native` (default) | Today's rung 2, unchanged: the CLI's own non-interactive mode. Herdr is reached only through rung 4, for a kind with no exec mode. Nothing is probed at step 0 |
    | `auto` | Step 0 performs H1. When it succeeds, rung 2 runs the other CLI as its interactive agent in a Herdr pane, where the user can answer it. Outside Herdr, exactly `native`, and nothing is said; announces once when inside Herdr but a later check fails |
    | `herdr` | As `auto`, but announces any failed H1 check once, then delegates as `native` for the run |

  - Any other value: announce once and treat as native.
  - The literal sentence "A Butler runs one phase at a time." plus "Inside a phase, only a wave runs
    several workers at once, and the Butler waits for all of them before doing anything else in the
    command."
  - "Detect, never repair."
- Currently "Delegation follows observed runtime capability, not the harness name." followed by "When
  a command says... do whichever of these the current harness supports, in this order — unless the
  configuration selects rung 2:" - keep both unchanged. Rung 2 is still the path the configuration
  selects; the transport only changes how rung 2 runs.
- Rungs 1, 2 and 3 keep their bold openings verbatim (`**1. The harness has first-class subagents**`,
  `**2. A second non-interactive session**`, `**3. Neither.** **Adopt the role inline.**`), because
  `tests/test_codex_plugin.py`'s `test_ladder_order_and_corrected_authorization_invariant` pins their
  order. There is no rung 0. At the end of rung 2's paragraph, add: "When `delegation.transport` is
  `auto` or `herdr` and step 0 detected Herdr, rung 2 runs the other CLI as its interactive agent in a
  Herdr pane instead of its non-interactive mode (`reference/herdr.md` H2 to H8). On any Herdr
  failure: announce once, and run the same role through the CLI's non-interactive mode; it is never
  retried on Herdr in the same phase, and the phase is never skipped."
- In *Delegating several roles at once*, the rung-2 bullet (currently "**Rung 2, a second
  non-interactive session**... Under Herdr that is one pane per task, and every pane JDI opened is
  closed on every exit."): keep the bold opening and the first sentence, and change the Herdr
  sentence to: "Under Herdr that is one pane per task, all started together in one wave tab, each with
  its own run directory, at most 4 open at once (`reference/herdr.md`, *Waves*); the Butler waits on
  every worker, sends the user to any pane that is blocked or asking, and every pane JDI opened is
  closed on every exit." The rest of the section (settle the whole wave, never cancel a sibling, one
  commit per task by path) is unchanged and applies to Herdr workers as written. No existing test pins
  the sentence being replaced (checked: `tests/test_parallel_waves.py` pins only the heading and
  `*Delegating several`).
- In *Where a role runs*, the paragraph currently ending "Resolution is **exec-first, Herdr second**.":
  keep the first two sentences of that paragraph, change the last to: "Under `transport: native`,
  resolution is exec-first, Herdr second. Under `auto` or `herdr` with Herdr detected, a role on
  another CLI runs in a Herdr pane first, and exec is its fallback."
- Keep the "Prefer the CLI's own non-interactive mode" paragraph and its three bullets
  (`codex exec -m <model> -o <file>`, `opencode run`, `claude -p`) verbatim, and the
  "`harness: claude` is a first-class value" paragraph verbatim - both are pinned. Add one sentence
  after them: "The model flag is the one flag JDI composes from the config, on every separate-process
  path, exactly as above."
- Replace the two paragraphs currently reading "**Use Herdr only**... `herdr pane split` → `herdr
  pane run <PANE_ID> <command>` → `herdr pane wait-output`... **Not `herdr agent start`**... and not
  `herdr agent read`..." and "**A pane JDI created is JDI's to close.**..." with these two paragraphs,
  with no `herdr` command in either:
  - **Herdr.** Under `native`, Herdr is used only when the kind has no exec mode JDI knows. Under
    `auto` or `herdr` it is how rung 2 runs another CLI when Herdr is detected. Every Herdr step
    (detection, pane, start, prompt and wait, states, the result contract, waves, pane close) is in
    `reference/herdr.md` and nowhere else. It uses Herdr's agent surface and receives the report
    through a file, and `reference/herdr.md` gives the reason.
  - **A pane JDI created is JDI's to close** (H8).

  The current "or when the user has asked to watch the run" trigger is dropped and not mentioned in
  the new text (`TransportSelectionTest` asserts its absence). The reason, recorded in the plan's
  revision: a subagent is watchable in its own harness, and a role on another CLI already gets a pane
  under `auto` or `herdr`.
- After "**Role instructions have to travel.**..." (ending "...forbids searching ancestors for a
  plausible checkout."), add: "Under Herdr, the role file is copied into the run's `prompt.md`
  (`reference/herdr.md` H3)." The rest of that section is unchanged.
- Under "## What delegation does not grant", keep every sentence verbatim (this section is pinned by
  `test_ladder_order_and_corrected_authorization_invariant`'s assertions). Append:
  - A Herdr worker is a separately spawned CLI in this sense.
  - The worker's approval, permission and trust dialogs belong to the user, and the Butler never
    answers one.
  - The Butler answers a worker's content question only from context it already holds, and says so.
  - A worker writes only its run directory and what the active command lets the role write, and the
    Butler checks the tree afterward (H7).
- Under "## When the configuration cannot be honoured", rungs 4 and 6-9:
  - Rung 4: "Try the Herdr transport, `reference/herdr.md` H1 to H8 (rungs 6-9)."
  - Rung 6: "Herdr is wanted but not detected. H1 failed at step 0."
  - Rung 7 becomes: "**The kind is not one Herdr supports, or its CLI is not installed.** Herdr's
    `kinds:` line lists the kinds it supports; installed means `<kind>` resolves on `PATH`.
    Integration status affects only detection quality." This fixes the current misreading ("Herdr
    does not report the kind installed").
  - Rung 8: "The pane or the agent cannot be started."
  - Rung 9: "The run started but produced no valid result. H7 failed, or the state stayed `unknown`
    or timed out and the user chose to abandon. `unknown` does not prove completion."
  - The shared tail for rungs 6 to 9: "Close the pane JDI opened (H8), announce, and continue as
    `native` would resolve the role: rung 2's non-interactive mode, or the floor where rung 4 sent a
    kind with no exec mode."
- Under "Four directions the ladder never takes", keep "Never acquire a flag the user did not write."
  verbatim (pinned). Change the next sentence to: "JDI composes only the invocation and the model
  flag, adds no authority-affecting argument of its own, and translates none between kinds."

`roles/butler.md`:
- After "**Verify before relaying.**..." (ending "...before telling the user a task passed"), append
  a new bullet: "A report from a separately launched worker is accepted only through its validated
  result file, never a transcript."
- Change the "**Resolve capabilities once...**" bullet's list (currently "A test runner, a tracker
  integration, a Jev API key") to "A test runner, a tracker integration, a Jev API key, a delegation
  transport".
- Add a new sentence in the Responsibilities list: "A Butler runs one phase at a time; inside a
  phase, only a wave runs several workers at once, and the Butler waits for all of them."
- No Herdr command appears anywhere in this file.

`agents/feedbacker.md`: currently "Where the config offers more than one model, the Feedbacker should
not be the same model that produced the output under review... If only one model is available, run
the review anyway and say that producer and reviewer were the same model." Change to "should not run
on the same model and harness that produced the output under review", and "If no different model or
harness is available, run the review anyway and say that producer and reviewer were the same."

Existing test assertions to rewrite in `tests/test_codex_plugin.py`:
- `test_harness_is_a_first_class_value_in_both_directions`: currently asserts `"herdr pane split"` and
  `"Not \`herdr agent start\`"`. Remove both. Keep `"\`harness: claude\` is a first-class value"` and
  add `"\`reference/herdr.md\`"`.
- `test_degradation_ladder_runs_from_the_first_rung_to_the_floor`: currently asserts `"herdr pane
  close"`. Remove it; that string now lives only in `tests/test_herdr_operations.py`'s
  `HerdrOperationsTest` (Task 01). Keep the rest of the assertions in that test (`"one announcement,
  not two"`, `"**The phase always runs.**"`, `"Never skip the phase."`, `"Never acquire a flag the
  user did not write."`).

## Files

- `reference/delegation.md`
- `roles/butler.md`
- `agents/feedbacker.md`
- `tests/test_codex_plugin.py`
- `tests/test_delegation_transport.py` (new)

## Verification

- `python3 -m unittest tests.test_delegation_transport -v` - the three new classes
  (`TransportSelectionTest`, `HerdrConfinementTest`, `ButlerSequentialTest`) fail before the edits
  (`HerdrConfinementTest` fails specifically because `reference/delegation.md` still names `herdr
  pane split`), pass after.
- `python3 -m unittest tests.test_codex_plugin.ManualInvocationGuidanceTest -v` - passes with the
  rewritten assertions; grep the test file first to confirm the old `"herdr pane split"` and `"Not
  \`herdr agent start\`"` / `"herdr pane close"` literals are gone from the assertions themselves, not
  just from the source file.
- `grep -n "herdr" reference/delegation.md roles/butler.md agents/feedbacker.md` - empty (no bare
  `herdr` mention outside `reference/herdr.md`).
- `python3 -m unittest discover -s tests -v` - no new failures.
