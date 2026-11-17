status: done
# 18 — UAT: `/jdi:herd --cleanup` from the herd record (agent smoke test)

Depends on: 12, 13, 14, 15, 16, 17, 19

## Why
Every clause of issue #37 must be observed in a running Herdr before the pull request: a herd writes its record, and `/jdi:herd --cleanup` reads it instead of guessing from names, skips busy agents, guards the plan, asks once, closes then removes (app: space first), deletes only a commit-less scratch branch and never a feature branch, keeps the record up to date, and reports, on both surfaces. It runs as an agent smoke test in a throwaway session so the user's own app, core and repository are never touched; real acceptance stays with the user. Rests on: C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11.

## Description
Planner's Task 18. An agent smoke test in a throwaway app session, plus one scenario only the user
can walk. **UAT is walked before `/jdi:pr`.** Nothing here merges or pushes.

Record every scenario's observed result in a new `## UAT log (#37)` section in PLAN.md, placed
directly above `## Tasks` (below `## Probe log (#37)`), one entry per scenario id. Sanitise it as
Task 12's log: `$HOME` becomes `~`, the scratch path `<scratch>`, no session, machine or user name.

**Read `## Probe log (#37)` first.** Its amendments decide the TUI removal and the app busy check
that (b), (e) and (j) observe.

Risk R1 applies in full: **every command that addresses Herdr goes through the isolation guard**.
If a window cannot be opened, hand the scenarios to the user. No Codex (so `~/.codex/config.toml` is
not touched).

### Harness (Appendix B, as in Tasks 10 and 12)
1. **The guard** `<scratch>/g`, POSIX `sh`: refuses with exit 64, a stderr line and no stdout unless
   `JDI_PROBE_SESSION` and `JDI_PROBE_HOME` are set and the session matches `jdiprobe-*`; runs
   `unset HC_TERMINAL_ID HC_TERMINAL_SOCKET HC_SCOPE HC_SOCKET HERDR_ENV HERDR_SOCKET_PATH HERDR_PANE_ID HERDR_TAB_ID HERDR_WORKSPACE_ID`
   and the driver's Claude variables (`CLAUDECODE`, `CLAUDE_CODE_*`, `CLAUDE_PID`,
   `CLAUDE_EFFORT`); `export HC_SESSION=$JDI_PROBE_SESSION HERDR_APP_HOME=$JDI_PROBE_HOME`;
   `exec "$@"`. XDG is not overridden.
2. **Setup.** Record the **count** of the user's own `hc ls --json` entries and of the real
   repository's `git worktree list` lines (read-only, outside the guard). Clone the repo into
   `<scratch>/repo` with a bare local `origin` whose `main` is this branch's HEAD. Back up
   `~/.claude.json` and pre-trust only `<scratch>/repo`. Throwaway home with `settings.json` =
   `{"worktrees":{"directory":"<scratch>/worktrees"}}`; session `jdiprobe-<4 hex>`. Through the
   guard, `herdr-app status` fails and `hc ls --json` is empty; then start `herdr-app` in the
   background (tell the user a window will appear) and close its welcome overlay.
3. **Clone config.** `.jdi/config.local.yml`: `tracker: {name: none}` (herd names fall back to
   `jdi-herd-<issue>`), `jev.enabled: false`, `tdd.enabled: false`, `herd.kind: claude`.
4. **The Butler.** `claude --plugin-dir <this repo> --settings '{"enabledPlugins":{"jdi@just-do-it":false}}'`,
   the argv of a throwaway `space.new` on `<scratch>/repo`. Drive it with `hc send` and read it
   with `hc read`, through the guard. Evidence: the Butler's transcript (every command it ran),
   `herdr-app ls`, `hc get`, the record files, `git -C <scratch>/repo worktree list --porcelain`
   and `git -C <scratch>/repo branch --list`.
5. **Herd agents.** After each handoff the driver (not JDI) stops every herd agent a scenario does
   not need busy, so its state is idle or finished, and answers no herd dialog on JDI's behalf.

### Agent scenarios (throwaway session), walked in the order listed
- **(a) Herd and record.** `/jdi:herd 201 202 203` on the app.
  - Expected: `<scratch>/repo/.git/jdi/herds/<herd-id>.json` exists, is valid JSON with Appendix C's
    keys, `surface: app`, three entries whose `worktree` matches `git worktree list --porcelain`,
    `base_commit` equal to each worktree's first HEAD, the app IDs (`space_id`, `terminal_id`, ...)
    filled after step 8, `workspace_id: null`, and `state: handed_off`. The record is under the git
    directory, so `git -C <scratch>/repo ls-files` cannot list it. The step-11 report names
    `/jdi:herd --cleanup <herd-id>` and still lists the manual commands.
  - Then create a **decoy**: `git -C <scratch>/repo worktree add <scratch>/worktrees/repo/decoy-201 -b decoy-201 origin/main`
    (a non-herd worktree ending in the same suffix). It must survive every cleanup below.
- **(b) Busy.** The driver sends 202's agent a long prompt (a long count), then runs
  `/jdi:herd --cleanup <herd-id>` in the Butler and answers no at the question.
  - Expected: 202 is skipped as `working`, before the list; the list holds no 202 entry.
- **(c) Plan guard.** Leave an uncommitted `plans/x/NOTE.md` in 201's worktree. Run the cleanup.
  - Expected: 201 leaves the batch and gets its own question, with the plan commit offered; answer
    no. Nothing of 201 is touched: its space, worktree, branch and record entry remain.
- **(h) Own location.** With all three entries still present, the driver opens a second Butler in
  201's worktree (H9's reattach), runs `/jdi:herd --cleanup <herd-id>` there, and answers no.
  - Expected: 201 is skipped as the location of the session running the cleanup; the other
    entries are listed. Close that Butler before (d).
- **(d) Branches.** In 203's worktree, `git switch -c feat-203` and one commit. In 202's worktree
  (its agent stopped after (b)), one commit **on its scratch branch**. Remove 201's `NOTE.md`. Run
  the cleanup and answer yes.
  - Expected: 203's space is closed **before** its worktree is removed (the Butler's transcript
    order), `feat-203` still exists, and `jdi-herd-scratch-<herd-id>-3` is deleted. 202's worktree
    is removed and its scratch branch is **kept** (it has a commit of its own). 201 is removed and
    its scratch branch deleted. No other branch is deleted.
- **(e) Upkeep.** After each run, read the record.
  - Expected: an entry disappears once its worktree is gone from `git worktree list --porcelain`;
    the file is deleted with the last entry; a rerun of `/jdi:herd --cleanup <herd-id>` says there
    is no record and removes nothing. The decoy worktree and `decoy-201` still exist.
- **(f) No record.** In a fresh scratch clone with no herds, `/jdi:herd --cleanup`.
  - Expected: the C6 message (no record; points at `git worktree list` and step 11's commands), and
    nothing removed.
- **(g) Bad ID.** `/jdi:herd --cleanup ../x`.
  - Expected: refused for not matching `^[0-9]{8}T[0-9]{6}$`; no path is read or written. Also
    `/jdi:herd --cleanup 201` (an issue ID with `--cleanup`): stops with a sentence naming the two
    modes.
- **(i) Seeded.** A one-issue herd with `herd.seed.setup: ["touch untracked-seed.txt"]`.
  - Expected: the record has `seeded: true`; cleanup lists `untracked-seed.txt` before the single
    question and, on yes, removes the worktree with `--force`.
- **(k) A herd still `creating`** (*Splitter's addition, for C9*). Before (i)'s cleanup, the driver
  rewrites that record with `state: creating` (whole file, then `mv -f`).
  - Expected: `/jdi:herd --cleanup` without an ID skips it with "its herd may still be running;
    pass its herd ID to clean it anyway"; with its ID it is included and flagged. Then restore
    `handed_off` and finish (i).
- **(j) TUI, if cheap.** Start a throwaway nested TUI (`herdr --session <probe-session>`, as A10) in
  a throwaway space, and a Butler in a TUI pane; herd one issue there.
  - Expected: the record has `surface: tui`, `workspace_id`, `tab_id`, `pane_id`, `agent_name`
    filled at step 6, and app keys `null`. Cleanup from the **outer app** Butler reports the entry's
    surface as not reachable from here, skips the workspace close, and still offers the worktree
    marked "agent state unknown" (answer no). Cleanup from **inside the TUI** finds the workspace
    through `herdr worktree list` by path and removes it with the gated TUI removal; no branch but
    the commit-less scratch branch is deleted.
  - If skipped, record `(j) not run: <reason>`; the clause map then names Task 12's R1–R3 and
    `HerdCleanupFromRecordTest` as the only proof of the TUI side, and the user's (u3) carries it.

### User-walked scenario (before the PR, in the user's own window)
- **(u3) A real herd cleaned up.** After a real `/jdi:herd` in the user's own app (or TUI), the user
  runs the step-11 `/jdi:herd --cleanup <herd-id>` once agents finish.
  - Expected: one question, the finished worktrees and their spaces gone, feature branches kept.

This task closes as an agent smoke test. (u3) is recorded as pending or as deferred by the user,
carried into the PR description's test plan as unobserved, and asked again by `/jdi:pr`, as Task
10's (u1)/(u2) were.

### Cleanup (Appendix B)
1. Close every space and tab created; stop the nested TUI with
   `herdr --session <probe-session> server stop` through the guard.
2. Quit the throwaway window through the guard, then `hc server stop` through the guard only.
3. Remove the throwaway home, `~/.local/state/herdr-core/<probe-session>/`,
   `~/.config/herdr/sessions/<probe-session>/`,
   `~/.local/state/herdr-automatic-rename/sessions/<probe-session>/`; restore `~/.claude.json`.
4. `git worktree prune` in scratch, then remove `<scratch>`.
5. Confirm the user's `hc ls --json` count and the real `git worktree list` line count are
   unchanged.

### Issue #37 clause map
| Clause | Proven by |
|---|---|
| H9 writes a herd record when it creates a worktree | `test_record_write_points` (Task 13); scenario (a) |
| … at `$(git rev-parse --git-common-dir)/jdi/herds/<herd-id>.json` | `test_record_location_and_lifecycle` (`--path-format=absolute --git-common-dir`); scenario (a) |
| … per issue: worktree path, scratch branch, space/workspace ID, surface, when made | `test_record_shape_matches_appendix_c`; scenarios (a) app, (j) TUI |
| … never committed | `test_record_location_and_lifecycle` (`never committed`); scenario (a); scan 6 |
| … survives the branch switch | scenario (d) (`feat-203` entry still found by path and cleaned) |
| … same shape on both surfaces | `test_record_shape_matches_appendix_c` (one shape, `null` where a key does not apply); scenarios (a), (j) |
| `/jdi:herd --cleanup [<herd-id>]` exists | `test_herd_cleanup_mode`, `test_argument_hint_names_cleanup` (Task 15); `HerdCleanupDocumentationTest` (Task 16); scenarios (a)–(k) |
| … reads the records, never guesses from names | `test_selects_records_safely` (Task 14), `test_herd_cleanup_mode`; scenarios (e) decoy untouched, (f) no record |
| … skips an entry whose agent is still working | `test_skips`; scenario (b) |
| … runs the plan-file guard | `test_guards_and_force`, `test_removal_order` (re-check first); scenario (c) |
| … lists what will be removed and asks once | `test_guards_and_force` (`one list`, `asks once`), `test_herd_cleanup_mode`; scenarios (b)–(d), (i) |
| … closes the space/workspace, then removes the worktree (app: space first), per surface | `test_removal_order`; scenario (d) app; scenario (j) TUI, else Task 12's R2/R3 |
| … deletes the scratch branch only if it exists with no commits of its own | `test_scratch_branch_rule`; scenario (d) (203's deleted, 202's kept) |
| … never deletes a feature branch | `test_scratch_branch_rule` (`Never delete any other branch`); scenario (d) (`feat-203` kept); probe R2 |
| … removes the record entry once its worktree is gone | `test_record_upkeep`; scenario (e) |
| Report: removed, skipped and why | Task 14's report paragraph, read; scenarios (b), (c), (d), (e) reports. No test pins its wording. |
| Works on both surfaces | app: scenarios (a)–(k); TUI: scenario (j), or, if not run, Task 12's R1–R3 and `HerdCleanupFromRecordTest`, with (u3) deferred to the user |
| Part of the single Herdr PR, no new release | `VersionTest`; scan 5 (still 1.0.13) |
| Must not break: a normal herd | scenario (a) (handoff and report as before, plus the cleanup pointer); every pre-existing `tests/test_herd.py` test except the loosened ban passes (scan 2) |
| Must not break: the TUI H9 text | scan 1 (only additions to `reference/herdr.md`); `tests/test_herdr_operations.py` |
| Must not break: confinement | scan 4; `HerdrConfinementTest` |

### After the merge — deferred, and not part of marking this task done
- **The release reaches installed copies.** `claude plugin update` picks up 1.0.13 with the cleanup
  only once this PR is merged to the branch the marketplace serves. The version match is proven now
  by `VersionTest`.

## Files
None in the repository. The UAT log goes into this plan folder's `PLAN.md` (`## UAT log (#37)`),
which the Butler commits. The guard, scratch clones and throwaway home live in the Executor's
scratch directory and are removed at cleanup.

## Verification
Run from the repository root, after Tasks 12–17 are committed.

1. **The log is complete.** `awk '/^## UAT log \(#37\)$/{f=1;next} /^## /{f=0} f' plans/36-herdr-app-support/PLAN.md | grep -oE '\(([a-k]|u3)\)' | sort -u | wc -l` — expected: `12`, each result matching its expected outcome, or carrying an explanation and the user's decision; (j) may read `not run: <reason>` and (u3) `pending` or `deferred by the user`.
   red when: fewer than 12 (a scenario not recorded).
   at base: `0` (section absent).
2. **Sanitised.** `awk '/^## UAT log \(#37\)$/{f=1;next} /^## /{f=0} f' plans/36-herdr-app-support/PLAN.md | grep -nE '/home/|/Users/|jdiprobe-[0-9a-f]{4}'` — expected: no output.
   red when: a home path or the probe session name is printed.
   control: `grep -cE '/home/|/Users/|jdiprobe-[0-9a-f]{4}' plans/36-herdr-app-support/PLAN.md` prints a positive count (`4` at base).
   at base: no output.
3. **Scan 1, the H9 reference only grew.** `git diff cdd14046784af5ef7e58fe612067f17a2e5b60df HEAD -- reference/herdr.md | grep -E '^-[^-]'` — expected: no output (Tasks 13 and 14 only added lines).
   red when: a pre-existing H9 line was removed or re-wrapped.
   control: `git diff b06fbdbfc5ffa48fc2dff3633497e401b5254c19 HEAD -- reference/herdr.md | grep -cE '^-[^-]'` prints `18`.
   at base: no output.
4. **Scan 2, only the ban was loosened in `tests/test_herd.py`.** `git diff cdd14046784af5ef7e58fe612067f17a2e5b60df HEAD -- tests/test_herd.py | grep -E '^-[^-]'` — expected: only the line(s) of the ban tuple in `test_herd_drops_the_superseded_keys_and_tools` that held `"herd record"`.
   red when: any other removed line (a pre-existing assertion weakened).
   at base: no output.
5. **Scan 3, no personal value added.** `git diff cdd14046784af5ef7e58fe612067f17a2e5b60df HEAD -- . ':!plans' | grep -E '^\+' | grep -nE 'HC_SESSION=|HC_SOCKET=|HERDR_APP_HOME=|/home/|/Users/|jdiprobe'` — expected: no output.
   red when: a hardcoded session, home or path is printed.
   control: `git diff b06fbdbfc5ffa48fc2dff3633497e401b5254c19 HEAD -- . ':!plans' | grep -E '^\+' | grep -cE 'HC_SESSION=|HC_SOCKET=|HERDR_APP_HOME=|/home/|/Users/|jdiprobe'` prints a positive count (`3` at base: the tests that ban those values).
   at base: no output.
6. **Scan 4, app names confined.** `grep -rnE '\bherdr-app\b|\bhc\b|\bHC_[A-Z]|\b(space|tab|pane|agent)\.(new|split|close|select|focus)\b' commands agents roles reference skills/run/SKILL.md | grep -v '^reference/herdr.md:'` — expected: no output.
   red when: `commands/herd.md` or `commands/help.md` names an app command.
   control: `grep -cE '\bherdr-app\b|\bhc\b|\bHC_[A-Z]|\b(space|tab|pane|agent)\.(new|split|close|select|focus)\b' reference/herdr.md` prints `81` at base (more after Tasks 13–14).
   at base: no output.
7. **Scan 5, no version bump.** `grep -h '"version"' .claude-plugin/plugin.json .claude-plugin/marketplace.json .codex-plugin/plugin.json` — expected: three lines, each `1.0.13`.
   red when: a version moved.
   at base: three lines, `"version": "1.0.13"`.
8. **Scan 6, the record is never tracked.** `git ls-files | grep -c 'jdi/herds'` — expected: `0`.
   red when: a record path was committed.
   control: `printf '.git/jdi/herds/20261116T120000.json\n' | grep -c 'jdi/herds'` prints `1`.
   at base: `0`.
9. **Isolation held.** The user's own `hc ls --json` count and `git -C <repo root> worktree list | wc -l` equal the setup counts; through the guard, `herdr-app status` exits 2; `ls ~/.config/herdr/sessions/` lists no probe session.
   red when: a count changed or a probe session survives.
   at base: `git worktree list | wc -l` printed `1`; the `hc ls` count is taken at setup.
10. **Every clause map row** names a test whose result passes in step 11 and a scenario recorded as passing, or, for (j) and (u3) only, the stated fallback.
    red when: a row's scenario is missing from the log or recorded as failing without a user decision.
11. **The branch's gate.** The repository has no CI configuration (no `.github/` or other pipeline file), so the full suite is the gate the branch faces: `python3 -m unittest discover -s tests -v` — expected: `Ran 218 tests` (195 + 5 from Task 13, 7 from Task 14, 4 from Task 15, 3 from Task 16, 4 from Task 17, plus any a gate amendment added), `OK`.
    red when: any test fails or the count is lower.
    at base: `Ran 195 tests`, `OK`, no known reds.
