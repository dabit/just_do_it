status: done
# 01 - Write `reference/herdr.md` and enumerate it

Depends on: None

## Why

The transport rewrite in Task 03 and the herd command in Task 08 both call named Herdr operations
(H1-H8, later H9) rather than inlining `herdr` commands, so those operations need one home before
anything can point at it. Every `herdr` invocation in the whole plan lives in this one new file, and
nowhere else, so that a body-confinement test can prove no other command, agent, role, or reference
file ever names a Herdr subcommand directly.

Rests on: the Design summary's "Where the Herdr instructions go" decision ("All `herdr` invocations
go in one new file, `reference/herdr.md`... This matches the T1-T8, J1-J5 and TS1-TS2 convention.
No `herdr <subcommand>`, `HERDR_` variable or `AskUserQuestion` appears in `commands/`, `agents/`,
`roles/`, `skills/`, or any other `reference/` file. A new test enforces this."), the result-contract
decision ("The Butler writes `manifest.json` and `prompt.md`... A terminal transcript is never the
result."), and the "Why the agent surface, not pane run" rationale in the same section.

## Description

Write `tests/test_herdr_operations.py` first, class `HerdrOperationsTest`, whose `setUp` reads
`reference/herdr.md` (so every assertion fails before the file exists):

- The exact headings exist: `# Herdr operations`, `## The universal rules`, `## Scope`,
  `## H1 - Detect Herdr` through `## H8 - Close the pane and record the outcome`,
  `## When a step fails`, `## Why the agent surface, not pane run`, `## Waves`. `assertNotIn`
  `## Extending to waves`, "One active delegated role per Butler", and "Single-instance roles".
- In `## The universal rules`: "A Butler runs one phase at a time" and "only a wave runs several
  workers at once".
- In `## Scope`: "never runs under Herdr" (a role on the Butler's own CLI).
- In H1's section: `HERDR_ENV`, `HERDR_BIN_PATH`, `herdr status`, `compatible: yes`, "never from the
  harness name", "Detect, never repair".
- H2: "lists the kinds Herdr supports", `command -v <kind>`, `herdr integration status`, and
  `assertNotIn` for `herdr agent get "$HERDR_PANE_ID"` (the kind is never inferred from the Butler's
  pane).
- H3: `git rev-parse --absolute-git-dir`, `jdi/runs/<run-id>/`, the five filenames, and each
  manifest key as a quoted JSON key (`"run_id"`, `"role"`, `"plan"`, `"ticket"`, `"base_commit"`,
  `"head_commit"`, `"cwd"`, `"workspace_id"`, `"pane_id"`, `"agent_name"`, `"expected"`,
  `"allowed_writes"`), plus `"needs_input"`.
- H4: `herdr pane split --current`, `--env`, `--no-focus`, `herdr agent start`, "printed back before
  the spawn", `agent_not_ready`.
- H5: `herdr agent prompt`, `--wait --timeout`, `herdr agent wait`. Table rows whose lines start with
  `` | `working` ``, `` | `blocked` ``, `` | `idle` ``, `` | `done` ``, `` | `unknown` ``,
  `` | `timeout` ``, `` | `agent_blocked` ``, `` | `agent_prompt_stalled` ``, and
  `` | `idle` or `done` with no `result.json` ``; the section contains "which pane".
- `## Waves`: "at most 4", "one pane per task", `herdr tab create`, `jdi-wave-<first run id>`, "is not
  cancelled", "the union of the wave's `## Files` lists", and "cannot be attributed to one task".
- H6: "Never `send-keys` into".
- H7: "`idle` or `done` is not proof of success", "`JDI-RESULT-UNWRITABLE`".
- H8: `herdr pane close`, "every exit". This takes over the `"herdr pane close"` pin that Task 03
  removes from `tests/test_codex_plugin.py`.
- "`agent read` is for inspection only", "never counts as success", "never resubmit".

Use whitespace normalization (`" ".join(text.split())`) for phrase assertions, matching the suite's
existing style (see `tests/test_codex_plugin.py:42-46`), and `jdi_files.section` for the heading
checks.

Watch it fail (the file does not exist yet), then write `reference/herdr.md` with this exact
outline - headings use a spaced hyphen, not an em dash, which is this file's own deviation from
`reference/jev.md`'s `## J1 - ` style:

- `# Herdr operations`. The intro says:
  - Herdr is a transport: a Butler uses it to run a delegated role that is configured on another
    CLI as that CLI's interactive agent, in a pane the user can answer, and to wait for it.
  - `reference/delegation.md` rung 2 (under `auto` or `herdr`) and rung 4 call the operations by
    name.
  - `herdr` means `$HERDR_BIN_PATH` when that is set, else `herdr` on `PATH`.
  - Commands are argument lists, and placeholders are in angle brackets.
  - Everything in the file is inert under `delegation.transport: native`, except where rung 4 sends
    a kind with no exec mode.
- `## The universal rules`:
  1. Capability is observed and never inferred from the harness name.
  2. Detect, never repair: JDI starts no server, installs no integration, and changes no Herdr
     setting.
  3. A Butler runs one phase at a time. Inside a phase, only a wave runs several workers at once,
     and the Butler waits for all of them and does nothing else in the command meanwhile.
  4. The result arrives through a file. `agent read` is for inspection only.
  5. `idle` or `done` is not proof of success, and `unknown` or `timeout` never counts as success.
  6. The Butler never resubmits blindly.
  7. The worker's dialogs belong to the user.
  8. A pane JDI created is closed on every exit.
  9. A worker is a separately spawned CLI: its authority comes from its own configuration and from
     the arguments the user wrote.
- `## Scope`:
  - Only a role whose `models.<role>.harness` names another CLI reaches these operations. A role on
    the Butler's own CLI never runs under Herdr: it stays a subagent, watchable in the harness
    itself.
  - Any such role: the single roles (Researcher, Planner, Splitter, Synthesizer, PR Writer,
    Feedbacker) run one worker each; Executors in a wave run one worker per task (`## Waves`).
  - A worker uses the Butler's own worktree, because the Butler waits.
  - Butlers started by `/jdi:herd` are isolated from each other by worktrees.
- `## H1 - Detect Herdr`:
  - Performed once, at step 0. Checks run in order and the first failure wins:
    - (a) `printenv HERDR_ENV` prints `1`;
    - (b) the binary resolves: `$HERDR_BIN_PATH` is executable, else `command -v herdr`;
    - (c) `herdr status` reports server `status: running` and `compatible: yes`, and
      `HERDR_SOCKET_PATH`, when set, is an existing socket.
  - The answer, "available" or the first failed check with its output, is used for every delegation
    in the run. No role re-probes.
  - The `auto` versus `herdr` announcement rules: `auto` stays silent when `HERDR_ENV` is unset, and
    announces once when `HERDR_ENV=1` but a later check fails. `herdr` announces any failed check
    once.
  - The sentence "never from the harness name".
- `## H2 - Check the worker kind`:
  - The kind is `models.<role>.harness`, and only that. A role with no `harness`, or one naming the
    Butler's own kind, never reaches this operation.
  - Supported: the kind appears on the `kinds:` line of `herdr agent`. That line **lists the kinds
    Herdr supports**, not the kinds installed.
  - Installed: `command -v <kind>` resolves.
  - `herdr integration status` affects only detection quality. It is recorded in the manifest and
    stated once when the kind's integration is missing or outdated (for example, "lifecycle states
    for claude come from screen rules").
  - The model-flag table:

    | Kind | Model flag | Status |
    |---|---|---|
    | `claude` | `--model <model>` | verified in `claude --help` |
    | `opencode` | `-m <provider/model>` | verified in `opencode --help` 1.18.10 |
    | `codex` | `-m <model>` | not verified here: `codex` is not installed |

    For a kind with no known flag, rung 10 of `reference/delegation.md` applies.
  - With no `models.<role>.model`, no flag is passed, and the worker runs on its CLI's own default.
    Say so in the pre-spawn line.
- `## H3 - Prepare the run`:
  - Run ID: `<UTC yyyymmddThhmmssZ>-<role>-<4 hex>`. Agent name: `jdi-<role>-<4 hex>`, matching
    Herdr's `[a-z][a-z0-9_-]{0,31}` (for example `jdi-researcher-7f3a`, 20 characters). The Butler
    checks `herdr agent list` for a collision and draws a new suffix if it finds one.
  - `git rev-parse --absolute-git-dir`, then `mkdir -p <gitdir>/jdi/runs/<run-id>/`. A failure here
    is a transport failure.
  - The `manifest.json` field list (Butler writes it before the spawn, never edits it afterward,
    environment values never recorded, only the keys):

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
    because `agents/splitter.md` returns "Task files written to the plan folder".
  - The `prompt.md` template (Appendix A of `PLAN.md`, verbatim, reproduced here):

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

    The line breaks above are the plan's own; treat the fenced block as exact except for the
    `<...>` placeholders.
  - The role instructions are the installed `agents/<role>.md` body with its frontmatter removed.
    The Butler reads it with the same resolution it uses for `reference/`, copies the text, and
    never hands the worker a plugin path (`docs/harness-adapter-architecture.md:191-194`).
  - Inputs: exactly the role's *What it receives*. Short values are written inline and file inputs
    are given as absolute paths.
  - The short prompt, verbatim: `Read <abs run dir>/prompt.md and follow it exactly. This is JDI
    run <run-id>.`
  - Run directories are kept. JDI never deletes them in this release. Removing a linked worktree
    removes its git directory and its runs. The user may delete `<gitdir>/jdi/runs/` at any time.
- `## H4 - Start the worker`:
  - Print, before the spawn, the agent name, kind, model, every argument verbatim (from
    `harnesses.<kind>.args`), the environment keys, and the run directory. The words "printed back
    before the spawn" appear.
  - A single role: choose the direction with `herdr pane layout --pane "$HERDR_PANE_ID"` (`right`
    for a wide pane, `down` otherwise) and create a sibling pane: `herdr pane split --current
    --direction <d> --cwd <worktree root> [--env KEY=VALUE ...] --no-focus`. Read
    `.result.pane.pane_id`.
  - A wave: every worker's pane goes in the wave's own tab (`## Waves`). The first worker uses the
    tab's root pane; each later one splits a pane inside that tab.
  - `--env` carries `harnesses.<kind>.env` verbatim, because `herdr agent start` has no `--env` or
    `--cwd` (verified in `--help`).
  - Start the agent: `herdr agent start <name> --kind <kind> --pane <pane_id> --timeout 120000 [--
    <model flag> <args...>]`. Pass `--` only when something follows it.
  - `agent_started` means continue. `agent_not_ready` means H6 with the prompt unsent. Any other
    error means H8, then fallback.
  - Section **H4b** (reused by `/jdi:herd` in a later task): the start command alone, applied to a
    pane and a name the caller supplies.
- `## H5 - Prompt and wait`:
  - `herdr agent prompt <name> "<short prompt>" --wait --timeout 300000`, then loop `herdr agent
    wait <name> --timeout 300000` until a settled state appears or the overall deadline passes.
  - The overall deadline defaults to 2700000 ms. A value the user states in the conversation wins
    for that run.
  - Set the shell tool's own timeout above each call. Where the shell tool caps lower than 300000,
    use its cap minus 30000.
  - Without `--timeout`, Herdr's wait is indefinite (verified in `--help`), so `--timeout` is
    mandatory.
  - The state table:

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

  - Classification reads the JSON Herdr prints on stdout and stderr. The exit code alone is never
    evidence. The exact JSON field that holds the state is not assumed; it is recorded by the UAT's
    probe P6 (Task 10).
- `## H6 - Handle a blocked worker`:
  - Inspect with `agent get`, `agent explain <name>`, and `agent read <name> --source
    recent-unwrapped --lines 80`.
  - Show the user what was seen.
  - Approval, permission, trust, or any question UI goes to the user. The user answers in the
    worker's pane. The Butler offers to focus the pane and does so only on a yes. Then it resumes
    `herdr agent wait`.
  - **Never `send-keys` into** a dialog.
  - `needs_input` in `result.json`:
    - Move the file to `result.needs_input.<n>.json`.
    - Answer from context the Butler already holds, saying which question it answered and from
      what, or relay the question to the user.
    - Send the answer with `herdr agent prompt <name> "<answer>" --wait --timeout 300000`.
    - Resume H5.
  - The user may also answer a worker directly in its pane, at any time. The Butler then resumes
    waiting.
  - The reason: `agent prompt` rejects a blocked agent before sending input, so a question is
    answerable only once the worker is idle.
- `## H7 - Validate the result`. All checks must pass:
  1. `result.json` exists and parses as JSON.
  2. `run_id` and `role` equal the manifest's.
  3. `status` is `complete`.
  4. `report.md` exists, is not empty, and contains every item in the role's *What it returns*.
  5. `head_commit` equals the manifest's and HEAD has not moved.
  6. `git status --porcelain` shows no change outside `allowed_writes`, which checks the "no
     authority beyond the command" rule.

  Then the command's own spot-check still runs (`commands/prep.md` step 9 and `commands/research.md`
  step 4, both edited in a later task). A failure means H8, then announce with the failed check,
  then fallback. `failed` status, or a final message `JDI-RESULT-UNWRITABLE <run-id>: <reason>` seen
  during inspection, is a validation failure with that reason in the announcement. It is never a
  silent success.
- `## H8 - Close the pane and record the outcome`:
  - Write `outcome.json` (fields: `run_id`, `states` - a list of `{at, state, via}`, `final` -
    `valid | invalid | abandoned | transport_failed`, `validation`, `answers`, `user_decisions`,
    `fallback` - null or the path taken, `pane_closed` - boolean).
  - Run `herdr pane close <pane_id>` on every exit: success, failure, abandon, or a fallback of any
    kind. After a wave, close the wave tab once its last pane is closed (`herdr tab close <tab_id>`).
  - Keep the pane open only when the user asks to inspect it, and then say who now owns closing it.
  - A failed delegation must not leak one pane per attempt.
- `## When a step fails`: a table mapping each failure to its `reference/delegation.md` rung (6 to
  9), whether it is transport-level or delegation-level, and the announcement pattern:
  - Rung 6 ("Herdr is wanted but not detected. H1 failed at step 0.") - transport-level.
  - Rung 7 ("The kind is not one Herdr supports, or its CLI is not installed.") - delegation-level.
  - Rung 8 ("The pane or the agent cannot be started.") - transport-level when the pane cannot be
    created, delegation-level when only the agent start fails.
  - Rung 9 ("The run started but produced no valid result. H7 failed, or the state stayed `unknown`
    or timed out and the user chose to abandon.") - delegation-level.
  - Announcement patterns (use one line, state the observed cause; these are patterns, not literal
    text):
    - Step 0, `herdr`: `delegation.transport is herdr, but Herdr is not usable here: <failed check>
      returned <what came back>. Delegating natively for this run.`
    - Step 0, `auto`, inside Herdr but a later check failed: the same pattern, with `auto` in place
      of `herdr`.
    - Per delegation: `The <Role> did not run as a Herdr agent: <operation and observed reason>.
      Running it <as a subagent on <model> | through <kind>'s non-interactive mode | inline>
      instead.`
    - Invalid value: `delegation.transport is "<value>", which is not native, auto or herdr.
      Delegating natively for this run.`
  - A harness failure and a model failure that fire together are one announcement.
  - Transport-level failures switch the rest of the run to native, announced once. Kind-level
    failures and result-validation failures affect only that one delegation.
- `## Why the agent surface, not pane run`:
  - The reason is lifecycle state. `agent start` and `agent prompt --wait` report `working`,
    `blocked`, `idle`, `done` and `unknown`. That lets the Butler tell a worker waiting on an
    approval apart from one still thinking, which a sentinel match on pane output cannot do.
  - The result still arrives through a file, so the 1.0.5 objection to `agent read` as a result
    channel still stands. Rows lost to the alternate screen cannot be recovered
    (`~/.claude/skills/herdr/SKILL.md:183-185`). That is why `agent read` is limited to inspection.
  - This replaces the pane-split, pane-run, wait-output recipe and the "Not `herdr agent start`"
    line that `reference/delegation.md:136-141` carried.
- `## Waves` (Executors on another CLI, under `auto` or `herdr` with Herdr detected):
  - One pane per task, all started together, each with its own run directory, agent name and
    `manifest.json`. A task's `allowed_writes` is its task file's `## Files` plus its run directory.
  - The wave gets its own tab: `herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd <worktree
    root> --no-focus`, then `herdr tab rename <tab_id> jdi-wave-<first run id>`.
  - At most 4 worker panes are open at once. Fill the cap and start the next task as each slot frees,
    exactly as the subagent-cap rule in `reference/delegation.md` does.
  - The multi-worker wait: cycle over every live worker with `herdr agent wait <name> --timeout
    30000` (or `herdr agent get <name>`), under the overall deadline, applying the H5 state table to
    each. Send the user to any blocked or questioning pane by agent name and pane ID. Keep waiting on
    the others meanwhile.
  - Let the whole wave settle before acting on any one result. A sibling that is still running is
    not cancelled because another failed.
  - Then H7 per task (checks 1 to 5), and the combined file check once for the wave: every change
    `git status --porcelain` shows must fall inside the union of the wave's `## Files` lists plus
    their run directories. A change outside it cannot be attributed to one task in a shared tree, so
    it is reported to the user with the path, and the Butler asks before committing anything.
  - Then each task is committed by its own paths, one commit per task, as `reference/plan-store.md`
    *Waves* says. H8 closes every pane and then the tab.
  - A task whose worker failed falls back on its own (the CLI's non-interactive mode) after the wave
    settles; the other tasks' results stand.

Also in this task:
- `README.md`: insert a row after `reference/delegation.md` (currently the last row of `## How it is
  put together`'s table, at line 344): `` | `reference/herdr.md` | The Herdr operations (H1-H8) a
  Butler uses to run a role on another CLI in its own pane, one per task in a wave, and wait for its
  result | ``. This is the row
  the existing `ReferenceFileEnumerationTest` (`tests/test_enumerations.py:48-85`) needs, and it goes
  red the moment `reference/herdr.md` exists without it - treat that test as this edit's red half.
- `AGENTS.md`: in the **Reference files.** paragraph (currently `reference/config.md`,
  `reference/tracker.md`, `reference/testing.md`, `reference/jev.md`, `reference/plan-store.md`, and
  `reference/delegation.md`), add `` `reference/herdr.md` `` to the list, before
  `` `reference/delegation.md` ``. Same `ReferenceFileEnumerationTest` covers this half.

Do not add any `herdr` invocation, `HERDR_` variable, or `AskUserQuestion` mention outside
`reference/herdr.md` in this task - Task 03's `HerdrConfinementTest` checks the whole repository for
that, and this task's own file is the one place those strings belong.

## Files

- `reference/herdr.md` (new)
- `README.md`
- `AGENTS.md`
- `tests/test_herdr_operations.py` (new)

## Verification

- `python3 -m unittest tests.test_herdr_operations -v` - fails (`reference/herdr.md` not found)
  before the file is written, passes once every heading and phrase above is present.
- `python3 -m unittest tests.test_enumerations.ReferenceFileEnumerationTest -v` - passes once both
  the README row and the AGENTS.md list entry are in place.
- `grep -n " - " reference/herdr.md` - empty (no em dash in the new file; headings use a spaced
  hyphen, which is a literal `-`, not `—`).
- `grep -c "herdr " reference/herdr.md` - non-zero, confirming the operations actually name `herdr`
  subcommands (this file is the one place they are allowed).
- `python3 -m unittest discover -s tests -v` - no new failures beyond the two tests above; the
  suite's other 58 tests are unaffected by this task's files.
