# Delegation Transport Architecture

## Status

Implemented in the `herdr-role-delegation` branch for release 1.0.10. The role-delegation layer
(`reference/herdr.md` H1 to H8, the `delegation.transport` key, and rung 2's transport choice in
`reference/delegation.md`) exists. The `/jdi:herd` layer (the `herd` config block, H9 and
`commands/herd.md`) is planned in the same branch as a separable wave.

## Purpose

A JDI Butler hands each phase to a role. Most roles run as subagents inside the Butler's own
harness. A role can also be configured to run on another agent CLI through
`models.<role>.harness`. Before this change, that other CLI ran only in its non-interactive mode,
and the user could not see or answer it while it worked.

This document records how a Butler can instead run that other CLI as its interactive agent in a
Herdr pane, how the Butler waits for the result and checks it, and what stays unchanged. The
operations themselves are defined in `reference/herdr.md`. The selection rules are in
`reference/delegation.md`, under "Choosing the transport" and rung 2 of "How to delegate". The key
is documented in `reference/config.md`.

## Two layers

Two separate mechanisms use Herdr, and they do not share a control loop.

The outer layer is `/jdi:herd`. It fans a list of tickets out to independent Butlers: one
worktree, one Herdr workspace, one branch and one ticket each. Each Butler is a full JDI session,
and the herd does not coordinate them after it starts them.

The inner layer is role delegation inside one Butler. A Butler runs one phase at a time. Inside a
phase, only a wave runs several workers at once, and the Butler waits for all of them and does
nothing else in the command meanwhile (`reference/herdr.md`, universal rule 3). The Butler never
multitasks across unrelated work. Two phases never overlap, and a single-role phase has exactly
one worker.

## Backend choice

Herdr is used only when the harness differs. The rule has three cases:

- A role with no `models.<role>.harness`, or one that names the Butler's own CLI, is a native
  subagent under every value of `delegation.transport`. Its progress is watchable in the harness
  itself, so a pane would add nothing (`reference/delegation.md`, "Choosing the transport").
- A role on another CLI runs through rung 2 of "How to delegate". Under `auto` or `herdr` with
  Herdr detected at step 0, rung 2 runs that CLI's interactive agent in a Herdr pane the user can
  answer (H2 to H8).
- Otherwise rung 2 runs that CLI's non-interactive mode (`codex exec`, `opencode run`,
  `claude -p`), exactly as before this change. Under `native`, Herdr is reached only through rung
  4, for a kind with no exec mode JDI knows.

The Butler drives Herdr's agent surface (`herdr agent start`, `herdr agent prompt --wait`,
`herdr agent wait`) and does not use the older pane-run and output-match recipe. The agent surface
reports lifecycle states: `working`, `blocked`, `idle`, `done` and `unknown`. With these states,
the Butler can tell a worker that waits on an approval dialog apart from one that is still
working. A match on pane output cannot make that distinction (`reference/herdr.md`, "Why the agent
surface, not pane run").

This decision overrides the original brief, which asked to prefer a Herdr agent over a native
subagent whenever Herdr is on. The user revised it on 2026-09-24. A subagent is already watchable
in every harness JDI supports, so a pane gives a same-CLI role nothing it lacks. A pane helps
where another CLI runs, because that is the one case where the user otherwise cannot see or answer
the worker.

## Capability detection

The Butler performs H1 once, at step 0, and only when `delegation.transport` is `auto` or
`herdr`. The checks run in order, and the first failure wins:

1. `HERDR_ENV` is `1`.
2. The `herdr` binary resolves (`$HERDR_BIN_PATH`, else `PATH`).
3. `herdr status` reports a running, compatible server, and `HERDR_SOCKET_PATH`, when set, is an
   existing socket.

The answer is used for every delegation in the run, and no role probes again. `auto` stays silent
when `HERDR_ENV` is unset, because that is the expected state outside Herdr. It announces once when
`HERDR_ENV=1` but a later check fails. `herdr` announces any failed check once.

Detection never uses the harness name. The same harness can run inside or outside Herdr, with or
without a server, and with a compatible or incompatible version. Only an observation in this
session says whether Herdr can be used now (`reference/herdr.md`, universal rule 1). H2 applies the
same rule to the worker kind: the kind must appear on the `kinds:` line of `herdr agent` (the kinds
Herdr supports, not the kinds installed), and `command -v <kind>` must resolve.

## Result contract

Every Herdr run has its own directory, `$(git rev-parse --absolute-git-dir)/jdi/runs/<run-id>/`.
In a linked worktree that path is under `<common>/.git/worktrees/<name>`, so each worktree has its
own runs. The run ID is `<UTC yyyymmddThhmmssZ>-<role>-<4 hex>`, and the agent name is
`jdi-<role>-<4 hex>`.

The directory contains five files (`reference/herdr.md` H3):

| File | Written by | When | Contents |
|---|---|---|---|
| `manifest.json` | the Butler | after the pane split and before `agent start` (H4), never edited afterward | schema, run ID, role, command, plan, ticket, base and head commits, cwd, transport, the Herdr workspace, tab, pane and agent name, the integration status, the `JDI spawn` line exactly as printed (`spawn_line`), the worker kind, model, verbatim args and env keys (never values), the expected files, `allowed_writes`, the creation time and the deadline |
| `prompt.md` | the Butler | with `manifest.json` (H4) | the role file body copied verbatim, the role's inputs, where the worker may write, and the result contract |
| `report.md` | the worker | first | every item in the role's *What it returns* |
| `result.json` | the worker | last | `run_id`, `role`, `status` (`complete`, `needs_input` or `failed`), `report`, `head_commit`, `summary`, plus `questions` or `reason` |
| `outcome.json` | the Butler | at H8 | `run_id`, `states`, `final` (`valid`, `invalid`, `abandoned` or `transport_failed`), `validation`, `answers`, `user_decisions`, `fallback`, `pane_closed` |

H7 decides success. All six checks must pass: `result.json` parses; `run_id` and `role` match the
manifest; `status` is `complete`; `report.md` exists, is not empty and contains every returned
item; `head_commit` matches and HEAD has not moved; and `git status --porcelain` shows no change
outside `allowed_writes`. The command's own spot-check still runs after H7.

The result arrives through a file, and a terminal transcript is never the result. Rows that scroll
into the alternate screen cannot be recovered, a transcript mixes the worker's reasoning with its
answer, and a file can be validated field by field. `herdr agent read` is used only to inspect a
worker (`reference/herdr.md`, universal rule 4).

## States

A settled state is never proof of success. `idle` or `done` sends the Butler to H7. `unknown` or a
timeout never counts as success. The full table, with the Butler's action for each observed state,
is in `reference/herdr.md` H5. In summary:

- `working` after a per-call timeout: print one progress line and keep waiting, under an overall
  deadline of 2700000 ms unless the user states another value.
- `blocked`: an approval, permission, trust or question dialog. The Butler inspects the worker,
  shows the user what it saw, and the user answers in the worker's pane (H6).
- `idle` or `done` with `result.json`: validate it (H7). A `needs_input` status goes to H6's
  question path, where the Butler answers from context it already has or relays the question.
- `idle` or `done` with no `result.json`: the Butler reads the pane. A question in the pane is
  pointed out to the user, who answers there, and the Butler keeps waiting. No question and no
  result is an H7 validation failure.
- `agent_blocked`, `agent_prompt_stalled`, `agent_not_ready`, and a lost agent or pane each have
  their own row. The Butler never resends a prompt that may already have been sent.

## Authority

A Herdr worker is a separately spawned CLI. Its sandbox, approval policy and credentials come from
its own configuration and from the arguments the user wrote in `harnesses.<kind>.args`, which JDI
passes verbatim and prints back before the spawn. JDI composes only the invocation and the model
flag, and adds no authority-affecting flag of its own (`reference/herdr.md`, universal rule 9;
`reference/delegation.md`, "What delegation does not grant").

The worker's approval, permission, trust and question dialogs belong to the user. The Butler never
uses `send-keys` on a dialog and never answers one for the user. It answers a worker's content
question only from context it already has, and says which question it answered and from what.
H7's file check confirms afterward that the worker wrote nothing outside `allowed_writes`.

## Isolation

Butlers started by `/jdi:herd` are isolated from each other by worktrees. Each has its own
worktree, branch, workspace and run directories.

Workers inside one Butler are not isolated by worktree. A worker uses the Butler's own worktree,
because the Butler waits for it and commits its result there. `allowed_writes` and H7's
`git status --porcelain` check replace a separate checkout: a single worker may write only its run
directory and what its role returns (for example, the Splitter's task files and `PLAN.md`). In a
wave, each Executor may write its task's `## Files` plus its run directory, and the wave's file
check runs once against the union of those lists.

## Configuration

The mechanism reads these keys. Each one is documented in `reference/config.md`.

- `delegation.transport`: `native` (the default), `auto` or `herdr`. It changes only how a role on
  another CLI runs. Whether a user works inside Herdr is a fact about their machine, so the key
  usually belongs in `.jdi/config.local.yml`. Any other value is announced once and treated as
  `native`.
- `models.<role>.harness`: the worker kind. It is the only input that selects a role for Herdr.
- `models.<role>.model`: passed as the CLI's own model flag (`--model` for `claude`, `-m` for
  `opencode`, and `-m` for `codex`, which is not yet verified), before the verbatim args. With
  no model, no flag is passed and the pre-spawn line says the CLI's default applies.
- `harnesses.<kind>.args` and `harnesses.<kind>.env`: passed verbatim. Under Herdr, `env` is set on
  the pane with `--env`, because `herdr agent start` has no `--env` option.
- The herd keys, forthcoming in the `/jdi:herd` wave: `herd.kind`, `herd.max_parallel` and
  `herd.seed`. Herd agents take their arguments and environment from `harnesses.<herd.kind>`, so
  there is no `herd.args` or `herd.env`.

There is no run-path key and no deadline key. The overall deadline is a default that a value stated
in the conversation replaces for that run.

## Validate, never repair versus detect, never repair

The two layers fail in opposite directions, on purpose.

`/jdi:herd` keeps "validate, never repair". It checks Herdr and the worker kind before it starts
anything, and the first failure stops the run with its reason. It has no fallback. A herd that
quietly became one sequential prep would look exactly like a herd that worked, and the user would
not learn that the tickets ran one after another.

Role delegation is "detect, never repair, then fall down the ladder". JDI starts no Herdr server,
installs no integration and changes no Herdr setting. When Herdr cannot be used, the role goes back
to native resolution: rung 2's non-interactive mode, or the floor where rung 4 sent a kind with no
exec mode. It always continues natively, because a phase that never ran is the failure. A
transport-level failure (the pane cannot be created, a Herdr CLI error, or the run directory cannot
be created) switches the rest of the run to native, announced once. A kind-level or validation
failure affects only that one delegation. Every exit closes the pane JDI created (H8).

## Waves and other roles

Every role on another CLI uses the same operations, H2 to H8. The single roles (Researcher,
Planner, Splitter, Synthesizer, PR Writer, Feedbacker) run one worker each. No role file changes
for this.

Executors in a wave run one worker per task (`reference/herdr.md`, "Waves"):

- One pane per task, all in one wave tab named `jdi-wave-<first run id>`. Each task has its own run
  directory, agent name and manifest.
- At most 4 worker panes open at once. The Butler fills the cap and starts the next task as each
  slot frees, as the subagent-cap rule does.
- A multi-worker wait: the Butler cycles over every live worker with a 30000 ms per-agent timeout,
  applies the H5 table to each, and sends the user to any blocked or questioning pane by agent name
  and pane ID while it keeps waiting on the others.
- The whole wave settles before the Butler acts on any one result, and a running sibling is never
  cancelled because another failed.
- H7 checks 1 to 5 run per task. The file check runs once for the wave, against the union of the
  wave's `## Files` lists plus their run directories. A change outside that union cannot be
  attributed to one task in a shared tree, so the Butler reports the path and asks before it
  commits anything.
- Each task is committed by its own paths. H8 closes every pane and then the tab. A task whose
  worker failed falls back on its own, through the CLI's non-interactive mode, after the wave
  settles.

"A Butler runs one phase at a time" replaces the brief's "one active delegated role per Butler".
The brief's rule would have forbidden a wave of Herdr workers. Waves already ran concurrently
before this change, as one rung 2 process per task, so panes add observability and no new
concurrency. The rule that remains keeps the Butler out of unrelated work: it never starts a second
phase while one is running.

## Live validation matrix

The UAT in this plan (Task 10) runs the mechanism against real CLIs. The Butler is Claude Code in
a Herdr pane, working in a scratch clone with `tracker.name: none`.

| Worker | Configuration | What it proves |
|---|---|---|
| A: `opencode` | a single role (the Researcher in a full prep), then a wave of Executors | the single-role path end to end, and one pane per task with the multi-worker wait and the combined file check |
| B: the same-harness control | a role with `harness: claude` under a Claude Butler | the role runs as a native subagent, and no pane opens |
| C: `codex` | a single role | the `codex` model flag and start path; requires `codex` to be installed, which it was not when the plan was written |

Before the scenarios, the UAT runs pre-flight probes against Herdr itself (start after a split,
environment inheritance, timeouts, pane close, `agent_blocked`, trust dialogs, JSON output and
linked worktrees). A probe that contradicts `reference/herdr.md` stops the UAT until the reference
is fixed.

## Relationship to PR #5

PR #5 (`origin/herd-command`) added `/jdi:herd` with its own Herdr calls. The herd layer's
contract with the shared mechanism is H1 (detect Herdr), H2 (check the worker kind), H4b (start an
agent in a given pane), and the H9 that `/jdi:herd` adds (Task 08) to give each Butler its own
worktree.

PR #5 closes as superseded when the herd wave ships, or is rebased onto this contract if the wave
is dropped.
