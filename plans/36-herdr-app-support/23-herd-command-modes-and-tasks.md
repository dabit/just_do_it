status: pending
# 23 — `commands/herd.md`: modes, untracked tasks, the report

Depends on: 21

## Why
`/jdi:herd` must read `herd.mode` (default `do`, an invalid value announced once and run as `prep`), accept quoted free-text tasks beside issue IDs with the parse rules that never guess, name a task by a stable hash of its normalised text so a second herd finds the first one's folder, run no tracker step for a task, announce the mode before the first start, and report that a stopped `do` agent waits in its space showing `done`. The command calls H9 by name for the invocation, clause and quoting, which is why it depends on 21. Rests on: U1, U2, E2, E3, E4, E5, M3, M5, M6, M7.

## Description
Planner's Task 23. Edit `commands/herd.md` and pin it in `tests/test_herd.py`.

**Before starting, confirm Task 21 is in** (`grep -c '(untracked, started by /jdi:herd)' reference/herdr.md`
prints at least `1`): Task 21 edited `tests/test_herd.py` too, and this task adds to that version.

**Rules for `commands/herd.md`:**
- **Confined** (`HerdrConfinementTest` scans every line): no `herdr <subcommand>`, `herdr-app`, `hc`,
  `HC_*`, `HERDR_*`, `space.close`-style names, no `AskUserQuestion`. `git` commands are allowed
  (`git hash-object` is).
- The file uses ` - ` as its dash, never an em dash (it has none).
- **Where rules live (M6, C11):** parsing is defined here in step 3; naming and the task suffix here
  in step 5; the invocation table, the clause, the quoting and the record in H9, which this command
  calls by name and never restates. No `--mode` flag and no `mode` in the record (M7).
- **Keep every pinned fragment:** `perform **H1**`, `**H2**`, `**H4b**`, `**H9**`,
  `` `reference/herdr.md` ``, `Validate, never repair`, ``never fall back to a sequential `/jdi:prep` ``,
  `` `.jdi/config.local.yml` ``, `one name per issue`, `Worktree`, `uncommitted plan files`,
  `` `herd`, `herdr`, `harnesses` ``, `H1 settles which Herdr`, `On the app, the space is opened in step 8`,
  `perform **T2**`, `` `<slug>-<suffix>` ``, `**T6**`, `` `[a-z][a-z0-9_-]{0,31}` ``,
  `keep the suffix whole`, ``falls back to the old name `jdi-herd-<issue>` for that issue and says so once``,
  ``any folder whose name ends in `-<suffix>` ``, `The workspace label is the issue title`,
  `the Herdr sidebar shows `blocked` and `done` per pane`, the cleanup-mode fragments, step 11's
  `` `/jdi:herd --cleanup <herd-id>` `` in its first paragraph, `leaves the scratch branch behind`.
  Never write `--resume`, `herd.args`, `herd.env`, `` `/jdi:prep` renames the branch ``,
  `The name is `jdi-herd-<issue>``, `watch loop`, `loop facility` or `Every 5 minutes`.

TDD is on: write the tests first and watch them fail on their own assertions.

### 1. Tests first, in `tests/test_herd.py`
Add a module-level helper:

```python
def step_text(text, n):
    """Step n of commands/herd.md: from its first line to the next numbered step or `## ` heading."""
    lines = text.split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith("%d. **" % n))
    collected = [lines[start]]
    for line in lines[start + 1 :]:
        if re.match(r"^\d+\. \*\*", line) or line.startswith("## "):
            break
        collected.append(line)
    return normalized("\n".join(collected))
```
(`import re`; the first match wins, so step 1 is the herd's step 1, not the cleanup section's.)
Add `import subprocess`. New methods on `HerdCommandTest`, one `subTest` per fragment:

- `test_herd_reads_the_mode` (step 1): `` `herd.mode` ``, `` announced once and runs as `prep` ``.
- `test_herd_parses_issues_and_tasks` (step 3): `A quoted argument is always a task`,
  `an issue ID only when a tracker is configured`, `` `tracker.id_prefix` ``,
  `With no tracker configured, no argument is an issue ID`, `ask once`, `Never guess`,
  `start nothing before the answer`.
- `test_tasks_skip_the_tracker` (step 3): `Tasks skip **T2** and every other tracker step`,
  `nothing is read from or posted to a tracker for a task`.
- `test_task_suffix_is_a_stable_hash` (step 5): `printf '%s' '<normalised task>' | git hash-object --stdin`,
  `` `t96ae2d` ``, `` `fix-typo-signup-email-t96ae2d` ``,
  `an index in the herd would give every herd's first task the same suffix`.
- `test_task_suffix_example_is_reproducible`: find the line of `commands/herd.md` whose `strip()`
  starts with `printf '%s' '<normalised task>'` and **assert it exists** (a missing line is a
  failure, never a skip). Replace `<normalised task>` in it with `fix the typo in the signup email`,
  run `subprocess.run(["sh", "-c", cmd], cwd=jdi_files.ROOT, capture_output=True, text=True)`, and
  assert `result.stdout.strip()[:6] == "96ae2d"`. Precedent: `tests/test_structural_checks.py` runs
  shell snippets with `subprocess.run` the same way. `git hash-object` without `-w` writes nothing.
- `test_mode_announced_before_start` (step 8): `opens and merges its own pull request`, `` `herd.mode: prep` ``.
- `test_report_names_do_mode_stops` (step 10): `` a `do` agent that stopped ``, `` the sidebar shows `done` for it ``.
- `test_cleanup_refuses_tasks_alongside` (whole normalized file): `` Issue IDs, tasks or `--kind` ``.
- `test_argument_hint_names_tasks`: the frontmatter `argument-hint` (read as
  `test_argument_hint_names_cleanup` reads it) contains `'task text'` and `--cleanup [<herd-id>]`.

The existing pins listed under Rules stay as they are (no existing test is edited).

### 2. Edits to `commands/herd.md`

**Frontmatter (M-F, both lines exact):**
```text
description: "Run several issues or untracked tasks in parallel - one Herdr worktree, pane, and agent each, running /jdi:do (or /jdi:prep, by herd.mode) - or clean a herd up from its record."
argument-hint: "<issue-id | 'task text'> [...] [--kind <kind>] | --cleanup [<herd-id>]"
```

**Intro.** The role line: it starts one independent agent session per issue or task, each running
`/jdi:do` or `/jdi:prep` by `herd.mode`. "Prepare several issues at the same time" becomes "Run
several issues or untracked tasks at the same time"; each gets its own worktree, workspace and agent.
"Those happen inside the spawned agents, under `/jdi:prep`" becomes "under `/jdi:do` or `/jdi:prep`".

**Step 1.** Add `herd.mode` to what is read (`herd.kind`, `herd.mode`, `herd.max_parallel` and
`herd.seed`) and its default to the defaults sentence (`claude`, `do`, `5`, …). Then (M3): "An
invalid `herd.mode` is announced once and runs as `prep`, the mode with less authority, never the
other way."

**Step 3 — `3. **Parse the issues and tasks**`.** Replace its first paragraph with the parse rules
below. The bold lead-ins and the quoted fragments in the tests are exact; the rest is a draft you may
reword without changing a rule (E3):

- Read `$ARGUMENTS` as arguments: a run in matching quotes (`"…"` or `'…'`, opened at the start of
  an argument) is one argument; elsewhere split on whitespace and commas. Drop any `--kind <x>`.
- **A quoted argument is always a task**, whatever it looks like.
- **An unquoted argument is an issue ID only when a tracker is configured** (`tracker.name` set and
  not `none`) **and it has an issue's shape**: an issue URL, `#<digits>` or `<digits>` for GitHub,
  or `<KEY>-<digits>`; with `tracker.id_prefix` set, `<KEY>` must be that prefix. Normalize each
  issue ID per **T1**.
- **With no tracker configured, no argument is an issue ID**: unquoted words are not issues there.
- **Anything else is ambiguous**: other unquoted words, or a quote with no match. Each unbroken run
  of them is joined into one candidate task. Show the whole reading (each issue ID, each task, each
  ambiguous run as the task it would become) and ask once. Never guess, and start nothing before the
  answer.
- With nothing to herd at all, ask what to herd and stop; never invent an issue, and never create
  one here. `/jdi:herd` only takes issues that already exist.

Then: "Tasks skip **T2** and every other tracker step: nothing is read from or posted to a tracker
for a task." Keep the existing T2 paragraph and its fallback sentences for issues unchanged (the
`perform **T2**` and `falls back to the old name …` pins). The `herd.max_parallel` paragraph counts
issues and tasks together.

**Step 5.** Title `5. **Reserve the agent names - one name per issue or task**`; "Build **one name
per issue or task**". Add this bullet after the `<suffix>` bullet (M-F; wording exact, may be
rewrapped), with the fence indented as part of the bullet and holding exactly the one line shown:

> **An untracked task** has no title and no issue ID. `<slug>` comes from the task text's key words by the same rules, and `<suffix>` is `t` followed by the first six hex digits of its hash, where the normalised task is the task text lowercased, with every run of whitespace collapsed to one space and none at either end:
>
> ```text
> printf '%s' '<normalised task>' | git hash-object --stdin
> ```
>
> Single-quote the task as H9's invocation table says. The same text always gives the same suffix, so a second herd for the same task finds the first one's folder by the suffix check in step 6; an index in the herd would give every herd's first task the same suffix and make that check fire for unrelated work. `fix the typo in the signup email` hashes to `96ae2d07…`, so its suffix is `t96ae2d` and its name `fix-typo-signup-email-t96ae2d`.

(The `>` markers are this task file's quoting; in `commands/herd.md` it is a list bullet starting
`- **An untracked task**`, and the fence line inside it is `printf '%s' '<normalised task>' | git hash-object --stdin`
after its indent. `96ae2d07…` is the literal text, ellipsis included.) The fallback-name bullet
stays about issues: a task never falls back to `jdi-herd-<issue>` (H9 *Names*).

**Step 6.** "For issue *N*" becomes "For issue or task *N*". After the workspace-label paragraph:
for an untracked task the label is `<suffix> <task text>`, for example
`t96ae2d fix the typo in the signup email`. In the existing-folder paragraph, the choice becomes
"continue there, in a fresh session in that folder with `/jdi:status`, or `/jdi:do` again where no
plan exists, or skip this issue or task".

**Step 7.** Placeholder table rows: `{{issue}}` "the issue ID, e.g. `JUT-3073` (an untracked task:
its suffix, e.g. `t96ae2d`)"; `{{issue_lower}}` "the same, lowercased, e.g. `jut-3073` (an untracked
task: its suffix, e.g. `t96ae2d`)".

**Step 8 (M5).** Before the first start, announce the mode, e.g.: "Before the first start, say which
mode this herd runs in. In `do`, say that each agent opens and merges its own pull request,
unattended and in parallel with the others, and that `herd.mode: prep` stops every agent at a plan
instead. The herd invocation is the authorization, as `/jdi:do`'s request is."

**Step 9.** "Send each Butler its command, the invocation from H9's invocation table for the kind and
`herd.mode`, with `<WORK>` filled in, as H9 says."

**Step 10.** One row per issue or task (the issue ID, or the task text), and name the mode. Add the
M-F sentence (wording exact, may be rewrapped):
> In `do` mode, a `do` agent that stopped before merging (a product decision, a change the repository reserves for a person, a review that will not converge, or a pull request it could not open) waits in its space with its reason, and the sidebar shows `done` for it, as for one that merged: open its space to see which. An agent whose work was too big says so and continues with `/jdi:prep` in the same space.

The scratch sentence becomes "Say that `/jdi:do` or `/jdi:prep` leaves the scratch branch behind at
its base and works on a branch of its own, and that the record, not the branch name, is how cleanup
finds the worktree."

**Step 11.** "A herd worktree usually holds an uncommitted plan" becomes "A prep-mode worktree, or one
whose `do` agent continued with prep, usually holds an uncommitted plan, because `/jdi:prep` commits
only when asked." Step 11's first paragraph keeps `` `/jdi:herd --cleanup <herd-id>` ``.

**Cleanup step 2.** "Issue IDs or `--kind` alongside `--cleanup`" becomes "Issue IDs, tasks or
`--kind` alongside `--cleanup`".

**`## Limits worth stating in the report`**, two new bullets:
- "**`do` mode ships unattended.** Each agent opens and merges its own pull request, in parallel,
  with nobody approving each one. The repository's own rules still win, and `herd.mode: prep` is
  the way back."
- "**Parallel merges can conflict.** When a sibling merged first, a `do` agent brings its branch up
  to date with the default branch and runs its gates again before it merges (`/jdi:do` step 10); a
  conflict that needs a product decision stops it in its space."

The `harnesses.<kind>.env` limit's "or the prep command is not a command in that session" may become
"the herd's command"; nothing else changes.

## Files
- `commands/herd.md`
- `tests/test_herd.py`

## Verification
Run from the repository root.

1. **Red first.** After writing the tests, before editing the command: `python3 -m unittest discover -s tests -p 'test_herd.py' -v` — expected: `Ran 33 tests`, `FAILED`; failing exactly the nine new methods; the 24 from Task 21's version pass.
   red when: a new method passes before the edit (in particular `test_task_suffix_example_is_reproducible` passing with no `printf` line, which means it skipped), or an existing method fails.
   at base: `Ran 21 tests`, `OK` at `2f30a28`; `Ran 24 tests`, `OK` after Task 21.
2. **Green.** The same command after the edit — expected: `Ran 33 tests`, `OK`.
   red when: any test fails.
   at base: none — the 9 new methods are written by this task.
3. **The documented hash is the real one.** `printf '%s' 'fix the typo in the signup email' | git hash-object --stdin` — expected: `96ae2d07982d30fb9e3b6a127640b39f0f7bb696`. Then, in `commands/herd.md`, the file that defines the command, change that fence line's `printf '%s'` to `echo` and rerun step 2's command — expected: `test_task_suffix_example_is_reproducible` fails (`echo` appends a newline: the hash becomes `176623f7…`). Restore it.
   red when: the hash differs, or the mutation leaves the test green.
   at base: `96ae2d07982d30fb9e3b6a127640b39f0f7bb696`; with `echo`, `176623f7c47b80b9664688446171a50d1a4a4bd8`.
4. **Confined.** `python3 -m unittest discover -s tests -p 'test_delegation_transport.py' -k HerdrConfinementTest -v` — expected: `Ran 2 tests`, `OK`, with no subtest naming `commands/herd.md`.
   red when: a failure names `commands/herd.md`. (A failure naming `commands/do.md`, `commands/prep.md`, `commands/help.md` or `commands/init.md` belongs to Task 22 or 24.)
   at base: `Ran 2 tests`, `OK`.
5. **No em dash, no stale prep-only wording.** `grep -c '—' commands/herd.md` — expected: `0`. `grep -n 'Prepare several issues\|Prep several issues\|Parse the issues\*\*' commands/herd.md` — expected: no output.
   red when: a count above `0`, or a line printed (the intro, frontmatter or step 3 title still says issues only).
   control: `grep -c '—' commands/do.md` prints `20`; `git show 2f30a283e56c0c4673b80519810ec314290f7cc7:commands/herd.md | grep -c 'Prepare several issues\|Prep several issues\|Parse the issues\*\*'` prints `3`.
   at base: `0`; three lines (frontmatter `description`, the `Prepare several issues` intro line, step 3's title).
   compliant hits: none.
6. **Frontmatter still parses everywhere.** `python3 -m unittest discover -s tests -p 'test_frontmatter.py' -v` and `python3 -m unittest discover -s tests -p 'test_opencode_sync.py' -v` — expected: `Ran 6 tests`, `OK` and `Ran 4 tests`, `OK` (the `'` and `|` inside the double-quoted `argument-hint` are plain characters).
   red when: either fails.
   at base: `Ran 6 tests`, `OK`; `Ran 4 tests`, `OK`.
7. **Full suite.** `python3 -m unittest discover -s tests -v` — expected: every test passes except failures that belong to a sibling still running: `tests/test_herd_handoff.py` (Task 22), `tests/test_transport_docs.py` (Task 24), `tests/test_herdr_surfaces_doc.py` (Task 25), `tests/test_config_schema.py` (Task 20, if still running).
   red when: a failure in `tests/test_herd.py`, `tests/test_herd_record.py`, `tests/test_frontmatter.py`, `tests/test_opencode_sync.py`, or any module no sibling owns.
   at base: `Ran 219 tests`, `OK`, no known reds; Wave 11 adds 14 (233).
