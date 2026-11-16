status: done
# 16 — User docs and CHANGELOG: `/jdi:herd --cleanup`

Depends on: 12, 13

## Why
A user learns about `/jdi:herd --cleanup [<herd-id>]` from `/jdi:help`, the README and the 1.0.13 CHANGELOG: that a herd keeps a record under the git directory that is never committed, that cleanup skips what is busy or holds uncommitted work, asks once, and deletes only scratch branches with no commits of their own. It ships in the same 1.0.13 release as #36, with no version bump. Depends on 12 so a gate amendment that changes user-visible behaviour reaches these docs, and on 13 for the record's shape. Rests on: C1, C2, C3, C4.

## Description
Planner's Task 16. Name the cleanup mode in the four user-facing files and pin three of them in
`tests/test_transport_docs.py`.

**Before starting, read `## Probe log (#37)` in PLAN.md (Task 12).** An amendment there that
changes what the user sees (for example, the TUI being unreachable for cleanup) wins over this file.

**Rules:**
- `commands/help.md` is confined (`HerdrConfinementTest`): no `herdr <subcommand>`, `herdr-app`,
  `hc`, `HC_*` or `space.close`-style names. The README and CHANGELOG are not scanned, but the
  Planner's rule applies to them too: **no app command names**, only "the Herdr app", "space",
  "workspace".
- No version bump: `.claude-plugin` and `.codex-plugin` stay at `1.0.13`, and the bullet goes into
  the existing `## 1.0.13` section.

TDD is on: write the tests first and watch them fail.

### 1. Tests first: class `HerdCleanupDocumentationTest` in `tests/test_transport_docs.py`
- `test_help_herd_row_names_cleanup`: the line of `commands/help.md` that starts with
  `` | `/jdi:herd` | `` exists and contains `` `--cleanup` ``.
- `test_readme_cleanup_paragraph`: `jdi_files.paragraph_starting_with(readme, "`/jdi:herd --cleanup ")`,
  joined with spaces and normalized, contains `herd record`, `never committed`, `asks once`.
- `test_changelog_names_cleanup`: `jdi_files.section(changelog, "## 1.0.13")`, normalized, contains
  `` `/jdi:herd --cleanup [<herd-id>]` ``.

### 2. Edits
- **`README.md`.** A new paragraph directly after the paragraph that starts
  `` `/jdi:herd ENG-1234 ENG-1235` preps several existing issues ``, starting at column 0 with
  `` `/jdi:herd --cleanup ``, for example `` `/jdi:herd --cleanup [<herd-id>]` cleans a herd up from its herd record. ``
  Say: a herd writes a herd record under the repository's git directory, never committed; cleanup
  reads it and never guesses from folder names; it skips an agent still working or blocked, the
  session's own worktree, and a worktree with uncommitted changes it may not force; a worktree
  whose plan folder holds uncommitted files gets its own question; it shows one list and asks once;
  it closes the space or workspace, then removes the worktree; it deletes a scratch branch only when
  it has no commits of its own, and never a feature branch; it reports what it removed and skipped.
  Adjust the herd paragraph's last sentence only if it now contradicts this (it says the command
  removes nothing on its own, which stays true).
- **`commands/help.md`.** In the `/jdi:herd` row, add a clause with `` `--cleanup [<herd-id>]` ``:
  cleans a herd up from its record, asking once.
- **`AGENTS.md`.** The `commands/herd.md` row gains a matching clause (`--cleanup` from the herd
  record). **Not pinned by a test; say so** in the task notes.
- **`CHANGELOG.md`.** In `## 1.0.13`, a bullet directly after the bullet that starts
  `` **`/jdi:herd` arrives on the shared Herdr operations ``, naming
  `` `/jdi:herd --cleanup [<herd-id>]` ``, the herd record (under the git directory, never committed,
  written atomically, same on both surfaces), and the safety rules (busy and own-location skips, the
  plan-file guard, one question, `--force` only for seeded worktrees, scratch branches only when
  they have no commits of their own). No version bump.

## Files
- `README.md`
- `commands/help.md`
- `AGENTS.md`
- `CHANGELOG.md`
- `tests/test_transport_docs.py`

## Verification
Run from the repository root.

1. **Red first.** After writing the tests and before editing the docs: `python3 -m unittest discover -s tests -p 'test_transport_docs.py' -v` — expected: `Ran 15 tests`, `FAILED`; the three new methods fail (`test_readme_cleanup_paragraph` with `no paragraph starting with`), the other 12 pass.
   red when: a new test passes before the edit.
   at base: `Ran 12 tests`, `OK`.
2. **Green.** The same command after the edits — expected: `Ran 15 tests`, `OK`.
   red when: any test fails.
   at base: none — written by this task.
3. **AGENTS.md row (not pinned).** `grep -n 'commands/herd.md' AGENTS.md` — expected: one line, the table row, now containing `--cleanup`.
   red when: the row does not mention `--cleanup`.
   at base: `27:| `commands/herd.md` | Prep several issues in parallel inside Herdr, one worktree and agent each |`.
4. **No app command names in the README paragraph.** `awk '/^`\/jdi:herd --cleanup /{f=1} f&&/^$/{exit} f' README.md | grep -nE 'herdr-app|\bhc\b|space\.close|herdr worktree|herdr workspace'` — expected: no output, exit status 1.
   red when: an app or TUI command name is printed.
   control: `grep -cE 'herdr-app|\bhc\b|space\.close|herdr worktree|herdr workspace' reference/herdr.md` prints a positive count (`78` at base), so the pattern matches when the names are there.
   at base: no output (the paragraph does not exist).
5. **Help stays confined.** `python3 -m unittest discover -s tests -p 'test_delegation_transport.py' -k HerdrConfinementTest -v` — expected: `Ran 2 tests`, `OK`.
   red when: the help row names an app or TUI command.
   at base: `Ran 2 tests`, `OK`.
6. **No version bump.** `python3 -m unittest discover -s tests -p 'test_versions.py' -v` — expected: `Ran 5 tests`, `OK`; and `grep -h '"version"' .claude-plugin/*.json .codex-plugin/*.json` prints `1.0.13` on every line.
   red when: a version moved, or the CHANGELOG and the JSON disagree.
   at base: `Ran 5 tests`, `OK`; three lines, each `"version": "1.0.13"`.
7. **Full suite.** `python3 -m unittest discover -s tests -v` — expected: every test passes, except failures that belong to a sibling still running: `tests/test_herd_record.py` (Task 14), `tests/test_herd.py` (Tasks 14 and 15), `tests/test_herdr_surfaces_doc.py` (Task 17).
   red when: a failure in `tests/test_transport_docs.py`, `tests/test_versions.py`, `tests/test_delegation_transport.py` or any file no sibling owns.
   at base: `Ran 195 tests`, `OK` before Wave 8; Task 13 adds 5.
