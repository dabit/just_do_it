status: done
# 17 — Architecture docs: the herd record and cleanup from it

Depends on: 12, 13

## Why
The surfaces architecture doc records each Herdr operation's TUI and app variant and the probes behind it, so the herd record and cleanup from it need their two operation-map rows and a section that states C1–C11 with Task 12's results; the transport doc still says the `/jdi:herd` layer "is planned in the same branch as a separable wave", which is stale, and its *Two layers* should name `/jdi:herd --cleanup`. Depends on 12 for the probe results the rows and section record, and on 13 for the record's location and shape. Rests on: C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11.

## Description
Planner's Task 17. Edit the two architecture docs and pin the changes in
`tests/test_herdr_surfaces_doc.py`.

**Before starting, read `## Probe log (#37)` in PLAN.md (Task 12).** The TUI and app columns of the
new rows, and the section's account of what was probed, come from that log; an amendment there
wins over this file.

**Rules:** no `/home/` anywhere in the surfaces doc (`test_no_personal_paths`); placeholders only.
Keep every existing heading in `PRESENT_HEADINGS` and the existing operation-map rows unchanged.

TDD is on: write the tests first and watch them fail.

### 1. Tests first, in `tests/test_herdr_surfaces_doc.py`
- Add `"## The herd record"` to `PRESENT_HEADINGS` (so `test_headings_present` covers it).
- `HerdrSurfacesDocTest.test_herd_record_section`: the joined, whitespace-flattened
  `jdi_files.section(self.text, "## The herd record")` contains `` `jdi/herds/<herd-id>.json` ``,
  `` `--git-common-dir` ``, `never by a recorded ID alone`.
- `HerdrSurfacesDocTest.test_operation_map_has_record_rows`: among the lines of
  `jdi_files.section(self.text, "## Operation map")`, one starts with `| H9 Herd record |` and one
  with `| H9 Cleanup from the record |`.
- `TransportDocPointsAtSurfacesTest.test_transport_status_is_not_stale`: the transport doc,
  whitespace-flattened, does not contain `is planned in the same branch as a separable wave`.
- `TransportDocPointsAtSurfacesTest.test_two_layers_names_cleanup`: the joined
  `jdi_files.section(transport, "## Two layers")`, flattened, contains `` `/jdi:herd --cleanup` ``.

### 2. `docs/herdr-surfaces-architecture.md`
- **`## Status`.** Name #37: the herd record and `/jdi:herd --cleanup` ship in the same 1.0.13, with
  their own probe gate (Task 12).
- **`## Operation map`.** Two rows after `| H9 List |`, with TUI and app columns per the Task 12
  gate:
  - `| H9 Herd record |`: both columns the same record at `<git-common-dir>/jdi/herds/<herd-id>.json`;
    TUI fills the workspace, tab and pane at step 6; app fills the space, tab, pane and terminal at
    step 8.
  - `| H9 Cleanup from the record |`: TUI, the entry found with
    `herdr worktree list --cwd <main checkout>` by `path` and `open_workspace_id`, busy from
    `herdr workspace get`'s `agent_status`, then the gated TUI removal; app, the space found in
    `herdr-app ls` by `folder`, busy across `hc ls --json --label herdr.space=<space>` (or the
    gated per-terminal `hc get`), then `space.close`, then `git -C <main checkout> worktree remove`.
- **New `## The herd record`**, after `## The app's worktree layout`: C1–C11 in prose (location
  under `--git-common-dir` and why every worktree sees it; `jdi/herds/<herd-id>.json`; never
  committed; written whole then `mv -f`; no session or app home recorded; `creating` and
  `handed_off`; a failed write costs one sentence; the checked herd ID; never guessing from folder
  names; IDs re-found by worktree path, never by a recorded ID alone, because app terminal IDs and
  TUI workspace IDs are reused; the skips; the plan-file guard and one question; `--force` only for
  seeded worktrees; the scratch-branch rule and why `/jdi:prep` leaves the branch behind; record
  upkeep; the report; rules defined only in `reference/herdr.md`). Then Task 12's results, R1–R5,
  briefly, with any `G<n>` amendment.

### 3. `docs/delegation-transport-architecture.md`
- **`## Status`.** Replace the stale sentence (the `/jdi:herd` layer "is planned in the same branch
  as a separable wave") with one saying that layer exists in the same release, including
  `/jdi:herd --cleanup`.
- **`## Two layers`.** One sentence in the outer-layer paragraph: the herd records what it made, and
  `/jdi:herd --cleanup` removes it from that record later.

## Files
- `docs/herdr-surfaces-architecture.md`
- `docs/delegation-transport-architecture.md`
- `tests/test_herdr_surfaces_doc.py`

## Verification
Run from the repository root.

1. **Red first.** After writing the tests and before editing the docs: `python3 -m unittest discover -s tests -p 'test_herdr_surfaces_doc.py' -v` — expected: `Ran 14 tests`, `FAILED`; `test_headings_present` fails on `## The herd record`, `test_herd_record_section` errors (heading not found), `test_operation_map_has_record_rows`, `test_transport_status_is_not_stale` and `test_two_layers_names_cleanup` fail; the other 9 pass.
   red when: a new or extended test passes before the edit.
   at base: `Ran 10 tests`, `OK`.
2. **Green.** The same command after the edits — expected: `Ran 14 tests`, `OK`.
   red when: any test fails.
   at base: none — written by this task.
3. **Stale sentence gone.** `grep -c 'is planned in the same branch as a separable wave' docs/delegation-transport-architecture.md` — expected: `0`.
   red when: `1`.
   control: `git show cdd14046784af5ef7e58fe612067f17a2e5b60df:docs/delegation-transport-architecture.md | grep -c 'is planned in the same branch as a separable wave'` prints `1`.
   at base: `1`.
4. **Rows in the map.** `awk '/^## Operation map$/{f=1;next} /^## /{f=0} f' docs/herdr-surfaces-architecture.md | grep -cE '^\| H9 (Herd record|Cleanup from the record) \|'` — expected: `2`.
   red when: fewer than 2.
   at base: `0`.
5. **No personal path.** `grep -c '/home/' docs/herdr-surfaces-architecture.md` — expected: `0`.
   red when: a probe path was copied in unsanitised.
   control: `grep -c '/home/' plans/36-herdr-app-support/PLAN.md` prints a positive count, so the pattern matches when the text is there.
   at base: `0`.
6. **Full suite.** `python3 -m unittest discover -s tests -v` — expected: every test passes, except failures that belong to a sibling still running: `tests/test_herd_record.py` (Task 14), `tests/test_herd.py` (Tasks 14 and 15), `HerdCleanupDocumentationTest` in `tests/test_transport_docs.py` (Task 16).
   red when: a failure in `tests/test_herdr_surfaces_doc.py` or any file no sibling owns.
   at base: `Ran 195 tests`, `OK` before Wave 8; Task 13 adds 5.
