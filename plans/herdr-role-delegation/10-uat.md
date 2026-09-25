status: pending
# 10 - UAT: live Herdr validation

Depends on: 09

## Why

Every automated test in Tasks 01-09 checks that the prose is internally consistent; none of them can
prove the Herdr commands cited in `reference/herdr.md` actually behave as documented, because that
requires a live Herdr session, a real `claude`/`opencode` process, and observation of states the test
suite cannot induce. This task is that proof, and it is the only place several of the plan's
acceptance criteria have any evidence at all.

Rests on: the plan's "Testing Strategy" section (this task reproduces its "Live Herdr validation
procedure" in full) and the "Acceptance-criteria mapping" table.

## Description

Walk the procedure below in order, recording each command and its raw output verbatim in this task
file (not just pass or fail) as you go. Shell snippets are bash; a fish user runs `bash` first. This
UAT is walked before `/jdi:pr` and contains no merge and no push - everything below runs against a
local scratch clone whose origin is the checkout itself, so nothing reaches GitHub.

**Scenario K applies only if Tasks 07 and 08 shipped** (the `/jdi:herd` layer). If the user dropped
Wave 3, skip K, record that it was skipped and why, and skip AC 9's row in the mapping table below
too - note there that AC 9 is deferred to whenever `/jdi:herd` ships against this mechanism, which is
either Tasks 07/08 in a follow-up or PR #5 rebased onto `reference/herdr.md` H1, H2 and H4.

### U0. Setup

1. Work in a Herdr pane: `printenv HERDR_ENV` prints `1`, and `herdr status` shows `status: running`
   and `compatible: yes`. Record `herdr --version` (expect 0.8.2), `claude --version` (2.1.282 when
   this plan was written), `opencode --version` (1.18.10), and `command -v codex`.
2. Create the scratch clone: `git clone /Users/supherman/claude_plugins/just_do_it /tmp/jdi-uat && cd
   /tmp/jdi-uat && git checkout herdr-role-delegation`. The clone's origin is local, so fetches work
   offline and nothing reaches GitHub.
3. Write `/tmp/jdi-uat/.jdi/config.local.yml`, which is gitignored by the committed `.gitignore`.
   Each scenario below shows its version. Every version starts with:
   ```yaml
   tracker:
     name: none
   ```
4. Load the branch's plugin in the Butler. The installed `jdi@just-do-it` is 1.0.8
   (`claude plugin list`). Run `claude plugin disable jdi@just-do-it`, then start the Butler in a
   Herdr pane at `/tmp/jdi-uat` with `claude --plugin-dir /Users/supherman/claude_plugins/just_do_it`.
   Accept the folder trust dialog for the Butler yourself. Confirm `/jdi:help` prints `### Separate
   agent processes`. If `--plugin-dir` does not expose `/jdi:*`, use the fallback:
   `claude plugin uninstall jdi@just-do-it && claude plugin install jdi@just-do-it` from a
   marketplace that points at this checkout. Record which path you took.
5. Choose an opencode model: `opencode models | head`, then pick one `provider/model` you can use.
   Refer to it below as `<OC_MODEL>`.

### U1. Pre-flight probes

Run these in a second Herdr pane in `/tmp/jdi-uat`, by hand.
`G=$(git rev-parse --absolute-git-dir); mkdir -p "$G/jdi/runs/probe"`. After each probe, close the
pane it created.

- **P0: start right after a split.**
  `P=$(herdr pane split --current --direction down --cwd "$PWD" --env JDI_PROBE=from-split --no-focus | jq -r .result.pane.pane_id); herdr agent start jdi-probe-o --kind opencode --pane "$P" --timeout 120000 -- -m <OC_MODEL>; echo "exit=$?"`
  Expect `agent_started`. If it fails because the shell is not ready, H4 needs a readiness wait
  before the start - record that as a UAT finding against H4 (`reference/herdr.md`).
- **P2 and P3 for opencode: environment inheritance and writing into `.git`.**
  `herdr agent prompt jdi-probe-o "Run the shell command: printenv JDI_PROBE > $G/jdi/runs/probe/env-opencode.txt . Then reply OK." --wait --timeout 120000; echo "exit=$?"; cat "$G/jdi/runs/probe/env-opencode.txt"`
  Expect `from-split` in the file. If the file is missing, record whether the worker was blocked on
  a permission, which is the P3 answer for opencode.
- **P1a: timeout.**
  `herdr agent prompt jdi-probe-o "Count from 1 to 300, one number per line, slowly." --wait --timeout 3000 >p1a.out 2>p1a.err; echo "exit=$?"; cat p1a.out p1a.err`
  Record the `timeout` code, which stream it arrived on, and the exit status.
- **P4: closing the pane stops the worker.**
  `pgrep -f opencode | wc -l; herdr pane close "$P"; sleep 2; pgrep -f opencode | wc -l; herdr agent list`
  Expect the count to drop by the worker's processes and `jdi-probe-o` to be absent. If the worker
  survives, record that H8 must add an explicit quit before `pane close` - a UAT finding against H8.
- **P1b and P3 for claude: `agent_blocked`.**
  Split a new pane with `--cwd /tmp/jdi-uat`. Run
  `herdr agent start jdi-probe-c --kind claude --pane "$P" --timeout 120000 -- --model sonnet`, then
  `herdr agent prompt jdi-probe-c "Run the shell command: touch /tmp/jdi-probe-blocked" --wait --timeout 60000`.
  Expect `blocked` from a Bash permission dialog in default permission mode. Then
  `herdr agent prompt jdi-probe-c "hello" --wait --timeout 10000 >p1b.out 2>p1b.err; echo "exit=$?"`
  and record the `agent_blocked` JSON, stream and exit status.
  Answer the dialog yourself in the pane. Then ask the worker to write `$G/jdi/runs/probe/claude.txt`
  and record whether it blocks on a write permission for a path under `.git`.
- **P1c: `agent_prompt_stalled`.**
  `herdr agent prompt jdi-probe-c " " --wait --timeout 20000 >p1c.out 2>p1c.err; echo "exit=$?"`
  If no `agent_prompt_stalled` appears, record "not induced" - the mechanism then rests on the
  `--help` contract only.
- **P5: trust dialog at start.**
  `mkdir -p /tmp/jdi-trust && git -C /tmp/jdi-trust init -q`. Split with `--cwd /tmp/jdi-trust`, then
  run `herdr agent start jdi-probe-t --kind claude --pane "$P" --timeout 60000; echo "exit=$?"; herdr agent get jdi-probe-t; herdr agent read jdi-probe-t --source recent-unwrapped --lines 40`.
  Expect `agent_not_ready` with a trust dialog. Record it and do not answer it.
- **P6: JSON shapes.**
  Record `herdr agent get <name>` output for an idle, a working and a blocked agent, and the stdout
  of a successful `agent prompt --wait`. Confirm which field reports the state, and that H5's wording
  ("read the state from the JSON") matches.
- **P3 for linked worktrees.**
  `git worktree add /tmp/jdi-uat-wt -b uat-wt`. In `/tmp/jdi-uat-wt`,
  `git rev-parse --absolute-git-dir` prints `/tmp/jdi-uat/.git/worktrees/jdi-uat-wt`, which is
  outside the worktree. Repeat the opencode and claude write probes against it and record the
  answers.
- **P8: `herdr worktree create --path`.** In the scratch clone, run
  `herdr worktree create --cwd "$PWD" --path "$HOME/.herdr/worktrees/jdi-uat/jdi-herd-probe" --branch jdi-herd-scratch-probe-1 --base origin/main --label PROBE --no-focus`.
  Record whether `--path` takes the full folder path (expected) or a parent directory, and whether
  `.result.worktree.path` echoes it. Remove it with `herdr worktree remove --workspace <id>` and
  `git branch -D jdi-herd-scratch-probe-1`. If `--path` means something else, H9 is contradicted:
  the probe gate applies.
- **P7.** `herdr integration status`. Record the claude and opencode rows.

**Probe gate.** If any probe contradicts `reference/herdr.md`, stop the UAT. Fix H4, H5, H6 or H8 in
a commit, record it, and re-run the affected probes. Do not continue on a contradicted mechanism.

### U2. Scenarios

In the Butler, after each scenario, check `herdr agent list`, which must show no `jdi-*` agent, and
`herdr pane list --workspace "$HERDR_WORKSPACE_ID"`, which must show no leftover JDI pane.

- **A. Worker A, opencode, full prep (AC 1, 2, 4, 5, 6).**
  Local config: `delegation: {transport: auto}` written as a block, plus
  `models.researcher: {model: <OC_MODEL>, harness: opencode}`. Run
  `/jdi:prep "Add a --dry-run flag to bin/sync-opencode.sh"` and answer "not tracked".
  Expect:
  - no step-0 transport announcement, because auto was detected;
  - a pre-spawn line with agent `jdi-researcher-xxxx`, kind `opencode`, model `<OC_MODEL>`,
    "no arguments", and the run directory;
  - a new pane without focus, and `herdr agent list` showing kind opencode;
  - the Butler waiting, not doing other work;
  - `$(git rev-parse --absolute-git-dir)/jdi/runs/<id>/` containing `manifest.json` (every field
    listed in `reference/herdr.md` H3) and `prompt.md` (the role body without frontmatter, and the
    Appendix A contract);
  - then `report.md`, `result.json` with `complete`, and `outcome.json` with `final: valid` and
    `pane_closed: true`;
  - the Butler saying it validated the result, then spot-checking citations, then updating
    `## References`;
  - the pane closed.

  The Planner and Splitter have no `harness` set, so they run as native subagents of the Claude
  Butler exactly as today: expect no pane, no run directory and no transport text for them. This is
  the "Herdr only when the harness differs" rule.
- **B. Same-harness control (AC 6, AC 8).**
  `delegation: {transport: auto}` and `models.researcher: {model: sonnet, harness: claude}`, with the
  Claude Butler. Run `/jdi:reresearch`. Expect the Researcher to run as a native `jdi:researcher`
  subagent on `sonnet`: no pane, no run directory, no pre-spawn Herdr line, and no transport
  announcement. `herdr agent list` shows no `jdi-*` agent during the run.
- **C. Worker C, codex. Requires installing Codex first; record the install command and version.**
  1. `models.researcher: {model: <codex model>, harness: codex}` and
     `harnesses.codex.args: ["--sandbox", "workspace-write"]`. Run `/jdi:research`. Expect the worker
     to fail to write under `.git` (openai/codex#15505, #14338), so no valid `result.json` appears.
     The Butler then announces an H7 failure with `JDI-RESULT-UNWRITABLE` or "result.json missing",
     closes the pane, and falls to rung 2 (`codex exec -m … -o <file>`). The phase completes.
  2. Add a writable root for the run directory to `harnesses.codex.args` in `config.local.yml`. The
     candidate is `--add-dir <abs gitdir>/jdi/runs`, but the flag is unverified on this machine:
     confirm it with `codex --help` first. Re-run and expect a valid result.

  Record both runs.
- **D. Blocked on an approval (AC 3).**
  Scenario A's config, with OpenCode set to ask before shell commands: write
  `/tmp/jdi-uat/opencode.json` containing `{"permission": {"bash": "ask"}}` and add `opencode.json`
  to `/tmp/jdi-uat/.git/info/exclude` so the combined file check does not see it. Confirm with
  `opencode --help` or its docs that project `opencode.json` permissions apply in the interactive
  TUI; record what you checked. Run `/jdi:research`. When the worker hits a permission prompt,
  expect:
  - the Butler reports `blocked`;
  - it shows `agent get`, `agent explain` and `agent read` output;
  - it asks you what to do and does **not** answer;
  - it offers to focus the pane.

  Approve in the pane yourself and expect the Butler to resume waiting and then validate. Search the
  Butler transcript for `send-keys`: there must be none.
- **E. Content question (AC 3).**
  Scenario A's config. Run `/jdi:research` with the plan's task description amended to end "Before
  finishing, ask the Butler which docs folder to treat as authoritative." Expect:
  - `result.json` with `needs_input`;
  - the Butler moving it to `result.needs_input.1.json`;
  - an answer from `docs.path` it already holds, saying so, sent through the prompt;
  - a later valid result.

  This is best-effort, because the worker may not ask. Record whether it was induced.
- **E2. Question asked in chat, no result file (AC 2, AC 3).**
  Scenario A's config. Run `/jdi:research` with the task description amended to end "Before writing
  any file, ask the user in the chat which docs folder is authoritative, and wait for the reply."
  When the worker goes `idle` or `done` with no `result.json`, expect:
  - the Butler reads the pane with `agent read`, and does not report a failure;
  - it names the pane (agent name and pane ID) and says you can answer there;
  - it keeps waiting, with no resubmit.

  Answer in the pane yourself. Expect the worker to finish, `result.json` with `complete`, and the
  Butler to validate. Then repeat with the amendment "Stop without writing any file." Expect `idle`
  with no question in the pane to be announced as an H7 validation failure, the pane closed, and the
  Researcher re-run through `opencode run`. Best-effort: record whether each case was induced.
- **F. Timeout (AC 3, 4).**
  Tell the Butler: "For this run, use a per-call wait timeout of 20000 ms and an overall deadline of
  60000 ms." Run `/jdi:research` with the opencode worker. At the deadline, expect:
  - inspection output, with no success claim and no resubmit;
  - the question keep waiting / accept a checked file / abandon.

  Choose abandon. Expect `outcome.json` `final: abandoned`, the pane closed, and one announcement,
  then the Researcher running through `opencode run` (rung 2). Repeat F three times and confirm no
  leaked pane.
- **G. Fallbacks (AC 6).**
  - (1) `transport: herdr` in a terminal outside Herdr (for example Terminal.app,
    `claude --plugin-dir …` at `/tmp/jdi-uat`): exactly one step-0 announcement stating `HERDR_ENV`,
    then native delegation, and the phase runs.
  - (2) `transport: auto` outside Herdr: complete silence about the transport.
  - (3) `transport: native` inside Herdr: no pane, a native subagent for a role with no harness,
    `opencode run` for a role on opencode, and no transport text.
  - (4) Misconfigured value: `models.researcher.harness: qwen` (a kind Herdr supports; `qwen` is not
    installed here). Expect one announcement ("supports but not installed"), then rung 3, then the
    floor.
  - (5) Invalid value: `transport: sometimes` gives one announcement, then native.
  - (6) Cannot launch: `harnesses.opencode.env: {PATH: /nonexistent}` makes H4 fail. Expect the pane
    closed and an announcement. The exec fallback then also fails and the role reaches the floor.
    The phase runs, with one announcement per failure.
  - (7) Server unreachable: start the Butler with `HERDR_SOCKET_PATH=/tmp/jdi-no-such.sock` under
    `transport: herdr`. Expect the H1 check (c) announcement. If Herdr ignores the variable, record
    "not induced".
- **H. Backward compatibility (AC 8).**
  Remove `delegation` from the local config and run `/jdi:research` and `/jdi:plan`. Expect no pane,
  no transport text, and delegation identical to a 1.0.9 run. For a reference, re-enable the
  installed plugin and compare against one run of the same command.
- **I. A wave of Executors on another CLI (AC 2, AC 3, AC 6).**
  `delegation: {transport: auto}`, `models.executor: {model: <OC_MODEL>, harness: opencode}`, and
  Scenario D's `opencode.json` with `{"permission": {"bash": "ask"}}`. Use Scenario A's plan if its
  first wave has at least two tasks with disjoint `## Files`; otherwise hand-write a two-task plan
  in the scratch clone (two tasks, `Depends on: None`, disjoint `## Files`, one of them requiring a
  shell command so it hits the permission prompt). Run `/jdi:execute`. Expect:
  - one new tab labeled `jdi-wave-<first run id>` with one pane per task, all started together;
  - one run directory per task, each `manifest.json` listing that task's `## Files` in
    `allowed_writes`;
  - the Butler waiting on both workers, with no other work;
  - one worker `blocked` on the shell permission prompt: the Butler names that pane and asks, the
    other worker keeps running and is not cancelled;
  - you approve in the pane; the Butler resumes the multi-worker wait;
  - both results validated, the combined file check passing, then one commit per task by path;
  - every pane and the wave tab closed.

  Cap check, best-effort: a hand-written five-task wave opens at most 4 panes at once and starts the
  fifth as a slot frees. Record what you saw.
- **J. Feedbacker independence.**
  With the Researcher from Scenario A (opencode), run `/jdi:feedback the research` with
  `models.feedbacker: {model: sonnet, harness: claude}` (a native subagent). Expect the Butler to
  state that producer and reviewer differ. Then set the Feedbacker to `{model: <OC_MODEL>, harness:
  opencode}` and expect "same model and harness" to be stated.
- **K. `/jdi:herd`, only if Tasks 07 and 08 shipped (AC 9).**
  Set `herd: {kind: claude, max_parallel: 2}` and
  `harnesses.claude.args: ["--plugin-dir", "/Users/supherman/claude_plugins/just_do_it"]`. Run
  `/jdi:herd UAT-1 UAT-2`. Expect:
  - two worktrees and two agents named `jdi-herd-uat-1` and `jdi-herd-uat-2`;
  - `/jdi:prep UAT-1` sent with no wait, and a report table;
  - each spawned Butler running its own prep in its own worktree, where its Researcher can itself go
    to Herdr.

  Then check names, the way back, and the cleanup guard:
  - `herdr agent list` shows `jdi-herd-uat-1` and `jdi-herd-uat-2`, and `herdr tab list` shows each
    tab labeled with the same name. `herdr workspace list` shows the workspaces labeled `UAT-1` and
    `UAT-2`. The pre-spawn lines carry no session-name flag.
  - The report lists each worktree path and scratch branch under "Worktree". The folders are
    `<worktrees dir>/jdi-uat/jdi-herd-uat-1` and `.../jdi-herd-uat-2`, and the scratch branches are
    `jdi-herd-scratch-<herd-id>-1` and `-2`.
  - Crash recovery before prep's branch step: start `/jdi:herd UAT-3`, and as soon as its worktree
    exists, close its Herdr workspace by hand (`herdr workspace close <id>`) before the Butler
    reaches step 6. Run `git worktree list` in the scratch clone. Expect a line whose path ends in
    `jdi-herd-uat-3` even though its branch is still a scratch branch. Run `herdr worktree open`
    on it and confirm the workspace comes back.
  - Existing folder: run `/jdi:herd UAT-3` again. Expect the Butler to report the existing
    `jdi-herd-uat-3` folder, its branch and plan state, and ask whether to continue there or skip,
    with no second folder created.
  - A second herd in the same repository does not collide on scratch branches: `git branch --list
    'jdi-herd-scratch-*'` shows two different `<herd-id>` values.
  - The way back does not need the old session. Once `jdi-herd-uat-1` has finished its prep, close
    its pane by hand. Run `git worktree list` and find its worktree by the branch naming `uat-1`.
    Start a fresh Claude Code session there and run `/jdi:status`. Expect it to find the plan and
    report its tasks, with nothing from the old conversation needed.
  - Cleanup guard: do not commit `jdi-herd-uat-2`'s plan. Ask the herd Butler to clean up. Expect it
    to name the uncommitted plan files, offer the `docs: Add <slug> plan` commit, and not remove that
    worktree until you answer. Say yes to the commit and confirm the removal then goes ahead.
  - Name edge cases: run `/jdi:herd 4 ENG-123456789012345678901234567890`. Expect `jdi-herd-4`, and
    a second name cut to 32 characters that still matches `[a-z][a-z0-9_-]{0,31}`. Then re-run
    `/jdi:herd UAT-2` while `jdi-herd-uat-2` is live. Expect the Butler to name the agent that holds
    it and ask, instead of starting a second agent.

  Outside Herdr, `/jdi:herd` stops with the H1 reason and never runs a sequential prep.
- **L. Provider neutrality (AC 10).** `python3 -m unittest discover -s tests -v` passes, and
  `HerdrConfinementTest` is in the run.

### U3. Cleanup

- `herdr pane close` any probe pane that is still open.
- Remove the herd worktrees with the commands H9 printed (skip if Scenario K did not run).
- `git worktree remove /tmp/jdi-uat-wt`.
- `rm -rf /tmp/jdi-uat /tmp/jdi-trust /tmp/jdi-probe-blocked`.
- `claude plugin enable jdi@just-do-it`.

### Acceptance-criteria mapping

| AC | Proven by |
|---|---|
| 1. Researcher delegated to a separate Herdr agent under `/jdi:prep` | Scenario A |
| 2. The Butler waits and resumes on settled or blocked | Scenarios A, D, E2 and I (a wave) |
| 3. A blocked worker is inspected and handled deliberately | Scenarios D, E, E2 (idle without a result file) and F, plus I (blocked inside a wave) |
| 4. Completion requires a valid artifact | Scenarios A, C1 and F, plus `HerdrOperationsTest` (H7, Task 01) |
| 5. Validation happens before `PLAN.md` changes | Scenario A, plus `ValidationGateTest` (Task 04) |
| 6. A different harness and model for the worker | Scenarios A and C (and I for a wave); B is the same-harness control that must stay a native subagent |
| 7. Unavailable, disabled, misconfigured or unlaunchable Herdr is announced and falls back | Scenario G (1)-(7), plus `TransportSelectionTest` (Task 03) |
| 8. No new keys means today's behavior | Scenario H, plus `DelegationBlockTest` (Task 02, default `native`) |
| 9. `/jdi:herd` stays ticket-level fan-out | Scenario K, plus `HerdCommandTest` (Task 08) - **deferred** if Wave 3 was dropped; see below |
| 9a. A herd worktree's folder names its issue, its plan can be continued from a fresh session, and cleanup never deletes an uncommitted plan | Scenario K way-back and cleanup-guard checks, plus `HerdCommandTest` (Task 08) |
| 10. Bodies stay provider-neutral | `HerdrConfinementTest` (Task 03) |
| 11. Every lifecycle-required site is updated | the Task 02, 05, 07, 08 and 09 tests, plus the `grep` checks in each task |
| 12. The suite passes | Scenario L |
| 13. A live procedure exists | this task |

**After the merge - deferred.** These are not exercised by this UAT and are not required to mark
this task done:

- **PR #5 (`origin/herd-command`) closing as superseded.** This happens only once this branch
  actually merges to the default branch - a UAT walked before `/jdi:pr` cannot observe a merge that
  has not happened. Record here whether Wave 3 shipped: if it did, note that closing PR #5 as
  superseded is the PR author's job after merge, not a UAT step; if Wave 3 was dropped, note instead
  that PR #5 needs rebasing onto `reference/herdr.md` H1, H2 and H4, and that this is tracked wherever
  the user decides to track it (a follow-up issue, or a note on PR #5 itself), not inside this plan
  folder, which is deleted at `/jdi:pr` time.
- **AC 9, if Wave 3 was dropped.** Deferred to whichever later change actually ships `/jdi:herd`
  against this mechanism - either a follow-up plan that adds Tasks 07/08's content, or PR #5 rebased
  onto H1, H2 and H4b. Record which of those two paths the user intends, so the deferral has a named
  destination rather than an open-ended one.

## Files

None. This task records its procedure, findings, and probe outputs in this file's own body (edit
this file in place to log results); it creates and destroys only scratch state under `/tmp`, which is
outside the repository and not committed.

## Verification

- Every command in U0 through U3 has been run and its raw output recorded in this file.
- The probe gate in U1 either passed cleanly or its fix commit is named and the affected probes were
  re-run.
- Every row of the acceptance-criteria mapping table has a recorded scenario result or an explicit
  "not induced" / deferred note - no row is left blank.
- `python3 -m unittest discover -s tests -v` (Scenario L) - the full suite passes, matching AC 12.
- `herdr agent list` and `herdr pane list` show no leftover `jdi-*` agent or pane after U3.

## Run log (agent smoke test, 2026-09-24)

This is an agent smoke test, not user acceptance. An Executor agent inside Herdr (pane `w3A:p1`)
played the user. It drove a Butler under test in a sibling pane with `herdr agent prompt`, and it
answered worker dialogs in the worker panes itself. `S` below is the session scratchpad
`/private/tmp/claude-501/-Users-supherman-claude-plugins-just-do-it/ac574946-cf7d-4f35-92b9-557eee1984ad/scratchpad`.
The Butler's full transcript was read from its Claude Code session JSONL, because the pane's
alternate screen lost the early lines.

### Setup deviations from the procedure

- Scratch clone: `$S/jdi-uat` (origin is the local checkout), not `/tmp/jdi-uat`. A second clone,
  `$S/jdi-uat-g`, ran the outside-Herdr cases so they could not collide with the Butler's plan edits.
- OpenCode: the global `~/.config/opencode/opencode.json` is invalid for 1.18.x ("Unrecognized key:
  agents"), so every OpenCode run used `harnesses.opencode.env: {XDG_CONFIG_HOME: $S/xdg}`. That
  folder symlinks Herdr's OpenCode state plugin. No PATH override was needed: panes found `opencode`
  on the inherited PATH. Panes ran the nvm binary `opencode` 1.18.32; `~/.opencode/bin/opencode`
  is 1.18.10.
- Models: `openai/*` fails with `Token refresh failed: 401` (OAuth, setup issue). Probes used
  `github-copilot/gpt-5.4`. Scenario A used `github-copilot/gpt-5.5`; D, E, E2 and F (first two
  repeats) used `github-copilot/gpt-5.4`. At about 01:49Z Copilot returned `402 You have exceeded
  your monthly quota`, so F repeats 3-4, G, H, I and J used `opencode/gpt-5.4-mini` (OpenCode Zen).
- The Butler ran as `claude --plugin-dir /Users/supherman/claude_plugins/just_do_it
  --permission-mode bypassPermissions` (bypass for the Butler under test only, in the scratch
  clone). `jdi@just-do-it` 1.0.8 was disabled for the run and re-enabled at the end.
- Local config always had `tracker: {name: none}` and `jev: {enabled: false}`. Scenario I also set
  `tdd: {enabled: false}` to keep the fixture small.
- The user's Claude default is `defaultMode: bypassPermissions`, so the claude probes passed
  `--permission-mode default` to get approval dialogs.
- The Butler's agent name `jdi-uat-butler` starts with `jdi-`; the leftover checks excluded it.

### U0

| Item | Result |
|---|---|
| `printenv HERDR_ENV` / `herdr status` | `1` / `status: running`, `compatible: yes` |
| Versions | herdr 0.8.2; claude 2.1.282; opencode 1.18.10 (`~/.opencode/bin`), 1.18.32 in panes; `command -v codex` exit 1 |
| Plugin path | `claude plugin disable jdi@just-do-it`, then `--plugin-dir`. `/jdi:help` printed `Separate agent processes` and `/jdi:herd`. No fallback install needed |
| Trust dialog | Accepted by the tester for `$S/jdi-uat` during probe P1b |

### U1 probes - probe gate: PASSED (no probe contradicts `reference/herdr.md`)

| Probe | Result | Key evidence |
|---|---|---|
| P0 | PASS | `herdr agent start jdi-probe-o --kind opencode --pane w3A:p6 ...` right after `pane split` returned `"type":"agent_started"`, `argv ["opencode","-m","github-copilot/gpt-5.4"]`, exit 0. No readiness wait needed |
| P2 | PASS | `env-opencode.txt` contained `from-split` (pane `--env` reached the worker) |
| P3 opencode, main checkout | PASS | The write to `<gitdir>/jdi/runs/probe/` happened with no permission prompt |
| P1a | PASS | `--wait --timeout 3000`: stdout empty, stderr `{"error":{"code":"timeout","message":"timed out waiting for agent status"}}`, exit 1; `agent get` then showed `working` |
| P4 | PASS | `pgrep -f opencode \| wc -l` 3 then 2 after `herdr pane close` (the 2 are unrelated: playwright MCP and `opencode2 serve`); `jdi-probe-o` gone from `agent list` |
| P1b | PASS | Bash approval (`rule: bash_permission_prompt`) gave `blocked`; then `prompt "hello" --wait`: stderr `{"error":{"code":"agent_blocked",...}}`, exit 1 |
| P3 claude | Observed | In default mode, a Write under `.git/jdi/runs/probe/` asks "Do you want to create claude.txt?"; the file landed after approval |
| P1c | PASS (induced) | `prompt " " --wait --timeout 20000`: stderr `{"error":{"code":"agent_prompt_stalled","message":"... state_change_seq remained 1542"}}`, exit 1 |
| P5 | PASS | Seen on the first claude start in `$S/jdi-uat`: `agent_not_ready` "blocked during startup", screen showed the folder trust dialog, state `blocked`. The separate `/tmp/jdi-trust` repeat was not run |
| P6 | PASS | State is `.result.agent.agent_status` in `agent get`, `agent prompt --wait` and `agent wait` stdout (idle, working, blocked, done all seen); errors are `.error.code` on stderr. H5's wording matches |
| P3 linked worktree, opencode | Finding | `git rev-parse --absolute-git-dir` gave `$S/jdi-uat/.git/worktrees/jdi-uat-wt`. OpenCode asked `Permission required - Access external directory .../.git/worktrees/jdi-uat-wt/jdi/runs/probe` on each access until "Allow always"; the write then landed |
| P3 linked worktree, claude | Not run | Default mode asks on every write, so the worktree case adds nothing |
| P7 | Recorded | `claude: outdated (v7 < v8)`, `opencode: outdated (v9 < v10)` |
| P8 | PASS (prior run) | `--path` takes the full folder; `.result.worktree.path` echoed `/Users/supherman/.herdr/worktrees/jdi-uat/jdi-herd-probe` |

Probe observations (not contradictions):

- Right after the tester answered a dialog, an immediate `agent wait` returned the stale `blocked`
  once. A resumed wait loop has to tolerate one stale read.
- An OpenCode error toast (`Token refresh failed: 401`) made `prompt --wait` return `blocked`,
  while `agent explain` said `state: idle` (`full_lifecycle_hook_authority`). H6 inspection
  handles it, but the Butler will report it as a dialog.
- A per-call `timeout` arrives as a JSON error on stderr with exit 1. H5's last row ("a JSON error
  on stderr with exit 1 ... transport failure") reads as if it covers this case too; only the
  `working` row makes clear it does not. The Butler classified it correctly in every run.

### U2 scenarios

**A - PASS, one FAIL item.** `/jdi:prep "Add a --dry-run flag to bin/sync-opencode.sh"`,
Researcher on `github-copilot/gpt-5.5` via opencode. Tracker none, so no "not tracked" question.

- No step-0 transport text. Worker `jdi-researcher-895a`, kind opencode, pane `w3A:pB` (no focus).
- Run dir `20260925T010028Z-researcher-895a`: `manifest.json prompt.md`, then `report.md
  result.json outcome.json`. The manifest has every H3 field (`"transport":"herdr"`,
  `"integration":"opencode: outdated (v9 < v10)"`, `"args":[]`, `"env_keys":["XDG_CONFIG_HOME"]`,
  `deadline_ms 2700000`). `prompt.md` has the role body without frontmatter and the contract
  ending `JDI-DONE <run-id>`.
- `result.json`: `"status":"complete"`, head `802a9cc`. `outcome.json`: `"final":"valid"`,
  `"validation":"H7 checks 1-6 passed"`, `"pane_closed":true`.
- Order: "The result passes all six H7 checks. I'll close the pane, record the outcome, and
  spot-check the citations", then "Citations match", then `## References` was written. The Butler
  only waited while the worker ran. The first `prompt --wait --timeout 270000` returned `timeout`;
  the Butler did not resend.
- Planner ran as a native `jdi:planner` on opus: no pane, no run dir. The Butler wrote the split
  itself ("I'll skip the Splitter", allowed by `commands/prep.md` step 16).
- FAIL: no H4 pre-spawn line (agent name, kind, model, "no arguments", env keys, run dir) was
  printed before `agent start`. The text before the spawn was only "Next I check whether Herdr can
  run the Researcher on OpenCode." The same was true of every later Herdr spawn in this log.
- Minor: the manifest was written with `"pane_id": null` and edited after `pane split`, against
  H3's "never edited afterward". The `outcome.json` timestamps were estimates (idle at 01:08Z,
  but `report.md` appeared about 01:15Z).

**B - PASS.** Researcher `{model: sonnet, harness: claude}`, `/jdi:reresearch`. `[231] AGENT:
type=jdi:researcher model=sonnet`. No pane, no run dir, no `jdi-*` agent. Note: the summary said
"it ran as a subagent and Herdr was not used, although it is detected", although rung 2 is
supposed to be silent.

**C - NOT RUN:** codex not installed.

**D - PASS.** `$S/xdg/opencode/opencode.json` = `{"permission":{"bash":"ask"}}`;
`opencode debug config` showed `"bash": "ask"`. `/jdi:research`, worker `jdi-researcher-86ef`
blocked on `$ git rev-parse HEAD`. The Butler ran `agent explain` and `agent read` (it did not run
`agent get`; the prompt JSON already had the state), then said "The Researcher is waiting for your
permission in its pane, and I don't answer a worker's dialogs for you ... Do you want me to focus
that pane for you?" The tester approved in the pane. `outcome.json`: `"final":"valid"`,
`"user_decisions":["User approved the OpenCode permission dialog ... in pane w3A:pC"]`. The
transcript has no `send-keys`. The config file was removed after D.

**E - PASS (induced on the second try).** The first amendment ("ask the Butler which docs
folder...") made the worker ask in chat instead (recorded under E2). With "... through the
needs_input status of your result contract", the worker wrote `result.json`
`"status":"needs_input"`. The Butler ran `mv result.json result.needs_input.1.json` and answered
through `herdr agent prompt` from `docs.path` and the user's earlier answer, saying so. Then came a
valid result: `answers[0].answered_by: "Butler, from context"`, `moved_to:
"result.needs_input.1.json"`.

**E2 case 1 - PASS with a note.** The worker went idle with no `result.json` and asked in chat.
The Butler: "The worker went idle without writing `result.json`, so I'll check its screen", then
"This is not a failure, because it is waiting for an answer ... You can answer it directly in
pane `w3A:pD`." It did not resubmit. Note: it ended its turn and asked how to answer instead of
continuing to wait. The tester answered in the pane and got a valid result.

**E2 case 2 - NOT INDUCED.** Tried "Stop without writing any file." and "Do not write report.md or
result.json, and do not ask anything." Both times the worker followed its result contract and
wrote a valid result.

**F - PASS.** Per-call 20000 ms, overall 60000 ms, and the worker told to `sleep 120` (the first
try without sleep finished in 45 s and did not trigger).

- At the deadline: "I won't count this as success, and I won't resubmit", an `agent read`
  inspection, then a question with "Keep waiting / Abandon and fall back / Accept a file". The
  tester chose abandon.
- `outcome.json`: `"final":"abandoned"`, `"pane_closed":true`, `"fallback":"opencode run
  (non-interactive)"`.
- The `opencode run` fallback put the role file inline (no `jdi-researcher` agent under the moved
  `XDG_CONFIG_HOME`). It failed with `402 quota_exceeded`, and the Butler retried without `-m`
  (rung 11); OpenCode picked `opencode-go/gpt-5.6-luna`, and the run was valid.
- Repeat 3 (Zen): abandon, then `opencode run` exit 0 with no report, then the floor (a native
  subagent). Repeat 4: abandon, then a valid `opencode run`. No pane leaked in any repeat.

**G - (1) PASS, (2) PASS, (3) PARTIAL, (4) PASS, (5) PASS with a note, (6) PASS with a deviation,
(7) PASS.** G(1) and G(2) ran `env -u HERDR_ENV -u HERDR_PANE_ID -u HERDR_WORKSPACE_ID -u
HERDR_TAB_ID claude -p ...` in `$S/jdi-uat-g`, which simulates "outside Herdr" by unsetting the
variables.

- (1) `transport: herdr`: "The transport is set to `herdr`, but the Herdr check failed on its first
  step: `printenv HERDR_ENV` printed nothing and exited 1. So this run delegated as `native`."
  Then `opencode run -m opencode/gpt-5.4-mini`, and the phase ran.
- (2) `transport: auto`: no `herdr` command and no transport text anywhere in the stream.
- (3) `transport: native`, inside Herdr: no pane, and `opencode run` for the Researcher. But the
  Butler still ran `herdr status` at step 0, and `reference/delegation.md` says "Nothing is probed
  at step 0". The summary also said "the transport was `native`, so there was no pane". The
  no-harness native-subagent half was not exercised: only the Researcher ran.
- (4) `harness: qwen`: "Herdr supports the `qwen` kind, but `command -v qwen` found nothing. So the
  Researcher ran as a subagent in this session, on the session's own model. The Agent tool can't
  take `qwen3-coder`." That is one announcement for both rungs, then the floor.
- (5) `transport: sometimes`: exactly one announcement, "`delegation.transport` was "sometimes",
  which isn't a valid value, so I delegated natively", but only in the final summary, not at step
  0. No `herdr` call. Environment trouble in the same run: the native `opencode run` hung for 10
  minutes with no output. The Butler asked; the tester chose kill, and the floor ran.
- (6) `harnesses.opencode.env.PATH: /nonexistent`: `agent start` returned `timeout` after 120 s,
  and the pane showed `fish: Unknown command: opencode`. Then `herdr pane close w3A:pN`, and
  `outcome.json` `"final":"transport_failed"`, `"pane_closed":true`. Deviation from the expected
  result: the exec fallback ran `env ... PATH=/nonexistent /Users/supherman/.opencode/bin/opencode
  run ...` by absolute path, so it launched and returned a degraded report (glob, grep and bash
  failed) instead of reaching the floor.
- (7) `HERDR_SOCKET_PATH=/tmp/jdi-no-such.sock` (Herdr honors it: `status: not running`) under
  `herdr`: "Herdr detection failed at check (c)" and "the Herdr server is not running (socket
  `/tmp/jdi-no-such.sock`). I delegated the normal way instead."

**H - PASS (partial coverage).** No `delegation` key: no `herdr` command in the transcript and no
pane; `opencode run` ran. The summary mentioned "no `delegation` block ... the transport is
`native`". This long-lived session had run every earlier scenario, so the mention is most likely
carried context. Not run: `/jdi:plan`, and the reference run on the installed 1.0.8 plugin.

**I - PASS.** Hand-written two-task wave (`plans/uat-wave`, tasks 01 and 02, disjoint `## Files`),
Executor on `opencode/gpt-5.4-mini`, `{"permission":{"bash":"ask"}}`.

- `herdr tab create` gave `w3A:t3`, then `herdr tab rename w3A:t3
  jdi-wave-20260925T023714Z-executor-7673`. Both agents were started together in that tab (panes
  `w3A:pP`, `w3A:pQ`).
- Each manifest's `allowed_writes` held its own `scratch/wave-a.txt` or `scratch/wave-b.txt` plus
  its run files.
- Both workers went `blocked`. The Butler named both panes and the tab, asked, and did not answer.
  The tester approved in the panes, and the Butler resumed the multi-worker wait.
- Both `outcome.json`: `"final":"valid"`, "H7 checks 1-5 passed; wave file check passed". Then
  `herdr pane close w3A:pQ`, `herdr pane close w3A:pP`, `herdr tab close w3A:t3`.
- `/jdi:done` made `f817e04 chore: Add scratch/wave-a.txt` and `9a8731a chore: Add
  scratch/wave-b.txt`, one commit per task by path.
- Findings: the Butler's `agent read --source visible` did not show the dialog in the half-width
  panes, while `--source detection` did. Herdr closed the tab by itself when its last pane closed,
  so `tab close` returned `tab_not_found`. The tab label showed the terminal title (`[3] OC |
  Follow prompt.md in`) after the rename. The first prompt attempt used `--timeout` without
  `--wait` and was rejected (`--timeout requires --wait`, exit 2) before any input was sent, so the
  second send was the first submission, not a resubmit. The "one worker keeps running" check was
  not isolated: both workers needed bash (`git add`, `git rev-parse`) and both blocked.
- Cap check (five-task wave): NOT RUN.

**J - PASS.** Feedbacker `{sonnet, claude}`: `[1295] AGENT: type=jdi:feedbacker model=sonnet`. The
Butler did not state that producer and reviewer differ, but `commands/feedback.md:56-58` asks for
a statement only when they are the same, so the UAT expectation is stricter than the command.
Feedbacker `{opencode/gpt-5.4-mini, opencode}`: "The Feedbacker is configured on
opencode/gpt-5.4-mini, the same model and harness as the last Researcher pass it would review."
It asked; the tester chose "As configured". The Feedbacker then ran as Herdr worker
`jdi-feedbacker-afbb` with `"final":"valid"`, and the verdict noted the same model and harness.
The run dir also held an extra `inputs` entry beside the five H3 files.

**K - PASS (crash-recovery step partial).** `herd: {kind: claude, max_parallel: 2}`,
`harnesses.claude.args: ["--plugin-dir", "/Users/supherman/claude_plugins/just_do_it",
"--permission-mode", "bypassPermissions"]`.

- `/jdi:herd UAT-1 UAT-2`: `herdr worktree create --cwd "$PWD" --path $W/$name --branch
  jdi-herd-scratch-20260925T025438-$n --base origin/herdr-role-delegation --label "$id"
  --no-focus`. Agents `jdi-herd-uat-1` (`w3F:p1`) and `jdi-herd-uat-2` (`w3G:p1`); tabs
  `jdi-herd-uat-1`, `jdi-herd-uat-2`; workspaces labeled `UAT-1`, `UAT-2`.
- Each Butler got `/jdi:prep UAT-N` with no wait. The report table lists folders
  `/Users/supherman/.herdr/worktrees/jdi-uat/jdi-herd-uat-N` and scratch branches under
  "Worktree", and the start lines have no session-name flag.
- The herd worktrees have no `config.local.yml`, so their Butlers read the committed `tracker:
  github`. `gh` could not reach GitHub (origin is a local path), and both Butlers asked what the
  ID meant. The tester chose "untracked smoke task".
- UAT-2 went to branch `uat-2-herd-smoke-test`. UAT-1 went to `help-command-table-guard`, which
  does not name the issue; the folder name `jdi-herd-uat-1` still does.
- `/jdi:herd UAT-2` while live: "A Butler for UAT-2 (jdi-herd-uat-2) is still working in its
  worktree, with an uncommitted plan. What should this herd do?" It started nothing and made no
  second folder.
- `/jdi:herd 4 ENG-123456789012345678901234567890`: agents `jdi-herd-4` and
  `jdi-herd-eng-1234567890123456789` (32 characters, matches `[a-z][a-z0-9_-]{0,31}`). The second
  herd's scratch branches are `jdi-herd-scratch-20260925T025849-{1,2}`, a different herd ID from
  `...025438-...`.
- Way back: once UAT-1 finished prep (2 tasks), the tester closed `w3F:p1`. Herdr closed workspace
  `w3F` too, and the worktree stayed in `git worktree list`. A fresh `claude -p ... "/jdi:status"`
  in the folder printed "## Plan status: `help-command-table-guard` ... 0/2 tasks complete" with
  both waves.
- Existing folder: `/jdi:herd UAT-1` said "The UAT-1 worktree already exists on branch
  help-command-table-guard, with an uncommitted plan and no live agent", then asked "Continue
  there / Skip UAT-1". No second folder was made.
- Reattach: `herdr worktree open --cwd $S/jdi-uat --path .../jdi-herd-uat-1 --label UAT-1
  --no-focus` gave workspace `w3K` on branch `help-command-table-guard`.
- Cleanup guard: "UAT-1 and UAT-2 have uncommitted plans that removing their worktrees would
  delete", with "Commit plans, then remove" offered first. Nothing was removed until the tester
  answered. Then `9609593 docs: Add help-command-table-guard plan` and `1d56a9e docs: Add
  uat-2-herd-smoke-test plan`, `herdr worktree remove --workspace` for w3K, w3G, w3H and w3J
  without `--force`, and all four scratch branches deleted.
- Outside Herdr (`env -u HERDR_ENV ... claude -p "/jdi:herd UAT-9"`): "Herdr check failed at H1
  (a) ... `/jdi:herd` has no sequential fallback, so I did not run UAT-9 as a single `/jdi:prep`."
- NOT RUN: crash recovery with UAT-3, which needs the workspace closed by hand before step 6. The
  worktree surviving a closed workspace and `worktree open` reattaching were both shown with UAT-1
  instead.

**L - PASS.** `python3 -m unittest discover -s tests -v`: `Ran 110 tests ... OK`, including
`test_no_herdr_command_variable_or_question_tool_outside_the_reference
(test_delegation_transport.HerdrConfinementTest) ... ok`.

**After every scenario:** `herdr agent list` showed no leftover `jdi-*` worker and `herdr pane
list` no leftover JDI pane. The Butler never leaked a pane. At the end, the tester closed the
Butler pane `w3A:pA`.

### U3 cleanup

Every probe pane and the Butler pane were closed. The herd worktrees were removed by the herd
Butler as above, and `~/.herdr/worktrees/jdi-uat/` is empty. `$S/jdi-uat-wt` was removed along
with branch `uat-wt`. `$S/xdg/opencode/opencode.json` was removed. `/tmp/jdi-probe-blocked` was
never created. `claude plugin enable jdi@just-do-it` ran, and `claude plugin list` shows
`Status: ✔ enabled`. `$S/jdi-uat`, `$S/jdi-uat-g` and `$S/xdg` were left in place. Final `herdr
agent list` shows only the user's two claude agents (`w3A:p1`, `w3B:p1`).

### Findings to act on

1. Branch defect: the H4 "Print first" line never appeared in any Herdr spawn (A, D, E, E2, F, G6,
   I, J2). The rule is only in `reference/herdr.md` H4. A step in the delegating commands, or a
   template line, would make it hard to skip.
2. Branch defect, minor: under `transport: native` the Butler still ran H1's `herdr status` at step
   0 (G3). Several summaries also mentioned the transport when the ladder says to stay silent (B,
   G3, H). The long-lived session may have contributed; a fresh-session repeat would settle it.
3. Doc gap: H3 says the manifest is written before the spawn and never edited, but `pane_id` comes
   from H4's `pane split`. Every run wrote `null` and edited it afterward.
4. Doc gap: H6 and the wave wait read the pane with `--source visible` or `recent-unwrapped`. In a
   half-width wave pane only `--source detection` showed the OpenCode dialog.
5. Doc gap: in a linked worktree, OpenCode asks "Access external directory" for the run directory
   on every access (P3), so every herd Researcher on OpenCode will block at least once.
6. Doc gap: Herdr closes a tab when its last pane closes, so H8's `herdr tab close` after a wave
   returns `tab_not_found`. It is harmless, but the doc could say so. The tab label is overwritten
   by the terminal title.
7. Test-spec mismatch: J expects a "differ" statement that `commands/feedback.md` does not
   require. G6 expects the exec fallback to fail, but the Butler resolved the binary before
   applying the env.
8. Test setup: OpenAI OAuth expired, the Copilot quota ran out mid-run, and one native `opencode
   run` hung. None of these is a branch defect.

### Acceptance-criteria results

| AC | Result |
|---|---|
| 1. Researcher delegated to a separate Herdr agent under `/jdi:prep` | PASS - Scenario A (`jdi-researcher-895a`, opencode, `final: valid`). H4 pre-spawn print missing (finding 1) |
| 2. The Butler waits and resumes on settled or blocked | PASS - A, D, E2 case 1, I. The Butler ends its turn to ask and resumes when told |
| 3. A blocked worker is inspected and handled deliberately | PASS - D, E (needs_input), E2 case 1, F, I. E2 case 2 not induced |
| 4. Completion requires a valid artifact | PASS - A and F (abandoned run never counted; exec output validated), plus `HerdrOperationsTest`. C1 not run (no codex) |
| 5. Validation happens before `PLAN.md` changes | PASS - A: H7, then spot-check, then `## References`; plus `ValidationGateTest` |
| 6. A different harness and model for the worker | PASS - A (opencode) and I (wave); B stayed a native subagent. C not run (no codex) |
| 7. Unavailable, disabled, misconfigured or unlaunchable Herdr is announced and falls back | PASS with notes - G(1), (2), (4), (5), (6), (7) pass; G(3) probed H1 under native (finding 2); (5) announced late; plus `TransportSelectionTest` |
| 8. No new keys means today's behavior | PASS (partial) - H: no Herdr call, no pane. `/jdi:plan` and the 1.0.8 reference run not done; plus `DelegationBlockTest` |
| 9. `/jdi:herd` stays ticket-level fan-out | PASS - K, plus `HerdCommandTest` |
| 9a. Herd folder names its issue, plan continues from a fresh session, cleanup never deletes an uncommitted plan | PASS - K folder names, way-back `/jdi:status`, cleanup guard. UAT-3 crash step not run (covered in part with UAT-1) |
| 10. Bodies stay provider-neutral | PASS - `HerdrConfinementTest` in Scenario L |
| 11. Every lifecycle-required site is updated | PASS - suite green (Task 02, 05, 07, 08, 09 tests) |
| 12. The suite passes | PASS - L: 110 tests OK |
| 13. A live procedure exists | PASS - this task, walked as an agent smoke test |

Wave 3 shipped (Tasks 07 and 08), so closing PR #5 as superseded is the PR author's job after the
merge. It is not a UAT step.
