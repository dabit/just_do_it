status: pending
# 25 — Architecture docs: herd modes, untracked tasks, single-quoted handoff

Depends on: 21

## Why
The two architecture docs must record what #38 changed in the herd layer: herd agents run `/jdi:do` or `/jdi:prep` by `herd.mode`, the H9 handoff is single-quoted on both surfaces, the herd record carries a `task` key for an untracked task, `/jdi:do` and `/jdi:prep` both leave the scratch branch at its base, and in `do` mode each agent opens and merges its own pull request, a later one updating its branch when a sibling merged first. Depends on 21, whose H9 text these docs describe. Rests on: U1, E4, M2, M4.

## Description
Planner's Task 25. Edit `docs/herdr-surfaces-architecture.md` and
`docs/delegation-transport-architecture.md`, and pin three facts in
`tests/test_herdr_surfaces_doc.py`.

**Rules:** no `/home/` path (`test_no_personal_paths`); keep every heading in `PRESENT_HEADINGS`, the
`--name '<label>'` operation-map pin, `## The herd record`'s pinned fragments
(`` `jdi/herds/<herd-id>.json` ``, `` `--git-common-dir` ``, `never by a recorded ID alone`), the map
rows starting `| H9 Herd record |` and `| H9 Cleanup from the record |`, and the transport doc's
`` `/jdi:herd --cleanup` `` in `## Two layers`.

TDD is on: write the tests first and watch them fail on their own assertions.

### 1. Tests first, in `tests/test_herdr_surfaces_doc.py`
Under a comment `# Task 25, herd modes and untracked tasks (#38).`:
- `HerdrSurfacesDocTest.test_operation_map_single_quotes_the_invocation`: the line of
  `jdi_files.section(self.text, "## Operation map")` starting `| H9 Hand it the work |` exists and
  contains `` `herdr agent prompt <name> '<invocation>'` `` and
  `` `hc send <terminal> '<invocation>' --if idle` ``, and does not contain `"<invocation>"`.
- `HerdrSurfacesDocTest.test_herd_record_section_names_task`: the normalized `## The herd record`
  section contains `` `task` `` and `` `/jdi:do` ``.
- `TransportDocPointsAtSurfacesTest.test_two_layers_names_herd_mode`: the normalized `## Two layers`
  section of the transport doc contains `` `herd.mode` `` and `` `/jdi:do` ``.

### 2. `docs/herdr-surfaces-architecture.md`
- **Operation map**, row `| H9 Hand it the work |`: TUI column `` `herdr agent prompt <name> '<invocation>'` ``;
  app column "after the readiness wait reports `status: idle`, `` `hc send <terminal> '<invocation>' --if idle` `` (D6).
  Never `space.new --task`". Add, in either column or after the row in prose, that the invocation is
  single-quoted with `'` written `'\''` (M2). The row stays one line.
- **`## The herd record`**:
  - In *Where it lives and how it is written*, a bullet on the `task` key: `issue` is `null` for an
    untracked task and `task` holds its text without the clause (`null` for an issue); `task` is
    additive, so `schema` stays `1`, and a missing `task` reads as `null`.
  - In *How cleanup uses it*, *The scratch branch* bullet's last sentence becomes: "`/jdi:do` and
    `/jdi:prep` start the real work on a branch of their own (`/jdi:do` with **T6** from
    `origin/<default>` at its step 2, `/jdi:prep` with `git switch -c <branch> origin/<default>`);
    neither renames the scratch branch, so it still points at its base." A merged `do` therefore
    leaves a worktree whose scratch branch has no commits of its own.
  - *The report* bullet: an entry with a `null` issue is reported by its `name` and task text.
- **`## Status`**: a sentence naming issue #38 in the same 1.0.13: `herd.mode` (`do` by default,
  `prep` the way back), untracked tasks, the single-quoted handoff, the record's `task` key.

### 3. `docs/delegation-transport-architecture.md`
- **`## Two layers`**: the outer-layer paragraph says each Butler is a full JDI session running
  `/jdi:do` or `/jdi:prep` by `herd.mode`, on an issue or an untracked task. Keep
  `` `/jdi:herd --cleanup` ``.
- **`## Isolation`**: add that in `do` mode each herd Butler opens and merges its own pull request,
  so the worktrees isolate the work but not the merge: a later one finds the default branch moved,
  updates its branch, re-runs its gates and merges (`/jdi:do` step 10).
- **`## Configuration`** (unpinned): the herd-keys bullet ("The herd keys, forthcoming in the
  `/jdi:herd` wave: …") names `herd.mode` too and drops "forthcoming".

## Files
- `docs/herdr-surfaces-architecture.md`
- `docs/delegation-transport-architecture.md`
- `tests/test_herdr_surfaces_doc.py`

## Verification
Run from the repository root.

1. **Red first.** After writing the tests, before editing the docs: `python3 -m unittest discover -s tests -p 'test_herdr_surfaces_doc.py' -v` — expected: `Ran 17 tests`, `FAILED`; failing exactly the three new methods; the other 14 pass.
   red when: a new method passes before the edit, or an existing one fails.
   at base: `Ran 14 tests`, `OK`.
2. **Green.** The same command after the edits — expected: `Ran 17 tests`, `OK`.
   red when: any test fails.
   at base: none — the 3 new methods are written by this task.
3. **The tests bite.** In `docs/herdr-surfaces-architecture.md`, the file that holds the row, put the TUI column back to `herdr agent prompt <name> "<invocation>"` and rerun step 2's command — expected: `test_operation_map_single_quotes_the_invocation` fails. Restore.
   red when: the module stays green.
   at base: none — the mutated text is written by this task.
4. **No double-quoted invocation left in either doc.** `grep -n '"<invocation>"' docs/herdr-surfaces-architecture.md docs/delegation-transport-architecture.md` — expected: no output, exit 1.
   red when: a line is printed.
   control: `git show 2f30a283e56c0c4673b80519810ec314290f7cc7:docs/herdr-surfaces-architecture.md | grep -c '"<invocation>"'` prints `1`.
   at base: one line, the `| H9 Hand it the work |` row of `docs/herdr-surfaces-architecture.md`.
   compliant hits: none.
5. **Full suite.** `python3 -m unittest discover -s tests -v` — expected: every test passes except failures that belong to a sibling still running: `tests/test_herd_handoff.py` (Task 22), `tests/test_herd.py` (Task 23), `tests/test_transport_docs.py` (Task 24).
   red when: a failure in `tests/test_herdr_surfaces_doc.py` or any module no sibling owns.
   at base: `Ran 219 tests`, `OK`, no known reds; Wave 11 adds 14 (233).
