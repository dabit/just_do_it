status: pending
# 05 - User-facing docs: init, help, README

Depends on: 01, 02

## Why

`/jdi:init` has to be able to ask the new question and `/jdi:help` and the README have to describe
the resulting behavior, and neither can be written accurately until the operation it names (H1, from
Task 01) and the key it sets (`delegation.transport`, from Task 02) both exist.

Rests on: the Design summary's "What `auto` and `herdr` do" decision and the config key's "usually
personal" property ("Two repos or two people would answer differently: yes. Whether someone works
inside Herdr is a fact about their machine, so `.jdi/config.local.yml` is its natural home").

## Description

Write `tests/test_transport_docs.py` first, class `TransportDocumentationTest`:

- The `commands/init.md` frontmatter `description:` contains "how delegated roles reach their own
  process".
- `commands/init.md` contains "`delegation.transport`" and "perform **H1**".
- `commands/help.md` has the heading `### Separate agent processes`, and its first paragraph
  (`jdi_files.paragraph_starting_with(text, "Explain the Just Do It")`) contains "delegation
  transport".
- `README.md` has the heading `### Separate agent processes under Herdr`, and that section contains
  "`delegation.transport`".
- That README section contains "one pane per task" and "stays a subagent", and does not contain
  "waves unaffected".
- The existing `ReadmeCodexDocumentationTest.test_scope_snapshot_and_capability_delegation_are_accurate`
  (`tests/test_codex_plugin.py`) must stay green - it proves the "### Roles and models, not agents and
  vendors" section keeps its three pinned phrases ("Delegation follows observed runtime capability",
  "a suitable generic subagent", "adopt the role inline and announce the switch") after this task adds
  a bullet to that section.

Confirm the new class fails, then make the edits.

`commands/init.md`:
- Frontmatter `description:` (currently "...whether roles may ask Jev for typed judgments, where
  plans and docs live, and which model each role runs on."): add ", how delegated roles reach their
  own process," before "and which model each role runs on".
- Insert a new step 10 after the current models step (step 9, lines 141-169: "**Ask which model each
  role runs on...**"): **Ask how delegated roles should run - only when this session is inside
  Herdr.**
  - Perform **H1** from `reference/herdr.md`.
  - When `HERDR_ENV` is unset, skip the question entirely and write no `delegation` block.
  - Otherwise, propose `native` (the default) and explain `auto` and `herdr` in one sentence each.
    Say that the key only matters for a role whose `models.<role>.harness` names another CLI: such a
    role then runs in its own pane where the user can answer it, one pane per task in a wave, while a
    role on this session's own CLI always stays a subagent.
  - Say that it is usually personal, and offer to leave it out of `config.yml` for `config.local.yml`.
- Renumber the old steps 10-13 (currently: 10 "Ask about consumers", 11 "Write `.jdi/config.yml`",
  12 "Offer to record the branch and commit conventions", 13 "Report and point at the next step") as
  11-14.
- Fix the back-reference currently at line 24 ("If git tracks the local file, say so now; step 11
  offers the fix."): change "step 11" to "step 12" (the git-tracked-local-file fix is in what becomes
  step 12 after renumbering).
- Run `grep -n "step [0-9]" commands/init.md` after the edit. The current hits at lines 67, 74, 113,
  139 and 168 refer to steps 1-3 and are unaffected by inserting a step after step 9 - confirm they
  still read correctly, but do not renumber them.

`commands/help.md`:
- The closing-line instruction (currently ending "...which roles have a model configured and whether
  any of them runs in another agent CLI, whether `.jdi/config.yml` exists at all, and whether a
  `.jdi/config.local.yml` overrides any of it"): add "which delegation transport is set, when it is
  not `native`".
- The `/jdi:init` table row (currently "Set JDI up for this repo — tracker, split pieces, TDD, Jev,
  plan store, docs folder, models."): add "delegation transport" to the enumeration.
- The `/jdi:prep` table row (currently "Run start, research, plan, and split in one pass. Stops only
  for real questions, and leaves a task list ready for `/jdi:yolo`."): add "Runs a role configured on
  another CLI in its own pane when `delegation.transport` allows it."
- A new `### Separate agent processes` subsection, inserted after `### Roles and models` (currently
  ending "...they just share one context window.", before `### Personal overrides`). Two paragraphs:
  - What `auto` and `herdr` do: a role on another CLI runs as that CLI's interactive agent in its own
    pane, every Executor of a wave gets its own pane, and the result arrives as a file the Butler
    validates. A role on this session's own CLI stays a subagent.
  - Blocked or questioning workers are answered by you in their pane, the rest falls back to the
    CLI's non-interactive mode, and `native` is silent.

`README.md`:
- The `/jdi:init` snippet comment (currently
  `/jdi:init      # asks about the tracker, the split pieces, TDD, Jev, the plan store, the docs folder, and models`)
  and the prose enumeration right below it (currently "`/jdi:init` asks about the tracker, what the
  split pieces should become, whether the Executor should write tests first (TDD), whether roles may
  ask Jev for typed judgments, where plans should live, where architecture docs live, and which model
  each role runs on."): add "how delegated roles reach their own process" to both.
- A new `### Separate agent processes under Herdr` section, inserted after `### Typed judgments with
  Jev` (currently ending "...uncommitted is not the same as secret.", before `## Use it`). It has a
  `| \`delegation.transport\` | What you get |` table with three rows (mirroring the table this plan
  writes into `reference/delegation.md`'s "Choosing the transport" in Task 03), then paragraphs
  covering: only roles on another CLI are affected, the run directory, validation before use,
  blocked and questioning workers answered in their pane, waves as one pane per task (at most 4 at
  once, in one tab), the fallback, and one phase at a time.
- `### Roles and models, not agents and vendors` (currently three bullets: "A matching role is
  registered", "Generic subagents are available", "No subagents are available"): add one bullet
  **after** the three existing ones: "**A role is set on another CLI** → run that CLI's
  non-interactive mode, or, when `delegation.transport` allows it and Herdr is detected, its
  interactive agent in a Herdr pane you can answer; either way the Butler waits for its validated
  result." Keep the three
  existing bullets verbatim, including their exact wording ("Delegation follows observed runtime
  capability", "a suitable generic subagent", "adopt the role inline and announce the switch"), which
  `tests/test_codex_plugin.py`'s `test_scope_snapshot_and_capability_delegation_are_accurate` pins.

What no automated test can observe in this task: the renumbering of init steps 11-14 and the fixed
back-reference at line 24, and the quality of the new question's wording. Run
`grep -n "step [0-9]" commands/init.md` yourself and paste the output into the task report, and note
in the report that the reviewer verifies the question wording by reading.

## Files

- `commands/init.md`
- `commands/help.md`
- `README.md`
- `tests/test_transport_docs.py` (new)

## Verification

- `python3 -m unittest tests.test_transport_docs -v` - fails before the edits (no `### Separate agent
  processes` heading, no `delegation.transport` mention in `commands/init.md`), passes after.
- `python3 -m unittest tests.test_codex_plugin.ReadmeCodexDocumentationTest -v` - stays green,
  confirming the new bullet in "### Roles and models, not agents and vendors" did not disturb the
  three pinned phrases.
- `grep -n "step [0-9]" commands/init.md` - paste the output into the report; confirm line 24 now
  reads "step 12" and no other numbered back-reference needs to change.
- `python3 -m unittest discover -s tests -v` - no new failures.
