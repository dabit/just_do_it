status: done
# 04 — User docs: `/jdi:init`, `/jdi:help` and the README name the Herdr surface

Depends on: 01

## Why
Users have to learn that JDI now drives either Herdr surface, and where to pin one. That means `/jdi:init` offering `herdr.surface`, with `auto` recommended and `config.local.yml` suggested, and `/jdi:help` and the README describing it. None of these docs name an app binary or command. Rests on: D1, D-struct.

## Description
Planner's Task 7. This task documents the key that Task 01 adds. Treat Task 01's schema comment
(Appendix A1, now in `reference/config.md`) as the wording to echo. This task depends on Task 01
only so the key exists before the docs offer it; it shares no file with any other task.

**Confinement.** Task 03 widens `HerdrConfinementTest` to scan `commands/*.md` for `herdr-app`, `hc`,
`HC_*` and `space|tab|pane|agent.new|split|close|select|focus`, and the two tasks may run at the
same time. In `commands/init.md` and `commands/help.md`, write "the Herdr app" and "the Herdr TUI",
never a binary name or an app command. Keep the README free of app command names too (Planner,
Task 7); it is not scanned, but the rule holds.

TDD is on: write the tests first and watch them fail.

### 1. Tests first, in `tests/test_transport_docs.py`
- In the init `description` frontmatter: assert it contains both
  "how delegated roles reach their own process" and "which Herdr they use". The first is already
  pinned by `test_init_description_names_the_transport_question`; extend that test or add one.
- `commands/init.md` contains "offer `herdr.surface`".
- In help: the opening paragraph, `jdi_files.paragraph_starting_with(text, "Explain the Just Do It")`,
  contains "which Herdr surface".
- In help: `jdi_files.section(text, "### Separate agent processes")` names `` `herdr.surface` ``,
  and the `/jdi:init` row of the command table contains "Herdr surface". Find the row as the line
  that starts with `|` and contains `/jdi:init`.
- In the README: `jdi_files.section(text, "### Separate agent processes under Herdr")` contains
  "`herdr.surface`" and "the Herdr app".
- In the README: both init enumerations contain "which Herdr". These are the comment on the
  `/jdi:init` snippet (around `README.md:186`) and the prose below it (around `:193-202`). Assert
  that the line containing that comment, and the paragraph that enumerates init's questions, each
  contain the phrase. Locate them by a stable fragment you find in the file, not by line number.

### 2. Edits
- **`commands/init.md`:**
  - Extend the `description` with "and which Herdr they use".
  - Step 10, the transport question: change its skip condition to "H1 answers `none`".
  - Add a sub-bullet under step 10. It says which surface H1 found, and offers `herdr.surface` only
    to pin it. It recommends `auto`, and offers to write the value to `.jdi/config.local.yml`. Use
    the literal words "offer `herdr.surface`".
  - **Add no new numbered step.** This follows the `herd` precedent and deviates from
    `docs/config-key-lifecycle.md` §2's "new numbered step" on purpose. Say so in one sentence in
    your report, so the PR can record it.
- **`commands/help.md`** (three edits, per the lifecycle doc):
  - The closing-line instruction says "which Herdr surface is pinned, when not `auto`".
  - The `/jdi:init` row names the Herdr surface.
  - The `/jdi:herd` row says "inside Herdr, the TUI or the app".
  - Add a paragraph to `### Separate agent processes` naming `herdr.surface`: `auto`, `app` or
    `tui`; usually personal; on and off stays `delegation.transport`.
- **`README.md`:**
  - Both init enumerations say "which Herdr".
  - Add a paragraph to "Separate agent processes under Herdr" naming `herdr.surface` and
    "the Herdr app".
  - The `/jdi:herd` paragraph says "workspace or space".
  - In the "How it is put together" row for `reference/herdr.md`, say "on the Herdr TUI or the
    Herdr app". Keep the backticked `reference/herdr.md` in that row: `test_enumerations.py`
    reads it.

## Files
- `tests/test_transport_docs.py`
- `commands/init.md`
- `commands/help.md`
- `README.md`

## Verification
1. **Red first.** Run `python3 -m unittest discover -s tests -p 'test_transport_docs.py' -v` before
   editing the docs. Expected: the new assertions fail, and the five existing tests pass.
2. **Green.** Run the same command after the edits. Expected: every test passes.
3. **The tests bite.** Delete the "offer `herdr.surface`" sub-bullet from `commands/init.md`, the
   file that defines init's question, and run the module. Expected: the init test fails. Restore
   the sub-bullet. Then remove `` `herdr.surface` `` from the README's
   `### Separate agent processes under Herdr` paragraph. Expected: the README test fails. Restore it.
4. **No app names.** Run
   `grep -nE '\bherdr-app\b|\bhc\b|\bHC_[A-Z]|\b(space|tab|pane|agent)\.(new|split|close|select|focus)\b' commands/init.md commands/help.md README.md`.
   Expected: no output, exit status 1.
5. **Init's step references still resolve.** Run `grep -n 'step [0-9]' commands/init.md` and read each
   hit. Expected: every reference still points at the step it meant, because no step was added or
   renumbered.
6. **Full suite.** Run `python3 -m unittest discover -s tests -v`. Expected: every test passes, with
   one exception: failures in a test module owned by a task running at the same time,
   `tests/test_herdr_operations.py` or `tests/test_delegation_transport.py` (Task 03) and
   `tests/test_herdr_surfaces_doc.py` (Task 05). A `HerdrConfinementTest` failure on a line of
   `commands/init.md` or `commands/help.md` is this task's to fix.
