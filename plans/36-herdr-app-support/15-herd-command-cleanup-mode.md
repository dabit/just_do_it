status: done
# 15 — `commands/herd.md`: the `--cleanup` mode

Depends on: 12, 13

## Why
The user reaches herd cleanup as `/jdi:herd --cleanup [<herd-id>]`, a mode of the existing command rather than a new command file, and a normal herd's step 11 must name `/jdi:herd --cleanup <herd-id>` so the cleanup is findable when the agents finish. The command calls *The herd record* and *Cleanup from the herd record* by name and restates none of their rules, and it stops saying `/jdi:prep` renames the scratch branch, because prep leaves it behind. Depends on 12 because a gate amendment can change what this task writes, and on 13 for the record's write points. Rests on: C2, C4, C8, C11.

## Description
Planner's Task 15. Add the `--cleanup` mode to `commands/herd.md`, have steps 5–11 say what H9
records, and pin it in `tests/test_herd.py`.

**Before starting, read `## Probe log (#37)` in PLAN.md (Task 12).** An amendment there wins over
this file. None of the pre-agreed amendments is expected to change this command's text, because the
command names no surface command; if one does, follow it.

**This task runs beside Task 14**, which writes `### Cleanup from the herd record` in
`reference/herdr.md`. This command refers to that section by its exact name,
*Cleanup from the herd record*, and to Task 13's *The herd record*. No test here checks that the
referenced sections exist, so the names must be spelt exactly so.

**Rules for `commands/herd.md`:**
- **Confined.** `HerdrConfinementTest` scans every line: no `herdr <subcommand>`, no `HERDR_`, no
  `herdr-app`, no `hc`, no `HC_*`, no `space.close` or other `<space|tab|pane|agent>.<action>`, no
  `AskUserQuestion`. Write "closes the space or workspace", never the app action name. `git`
  commands are allowed.
- No restated rules (C11): the herd-ID pattern, the busy and own-location skips, the force rule and
  the branch rule are named by section, not copied.
- Keep every pinned fragment (`test_herd_names_the_shared_operations_and_the_config_load`,
  `test_herd_names_each_agent_from_the_issue_title`, `test_herd_offers_no_watch_loop`), including
  "the Herdr sidebar shows `blocked` and `done` per pane" verbatim. `--resume` stays absent.

TDD is on: write the tests first and watch them fail.

### 1. Tests first, in `tests/test_herd.py`
- **Loosen the ban.** In `test_herd_drops_the_superseded_keys_and_tools`, drop `"herd record"` from
  the tuple and keep `"--resume"`, with a comment: #31 banned a *resume* record (its D12); #37's
  record is for cleanup only. **Not red-first** (removing a ban cannot fail first); say so in the
  commit's task notes.
- `test_herd_cleanup_mode`, fragments on `normalized(self.herd_text())`, one `subTest` each:
  `` `--cleanup` ``, `` `/jdi:herd --cleanup <herd-id>` ``, `*The herd record*`,
  `*Cleanup from the herd record*`, `asks once`, `Never guess from folder names`,
  `never names or resumes a session`, `cleanup never stops on H1's answer`.
- `test_argument_hint_names_cleanup`: `jdi_files.frontmatter_scalars(jdi_files.split_frontmatter(text)[0])["argument-hint"]`
  contains `--cleanup [<herd-id>]`.
- `test_step_eleven_points_at_cleanup`: the paragraph from
  `jdi_files.paragraph_starting_with(text, "11. **Say how to clean up")`, joined and normalized,
  contains `` `/jdi:herd --cleanup <herd-id>` ``. That helper stops at the first blank line, so the
  pointer goes in step 11's **first** paragraph.
- `test_prep_leaves_the_scratch_branch_behind`: the normalized text contains
  `leaves the scratch branch behind`, and does not contain `` `/jdi:prep` renames the branch ``.

### 2. Edits to `commands/herd.md`
- **Frontmatter.** `description` gains a cleanup clause (keep it one quoted line, e.g.
  `"Prep several issues in parallel - one Herdr worktree, pane, and agent for each - or clean a herd up from its record."`).
  `argument-hint: "<issue-id> [<issue-id> ...] [--kind <kind>] | --cleanup [<herd-id>]"`.
- **After the `$ARGUMENTS` paragraph** (the one ending "The user asked for: $ARGUMENTS"): with
  `--cleanup`, perform step 1, then *Clean up a herd from its record* below, instead of steps 2–11.
- **Step 5.** Where the herd ID is taken: the herd's record is
  `<git-common-dir>/jdi/herds/<herd-id>.json` (*The herd record*); if a record with that ID already
  exists, take a new herd ID.
- **Steps 6, 7, 8**, one sentence each on what H9 records: step 6, H9 starts the record at the first
  successful worktree and adds each issue's entry; step 7, a seeded worktree is recorded as seeded;
  step 8, on the app the space and terminal are recorded once opened.
- **Step 10.** Print the record path. Replace the sentence "Say that `/jdi:prep` renames the branch
  to one naming the issue, so `git worktree list` finds it later." with one saying that `/jdi:prep`
  leaves the scratch branch behind at its base and works on a branch of its own, and that the
  record, not the branch name, is how cleanup finds the worktree.
- **Step 11 (C8).** In its first paragraph, name `` `/jdi:herd --cleanup <herd-id>` `` as the way to
  clean this herd up later. Keep the manual commands, the plan guard and "Remove nothing yourself
  unless the user asks."
- **New `## Clean up a herd from its record`**, placed before `## Limits worth stating in the
  report`, as numbered steps that call the reference by name:
  1. Load the config (step 1).
  2. Parse the arguments and validate the herd ID as *Cleanup from the herd record* says (C2).
     Issue IDs or `--kind` alongside `--cleanup` stop the run with one sentence naming the two
     modes.
  3. Perform **H1** only to learn which Herdr surface is reachable from here; cleanup never stops
     on H1's answer.
  4. Find the records as *The herd record* and *Cleanup from the herd record* say. Never guess from
     folder names; with no record, say so and point at `git worktree list` and step 11's commands.
  5. Sort the entries (skips, plan files, force) as *Cleanup from the herd record* says.
  6. Show one list and ask once; an entry with uncommitted plan files gets its own question.
  7. Remove, closing the space or workspace first, as *Cleanup from the herd record* says.
  8. Report per issue: removed, or skipped and why, and the record's state (C7).

  Say that cleanup reads only the record: it never names or resumes a session.

## Files
- `commands/herd.md`
- `tests/test_herd.py`

## Verification
Run from the repository root.

1. **Red first.** After writing the tests and before editing the command: `python3 -m unittest discover -s tests -p 'test_herd.py' -v` — expected: `Ran 21 tests`, `FAILED`; `test_herd_cleanup_mode`, `test_argument_hint_names_cleanup`, `test_step_eleven_points_at_cleanup` and `test_prep_leaves_the_scratch_branch_behind` fail; the other 17 pass (the loosened ban passes before and after).
   red when: a new test passes before the edit, or an existing one fails.
   at base: `Ran 17 tests`, `OK`.
2. **Green.** The same command after the edit — expected: `Ran 21 tests`, `OK`. If Task 14 is still running, a `test_h9*` failure belongs to it (it edits `reference/herdr.md`, which those read); rerun once it is done.
   red when: any test outside `test_h9*` fails.
   at base: none — written by this task.
3. **The step-11 test bites.** In `commands/herd.md`, the file that defines step 11, delete the `/jdi:herd --cleanup <herd-id>` pointer from step 11's first paragraph — expected: `test_step_eleven_points_at_cleanup` fails. Restore it.
   red when: the module stays green.
4. **Confined.** `python3 -m unittest discover -s tests -p 'test_delegation_transport.py' -k HerdrConfinementTest -v` — expected: `Ran 2 tests`, `OK`. Then write `space.close` into the new cleanup section, rerun — expected: `test_no_herdr_command_variable_or_question_tool_outside_the_reference` fails; remove it.
   red when: an app or TUI command name was written into `commands/herd.md`, or the mutation passes.
   at base: `Ran 2 tests`, `OK`.
5. **The stale sentence is gone.** `grep -c 'renames the branch' commands/herd.md` — expected: `0`.
   red when: `1` (step 10 still says prep renames the scratch branch).
   control: `git show cdd14046784af5ef7e58fe612067f17a2e5b60df:commands/herd.md | grep -c 'renames the branch'` prints `1`.
   at base: `1`.
6. **Frontmatter still parses everywhere.** `python3 -m unittest discover -s tests -p 'test_frontmatter.py' -v` and `python3 -m unittest discover -s tests -p 'test_opencode_sync.py' -v` — expected: `Ran 6 tests`, `OK` and `Ran 4 tests`, `OK` (the `|` inside the quoted `argument-hint` is not a block scalar).
   red when: either fails.
   at base: `Ran 6 tests`, `OK`; `Ran 4 tests`, `OK`.
7. **Full suite.** `python3 -m unittest discover -s tests -v` — expected: every test passes, except failures that belong to a sibling still running: `tests/test_herd_record.py` and `test_h9*` in `tests/test_herd.py` (Task 14), `HerdCleanupDocumentationTest` in `tests/test_transport_docs.py` (Task 16), `tests/test_herdr_surfaces_doc.py` (Task 17).
   red when: a failure in a non-`test_h9` method of `tests/test_herd.py`, in `tests/test_delegation_transport.py`, or in any file no sibling owns.
   at base: `Ran 195 tests`, `OK` before Wave 8; Task 13 adds 5.
