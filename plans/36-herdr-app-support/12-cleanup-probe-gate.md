status: done
# 12 — Probe the herd cleanup mechanics in a throwaway session (the #37 probe gate)

Depends on: None

## Why
Herd cleanup re-finds every space or workspace by worktree path, decides busy from the agent's state, and removes worktrees and scratch branches, so the TUI's removal semantics, the app's per-terminal state, and git's worktree edge cases must be observed before Task 14 writes them down. The gate records here, before Task 14 starts, which pre-agreed amendment applies: whether the TUI removal changes command, how busy is read on the app, and which fragments Task 14 pins. Rests on: C1, C3, C4, C5.

## Description
Planner's Task 12. Run probes R1–R5 below in a **throwaway** app session and app home, with the
Herdr TUI nested inside it as in probe A10, on a scratch clone. Record the sanitised results in this
plan's `PLAN.md`, in a new section `## Probe log (#37)` placed directly above `## Tasks` (below
`## UAT log`). Tasks 14, 15, 17 and 18 read that section first, and any amendment recorded there
overrides their own text.

**Risk R1 applies in full.** An inherited `HC_TERMINAL_SOCKET` or `HC_TERMINAL_ID` can route `hc` to
the user's real core, and an inherited `HERDR_SOCKET_PATH` can route `herdr` to the user's real TUI.
- Every command that addresses Herdr goes through the isolation guard.
- Never run `hc server stop`, `herdr-app do app.quit` or `herdr ... server stop` outside it.
- No TUI worktree may land in the user's real worktrees folder: always pass `--path` under scratch.
- The probes spend agent tokens and open a visible window. Tell the user a window will appear. If
  you cannot open a window, stop and hand this task to the user.

### Isolation guard (Appendix B, as recreated in Task 10)
Write the guard as a POSIX `sh` wrapper `<scratch>/g` in your scratch directory, never in the
repository.
- It refuses unless `JDI_PROBE_SESSION` and `JDI_PROBE_HOME` are both set and the session matches
  `jdiprobe-*`. The refusal goes to **stderr** with exit 64, and nothing goes to stdout: a probe's
  stdout is the JSON you parse.
- It runs `unset HC_TERMINAL_ID HC_TERMINAL_SOCKET HC_SCOPE HC_SOCKET HERDR_ENV HERDR_SOCKET_PATH HERDR_PANE_ID HERDR_TAB_ID HERDR_WORKSPACE_ID`,
  and also unsets the driving session's own Claude variables (`CLAUDECODE`, `CLAUDE_CODE_*`,
  `CLAUDE_PID`, `CLAUDE_EFFORT`), as Task 10 did.
- It runs `export HC_SESSION=$JDI_PROBE_SESSION HERDR_APP_HOME=$JDI_PROBE_HOME`, then `exec "$@"`.
- XDG is **not** overridden: the probe log's XDG finding is that the core keys its socket and state
  by session name.
- **TUI commands.** The nested TUI is addressed through its own socket,
  `~/.config/herdr/sessions/<probe-session>/herdr.sock`. VERIFY-AT-EXECUTION how the `herdr` CLI
  reaches it: either run the TUI commands from a script inside the nested TUI's pane (as A10's
  "inside" probes), or set `HERDR_SOCKET_PATH` to that socket after the guard's `unset`. Before R1,
  prove the address: a `herdr workspace list` (or equivalent) shows only the probe's workspaces.
  A TUI command that could reach the user's own TUI is never run.

### Setup
1. Record the versions of `herdr`, `herdr-app`, `hc` and `git`. Record the **count** (never the
   contents) of the user's own `hc ls --json` entries, and of `git -C <repo root> worktree list`
   lines. Both are read-only and run outside the guard.
2. Clone the repo into `<scratch>/repo` with a bare local `origin` whose `origin/HEAD` is `main`.
   Take a backup of `~/.claude.json` and pre-trust only `<scratch>/repo` in it (as Task 10 did); the
   backup is restored at cleanup.
3. Create the throwaway home with `settings.json` = `{"worktrees":{"directory":"<scratch>/worktrees"}}`.
4. Name the session `jdiprobe-<4 hex>`.
5. Through the guard: `herdr-app status` must fail and `hc ls --json` must be empty. Then start
   `herdr-app` in the background (the only bare launch) and close its welcome overlay.
6. Open a throwaway space on `<scratch>`, and start the nested TUI in it as A10 did:
   `pane.split --argv '["<absolute herdr>","--session","<probe-session>"]'`.

### Probes
- **R1 (TUI): create and read back.**
  - `herdr worktree create --cwd <scratch>/repo --path <scratch>/worktrees/repo/probe-1 --branch jdi-herd-scratch-T-1 --base origin/main --label "probe 1" --no-focus`.
  - Inside that worktree: `git switch -c probe-feature`, then one commit.
  - Record the fields of `herdr worktree list --cwd <scratch>/repo` for that entry, at least
    `path`, `branch` and `open_workspace_id`, and whether `path` is printed exactly as
    `git worktree list --porcelain` prints it.
  - Record the shape of `herdr workspace get <ws>`'s `agent_status` (with no agent, and, if cheap,
    with an idle agent).
  - Note whether either command needs `--trust-repository`. **Never pass it.** If it is needed, the
    TUI counts as unreachable for cleanup, and the gate says so.
- **R2 (TUI, safety): what removal deletes.**
  - On a clean tree: `herdr worktree remove --workspace <ws>`. Record: is the folder gone? Is the
    workspace closed? Do `probe-feature` and `jdi-herd-scratch-T-1` still exist
    (`git -C <scratch>/repo show-ref --verify refs/heads/<branch>`)?
  - Make a second worktree the same way (`--path <scratch>/worktrees/repo/probe-2`, branch
    `jdi-herd-scratch-T-2`), leave an untracked file in it, and run the same removal **without**
    `--force`. Record whether it refuses, its exit status and message.
- **R3 (TUI): a closed workspace.** On a third worktree, `herdr workspace close <ws>`, then
  `herdr worktree list --cwd <scratch>/repo`. Expected by the plan: `open_workspace_id: null`.
  Record what is shown.
- **R4 (app): where the agent state lives.** In a throwaway space on `<scratch>/repo`, run
  `hc ls --json --label herdr.space=<space>`:
  - with only an idle shell;
  - with a Claude agent idle;
  - with the same agent working on a long counting prompt (typed with `hc send ... --if idle`).

  Record where the state is (the plan expects `status.state`), and whether `cwd` and `labels` are
  present per terminal.
- **R5 (git): path forms and blocked removals**, in `<scratch>/repo`.
  - Add a worktree through a symlinked parent folder; record the path form
    `git worktree list --porcelain` prints for it.
  - Delete a registered worktree's folder with `rm -rf`, then run `git worktree remove <path>`:
    record the exit status, the message, and whether `git worktree list --porcelain` marks the
    entry `prunable`.
  - On fresh worktrees: does an **ignored** file alone block a plain `git worktree remove`? Does an
    **untracked** file alone block it?

### The probe gate
Compare each result with the decision it tests, and apply the pre-agreed amendments:
- **R2 deletes a branch** (either `probe-feature` or the scratch branch): the TUI removal in Task 14
  becomes `herdr workspace close <ws>` then `git -C <main checkout> worktree remove [--force] <path>`.
- **R4 shows no state** in `hc ls --json --label herdr.space=<space>`: the busy check in Task 14
  uses `hc get <terminal> --json` per listed terminal, and Task 14's fragment
  `hc ls --json --label herdr.space=<space>` is kept for the listing only.
- **R1's fields differ** from `path`, `branch`, `open_workspace_id`, or `agent_status` has another
  name or shape: amend Task 14's fragments (`herdr worktree list --cwd <main checkout>`,
  `open_workspace_id`, `herdr workspace get <workspace_id>`) to what was observed.
- **R1 needs `--trust-repository`:** cleanup treats the TUI as unreachable (C3's "not reachable
  from here" path); record it for Tasks 14 and 18.
- **R5** fixes the path form C1 stores and C3 compares, the `prunable` handling of C5, and whether
  untracked or ignored files make a removal need `--force` (C3). Record each as *confirms* or as an
  amendment to the named decision.

Record each amendment in the log as `G<n>`, with the decision it amends, the task files whose text
it overrides (14, 15, 17, 18), and the exact replacement fragment. Any result that contradicts C1,
C3, C4 or C5 and is **not** covered by the amendments above stops the work: record it, end the log
with `Gate (#37): stopped`, and hand it to the Butler and the user, as Task 02 did. No decision text
in `## Herd cleanup (#37) — plan` is changed by this task.

### Recording
One entry per probe, R1–R5, each with the command (sanitised), the observed output (sanitised), the
decision it tests, and *confirms* or *amends*. Sanitise everything: `$HOME` becomes `~`, the scratch
path becomes `<scratch>`, no session, machine or user name appears (`<probe-session>`,
`<probe-home>`). End the section with exactly one line: `Gate (#37): passed`, or
`Gate (#37): passed after amendments G1, G2, ...`, or `Gate (#37): stopped`.

### Cleanup (Appendix B)
1. Close every space and tab created; remove every probe worktree and branch in the scratch clone.
2. Stop the nested TUI with `herdr --session <probe-session> server stop`, through the guard.
3. Quit the throwaway window through the guard (`window.close` ended only the throwaway window in
   Task 02), then `hc server stop` through the guard only.
4. Remove the throwaway home, `~/.local/state/herdr-core/<probe-session>/`,
   `~/.config/herdr/sessions/<probe-session>/` and
   `~/.local/state/herdr-automatic-rename/sessions/<probe-session>/`.
5. Restore `~/.claude.json` from the backup (no `projects` entry under `<scratch>` survives).
6. `git worktree prune` in scratch, then remove `<scratch>`.
7. Confirm the user's `hc ls --json` count and the real repository's `git worktree list` line count
   equal the counts taken at setup.

## Files
None in the repository. The probe log goes into this plan folder's `PLAN.md`
(`## Probe log (#37)`), which the Butler commits with the plan. The guard, scratch clone, throwaway
home and probe scripts live in the Executor's scratch directory, and nothing is left behind.

## Verification
Run from the repository root.

1. **The log section exists once.** `grep -c '^## Probe log (#37)$' plans/36-herdr-app-support/PLAN.md` — expected: `1`.
   red when: `0` (the log was written somewhere else or not at all) or `2` (written twice).
   at base: `0`.
2. **Every probe is recorded.** `awk '/^## Probe log \(#37\)$/{f=1;next} /^## /{f=0} f' plans/36-herdr-app-support/PLAN.md | grep -oE '\bR[1-5]\b' | sort -u | wc -l` — expected: `5`.
   red when: fewer than 5 (a probe skipped). The awk scope keeps PLAN.md's risk ids R1–R18 elsewhere out of the count.
   at base: `0` (section absent; the same awk over `## Probe log` with `A(1[0-7]|[1-9])` prints `17`, which proves the scope works).
3. **The gate has exactly one verdict.** `awk '/^## Probe log \(#37\)$/{f=1;next} /^## /{f=0} f' plans/36-herdr-app-support/PLAN.md | grep -cE '^Gate \(#37\): (passed|passed after amendments G[0-9].*|stopped)$'` — expected: `1`, and the line is `passed` or `passed after amendments ...` for this task to be done. A `stopped` line means the task waits for the Butler and the user.
   red when: `0` (no verdict) or more than `1`.
   at base: `0`.
4. **Every amendment names what it overrides.** Read each `G<n>` entry in the section — expected: each names the decision it amends (C1, C3, C4 or C5), the task files it overrides (14, 15, 17, 18), and the replacement fragment.
   red when: an amendment names no task, so Task 14 writes the unamended text.
5. **Sanitised.** `awk '/^## Probe log \(#37\)$/{f=1;next} /^## /{f=0} f' plans/36-herdr-app-support/PLAN.md | grep -nE '/home/|/Users/|jdiprobe-[0-9a-f]{4}'` — expected: no output, exit status 1.
   red when: a home path or the real probe session name is printed.
   control: `grep -cE '/home/|/Users/|jdiprobe-[0-9a-f]{4}' plans/36-herdr-app-support/PLAN.md` prints `4` (the plan's own prose mentions those forms outside the log), so the pattern matches when the text is there.
   at base: no output (section absent).
6. **Isolation held.** Run the user's own `hc ls --json` (read-only, outside the guard) and count the entries; run `git -C <repo root> worktree list | wc -l` — expected: both equal the counts taken at setup. Through the guard, `herdr-app status` exits 2 (the throwaway core and window are gone), and `ls ~/.config/herdr/sessions/` lists no probe session.
   red when: a count changed (a probe reached the user's core or the real repository) or a probe session folder survives.
   at base: `git worktree list | wc -l` printed `1`; the `hc ls` count is taken at this task's setup.
7. **The guard refuses.** `env -u JDI_PROBE_SESSION <scratch>/g echo X` — expected: exit 64, a message on stderr, 0 bytes on stdout. Run it before step 6 of Cleanup removes `<scratch>`.
   red when: it exits 0 or prints `X` (the guard would pass an unset session through).
   at base: none — the guard is written by this task.
8. **No repository file changed.** `python3 -m unittest discover -s tests -v` — expected: every test passes, except that Task 13 runs beside this task and owns `tests/test_herd_record.py`: its tests may be added (the count is 195 plus Task 13's) and may be red while it is mid-flight. Any failure outside `HerdRecordTest` belongs to this task.
   red when: a test outside `tests/test_herd_record.py` fails (a probe wrote into the repository).
   at base: `Ran 195 tests`, `OK`, no known reds.
