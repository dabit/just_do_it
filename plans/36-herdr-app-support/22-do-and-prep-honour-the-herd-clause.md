status: done
# 22 — `/jdi:do` and `/jdi:prep` honour the herd clause; `/jdi:do` updates a branch the default moved under

Depends on: 21

## Why
A herd-started `/jdi:do` that finds the work too big for one session before step 6 has changed anything must say so in one line and continue with `/jdi:prep` in the same session, pushing nothing, instead of handing back; a herd-started `/jdi:prep` must take the herd's tracking answer instead of asking; both leave the clause out of the work. And `/jdi:do` step 10 must update a branch whose pull request stopped merging cleanly because a parallel change merged first, standalone or not. Depends on 21 because the clause strings are defined in H9 and a test here reads them there. Rests on: E1, E7, M1, M4, M8.

## Description
Planner's Task 22. Append the M-E sentences to four paragraphs, three in `commands/do.md` (steps
1, 5 and 10) and one in `commands/prep.md` (step 2), and pin them in a new
`tests/test_herd_handoff.py`.

**Before starting, confirm Task 21 is in:** `grep -c '(untracked, started by /jdi:herd)' reference/herdr.md`
prints at least `1`. `test_clauses_match_h9` reads H9.

**Rules:**
- **Every insertion stays inside its paragraph.** The tests read paragraphs with
  `jdi_files.paragraph_starting_with`, which stops at the first blank line. No blank line inside any
  of the four paragraphs; do not renumber any step.
- Both command files are scanned by `HerdrConfinementTest`: no `herdr <subcommand>`, `herdr-app`,
  `hc`, `HC_*`, `HERDR_*` or `space.close`-style names. The M-E text has none.
- **Standalone `/jdi:do` is unchanged**, except step 10 (M4), which applies to every run. The *Too
  big* bullet keeps "Recommend `/jdi:prep` with what you learned".
- Known, not fixed here (R24, M8): in an OpenCode project sync, `${CLAUDE_PLUGIN_ROOT}` is rewritten
  to `.opencode/jdi`, where no `commands/prep.md` exists; the sentence's "the prep command file
  beside this one" is the fallback that covers it. UAT (u7) is where it is observed.

TDD is on: write the tests first and watch them fail on their own assertions.

### 1. Tests first: new `tests/test_herd_handoff.py`
A module docstring saying what it guards (a herd-started `/jdi:do` continues into `/jdi:prep`; a
herd-started `/jdi:prep` asks no tracking question; both clauses match H9; `/jdi:do` step 10
updates a branch the default moved under). Import `unittest` and `jdi_files`; define
`normalized(text) = " ".join(text.split())` and a helper
`paragraph(path, prefix) = normalized(" ".join(jdi_files.paragraph_starting_with(jdi_files.read(path), prefix)))`.

**Deviation from `DoPlanShapeTest` (record it in the docstring):** that class's `step()` helper
lives in `tests/test_structural_checks.py`; importing it would make unittest collect that module's
classes a second time, so this module uses `jdi_files.paragraph_starting_with`, which stops at the
first blank line.

Constants: `CLAUSES = ("`(started by /jdi:herd)`", "`(untracked, started by /jdi:herd)`")` (each
with its backticks).

- `test_too_big_in_a_herd_continues_with_prep`: `p = paragraph("commands/do.md", "   - **Too big for one session.**")`
  (three spaces, then `- `). The step-5 bullets have no blank line between them, so the paragraph
  runs to the end of the list; cut it to the *Too big* bullet:
  `bullet = p[p.index("**Too big for one session.**"):p.index("**A product decision outside the request.**")]`.
  Assert, one `subTest` each, that `bullet` contains: both `CLAUSES`, `before step 6 has changed anything`,
  `do not hand back`, `Say in one line that the work is too big for one session`,
  ``continue with `/jdi:prep` ``, `in this session`, `Push nothing`,
  `prep's step 6 keeps the branch step 2 created`.
- `test_standalone_too_big_still_hands_back`: the same `bullet` contains
  ``Recommend `/jdi:prep` with what you learned``. (A guard: green before and after.)
- `test_clause_is_not_part_of_the_work`: `paragraph("commands/do.md", "1. **Identify the work**")`
  contains `that clause is not part of the work`.
- `test_merge_updates_a_branch_the_default_moved_under`: `paragraph("commands/do.md", "10. **Merge**")`
  contains `a parallel change merged first`, `run step 7's gates again`, `a step-5 stop`.
- `test_prep_takes_the_herds_tracking_answer`: `paragraph("commands/prep.md", "2. **Determine the tracking context**")`
  contains both `CLAUSES`, `Ask neither`, `The clause is not part of the work`.
- `test_clauses_match_h9`: for each clause, one `subTest` per source, the clause is in the normalized
  `jdi_files.section(jdi_files.read("reference/herdr.md"), "## H9 - Give a Butler its own worktree")`,
  in `normalized(jdi_files.read("commands/do.md"))` and in `normalized(jdi_files.read("commands/prep.md"))`.

### 2. Edits (M-E; prose may be rewrapped to the file's width, wording exact)

1. **`commands/do.md` step 1**, end of its **first** paragraph (the one that starts
   `1. **Identify the work**` and ends "…this command does not ask for one)."; at base it is four
   lines, followed by a blank line):
   > A request that ends with `(started by /jdi:herd)` or `(untracked, started by /jdi:herd)` came from a herd: that clause is not part of the work, so leave it out of the branch name, the commits and the pull request, and with `untracked` run no tracker step at all.
2. **`commands/do.md` step 5**, end of the *Too big for one session* bullet (after "…This is the
   expected exit for large work, not a failure."), continuing the same bullet, indented five spaces
   like its other continuation lines:
   > **Started by `/jdi:herd`** (the request ends with `(started by /jdi:herd)` or `(untracked, started by /jdi:herd)`) **and found before step 6 has changed anything:** do not hand back. Say in one line that the work is too big for one session, why, and that you continue with `/jdi:prep`; then read JDI's prep command (`${CLAUDE_PLUGIN_ROOT}/commands/prep.md`, or, if that variable does not resolve, the prep command file beside this one) and follow its steps on the same request in this session, with what you learned. Push nothing and note nothing on the issue first: prep's step 6 keeps the branch step 2 created, because it already names this work, and creates one when step 2 has not run yet.
3. **`commands/do.md` step 10**, appended to its paragraph (after "…unless the repository's
   instructions tell you to."), indented four spaces like the paragraph:
   > When the pull request no longer merges cleanly because the default branch moved (a parallel change merged first), bring the branch up to date with `origin/<default>` the way the repository allows, run step 7's gates again, push, and wait for the checks on the new head; a conflict whose resolution needs a product decision is a step-5 stop.
4. **`commands/prep.md` step 2**, appended to its paragraph (after "\"Not tracked\" is a fine
   answer."):
   > When the request ends with `(started by /jdi:herd)` or `(untracked, started by /jdi:herd)`, the herd has answered this step and step 3's question: an issue in it uses the configured tracker, and `untracked` means not tracked. Ask neither. The clause is not part of the work: leave it out of the slug and the title.

Nothing else in either file changes.

## Files
- `commands/do.md`
- `commands/prep.md`
- `tests/test_herd_handoff.py`

## Verification
Run from the repository root.

1. **Red first.** After writing the tests, before editing the commands: `python3 -m unittest discover -s tests -p 'test_herd_handoff.py' -v` — expected: `Ran 6 tests`, `FAILED`; every method fails except `test_standalone_too_big_still_hands_back`, which passes. `test_clauses_match_h9` fails only on its `commands/do.md` and `commands/prep.md` subtests; its H9 subtests pass (Task 21).
   red when: a method other than the guard passes, the guard fails, or an H9 subtest fails (Task 21 is not in).
   at base: none — the module is written by this task (at `2f30a28` the file does not exist).
2. **Green.** The same command after the edits — expected: `Ran 6 tests`, `OK`.
   red when: any test fails.
   at base: none — written by this task.
3. **The tests bite at the definition site.** In `commands/do.md`, the file that defines the rule, delete `Push nothing and note nothing on the issue first: ` from the *Too big* bullet and rerun step 2's command — expected: `test_too_big_in_a_herd_continues_with_prep` fails. Restore it. Then move the *Started by `/jdi:herd`* sentence from the *Too big* bullet to the end of the **A product decision outside the request** bullet — expected: the same test fails (its fragments are cut to the *Too big* bullet). Restore. Then in `commands/prep.md` change `(untracked, started by /jdi:herd)` to `(untracked, by /jdi:herd)` — expected: `test_clauses_match_h9` and `test_prep_takes_the_herds_tracking_answer` fail. Restore.
   red when: any mutation leaves the module green.
   at base: none — the mutated text is written by this task.
4. **The clauses are where they belong, and only there.** `grep -c 'started by /jdi:herd)' commands/do.md commands/prep.md` — expected: each count at least `1` (the exact line counts depend on how you wrap: a line holding both clauses counts once). Then `grep -n 'started by /jdi:herd)' commands/do.md` — expected: every printed line number lies between the `1. **Identify the work**` line and the `6. **Build**` line (steps 1 to 5).
   red when: a count is `0`, or a hit in `commands/do.md` lies at or after step 6.
   control: `grep -c 'started by /jdi:herd)' reference/herdr.md` prints a positive count once Task 21 is in.
   at base: `commands/do.md:0`, `commands/prep.md:0`.
   compliant hits: none outside the four inserted sentences.
5. **The standing structure of both commands survives.** `python3 -m unittest discover -s tests -p 'test_structural_checks.py' -v` — expected: `Ran 20 tests`, `OK` (`DoPlanShapeTest` reads `commands/do.md` steps 1 and 4; `VerificationProbeTest`, `TestingStrategyFieldsTest`, `PremisesSlotTest`, `PremisePassTest` and `ClarificationOptionsTest` read numbered steps of `commands/prep.md`, which a stray numbered line would cut short).
   red when: any test fails.
   at base: `Ran 20 tests`, `OK`.
6. **Confined.** `python3 -m unittest discover -s tests -p 'test_delegation_transport.py' -k HerdrConfinementTest -v` — expected: `Ran 2 tests`, `OK`, with no subtest naming `commands/do.md` or `commands/prep.md`.
   red when: a failure names either file. (A failure naming `commands/herd.md`, `commands/help.md` or `commands/init.md` belongs to Task 23 or 24, running beside this one.)
   at base: `Ran 2 tests`, `OK`.
7. **Full suite.** `python3 -m unittest discover -s tests -v` — expected: every test passes except failures that belong to a sibling still running: `tests/test_herd.py` (Task 23), `tests/test_transport_docs.py` (Task 24), `tests/test_herdr_surfaces_doc.py` (Task 25), `tests/test_config_schema.py` (Task 20, if still running).
   red when: a failure in `tests/test_herd_handoff.py`, `tests/test_structural_checks.py`, `tests/test_frontmatter.py`, `tests/test_opencode_sync.py`, or any module no sibling owns.
   at base: `Ran 219 tests`, `OK`, no known reds; Wave 11 adds 14 (233).
