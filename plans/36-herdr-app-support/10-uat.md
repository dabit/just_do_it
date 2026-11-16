status: done
# 10 — UAT: JDI under the Herdr app, the Herdr TUI, and neither

Depends on: 01, 02, 03, 04, 05, 06, 07, 08, 09

## Why
Every clause of issue #36's goal must be observed working in a real Herdr app before the pull request:
- detection with an override;
- routing of every Herdr operation;
- app worktrees in the dialog's layout;
- respect for the session;
- an unchanged TUI path.

The scenarios run end to end in a throwaway session, so the user's own app and core are never touched. Rests on: D1, D-wt, D-struct, P7, P11.

## Description
This folds in Planner's Task 10. It is an agent smoke test in a throwaway session, plus two short
scenarios only the user can walk in their own windows. **UAT is walked before `/jdi:pr`.** Nothing
here merges or pushes.

Record every scenario's observed result in a new `## UAT log` section in PLAN.md, placed above
`## Tasks`, with one entry per scenario id. Sanitise it the way Task 02's probe log is sanitised:
`$HOME` becomes `~`, the scratch path becomes `<scratch>`, and no session, machine or user name
appears.

Risk R1 applies in full. **Every command that addresses Herdr goes through the isolation guard.**
If a window cannot be opened, hand the agent scenarios to the user.

### Harness (Appendix B)
1. **Recreate the isolation guard from Task 02** in your scratch directory:
   - It refuses, on stderr with a non-zero exit, unless `JDI_PROBE_SESSION` and `JDI_PROBE_HOME`
     are set. It writes nothing to stdout.
   - It runs `unset HC_TERMINAL_ID HC_TERMINAL_SOCKET HC_SCOPE HC_SOCKET HERDR_ENV HERDR_SOCKET_PATH HERDR_PANE_ID HERDR_TAB_ID HERDR_WORKSPACE_ID`.
   - It runs `export HC_SESSION=$JDI_PROBE_SESSION HERDR_APP_HOME=$JDI_PROBE_HOME`, then
     `exec "$@"`.
   - Apply the XDG finding from the probe log.
2. **Set up the scratch environment:**
   - Record the **count** of the user's own `hc ls --json` entries. This is read-only, outside the
     wrapper.
   - Clone the repo into scratch, with a local `origin`.
   - Create a throwaway home whose `settings.json` is `{"worktrees":{"directory":"<scratch>/worktrees"}}`.
   - Name the session `jdiprobe-<4 hex>`.
   - Through the wrapper, `herdr-app status` must fail and `hc ls --json` must be empty.
   - Start `herdr-app` in the background, and tell the user a window will appear.
3. **Configure the scratch clone.** `.jdi/config.local.yml` has `tracker: {name: none}`, a role on
   another CLI (for example `models.researcher.harness: opencode`, and Executors on the same), and
   the `delegation.transport` / `herdr.surface` each scenario names.
4. **Start the branch plugin** as `claude --plugin-dir <repo>`, launched as the argv of a throwaway
   `space.new` on the scratch clone. That is the "Butler" terminal. Drive it by sending prompts with
   `hc send` through the wrapper, and read it with `hc read`.

### Agent scenarios (throwaway session)
Each scenario lists its steps, then what is expected.

- **(a) Role delegation on the app.**
  - Steps: `transport: auto`, no `herdr` key. Run `/jdi:prep` on a small scratch task.
  - Expected:
    - No step-0 note.
    - A `JDI spawn` line is printed, and appears in the command's output.
    - One pane is split to the **right** of the Butler.
    - The worker runs in the worktree root: `foreground.cwd` in `hc get` equals the scratch clone's
      root.
    - The run directory's `manifest.json` carries `"herdr": {"surface": "app", …}` with
      `terminal_id`, and only env **keys**.
    - A valid `result.json` is accepted through H7.
    - The pane is gone from `herdr-app ls` afterwards.
- **(b) A wave on the app.**
  - Steps: a two-task wave whose Executors are on another CLI.
  - Expected:
    - A tab named `jdi-wave-<first run id>` opens.
    - The first worker is in the tab's root, and the second is split from it.
    - No more than 4 worker panes are open.
    - Each task is committed by its own paths.
    - The wave tab is closed afterwards.
- **(c) `/jdi:herd` on the app.**
  - Steps: run it with two issue IDs; with `tracker: none`, fallback names apply.
  - Expected:
    - Worktrees are at `<scratch>/worktrees/<repo>/<name>`, where `<repo>` is the scratch clone's
      name from `--git-common-dir`.
    - Branches are `jdi-herd-scratch-<herd-id>-<N>`, from `origin/<default>`.
    - Spaces are named `<SHORT-ID> <TITLE>`, and nest under the repository in the sidebar like a
      dialog-made worktree.
    - The space opens only after seeding.
    - Each agent receives its invocation as typed input, by `hc send` (`hc read` shows it). It does
      not arrive as a launch argument.
    - The report lists each space and terminal ID and the cleanup commands.
  - After the handoff, close the spaces. Do not run prep to completion.
- **(c2) Open and list.**
  - Steps: with one herd space closed and its worktree present, perform H9's reattach. Then
    reattach again, with the space open.
  - Expected:
    - The first reattach runs `space.new --folder <path>`; the second runs `space.select --id`.
    - `git worktree list --porcelain` lists both herd worktrees.
- **(c3) Remove.**
  - Steps: leave an uncommitted file in one worktree's plan folder, then follow the report's
    cleanup. Delete the file and clean up again.
  - Expected:
    - The first cleanup refuses that worktree and names the file.
    - With the file gone, `space.close` runs **before** `git worktree remove`, and the worktree and
      its space are gone.
- **(c4) `worktrees.directory` is honoured.**
  - Steps: set `settings.json` `worktrees.directory` to a second absolute scratch path and herd one
    issue. Then set it to the relative value `relative/dir` and herd again.
  - Expected:
    - The first worktree lands under the second path.
    - The relative value makes H9 fail with a reason that names the value, and the herd stops.
- **(d) `transport: native`.**
  - Steps: run `/jdi:prep` with a role on another CLI.
  - Expected:
    - No app CLI command and no `herdr` command runs.
    - Neither Herdr nor the transport is mentioned anywhere, summaries included.
- **(e) Pinned `tui` inside the app.**
  - Steps: `herdr.surface: tui`, run once with `transport: auto` and once with `transport: herdr`.
  - Expected:
    - Under `auto`: silent `native`, and no app command.
    - Under `herdr`: exactly one note, "Herdr (tui) is not usable here: …", then `native`. Never the
      app, because a pinned surface never falls to the other.
- **(f) Invalid value.**
  - Steps: `herdr.surface: bogus` with `transport: auto`.
  - Expected: exactly one note naming the value, then behaviour identical to (a).
- **(g) Outside any Herdr (`none`), with a named session set.**
  - Steps: run the Butler in a plain shell through the wrapper. `HC_SESSION` and `HERDR_APP_HOME`
    are set by the wrapper; `HC_TERMINAL_ID` and `HERDR_ENV` are unset. Use `transport: auto`.
  - Expected:
    - Silent `native`.
    - **No `hc` command runs**, because app check (a) fails first.
    - The throwaway `hc ls --json` count is unchanged, so no core was auto-started.
  - Then run with `herdr.surface: app` and `transport: herdr`. Expected: one note,
    "Herdr (app) is not usable here: …", then `native`, and no `herdr` TUI command.
- **(h) The TUI path, nested.**
  - Steps: in a throwaway space, start a throwaway TUI with `herdr --session <throwaway>`, and run
    the Butler inside a TUI pane with `transport: auto`.
  - Expected:
    - The innermost surface wins: H1 answers `tui`.
    - The worker opens through `herdr pane split` and `herdr agent start`, exactly as in 1.0.10.
    - Its manifest has `"surface": "tui"`, and it completes through H7.
    - Its pane is closed.

### User-walked scenarios (before the PR, in the user's own windows)
Real acceptance stays with the user, as in #31's Task 10. The agent must never run these.
- **(u1) The default app window, with no named session.** In the user's normal window, where neither
  `HC_SESSION` nor `HERDR_APP_HOME` is set, the user runs scenario (a) once.
  - Expected: it behaves as in (a). Worktrees for a herd would use `~/.herdr/worktrees`, or their
    own `worktrees.directory`.
- **(u2) An existing TUI user.** In the user's own Herdr TUI, with `transport: auto` and no `herdr`
  key, the user runs one delegated role.
  - Expected: exactly the 1.0.10 behaviour.

The UAT is done when (u1) and (u2) are recorded in `## UAT log`. If the user explicitly defers
either one, record it as *deferred by the user*, and carry it into the PR description's test plan
as unobserved.

### Cleanup (Appendix B)
1. Close every space and tab created.
2. Quit the throwaway window through the wrapper (confirm `app.quit` scope first).
3. Run `hc server stop`, **through the wrapper only**.
4. Stop the throwaway TUI with `herdr --session <throwaway> server stop`.
5. Run `git worktree prune` in scratch, then remove scratch.
6. Confirm the user's `hc ls --json` count is unchanged.

### Issue #36 clause map
Each clause is listed with the scenario or test that proves it.

| Clause | Proven by |
|---|---|
| **Detect** app vs TUI vs none | `test_choosing_the_surface`, `test_h1_app_checks_in_order` (Task 03); scenarios (a) app, (h) TUI, (g) none |
| … with a config override | `HerdrBlockTest` (Task 01); scenarios (e) pinned `tui`, (g) pinned `app`, (f) invalid value; `test_transport_docs` (Task 04) for init/help/README offering it |
| **Route** role delegation through the detected surface | `test_h2_app` … `test_h8_app` (Task 06); `StepZeroTransportTest`, `TransportSelectionTest` (Task 07); scenario (a) |
| **Route** waves | `test_waves_app` (Task 06); scenario (b) |
| **Route** `/jdi:herd`'s one-worktree-per-issue | `test_h9_app_*`, herd fragments (Task 08); scenario (c) |
| **App worktrees**: create, in the dialog's layout | `test_h9_app_folder_matches_the_app_dialog`, `test_h9_app_branches_from_the_default_branch`; scenario (c); probes A8/A9 (Task 02) |
| … open | `test_h9_app_reattach_and_list`; scenario (c2) |
| … list | `test_h9_app_reattach_and_list`; scenario (c2) |
| … remove | `test_h9_app_cleanup_order`; scenario (c3) |
| … honour `worktrees.directory` | `test_h9_app_folder_matches_the_app_dialog`; scenarios (c), (c4) |
| … spaces nest under their repo like dialog-made ones | scenario (c), sidebar comparison; probe A9 |
| **Sessions**: never hardcode or set `HC_SESSION`, `HERDR_APP_HOME`, a home or a path | `test_no_personal_values`, `test_surfaces_section` "Inherit, never set" (Task 03); `test_herdr_surfaces_doc` no `/home/` (Task 05); scan 2 below |
| … works with them set | every agent scenario runs under a named session and app home; (g) with no terminal |
| … works without them | (u1), user-walked; the mechanism is `${HERDR_APP_HOME:-~/.config/herdr-app}` and the `~/.herdr/worktrees` default (`test_h9_app_folder_matches_the_app_dialog`) |
| **TUI path unchanged** (must not break) | every pre-existing test in `tests/test_herdr_operations.py` and `tests/test_herd.py` passes unmodified (scan 1 below); scenario (h); (u2), user-walked |
| `native` stays silent (must not break) | `test_h1_native_runs_no_herdr_command`; scenario (d) |
| Out of scope: no Herdr changes, no remote machines | nothing to prove. No task edits Herdr or adds `--on` or `--machine` |

### Repository scans (run from the repository root)
1. **TUI assertions only grew.** Run
   `git diff --numstat b06fbdbfc5ffa48fc2dff3633497e401b5254c19 -- tests/test_herdr_operations.py tests/test_herd.py`.
   Expected: `0` in the deletions column for both files. Any deletion must be shown not to weaken a
   TUI assertion.
2. **No hardcoded session, home or personal path was added.** Run
   `git diff b06fbdbfc5ffa48fc2dff3633497e401b5254c19 -- . ':!plans' | grep -E '^\+' | grep -nE 'HC_SESSION=|HC_SOCKET=|HERDR_APP_HOME=|/home/|/Users/|jdiprobe'`.
   Expected: no output.
3. **App names are confined.** Run
   `grep -rnE '\bherdr-app\b|\bhc\b|\bHC_[A-Z]|\b(space|tab|pane|agent)\.(new|split|close|select|focus)\b' commands agents roles reference skills/run/SKILL.md | grep -v '^reference/herdr.md:'`.
   Expected: no output.
4. **Full suite.** Run `python3 -m unittest discover -s tests -v`. Expected: every test passes.

### After the merge: deferred, and not part of marking this task done
- **The release reaches installed copies.** `claude plugin update` picks up 1.0.11 only once the
  stack is merged to the branch the marketplace serves. Observe it when #31 and this PR land. The
  version match itself is proven now by `VersionTest`.
- **R9, renumbering.** `origin/main` has its own 1.0.10–1.0.12. When #31 and this PR are rebased onto
  main, both versions are renumbered, and `/jdi:do` (1.0.12 on main) gains the step-0
  `herdr.surface` sentence if it delegates. `/jdi:pr` records this as a follow-up in the PR
  description.

## Files
None in the repository. The UAT log goes into this plan folder's `PLAN.md` (`## UAT log`), which the
Butler commits. The wrapper, scratch clone and throwaway home live in the Executor's scratch
directory and are removed at cleanup.

## Verification
1. **The log is complete.** Run
   `sed -n '/^## UAT log/,/^## Tasks/p' plans/36-herdr-app-support/PLAN.md | grep -oE '\((a|b|c|c2|c3|c4|d|e|f|g|h|u1|u2)\)' | sort -u | wc -l`.
   Expected: `13`. Every recorded result matches its expected outcome, or carries an explanation and
   a decision from the user.
2. **Sanitised.** Run
   `sed -n '/^## UAT log/,/^## Tasks/p' plans/36-herdr-app-support/PLAN.md | grep -nE '/home/|/Users/|jdiprobe-[0-9a-f]{4}'`.
   Expected: no output.
3. **Repository scans 1–4 above** each give their stated result.
4. **Isolation held.** The user's own `hc ls --json` count equals the count recorded at setup.
   Through the wrapper, `herdr-app status` fails, because the throwaway core is stopped.
   `git -C <repo root> worktree list` shows no worktree added by the UAT.
5. **Every row of the clause map** names a scenario or test whose result is recorded as passing, or,
   for (u1) and (u2) only, as explicitly deferred by the user.
