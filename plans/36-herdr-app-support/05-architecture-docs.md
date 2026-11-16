status: done
# 05 — Architecture docs: record the surfaces design as decided and probed

Depends on: 02

## Why
`docs/herdr-surfaces-architecture.md` was drafted as a proposal. It still has open decisions, a "nothing implemented" status, and a probe instruction that would run probes in the user's real window. This task records it as built: the decisions D1–D10 and P1–P11, the probe results from the probe gate, and probes that only ever run in a throwaway session. It also points the transport doc's detection section at it. Rests on: D1, D-wt, D-struct, D2, D3, D4, D5, D6, D7, D8, D9, D10, P1–P11.

## Description
Planner's Task 8. **Read PLAN.md's `## Probe log` first.** This task records its results and every
amendment it made. Where the gate amended a decision, record the amended decision, not the
original. This task only edits documentation. It shares no file with any other task and does not
cite `reference/herdr.md` text that Tasks 03, 06 and 08 are still writing. Refer to operations by
name (H1–H9), not by quoting their final wording.

TDD is on: write the new test module first and watch it fail.

### 1. Tests first: new file `tests/test_herdr_surfaces_doc.py`
Use the style of the other modules: `import jdi_files`, `unittest`, `longMessage = False`, a module
docstring that says what it guards, and `if __name__ == "__main__": unittest.main()`.

Assertions on `docs/herdr-surfaces-architecture.md` (`jdi_files.read`):
- These headings are present, each as an exact line: `## Detection`, `## Operation map`,
  `## The app's worktree layout`, `## Decisions`, `## App-side live probes`.
- These are absent: the heading `## Open decisions`, and the phrases
  "Nothing here is implemented yet" and "in an app terminal of the user's normal window".
- `jdi_files.section(text, "## App-side live probes")` contains "throwaway".
- The file contains no `/home/`.

Assertion on `docs/delegation-transport-architecture.md`:
- `jdi_files.section(text, "## Capability detection")` contains
  "`docs/herdr-surfaces-architecture.md`" and "`herdr.surface`".

### 2. Edits

**`docs/herdr-surfaces-architecture.md`:**
- **`## Status`.** Say it is implemented in 1.0.11, stacked on `herdr-role-delegation`. Remove
  "Nothing here is implemented yet" and the sentences about open decisions and pending probes.
- **`## Open decisions` becomes `## Decisions`.** Record each decision with its id and one or two
  sentences, as PLAN.md's `### Decisions` states it (amended where the probe log says so):
  - user decisions: D1, D-wt, D-struct;
  - the Butler's defaults: D2–D10;
  - the Planner's decisions: P1–P11.
  The current items 1–10 map onto D1 (with D-wt), D2, D3, D4, D5, D6, D7, D8, D9 and D10.
- **`## Operation map`.** Fill every cell that still says "open decision" with what was decided.
- **The `errors`/`error` fact.** `herdr-app status` returns an `errors` list on success and
  `{"error": …}` on failure. The window check passes when there is no top-level `error` (P6).
  Record it where the doc discusses the window check (`### The checks`, step 5).
- **`## App-side live probes`.**
  - Replace the opening "in an app terminal of the user's normal window" with this: probes run
    only in a **throwaway** session and app home, through the isolation guard (P11). Summarise
    the guard: refuse without probe variables, `unset` the inherited `HC_*`/`HERDR_*` terminal
    variables, export the throwaway `HC_SESSION`/`HERDR_APP_HOME`, then `exec`.
  - Add A13–A17 (focus, split folder, core env, IDs and labels, argument forms) as PLAN.md's
    Appendix B defines them.
  - Add a short summary of the results from the probe log, with versions. Sanitise it: no
    absolute home paths, no session names.
- Leave `## Detection`, `## The app's worktree layout` and the other sections in place. Edit them
  only where a decision or probe result changes what they say.

**`docs/delegation-transport-architecture.md`:**
- **`## Capability detection`.** Make it surface-neutral. H1 now also picks the surface, from
  `herdr.surface`. Point to `docs/herdr-surfaces-architecture.md` for each surface's checks. Keep
  the "detect, never repair" and "never from the harness name" content.
- **Configuration**, the `harnesses.<kind>.env` bullet: env is set "on the pane, or in the worker's
  argv on the app".

## Files
- `tests/test_herdr_surfaces_doc.py` (new)
- `docs/herdr-surfaces-architecture.md`
- `docs/delegation-transport-architecture.md`

## Verification
1. **Red first.** Run `python3 -m unittest discover -s tests -p 'test_herdr_surfaces_doc.py' -v`
   before editing the docs. Expected: these fail:
   - the `## Decisions` heading test;
   - the three absence tests (`## Open decisions`, "Nothing here is implemented yet", "in an app
     terminal of the user's normal window");
   - the "throwaway" test;
   - the transport-doc test.
   The present-heading tests for `## Detection`, `## Operation map`,
   `## The app's worktree layout` and `## App-side live probes` pass already, and so does the
   no-`/home/` test.
2. **Green.** Run the same command after the edits. Expected: every test passes.
3. **The tests bite.** Put the line `## Open decisions` back into `docs/herdr-surfaces-architecture.md`,
   the file under test, and run the module. Expected: the absence test fails. Remove the line. Then
   add a literal `/home/` path to the probe summary. Expected: the no-`/home/` test fails. Remove it.
4. **No stale "open decision" cells.** Run
   `grep -nci 'open decision' docs/herdr-surfaces-architecture.md`. Expected: `0`.
5. **Full suite.** Run `python3 -m unittest discover -s tests -v`. Expected: every test passes, with
   one exception: failures in a test module owned by a task running at the same time
   (`tests/test_herdr_operations.py` and `tests/test_delegation_transport.py` for Task 03,
   `tests/test_transport_docs.py` for Task 04). Any failure in `tests/test_herdr_surfaces_doc.py`
   is this task's.
