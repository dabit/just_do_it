# Herdr operations

Herdr is a transport. A Butler uses it to run a delegated role that is configured on another CLI
as that CLI's **interactive agent**, in a pane the user can answer, and to wait for it. This file
says what each Herdr operation does, which `herdr` commands it runs, and what the Butler does with
what comes back. `reference/delegation.md` calls the operations **by name**: rung 2 (under
`delegation.transport: auto` or `herdr`) and rung 4.

`herdr` below means `$HERDR_BIN_PATH` when that is set, else `herdr` on `PATH`. Commands are
argument lists, and placeholders are in angle brackets.

Everything in this file is inert under `delegation.transport: native`, except where rung 4 sends a
kind with no exec mode.

## The universal rules

1. **Capability is observed and never inferred from the harness name.** Herdr is available only
   when H1's checks pass in this session.
2. **Detect, never repair.** JDI starts no server, installs no integration, and changes no Herdr
   setting. When Herdr cannot be used, the Butler falls down the ladder in
   `reference/delegation.md`.
3. **A Butler runs one phase at a time.** Inside a phase, only a wave runs several workers at once,
   and the Butler waits for all of them and does nothing else in the command meanwhile.
4. **The result arrives through a file.** A terminal transcript is never the result. `agent read`
   is for inspection only.
5. **`idle` or `done` is not proof of success, and `unknown` or `timeout` never counts as
   success.** Only H7 decides that a run succeeded.
6. **The Butler never resubmits blindly.** A prompt that may have been sent is never sent again
   without evidence that it was not.
7. **The worker's dialogs belong to the user.** Approval, permission, trust and question dialogs go
   to the user, who answers them in the worker's pane.
8. **A pane JDI created is closed on every exit.** See H8.
9. **A worker is a separately spawned CLI.** Its authority comes from its own configuration and
   from the arguments the user wrote in `harnesses.<kind>.args`. JDI adds no authority-affecting
   flag of its own.

## Scope

- Only a role whose `models.<role>.harness` names another CLI reaches these operations. A role on
  the Butler's own CLI never runs under Herdr: it stays a subagent, watchable in the harness
  itself.
- Any such role qualifies. The single roles (Researcher, Planner, Splitter, Synthesizer, PR Writer,
  Feedbacker) run one worker each. Executors in a wave run one worker per task (`## Waves`).
- A worker uses the Butler's own worktree, because the Butler waits for it.
- Butlers started by `/jdi:herd` are isolated from each other by worktrees.

## H1 - Detect Herdr

The Butler performs H1 **once**, at step 0, and there only under `auto` or `herdr`. Under `native`,
or with no `delegation` key, H1 does not run at step 0: no Herdr command runs at step 0, and nothing
in the run mentions the transport, summaries included. The one exception is rung 4 of
`reference/delegation.md`, which runs H1 when it delegates a kind with no exec mode and announces
what fails. The checks run in order, and the first failure wins:

- (a) `printenv HERDR_ENV` prints `1`.
- (b) The binary resolves: `$HERDR_BIN_PATH` is executable, else `command -v herdr` resolves.
- (c) `herdr status` reports the server as `status: running` and `compatible: yes`, and
  `HERDR_SOCKET_PATH`, when it is set, is an existing socket.

The answer is either "available" or the first failed check with its output. The Butler uses that
answer for every delegation in the run. No role re-probes.

The announcement depends on the configured value:

- `auto` stays silent when `HERDR_ENV` is unset. That is the expected absence outside Herdr. It
  announces once when `HERDR_ENV=1` but a later check fails, because that is a malfunction.
- `herdr` announces any failed check once.

Capability comes from these checks, never from the harness name. Detect, never repair: a stopped
server or an incompatible version is reported, and JDI does not start, upgrade or configure
anything.

## H2 - Check the worker kind

- The kind is `models.<role>.harness`, and only that. A role with no `harness`, or one that names
  the Butler's own kind, never reaches this operation.
- Supported: the kind appears on the `kinds:` line of `herdr agent`. That line **lists the kinds
  Herdr supports**, not the kinds installed.
- Installed: `command -v <kind>` resolves.
- `herdr integration status` affects only detection quality. The Butler records its answer in the
  manifest and states it once when the kind's integration is missing or outdated (for example,
  "lifecycle states for claude come from screen rules").

The model flag, by kind:

| Kind | Model flag | Status |
|---|---|---|
| `claude` | `--model <model>` | verified in `claude --help` |
| `opencode` | `-m <provider/model>` | verified in `opencode --help` 1.18.10 |
| `codex` | `-m <model>` | not verified here: `codex` is not installed |

For a kind with no known flag, rung 10 of `reference/delegation.md` applies. The model flag comes
before the verbatim `harnesses.<kind>.args`.

With no `models.<role>.model`, no flag is passed, and the worker runs on its CLI's own default. The
Butler says so in the `JDI spawn` line (H4).

## H3 - Prepare the run

**Names.** The run ID is `<UTC yyyymmddThhmmssZ>-<role>-<4 hex>`. The agent name is
`jdi-<role>-<4 hex>`, which matches Herdr's `[a-z][a-z0-9_-]{0,31}` (for example
`jdi-researcher-7f3a`, 20 characters). The Butler checks `herdr agent list` for a collision and
draws a new suffix if it finds one.

**The run directory.** Run `git rev-parse --absolute-git-dir`, then
`mkdir -p <gitdir>/jdi/runs/<run-id>/`. A failure here is a transport failure. In a linked
worktree the git directory is `<common>/.git/worktrees/<name>`, so each worktree has its own runs.

The run directory holds five files:

| File | Written by | When |
|---|---|---|
| `manifest.json` | the Butler | in H4, after the pane split and before `agent start`; never edited afterward |
| `prompt.md` | the Butler | in H4, with `manifest.json` |
| `report.md` | the worker | first |
| `result.json` | the worker | last |
| `outcome.json` | the Butler | at H8 |

H3 fixes the names, creates the run directory, and composes both Butler files. H4 writes them once
the pane exists, because `manifest.json` records the new pane's ID and is never edited afterward.

**`manifest.json`.** Environment values are never recorded, only the keys.

```json
{
  "schema": 1,
  "run_id": "<UTC yyyymmddThhmmssZ>-<role>-<4 hex>",
  "role": "researcher",
  "command": "prep",
  "plan": "<abs path to PLAN.md>",
  "ticket": "<Issue: value from PLAN.md, or none>",
  "base_commit": "<Base commit SHA from PLAN.md>",
  "head_commit": "<git rev-parse HEAD at launch>",
  "cwd": "<abs worktree root>",
  "transport": "herdr",
  "herdr": {
    "workspace_id": "<HERDR_WORKSPACE_ID>",
    "tab_id": "<HERDR_TAB_ID>",
    "butler_pane_id": "<HERDR_PANE_ID>",
    "pane_id": "<from pane split>",
    "agent_name": "jdi-<role>-<4 hex>",
    "integration": "<what herdr integration status reported for the kind>"
  },
  "worker": {"kind": "opencode", "model": "<value or null>", "args": ["<verbatim>"], "env_keys": ["<KEY>"]},
  "prompt": "<abs>/prompt.md",
  "expected": {"report": "<abs>/report.md", "result": "<abs>/result.json"},
  "allowed_writes": ["<abs>/report.md", "<abs>/result.json"],
  "created_at": "<UTC ISO 8601>",
  "deadline_ms": 2700000
}
```

For the Splitter role, `allowed_writes` also lists the plan folder's task files and `PLAN.md`,
because `agents/splitter.md` returns "Task files written to the plan folder". For an Executor in a
wave, `allowed_writes` is its task file's `## Files` plus its run directory (`## Waves`).

**`result.json`.** The worker writes it last, with the fields `run_id`, `role`, `status`
(`"complete"`, `"needs_input"` or `"failed"`), `report` (`"report.md"`), `head_commit` and
`summary`. With `"needs_input"` it adds `"questions"`, a list of strings. With `"failed"` it adds
`"reason"`.

**`prompt.md`.** The template is literal except for the `<...>` placeholders, and the line breaks
are its own:

```markdown
# JDI delegated run <run-id>

A JDI Butler started you to perform one JDI role, and it is waiting for your result. Nobody
reads your terminal output as the result: only the files named below count.

## Your role

<the body of agents/<role>.md, frontmatter removed, copied verbatim>

## Your inputs

<exactly the items the role's "What it receives" lists: short values written inline, file
inputs as absolute paths>

## Where you work and what you may change

- Work in <cwd>. The plan was written against <base commit>. Do not change branches, commit,
  push, stash, reset, or rebase.
- Write only these paths: <allowed_writes, one per line>.
- Do not write to an issue tracker or any other external system.
- If a tool asks for approval, leave the dialog for the user. Do not look for a way around it.

## Result contract

1. Write your complete report, in markdown, to <abs run dir>/report.md. It must contain every
   item listed under your role's "What it returns".
2. Then, last, write <abs run dir>/result.json:
   {"run_id": "<run-id>", "role": "<role>", "status": "complete", "report": "report.md",
    "head_commit": "<output of git rev-parse HEAD when you finish>", "summary": "<one line>"}
3. If you need an answer before you can finish, do not open a question dialog. Write
   result.json with "status": "needs_input" and "questions": ["..."], then stop. The Butler
   will reply in this session.
4. If you cannot do the work, write result.json with "status": "failed" and "reason": "...".
5. If you cannot write to <abs run dir> at all, end with exactly
   JDI-RESULT-UNWRITABLE <run-id>: <reason>
6. When both files are written, reply with only: JDI-DONE <run-id>
```

- The role instructions are the installed `agents/<role>.md` body with its frontmatter removed.
  The Butler reads it with the same resolution it uses for `reference/`, copies the text, and never
  hands the worker a plugin path (`docs/harness-adapter-architecture.md:192-195`).
- The inputs are exactly the role's *What it receives*. Short values are written inline, and file
  inputs are given as absolute paths.
- The short prompt the Butler sends is, verbatim:
  `Read <abs run dir>/prompt.md and follow it exactly. This is JDI run <run-id>.`

Run directories are kept. JDI never deletes them in this release. Removing a linked worktree
removes its git directory and its runs. The user may delete `<gitdir>/jdi/runs/` at any time.

## H4 - Start the worker

1. **Print the spawn line.** Print the `JDI spawn` line from `reference/delegation.md`, *Where a
   role runs*, with this run's ID and run directory, and append ` - agent: <agent name>`. Print it
   immediately before step 2, because the pane split starts the spawn. Nothing else runs in
   between. A spawn without this line printed first is a defect.
2. **Create the pane.**

   - A single role: choose the direction with `herdr pane layout --pane "$HERDR_PANE_ID"`
     (`right` for a wide pane, `down` otherwise), then create a sibling pane:
     `herdr pane split --current --direction <d> --cwd <worktree root> [--env KEY=VALUE ...] --no-focus`.
     Read the new pane's ID from `.result.pane.pane_id`.
   - A wave: every worker's pane goes in the wave's own tab (`## Waves`). The first worker uses
     the tab's root pane, and each later one splits a pane inside that tab.

   `--env` carries `harnesses.<kind>.env` verbatim, because `herdr agent start` has no `--env` or
   `--cwd` (verified in `--help`).
3. **Write the run files.** Write `manifest.json`, with the real `pane_id` from step 2, then
   `prompt.md` (H3). The manifest is written once, here, because the pane ID exists only after
   the pane split.
4. **Start the agent.**

   ```text
   herdr agent start <name> --kind <kind> --pane <pane_id> --timeout 120000 [-- <model flag> <args...>]
   ```

   Pass `--` only when something follows it.

   - `agent_started`: continue to H5.
   - `agent_not_ready`: go to H6 with the prompt unsent.
   - Any other error: H8, then fall back (`## When a step fails`).

### H4b - Start an agent in a given pane

The start command alone, applied to a pane and a name the caller supplies:
`herdr agent start <name> --kind <kind> --pane <pane_id> --timeout 120000 [-- <model flag> <args...>]`,
with the same three outcomes as above. `/jdi:herd` reuses it for panes it creates itself.

## H5 - Prompt and wait

Send the short prompt, then wait:

1. `herdr agent prompt <name> "<short prompt>" --wait --timeout 300000`
2. Loop `herdr agent wait <name> --timeout 300000` until a settled state appears or the overall
   deadline passes.

The overall deadline defaults to 2700000 ms. A value the user states in the conversation wins for
that run. Set the shell tool's own timeout above each call. Where the shell tool caps lower than
300000 ms, use its cap minus 30000 ms as the `--timeout`. Without `--timeout`, Herdr's wait is
indefinite (verified in `--help`), so `--timeout` is mandatory.

| Observed | Meaning | Butler action |
|---|---|---|
| `working` (a per-call `--timeout` expired) | still running | Under the overall deadline: print one progress line and loop `herdr agent wait`. At the deadline: go to the `timeout` row |
| `blocked` | approval, permission, trust or question UI | H6: inspect with `agent get`, `agent explain`, `agent read --source recent-unwrapped --lines 80`, show the user what was seen, and ask. Never `send-keys` |
| `idle` or `done` | settled. **This is not proof of success** | H7: validate `result.json` and `report.md`. `needs_input` goes to H6's question path |
| `idle` or `done` with no `result.json` | the worker stopped without writing its result, often to ask something in chat | Inspect with `agent read <name> --source recent-unwrapped --lines 80`. If the pane ends in a question or prompt from the worker, tell the user which pane (agent name and pane ID) and that they can answer there, then keep waiting; this is not a resubmit. If it ends with no question and no result, it is an H7 validation failure: announce, H8, fall back |
| `unknown` | Herdr cannot classify the agent | Inspect. Never count it as success. Continue waiting under the deadline (a plain `agent wait` does not match `unknown`) |
| `timeout` (overall deadline) | no settled state in time | Inspect. Never count it as success and never resubmit. Show whether a result file exists and ask: keep waiting, accept the file the user has checked, or abandon (H8, then fallback) |
| `agent_blocked` (the prompt was rejected) | a dialog was already open, so the prompt was **not** sent | H6. After the user clears the dialog, send the prompt: this is the first submission, not a resubmit |
| `agent_prompt_stalled` | the prompt was accepted but no state change came within 5000 ms | Do not resend. Run `agent get`, then continue the wait loop. If `agent read` shows the text still unsubmitted in the input box, ask the user |
| `agent_not_ready` (from start) | blocked at startup, usually a trust or first-run dialog | H6 with the prompt unsent |
| agent or pane gone, a JSON error on stderr with exit 1, or exit 2 | the worker exited or the transport broke | H8, announce, fall back. Treat as a transport failure |

Classification reads the JSON Herdr prints on stdout and stderr. The exit code alone is never
evidence. The exact JSON field that holds the state is not assumed: the UAT's probe P6 (Task 10)
records it.

## H6 - Handle a blocked worker

1. Inspect with `herdr agent get <name>`, `herdr agent explain <name>`, and
   `herdr agent read <name> --source recent-unwrapped --lines 80`. When that read (or
   `--source visible`) does not show the dialog, use
   `herdr agent read <name> --source detection --lines 80` (`detection` is one of the four
   sources `herdr agent read --help` lists in 0.8.2). The smoke test saw this in half-width wave
   panes, where only `detection` showed an OpenCode dialog.
2. Show the user what was seen.
3. Approval, permission, trust, or any question UI goes to the user. The user answers in the
   worker's pane. The Butler offers to focus the pane and does so only on a yes. Then it resumes
   `herdr agent wait`.

Never `send-keys` into a dialog, and never answer one on the user's behalf.

**`needs_input` in `result.json`:**

1. Move the file to `result.needs_input.<n>.json`.
2. Answer from context the Butler already holds, saying which question it answered and from what,
   or relay the question to the user.
3. Send the answer with `herdr agent prompt <name> "<answer>" --wait --timeout 300000`.
4. Resume H5.

The user may also answer a worker directly in its pane, at any time. The Butler then resumes
waiting.

The reason for this path: `agent prompt` rejects a blocked agent before it sends any input, so the
Butler can answer a question only once the worker is idle.

## H7 - Validate the result

`idle` or `done` is not proof of success. All of these checks must pass:

1. `result.json` exists and parses as JSON.
2. `run_id` and `role` equal the manifest's.
3. `status` is `complete`.
4. `report.md` exists, is not empty, and contains every item in the role's *What it returns*.
5. `head_commit` equals the manifest's, and HEAD has not moved.
6. `git status --porcelain` shows no change outside `allowed_writes`. This checks the "no authority
   beyond the command" rule.

Then the command's own spot-check still runs (`commands/prep.md` step 9 and `commands/research.md`
step 4). A failure means H8, then an announcement that names the failed check, then fallback.

A `failed` status is a validation failure, with its `reason` in the announcement. So is the marker
`JDI-RESULT-UNWRITABLE`: a final message `JDI-RESULT-UNWRITABLE <run-id>: <reason>`, seen during
inspection, is a validation failure with that reason in the announcement. Neither is ever a silent
success.

## H8 - Close the pane and record the outcome

1. Write `outcome.json` with these fields: `run_id`; `states`, a list of `{at, state, via}`;
   `final`, one of `valid`, `invalid`, `abandoned` or `transport_failed`; `validation`; `answers`;
   `user_decisions`; `fallback`, null or the path taken; and `pane_closed`, a boolean.
2. Run `herdr pane close <pane_id>` on every exit: success, failure, abandon, or a fallback of any
   kind. After a wave, close the wave tab once its last pane is closed:
   `herdr tab close <tab_id>`. Herdr closes a tab itself when its last pane closes, so this call
   may return `tab_not_found`. That result is expected and harmless: the tab is already gone.

Keep the pane open only when the user asks to inspect it, and then say that the user now owns
closing it. A failed delegation must not leak one pane per attempt.

## When a step fails

| Rung in `reference/delegation.md` | Failure | Level |
|---|---|---|
| 6 | Herdr is wanted but not detected. H1 failed at step 0. | transport-level |
| 7 | The kind is not one Herdr supports, or its CLI is not installed. | delegation-level |
| 8 | The pane or the agent cannot be started. | transport-level when the pane cannot be created, delegation-level when only the agent start fails |
| 9 | The run started but produced no valid result. H7 failed, or the state stayed `unknown` or timed out and the user chose to abandon. | delegation-level |

The announcement is one line that states the observed cause. These are patterns, not literal text:

- Step 0, `herdr`: `delegation.transport is herdr, but Herdr is not usable here: <failed check>
  returned <what came back>. Delegating natively for this run.`
- Step 0, `auto`, inside Herdr but a later check failed: the same pattern, with `auto` in place of
  `herdr`.
- Per delegation: `The <Role> did not run as a Herdr agent: <operation and observed reason>.
  Running it <as a subagent on <model> | through <kind>'s non-interactive mode | inline> instead.`
- Invalid value: `delegation.transport is "<value>", which is not native, auto or herdr.
  Delegating natively for this run.`

A harness failure and a model failure that fire together are one announcement.

A transport-level failure switches the rest of the run to native, announced once, so later phases
do not repeat a broken launch. Transport-level failures are: the pane cannot be created, a Herdr
CLI error, or the run directory cannot be created. A kind-level failure or a result-validation
failure affects only that one delegation.

## Why the agent surface, not pane run

The reason is lifecycle state. `agent start` and `agent prompt --wait` report `working`,
`blocked`, `idle`, `done` and `unknown`. That lets the Butler tell a worker waiting on an approval
apart from one still thinking, which a sentinel match on pane output cannot do.

The result still arrives through a file, so the 1.0.5 objection to `agent read` as a result channel
still stands. Rows lost to the alternate screen cannot be recovered
(`~/.claude/skills/herdr/SKILL.md:183-185`). That is why `agent read` is limited to inspection.

This replaces the pane-split, pane-run, wait-output recipe and the "Not `herdr agent start`" line
that `reference/delegation.md:136-141` carried.

## Waves

This section applies to Executors on another CLI, under `auto` or `herdr` with Herdr detected.

- **Panes.** The wave runs one pane per task, all started together. Each task has its own run
  directory, agent name and `manifest.json`. A task's `allowed_writes` is its task file's
  `## Files` plus its run directory.
- **The wave tab.** The wave gets its own tab:
  `herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd <worktree root> --no-focus`, which
  returns `.result.tab` and `.result.root_pane`. Then name it with
  `herdr tab rename <tab_id> jdi-wave-<first run id>`.
- **The cap.** The Butler keeps at most 4 worker panes open at once. It fills the cap and starts
  the next task as each slot frees, exactly as the subagent-cap rule in `reference/delegation.md`
  does.
- **The multi-worker wait.** The Butler cycles over every live worker with
  `herdr agent wait <name> --timeout 30000` (or `herdr agent get <name>`), under the overall
  deadline, and applies the H5 state table to each. It sends the user to any blocked or questioning
  pane by agent name and pane ID, and keeps waiting on the others meanwhile.
- **Settle first.** The whole wave settles before the Butler acts on any one result. A sibling that
  is still running is not cancelled because another failed.
- **Validate.** H7 runs per task (checks 1 to 5). The file check runs once for the wave: every
  change `git status --porcelain` shows must fall inside the union of the wave's `## Files` lists
  plus their run directories. A change outside it cannot be attributed to one task in a shared
  tree, so the Butler reports it to the user with the path and asks before it commits anything.
- **Commit and close.** Each task is committed by its own paths, one commit per task, as
  `reference/plan-store.md` *Waves* says. H8 closes every pane and then the tab.
- **Fallback.** A task whose worker failed falls back on its own, through the CLI's
  non-interactive mode, after the wave settles. The other tasks' results stand.

## H9 - Give a Butler its own worktree

This section applies to `/jdi:herd` only. Each issue in a herd gets its own worktree, workspace,
pane and agent, and the agent is a whole Butler running the prep command. Nothing waits for it:
the herd hands the work off and reports.

**The kind.** A herd applies H2's supported and installed checks to `herd.kind`, or to the
`--kind` the user passed, in place of `models.<role>.harness`. A kind with no row in the
invocation table below is rejected at H2 for a herd.

**Names.** The caller supplies one name per issue, `jdi-herd-<issue>`, built as
`commands/herd.md` step 5 says. Check it against `herdr agent list`. A live agent that already
holds the name may be a Butler for that issue, so the caller reports it and asks.

**The worktree folder carries the issue.** Its folder name is the step-5 name,
`jdi-herd-<issue>`, so after a crash or a closed workspace `git worktree list` (or `ls`) shows
which folder belongs to which issue, even when prep never reached its branch step. Build the path
as `<worktrees dir>/<repo>/jdi-herd-<issue>`:

- `<worktrees dir>` is `[worktrees] directory` from Herdr's config (`~/.config/herdr/config.toml`)
  when that is set, else Herdr's documented default `~/.herdr/worktrees` (from
  `herdr --default-config`). Expand a leading `~` to `$HOME`.
- `<repo>` is the basename of the main checkout. This matches the layout Herdr already uses
  (`~/.herdr/worktrees/<repo>/<folder>`, observed on this machine).

**An existing folder is not overwritten.** When `<worktrees dir>/<repo>/jdi-herd-<issue>` already
exists, a herd has run for this issue before. Say so. Show its branch
(`git -C <path> branch --show-current`) and whether its plan folder has uncommitted files
(`git -C <path> status --porcelain -- <plans.path>`). Then ask: continue there (a fresh session in
that folder, `/jdi:status`), or skip this issue. Never create a second folder beside it, and never
remove it here.

**Scratch branches are unique per herd run.** The scratch branch is
`jdi-herd-scratch-<herd-id>-<N>`, where `<herd-id>` is the herd's UTC start time
`yyyymmddThhmmss` and `<N>` is the issue's 1-based index in the herd. Prep switches away from the
scratch branch but does not delete it. PR #5's `jdi-herd-scratch-<N>` therefore collides with the
branch a previous herd left behind (observed: every earlier scratch branch of that form still
exists in three repositories on this machine). The scratch branch still omits the issue ID, for
PR #5's reason: prep adopts a branch that already names the work, and would then skip its **T6**
branch.

**Create it.**

```text
herdr worktree create --cwd "$PWD" --path <worktrees dir>/<repo>/jdi-herd-<issue> --branch jdi-herd-scratch-<herd-id>-<N> --base origin/<default> --label "<ISSUE-ID>" --no-focus
```

Read `.result.worktree.path`, `.result.root_pane.pane_id`, `.result.workspace.workspace_id` and
`.result.tab.tab_id`. Confirm that `.result.worktree.path` equals the path asked for. When it
differs, report both and use the one Herdr returned. `--path` is in `herdr worktree create --help`
(0.8.2) without stated semantics, so UAT probe P8 settles it before the herd scenario runs.

**Reattach after a restart.** `herdr worktree open` opens an existing worktree as a workspace
again. The report's closing line names it.

**Environment.** `herdr worktree create` takes no `--env`. When `harnesses.<kind>.env` is not
empty, create a tab inside the new workspace and use its root pane instead:
`herdr tab create --workspace <id> --cwd <path> --env KEY=VALUE ... --no-focus`, then use
`.result.root_pane.pane_id` and `.result.tab.tab_id` from that result.

**The invocation table.** The command each herd Butler receives, by kind:

| Kind | Invocation |
|---|---|
| `claude` | `/jdi:prep <ISSUE-ID>` |
| `codex` | `$jdi:run prep <ISSUE-ID>` |
| `opencode` | `/jdi-prep <ISSUE-ID>` |

These spellings come from the README install table that `tests/test_codex_plugin.py`'s
`test_harness_table_uses_jdi_run_and_preserves_other_harnesses` pins (`/jdi:prep`,
`$jdi:run <command> [arguments]`, `/jdi-prep`). Other kinds are rejected at H2 for a herd.

**Label the tab.** `herdr tab rename <tab_id> <name>`, with `tab_id` read from `.result.tab.tab_id`
(or from the `herdr tab create` result when the environment forced a new tab). The workspace keeps
the `--label "<ISSUE-ID>"` it was created with.

**Start the Butler** with **H4b** under `<name>`, in the pane chosen above. The arguments are
`harnesses.<kind>.args` verbatim, with no model flag.

**Hand it the work.** `herdr agent prompt <name> "<invocation>"`, with no `--wait`. The herd sends
every prompt first and reads the states afterward.

**Watch.** `herdr agent get <name>` reports the state. `herdr agent read <name> --source
recent-unwrapped --lines 80` shows a blocked agent's question, for inspection only (rule 4). A herd
Butler's dialogs belong to the user (rule 7).

**Cleanup.** `herdr worktree remove --workspace <id>`, plus `--force` when the worktree was seeded.
Before either, run `git -C <worktree> status --porcelain -- <plans.path>`. Any output means
uncommitted plan files: stop, name them, and offer the plan commit in that worktree. `--force` is
used only after that check is empty or the user has said yes to losing the files. Under
`plans.mode: external` the plan is not in the worktree, and the check finds nothing. JDI removes
nothing unless the user asks.
