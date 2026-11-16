status: done
# 13 — `reference/herdr.md`: `### The herd record`

Depends on: None

## Why
`/jdi:herd --cleanup` must find herd worktrees from a record and never from folder names, so H9 has to write one: `<git-common-dir>/jdi/herds/<herd-id>.json`, one file per herd, the same shape on both surfaces, created at the first successful worktree, written whole and moved over with `mv -f`, never committed, `state` `creating` until step 10 and `handed_off` after, and a failed write costs one sentence while the herd continues. Every later #37 task (the cleanup rules, the command, the docs) points at this section. Rests on: C1, C9, C10.

## Description
Planner's Task 13. Add `### The herd record` to `reference/herdr.md`, inside `## H9 - Give a Butler
its own worktree`, directly after `### H9 on the app` (today the last section of the file), and
guard it with a new test file. This task does not depend on Task 12: the record's shape and write
points are not gated by any probe.

**Rules for `reference/herdr.md`:**
- No em dash (`test_no_em_dash`).
- No `/home/`, `/Users/`, `jdiprobe`, `HC_SESSION=` or `HERDR_APP_HOME=` (`test_no_personal_values`).
  Placeholders only (`<git-common-dir>`, `<herd-id>`, `<path>`).
- **Additions only.** Every existing line stays byte-identical. The two pointer sentences go on new
  lines of their own (a new line inside a paragraph, or a new paragraph), so no existing line is
  re-wrapped.
- The JSON fence starts at column 0 (```` ```json ```` alone on its line, closed by ```` ``` ````).
  `jdi_files.section` toggles its fence tracking on any line starting with three backticks, and no
  line inside the fence starts with `#`.

TDD is on: write the tests first and watch them fail.

### 1. Tests first: new `tests/test_herd_record.py`
Module docstring: what the herd record is for (#37: cleanup reads a record, never folder names) and
that the rules live in `reference/herdr.md`. Import `json`, `unittest`, `jdi_files`. Constants
`HERDR_REFERENCE = "reference/herdr.md"`, `H9_HEADING = "## H9 - Give a Butler its own worktree"`,
`H9_APP_HEADING = "### H9 on the app"`, `RECORD_HEADING = "### The herd record"`, and a
`normalized(text)` helper (`" ".join(text.split())`).

Class `HerdRecordTest(unittest.TestCase)`, modelled on `HerdCommandTest` in `tests/test_herd.py`
(the class's opening helpers: `longMessage = False`, a `*_lines()` helper over `jdi_files.section`,
a normalized-text helper, and an `assert...Contains(*fragments)` helper that runs one `subTest` per
fragment). That template covers every case below; the shape test additionally needs the raw lines,
which `jdi_files.section` already returns.

- `test_record_shape_matches_appendix_c`: take the raw lines of
  `jdi_files.section(text, "### The herd record")`; slice from the line **equal to** ```` ```json ````
  (exclusive) to the next line **starting with** ```` ``` ````; `json.loads` the joined slice; assert
  **exact** key sets with `assertEqual(set(...), {...})`:
  - top level `{schema, herd_id, created, surface, state, issues}`;
  - `issues[0]`: `{n, issue, name, worktree, scratch_branch, base_commit, seeded, created, herdr}`;
  - `issues[0]["herdr"]`: `{workspace_id, space_id, tab_id, pane_id, terminal_id, agent_name}`.
- `test_record_heading_is_inside_h9`: in the file's lines, `### The herd record` comes after
  `## H9 - Give a Butler its own worktree` and after `### H9 on the app`, and it is one of the lines
  `jdi_files.section(text, H9_HEADING)` returns (no `## ` heading intervenes).
- `test_record_location_and_lifecycle`, on the normalized section text:
  `git rev-parse --path-format=absolute --git-common-dir`,
  `<git-common-dir>/jdi/herds/<herd-id>.json`, `never committed`, `one file per herd`, `mv -f`,
  `never edited in place`, `names no session and no app home`.
- `test_record_write_points`, on the normalized section text: `step 6`, `step 7`, `step 8`,
  `step 10`, `` `creating` ``, `` `handed_off` ``, `git worktree list --porcelain`,
  `refs/heads/<scratch branch>`, `git -C <path> rev-parse HEAD`, `the herd continues`.
- `test_create_steps_point_at_the_record`: the lines of the `## H9` section **before**
  `### H9 on the app` contain `*The herd record*`, and so does
  `jdi_files.section(text, "### H9 on the app")`.

### 2. `reference/herdr.md`: append `### The herd record` after `### H9 on the app`
Write, in this order:

- **What and where (C1).** H9 writes one file per herd at
  `<git-common-dir>/jdi/herds/<herd-id>.json`, where `<git-common-dir>` is
  `git rev-parse --path-format=absolute --git-common-dir`, so every worktree of the repository sees
  the same record. It lives inside git's own directory, so it is never committed. The shape is
  identical on both surfaces; a key that does not apply to the surface is `null`.
- **The shape: Appendix C verbatim** (below), as a ```` ```json ```` fence at column 0.
- **Write rules (C1).** Created on the first successful worktree, never before. Written whole to
  `<dir>/.<herd-id>.json.tmp`, then `mv -f` over the record; never edited in place. The record
  names no session and no app home (the surfaces' rule *Inherit, never set*): which surface is
  reachable is observed at cleanup, never recorded. `worktree` is stored exactly as
  `git worktree list --porcelain` prints it, taken from the entry whose `branch` is
  `refs/heads/<scratch branch>`. `base_commit` is `git -C <path> rev-parse HEAD`, run right after
  the worktree is created.
- **Write points.**
  - **Step 6**, after each successful create: append the entry. On the TUI it fills
    `workspace_id`, `tab_id`, `pane_id` and `agent_name` (from the create result, or from the
    `herdr tab create` result when the environment forced a new tab).
  - **Step 7**: `seeded: true` when a seed step wrote into the worktree.
  - **Step 8**, app only: `space_id`, `tab_id`, `pane_id`, `terminal_id` and `agent_name`, from
    `space.new`'s output and `herdr-app ls`.
  - **Step 10**: `state` becomes `handed_off`.
- **State (C9).** `state` is `creating` from the first write until step 10, and `handed_off` after.
  Say what that is for: a cleanup without a herd ID skips a `creating` record, because its herd may
  still be running; given that herd's ID it includes the record and flags it.
- **A failed write (C10).** A record that cannot be written gets one sentence in the run, and the
  herd continues; step 11's manual commands still cover that herd.

**Pointer sentences.** One sentence pointing at *The herd record* (written exactly so, in
italics, as `*The herd record*`) under the shared `**Create it.**` (the TUI part of `## H9`, before
`### H9 on the app`), and one under the app's `**Create it**` in `### H9 on the app`. Each says that
after a successful create, H9 records the worktree as *The herd record* says.

### Appendix C — herd record shape (verbatim; must stay valid JSON)
Copy these lines byte for byte between the fences. The key names and nesting are exact; the string
values are placeholders and stay as written; `"schema": 1`, `"n": 1` and `"seeded": false` are
literal.

```json
{
  "schema": 1,
  "herd_id": "<yyyymmddThhmmss>",
  "created": "<UTC yyyy-mm-ddThh:mm:ssZ>",
  "surface": "<tui | app>",
  "state": "<creating | handed_off>",
  "issues": [
    {
      "n": 1,
      "issue": "<ISSUE-ID>",
      "name": "<slug>-<suffix>",
      "worktree": "<path as git worktree list --porcelain prints it>",
      "scratch_branch": "jdi-herd-scratch-<herd-id>-<N>",
      "base_commit": "<full SHA of the worktree's HEAD right after creation>",
      "seeded": false,
      "created": "<UTC yyyy-mm-ddThh:mm:ssZ>",
      "herdr": {
        "workspace_id": "<TUI workspace, else null>",
        "space_id": "<app space, else null>",
        "tab_id": "<tab the agent runs in>",
        "pane_id": "<the agent's pane>",
        "terminal_id": "<app terminal, else null>",
        "agent_name": "<name>"
      }
    }
  ]
}
```

## Files
- `tests/test_herd_record.py` (new)
- `reference/herdr.md`

## Verification
Run from the repository root.

1. **Red first.** After writing the tests and before editing `reference/herdr.md`: `python3 -m unittest discover -s tests -p 'test_herd_record.py' -v` — expected: `Ran 5 tests`, `FAILED`; the four section tests fail or error with `heading '### The herd record' not found` (or its absence from the line list), and `test_create_steps_point_at_the_record` fails on the missing `*The herd record*`.
   red when: any of the five passes before the edit (it tests nothing new).
   at base: `Ran 0 tests`, `NO TESTS RAN` (the file does not exist).
2. **Green.** The same command after the edit — expected: `Ran 5 tests`, `OK`.
   red when: any test fails.
   at base: none — written by this task.
3. **The tests bite.** In `reference/herdr.md`, `### The herd record`, the fence that defines the shape: rename the key `scratch_branch` to `branch`, and run the module — expected: `test_record_shape_matches_appendix_c` fails. Restore it. Then, in the same section's location sentence, replace `--git-common-dir` with `--absolute-git-dir` — expected: `test_record_location_and_lifecycle` fails. Restore it and rerun step 2.
   red when: either mutation leaves the suite green (the test reads the wrong text).
4. **Heading placed once, after the app section.** `grep -nE '^### (H9 on the app|The herd record)$' reference/herdr.md` — expected: two lines, `### H9 on the app` first, `### The herd record` second.
   red when: one line (the section is missing) or the record heading comes first.
   at base: one line, `868:### H9 on the app`.
5. **Additions only.** `git diff cdd14046784af5ef7e58fe612067f17a2e5b60df -- reference/herdr.md | grep -E '^-[^-]'` — expected: no output.
   red when: an existing line was removed or re-wrapped (a pinned H9 fragment may have moved or gone).
   control: `git diff b06fbdbfc5ffa48fc2dff3633497e401b5254c19 -- reference/herdr.md | grep -cE '^-[^-]'` prints `18`, so the pattern does catch removed lines.
   at base: no output.
6. **The reference's guards hold.** `python3 -m unittest discover -s tests -p 'test_herdr_operations.py' -v` — expected: `Ran 39 tests`, `OK`, including `test_no_em_dash` and `test_no_personal_values`.
   red when: an em dash or a personal value was written into the new section.
   at base: `Ran 39 tests`, `OK`.
7. **H9's existing tests still pass.** `python3 -m unittest discover -s tests -p 'test_herd.py' -v` — expected: `Ran 17 tests`, `OK`, including `test_h9_app_cleanup_order` (whose section now ends at `### The herd record`) and `test_h9_drops_the_collision_prone_scratch_branch`.
   red when: a pointer sentence disturbs a pinned H9 fragment or its order.
   at base: `Ran 17 tests`, `OK`.
8. **Full suite.** `python3 -m unittest discover -s tests -v` — expected: `Ran 200 tests`, `OK`.
   red when: any test fails or the count is not 195 + 5.
   at base: `Ran 195 tests`, `OK`, no known reds.
