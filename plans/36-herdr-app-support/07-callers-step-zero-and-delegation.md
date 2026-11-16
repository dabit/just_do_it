status: done
# 07 — Callers: the step-0 line in nine commands, and `reference/delegation.md`, name either surface

Depends on: 03

## Why
The callers keep calling Herdr operations by name, so they must not learn which surface ran them. They do need to say that H1 now also settles the surface from `herdr.surface`, and that a Herdr role may run on either surface. The step-0 line, the block lists and the delegation ladder carry that. Rests on: D-struct, D1, P1, P7.

## Description
Planner's Task 6, minus its `commands/herd.md` part, which moved to Task 08. Splitting it lets this
part run alongside Task 06 instead of waiting for H9. The two parts share no file.

This task depends on Task 03 for two reasons: both edit `tests/test_delegation_transport.py`, and
Task 03 is where H1 learns the surface. It does not need Task 06's text. The rung wording below
cites behaviour Task 06 documents (H2's check on the app, the `error` state), but by operation
name only.

**Before starting, read `## Probe log` in PLAN.md.** An amendment there wins over this file.

**Confinement.** Every file this task edits is scanned by `HerdrConfinementTest`, which Task 03
widened. Write "the Herdr TUI" and "the Herdr app", never `herdr-app`, `hc`, `HC_*` or an app
command such as `pane.split`. **Do not touch `roles/butler.md`**: a test forbids it from naming
Herdr.

TDD is on: write the tests first and watch them fail.

### 1. Tests first
**In `tests/test_step_zero_transport.py`:**
- Append to `STEP_ZERO_FRAGMENTS`:
  ``"H1 also settles which Herdr this is, the TUI or the app, from `herdr.surface`"``.
- In `test_block_name_lists_include_delegation`, change the expected fragments to:
  - `commands/prep.md`: ``"`models`, `harnesses`, `delegation`, and `herdr` from it"``;
  - `commands/research.md`: ``"`models`, `harnesses`, `delegation`, and `herdr` from that config"``.

**In `tests/test_delegation_transport.py`:**
- Add to the fragment tuple in `TransportSelectionTest.test_transport_section_and_selection_rules_are_present`:
  "Herdr here is either surface, the Herdr TUI or the Herdr app" and "or `error` on the app".
- Leave `CONFINED_PATTERNS` and the confinement tests alone. Task 03 owns them.

### 2. Edits
- **All nine step-0 sites:** `commands/prep.md`, `research.md`, `plan.md`, `split.md`,
  `feedback.md`, `pr.md`, `execute.md`, `next.md` and `yolo.md`. In the "**Then resolve the
  delegation transport, once**" paragraph, right after "…no role re-probes.", add the sentence
  "H1 also settles which Herdr this is, the TUI or the app, from `herdr.surface`." Keep the wording
  identical at every site.
- **Block lists.** `commands/prep.md` becomes "`models`, `harnesses`, `delegation`, and `herdr` from
  it". `commands/research.md` becomes "… `delegation`, and `herdr` from that config".
- **`reference/delegation.md`:**
  - After the transport table in `## Choosing the transport`, add a sentence containing "Herdr here
    is either surface, the Herdr TUI or the Herdr app". It goes on: H1 settles which, from
    `herdr.surface`, and a pinned surface never falls to the other.
  - Rung 7 keeps its pinned TUI sentence, "Herdr's `kinds:` line lists the kinds it supports".
    Add: "On the app there is no kinds list; H2 checks only that the CLI resolves."
  - Rung 9 adds "(or `error` on the app)" after the states that never count as success. The
    fragment "or `error` on the app" must appear verbatim.
  - In `## Where a role runs`, env is set "…on the pane, or in the worker's command on the app, as
    H4 says".

## Files
- `tests/test_step_zero_transport.py`
- `tests/test_delegation_transport.py`
- `reference/delegation.md`
- `commands/prep.md`
- `commands/research.md`
- `commands/plan.md`
- `commands/split.md`
- `commands/feedback.md`
- `commands/pr.md`
- `commands/execute.md`
- `commands/next.md`
- `commands/yolo.md`

## Verification
1. **Red first.** Run `python3 -m unittest discover -s tests -p 'test_step_zero_transport.py' -v`
   and `python3 -m unittest discover -s tests -p 'test_delegation_transport.py' -v` before editing
   the docs. Expected failures:
   - `test_every_delegating_command_resolves_the_transport_at_step_zero`, once per command, nine
     subtests;
   - `test_block_name_lists_include_delegation`, two subtests;
   - `test_transport_section_and_selection_rules_are_present`, two new subtests.

   Everything else passes.
2. **Green.** Run both commands after the edits. Expected: every test passes, including
   `HerdrConfinementTest` over all eleven edited docs.
3. **The test bites.** Delete the new sentence from `commands/prep.md`, the file that defines prep's
   step 0, and run the step-zero module. Expected: one failing subtest, for `commands/prep.md` and
   the new fragment. Restore the sentence.
4. **Every site is identical.** Run
   `grep -c 'H1 also settles which Herdr this is, the TUI or the app, from `herdr.surface`' commands/{prep,research,plan,split,feedback,pr,execute,next,yolo}.md`.
   Expected: `:1` for each of the nine files.
5. **`roles/butler.md` untouched.** Run `git diff --quiet -- roles/butler.md`. Expected: exit status 0.
6. **Full suite.** Run `python3 -m unittest discover -s tests -v`. Expected: every test passes, with
   one exception: failures in a test module owned by a task running at the same time. Task 06 owns
   `tests/test_herdr_operations.py`, and Task 08 owns `tests/test_herd.py` if it has started.
