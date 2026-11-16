status: done
# 02 — Run the live Herdr app probes in a throwaway session (the probe gate)

Depends on: None

## Why
The app variants in later tasks rest on the Butler's defaults (D2–D10) and the Planner's facts (P1–P6). Those were read from the docs, not yet observed in a running app. This task observes them in an isolated throwaway session first, so no live app behaviour is guessed. Any contradiction stops the work until the plan is amended. Rests on: P11, D2, D3, D4, D5, D6, D7, D8, D9, D10, P1, P2, P3, P4, P5, P6.

## Description
Planner's Task 2. Run probes A1–A12 from `docs/herdr-surfaces-architecture.md`, `## App-side live
probes`, plus the new A13–A17 below. Run every one in a **throwaway** session and app home,
through the isolation guard. Record the sanitised results in this plan's `PLAN.md`, in a new
`## Probe log` section placed just above `## Tasks`.

**Ignore one sentence in the architecture doc.** That doc says probes run "in an app terminal of the
user's normal window". P11 supersedes it, and Task 05 removes it. Never probe the user's real
session or core.

**Risk R1, the highest in the plan.** An inherited `HC_TERMINAL_SOCKET` or `HC_TERMINAL_ID` can
route `hc` to the user's real core. So:
- The wrapper's `unset` is mandatory.
- Never run `hc server stop` or `herdr-app do app.quit` outside the wrapper.
- The probes spend agent tokens and open a visible window. If you cannot open a window, stop and
  hand this task to the user.

### Isolation guard (Appendix B)
Write the guard as a wrapper script in your scratch directory, never in the repository. Every probe
command goes through it.
- It refuses unless `JDI_PROBE_SESSION` and `JDI_PROBE_HOME` are both set. The refusal goes to
  **stderr** with a non-zero exit, and nothing goes to stdout. A probe's stdout is the JSON you
  parse, so the wrapper itself must never write to stdout.
- It runs `unset HC_TERMINAL_ID HC_TERMINAL_SOCKET HC_SCOPE HC_SOCKET HERDR_ENV HERDR_SOCKET_PATH HERDR_PANE_ID HERDR_TAB_ID HERDR_WORKSPACE_ID`.
  Without this, the inherited socket can address the user's real core.
- It runs `export HC_SESSION=$JDI_PROBE_SESSION HERDR_APP_HOME=$JDI_PROBE_HOME`.
- It ends with `exec "$@"`.
- **VERIFY-AT-EXECUTION.** The hc manual says tests need scratch XDG paths too. Check which XDG
  variables the core reads. If you override them, pass the agent CLIs their real config through
  the env prefix.

### Setup
1. Record the versions of `herdr`, `herdr-app` and `hc`. Also record the **count** (never the
   contents) of the user's `hc ls --json` entries. That read-only call runs outside the wrapper.
2. Clone the repo into scratch, with a local `origin`.
3. Create the throwaway home, with `settings.json` set to `{"worktrees":{"directory":"<scratch>/worktrees"}}`.
4. Name the session `jdiprobe-<4 hex>`.
5. Through the wrapper, check the throwaway session does not exist yet: `herdr-app status` must fail
   and `hc ls --json` must be empty.
6. Start `herdr-app` in the background. This is the only allowed bare launch. Tell the user a
   window will appear.
7. Run each "inside" probe as a script launched by `space.new` or `pane.split --argv`. The script
   writes its findings to scratch files.

### Probes
- **A1–A12**, exactly as listed in the architecture doc: `tab.new` output, readiness, status
  reporting, send and wait, timeouts, environment, close, the herd path, nesting, the nested
  surface, no window, and the worker's writes.
- **Additions to those:**
  - A2/A3: record whether each kind reports status through the `sh -c 'cd -- "$1" && shift && exec "$@"'` wrapper.
  - A7: record the exact "already gone" error JSON.
  - A11: record the no-window output, and whether `window.close` or `app.quit` leaves the core
    running.
  - A missing `codex` is recorded as "not installed".
- **A13, focus.** Does `pane.split` change `.focused_pane` in `herdr-app status`? This settles P3.
- **A14, split folder.** Start the "Butler" space in a parent folder. Then read the start folder
  of `pane.split --argv` from `foreground.cwd` in `hc get`, once with the wrapper and once without.
  This settles P2.
- **A15, core env.** Record the PATH a terminal gets, and whether `command -v <kind>` resolves
  there. Confirm that a variable exported only in the Butler's shell is absent. This settles P1
  and D3.
- **A16, IDs and labels.**
  - Compare the `terminal` form in `herdr-app ls` with the form of `HC_TERMINAL_ID`.
  - Check `hc label` and `hc ls --label` on terminals the app created.
  - Check `parent`, `die_with_parent` and `notify`, to show that split and space terminals are not
    the requester's children.
  This settles D5.
- **A17, argument forms.** Check that `--argv '<json>'` and `--focus false` are accepted. Check that
  a `--name` containing `'`, `$` and a backtick arrives literally.

### The probe gate
Compare each result with the decision it tests. The decisions, as written in PLAN.md:
- D2: when the nested check is inconclusive, say so once, then `tui`.
- D3: worker env goes as an argv prefix, `env KEY=VALUE … <kind> …`, with every path expanded.
- D4: a single worker uses `pane.split --argv`. A wave uses `tab.new --argv` for its first worker
  and `pane.split --argv` for the rest. Never `hc run`.
- D5: workers are addressed by terminal ID, labelled `jdi.agent=<name>`, and found with
  `hc ls --label`.
- D6: herd handoff is `hc wait`, then `hc send <t> "<invocation>"`. Never `--task`.
- D7: a kind that reports no status is accepted with a one-time note.
- D8: Codex's `--no-daemon` goes in `harnesses.codex.args`.
- D9: app H1 requires `herdr-app status` to succeed.
- D10: the split direction is always `right`.
- P1: the kind is resolved to an absolute path by `command -v`.
- P2: a split needs the `sh -c 'cd -- …'` wrapper.
- P3: H4 restores focus only if `pane.split` moves it.
- P4: a missing binary or socket means `tui` with no note, and only a failed `hc get` is
  "inconclusive".
- P5: H9 creates only the worktree, and the space is opened at herd step 8.
- P6: the window check passes when there is no top-level `error`, and `errors` is recorded.

**Any probe that contradicts one of these stops the work.** Amend that decision's text in PLAN.md's
`## Implementation Plan`, record why in the probe log, and rerun the affected probes. Later tasks
read the probe log and take any amendment over their own text. If an amendment invalidates a task
file's prescribed text, say which task in the log. The Butler decides whether that task file needs
rewording before Task 03 starts.

**R2 fallback.** If A14 or A6 shows the `sh` wrapper breaks status reporting, single workers fall
back to `tab.new --folder`. That amends D4: record it as an amendment.

### Recording
Write one entry per probe, A1–A17. Each entry has:
- the command, sanitised;
- the observed output, sanitised;
- the decision or decisions it tests;
- a verdict of *confirms* or *amends*, with the amended text if it amends.

Sanitise everything you record:
- `$HOME` becomes `~`.
- The scratch path becomes `<scratch>`.
- No session name, machine name or user name appears.

End the log with one line: `Gate: passed`, or `Gate: passed after amendments to <ids>` with the
rerun results.

### Cleanup (Appendix B)
1. Close every space and tab you created.
2. Quit the throwaway window through the wrapper. VERIFY-AT-EXECUTION: `app.quit` must address only
   the window `HERDR_APP_HOME` selects. If it does not, close the window by hand.
3. Run `hc server stop`, **through the wrapper only**.
4. Run `git worktree prune` in scratch, then remove scratch.
5. Confirm the user's `hc ls --json` count is unchanged.
6. Stop any throwaway TUI, for example from A10, with `herdr --session <throwaway> server stop`.

## Files
None in the repository. The probe log goes into this plan folder's `PLAN.md` (`## Probe log`),
which the Butler commits with the plan. The guard wrapper, scratch clone, throwaway home and probe
scripts all live in the Executor's scratch directory, and nothing is left behind.

## Verification
1. **The log is complete.** Run
   `sed -n '/^## Probe log/,/^## Tasks/p' plans/36-herdr-app-support/PLAN.md | grep -oE '\bA(1[0-7]|[1-9])\b' | sort -u | wc -l`.
   Expected: `17`.
2. **The gate has a verdict.** Run
   `grep -nE '^Gate: passed' plans/36-herdr-app-support/PLAN.md`. Expected: exactly one line.
3. **Sanitised.** Run
   `sed -n '/^## Probe log/,/^## Tasks/p' plans/36-herdr-app-support/PLAN.md | grep -nE '/home/|/Users/|jdiprobe-[0-9a-f]{4}'`.
   Expected: no output, exit status 1. PLAN.md's References mention a probe session named
   `jdiprobe` outside this section, which is why the grep is scoped to the log.
4. **Isolation held.** Run the user's own `hc ls --json`, read-only and outside the wrapper, and
   count the entries. Expected: the same count recorded at setup. Through the wrapper, with the
   probe variables still set, `herdr-app status` is expected to fail, because the throwaway core is
   stopped. Run `git -C <repo root> worktree list`: no worktree was added to the real repository.
5. **The wrapper refuses.** Run the wrapper with `JDI_PROBE_SESSION` unset. Expected: a non-zero
   exit, a message on stderr, and empty stdout.
6. No unit tests change in this task. Run the full suite as a control, `python3 -m unittest discover -s tests -v`:
   it passes or fails exactly as before this task.
