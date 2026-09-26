# Herdr-aware role delegation

- Tracker: github
- Project: feature development
- Issue: none
- Issue URL: none
- Created: 2026-09-24
- Started: 2026-09-24
- TDD: on — proven 2026-09-24 with `python3 -m unittest discover -s tests -v`
- Base commit: origin/main @ 94912b348658fffee5b41e69e04cd2b46d12dfac
- Summary: A JDI Butler runs a delegated role as a separate Herdr-managed agent only when that role
  is configured on a different CLI than the Butler's own; a role on the Butler's own CLI always
  stays a native subagent. A wave of Executors on another CLI gets one pane per task. `/jdi:herd`
  (Tasks 07-08) supersedes PR #5's Herdr plumbing.

## References

- reference/delegation.md
- reference/herdr.md
- reference/config.md
- reference/jev.md
- reference/plan-store.md
- reference/tracker.md
- reference/testing.md
- roles/butler.md
- agents/researcher.md
- agents/planner.md
- agents/splitter.md
- agents/executor.md
- agents/synthesizer.md
- agents/pr-writer.md
- agents/feedbacker.md
- commands/prep.md
- commands/research.md
- commands/plan.md
- commands/split.md
- commands/feedback.md
- commands/pr.md
- commands/execute.md
- commands/next.md
- commands/yolo.md
- commands/reresearch.md
- commands/replan.md
- commands/status.md
- commands/done.md
- commands/start.md
- commands/init.md
- commands/help.md
- commands/herd.md
- docs/harness-adapter-architecture.md
- docs/config-key-lifecycle.md
- docs/delegation-transport-architecture.md
- README.md
- AGENTS.md
- CHANGELOG.md
- jdi.config.example.yml
- .claude-plugin/plugin.json
- .codex-plugin/plugin.json
- .claude-plugin/marketplace.json
- bin/sync-opencode.sh
- skills/run/SKILL.md
- tests/test_codex_plugin.py
- tests/test_config_schema.py
- tests/test_enumerations.py
- tests/test_parallel_waves.py
- tests/test_opencode_sync.py
- tests/test_versions.py
- tests/jdi_files.py
- tests/test_herdr_operations.py
- tests/test_delegation_transport.py
- tests/test_step_zero_transport.py
- tests/test_transport_docs.py
- tests/test_herd.py
- plans/9-agent-model-settings/PLAN.md
- plans/11-jev-typed-judgments/PLAN.md
- plans/7-codex-skill-model/PLAN.md
- plans/1-tdd-configuration/PLAN.md

PR #5 (`origin/herd-command`, head `2c28c11`, version 1.0.5) is the prior, superseded design for
`/jdi:herd`; it is not a path in this repo and is cited here, not listed above.

## Decisions

1. **Herdr only when the harness differs (revised 2026-09-24).** Herdr is a second way to run rung
   2 of the delegation ladder (the separate-CLI session), not a new rung 0. A role whose
   `models.<role>.harness` is empty or names the Butler's own kind is always a native subagent and
   never reaches Herdr. `native` (default) probes nothing at step 0 and reaches Herdr only through
   today's rung-4 floor, for a kind with no exec mode; `auto`/`herdr` with Herdr detected runs the
   other CLI's interactive agent in a Herdr pane instead of its non-interactive mode.
2. **Waves are in scope.** Executors on another CLI in a wave get one pane per task, all started
   together in one wave tab, each with its own run directory and `allowed_writes` (that task's
   `## Files` plus its run directory), capped at 4 open panes at once. The Butler runs a
   multi-worker wait, points the user at any blocked or questioning pane, lets the whole wave settle
   before acting on any one result (a running sibling is never canceled because another failed),
   validates each task, runs one combined file check against the union of the wave's `## Files`,
   then commits each task by path.
3. **Idle or done with no `result.json` is inspected, never resubmitted.** A question seen in the
   pane is relayed to the user, who answers there while the Butler keeps waiting; no question and
   no result is an H7 validation failure.
4. **The "watch the run" Herdr trigger is dropped** from `reference/delegation.md`, superseded by
   decision 1: a role on another CLI always gets a pane under `auto`/`herdr`, so a separate watch
   trigger has nothing left to add.
5. **The brief was overridden twice, by the user, on 2026-09-24.** The brief asked to prefer a Herdr
   pane over a native subagent whenever Herdr is on: overridden because a subagent is watchable in
   every harness JDI supports, so a pane adds nothing for a role on the Butler's own CLI, and a pane
   matters only where another CLI runs. The brief asked for one active delegated role per Butler:
   this becomes "a Butler runs one phase at a time; inside a phase, only a wave runs several workers
   at once, and the Butler waits for all of them" - because waves already ran concurrently today
   through rung-2 processes, so panes add observability, not new concurrency.
6. **`delegation.transport`: `native | auto | herdr`, default `native`, one key.** One key covers
   both on/off and policy. `native` probes nothing at step 0 and announces nothing. `auto` stays
   silent when `HERDR_ENV` is unset and announces once if Herdr is present but a later check fails.
   `herdr` announces any failed check once. All three degrade to `native` and never beyond: a failed
   Herdr run never skips the phase, never opens a third CLI, and never acquires a flag it did not
   already have.
7. **No tier vocabulary.** Roles map to workers only through `models.<role>`; "tier" stays banned
   repo-wide (enforced by `TierVocabularyTest`).
8. **The result contract.** Run directory: `$(git rev-parse --absolute-git-dir)/jdi/runs/<run-id>/`
   (`--absolute-git-dir` over `--git-dir` because the worker needs an absolute path; in a linked
   worktree this resolves under `<common>/.git/worktrees/<name>`, giving one run directory per
   worktree). The Butler writes `manifest.json` (after the pane split and before `agent start`, so it
   carries the real `pane_id`; environment keys only; never edited afterward - the smoke test
   found the original "before the spawn" order could not hold, see Remaining work, defect (c)) and
   `prompt.md`. The worker writes `report.md`, then, last, `result.json`.
   The Butler writes `outcome.json`. A terminal transcript is never the result; `agent read` is for
   inspection only.
9. **Blocked dialogs belong to the user; the Butler never sends keys.** `herdr agent prompt` rejects
   a blocked agent with `agent_blocked` before sending any input (verified in `--help`), so a
   content question is answerable only once the worker is idle again. Content questions therefore
   travel through `result.json`'s `needs_input` status, not through a Herdr `blocked` state. The
   Butler answers a worker's question only from context it already holds, and says so; otherwise it
   relays the question to the user.
10. **"Validate, never repair" (`/jdi:herd`) versus "detect, never repair" (role delegation).**
    `/jdi:herd` has no fallback - a herd that quietly became one sequential `/jdi:prep` would look
    exactly like a herd that worked, so it stops on the first failed check instead. Role delegation
    starts no server and installs no integration, but always falls down the ladder to a native run
    on failure, because a phase that never ran is the real failure there.
11. **Herd names, worktrees, scratch branches, and the cleanup guard.** Herd agents, tabs and
    worktree folders share one name per issue, `<slug>-<suffix>`: a short slug of the issue title
    (read with T2, built the way T6 builds a branch slug) and the issue's short ID, the repo's own
    short-ID convention where it states one, else the lowercased issue ID. A UUID-keyed ID alone
    reads `jdi-herd-f4960613-9705-48f4-a555`; the title gives `copy-lands-below-f4960613`. The herd
    cannot reuse prep's plan slug, because it names the agent before prep runs. With no title, the
    name falls back to `jdi-herd-<issue>` (Herdr rejects a bare numeric agent name, so a name that
    would not start with a letter gets `jdi-`). Worktree folders are `<worktrees dir>/<repo>/<name>`,
    so a crashed or closed workspace is found again by folder name even if prep never reached its
    branch step, and `herdr worktree open` reattaches it. An existing folder is matched on its
    `-<suffix>` ending, because a second herd can pick different slug words. The workspace label
    is the short ID and the full title.
    Scratch branches are `jdi-herd-scratch-<herd-id>-<N>`: PR #5's `jdi-herd-scratch-<N>` collides on
    a second herd run in the same repo (observed on this machine) because it omits the issue ID.
    Before removing a worktree, `/jdi:herd` checks the plan folder with `git status --porcelain`,
    names any uncommitted files, offers a `docs: Add <slug> plan` commit, and never forces removal
    without an explicit yes.
12. **JDI never names or resumes harness sessions.** The plan on the branch (`PLAN.md`, each task's
    `status:`, one commit per task) is the durable state; a fresh session in a herd worktree picks
    the work up with `/jdi:status` or `/jdi:yolo`. No session-name flag is passed. The model flag
    stays the only flag JDI composes on any separate-process path, exec or Herdr.
13. **Version 1.0.10** across `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and
    `.claude-plugin/marketplace.json`.
14. **A worker cannot always write under `.git` without a dialog.** Codex's `workspace-write`
    sandbox keeps `.git` read-only (openai/codex#15505, #14338), so a Codex worker cannot write
    `jdi/runs/` there without a user-supplied writable root. This is why H7 treats a missing result
    as a validation failure rather than assuming success, and why Scenario C in the UAT carries an
    explicit writable-root step.

## Plan gaps caught during execution

None surfaced during the automated implementation (Tasks 01-09); the design settled in the
2026-09-24 revision above, before the plan was split, and the Executors matched it without further
research gaps. The live UAT (Task 10, still pending) is where gaps between the documented mechanism
and its live behavior actually surfaced - see Remaining work below, which is exempt from
compression for exactly this reason.

## Outcome

### Shipped

| Batch | Area | Commit |
|---|---|---|
| Wave 1 | `reference/herdr.md`, H1-H8, `HerdrOperationsTest` | `2b18c0c` |
| Wave 1 | `delegation.transport` config key and schema | `4e0431f` |
| Wave 1 | Transport rewrite: `reference/delegation.md`, `roles/butler.md`, `agents/feedbacker.md` | `f64bd6b` |
| Wave 2 | User docs: `commands/init.md`, `commands/help.md`, `README.md` | `86e40c8` |
| Wave 2 | `docs/delegation-transport-architecture.md` and architecture doc updates | `8ebaae0` |
| Wave 3 | Step-0 transport line in nine delegating commands | `01420dc` |
| Wave 3 | `herd:` config block | `dfb27f6` |
| Wave 3 | `commands/herd.md`, H9, command enumerations | `cb44ff2` |
| Wave 4 | Release 1.0.10 (version bump, CHANGELOG) | `802a9cc` |
| Wave 5 | Task 10 run log: agent smoke test recorded (task itself still pending) | `5af2893` |

See `git log origin/main..HEAD` for the full commit list and its exact count; that range includes
the plan-approval commit and will include the commit that stores this file, so no total is stated
here on purpose.

### Deferred

Issue: none for this plan, so nothing was filed under a tracked issue as a formal deferral. The
open items are Task 10 itself (UAT, not yet walked by a user) and the post-merge closure of PR #5 -
both carried in full under Remaining work below, since the task files that would otherwise hold them
are deleted at `/jdi:pr` time.

## Test result

Automated: `python3 -m unittest discover -s tests -v` - 110 tests, OK at `5af2893`, matching every
task's own report and the run log's Scenario L.

Live UAT: **not user acceptance.** An agent smoke test of Task 10's procedure ran on 2026-09-24
(recorded as a run log appended to that task file, commit `5af2893`), with an Executor agent playing
the user and driving a Butler under test. As the run log records it:

- The probe gate passed with no contradiction of `reference/herdr.md`.
- Passed: B, D, F, I, J, K, L, and G(1), G(2), G(4), G(7).
- Passed with a failed item or a note: A (the H4 pre-spawn line was never printed); E (only on its
  second wording); E2 (first case; the second case was not induced); G(5) (the announcement came
  only in the final summary); G(6) (the fallback ran degraded instead of reaching the floor); H
  (`/jdi:plan` and the 1.0.8 comparison not run); I (the five-task cap check not run); K (the
  UAT-3 crash step not run).
- Partial: G(3) (no pane, but the Butler ran `herdr status` under `native`).
- Not run: C (Codex is not installed).

Two branch defects and several documentation gaps surfaced - see Remaining work. Task 10 stays
**pending**: a smoke test of the mechanism is not a user walking the procedure.

## Remaining work

This section is exempt from compression: the task files it draws from are deleted once this plan is
condensed, so this is the only place the outstanding UAT procedure, the defects the smoke test
found, and the follow-ups it produced will still exist.

### 1. UAT (Task 10) is not done

Walk this procedure, recording each command and its raw output, before treating the branch as user-
accepted. Scenario K applies only because the herd wave (Tasks 07-08) shipped; if it had not, skip K
and its AC 9 row.

**Setup (U0).**
1. Confirm a Herdr pane (`printenv HERDR_ENV` = `1`, `herdr status` shows `running`/`compatible`).
   Record `herdr --version` (0.8.2 when planned), `claude --version`, `opencode --version`, and
   `command -v codex`.
2. Scratch clone: `git clone <this repo> /tmp/jdi-uat && cd /tmp/jdi-uat && git checkout
   herdr-role-delegation`. Local origin, so nothing reaches GitHub.
3. `/tmp/jdi-uat/.jdi/config.local.yml` (gitignored) starts every scenario with `tracker: {name:
   none}`.
4. Load the branch's plugin: disable the installed `jdi@just-do-it`, start the Butler with `claude
   --plugin-dir <repo>` in a Herdr pane, accept the trust dialog, confirm `/jdi:help` prints
   "Separate agent processes". Fallback if `--plugin-dir` does not expose `/jdi:*`: uninstall and
   reinstall from a marketplace pointing at the checkout. **Carry forward from the smoke test:** the
   tester's global `~/.config/opencode/opencode.json` was invalid for OpenCode 1.18.x
   (`Unrecognized key: agents`), so every OpenCode pane needs
   `harnesses.opencode.env: {XDG_CONFIG_HOME: <scratch dir>}` pointed at a folder that symlinks
   Herdr's OpenCode state plugin, or OpenCode panes will not start correctly. This is a workaround
   for a broken global config, not a JDI defect, but it will still be needed on the next run.
5. Pick an OpenCode model: `opencode models | head` -> `<OC_MODEL>`.

**Pre-flight probes (U1), by hand in a second pane, closing each probe's pane afterward.**
- P0: split a pane then `agent start` an opencode worker -> expect `agent_started`; a failure from
  an unready shell is an H4 finding.
- P2/P3 (opencode): confirm `--env` reaches the worker and it can write inside `.git`; a missing
  output file means "blocked on permission" is the P3 answer.
- P1a: a 3000 ms wait timeout -> record the `timeout` code, which stream it arrives on, and the exit
  status.
- P4: `pane close` must stop the opencode process and drop the agent from `agent list`; survival is
  an H8 finding (an explicit quit needed before close).
- P1b/P3 (claude): start on `--model sonnet`, trigger a Bash approval -> expect `blocked`; a further
  prompt must return `agent_blocked` before any input is sent; after approving, test whether a write
  under `.git` also needs its own permission.
- P1c: an empty-string prompt, to test `agent_prompt_stalled`; if it does not appear, record "not
  induced".
- P5: a trust dialog on a brand-new repo -> expect `agent_not_ready`; do not answer it.
- P6: capture `agent get` JSON for idle/working/blocked and a successful `prompt --wait`; confirm
  which field carries the state and that H5's wording matches.
- P3 (linked worktree): `git worktree add`, confirm `--absolute-git-dir` resolves outside the
  worktree, repeat the opencode and claude write probes there.
- P8: `herdr worktree create --path <full folder path>`, confirm `.result.worktree.path` echoes it;
  clean up.
- P7: `herdr integration status` for claude and opencode.

**Probe gate.** Any probe that contradicts `reference/herdr.md` stops the UAT: fix H4, H5, H6 or H8
in a commit, record it, and re-run the affected probes before continuing.

**Scenarios (U2).** After each, confirm `herdr agent list` and `herdr pane list` show no leftover
`jdi-*` agent or pane.
- **A** (AC 1,2,4,5,6). Full `/jdi:prep` with the Researcher on OpenCode (`transport: auto`).
  Expect: no step-0 announcement; the `JDI spawn` line (`reference/delegation.md`, *Where a role
  runs*) naming the run ID, role, kind, model, every argument, the env keys, the run directory and
  the agent name, printed before `pane split`; an unfocused new pane; the Butler waiting and doing
  nothing else; a run directory with `manifest.json` and `prompt.md`, then `report.md`, `result.json`
  (`complete`), and `outcome.json` (`final: valid`, `pane_closed: true`); validation stated before
  the citation spot-check and before `## References` is updated; the pane closed. The Planner and
  Splitter have no `harness` set, so they run as native subagents: no pane, no run directory, no
  transport text for them.
- **B** (AC 6,8). Same-harness control: Researcher `{sonnet, claude}` under a Claude Butler, via
  `/jdi:reresearch`. Expect a native subagent: no pane, no run directory, no pre-spawn line, no
  transport announcement, no `jdi-*` agent.
- **C** (requires installing Codex first). (1) Sandboxed `workspace-write`: expect the worker fails
  to write under `.git` (openai/codex#15505, #14338), so H7 fails (`JDI-RESULT-UNWRITABLE` or a
  missing `result.json`), the pane closes, and the role falls to `codex exec` (rung 2); the phase
  completes. (2) Add a writable root for the run directory to `harnesses.codex.args` (confirm the
  flag with `codex --help` first - it is unverified); re-run and expect a valid result.
- **D** (AC 3). Blocked on an approval: OpenCode configured to ask before shell commands. Expect the
  Butler to report `blocked`, show `agent get`/`explain`/`read` output, ask the user rather than
  answer, and offer to focus the pane; after the user approves in the pane, the Butler resumes and
  validates; no `send-keys` anywhere in the transcript.
- **E** (AC 3). Content question: the task description asks the worker to question the Butler before
  finishing. Expect `result.json` `needs_input`, the file moved to `result.needs_input.1.json`, an
  answer sent from context the Butler already holds (stated as such), then a valid result.
  Best-effort - record whether it was induced.
- **E2** (AC 2,3). Question asked in chat, no result file: the task description asks the worker to
  ask in chat and wait. Expect the Butler to read the pane, name it by agent name and pane ID, say
  the user can answer there, and keep waiting with no resubmit; answering there yields a valid
  result. Repeat with "stop without writing any file": expect an H7 validation failure, the pane
  closed, and a re-run through the CLI's non-interactive mode. Best-effort - record whether each
  case was induced.
- **F** (AC 3,4). Timeout: a short per-call wait and overall deadline. At the deadline expect
  inspection output with no success claim and no resubmit, then a choice of keep-waiting / accept-a-
  checked-file / abandon. Choosing abandon should give `outcome.json` `final: abandoned`, the pane
  closed, one announcement, then a non-interactive retry. Repeat three times with no leaked pane.
- **G** (AC 6), seven sub-cases. (1) `transport: herdr` outside Herdr: exactly one step-0
  announcement naming `HERDR_ENV`, then native delegation, phase runs. (2) `transport: auto` outside
  Herdr: complete silence about the transport. (3) `transport: native` inside Herdr: no pane, a
  native subagent for a role with no harness, the CLI's non-interactive mode for a role on another
  CLI, no transport text. (4) `harness: qwen` (a kind Herdr supports but that is not installed): one
  "supports but not installed" announcement, then the floor. (5) `transport: sometimes` (invalid):
  one announcement, then native. (6) an unlaunchable environment (bad `PATH`): H4 fails, the pane
  closes and is announced, and the exec fallback runs. Corrected after the smoke test: when the
  Butler resolves the CLI's absolute path before it applies the broken `PATH`, the fallback launches
  and returns a report degraded by that `PATH` (its tools fail), the phase completes, and the floor
  is not reached. Only a fallback that cannot launch the binary fails and reaches the floor. Either
  way, one announcement per failure; record which outcome happened. (7) an unreachable Herdr socket
  under `transport: herdr`: the H1 check-(c) announcement, or "not induced" if Herdr ignores the
  variable.
- **H** (AC 8). Backward compatibility: remove the `delegation` key and run `/jdi:research` and
  `/jdi:plan`. Expect no pane, no transport text, and behavior identical to a 1.0.9 run (compare
  against the installed plugin as a reference).
- **I** (AC 2,3,6). A wave of Executors on another CLI: two disjoint-`## Files` tasks, OpenCode set
  to ask before shell commands. Run `/jdi:execute`. Expect one `jdi-wave-<first run id>` tab with one
  pane per task started together, one run directory and `allowed_writes` per task, the Butler
  waiting on both with no other work, one worker's block named and asked about while the other keeps
  running uncanceled, the user's approval resuming the wait, both results validated, the combined
  file check passing, one commit per task by path, and every pane plus the tab closed. Best-effort
  cap check: a five-task wave opens at most 4 panes at once.
- **J**. Feedbacker independence, as `commands/feedback.md` step 3 requires it: where the config maps
  more than one model, the review runs on a different model or a different harness from the
  producer, and a statement is required only when neither differs. A Claude Feedbacker
  (`{sonnet, claude}`) reviewing an OpenCode Researcher's output should run on its configured model
  and harness; no "they differ" statement is required. An OpenCode Feedbacker on the same model and
  harness as the Researcher should still run, and the Butler should say that producer and reviewer
  were the same.
- **K** (AC 9, 9a; only if the herd wave shipped). `/jdi:herd UAT-1 UAT-2`. The scratch clone runs
  with `tracker: {name: none}`, so T2 reads no title and the herd takes the fallback path: expect
  one note naming both issues as fallbacks, two worktrees and two agents named
  `jdi-herd-uat-1`/`jdi-herd-uat-2` with matching tab and folder names, and workspaces labeled
  with the issue IDs. K does not exercise title-based `<slug>-<suffix>` names; that needs a real
  tracker and real issues, and `commands/herd.md` step 5's worked examples state the expected
  names. Each agent gets `/jdi:prep <ISSUE-ID>` sent with no wait, and a report naming its worktree
  path and scratch branch.
  Then: a workspace closed by hand before prep reaches its branch step still leaves the worktree
  findable by folder name, and `herdr worktree open` reattaches it; requesting an existing folder
  reports its branch/plan state and asks to continue or skip rather than duplicating it; a second
  herd run in the same repo gets different scratch-branch IDs; a fresh session in an orphaned
  worktree recovers the plan with `/jdi:status` and no prior session needed; the cleanup guard names
  any uncommitted plan files, offers the `docs: Add <slug> plan` commit, and does not remove the
  worktree until the user answers; under the fallback, GitHub-style issue `4` is named
  `jdi-herd-4` and an over-length ID is cut to Herdr's 32-character rule; an existing folder is
  found by its `-<suffix>` ending (create `<worktrees dir>/<repo>/other-words-uat-1` by hand first,
  and expect the herd to report it for UAT-1 rather than create a second folder);
  requesting an already-live herd name reports its holder and asks instead of duplicating it. Outside
  Herdr, `/jdi:herd` stops with the H1 reason and never falls back to a sequential prep.
- **L** (AC 10). `python3 -m unittest discover -s tests -v` passes, with `HerdrConfinementTest`
  included in the run.

**Cleanup (U3).** Close any probe pane still open; remove the herd worktrees with the commands H9
printed; remove the linked worktree; delete the scratch clone(s); re-enable the installed plugin.

**Acceptance-criteria mapping.**

| AC | Proven by |
|---|---|
| 1. Researcher delegated to a separate Herdr agent under `/jdi:prep` | Scenario A |
| 2. The Butler waits and resumes on settled or blocked | A, D, E2, I |
| 3. A blocked worker is inspected and handled deliberately | D, E, E2, F, I |
| 4. Completion requires a valid artifact | A, C1, F, `HerdrOperationsTest` |
| 5. Validation happens before `PLAN.md` changes | A, `ValidationGateTest` |
| 6. A different harness and model for the worker | A, C, I; B is the same-harness control |
| 7. Unavailable/disabled/misconfigured/unlaunchable Herdr announces and falls back | G(1)-(7), `TransportSelectionTest` |
| 8. No new keys means today's behavior | H, `DelegationBlockTest` |
| 9. `/jdi:herd` stays ticket-level fan-out | K, `HerdCommandTest` |
| 9a. Herd folder names its issue; plan continues from a fresh session; cleanup never deletes an uncommitted plan | K |
| 10. Bodies stay provider-neutral | `HerdrConfinementTest` |
| 11. Every lifecycle-required site is updated | Task 02/05/07/08/09 tests, plus the `grep` checks |
| 12. The suite passes | L |
| 13. A live procedure exists | this task |

### 2. Defects the smoke test found

Defects (a), (b) and (c) are fixed on the branch. An agent re-check on 2026-09-24 (see the end of
this section) passed for (b) and failed for (a). A second agent re-check the same day passed for
(a) at `2c2370d`. (c) remains pending re-check in UAT, and none of the three has user acceptance.

(a) **The H4 pre-spawn line never printed.** Fixed on the branch; agent re-check passed (not user
acceptance). In Re-check 2 the Butler also repeated the line in a visible message in the same turn
(criterion 3 held). The first fix:
`reference/delegation.md` *Where a role runs* now gives a fixed `JDI spawn` template for every
separately spawned process, H4 makes it step 1, and `roles/butler.md` names it beside the skip
announcements. What the smoke test saw: on every Herdr spawn (Scenarios A, D, E, E2, F, G6, I,
J2), the text before `agent start` was only a sentence like "Next I check whether Herdr can run the
Researcher on OpenCode" - never the agent name, kind, model, arguments, env keys, and run directory
that `reference/herdr.md` H4 required. The rule lived only in that one doc section with nothing
enforcing it at the call sites, so it was easy to skip.
After the re-check below failed, a second fix ties the line to the spawn: the same shell command
prints the `JDI spawn` line and then spawns (`printf ... && <spawn command>`, and in H4 step 1
`printf ... && herdr pane split ...`), and `manifest.json` records the printed line in
`"spawn_line"`. Re-check 2 below verified this second fix in a live run.

(b) **A `native` Butler still probed Herdr, and summaries broke silence.** Fixed on the branch;
agent re-check passed (not user acceptance): the step-0 line in the nine delegating commands and H1 now say to run no
Herdr command at step 0 under `native` or with no `delegation` key, and to mention the transport
nowhere in the run, summaries included. What the smoke test saw: under `transport: native` inside
Herdr (Scenario G3), the Butler still ran `herdr status` at step 0, though `reference/delegation.md`
says nothing is probed at step 0 under `native`. Several run summaries (Scenarios B, G3, H) also
mentioned the transport by name even though the ladder says to stay silent in those cases.

(c) **Three documentation gaps in `reference/herdr.md`.** Fixed on the branch, pending re-check in
UAT: H4 now creates the pane, then writes `manifest.json` and `prompt.md`, then starts the agent;
H6 adds `--source detection`; H8 says `tab_not_found` is expected after a wave. What the smoke test
saw: the manifest was described as "written once, before the spawn, never edited afterward", but its
`pane_id` field is only known after H4's `pane split` runs, so every run in the smoke test wrote
`null` and edited it in afterward. In a half-width wave pane, only `agent read --source detection`
showed the OpenCode dialog; `--source visible` and `--source recent-unwrapped` did not. Herdr closes
a tab itself once its last pane closes, so H8's `herdr tab close` after a wave returns
`tab_not_found` - harmless, but undocumented.

**The UAT spec itself was off in two places.** Both are corrected in section 1 (Scenarios J and
G(6)). Scenario J expected a "the producer and reviewer differ" statement from the Butler, but
`commands/feedback.md` only requires a statement when they are the *same* - the smoke test's
expectation was stricter than the command it was testing. Scenario G(6) expected the exec fallback
to fail alongside the Herdr path, but the Butler resolved `opencode`'s absolute binary path before
applying the broken `PATH`, so the fallback ran (with a degraded report) instead of reaching the
floor.

**Not run or not induced:** Scenario C (Codex not installed); Scenario E2's second case (worker
wrote a valid result both times instead of stopping without one); the claude write probe against a
linked worktree (the default-mode dialog already covers it); the UAT-3 crash-recovery step in
Scenario K (partially covered via UAT-1 instead); the five-task wave pane-cap check in Scenario I;
Scenario H's `/jdi:plan` run and its comparison against the installed 1.0.8 plugin.

### Re-check (agent smoke test, 2026-09-24)

An agent ran this re-check, not the user. Each check used a fresh Butler (`claude --plugin-dir
<repo> --permission-mode bypassPermissions`, installed plugin disabled) in its own Herdr pane, in the
scratch clone at `3b2749b`, running `/jdi:research` on the clone's `herdr-role-delegation` plan.
Worker model: `opencode/big-pickle` (OpenCode Zen free tier). A probe of `mimo-v2.6-flash-free`
returned no output, so this run did not use it.

**Check 1, defect (a), the spawn line: FAIL.** Config: `delegation: {transport: auto}`,
`tracker: {name: none}`, `models.researcher: {model: opencode/big-pickle, harness: opencode}`,
`harnesses.opencode.env: {XDG_CONFIG_HOME: <scratch>/xdg}`. No `PATH` entry was needed. The Butler
printed no `JDI spawn` line. The session transcript (`1b86c7e1-...jsonl`) has no text block with
`JDI spawn <run-id>` in it. The only text between the run setup and the pane split was a thinking
narration that the Claude Code UI shows:

```text
Herdr's OpenCode integration is outdated (v9 < v10), which may make lifecycle detection less
reliable. I'm spawning a researcher agent (20260925T053238Z-researcher-a456) on opencode to investigate.
```

The next tool call was `herdr pane split ... --env XDG_CONFIG_HOME=... --no-focus` (pane `w3A:pT`).
The final summary still said "The JDI spawn line printed before the pane split, with the agent
name included". That claim is false. The rest of the run passed. The manifest was written once,
after the split, in the same command as `agent start`, and no later command edited it
(`manifest.json` mtime 23:33:18, equal to `prompt.md`):

```text
"herdr": {"butler_pane_id": "w3A:pS", "pane_id": "w3A:pT", "agent_name": "jdi-researcher-a456", ...}
"worker": {"kind": "opencode", "model": "opencode/big-pickle", "args": [], "env_keys": ["XDG_CONFIG_HOME"]}
```

`outcome.json`: `"final": "valid"`, `"pane_closed": true`. That result confirms the manifest part of
defect (c) only; the other parts of (c) were not exercised.

**Check 2, defect (b), native silence: PASS.** Config: `delegation: {transport: native}`, no role
harness (Researcher native, `model: opus`). The Butler's six Bash calls at step 0 and afterward
read config, plans and git state only. None ran `herdr`, `printenv HERDR_ENV` or `herdr status`.
The Researcher ran as a native `jdi:researcher` subagent, and its 28 tool calls ran no `herdr`
command either. No pane was opened. No message says which transport the run used. The setup note
says only that `.jdi/config.local.yml` "overrides the `tracker`, `jev`, and `delegation` blocks".
Each Herdr mention in the final summary is a research finding about this plan's subject, for
example "`native` runs no Herdr command at step 0", and none describes this run's delegation.

### Re-check 2 (agent smoke test, 2026-09-24)

An agent ran this re-check, not the user. It repeated Check 1 above with the same config and setup,
in the scratch clone at `2c2370d`. The Butler was a fresh session (`claude --plugin-dir <repo>
--permission-mode bypassPermissions`, installed plugin disabled) in its own Herdr pane, running
`/jdi:research`. Transcript: `497b3697-30ca-466e-83cb-f10bd67490ed.jsonl`. Worker:
`opencode/big-pickle`. The run finished in one turn with no questions to answer.

**Criterion 1, the line and the split are one command: PASS.** The Bash call that created the
worker pane was:

```text
printf '%s\n' "JDI spawn 20260925T055127Z-researcher-bed6: Researcher on opencode (opencode/big-pickle) - args: none - env keys: XDG_CONFIG_HOME - run dir: <clone>/.git/jdi/runs/20260925T055127Z-researcher-bed6 - agent: jdi-researcher-bed6" && herdr pane split --current --direction down --cwd <clone> --env XDG_CONFIG_HOME=<scratch>/xdg --no-focus
```

Its tool result starts with the printed line, then the split's JSON (`"pane_id":"w3A:pX"`).

**Criterion 2, the manifest: PASS.** `manifest.json` has `"spawn_line"` equal, character for
character, to the printed line, and `"pane_id": "w3A:pX"`. The Butler wrote it once, after the
split and before `agent start`. No later command wrote to it.

**Criterion 3, the line in a visible message: PASS, with one limit.** The text block just before
the split said only "Printing the spawn line and splitting the worker pane in one command:". The
line itself appears verbatim, in a code block, in the final visible message of the same turn, under
**Delegation**. So the repeat came at the end of the turn, not next to the spawn.

**The summary's claim is true.** The final message says "The line above is from the pane-split
command's own output." The tool result above confirms it. The rest of the run also passed:
`outcome.json` has `"final": "valid"` and `"pane_closed": true`, and the worker agent was gone from
`herdr agent list` afterward.

### 3. Follow-ups

- **OpenCode 2.0 preview (`opencode2`) is not a Herdr kind.** A scoped fish function works as a
  stopgap for a user running it; proper support belongs in a separate task, not this one.
- **Codex scenario C was not run** because Codex is not installed on the machine that ran the smoke
  test; it needs a real run before Codex support is considered proven.
- **Several citations in `docs/config-key-lifecycle.md` were already stale on `main`** before this
  plan started (independent of this work) and were only partly corrected by Task 08's pass.
- **The task files' own verification commands do not run as written.** Every task specifies
  `python3 -m unittest tests.<module>`, which fails from the repository root with
  `ModuleNotFoundError: No module named 'jdi_files'` (confirmed independently). The form that works
  is `python3 -m unittest discover -s tests -p '<file>.py' -v`. Future plans should specify the
  working form.
- **After merge, close PR #5 (`origin/herd-command`) as superseded** - the herd wave shipped in
  Tasks 07-08, so PR #5's `herd.args`/`herd.env` plumbing is replaced. Closing it is the PR author's
  job once this branch actually merges; it is not something this plan or its UAT can do.
