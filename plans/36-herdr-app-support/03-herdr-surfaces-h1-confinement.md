status: done
# 03 — `reference/herdr.md`: the two surfaces, H1 on each, and app-name confinement

Depends on: 02

## Why
H1–H9 become one set of operations, each with a TUI variant and an app variant. This task lays that structure down in `reference/herdr.md`. It adds the surface choice (`auto` picks the innermost surface, an inconclusive check means the TUI, a pinned surface never falls to the other) and the rule that the session is inherited, never set. It also extends the confinement test so the app's binaries and variables can appear only in that file. The TUI checks themselves are unchanged. Rests on: D-struct, D1, D2, P4, P6, P7, D9.

## Description
Planner's Task 3. **Before starting, read `## Probe log` in PLAN.md.** Where the probe gate (Task 02)
amended D2, D9, P4 or P6, the amended text wins over this file. Say so in your report.

TDD is on: write the tests first and watch them fail. Use
`python3 -m unittest discover -s tests -p '<file>.py' -v`; the `tests.<module>` form fails with
`ModuleNotFoundError`.

### 1. Tests first

In **`tests/test_herdr_operations.py`**:
- Add to `HEADINGS`: `## Surfaces`, `### Choosing the surface`, `### H1 on the TUI`,
  `### H1 on the app`.
- `test_surfaces_section`: `self.assertSectionContains("## Surfaces", …)` with
  "`herdr.surface`", "Inherit, never set", "`HC_SESSION`", "`HERDR_APP_HOME`",
  "Never run bare `herdr-app` or bare `hc`", "`hc server`", "seconds".
- `test_choosing_the_surface`: in `### Choosing the surface`: "innermost surface wins",
  "`foreground`", "says so once and uses the TUI", "never falls to the other surface".
- `test_h1_app_checks_in_order`: in `self.section_text("### H1 on the app")`, the following appear
  with strictly increasing `index`: `HC_TERMINAL_ID`, `command -v hc`,
  `test -S "$HC_TERMINAL_SOCKET"`, `hc get "$HC_TERMINAL_ID" --json`, `herdr.space`,
  `herdr-app status`. The section also contains "before any `hc` command".
- `test_no_personal_values`: `self.text` contains none of `/home/`, `/Users/`, `jdiprobe`,
  `HC_SESSION=`, `HERDR_APP_HOME=`. A `${HERDR_APP_HOME:-…}` default, which Task 08 writes, does not
  contain `HERDR_APP_HOME=`.
- `test_failure_patterns_name_the_surface`: `## When a step fails` contains "Herdr (<surface>)".

In **`tests/test_delegation_transport.py`**:
- Add to `CONFINED_PATTERNS`: `re.compile(r"\bherdr-app\b")`, `re.compile(r"\bhc\b")`,
  `re.compile(r"\bHC_[A-Z]")` and
  `re.compile(r"\b(space|tab|pane|agent)\.(new|split|close|select|focus)\b")`. Keep the three
  existing patterns. `HERDR_APP_HOME` is already caught by `HERDR_`.
- Add `test_confined_patterns_catch_every_app_name`, a method on `HerdrConfinementTest` or a class
  of its own.
  - Each **forbidden** sample matches at least one pattern: `hc send t3 hi`,
    `herdr-app do pane.split`, `HC_TERMINAL_ID`, `HERDR_APP_HOME`, `pane.split --pane p1`,
    `herdr agent start`.
  - Each **allowed** sample matches none: `the Herdr app`, `` `herdr.surface: app` ``,
    `Herdr TUI`, `` `delegation.transport: herdr` ``.
  - Use `subTest` per sample.

Run both modules and confirm the new methods fail. The widened `HerdrConfinementTest` should already
pass: today no confined file names these. Check with the grep in Verification 4.

### 2. `reference/herdr.md`

Write no em dash anywhere in this file (`test_no_em_dash`). Inside an indented fence, no line may
start with `#` at column 0: `jdi_files.section` only tracks fences at column 0.

- **Intro.** Add the sentence "`herdr-app` and `hc` are the Herdr app's CLIs, used only by the app
  variants."
- **New `## Surfaces`**, placed right after `## Scope`. It covers:
  - what each surface is;
  - that `herdr.surface` picks one;
  - **"Inherit, never set"**: never set, export or write `HC_SESSION`, `HC_SOCKET` or
    `HERDR_APP_HOME` in a command, manifest, config or prose;
  - "Never run bare `herdr-app` or bare `hc`", and never `hc server`;
  - that hc timeouts are in **seconds**;
  - that target IDs are strings;
  - that app variants assume POSIX `sh`;
  - that each operation has a TUI subsection and an app subsection, and shared text applies to both.
- **H1.**
  - Keep the shared intro, including every phrase the existing tests pin: `HERDR_ENV`,
    `HERDR_BIN_PATH`, `` `herdr status` ``, `` `compatible: yes` ``, "never from the harness
    name", "Detect, never repair", "Under `native`, or with no `delegation` key, H1 does not
    run", "no Herdr command runs at step 0", "summaries included".
  - Add **`### Choosing the surface`**:
    - the detection matrix;
    - the nested rule: the innermost surface wins, decided from `hc get`'s `foreground`;
    - P4: if app check (b) or (c) fails, because the binary or socket is missing, the app is
      unreachable, so use `tui` with no note. "Inconclusive" means only that `hc get` failed or
      had no `foreground`; then the Butler "says so once and uses the TUI";
    - P7: a pinned `app` or `tui` "never falls to the other surface". An invalid value is
      announced once, and only when H1 runs, then treated as `auto`.
  - Put the existing checks (a)–(c), unchanged, under **`### H1 on the TUI`**.
  - Add **`### H1 on the app`** with checks (a)–(e), in this order, as the architecture doc's
    `### The checks` gives them:
    - (a) `HC_TERMINAL_ID` is set;
    - (b) `command -v hc` resolves;
    - (c) `test -S "$HC_TERMINAL_SOCKET"`, which runs **before any `hc` command**;
    - (d) `hc get "$HC_TERMINAL_ID" --json` returns JSON whose labels include `herdr.space`. This
      guards against a foreign `hc` on PATH (R7);
    - (e) `herdr-app status` exits 0 and its stdout parses as JSON with no top-level `error` key.
      Its `errors` list is recorded, not treated as a failure. With no window it exits 2 with plain
      text on stderr (P6 as refined by A11, D9). Also record the version.
  - Under `auto`, the announcement is silent when the chosen surface's first check fails or the
    answer is `none`.
  - H1's answers are `tui`, `app` or `none`.
- **`## When a step fails`.**
  - Change the step-0 pattern to "`… but Herdr (<surface>) is not usable here: …`".
  - Add an invalid-`herdr.surface` pattern: one line, announced once, then `auto`.
- **Universal rules.** Keep every pinned phrase.
  - Rule 4 keeps "`agent read` is for inspection only" and adds "and so is `hc read` on the app".
  - Rule 5 keeps "`idle` or `done` is not proof of success" and "never counts as success",
    contiguous, and adds `error` on the app. For example: "… and `unknown` or `timeout` (or
    `error` on the app) never counts as success."
  - Rule 7 adds: never `hc keys`, `hc send --force` or `hc interrupt`.

H2–H9 are untouched in this task. Tasks 06 and 08 add their app variants.

## Files
- `tests/test_herdr_operations.py`
- `tests/test_delegation_transport.py`
- `reference/herdr.md`

## Verification
1. **Red first.** Run `python3 -m unittest discover -s tests -p 'test_herdr_operations.py' -v` and
   `python3 -m unittest discover -s tests -p 'test_delegation_transport.py' -v` before editing
   `reference/herdr.md`. Expected: the new heading subtests and the five new
   `test_herdr_operations` methods fail. `test_no_personal_values` may already pass, and that is
   fine: it is a guard. `test_confined_patterns_catch_every_app_name` fails until the patterns are
   added and passes once they are. Every pre-existing test passes.
2. **Green.** After the edits, run both commands again. Expected: every test passes. That includes
   the untouched `test_h1_detect`, `test_h1_native_runs_no_herdr_command`, `test_universal_rules`,
   `test_result_channel_rules` and `test_no_em_dash`.
3. **The confinement bites.**
   - Append the line `hc send t3 hi` to `commands/herd.md`, a confined file that defines the herd's
     steps, and run the `test_delegation_transport.py` module. Expected: `HerdrConfinementTest`
     fails at that line, naming the `\bhc\b` pattern. Remove the line, then run
     `git diff --quiet -- commands/herd.md`: expected exit status 0.
   - Remove `re.compile(r"\bhc\b")` from `CONFINED_PATTERNS` in `tests/test_delegation_transport.py`,
     the file that defines the confinement. Expected: `test_confined_patterns_catch_every_app_name`
     fails for `hc send t3 hi`. Restore the pattern.
4. **Nothing outside the reference names the app.** Run
   `grep -rnE '\bherdr-app\b|\bhc\b|\bHC_[A-Z]|\b(space|tab|pane|agent)\.(new|split|close|select|focus)\b' commands agents roles reference skills/run/SKILL.md | grep -v '^reference/herdr.md:'`.
   Expected: no output.
5. **Full suite.** Run `python3 -m unittest discover -s tests -v`. Expected: every test passes, with
   two possible exceptions:
   - a failure in a test module owned by a task running at the same time. For Task 04 that is
     `tests/test_transport_docs.py`; for Task 05 it is `tests/test_herdr_surfaces_doc.py`;
   - a `HerdrConfinementTest` failure on a line of a file in a concurrent task's `## Files`, for
     example `commands/init.md`, `commands/help.md` or `reference/config.md`. Report it to the
     Butler as that task's defect.

   A failure in `test_herdr_operations.py` or `test_delegation_transport.py` that is not of that
   kind belongs to this task.
