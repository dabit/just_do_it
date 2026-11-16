status: done
# 08 — H9 on the app (worktree create, open, list, remove) and `/jdi:herd` on either surface

Depends on: 06

## Why
The Herdr app has no worktree CLI, so `/jdi:herd`'s one-worktree-per-issue needs a documented recipe that matches what the app's own dialog does:
- the folder is `<worktrees.directory>/<repo>/<name>`;
- the space is opened only after seeding;
- work is handed off by `hc send`, never `--task`;
- removal runs plan-file guard, then `space.close`, then `git worktree remove`.

`commands/herd.md` must name either surface without naming any app command. Rests on: D-wt, D-struct, D6, P5, P9.

## Description
This is Planner's Task 5 plus the `commands/herd.md` part of Planner's Task 6. Both edit
`tests/test_herd.py`, and the herd command describes H9's surface split, so they are one task. That
removes a sequential link from the critical path; see PLAN.md `## Tasks`.

This task depends on Task 06 because both edit `reference/herdr.md`, and H9 on the app calls
`#### H4b on the app`, which Task 06 writes.

**Before starting, read `## Probe log` in PLAN.md.** These probes bear on this task:
- A8: the herd path and nesting;
- A9: whether only git decides nesting;
- A16: the `parent` field;
- A17: `--name` quoting.

An amendment there wins over this file.

**Rules for `reference/herdr.md`:**
- No em dash.
- Inside an indented fence, no line starts with `#` at column 0.
- No `/home/`, `/Users/`, `HC_SESSION=` or `HERDR_APP_HOME=` (Task 03's `test_no_personal_values`).
  The `${HERDR_APP_HOME:-~/.config/herdr-app}` default form is allowed.
- The existing H9 text (`## H9 - Give a Butler its own worktree`) stays unchanged. The app variant
  is appended under it.

**Rules for `commands/herd.md`:**
- It is confined: it may name no app binary, `HC_*` variable or app command.
- Keep "the Herdr sidebar shows `blocked` and `done` per pane" verbatim.

TDD is on: write the tests first and watch them fail.

### 1. Tests first, in `tests/test_herd.py`
- Add the constant `H9_APP_HEADING = "### H9 on the app"`, and a helper:
  ```python
  def h9_app_lines(self):
      return jdi_files.section(jdi_files.read(HERDR_REFERENCE), H9_APP_HEADING)
  ```
- **New methods** on `normalized("\n".join(self.h9_app_lines()))`:
  - `test_h9_app_folder_matches_the_app_dialog`: `${HERDR_APP_HOME:-~/.config/herdr-app}/settings.json`,
    `worktrees.directory`, `~/.herdr/worktrees`, `--git-common-dir`, `<worktrees dir>/<repo>/<name>`.
  - `test_h9_app_branches_from_the_default_branch`:
    `git worktree add -b jdi-herd-scratch-<herd-id>-<N> <path> origin/<default>`.
  - `test_h9_app_opens_the_space_after_seeding`: `herdr-app do space.new --name`,
    `--folder <path> --tab <name>`, `--focus false`, "after `herd.seed`".
  - `test_h9_app_hands_off_by_send`: `hc wait <terminal> --timeout 120`, `status: idle`,
    `hc send <terminal> "<invocation>" --if idle`, "Never `--task`", "blocked at startup".
  - `test_h9_app_cleanup_order`: these appear with strictly increasing `index`:
    `git -C <worktree> status --porcelain -- <plans.path>`, then
    `herdr-app do space.close --id <space> --confirmed true`, then `worktree remove`.
  - `test_h9_app_reattach_and_list`: `herdr-app do space.select --id <space>`,
    `git worktree list --porcelain`.
- **Herd fragments.** Append to the tuple in `test_herd_names_the_shared_operations_and_the_config_load`:
  "`herd`, `herdr`, `harnesses`", "H1 settles which Herdr", "On the app, the space is opened in
  step 8".
- **Existing tests.** `h9_lines()` reads all of `## H9`, which now includes the app subsection. The
  existing negative checks stay as they are and must keep passing:
  - `test_h9_drops_the_collision_prone_scratch_branch` forbids `--branch jdi-herd-scratch-<N> `.
    The app's `-b jdi-herd-scratch-<herd-id>-<N>` does not match it.
  - `test_h9_uses_the_title_name_suffix_match_and_title_label` forbids
    `--path <worktrees dir>/<repo>/jdi-herd-<issue>`.

### 2. `reference/herdr.md`: append `### H9 on the app` inside `## H9`
- **Shared with the TUI:** the kind and name rules, and the suffix check.
- **Folder.** Read `worktrees.directory` from the app's `${HERDR_APP_HOME:-~/.config/herdr-app}/settings.json`.
  - The default is `~/.herdr/worktrees`.
  - A leading `~` becomes `$HOME`. Any other relative value fails H9 with its reason.
  - Drop a trailing `/`.
  - The app does not read the TUI's `config.toml`.
- **`<repo>`.** The basename of `git rev-parse --path-format=absolute --git-common-dir`, with
  `/.git` removed. The path is `<worktrees dir>/<repo>/<name>`.
- **Create** returns the path only (P5):
  `git worktree add -b jdi-herd-scratch-<herd-id>-<N> <path> origin/<default>`.
- **At herd step 8**, after `herd.seed` (step 7), open the space:
  `herdr-app do space.new --name '<SHORT-ID> <TITLE>' --folder <path> --tab <name> --argv '<argv>' --focus false`.
  - The argv is the env prefix plus the kind's absolute path. No model flag, and no `sh` wrapper,
    because `--folder` sets the folder.
  - The output is `{space, tab, terminal}`. Read the pane from `herdr-app ls`.
  - Single-quote the name so `'`, `$` and backticks arrive literally (A17).
  - The tab is named at creation.
  - The Butler is not the herd session's parent (A8 checks `parent`).
  - Then perform `#### H4b on the app`.
- **Handoff** (D6, amended after the probe gate): `hc wait <terminal> --timeout 120`; only when it
  reports `status: idle`, `hc send <terminal> "<invocation>" --if idle`, without `--wait`. If it does
  not reach `status: idle` (a new worktree always shows Claude's or Codex's trust dialog, which
  reports no status), type nothing: report that issue as blocked at startup, leave its space open,
  and tell the user to answer the dialog there (D7). The invocation table is shared. "Never `--task`": it arrives as a launch
  argument, not typed input.
- **Watch** with `hc get` and `hc read --lines 80`.
- **Reattach (open).** Look in `herdr-app ls` for a space whose `folder` is inside the path. If
  there is one, `herdr-app do space.select --id <space>`; otherwise
  `space.new --folder <path> --focus false`.
- **Cleanup (remove)**, in this order:
  1. the plan-file check, `git -C <worktree> status --porcelain -- <plans.path>`;
  2. `herdr-app do space.close --id <space> --confirmed true`;
  3. `git -C <main checkout> worktree remove [--force] <path>`.

  Never `hc kill` or `hc rm` (P9).
- **List:** `git worktree list --porcelain`.

### 3. `commands/herd.md` (surface-neutral, no app commands)
- **Step 1.** The block list becomes "`herd`, `herdr`, `harnesses`, `git`, `tracker` and `plans`".
- **Step 2.** Add "H1 settles which Herdr (`herdr.surface`)".
- **Step 6.**
  - Add "H9 returns the worktree path, and on the TUI also the workspace, tab and root pane. On the
    app, the space is opened in step 8, after seeding."
  - Where step 6 describes the extra pane needed for `harnesses.<kind>.env`, add "H9 says what the
    environment needs on the surface in use".
- **Step 8.** "blocked at startup (on the TUI, `agent_not_ready`)".
- **Step 9.** "a blocked result (on the TUI, `agent_blocked`)".
- **Step 10.**
  - The row lists "pane or terminal ID, workspace (space on the app)".
  - Keep the pinned sentence "the Herdr sidebar shows `blocked` and `done` per pane", and add "the
    app also rolls it up per space and tab".

## Files
- `tests/test_herd.py`
- `reference/herdr.md`
- `commands/herd.md`

## Verification
1. **Red first.** Run `python3 -m unittest discover -s tests -p 'test_herd.py' -v` before editing the
   docs. Expected:
   - the six new `test_h9_app_*` methods error, with "heading '### H9 on the app' not found";
   - `test_herd_names_the_shared_operations_and_the_config_load` fails on the three new fragments;
   - every other test passes.
2. **Green.** Run the same command after the edits. Expected: every test passes, including
   `test_h9_names_the_worktree_commands_and_paths`, `test_herd_offers_no_watch_loop` and
   `test_h9_drops_the_collision_prone_scratch_branch`.
3. **The test bites.** In `### H9 on the app` in `reference/herdr.md`, the recipe that defines the
   cleanup order, move the `space.close` line after the `worktree remove` line. Run the module.
   Expected: `test_h9_app_cleanup_order` fails. Restore the order, and confirm with
   `git diff -- reference/herdr.md`.
4. **The reference's guards still hold.** Run `python3 -m unittest discover -s tests -p 'test_herdr_operations.py' -v`.
   Expected: every test passes, including `test_no_personal_values` and `test_no_em_dash`.
5. **`commands/herd.md` stays confined.** Run
   `python3 -m unittest discover -s tests -p 'test_delegation_transport.py' -k HerdrConfinementTest -v`.
   Expected: every test passes.
6. **The existing H9 text is unchanged.** Run
   `git diff -U0 -- reference/herdr.md | grep -E '^-[^-]'`. Expected: no output, because this task
   only adds lines to `reference/herdr.md`.
7. **Full suite.** Run `python3 -m unittest discover -s tests -v`. Expected: every test passes, with
   one exception: if Task 07 is still running, failures in `tests/test_step_zero_transport.py` or in
   `TransportSelectionTest` in `tests/test_delegation_transport.py` belong to it.
