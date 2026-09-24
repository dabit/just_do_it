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
