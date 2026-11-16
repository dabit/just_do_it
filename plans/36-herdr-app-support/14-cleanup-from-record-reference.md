status: pending
# 14 — `reference/herdr.md`: `### Cleanup from the herd record`

Depends on: 12, 13

## Why
`/jdi:herd --cleanup [<herd-id>]` needs one place that defines, for both surfaces, how a herd is cleaned from its record: a checked herd ID, records chosen without guessing from folder names, every space or workspace re-found by worktree path, busy agents and the session's own location skipped, the plan-file guard and one question, close then remove (app: space first), `--force` only for seeded worktrees, only a commit-less scratch branch deleted, the record kept up to date, and a per-issue report. Those rules live only here, so the command calls them by name. Depends on 12 for the probed TUI removal and app state commands, and on 13 for the record and because both edit `reference/herdr.md` and `tests/test_herd_record.py`. Rests on: C2, C3, C4, C5, C6, C7, C9, C11.

## Description
Planner's Task 14. Append `### Cleanup from the herd record` to `reference/herdr.md`, directly after
`### The herd record` (Task 13), still inside `## H9`, and guard it with a second class in
`tests/test_herd_record.py`.

**Before starting, read `## Probe log (#37)` in PLAN.md (Task 12).** Its gate line and any `G<n>`
amendment win over this file's text, fragments included. In particular:
- **TUI removal.** Unamended, the TUI removes with `herdr worktree remove --workspace <workspace_id>`
  (plus `--force` per the force rule), which closes the workspace and removes the worktree. If the
  gate found that it deletes a branch, the TUI removal is `herdr workspace close <workspace_id>`
  then `git -C <main checkout> worktree remove [--force] <path>`.
- **App busy check.** Unamended, read each terminal's state from
  `hc ls --json --label herdr.space=<space>`. If the gate found no state there, list the terminals
  with that command and read each one's state with `hc get <terminal> --json`; add that fragment
  to `test_resolves_by_worktree_path`.
- **TUI fields.** If R1's fields or `agent_status` differ, use the observed names in the text and in
  `test_resolves_by_worktree_path`, and say in that test's docstring which gate amendment changed
  it.
- If the gate found the TUI needs `--trust-repository`, write that the TUI is then not reachable
  from here (never pass the flag).

**Rules for `reference/herdr.md`:** no em dash; no `/home/`, `/Users/`, `jdiprobe`, `HC_SESSION=`
or `HERDR_APP_HOME=`; placeholders only. **Every pinned H9 fragment stays**: the existing H9 text,
`### H9 on the app` and `### The herd record` are changed only by the two pointer sentences below,
each on a new line of its own so no existing line is re-wrapped.

TDD is on: write the tests first and watch them fail.

### 1. Tests first: class `HerdCleanupFromRecordTest` in `tests/test_herd_record.py`
Same helpers as `HerdRecordTest` (Task 13), over
`jdi_files.section(text, "### Cleanup from the herd record")`, normalized. Fragments, each in a
`subTest`:

- `test_selects_records_safely`: `` `^[0-9]{8}T[0-9]{6}$` ``, `never builds a path from`,
  `` `creating` ``, `Never guess from folder names`, `git worktree list`.
- `test_resolves_by_worktree_path` (per Task 12's gate): `never by a recorded ID alone`,
  `herdr-app ls`, `hc ls --json --label herdr.space=<space>`,
  `herdr worktree list --cwd <main checkout>`, `open_workspace_id`,
  `herdr workspace get <workspace_id>`.
- `test_skips`: `` `working` or `blocked` ``, `not reachable from here`, `agent state unknown`,
  `the session running the cleanup`, `prunable`, `git worktree prune`.
- `test_guards_and_force`: `git -C <worktree> status --porcelain -- <plans.path>`,
  `git -C <worktree> status --porcelain`, `the whole tree`,
  `` `--force` only when the entry's `seeded` is true ``, `uncommitted changes`, `one list`,
  `asks once`, `its own yes`.
  (*Splitter's addition:* `the whole tree`. The Planner's `git -C <worktree> status --porcelain` is
  a prefix of the plan-file command and passes on that alone; `the whole tree` is what proves the
  whole-tree check is written.)
- `test_scratch_branch_rule`: `jdi-herd-scratch-<herd-id>-<N>`,
  `git show-ref --verify --quiet refs/heads/<scratch branch>`,
  `git rev-list --count <base_commit>..refs/heads/<scratch branch>`,
  `git branch -D <scratch branch>`, `Never delete any other branch`.
- `test_record_upkeep`: `removes the entry`, `deletes the record file`.
- `test_removal_order`. Precedent: `test_h9_app_cleanup_order` in `tests/test_herd.py` (collect
  each fragment's `index`, assert the positions are sorted and distinct). **Deviation from that
  precedent:** search only the normalized text **after** the marker
  `**The removal, per entry, in this order:**` (assert the marker is present, then slice after it),
  because the earlier per-entry checks name some of the same commands. Strictly increasing:
  1. `git -C <worktree> status --porcelain -- <plans.path>`
  2. `herdr-app do space.close --id <space> --confirmed true`
  3. `git -C <main checkout> worktree remove`
  4. `git branch -D <scratch branch>`
  5. `removes the entry`

### 2. `reference/herdr.md`: append `### Cleanup from the herd record`
Write it with C2–C7, C9 and C11, in this order. The text is the single definition: the command
calls it by name and restates none of it.

- **Choosing the records (C2, C6, C9).**
  - A herd ID must match `` `^[0-9]{8}T[0-9]{6}$` `` or the run refuses: JDI never builds a path
    from an unchecked argument.
  - With an ID, the record is `<git-common-dir>/jdi/herds/<herd-id>.json`; a `creating` record is
    included but flagged. Without one, every record in `<git-common-dir>/jdi/herds/`; a `creating`
    record is skipped with "its herd may still be running; pass its herd ID to clean it anyway".
  - No record, or an unknown herd ID: say so, clean nothing, and point at `git worktree list` and
    step 11's manual commands. Never guess from folder names.
- **Which surface is reachable (C3).** H1's answer, compared with each record's `surface`. A record
  whose surface is not reachable from here (another surface, or none) skips the space/workspace
  close and is still offered the worktree removal, marked "agent state unknown"; its removal is the
  git removal alone. Cleanup never stops on H1's answer.
- **Per entry, before anything is listed (C3, C5):**
  - **Find by path, never by a recorded ID alone** (app terminal IDs and TUI workspace IDs are
    reused). App: the `herdr-app ls` space whose `folder` is the entry's `worktree` or inside it.
    TUI: the `herdr worktree list --cwd <main checkout>` entry whose `path` equals the record's
    `worktree`, and its `open_workspace_id` (`null` means no open workspace).
  - **Gone or prunable (C5).** An entry whose worktree is no longer in
    `git worktree list --porcelain`: nothing to remove; the record removes the entry. A listed but
    missing (`prunable`) worktree keeps its entry, and the user is told to run `git worktree prune`.
  - **Own location.** Skip an entry whose worktree contains the session running the cleanup, or
    whose space/workspace is the Butler's own.
  - **Busy.** Checked across the whole space or workspace: app, every terminal in
    `hc ls --json --label herdr.space=<space>`; TUI, the workspace's `agent_status` from
    `herdr workspace get <workspace_id>`. An agent that is `working` or `blocked` skips the entry. A
    reattached session counts as busy. A blocked-at-startup agent (a dialog open) is skipped with a
    reason telling the user to answer it or close the space (R18).
  - **Plan-file guard.** `git -C <worktree> status --porcelain -- <plans.path>`. Entries with
    uncommitted plan files leave the batch and get their own yes, with the plan commit offered.
  - **The whole tree.** `git -C <worktree> status --porcelain` on the whole tree. Anything shown and
    the entry is seeded: list the files; the removal uses `--force`. Not seeded: skip with
    "uncommitted changes". `--force` only when the entry's `seeded` is true.
- **One list, one question (C3).** Show one list of everything that will be closed and removed, per
  entry, and ask once. Plan-file entries are asked separately, each its own yes.
- **The numbered removal**, introduced by the exact line `**The removal, per entry, in this
  order:**` (keep it on one line in the file):
  1. Re-check the plan files: `git -C <worktree> status --porcelain -- <plans.path>`; any output
     stops this entry.
  2. Close: app, `herdr-app do space.close --id <space> --confirmed true`; TUI, the command the
     Task 12 gate settled. Skipped when the surface is not reachable or nothing is open.
  3. Remove the worktree: `git -C <main checkout> worktree remove [--force] <path>` (on the TUI, the
     gated TUI removal where it both closes and removes, else this).
  4. The scratch branch (C4): only if its name is `jdi-herd-scratch-<herd-id>-<N>` for this record's
     `herd_id`; it still exists (`git show-ref --verify --quiet refs/heads/<scratch branch>`);
     `git rev-list --count <base_commit>..refs/heads/<scratch branch>` is `0`; and its worktree is
     gone. Then `git branch -D <scratch branch>`. Never delete any other branch. Say why: `/jdi:prep`
     leaves the scratch branch behind at its base and works on a branch of its own.
  5. Update the record: removes the entry once its worktree is no longer in
     `git worktree list --porcelain`; deletes the record file when the last entry goes. Written as
     *The herd record* says (whole, then `mv -f`).
- **The report (C7).** Per issue: removed, or skipped with its reason; and the record's state
  afterwards (entries left, or deleted).

**Pointer sentences.** One sentence, on a new line, at the end of the TUI `**Cleanup.**` paragraph,
and one after the numbered list under the app's `**Cleanup (remove)**`: a whole herd is cleaned from
its record with `/jdi:herd --cleanup`, as *Cleanup from the herd record* says. The app's sentence
goes **after** its numbered list and names none of the list's commands, so
`test_h9_app_cleanup_order` (which takes each command's first occurrence) is unchanged.

## Files
- `tests/test_herd_record.py`
- `reference/herdr.md`

## Verification
Run from the repository root.

1. **Red first.** After writing the tests and before editing the reference: `python3 -m unittest discover -s tests -p 'test_herd_record.py' -v` — expected: `Ran 12 tests`, `FAILED`; the seven new methods error with `heading '### Cleanup from the herd record' not found`, and Task 13's five pass.
   red when: a new method passes before the edit, or one of Task 13's five fails.
   at base: none — `Ran 5 tests`, `OK` once Task 13 is done (the file is Task 13's).
2. **Green.** The same command after the edit — expected: `Ran 12 tests`, `OK`.
   red when: any test fails.
   at base: none — written by this task.
3. **The tests bite.** In `reference/herdr.md`, `### Cleanup from the herd record`, the section that defines the behaviour: (a) delete the `git rev-list --count` guard sentence — expected: `test_scratch_branch_rule` fails; (b) move the `git branch -D <scratch branch>` step above the worktree removal — expected: `test_removal_order` fails; (c) move the `space.close` step after the worktree removal — expected: `test_removal_order` fails; (d) delete `never by a recorded ID alone` — expected: `test_resolves_by_worktree_path` fails. Restore after each and rerun step 2.
   red when: any mutation leaves the module green.
4. **Headings in order.** `grep -nE '^### (H9 on the app|The herd record|Cleanup from the herd record)$' reference/herdr.md` — expected: three lines in that order.
   red when: the cleanup heading is missing or not last.
   at base: one line, `868:### H9 on the app` (Task 13 adds the second).
5. **Additions only.** `git diff "$(git log -1 --format=%H -- reference/herdr.md)" -- reference/herdr.md | grep -E '^-[^-]'` — the base is the last commit that touched the file, which is Task 13's — expected: no output.
   red when: an existing line (a pinned H9 or record fragment) was removed or re-wrapped.
   control: `git diff b06fbdbfc5ffa48fc2dff3633497e401b5254c19 -- reference/herdr.md | grep -cE '^-[^-]'` prints `18`.
   at base: no output.
6. **The reference's guards hold.** `python3 -m unittest discover -s tests -p 'test_herdr_operations.py' -v` — expected: `Ran 39 tests`, `OK`.
   red when: `test_no_em_dash` or `test_no_personal_values` fails.
   at base: `Ran 39 tests`, `OK`.
7. **H9's tests are undisturbed.** `python3 -m unittest discover -s tests -p 'test_herd.py' -k test_h9 -v` — expected: `Ran 12 tests`, `OK`, including `test_h9_app_cleanup_order`. Only the `test_h9*` methods are run because Task 15 edits `tests/test_herd.py` beside this task; none of its new methods starts with `test_h9`.
   red when: a pointer sentence moves a pinned H9 fragment or breaks the app cleanup order.
   at base: `Ran 12 tests`, `OK`.
8. **Full suite.** `python3 -m unittest discover -s tests -v` — expected: every test passes, except failures that belong to a sibling still running: `tests/test_herd.py` (Task 15), `HerdCleanupDocumentationTest` in `tests/test_transport_docs.py` (Task 16), `tests/test_herdr_surfaces_doc.py` (Task 17).
   red when: a failure in `tests/test_herd_record.py`, `tests/test_herdr_operations.py` or any file no sibling owns.
   at base: `Ran 195 tests`, `OK` before Wave 8; Task 13 adds 5.
