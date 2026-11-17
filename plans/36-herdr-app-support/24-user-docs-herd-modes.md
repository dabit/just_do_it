status: pending
# 24 — User docs and CHANGELOG: herd modes and untracked tasks

Depends on: 20, 21

## Why
A user learns from `/jdi:help`, `/jdi:init`, the README, `AGENTS.md` and the 1.0.13 CHANGELOG that `/jdi:herd` now runs `/jdi:do` by default and takes quoted untracked tasks, and that `do` mode opens and merges pull requests unattended and in parallel, with `herd.mode: prep` as the way back; init offers `herd.mode` as a team choice for `config.yml`. It ships in the same 1.0.13, with no version bump. Depends on 20 for the key's name, default and notes, and on 21 for the invocation and clause the docs describe. Rests on: U1, U2, U3, E6, M5.

## Description
Planner's Task 24. Five user-facing files, four pinned by a new class in
`tests/test_transport_docs.py`.

**Rules:**
- `commands/help.md` and `commands/init.md` are confined (`HerdrConfinementTest`): no
  `herdr <subcommand>`, `herdr-app`, `hc`, `HC_*`, `HERDR_*`, `space.close`-style names. The README,
  `AGENTS.md` and the CHANGELOG are not scanned, but the same rule applies: no app or TUI command
  names, only "the Herdr app", "space", "workspace".
- No version bump: the bullet goes into the existing `## 1.0.13`; `.claude-plugin` and
  `.codex-plugin` stay at `1.0.13`.
- Say plainly (E6, R19): `do` mode merges unattended and in parallel; `herd.mode: prep` is the way
  back; the repository's own rules still win.
- Keep the pins the existing classes read: help's opening paragraph keeps `which Herdr surface`;
  the help `/jdi:herd` row keeps `` `--cleanup` ``; the README keeps its paragraph starting
  `` `/jdi:herd --cleanup `` (with `herd record`, `never committed`, `asks once`) directly after the
  herd paragraph; `## 1.0.13` keeps `` `/jdi:herd --cleanup [<herd-id>]` ``; init keeps
  `offer `herdr.surface``.

TDD is on: write the tests first and watch them fail on their own assertions.

### 1. Tests first: class `HerdModeDocumentationTest` in `tests/test_transport_docs.py`
Place it after `HerdCleanupDocumentationTest`, with a docstring naming #38 and that the AGENTS.md
row and the help `/jdi:do` row are not pinned. Use the module's `normalized`. One `subTest` per
fragment.

- `test_help_herd_row_names_the_modes`: the line of `commands/help.md` starting `` | `/jdi:herd` | ``
  contains `` `/jdi:do` ``, `` `herd.mode: prep` ``, `merges`.
- `test_help_opening_names_the_herd_mode`: `normalized(" ".join(jdi_files.paragraph_starting_with(help, "Explain the Just Do It")))`
  contains ``which herd mode is set, when not `do` ``.
- `test_init_offers_the_mode`: `commands/init.md` contains `` offer `herd.mode` ``.
- `test_readme_herd_paragraph_names_the_modes`: `normalized(" ".join(jdi_files.paragraph_starting_with(readme, "`/jdi:herd ENG-1234 ")))`
  contains `` `herd.mode` ``, `unattended`, `in parallel`, `` `herd.mode: prep` ``,
  `"fix the typo in the signup email"` (with its double quotes).
- `test_changelog_names_the_modes`: `normalized("\n".join(jdi_files.section(changelog, "## 1.0.13")))`
  contains `` `herd.mode` ``, `unattended`, `in parallel`, `` `herd.mode: prep` ``, `untracked`.

Note: `` `herd.mode: do` `` does **not** contain `` `herd.mode` `` (the backtick closes after
`do`); each doc needs the bare key in backticks somewhere in the pinned span.

### 2. Edits
- **`README.md`.** Rewrite the paragraph that starts `` `/jdi:herd ENG-1234 ENG-1235` preps several
  existing issues `` so it starts at column 0 with
  `` `/jdi:herd ENG-1234 "fix the typo in the signup email"` `` and stays **one paragraph** (no blank
  line inside; the `--cleanup` paragraph follows it). Cover: issues and quoted untracked tasks (a
  task needs no tracker; its name, folder and herd record entry come from its text); the `herd.mode`
  key: by default (`herd.mode: do`) each agent runs `/jdi:do`, which plans in chat, builds,
  verifies, opens its pull request and merges it, unattended and in parallel with the others, the
  repository's own rules still winning; an agent whose work is too big continues with `/jdi:prep` in
  the same space; an agent that stops before merging waits in its space and the sidebar shows it
  as done, so open the space to see why; `herd.mode: prep` is the way back, every agent stopping at
  a plan. Keep the facts the paragraph states today: one worktree, workspace or space and agent
  each; the issue-title label; the readable name such as `add-presence-indicators-eng-1234` and the
  `jdi-herd-<issue>` fallback; Herdr required, never a sequential prep; the `herd` block (now also
  the mode); removes no worktree on its own, never one holding an uncommitted plan without your yes.
- **`commands/help.md`.**
  - The `/jdi:herd` row: runs several issues or untracked tasks at once inside Herdr, the TUI or the
    app, one worktree, pane and agent each, each running `/jdi:do`, which opens and merges its own
    pull request unattended; `herd.mode: prep` stops each at a plan instead. Keep "Needs Herdr …",
    "never falls back to a sequential prep" and the `--cleanup` clause.
  - The opening paragraph's list of what the closing line names gains, after "which Herdr surface is
    pinned, when not `auto`,": "which herd mode is set, when not `do`,".
  - The `/jdi:do` row (unpinned): after "… or a review that will not converge." add "(under
    `/jdi:herd` it continues with `/jdi:prep` instead)" attached to the too-big stop, e.g. "Stops
    only for work too big for one session (under `/jdi:herd` it continues with `/jdi:prep`
    instead), …".
- **`commands/init.md`**, step 10's herd sub-bullet (the one starting "When the user plans to use
  `/jdi:herd`, offer the `herd` block too"): add a sentence that offers the key, e.g. "Then offer
  `herd.mode`: `do`, the default, has each herd agent run `/jdi:do`, which opens and merges its own
  pull request unattended and in parallel; `prep` stops each at a plan. Say that this is the team's
  call, so it belongs in `config.yml`, not `.jdi/config.local.yml`." No new numbered step.
- **`AGENTS.md`** (unpinned; say so in the task notes): the `commands/herd.md` row becomes "Run
  several issues or untracked tasks in parallel inside Herdr, one worktree and agent each, running
  `/jdi:do` (or `/jdi:prep`, by `herd.mode`); `--cleanup` cleans a herd up from its herd record".
- **`CHANGELOG.md`**, `## 1.0.13`:
  - The bold headline's clause "`/jdi:herd` preps several issues at once, one worktree and agent
    each" names `/jdi:do`, e.g. "`/jdi:herd` runs several issues or untracked tasks at once, one
    worktree and agent each, each agent running `/jdi:do` (or `/jdi:prep`)".
  - A bold bullet directly after the bullet that starts `` **`/jdi:herd --cleanup [<herd-id>]` cleans a herd up ``:
    `herd.mode: do | prep`, default `do`; in `do` each agent opens and merges its own pull request,
    **unattended and in parallel**, the repository's own rules still winning, and `herd.mode: prep`
    is the way back; the herd announces the mode before the first start; a too-big `/jdi:do` started
    by a herd continues with `/jdi:prep` in the same session; an invalid `herd.mode` runs as `prep`;
    quoted **untracked** tasks need no tracker and are named by a stable hash of their text
    (`t` + six hex digits); the invocation is single-quoted on both surfaces; the herd record gains
    `task`; `/jdi:do` now updates a branch whose pull request the default branch moved under, then
    re-runs its gates. Name the key as `` `herd.mode` `` at least once.

## Files
- `README.md`
- `commands/help.md`
- `commands/init.md`
- `AGENTS.md`
- `CHANGELOG.md`
- `tests/test_transport_docs.py`

## Verification
Run from the repository root.

1. **Red first.** After writing the tests, before editing the docs: `python3 -m unittest discover -s tests -p 'test_transport_docs.py' -v` — expected: `Ran 20 tests`, `FAILED`; failing exactly the five new methods; the other 15 pass.
   red when: a new method passes before the edit, or an existing one fails.
   at base: `Ran 15 tests`, `OK`.
2. **Green.** The same command after the edits — expected: `Ran 20 tests`, `OK`.
   red when: any test fails (an existing pin such as `test_readme_cleanup_paragraph` or `test_help_opening_names_the_pinned_surface` failing means the rewrite dropped it).
   at base: none — the 5 new methods are written by this task.
3. **The tests bite.** In `CHANGELOG.md`, the file that states the release, delete `` `herd.mode: prep` `` from the new bullet and rerun step 2's command — expected: `test_changelog_names_the_modes` fails. Restore. In `README.md`, insert a blank line in the middle of the herd paragraph — expected: `test_readme_herd_paragraph_names_the_modes` fails (the paragraph is cut). Remove it.
   red when: either mutation leaves the module green.
   at base: none — the mutated text is written by this task.
4. **AGENTS.md row (not pinned).** `grep -n 'commands/herd.md' AGENTS.md` — expected: one line, the table row, containing `/jdi:do`, `herd.mode` and `--cleanup`.
   red when: the row lacks any of the three.
   at base: ``27:| `commands/herd.md` | Prep several issues in parallel inside Herdr, one worktree and agent each; `--cleanup` cleans a herd up from its herd record |``.
5. **No app or TUI command names in the README herd paragraph.** ``awk '/^`\/jdi:herd ENG-1234 /{f=1} f&&/^$/{exit} f' README.md | grep -nE 'herdr-app|\bhc\b|space\.close|herdr worktree|herdr workspace|herdr agent'`` — expected: no output, exit 1.
   red when: a line is printed.
   control: ``grep -cE 'herdr-app|\bhc\b|space\.close|herdr worktree|herdr workspace|herdr agent' reference/herdr.md`` prints a positive count (`113` at base; Task 21 may move it), so the pattern matches when the names are there.
   at base: no output; the paragraph the awk extracts is 10 lines and names none.
   compliant hits: none.
6. **Help and init stay confined.** `python3 -m unittest discover -s tests -p 'test_delegation_transport.py' -k HerdrConfinementTest -v` — expected: `Ran 2 tests`, `OK`, with no subtest naming `commands/help.md` or `commands/init.md`.
   red when: a failure names either file. (One naming `commands/herd.md`, `do.md` or `prep.md` belongs to Task 22 or 23.)
   at base: `Ran 2 tests`, `OK`.
7. **No version bump.** `python3 -m unittest discover -s tests -p 'test_versions.py' -v` — expected: `Ran 5 tests`, `OK`; and `grep -h '"version"' .claude-plugin/plugin.json .claude-plugin/marketplace.json .codex-plugin/plugin.json` — expected: three lines, each `"version": "1.0.13"`.
   red when: a version moved, or the CHANGELOG's first heading is no longer `## 1.0.13`.
   at base: `Ran 5 tests`, `OK`; three lines, each `"version": "1.0.13"`.
8. **Full suite.** `python3 -m unittest discover -s tests -v` — expected: every test passes except failures that belong to a sibling still running: `tests/test_herd_handoff.py` (Task 22), `tests/test_herd.py` (Task 23), `tests/test_herdr_surfaces_doc.py` (Task 25).
   red when: a failure in `tests/test_transport_docs.py`, `tests/test_versions.py`, `tests/test_config_schema.py`, or any module no sibling owns.
   at base: `Ran 219 tests`, `OK`, no known reds; Wave 11 adds 14 (233).
