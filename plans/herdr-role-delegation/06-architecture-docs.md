status: done
# 06 - Architecture docs

Depends on: 01, 02, 03

## Why

The new architecture doc has to describe the mechanism Tasks 01-03 actually built (the operations,
the config key, and the rung-2 transport choice with waves), and `docs/config-key-lifecycle.md`'s own citations into
`reference/config.md` need re-deriving against the post-Task-02 file, so this task cannot start until
all three exist.

Rests on: the plan's `### Revision (2026-09-24)`, the Design summary's "The result contract"
decision, "How blocked states reconcile", and
the plan's "Relationship to PR #5" note ("PR #5 closes as superseded when the herd wave ships, or is
rebased onto this contract if the wave is dropped").

## Description

Extend `tests/test_delegation_transport.py` (created in Task 03) with a new class,
`ArchitectureDocTest`. Do not touch the classes Task 03 or Task 04 added to this file.

- `docs/delegation-transport-architecture.md` exists with the headings `## Two layers`, `## Result
  contract`, `## Waves and other roles`, `## Live validation matrix` and `## Relationship to PR #5`,
  and not `## Extending to other roles and waves`.
- It contains "only when the harness differs" and "same-harness control".
- It contains "`reference/herdr.md`", "validate, never repair" and "detect, never repair".
- `jdi_files.section(docs/harness-adapter-architecture.md, "## Capability-Based Delegation")` contains
  "`delegation.transport`".
- `docs/config-key-lifecycle.md` contains "`commands/prep.md:28-29`" and does not contain "are all
  `1.0.6`".
- The existing `ReleaseDocumentationTest` (`tests/test_versions.py`) must stay green.

Confirm `ArchitectureDocTest` fails, then make the edits.

Write `docs/delegation-transport-architecture.md`. The headings are pinned by the test above; write
these sections, in order:
- `# Delegation Transport Architecture`
- `## Status`
- `## Purpose`
- `## Two layers`: `/jdi:herd` fans tickets out to independent Butlers, one worktree, workspace,
  branch and ticket each. Inside one Butler, one phase at a time; inside a phase, only a wave runs
  several workers at once, and the Butler waits for all of them. The Butler never multitasks across
  unrelated work.
- `## Backend choice`: Herdr only when the harness differs. A role on the Butler's own CLI is a
  native subagent, watchable in the harness itself. A role on another CLI runs through rung 2: that
  CLI's interactive agent in a Herdr pane the user can answer, under `auto` or `herdr` with Herdr
  detected, otherwise its non-interactive mode. Why the agent surface. Record that this overrides the
  brief's "prefer Herdr over native subagents", and why.
- `## Capability detection`: H1, and why never the harness name.
- `## Result contract`: the files (`manifest.json`, `prompt.md`, `report.md`, `result.json`,
  `outcome.json`), the fields, H7, and why a file instead of a transcript.
- `## States`: a summary, with a reference to H5.
- `## Authority`
- `## Isolation`: worktrees, and workers sharing the Butler's worktree.
- `## Configuration`: `delegation.transport`, `models.<role>`, `harnesses.<kind>`, and the herd keys
  (name them as forthcoming - `herd.kind`, `herd.max_parallel`, `herd.seed` - even though they do not
  land until a later task; this section describes the whole configuration surface the mechanism
  touches).
- `## Validate, never repair versus detect, never repair`: `/jdi:herd` keeps "validate, never repair"
  and stops, with no fallback. Role delegation is "detect, never repair, then fall down the ladder"
  and always continues natively.
- `## Waves and other roles`: every role on another CLI uses the same H2 to H8. Executors in a wave
  get one pane per task in one wave tab, at most 4 open at once, a multi-worker wait, and the
  combined file check; one phase at a time replaces the brief's "one active delegated role per
  Butler", and why (waves already ran concurrently through rung 2 processes, so panes add
  observability, not concurrency).
- `## Live validation matrix`: Butler Claude Code in Herdr; worker A `opencode` (single role and a
  wave), worker B the same-harness control (a role with `harness: claude` under a Claude Butler runs
  as a native subagent, no pane), worker C `codex` (requires install). Refer to this plan's UAT task
  (Task 10) by number.
- `## Relationship to PR #5`: the herd layer's contract is H1, H2, H4b and the H9 that `/jdi:herd`
  adds (Task 08). PR #5 closes as superseded when the herd wave ships, or is rebased onto this
  contract if the wave is dropped.

`docs/harness-adapter-architecture.md`:
- In `## Capability-Based Delegation` (currently a three-item numbered list: "1. Use a first-class
  subagent...", "2. Run a second non-interactive session...", "3. Adopt the role inline..."), add a
  sentence to item 2 instead of a new item (there is no rung 0): "When `delegation.transport` allows
  it and Herdr is detected, this runs the other CLI as its interactive agent in a Herdr pane, one
  pane per task in a wave (`reference/herdr.md`)." Items 1 and 3 are unchanged.
- In that same section's second list item ("2. Run a second non-interactive session — selected by
  `models.<role>.harness`, not only a fallback."), qualify it to read "under `native`" before its
  "exec-first" sense, so the summary does not imply this is the only path once `auto`/`herdr` exist.
  Read the current wording carefully: the phrase "exec-first" itself lives in
  `reference/delegation.md:120`, not in this file today, so treat this edit as adding the
  `native`-scoping qualifier to this file's existing item 2, matching how `reference/delegation.md`'s
  own "exec-first, Herdr second" sentence was qualified in Task 03.
- In the `## Canonical Sources` table's `reference/*.md` row (currently "Shared configuration,
  testing, tracker, plan-store, and delegation contracts"), add "Herdr" to the list.

`docs/config-key-lifecycle.md`. These are passing corrections; say so in the commit body:
- The two "are all `1.0.6`" sites (currently "`.claude-plugin/plugin.json:3`,
  `.codex-plugin/plugin.json:3`, and `.claude-plugin/marketplace.json:10` are all `1.0.6` right now."
  and, later, "...and `.claude-plugin/marketplace.json:10`, all `1.0.6`."): change both to "carry the
  same version". Keep "**Three version files, and they must match.**" and the other strings
  `tests/test_versions.py`'s `ReleaseDocumentationTest` pins (`"Nine files are the **floor**"`,
  `"three JSON version edits"`, `"The nine mandatory files:"`,
  `"- [ ] \`.codex-plugin/plugin.json\` — the **same** version."`).
- The `reference/config.md` line-range citations (currently: schema block `:17-179`, `split:` at
  `:42-55`, defaults table `:214-230` with `split.pieces` at `:220`, notes `:232-281` with
  `split.pieces`'s two bullets at `:236-239` and `:240-243`): open the post-Task-02
  `reference/config.md`, find the real current line numbers for the schema fence, the `split:` block,
  the defaults table, `split.pieces`'s defaults row, the `## Notes` section, and `split.pieces`'s two
  bullets, and correct every one of these ranges to match. Quote the first line at each corrected
  range in the task report as evidence, per this task's own "what no test can observe" note below.
- Currently "The load itself is repeated in twelve of the sixteen command files... `commands/prep.md:23-24`
  says..." - no, check the actual current text: the citation this plan calls out is
  `commands/prep.md:23-24` becoming `commands/prep.md:28-29`, with `commands/research.md:23-24` added
  alongside it (both now point at the "Everything below refers to..." sentence Task 04 touched).
- The checklist item currently reading "`commands/prep.md:23-24` — the literal list of config block
  names includes the new block." and the nearby citations of `README.md:290-294` and
  `AGENTS.md:49-53`: correct all three to the lines they actually sit at now (`README.md`'s reference
  table row for `reference/delegation.md`, and `AGENTS.md`'s **Reference files.** paragraph - both
  edited in Task 01, so re-derive against the post-Task-01 files).
- Verify every `reference/config.md:` citation in the whole file against the post-Task-02 file while
  you are in it, not only the ones named above.

What no test can observe in this task: the correctness of the re-derived `reference/config.md` line
ranges. Prove it by opening each cited range and quoting its first line in the task report.

## Files

- `docs/delegation-transport-architecture.md` (new)
- `docs/harness-adapter-architecture.md`
- `docs/config-key-lifecycle.md`
- `tests/test_delegation_transport.py` (adds `ArchitectureDocTest`)

## Verification

- `python3 -m unittest tests.test_delegation_transport.ArchitectureDocTest -v` - fails before
  `docs/delegation-transport-architecture.md` exists and before the two `docs/config-key-lifecycle.md`
  corrections land, passes after.
- `python3 -m unittest tests.test_versions.ReleaseDocumentationTest -v` - stays green.
- `grep -n "are all \`1.0.6\`" docs/config-key-lifecycle.md` - empty.
- `grep -n "reference/config.md:" docs/config-key-lifecycle.md` - paste the output and the first line
  of each cited range into the task report as the evidence the re-derivation is correct.
- `python3 -m unittest discover -s tests -v` - no new failures.
