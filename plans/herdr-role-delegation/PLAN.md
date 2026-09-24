# Herdr-aware role delegation

- Tracker: github
- Project: feature development
- Issue: none
- Issue URL: none
- Created: 2026-09-24
- Started: 2026-09-24
- TDD: on — proven 2026-09-24 with `python3 -m unittest discover -s tests -v`
- Base commit: origin/main @ 94912b348658fffee5b41e69e04cd2b46d12dfac
- Summary: Let a JDI Butler run delegated roles (Researcher first) as separate Herdr-managed agent processes, with a durable result contract and the existing fallback chain, while /jdi:herd (PR #5) stays a thin batch launcher of independent Butlers.

## References

Citations are against base commit `94912b3` unless marked otherwise. The Butler spot-checked the
entries marked (verified).

### Current delegation and config (the code that changes)

- `reference/delegation.md:56-89` — the three-rung *How to delegate* ladder (subagent → second
  non-interactive session → inline); rung 2 is a chosen path when `models.<role>.harness` names
  another kind.
- `reference/delegation.md:91-113` — *Delegating several roles at once*; `:102-104` says "under
  Herdr that is one pane per task".
- `reference/delegation.md:115-153` — *Where a role runs*. `:120` "exec-first, Herdr second"
  (verified); `:136-141` the current Herdr transport: `pane split → pane run → pane wait-output`,
  "**Not `herdr agent start`**", `herdr agent read` banned (verified). Both must change.
- `reference/delegation.md:155-164` — *What delegation does not grant*.
- `reference/delegation.md:166-225` — the 12-rung "cannot be honoured" ladder; rung 6 (`:187-188`)
  is Herdr detection, rung 7 (`:189-190`) misreads Herdr's `kinds:` line as "installed", rung 9
  (`:193-195`) says `unknown` does not prove completion; `:208-220` the four never-directions;
  `:222-225` the dead `deep/standard/fast` shape.
- `reference/config.md:15-30` local override merge; `:134-161` `models.<role>.{model,harness}`;
  `:163-187` `harnesses.<kind>.{args,env}` ("under Herdr, on the pane"); `:229-245` defaults table;
  `:281-293` invariants (`harness` degrades down never up, no `models.butler`).
- `roles/butler.md:22-24` verify before relaying; `:27-34` announce every skip, resolve
  capabilities once at step 0 (verified).
- `docs/harness-adapter-architecture.md:238-263` three-step capability-delegation summary
  (`:244` repeats "exec-first" and needs the same update); `:32-51` command allowlist;
  `:191-194` never derive a plugin root.

### Config-key lifecycle (what must change when a key is added)

- `docs/config-key-lifecycle.md:61-76` the nine-file mandatory floor (verified); `:136-139` grep the
  key when done; `:153-220` repeat-in-place rule for step-0 lines; `:222-280` degradation idiom;
  `:282-347` where a key belongs; `:320-335` the five-question test; `:349-439` CHANGELOG and
  version convention plus checklist. Its own citations are stale (`:123`, `:355` say 1.0.6; all
  three manifests are 1.0.9, verified).
- `commands/prep.md:28-29` and `commands/research.md:23-24` — the literal block-name lists
  (verified).
- `commands/init.md:141-169` models/harnesses questions (13 steps today); `commands/help.md:9-15`,
  `:149-162`; `README.md:186`, `:202-210` init enumerations, `:332-347` reference-file table;
  `AGENTS.md:50-52` reference-file mention.
- `jdi.config.example.yml`; `.claude-plugin/plugin.json:3`, `.codex-plugin/plugin.json:3`,
  `.claude-plugin/marketplace.json:10` (all 1.0.9 → 1.0.10).

### Delegation call sites

- Point at `reference/delegation.md`: `commands/prep.md:120-121`, `commands/research.md:49-51`,
  `commands/plan.md:78-80`, `commands/split.md:77-78`, `commands/feedback.md:46-47`,
  `commands/pr.md:57-59`. Wave commands point at *Delegating several roles at once*:
  `commands/execute.md:78-82`, `commands/yolo.md:98-102`, `commands/next.md:66-69`.
- No pointer at all: `commands/prep.md:136`, `:152`; `commands/research.md:72`;
  `commands/pr.md:106`.
- Validation gates a result check must precede: `commands/research.md:64-67`,
  `commands/prep.md:130-133`. `commands/feedback.md:48-50` asks for a different model only.

### Role contracts

- `agents/researcher.md:8` read-only, `:18` tools, `:76-89` receives/returns (verified by the
  Butler this run). `agents/planner.md:108-119`; `agents/splitter.md:207-219`;
  `agents/executor.md:1-19` (no `tools:` key), `:114-150`; `agents/synthesizer.md:47-56`;
  `agents/pr-writer.md:43-52`; `agents/feedbacker.md:35-37` (not the producing model), `:86-99`.

### Tests

- `tests/test_codex_plugin.py:183-231` pins literal delegation text, including `herdr pane split`
  and "Not `herdr agent start`" at `:213-218` (verified) — must be rewritten with the transport.
- `tests/test_config_schema.py:26-101` schema/example/defaults bidirectional guard; `:104-153`
  `ModelsBlockTest`. `tests/jdi_files.py:99-139` `key_paths` parses two-space mappings only.
- `tests/test_enumerations.py:48-85` new `reference/*.md` needs README and AGENTS rows;
  `:114-175` command enumerations; `:178-210` `TierVocabularyTest` bans "tier" (verified);
  `:213-243` `ConfigLoadStepTest` (count 12, local-override mention).
- `tests/test_parallel_waves.py:21-36` pins the waves heading. `tests/test_opencode_sync.py:74-80`
  copies all of `reference/`. Baseline: 60 tests OK (verified).

### Adapters

- `bin/sync-opencode.sh:64-67` copies `reference/` and `roles/`; `:120-132` rewrites
  `${CLAUDE_PLUGIN_ROOT}` only. `skills/run/SKILL.md:18-35` Codex command allowlist, `:90-96`
  dispatcher defers to `reference/delegation.md`. `AGENTS.md:66-76` bodies never touched.

### PR #5 (`origin/herd-command`, head `2c28c11`, version 1.0.5, merge-base `296103d`)

- `git show origin/herd-command:commands/herd.md` (281 lines) and
  `git show origin/herd-command:reference/config.md` (`herd:` block). Diff saved at
  `scratchpad/pr5.diff` for this session.
- Adds `herd.{kind,max_parallel,args,env,seed}`; `herd.args`/`herd.env` duplicate
  `harnesses.<kind>.{args,env}` on main. Four validation checks (`HERDR_ENV`, `command -v herdr`,
  `herdr workspace list`, `kinds:` line); worktree via `herdr worktree create --branch
  jdi-herd-scratch-<N> --base origin/<default> --label <ISSUE>`; agents via `herdr agent start
  <name> --kind <kind> --pane <id> -- <args>` then `herdr agent prompt` with no `--wait`; never
  answers another agent's dialog; "validate, never repair".
- Stale against main: tier column edits, init step numbering, versions 1.0.4/1.0.5, no
  `config.local.yml` in its step 1, no Codex allowlist update, `AskUserQuestion` and `herdr`
  commands in the command body.

### Past plans

- `plans/9-agent-model-settings/PLAN.md` — replaced tiers with `models.<role>` (1.0.5); `:51-57`
  exec-first/never `agent start` rationale; `:58-60` expected PR #5 to move onto `harnesses:`;
  `:61-67` spawned CLI authority; live Herdr scenarios never ran (`:238-243`, `:290-292`).
- `plans/11-jev-typed-judgments/PLAN.md:74-77`, `:101-104` — resolve once at step 0, then a
  step-0 line in every calling command.
- `plans/7-codex-skill-model/PLAN.md:42-56` — capability not harness name; exact command
  allowlist. `plans/1-tdd-configuration/PLAN.md:39-51`, `:68-73` — decision written once; silent
  when off; stdlib tests prove behaviour.

### Herdr 0.8.2, observed live in this session (external)

- `~/.claude/skills/herdr/SKILL.md` (identical to `herdr --skill`); `:58` unknown ≠ completion;
  `:128` ask the user before answering a blocked agent; `:185` generic advice against file output
  (JDI departs from it deliberately); `:195` exit codes.
- Env set in every pane: `HERDR_ENV=1`, `HERDR_BIN_PATH`, `HERDR_SOCKET_PATH`, `HERDR_PANE_ID`,
  `HERDR_WORKSPACE_ID`, `HERDR_TAB_ID`. `herdr status` reports `running`, `compatible: yes`.
- `herdr pane split [--current] --direction right|down --cwd PATH --env K=V --no-focus` → new pane
  id at `.result.pane.pane_id` (verified `--help`).
- `herdr agent start <NAME> --kind <KIND> --pane <ID> [--timeout MS] [-- ARGS...]`: no `--cwd`,
  `--env`, or `--model`; model travels after `--` as the CLI's own flag; returns `agent_started`
  once ready or `agent_not_ready` (verified `--help`).
- `herdr agent prompt <T> <TEXT> --wait [--until S]... --timeout MS`: rejects `agent_blocked`
  up front; `agent_prompt_stalled` if no state change in 5000 ms; matches idle/done/blocked by
  default; **indefinite without `--timeout`** (verified `--help`). `herdr agent wait` same shape.
- States: `idle | working | blocked | done | unknown`; `done` = idle after unseen background
  work (a `--no-focus` worker usually ends `done`). Inspect: `agent get`, `agent read --source
  recent-unwrapped --lines N`, `agent explain`. Close: `herdr pane close <id>`.
- State detection here: Claude by screen rules (hook v7 reports session only, "outdated");
  OpenCode plugin v9 reports idle/working/blocked itself (`session.error` → blocked); Codex not
  installed, screen rules only.
- Machine: `claude` 2.1.282, `opencode` 1.18.10, no `codex`, no synced
  `~/.config/opencode/agent/jdi-*.md`.
- Codex `workspace-write` keeps `.git` read-only (openai/codex#15505, #14338): a Codex worker
  cannot write under `.git/jdi/runs/` without a user-written writable root.

## Implementation Plan

### Revision (2026-09-24)

The user revised the design after planning. These decisions replace the original rung-0 design
wherever the text below still differs, and the task files carry the exact text:

1. **Herdr only when the harness differs.** The Herdr path is a second way to run rung 2 of *How to
   delegate* (the separate CLI session), not a new rung 0. A role whose `models.<role>.harness` is
   empty or names the Butler's own kind is a native subagent, always, and never reaches Herdr. When
   the harness differs, `auto` or `herdr` with Herdr detected runs that CLI's interactive agent in a
   Herdr pane (H2 to H8); otherwise its non-interactive mode, exactly as today. `native` (the
   default) is today, including rung 4 for a kind with no known exec mode.
2. **Waves are in scope.** Executors on another CLI in a wave get one pane per task, all started
   together in one wave tab, each with its own run directory and `allowed_writes` (its task's
   `## Files` plus its run directory), at most 4 panes open at once. The Butler runs a multi-worker
   wait, sends the user to any blocked or questioning pane, lets the whole wave settle, never cancels
   a running sibling, validates each task, runs a combined file check against the union of the
   wave's `## Files`, and commits each task by path.
3. **Idle without a result file.** `idle` or `done` with no `result.json` is inspected: a question
   in the pane is pointed out to the user, who answers there, and the Butler keeps waiting; no
   question and no result is an H7 validation failure.
4. **No watch trigger.** The "user asked to watch the run" Herdr trigger is dropped from
   `reference/delegation.md`.

**The brief is overridden in two places, by the user, on 2026-09-24.** The brief asked to prefer a
Herdr agent over a native subagent whenever Herdr is on, and for one active delegated role per
Butler. The reasons for overriding both: a subagent is watchable in every harness JDI supports, so a
pane adds nothing for a role on the Butler's own CLI; a pane matters where another CLI runs, because
the user can answer that worker there; and waves already ran concurrently today through rung 2
processes, so panes add observability, not concurrency. "One active delegated role per Butler"
becomes "A Butler runs one phase at a time. Inside a phase, only a wave runs several workers at once,
and the Butler waits for all of them."

This plan answers the brief with the Butler's twelve decisions treated as settled. Line numbers refer to base commit `94912b3`. Each step lists its wave and dependencies so the Splitter can see which steps can run in parallel. Steps 7 and 8 form the separable `/jdi:herd` wave. Drop that wave and PR #5 can be rebased onto the shared mechanism instead.

**When this branch merges, PR #5 (`origin/herd-command`, head `2c28c11`) closes as superseded**, unless the user drops Wave 3. In that case PR #5 stays open and must be rebased onto `reference/herdr.md` H1, H2 and H4.

### Design summary (the decisions the steps implement)

**The config key.** A new `delegation:` block has one key, `transport`, with the values `native | auto | herdr` and the default `native`. One key covers both parts of the brief: `native` is "off", and `auto` or `herdr` is "on" plus a policy. The key passes the five-question test in `docs/config-key-lifecycle.md:320-335`:

- Two repos or two people would answer differently: yes. Whether someone works inside Herdr is a fact about their machine, so `.jdi/config.local.yml` is its natural home, and the docs say so.
- No level-2 source exists.
- It is not a frontmatter fact.
- It has a safe default, `native`.
- The ladder was written first (Step 3).

**What `native` means.** (Unchanged by the revision.) It is exactly today's behavior: the exec-first ladder, with Herdr reached only through today's rung 4, for a kind with no exec mode JDI knows. Nothing is probed at step 0 and nothing is announced. For the three kinds JDI knows (`claude`, `codex`, `opencode`), all have exec modes, so a user with no new keys never reaches Herdr. The only change under `native` is the mechanics of the rung-4 Herdr path, which move from pane-run to the agent surface (Decision 7). The only user who sees that change is one whose `models.<role>.harness` names a kind like `gemini`.

**What `auto` and `herdr` do.** (Revised 2026-09-24.)
- Step 0 performs **H1** once.
- A role on the Butler's own CLI (no `models.<role>.harness`, or one naming the Butler's kind) is unaffected: it stays a native subagent.
- When H1 succeeds, a role whose `models.<role>.harness` names another CLI runs through rung 2 as that CLI's interactive agent in a Herdr pane the user can answer, with `models.<role>.model` passed as the CLI's own model flag. Executors of a wave each get their own pane (`reference/herdr.md`, *Waves*). When H1 fails, or a Herdr run fails, rung 2 uses the CLI's non-interactive mode, as today.
- `auto` stays silent when `HERDR_ENV` is unset. That is the expected absence, and announcing it would repeat on every command run outside Herdr. It announces once when `HERDR_ENV=1` but a later check fails, because that is a malfunction.
- `herdr` announces any failed check once.
- In both modes, a failure hands the role back to native resolution. The phase always runs.

**Where the Herdr instructions go.** All `herdr` invocations go in one new file, `reference/herdr.md`, written as named operations H1 to H8 (H9 in Wave 3). This matches the T1-T8, J1-J5 and TS1-TS2 convention. `reference/delegation.md` gains the transport choice inside rung 2 and the selection table and refers to the file by name. No `herdr <subcommand>`, `HERDR_` variable or `AskUserQuestion` appears in `commands/`, `agents/`, `roles/`, `skills/`, or any other `reference/` file. A new test enforces this.

**The result contract.** The run directory is `$(git rev-parse --absolute-git-dir)/jdi/runs/<run-id>/`.
- I used `--absolute-git-dir` instead of `--git-dir` because `--git-dir` prints a relative `.git` in the main worktree, and the worker needs an absolute path. I verified that it resolves to `/Users/supherman/claude_plugins/just_do_it/.git` here.
- In a linked worktree the command resolves to `<common>/.git/worktrees/<name>`, which gives one run directory per worktree.
- The Butler writes `manifest.json` and `prompt.md`. The worker writes `report.md` and then, last, `result.json`. The Butler writes `outcome.json`.
- A terminal transcript is never the result. `agent read` is for inspection only.

**How blocked states reconcile.** `herdr agent prompt` rejects a blocked agent with `agent_blocked` before sending any input. I verified this in `herdr agent prompt --help` (0.8.2). So the Butler cannot answer a question UI through `agent prompt`. The rules are:
- `prompt.md` tells the worker to ask content questions by writing `result.json` with `"status": "needs_input"` and a `questions` list, and then to stop. The worker is then `idle`, so `agent prompt` accepts the Butler's answer.
- The user may also answer any worker directly in its pane. A worker that asks in chat instead goes `idle` or `done` with no `result.json`: the Butler reads the pane, points the user at it by agent name and pane ID, and keeps waiting. No question and no result is an H7 validation failure.
- The Butler answers only from context it already holds, and says so. Otherwise it relays the question to the user.
- A Herdr `blocked` state is therefore an approval, permission or trust dialog, or a question UI the worker opened despite the instruction. It always goes to the user.
- The Butler never uses `send-keys` on it.

**"Validate, never repair" versus "detect, never repair".** `/jdi:herd` keeps "validate, never repair" and stops. It has no fallback, and a herd that quietly became one sequential prep looks exactly like a herd that worked. Role delegation becomes "detect, never repair, then fall down the ladder". It never starts a server or installs an integration, and it always continues natively, because a phase that never ran is the failure.

**Model flag and authority.** The "JDI adds no flag of its own" rule is restated as "no authority-affecting flag". JDI already composes invocation flags and the model flag on the exec path (`reference/delegation.md:125-130`). The Herdr path composes the model flag exactly the same way:

| Kind | Model flag | Status |
|---|---|---|
| `claude` | `--model <model>` | verified in `claude --help` |
| `opencode` | `-m <provider/model>` | verified in `opencode --help` 1.18.10 |
| `codex` | `-m <model>` | not verified here: `codex` is not installed. See Risk 5 |

The model flag comes before the verbatim `harnesses.<kind>.args`, matching "after its own flags" in `reference/delegation.md:118`.

### Final config schema and defaults

This block is literal. It goes into `reference/config.md`'s `## Schema` fence after `harnesses:` (`:178-187`) and before `consumers:` (`:189`). Line breaks are the file's own. There are no elisions.

```yaml
# Optional. How a delegated role reaches its own process. See
# reference/delegation.md, "Choosing the transport", and reference/herdr.md.
delegation:
  # native | auto | herdr
  #   native - the delegation JDI has always done: a subagent where the harness
  #            has one, the CLI's non-interactive mode where `models.<role>.harness`
  #            names another kind, inline otherwise. Herdr is reached only for a
  #            kind with no known non-interactive mode. This is the default, and
  #            the only mode that probes nothing at step 0.
  #   auto   - when this session runs inside Herdr, a role whose
  #            `models.<role>.harness` names another CLI runs as that CLI's
  #            interactive agent in its own Herdr pane, where you can answer it,
  #            and the Butler waits for it. Every Executor of a wave gets its own
  #            pane. Outside Herdr, exactly `native`, and nothing is said.
  #   herdr  - as `auto`, but Herdr is expected: when it cannot be used, JDI says
  #            why, once, and delegates as `native`. The phase still runs.
  #
  # A role on this session's own CLI is never affected: it stays a subagent.
  # Whether you work inside Herdr is usually true of your machine, not the
  # repository: set it in .jdi/config.local.yml.
  transport: native
```

- Defaults table row (after `harnesses.*` at `:244`): `` | `delegation.transport` | `native` - roles are delegated exactly as before this key existed; nothing is probed at step 0 and nothing is announced | ``
- Example value in `jdi.config.example.yml`: `transport: auto`. The example deliberately uses a non-default value, per the lifecycle doc.

### Correlation, result and outcome fields

**`manifest.json`.** The Butler writes it before the spawn and never edits it afterward. Environment values are never recorded, only the keys.

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

For the Splitter, `allowed_writes` also lists the plan folder's task files and `PLAN.md`, because `agents/splitter.md:215-216` returns "Task files written to the plan folder". For an Executor in a wave, `allowed_writes` is its task file's `## Files` plus its run directory.

**`result.json`.** The worker writes it last.
- Fields: `run_id`, `role`, `status` (`complete | needs_input | failed`), `report` (`"report.md"`), `head_commit`, `summary`.
- With `needs_input` it adds `questions` (a list of strings). With `failed` it adds `reason`.

**`outcome.json`.** The Butler writes it at H8.
- Fields: `run_id`, `states` (a list of `{at, state, via}`), `final` (`valid | invalid | abandoned | transport_failed`), `validation` (checks passed and failures), `answers` (questions answered and by whom), `user_decisions`, `fallback` (null or the path taken), `pane_closed` (boolean).

Agent names match Herdr's `[a-z][a-z0-9_-]{0,31}`, for example `jdi-researcher-7f3a` or `jdi-synthesizer-7f3a` (20 characters). The Butler checks `herdr agent list` for a collision and draws a new suffix if it finds one.

### State-handling table

This table goes into `reference/herdr.md` H5. Every row names the Butler's next action.

| Observed | Meaning | Butler action |
|---|---|---|
| `working` (a per-call `--timeout` expired) | still running | Under the overall deadline: print one progress line and loop `herdr agent wait`. At the deadline: go to the `timeout` row |
| `blocked` | approval, permission, trust or question UI | H6: inspect with `agent get`, `agent explain`, `agent read --source recent-unwrapped --lines 80`, show the user what was seen, and ask. Never `send-keys` |
| `idle` or `done` | settled. **This is not proof of success** | H7: validate `result.json` and `report.md`. `needs_input` goes to H6's question path |
| `idle` or `done` with no `result.json` | the worker stopped without writing its result, often to ask something in chat | Inspect with `agent read --source recent-unwrapped`. A question or prompt in the pane: tell the user which pane (agent name and pane ID) and that they can answer there, then keep waiting; this is not a resubmit. No question and no result: H7 validation failure, announce, H8, fall back |
| `unknown` | Herdr cannot classify the agent | Inspect. Never count it as success. Continue waiting under the deadline (a plain `agent wait` does not match `unknown`) |
| `timeout` (overall deadline) | no settled state in time | Inspect. Never count it as success and never resubmit. Show whether a result file exists and ask: keep waiting, accept the file the user has checked, or abandon (H8, then fallback) |
| `agent_blocked` (the prompt was rejected) | a dialog was already open, so the prompt was **not** sent | H6. After the user clears the dialog, send the prompt: this is the first submission, not a resubmit |
| `agent_prompt_stalled` | the prompt was accepted but no state change came within 5000 ms | Do not resend. Run `agent get`, then continue the wait loop. If `agent read` shows the text still unsubmitted in the input box, ask the user |
| `agent_not_ready` (from start) | blocked at startup, usually a trust or first-run dialog | H6 with the prompt unsent |
| agent or pane gone, a JSON error on stderr with exit 1, or exit 2 | the worker exited or the transport broke | H8, announce, fall back. Treat as a transport failure (see below) |

Classification reads the JSON Herdr prints on stdout and stderr. The exit code alone is never evidence (`~/.claude/skills/herdr/SKILL.md:195`). The exact JSON field that holds the state is not assumed. It is recorded by UAT probe P6.

### Fallback announcement patterns

Use one line and state the observed cause. These are patterns, not literal text:

- Step 0, `herdr`: `delegation.transport is herdr, but Herdr is not usable here: <failed check> returned <what came back>. Delegating natively for this run.`
- Step 0, `auto`, inside Herdr but a later check failed: the same pattern, with `auto` in place of `herdr`.
- Per delegation: `The <Role> did not run as a Herdr agent: <operation and observed reason>. Running it <as a subagent on <model> | through <kind>'s non-interactive mode | inline> instead.`
- Invalid value: `delegation.transport is "<value>", which is not native, auto or herdr. Delegating natively for this run.`

A harness failure and a model failure that fire together are one announcement, as `reference/delegation.md:168-172` already requires.

Transport-level failures switch the rest of the run to native, announced once, so later phases do not repeat a broken launch. These are: the pane cannot be created, a Herdr CLI error, or the run directory cannot be created. Kind-level failures and result-validation failures affect only that one delegation.

### Wave 1 (no dependencies; Steps 1, 2 and 3 run in parallel)

#### Step 1. Write `reference/herdr.md` and enumerate it

Files:
- `reference/herdr.md` (new)
- `README.md` (one table row only)
- `AGENTS.md` (the sentence at `:50-52`)
- `tests/test_herdr_operations.py` (new)

**The outline below is exact and the tests pin it.** Headings use a spaced hyphen, not an em dash, per the writing rules. This is the file's own deviation from `reference/jev.md`'s `## J1 - ` style.

- `# Herdr operations`. The intro says:
  - Herdr is a transport: a Butler uses it to run a delegated role that is configured on another CLI as that CLI's interactive agent, in a pane the user can answer, and to wait for it.
  - `reference/delegation.md` rung 2 (under `auto` or `herdr`) and rung 4 call the operations by name.
  - `herdr` means `$HERDR_BIN_PATH` when that is set, else `herdr` on `PATH`.
  - Commands are argument lists, and placeholders are in angle brackets.
  - Everything in the file is inert under `delegation.transport: native`, except where rung 4 sends a kind with no exec mode.
- `## The universal rules`:
  1. Capability is observed and never inferred from the harness name.
  2. Detect, never repair: JDI starts no server, installs no integration, and changes no Herdr setting.
  3. A Butler runs one phase at a time. Inside a phase, only a wave runs several workers at once, and the Butler waits for all of them and does nothing else in the command meanwhile.
  4. The result arrives through a file. `agent read` is for inspection only.
  5. `idle` or `done` is not proof of success, and `unknown` or `timeout` never counts as success.
  6. The Butler never resubmits blindly.
  7. The worker's dialogs belong to the user.
  8. A pane JDI created is closed on every exit.
  9. A worker is a separately spawned CLI: its authority comes from its own configuration and from the arguments the user wrote.
- `## Scope`:
  - Only a role whose `models.<role>.harness` names another CLI reaches these operations. A role on the Butler's own CLI never runs under Herdr: it stays a subagent, watchable in the harness itself.
  - The single roles run one worker each; Executors in a wave run one worker per task (`## Waves`).
  - A worker uses the Butler's own worktree, because the Butler waits.
  - Butlers started by `/jdi:herd` are isolated from each other by worktrees.
- `## H1 - Detect Herdr`:
  - Performed once, at step 0. Checks run in order and the first failure wins:
    - (a) `printenv HERDR_ENV` prints `1`;
    - (b) the binary resolves: `$HERDR_BIN_PATH` is executable, else `command -v herdr`;
    - (c) `herdr status` reports server `status: running` and `compatible: yes`, and `HERDR_SOCKET_PATH`, when set, is an existing socket.
  - The answer, "available" or the first failed check with its output, is used for every delegation in the run. No role re-probes.
  - The `auto` versus `herdr` announcement rules from the design summary.
  - The sentence "never from the harness name".
- `## H2 - Check the worker kind`:
  - The kind is `models.<role>.harness`, and only that. A role with no `harness`, or one naming the Butler's own kind, never reaches this operation.
  - Supported: the kind appears on the `kinds:` line of `herdr agent`. That line **lists the kinds Herdr supports**, not the kinds installed.
  - Installed: `command -v <kind>` resolves.
  - `herdr integration status` affects only detection quality. It is recorded in the manifest and stated once when the kind's integration is missing or outdated (for example, "lifecycle states for claude come from screen rules").
  - The model-flag table from the design summary. For a kind with no known flag, rung 10 applies.
  - With no `models.<role>.model`, no flag is passed, and the worker runs on its CLI's own default, which may differ from this session's model. Say so in the pre-spawn line.
- `## H3 - Prepare the run`:
  - Run ID and agent name as above.
  - `git rev-parse --absolute-git-dir`, then `mkdir -p <gitdir>/jdi/runs/<run-id>/`. A failure here is a transport failure.
  - The `manifest.json` field list above.
  - The `prompt.md` template (Appendix A, verbatim).
  - The role instructions are the installed `agents/<role>.md` body with its frontmatter removed. The Butler reads it with the same resolution it uses for `reference/`, copies the text, and never hands the worker a plugin path (`docs/harness-adapter-architecture.md:191-194`).
  - Inputs: exactly the role's *What it receives*. Short values are written inline and file inputs are given as absolute paths.
  - The short prompt, verbatim: `Read <abs run dir>/prompt.md and follow it exactly. This is JDI run <run-id>.`
  - Run directories are kept. JDI never deletes them in this release. Removing a linked worktree removes its git directory and its runs. The user may delete `<gitdir>/jdi/runs/` at any time.
- `## H4 - Start the worker`:
  - Print, before the spawn, the agent name, kind, model, every argument verbatim (from `harnesses.<kind>.args`), the environment keys, and the run directory. The words "printed back before the spawn" appear.
  - Choose the direction with `herdr pane layout --pane "$HERDR_PANE_ID"`: `right` for a wide pane, `down` otherwise.
  - Create the pane: `herdr pane split --current --direction <d> --cwd <worktree root> [--env KEY=VALUE ...] --no-focus`. Read `.result.pane.pane_id`. `--env` carries `harnesses.<kind>.env` verbatim, because `herdr agent start` has no `--env` or `--cwd` (verified in `--help`).
  - In a wave, every worker's pane goes in the wave's own tab (`## Waves`): the first worker uses the tab's root pane, later ones split inside it.
  - Start the agent: `herdr agent start <name> --kind <kind> --pane <pane_id> --timeout 120000 [-- <model flag> <args...>]`. Pass `--` only when something follows it.
  - `agent_started` means continue. `agent_not_ready` means H6 with the prompt unsent. Any other error means H8, then fallback.
  - Section **H4b** (reused by `/jdi:herd`) is the start command alone, applied to a pane and a name the caller supplies.
- `## H5 - Prompt and wait`:
  - `herdr agent prompt <name> "<short prompt>" --wait --timeout 300000`, then loop `herdr agent wait <name> --timeout 300000` until a settled state appears or the overall deadline passes.
  - The overall deadline defaults to 2700000 ms. A value the user states in the conversation wins for that run.
  - Set the shell tool's own timeout above each call. Where the shell tool caps lower than 300000, use its cap minus 30000.
  - Without `--timeout`, Herdr's wait is indefinite (verified in `--help`), so `--timeout` is mandatory.
  - The state table above.
- `## H6 - Handle a blocked worker`:
  - Inspect with `agent get`, `agent explain <name>`, and `agent read <name> --source recent-unwrapped --lines 80`.
  - Show the user what was seen.
  - Approval, permission, trust, or any question UI goes to the user. The user answers in the worker's pane. The Butler offers to focus the pane and does so only on a yes. Then it resumes `herdr agent wait`.
  - **Never `send-keys` into** a dialog.
  - `needs_input` in `result.json`:
    - Move the file to `result.needs_input.<n>.json`.
    - Answer from context the Butler already holds, saying which question it answered and from what, or relay the question to the user.
    - Send the answer with `herdr agent prompt <name> "<answer>" --wait --timeout 300000`.
    - Resume H5.
  - The reason: `agent prompt` rejects a blocked agent before sending input, so a question is answerable only once the worker is idle.
- `## H7 - Validate the result`. All checks must pass:
  1. `result.json` exists and parses as JSON.
  2. `run_id` and `role` equal the manifest's.
  3. `status` is `complete`.
  4. `report.md` exists, is not empty, and contains every item in the role's *What it returns*.
  5. `head_commit` equals the manifest's and HEAD has not moved.
  6. `git status --porcelain` shows no change outside `allowed_writes`, which checks the "no authority beyond the command" rule.

  Then the command's own spot-check still runs: `commands/prep.md:130-133` and `commands/research.md:64-67`. A failure means H8, then announce with the failed check, then fallback. `failed` status, or a final message `JDI-RESULT-UNWRITABLE <run-id>: <reason>` seen during inspection, is a validation failure with that reason in the announcement. It is never a silent success.
- `## H8 - Close the pane and record the outcome`:
  - Write `outcome.json`.
  - Run `herdr pane close <pane_id>` on every exit: success, failure, abandon, or a fallback of any kind.
  - Keep the pane open only when the user asks to inspect it, and then say who now owns closing it.
  - A failed delegation must not leak one pane per attempt.
- `## When a step fails`: a table mapping each failure to its `reference/delegation.md` rung (6 to 9), whether it is transport-level or delegation-level, and the announcement pattern.
- `## Why the agent surface, not pane run`:
  - The reason is lifecycle state. `agent start` and `agent prompt --wait` report `working`, `blocked`, `idle`, `done` and `unknown`. That lets the Butler tell a worker waiting on an approval apart from one still thinking, which a sentinel match on pane output cannot do.
  - The result still arrives through a file, so the 1.0.5 objection to `agent read` as a result channel still stands. Rows lost to the alternate screen cannot be recovered (`~/.claude/skills/herdr/SKILL.md:183-185`). That is why `agent read` is limited to inspection.
  - This replaces the pane-split, pane-run, wait-output recipe and the "Not `herdr agent start`" line that `reference/delegation.md:136-141` carried.
- `## Waves` (Executors on another CLI, under `auto` or `herdr` with Herdr detected):
  - One pane per task, all started together, each with its own run directory, agent name and `manifest.json`; `allowed_writes` is the task's `## Files` plus its run directory.
  - One wave tab: `herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd <worktree root> --no-focus`, then `herdr tab rename <tab_id> jdi-wave-<first run id>`.
  - At most 4 worker panes open at once; fill the cap and start the next task as each slot frees, as the subagent-cap rule does.
  - The multi-worker wait cycles `herdr agent wait <name> --timeout 30000` (or `agent get`) over every live worker under the overall deadline, applying the H5 table to each, and sends the user to any blocked or questioning pane by agent name and pane ID.
  - The whole wave settles before any result is acted on; a sibling that is still running is not cancelled because another failed.
  - H7 checks 1 to 5 per task, then the combined file check once: every change must fall inside the union of the wave's `## Files` lists plus their run directories. A change outside it cannot be attributed to one task in a shared tree, so it is reported and the Butler asks before committing.
  - One commit per task by path; H8 closes every pane, then the tab. A failed task falls back on its own after the wave settles.

Also in Step 1:
- `README.md`: insert a row after `reference/delegation.md` at `:344`: `` | `reference/herdr.md` | The Herdr operations (H1-H8) a Butler uses to run one role as its own agent process and wait for its result | ``
- `AGENTS.md:50-52`: add `` `reference/herdr.md` `` to the list, before `` `reference/delegation.md` ``.

#### Step 2. Add the `delegation` block to the config documents

Files:
- `reference/config.md` (three edits, plus two wording corrections)
- `jdi.config.example.yml`
- `tests/test_config_schema.py`

The three edits:
1. The schema block above.
2. The defaults row above.
3. Invariant bullets under `## Notes`, inserted after the `harness` bullet at `:287-290`:
   - **`delegation.transport: native` is today's delegation, unchanged.** A repo with no `delegation` block behaves exactly as before the key existed.
   - **`auto` and `herdr` are detected once, at step 0, and never repaired.** State H1 and the announcement rules.
   - **The transport never grants authority.** A Herdr worker is a separately spawned CLI, and its dialogs belong to the user.
   - **The transport degrades to `native`, never beyond.** A failed Herdr run returns the role to native resolution for its kind. It never skips the phase, never opens a third CLI, and never acquires a flag.
   - **`delegation.transport` is usually personal.** It belongs in `config.local.yml`, because working inside Herdr is a fact about the machine.

The two wording corrections:
- `:164-170`, the `harnesses` comment: change "adds no flag of its own - in particular no approval- or sandbox-affecting one" to "adds no flag of its own beyond the model flag and the invocation JDI needs to reach the CLI, and never an approval- or sandbox-affecting one". Keep "or, under Herdr, on the pane", which stays true under H4.
- `:283-286`: add that under a separate process, including Herdr, the model is passed as the CLI's own model flag, so a full identifier the Agent tool's enum cannot express can be expressed there.

In `jdi.config.example.yml`: add a `delegation:` block after `harnesses:` (`:113-122`) with a three-line comment and `transport: auto`.

#### Step 3. Rewrite the transport in `reference/delegation.md`, the Butler and the Feedbacker

Files:
- `reference/delegation.md`
- `roles/butler.md`
- `agents/feedbacker.md`
- `tests/test_codex_plugin.py` (rewrites)
- `tests/test_delegation_transport.py` (new)

`reference/delegation.md` edits, in file order:

- `:51-54`: the rule becomes "**the Feedbacker should not run on the same model and harness as the agent whose output it is reviewing**". The same-model note stays, extended to "same model on the same harness".
- A new section, `## Choosing the transport`, before `## How to delegate`:
  - The literal sentence "A role on this session's own CLI never runs under Herdr."
  - The `native | auto | herdr` table, scoped to a role whose `models.<role>.harness` names another CLI (rung 2).
  - Any other value: announce once and treat as native.
  - The literal sentence "A Butler runs one phase at a time." plus "Inside a phase, only a wave runs several workers at once, and the Butler waits for all of them before doing anything else in the command."
  - "Detect, never repair."
- `:58-61`: keep both sentences unchanged. Rung 2 is still what the configuration selects; the transport changes how rung 2 runs. There is no rung 0.
- Rungs 1, 2 and 3 keep their bold openings verbatim, because `tests/test_codex_plugin.py:196-202` pins their order. At the end of rung 2's paragraph add: "When `delegation.transport` is `auto` or `herdr` and step 0 detected Herdr, rung 2 runs the other CLI as its interactive agent in a Herdr pane instead of its non-interactive mode (`reference/herdr.md` H2 to H8). On any Herdr failure: announce once, and run the same role through the CLI's non-interactive mode; it is never retried on Herdr in the same phase, and the phase is never skipped."
- `:102-104`, the rung-2 bullet in *Delegating several roles at once*: keep the first sentence, and change the Herdr sentence to "Under Herdr that is one pane per task, all started together in one wave tab, each with its own run directory, at most 4 open at once (`reference/herdr.md`, *Waves*); the Butler waits on every worker, sends the user to any pane that is blocked or asking, and every pane JDI opened is closed on every exit." No test pins the replaced sentence.
- `:117-120`: keep the first two sentences. Change the last to: "Under `transport: native`, resolution is exec-first, Herdr second. Under `auto` or `herdr` with Herdr detected, a role on another CLI runs in a Herdr pane first, and exec is its fallback."
- `:122-134`: keep them verbatim. They are pinned: "Prefer the CLI's own non-interactive mode", "codex exec -m <model> -o <file>", and "`harness: claude` is a first-class value". Add one sentence: "The model flag is the one flag JDI composes from the config, on every separate-process path, exactly as above."
- Replace `:136-145` with two paragraphs, with no `herdr` commands:
  - **Herdr.** Under `native`, Herdr is used only when the kind has no exec mode JDI knows. Under `auto` or `herdr` it is how rung 2 runs another CLI when Herdr is detected. Every Herdr step (detection, pane, start, prompt and wait, states, the result contract, waves, pane close) is in `reference/herdr.md` and nowhere else. It uses Herdr's agent surface and receives the report through a file, and `reference/herdr.md` gives the reason. The current "watch the run" trigger is dropped and not mentioned (revision decision 4).
  - **A pane JDI created is JDI's to close** (H8).
- `:147-153`: add "Under Herdr, the role file is copied into the run's `prompt.md` (`reference/herdr.md` H3)". The rest is unchanged.
- `:155-164`: keep every sentence (pinned). Append:
  - A Herdr worker is a separately spawned CLI in this sense.
  - The worker's approval, permission and trust dialogs belong to the user, and the Butler never answers one.
  - The Butler answers a worker's content question only from context it already holds, and says so.
  - A worker writes only its run directory and what the active command lets the role write, and the Butler checks the tree afterward (H7).
- `:166-225`, rungs 4 and 6 to 9:
  - Rung 4: "Try the Herdr transport, `reference/herdr.md` H1 to H8 (rungs 6-9)."
  - Rung 6: "Herdr is wanted but not detected. H1 failed at step 0."
  - Rung 7 becomes: "**The kind is not one Herdr supports, or its CLI is not installed.** Herdr's `kinds:` line lists the kinds it supports; installed means `<kind>` resolves on `PATH`. Integration status affects only detection quality." This fixes the misreading at `:189-190`.
  - Rung 8: "The pane or the agent cannot be started."
  - Rung 9: "The run started but produced no valid result. H7 failed, or the state stayed `unknown` or timed out and the user chose to abandon. `unknown` does not prove completion."
  - The shared tail for rungs 6 to 9: "Close the pane JDI opened (H8), announce, and continue as `native` would resolve the role: rung 1 or rung 2 of *How to delegate*, or the floor where rung 4 sent a kind with no exec mode."
- `:212-214`: keep "Never acquire a flag the user did not write." (pinned). Change the next sentence to: "JDI composes only the invocation and the model flag, adds no authority-affecting argument of its own, and translates none between kinds."

`roles/butler.md`:
- `:22-24`: append "A report from a separately launched worker is accepted only through its validated result file, never a transcript."
- `:30-34`: change the list to "A test runner, a tracker integration, a Jev API key, a delegation transport".
- New sentence in the Responsibilities list: "A Butler runs one phase at a time; inside a phase, only a wave runs several workers at once, and the Butler waits for all of them."
- No Herdr command appears.

`agents/feedbacker.md:35-37`: change to "should not run on the same model and harness that produced the output under review", and "If no different model or harness is available, run the review anyway and say that producer and reviewer were the same."

The existing test assertions that must be rewritten in this step:
- `tests/test_codex_plugin.py:213-218` (`test_harness_is_a_first_class_value_in_both_directions`). Remove `"herdr pane split"` and `"Not \`herdr agent start\`"`. Keep `"\`harness: claude\` is a first-class value"` and add `"\`reference/herdr.md\`"`.
- `tests/test_codex_plugin.py:220-231` (`test_degradation_ladder_runs_from_the_first_rung_to_the_floor`). Remove `"herdr pane close"`; it moves to Step 1's `HerdrOperationsTest`. Keep the rest.

### Wave 2 (Steps 4, 5 and 6 run in parallel with each other)

#### Step 4. Command step-0 lines and hand-off sites

Depends on Steps 2 and 3.

Files:
- `commands/prep.md`, `research.md`, `plan.md`, `split.md`, `feedback.md`, `pr.md`, `execute.md`, `next.md`, `yolo.md`
- `tests/test_step_zero_transport.py` (new)

**The step-0 line is repeated in place in six files.** It is inserted as a new paragraph after the Jev paragraph, which ends at: `prep.md:39`, `research.md:33`, `plan.md:32`, `split.md:32`, `feedback.md:36`, `pr.md:33`. The text is literal apart from its wrap. The pinned fragments are the bold opening, "perform **H1** from JDI's `reference/herdr.md`", and "With `delegation.transport` `native` or absent, say nothing at all".

> **Then resolve the delegation transport, once** - If `delegation.transport` is `auto` or `herdr`, perform **H1** from JDI's `reference/herdr.md` here and nowhere else, and use its answer for every delegation in this run; no role re-probes. With `herdr`, a failed check is announced once, with the check and what came back, and this run delegates as `native`. With `auto`, say nothing when this session is not inside Herdr, and announce once when it is but a later check fails. With any other value, say so once and delegate as `native`. **With `delegation.transport` `native` or absent, say nothing at all** - nothing was skipped.

Other edits:
- Block-name lists:
  - `prep.md:28-29` becomes "…`jev`, `models`, `harnesses`, and `delegation` from it."
  - `research.md:23-24` becomes "…`jev`, `models`, `harnesses`, and `delegation` from that config."
- `prep.md:130-133` (step 9): prepend "When the Researcher ran as a separate process, its findings are the result file the transport validated (`reference/delegation.md`), never a terminal transcript; a result that failed validation was already announced and the role re-run another way."
- `research.md:64-67` (step 4): the same addition.
- `prep.md:136` (step 10) and `research.md:72` (step 5): add "delegated exactly as in step 8" and "delegated exactly as in step 3". These are within-file references.
- `feedback.md:48-50`:
  - "pick a different model or a different harness from the one that produced the output".
  - "If neither differs, run the review anyway and say that producer and reviewer were the same."
  - `:62-65`: append "When the transport waits on a separate process, that wait is this active turn, and its timeout handling replaces 'promptly'."
- `execute.md:78-82`, `next.md:66-69`, `yolo.md:98-102`: add one sentence at each site: "Each Executor is resolved per *Delegating several roles at once*, including the transport `delegation.transport` selects; a worker waiting on the user is answered where it runs, and the wave settles before anything is verified or committed." No transport name or Herdr term appears in these bodies. Keep "*Delegating several", which `tests/test_parallel_waves.py:45-53` pins.
- The step-0 transport line also goes into `execute.md`, `next.md` and `yolo.md`, which have no Jev paragraph: as a new paragraph at the end of step 0, after "...because it is meant to be ignored." (`execute.md:23`, `next.md:21`, `yolo.md:21`). Nine files carry the line in all.
- `commands/reresearch.md` and `commands/replan.md` inherit the line through their sibling's step 0 (`reresearch.md:16`). Leave them unchanged and say so in the commit body.
- `commands/status.md`, `done.md` and `start.md` do not delegate. They are excluded, and the commit body says so.

#### Step 5. User-facing docs: init, help, README

Depends on Steps 1 and 2.

Files:
- `commands/init.md`
- `commands/help.md`
- `README.md`
- `tests/test_transport_docs.py` (new)

`commands/init.md`:
- `:2`: the description adds ", how delegated roles reach their own process," before "and which model each role runs on".
- Insert a new step 10 after the models step (`:141-169`): **Ask how delegated roles should run - only when this session is inside Herdr.**
  - Perform **H1** from `reference/herdr.md`.
  - When `HERDR_ENV` is unset, skip the question entirely and write no `delegation` block.
  - Otherwise, propose `native` (the default) and explain `auto` and `herdr` in one sentence each.
  - Say that it is usually personal, and offer to leave it out of `config.yml` for `config.local.yml`.
- Renumber the old steps 10-13 as 11-14. Fix the back-reference at `:24`: "step 11 offers the fix" becomes "step 12". `grep -n "step [0-9]" commands/init.md` shows no other reference to the renumbered steps: `:67`, `:74`, `:113`, `:139` and `:168` refer to steps 1-3.

`commands/help.md`:
- `:9-15`: the closing line adds "which delegation transport is set, when it is not `native`".
- `:28`, the `/jdi:init` row: add "delegation transport".
- `:29`, the `/jdi:prep` row: add "Runs a role configured on another CLI in its own pane when `delegation.transport` allows it."
- A new `### Separate agent processes` subsection after `### Roles and models` (`:149-162`). Two paragraphs:
  - What `auto` and `herdr` do: a role on another CLI runs in its own pane, every Executor of a wave gets its own pane, and the result arrives as a file the Butler validates. A role on this session's own CLI stays a subagent.
  - Blocked or questioning workers are answered by you in their pane, the rest falls back to the CLI's non-interactive mode, and `native` is silent.

`README.md`:
- `:186` and `:202-204`: add "how delegated roles reach their own process" to both enumerations of init's questions.
- A new `### Separate agent processes under Herdr` section after `### Typed judgments with Jev` (`:248-278`). It has a `| \`delegation.transport\` | What you get |` table with three rows, then paragraphs covering: only roles on another CLI are affected, the run directory, validation before use, blocked and questioning workers answered in their pane, waves as one pane per task (at most 4 at once, in one tab), the fallback, and one phase at a time.
- `### Roles and models, not agents and vendors` (`:356-378`): add one bullet after the three existing ones: "**A role is set on another CLI** → run that CLI's non-interactive mode, or, when `delegation.transport` allows it and Herdr is detected, its interactive agent in a Herdr pane you can answer; either way the Butler waits for its validated result." Keep the three pinned phrases (`tests/test_codex_plugin.py:322-324`).

#### Step 6. Architecture docs

Depends on Steps 1, 2 and 3.

Files:
- `docs/delegation-transport-architecture.md` (new)
- `docs/harness-adapter-architecture.md`
- `docs/config-key-lifecycle.md`
- `tests/test_delegation_transport.py` (adds `ArchitectureDocTest`; Step 3 wrote this file in Wave 1)

`docs/delegation-transport-architecture.md`. The headings are pinned by the test:
- `# Delegation Transport Architecture`
- `## Status`
- `## Purpose`
- `## Two layers`: `/jdi:herd` fans tickets out to independent Butlers, one worktree, workspace, branch and ticket each. Inside one Butler, sequential role delegation. The Butler never multitasks.
- `## Backend choice`: native versus Herdr, and why the agent surface.
- `## Capability detection`: H1, and why never the harness name.
- `## Result contract`: the files, the fields, H7, and why a file instead of a transcript.
- `## States`: a summary, with a reference to H5.
- `## Authority`
- `## Isolation`: worktrees, and workers sharing the Butler's worktree.
- `## Configuration`: `delegation.transport`, `models.<role>`, `harnesses.<kind>`, and the herd keys.
- `## Validate, never repair versus detect, never repair`
- `## Waves and other roles`: every role on another CLI uses the same H2 to H8; waves get one pane per task, the cap, the multi-worker wait and the combined file check; "one phase at a time" replaces the brief's "one active delegated role per Butler", with the reason.
- `## Live validation matrix`: Butler Claude Code in Herdr; worker A `opencode` (single role and a wave), worker B the same-harness control (a role with `harness: claude` under a Claude Butler stays a native subagent, no pane), worker C `codex` (requires install). It refers to this plan's UAT task.
- `## Relationship to PR #5`: the herd layer's contract is H1, H2, H4b and the H9 that `/jdi:herd` adds. PR #5 closes as superseded when the herd wave ships, or is rebased onto this contract if the wave is dropped.

`docs/harness-adapter-architecture.md:238-263`:
- Add to item 2, not as a new item: "When `delegation.transport` allows it and Herdr is detected, this runs the other CLI as its interactive agent in a Herdr pane, one pane per task in a wave (`reference/herdr.md`)."
- `:244`: qualify it as "under `native`, … exec first".
- `:27`: add "Herdr" to the reference contracts list.

`docs/config-key-lifecycle.md`. These are passing corrections, and the commit body says so:
- `:122-123` and `:354-355`: "are all `1.0.6`" becomes "carry the same version". Keep "**Three version files, and they must match.**" and the other strings `tests/test_versions.py:83-89` pins.
- `:81-84`: re-derive the `reference/config.md` schema, defaults and notes ranges against the post-Step-2 file and correct them.
- `:425`: `commands/prep.md:23-24` becomes `commands/prep.md:28-29` and adds `commands/research.md:23-24`.
- `:430-431`: correct `README.md:290-294` and `AGENTS.md:49-53` to the current lines.
- Verify every `reference/config.md:` citation in the file against the post-Step-2 file.

### Wave 3: the `/jdi:herd` layer (separable; Steps 7 and 8 run in parallel)

#### Step 7. The herd config block

Depends on Step 2.

Files:
- `reference/config.md`
- `jdi.config.example.yml`
- `tests/test_config_schema.py` (adds `HerdBlockTest`)

- Schema: after `delegation:`, add a `herd:` block with `kind: claude` and `max_parallel: 5`. The comments are PR #5's, with the `kinds:` wording corrected to "a kind Herdr supports whose CLI is installed".
  - `seed: {}` keeps PR #5's commented structure and placeholders (`git show origin/herd-command:reference/config.md`, the `seed` comment block).
  - No `args` or `env` keys. A comment says herd agents take `harnesses.<herd.kind>.{args,env}`.
- Defaults rows: `herd.kind` `claude`, `herd.max_parallel` `5`, `herd.seed` empty.
- Notes: PR #5's four bullets, rewritten.
  - "`herd` is read by `/jdi:herd` and nothing else."
  - "`/jdi:herd` validates Herdr and stops; it never repairs", with the justification that it has no fallback, and a herd that became one prep looks like a herd that worked.
  - The `herd.seed` bullet.
  - "Herd agents take their arguments and environment from `harnesses.<herd.kind>`, verbatim."
- Example: `herd: {kind: opencode, max_parallel: 3}`, written as a two-space block because `key_paths` needs it. `seed: {}` goes with PR #5's commented example.

#### Step 8. `commands/herd.md`, H9, and the command enumerations

Depends on Steps 1, 5 and 6.

Files:
- `commands/herd.md` (new, reworked from `origin/herd-command:commands/herd.md`)
- `reference/herdr.md` (appends H9)
- `AGENTS.md`
- `README.md`
- `skills/run/SKILL.md`
- `docs/harness-adapter-architecture.md`
- `commands/help.md`
- `commands/init.md`
- `docs/config-key-lifecycle.md`
- `tests/test_enumerations.py`
- `tests/test_herd.py` (new)

`commands/herd.md` rework. PR #5's twelve steps stay, with these changes:
- (a) Step 1 is main's config load verbatim, including `config.local.yml`, then "reads `herd`, `harnesses`".
- (b) Step 2 performs **H1**, then **H2** for `herd.kind` or a `--kind` in `$ARGUMENTS`.
  - Validate, never repair: the first failure stops the run with its reason.
  - Never fall back to a sequential `/jdi:prep`.
  - `delegation.transport` is irrelevant here.
- (c) Step 5: one name per issue, `jdi-herd-<issue, lowercased, non-[a-z0-9-] replaced by ->`, cut to Herdr's 32-character rule, used as the Herdr agent name, the tab label and the worktree folder name. PR #5's bare lowercased ID fails Herdr's `^[a-z]` rule for a GitHub issue like `4`. A name held by a live agent is reported and the user is asked, as PR #5 does.
- (c2) Step 10 keeps the worktree path and scratch branch in the report. Step 12 adds the cleanup guard: a worktree with uncommitted plan files is never removed without an explicit yes, and the plan commit is offered first. See *Herd names and the cleanup guard* below.
- (d) Step 6 performs **H9**. Step 8 performs **H4b** with `harnesses.<kind>.args` printed verbatim and no model flag, because the Butler has no `models` key. Step 9 hands each Butler its command per H9's invocation table, with no wait.
- (e) Step 11 asks through "the harness's own multiple-choice question facility, where it has one; otherwise inline as a numbered list". No `AskUserQuestion`. The watch-loop text refers to H9 *Watch* instead of `herdr agent read`.
- (f) Step 12 lists cleanup per H9.
- (g) The "Limits" section drops the `--lines` detail.
- (h) No `herdr` command, `HERDR_` variable, or harness tool name appears in the body.

`## H9 - Give a Butler its own worktree`, for `/jdi:herd` only:
- `herdr worktree create --cwd "$PWD" --path <worktrees dir>/<repo>/jdi-herd-<issue> --branch jdi-herd-scratch-<herd-id>-<N> --base origin/<default> --label "<ISSUE-ID>" --no-focus` (PR #5's command plus `--path` and a unique scratch branch; see *Herd names and the cleanup guard*), reading `.result.worktree.path`, `.result.root_pane.pane_id` and `.result.workspace.workspace_id`.
- When `harnesses.<kind>.env` is not empty, `herdr tab create --workspace <id> --cwd <path> --env KEY=VALUE ... --no-focus`, then use `.result.root_pane.pane_id`.
- The invocation table:

  | Kind | Invocation |
  |---|---|
  | `claude` | `/jdi:prep <ISSUE-ID>` |
  | `codex` | `$jdi:run prep <ISSUE-ID>` |
  | `opencode` | `/jdi-prep <ISSUE-ID>` |

  These spellings come from the README install table that `tests/test_codex_plugin.py:269-276` pins. Other kinds are rejected at H2 for herd.
- `herdr agent prompt <name> "<invocation>"` with no `--wait`.
- *Watch*: `herdr agent get` and inspection-only `agent read`.
- Cleanup: `herdr worktree remove --workspace <id>`, plus `--force` when seeded.

Enumerations:
- `AGENTS.md`: a command table row.
- `README.md:334`: "The 16 workflow commands" becomes "The 17 workflow commands", plus a short `/jdi:herd` paragraph under `## Use it`.
- `skills/run/SKILL.md:18-35`: add `herd` in sorted position.
- `docs/harness-adapter-architecture.md:34-51`: add `herd` to the allowlist.
- `commands/help.md`: a `/jdi:herd` row.
- `commands/init.md` step 10: a sub-bullet offering `herd.kind`, `herd.max_parallel` and `herd.seed` when the user plans to use `/jdi:herd`.
- `docs/config-key-lifecycle.md:51-59`: "twelve of the sixteen" becomes "thirteen of the seventeen", with `commands/herd.md:<line>` added to the list.
- `tests/test_enumerations.py:230-235`: `12` becomes `13`. Update the docstring at `:219`.

### Wave 4

#### Step 9. Release 1.0.10

Depends on Steps 4, 5 and 6, and on Steps 7 and 8 unless the user dropped them.

Files:
- `.claude-plugin/plugin.json:3`
- `.codex-plugin/plugin.json:3`
- `.claude-plugin/marketplace.json:10`: all three `1.0.9` → `1.0.10`
- `CHANGELOG.md`: a new `## 1.0.10` entry

The CHANGELOG entry:
- A bold headline: "**A Butler inside Herdr can run a delegated role as its own agent process, wait for it, and accept its work only through a validated result file.**"
- The first bullet covers `delegation.transport` and states: "a repo with no `delegation` block behaves exactly as it did".
- Then bullets for:
  - `reference/herdr.md`;
  - the result contract;
  - blocked and timeout handling;
  - the fallback ("Degrades to `native`, never beyond");
  - a role on the session's own CLI stays a subagent; only roles on another CLI, waves included, get panes;
  - the corrected `kinds:` reading;
  - the Feedbacker's "model or harness" rule;
  - the herd bullet, only if Wave 3 shipped: "`/jdi:herd` arrives on the shared Herdr operations; `herd.args` and `herd.env` from PR #5 are replaced by `harnesses.<kind>`".

The commit subject is `feat: Run delegated roles as Herdr agents with a result contract (1.0.10)`. Its body names what was deliberately left out: tiers, a runs-path override key, and `skills/run/SKILL.md:90-92` (considered and unchanged, because "as that contract directs" covers the rung-2 transport).

### Wave 5

#### Step 10. UAT

Depends on Step 9. It is the live procedure in the Testing Strategy, and it maps every acceptance clause to evidence.

### Appendix A: the `prompt.md` template

Step 1 writes this verbatim into H3. It is literal except for the `<...>` placeholders, and the line breaks are the file's own.

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

### Herd names and the cleanup guard (decided after planning, 2026-09-24)

JDI's durable state is the plan on the branch: `PLAN.md`, each task's `status:`, and one commit per
task. A fresh session started in a herd worktree picks the work up with `/jdi:status` or
`/jdi:yolo`, so JDI does not name or resume harness sessions. It passes no session-name flag, and
the model flag stays the only flag it composes.

- Herd agents and their tabs are named `jdi-herd-<issue>`, because Herdr needs a valid agent name
  and rejects a bare numeric ID. The workspace label stays the issue ID.
- The worktree folder is named `jdi-herd-<issue>`, under Herdr's worktrees directory and the repo
  name (`<worktrees dir>/<repo>/jdi-herd-<issue>`). After a crash or a closed workspace,
  `git worktree list` shows which folder holds which issue, even if prep never reached its branch
  step, and `herdr worktree open` brings the workspace back. An existing folder for the issue is
  reported and the user chooses to continue there or skip; it is never duplicated or removed.
- Scratch branches are `jdi-herd-scratch-<herd-id>-<N>`. Prep leaves the scratch branch behind, so
  PR #5's `jdi-herd-scratch-<N>` collides on the next herd in the same repo (observed on this
  machine). The scratch branch still omits the issue ID, so prep creates its **T6** branch.
- The herd report lists each worktree path and scratch branch.
- Cleanup guard: a herd worktree usually holds an uncommitted plan, because prep commits only when
  asked. Before removing a worktree, `/jdi:herd` checks the plan folder with `git status
  --porcelain`, names any uncommitted files, offers the `docs: Add <slug> plan` commit, and never
  forces the removal without an explicit yes.

Tasks 08 and 10 carry the exact text and tests.

### Defaults taken (no open questions)

These are the defaults I took, and the user can override any of them:

- The key is `delegation.transport` with the values `native | auto | herdr` and the default `native`. One key covers both enabling and policy.
- `auto` stays silent when `HERDR_ENV` is unset, and announces once when Herdr is present but broken. `herdr` announces every failed check.
- The Herdr path applies to every role configured on another CLI, Executor waves included (revised 2026-09-24). The Researcher is the single-role case the UAT proves in depth, and a wave of OpenCode Executors is the wave case. No role file changes.
- The wave pane cap is 4, mirroring the subagent-cap rule; the multi-worker wait uses a 30000 ms per-agent timeout.
- No runs-path override key and no deadline key. The overall deadline is 45 minutes, a value the user states in conversation wins, and the per-call timeout is 300000 ms.
- `--absolute-git-dir` replaces the decided `--git-dir`, because the worker needs an absolute path and the directory it resolves to is the same.
- Content questions arrive through `result.json` `needs_input`, not a Herdr `blocked` state. This follows from `agent prompt` rejecting blocked agents.
- The UAT runs in a local scratch clone with `tracker.name: none`, so it writes nothing to GitHub. Pointing at a real issue is the user's choice.
- The dogfood `.jdi/config.yml` is unchanged. Live runs use `/tmp/jdi-uat/.jdi/config.local.yml`.
- `skills/run/SKILL.md:90-92`, `agents/*.md` other than `feedbacker.md`, adapter frontmatter, and `bin/sync-opencode.sh` are considered and left unchanged, except for the `herd` allowlist entry in Wave 3.

## Testing Strategy

The baseline is `python3 -m unittest discover -s tests -v` from the repository root: 60 tests, OK at `94912b3`. `tdd.enabled: true`, so each task writes its tests first, sees them fail, and then implements.

All new tests follow the suite's existing style:
- stdlib `unittest`;
- text read through `jdi_files.read`, `section`, `paragraph_starting_with`, `schema_block`, `key_paths` and `defaults_table_keys`;
- whitespace normalized with `" ".join(text.split())`, the idiom already used in `tests/test_codex_plugin.py:42-46` and `:174-181`.

Every test below fails before its step and passes after it.

### Automated tests, by step

**Step 1: `tests/test_herdr_operations.py`, class `HerdrOperationsTest`.** Its `setUp` reads `reference/herdr.md`, so every test fails before the file exists. It asserts:
- The exact headings exist: `# Herdr operations`, `## The universal rules`, `## Scope`, `## H1 - Detect Herdr` through `## H8 - Close the pane and record the outcome`, `## When a step fails`, `## Why the agent surface, not pane run`, `## Waves`; `assertNotIn` `## Extending to waves`, "One active delegated role per Butler" and "Single-instance roles".
- `## The universal rules` contains "A Butler runs one phase at a time" and "only a wave runs several workers at once"; `## Scope` contains "never runs under Herdr".
- In H1's section: `HERDR_ENV`, `HERDR_BIN_PATH`, `herdr status`, `compatible: yes`, "never from the harness name", "Detect, never repair".
- H2: "lists the kinds Herdr supports", `command -v <kind>`, `herdr integration status`; `assertNotIn` `herdr agent get "$HERDR_PANE_ID"`.
- H3: `git rev-parse --absolute-git-dir`, `jdi/runs/<run-id>/`, the five filenames, and each manifest key as a quoted JSON key (`"run_id"`, `"role"`, `"plan"`, `"ticket"`, `"base_commit"`, `"head_commit"`, `"cwd"`, `"workspace_id"`, `"pane_id"`, `"agent_name"`, `"expected"`, `"allowed_writes"`), plus `"needs_input"`.
- H4: `herdr pane split --current`, `--env`, `--no-focus`, `herdr agent start`, "printed back before the spawn", `agent_not_ready`.
- H5: `herdr agent prompt`, `--wait --timeout`, `herdr agent wait`. Table rows whose lines start with `` | `working` ``, `` | `blocked` ``, `` | `idle` ``, `` | `done` ``, `` | `unknown` ``, `` | `timeout` ``, `` | `agent_blocked` ``, `` | `agent_prompt_stalled` ``, `` | `idle` or `done` with no `result.json` ``, and "which pane".
- `## Waves`: "at most 4", "one pane per task", `herdr tab create`, `jdi-wave-<first run id>`, "is not cancelled", "the union of the wave's `## Files` lists", "cannot be attributed to one task".
- H6: "Never `send-keys` into".
- H7: "`idle` or `done` is not proof of success", "`JDI-RESULT-UNWRITABLE`".
- H8: `herdr pane close`, "every exit". This takes over the `"herdr pane close"` pin removed from `tests/test_codex_plugin.py`.
- "`agent read` is for inspection only", "never counts as success", "never resubmit".

The README and AGENTS rows are proven by the existing `ReferenceFileEnumerationTest` (`tests/test_enumerations.py:48-85`). That test fails the moment the file exists without them, which makes it the red half for those two edits.

**Step 2: `tests/test_config_schema.py`, new class `DelegationBlockTest`.**
- `delegation.transport` is in `key_paths(schema_block())`.
- A schema line matches `^  transport: native$`.
- A schema comment line contains `native | auto | herdr`.
- An example line matches `^  transport: (auto|herdr)$`, which proves the value is non-default.
- The defaults table has a row starting `` | `delegation.transport` | `native` ``.

The existing `ConfigSchemaTest` (`:26-101`) then guards schema, example and defaults agreement in both directions with no change.

**Step 3: `tests/test_delegation_transport.py` (new).**

Class `TransportSelectionTest`, over normalized `reference/delegation.md`:
- Present: `## Choosing the transport`, `` `delegation.transport` ``, `` `reference/herdr.md` ``, "A role on this session's own CLI never runs under Herdr", "rung 2 runs the other CLI as its interactive agent in a Herdr pane", "one pane per task", "A Butler runs one phase at a time.", "Herdr's `kinds:` line lists the kinds it supports".
- The three rung openings still appear in order (`**1. The harness has first-class subagents**`, `**2. A second non-interactive session**`, `**3. Neither.**`).
- `assertNotIn` for "**0. A separate agent", "asked to watch the run", "Herdr does not report the kind installed", "Not `herdr agent start`", and "herdr pane run".

Class `HerdrConfinementTest`:
- For every `*.md` in `commands/`, `agents/`, `roles/` and `reference/` except `reference/herdr.md`, plus `skills/run/SKILL.md`, no line matches `\bherdr (agent|pane|workspace|worktree|tab|status|integration|server|session|notification|terminal)\b`, `HERDR_`, or `AskUserQuestion`.
- It is red before Step 3, because `reference/delegation.md:137-141` holds `herdr pane split` and `herdr agent read`.
- It stays green through Step 4, and Step 8 confirms `commands/herd.md` is clean.

Class `FeedbackerIndependenceTest`:
- `agents/feedbacker.md` contains "same model and harness".
- `reference/delegation.md` contains "same model and harness".
- `commands/feedback.md` contains "a different model or a different harness". This last assertion is added in Step 4's task, which is the step that edits `feedback.md`. The Splitter must place it there, not in Step 3.

Class `ButlerSequentialTest`: `roles/butler.md` contains "one phase at a time" and "a delegation transport".

The rewritten assertions in `tests/test_codex_plugin.py` are `:213-218` and `:220-231`, as detailed in Step 3. They stay green with the rewritten text. Their removed fragments would have gone red, because Step 3 deletes that text.

**Step 4: `tests/test_step_zero_transport.py` (new).**
- `StepZeroTransportTest`: for each of `prep`, `research`, `plan`, `split`, `feedback`, `pr`, `execute`, `next` and `yolo` (nine files), the normalized file contains "**Then resolve the delegation transport, once**", "perform **H1** from JDI's `reference/herdr.md`", and "With `delegation.transport` `native` or absent, say nothing at all".
- `prep.md` contains "`models`, `harnesses`, and `delegation` from it".
- `research.md` contains "`models`, `harnesses`, and `delegation` from that config".
- `WaveTransportTest`: `execute.md`, `next.md` and `yolo.md` each contain "including the transport `delegation.transport` selects", and none contains "does not apply to a wave" or "Herdr".
- `ValidationGateTest`: `prep.md` and `research.md` each contain "the result file the transport validated".
- The `FeedbackerIndependenceTest` assertion for `commands/feedback.md`, as noted above.

**Step 5: `tests/test_transport_docs.py` (new), class `TransportDocumentationTest`.**
- The `commands/init.md` frontmatter description contains "how delegated roles reach their own process".
- `commands/init.md` contains "`delegation.transport`" and "perform **H1**".
- `commands/help.md` has the heading `### Separate agent processes`, and its first paragraph (`paragraph_starting_with(text, "Explain the Just Do It")`) contains "delegation transport".
- `README.md` has the heading `### Separate agent processes under Herdr`, and that section contains "`delegation.transport`".
- The existing `ReadmeCodexDocumentationTest.test_scope_snapshot_and_capability_delegation_are_accurate` (`tests/test_codex_plugin.py:314-324`) must stay green. It proves the Roles section edit kept its three phrases.

What no test can observe in Step 5: the renumbering of init steps 11-14 and the `:24` back-reference. The proof is `grep -n "step [0-9]" commands/init.md`, run by the Executor and pasted into its report, plus reviewer reading. The quality of the question wording is reviewer-verified only.

**Step 6: `tests/test_delegation_transport.py`, new class `ArchitectureDocTest`.**
- `docs/delegation-transport-architecture.md` exists with the headings `## Two layers`, `## Result contract`, `## Waves and other roles`, `## Live validation matrix` and `## Relationship to PR #5`, and not `## Extending to other roles and waves`.
- It contains "only when the harness differs" and "same-harness control".
- It contains "`reference/herdr.md`", "validate, never repair" and "detect, never repair".
- `section(docs/harness-adapter-architecture.md, "## Capability-Based Delegation")` contains "`delegation.transport`".
- `docs/config-key-lifecycle.md` contains "`commands/prep.md:28-29`" and does not contain "are all `1.0.6`".
- The existing `ReleaseDocumentationTest` (`tests/test_versions.py:58-97`) must stay green.

What no test can observe in Step 6: the correctness of the re-derived `reference/config.md` line ranges. The proof is the Executor opening each cited range and quoting its first line in the report.

**Step 7: `tests/test_config_schema.py`, new class `HerdBlockTest`.**
- `herd.kind`, `herd.max_parallel` and `herd.seed` are schema keys.
- `herd.args` and `herd.env` are **not** schema keys.
- The defaults table covers `herd`.

The existing `ConfigSchemaTest` proves the example agrees.

**Step 8: `tests/test_herd.py` (new), class `HerdCommandTest`.**
- `commands/herd.md` contains "perform **H1**", "**H2**", "**H4b**", "**H9**", "`reference/herdr.md`", "Validate, never repair", "never fall back to a sequential `/jdi:prep`", "`jdi-herd-<issue", "`.jdi/config.local.yml`", "one name per issue", "Worktree" and "uncommitted plan files", and not "herd record" or "--resume"; H9 contains `herdr tab rename`, `git -C <worktree> status --porcelain`, `--path`, `<worktrees dir>/<repo>/jdi-herd-<issue>`, `jdi-herd-scratch-<herd-id>-<N>` and `herdr worktree open`.
- It does not contain "herd.args", "herd.env" or "AskUserQuestion".
- `reference/herdr.md` has `## H9 - Give a Butler its own worktree`, `herdr worktree create`, and the three invocation rows exactly as in Step 8.

The existing tests that go red the moment `commands/herd.md` is added, and are fixed in the same task:
- `DispatcherContractTest.test_allowlist_matches_commands_in_both_directions` (`tests/test_codex_plugin.py:88-103`);
- `CommandTableTest` (`tests/test_enumerations.py:114-136`);
- `ReadmeCountTest.test_the_readme_command_count_matches_the_commands_directory` (`:159-166`);
- `ConfigLoadStepTest` (`:224-243`), whose count changes from 12 to 13 in this task;
- `OpenCodeGlobalSyncTest` and `OpenCodeProjectSyncTest`, which are glob-driven and stay green with 17 commands.

`HerdrConfinementTest` confirms the herd body is clean.

**Step 9.** The existing `VersionTest` (`tests/test_versions.py:17-40`) is the gate. It goes red if the manifests and the CHANGELOG disagree. The CHANGELOG wording is reviewer-verified only.

**Checks run before every commit (not tests):**
- `grep -rn "delegation.transport" .`, reading every hit (`docs/config-key-lifecycle.md:136-139`).
- `grep -rni "\btiers\?\b" commands agents reference roles docs README.md AGENTS.md`, which must be empty (`TierVocabularyTest`).
- `grep -rn " - " reference/herdr.md docs/delegation-transport-architecture.md`, which must be empty, since new files carry no em dash.

### Live Herdr validation procedure (UAT, Step 10)

Every step can be reproduced from this text. Record each command and its raw output verbatim in the UAT task file, not just pass or fail. Shell snippets are bash. A fish user runs `bash` first.

**U0. Setup.**
1. Work in a Herdr pane: `printenv HERDR_ENV` prints `1`, and `herdr status` shows `status: running` and `compatible: yes`. Record `herdr --version` (expect 0.8.2), `claude --version` (2.1.282 when this plan was written), `opencode --version` (1.18.10), and `command -v codex`.
2. Create the scratch clone: `git clone /Users/supherman/claude_plugins/just_do_it /tmp/jdi-uat && cd /tmp/jdi-uat && git checkout herdr-role-delegation`. The clone's origin is local, so fetches work offline and nothing reaches GitHub.
3. Write `/tmp/jdi-uat/.jdi/config.local.yml`, which is gitignored by the committed `.gitignore`. Each scenario below shows its version. Every version starts with:
   ```yaml
   tracker:
     name: none
   ```
4. Load the branch's plugin in the Butler. The installed `jdi@just-do-it` is 1.0.8 (`claude plugin list`). Run `claude plugin disable jdi@just-do-it`, then start the Butler in a Herdr pane at `/tmp/jdi-uat` with `claude --plugin-dir /Users/supherman/claude_plugins/just_do_it`. Accept the folder trust dialog for the Butler yourself. Confirm `/jdi:help` prints `### Separate agent processes`. If `--plugin-dir` does not expose `/jdi:*`, use the fallback: `claude plugin uninstall jdi@just-do-it && claude plugin install jdi@just-do-it` from a marketplace that points at this checkout. Record which path you took.
5. Choose an opencode model: `opencode models | head`, then pick one `provider/model` you can use. Refer to it below as `<OC_MODEL>`.

**U1. Pre-flight probes.** Run these in a second Herdr pane in `/tmp/jdi-uat`, by hand. `G=$(git rev-parse --absolute-git-dir); mkdir -p "$G/jdi/runs/probe"`. After each probe, close the pane it created.

- **P0: start right after a split.**
  `P=$(herdr pane split --current --direction down --cwd "$PWD" --env JDI_PROBE=from-split --no-focus | jq -r .result.pane.pane_id); herdr agent start jdi-probe-o --kind opencode --pane "$P" --timeout 120000 -- -m <OC_MODEL>; echo "exit=$?"`
  Expect `agent_started`. If it fails because the shell is not ready, H4 needs a readiness wait before the start. That is a UAT failure against H4.
- **P2 and P3 for opencode: environment inheritance and writing into `.git`.**
  `herdr agent prompt jdi-probe-o "Run the shell command: printenv JDI_PROBE > $G/jdi/runs/probe/env-opencode.txt . Then reply OK." --wait --timeout 120000; echo "exit=$?"; cat "$G/jdi/runs/probe/env-opencode.txt"`
  Expect `from-split` in the file. If the file is missing, record whether the worker was blocked on a permission, which is the P3 answer for opencode.
- **P1a: timeout.**
  `herdr agent prompt jdi-probe-o "Count from 1 to 300, one number per line, slowly." --wait --timeout 3000 >p1a.out 2>p1a.err; echo "exit=$?"; cat p1a.out p1a.err`
  Record the `timeout` code, which stream it arrived on, and the exit status.
- **P4: closing the pane stops the worker.**
  `pgrep -f opencode | wc -l; herdr pane close "$P"; sleep 2; pgrep -f opencode | wc -l; herdr agent list`
  Expect the count to drop by the worker's processes and `jdi-probe-o` to be absent. If the worker survives, H8 must add an explicit quit before `pane close`. That is a UAT failure against H8.
- **P1b and P3 for claude: `agent_blocked`.**
  Split a new pane with `--cwd /tmp/jdi-uat`. Run `herdr agent start jdi-probe-c --kind claude --pane "$P" --timeout 120000 -- --model sonnet`, then `herdr agent prompt jdi-probe-c "Run the shell command: touch /tmp/jdi-probe-blocked" --wait --timeout 60000`.
  Expect `blocked` from a Bash permission dialog in default permission mode. Then `herdr agent prompt jdi-probe-c "hello" --wait --timeout 10000 >p1b.out 2>p1b.err; echo "exit=$?"` and record the `agent_blocked` JSON, stream and exit status.
  Answer the dialog yourself in the pane. Then ask the worker to write `$G/jdi/runs/probe/claude.txt` and record whether it blocks on a write permission for a path under `.git`.
- **P1c: `agent_prompt_stalled`.**
  `herdr agent prompt jdi-probe-c " " --wait --timeout 20000 >p1c.out 2>p1c.err; echo "exit=$?"`
  If no `agent_prompt_stalled` appears, record "not induced". The mechanism then rests on the `--help` contract only.
- **P5: trust dialog at start.**
  `mkdir -p /tmp/jdi-trust && git -C /tmp/jdi-trust init -q`. Split with `--cwd /tmp/jdi-trust`, then run `herdr agent start jdi-probe-t --kind claude --pane "$P" --timeout 60000; echo "exit=$?"; herdr agent get jdi-probe-t; herdr agent read jdi-probe-t --source recent-unwrapped --lines 40`.
  Expect `agent_not_ready` with a trust dialog. Record it and do not answer it.
- **P6: JSON shapes.**
  Record `herdr agent get <name>` output for an idle, a working and a blocked agent, and the stdout of a successful `agent prompt --wait`. Confirm which field reports the state, and that H5's wording ("read the state from the JSON") matches.
- **P3 for linked worktrees.**
  `git worktree add /tmp/jdi-uat-wt -b uat-wt`. In `/tmp/jdi-uat-wt`, `git rev-parse --absolute-git-dir` prints `/tmp/jdi-uat/.git/worktrees/jdi-uat-wt`, which is outside the worktree. Repeat the opencode and claude write probes against it and record the answers.
- **P7.** `herdr integration status`. Record the claude and opencode rows.

**Probe gate.** If any probe contradicts `reference/herdr.md`, stop the UAT. Fix H4, H5, H6 or H8 in a commit, record it, and re-run the affected probes. Do not continue on a contradicted mechanism.

**U2. Scenarios.** In the Butler, after each scenario, check `herdr agent list`, which must show no `jdi-*` agent, and `herdr pane list --workspace "$HERDR_WORKSPACE_ID"`, which must show no leftover JDI pane.

- **A. Worker A, opencode, full prep (AC 1, 2, 4, 5, 6).**
  Local config: `delegation: {transport: auto}` written as a block, plus `models.researcher: {model: <OC_MODEL>, harness: opencode}`. Run `/jdi:prep "Add a --dry-run flag to bin/sync-opencode.sh"` and answer "not tracked".
  Expect:
  - no step-0 transport announcement, because auto was detected;
  - a pre-spawn line with agent `jdi-researcher-xxxx`, kind `opencode`, model `<OC_MODEL>`, "no arguments", and the run directory;
  - a new pane without focus, and `herdr agent list` showing kind opencode;
  - the Butler waiting, not doing other work;
  - `$(git rev-parse --absolute-git-dir)/jdi/runs/<id>/` containing `manifest.json` (every field listed in the Implementation Plan) and `prompt.md` (the role body without frontmatter, and the Appendix A contract);
  - then `report.md`, `result.json` with `complete`, and `outcome.json` with `final: valid` and `pane_closed: true`;
  - the Butler saying it validated the result, then spot-checking citations, then updating `## References`;
  - the pane closed.

  The Planner and Splitter have no `harness` set, so they run as native subagents exactly as today: expect no pane, no run directory and no transport text for them.
- **B. Same-harness control (AC 6, AC 8).**
  `delegation: {transport: auto}` and `models.researcher: {model: sonnet, harness: claude}`, with the Claude Butler. Run `/jdi:reresearch`. Expect a native `jdi:researcher` subagent on `sonnet`: no pane, no run directory, no Herdr pre-spawn line, no transport announcement, and no `jdi-*` agent in `herdr agent list`.
- **C. Worker C, codex. Requires installing Codex first; record the install command and version.**
  1. `models.researcher: {model: <codex model>, harness: codex}` and `harnesses.codex.args: ["--sandbox", "workspace-write"]`. Run `/jdi:research`. Expect the worker to fail to write under `.git` (openai/codex#15505, #14338), so no valid `result.json` appears. The Butler then announces an H7 failure with `JDI-RESULT-UNWRITABLE` or "result.json missing", closes the pane, and falls to rung 2 (`codex exec -m … -o <file>`). The phase completes.
  2. Add a writable root for the run directory to `harnesses.codex.args` in `config.local.yml`. The candidate is `--add-dir <abs gitdir>/jdi/runs`, but the flag is unverified on this machine: confirm it with `codex --help` first. Re-run and expect a valid result.

  Record both runs.
- **D. Blocked on an approval (AC 3).**
  Scenario A's config, with OpenCode set to ask before shell commands: `/tmp/jdi-uat/opencode.json` containing `{"permission": {"bash": "ask"}}`, excluded through `/tmp/jdi-uat/.git/info/exclude`. Confirm that project `opencode.json` permissions apply in the interactive TUI and record what you checked. Run `/jdi:research`. When the worker hits a permission prompt, expect:
  - the Butler reports `blocked`;
  - it shows `agent get`, `agent explain` and `agent read` output;
  - it asks you what to do and does **not** answer;
  - it offers to focus the pane.

  Approve in the pane yourself and expect the Butler to resume waiting and then validate. Search the Butler transcript for `send-keys`: there must be none.
- **E. Content question (AC 3).**
  Scenario A's config. Run `/jdi:research` with the plan's task description amended to end "Before finishing, ask the Butler which docs folder to treat as authoritative." Expect:
  - `result.json` with `needs_input`;
  - the Butler moving it to `result.needs_input.1.json`;
  - an answer from `docs.path` it already holds, saying so, sent through the prompt;
  - a later valid result.

  This is best-effort, because the worker may not ask. Record whether it was induced.
- **E2. Question asked in chat, no result file (AC 2, AC 3).**
  Scenario A's config, task description amended to end "Before writing any file, ask the user in the chat which docs folder is authoritative, and wait for the reply." When the worker goes `idle` or `done` with no `result.json`, expect the Butler to read the pane, name it (agent name and pane ID), say you can answer there, and keep waiting with no resubmit. Answer in the pane; expect a valid result. Repeat with "Stop without writing any file."; expect an H7 validation failure, the pane closed, and a re-run through `opencode run`. Best-effort; record whether each case was induced.
- **F. Timeout (AC 3, 4).**
  Tell the Butler: "For this run, use a per-call wait timeout of 20000 ms and an overall deadline of 60000 ms." Run `/jdi:research` with the opencode worker. At the deadline, expect:
  - inspection output, with no success claim and no resubmit;
  - the question keep waiting / accept a checked file / abandon.

  Choose abandon. Expect `outcome.json` `final: abandoned`, the pane closed, and one announcement, then the Researcher running through `opencode run` (rung 2). Repeat F three times and confirm no leaked pane.
- **G. Fallbacks (AC 6).**
  - (1) `transport: herdr` in a terminal outside Herdr (for example Terminal.app, `claude --plugin-dir …` at `/tmp/jdi-uat`): exactly one step-0 announcement stating `HERDR_ENV`, then native delegation, and the phase runs.
  - (2) `transport: auto` outside Herdr: complete silence about the transport.
  - (3) `transport: native` inside Herdr: no pane, a native subagent for a role with no harness, `opencode run` for a role on opencode, and no transport text.
  - (4) Misconfigured value: `models.researcher.harness: qwen` (a kind Herdr supports; `qwen` is not installed here). Expect one announcement ("supports but not installed"), then rung 3, then the floor.
  - (5) Invalid value: `transport: sometimes` gives one announcement, then native.
  - (6) Cannot launch: `harnesses.opencode.env: {PATH: /nonexistent}` makes H4 fail. Expect the pane closed and an announcement. The exec fallback then also fails and the role reaches the floor. The phase runs, with one announcement per failure.
  - (7) Server unreachable: start the Butler with `HERDR_SOCKET_PATH=/tmp/jdi-no-such.sock` under `transport: herdr`. Expect the H1 check (c) announcement. If Herdr ignores the variable, record "not induced".
- **H. Backward compatibility (AC 8).**
  Remove `delegation` from the local config and run `/jdi:research` and `/jdi:plan`. Expect no pane, no transport text, and delegation identical to a 1.0.9 run. For a reference, re-enable the installed plugin and compare against one run of the same command.
- **I. A wave of Executors on another CLI (AC 2, AC 3, AC 6).**
  `delegation: {transport: auto}`, `models.executor: {model: <OC_MODEL>, harness: opencode}`, Scenario D's `opencode.json`, and a plan whose first wave has at least two tasks with disjoint `## Files` (Scenario A's, or a hand-written two-task plan, one task needing a shell command). Run `/jdi:execute`. Expect one `jdi-wave-<first run id>` tab with one pane per task started together, one run directory per task with that task's `## Files` in `allowed_writes`, the Butler waiting on both, one worker `blocked` on the permission prompt that the Butler names while the other keeps running, you approving in the pane, both results validated, the combined file check passing, one commit per task by path, and every pane and the tab closed. Cap check, best-effort: a five-task wave opens at most 4 panes at once.
- **J. Feedbacker independence.**
  With the Researcher from Scenario A (opencode), run `/jdi:feedback the research` with `models.feedbacker: {model: sonnet, harness: claude}` (a native subagent). Expect the Butler to state that producer and reviewer differ. Then set the Feedbacker to `{model: <OC_MODEL>, harness: opencode}` and expect "same model and harness" to be stated.
- **K. `/jdi:herd`, only if Wave 3 shipped (AC 9).**
  Set `herd: {kind: claude, max_parallel: 2}` and `harnesses.claude.args: ["--plugin-dir", "/Users/supherman/claude_plugins/just_do_it"]`. Run `/jdi:herd UAT-1 UAT-2`. Expect:
  - two worktrees and two agents named `jdi-herd-uat-1` and `jdi-herd-uat-2`, with matching tab labels and worktree folders named `jdi-herd-uat-1` and `jdi-herd-uat-2`; a closed workspace is found again by its folder name; a fresh session in a worktree continues its plan; cleanup refuses to drop an uncommitted plan (full checks in `10-uat.md`, Scenario K);
  - `/jdi:prep UAT-1` sent with no wait, and a report table;
  - each spawned Butler running its own prep in its own worktree, where its Researcher can itself go to Herdr.

  Outside Herdr, `/jdi:herd` stops with the H1 reason and never runs a sequential prep.
- **L. Provider neutrality (AC 10).** `python3 -m unittest discover -s tests -v` passes, and `HerdrConfinementTest` is in the run.

**U3. Cleanup.**
- `herdr pane close` any probe pane that is still open.
- Remove the herd worktrees with the commands H9 printed.
- `git worktree remove /tmp/jdi-uat-wt`.
- `rm -rf /tmp/jdi-uat /tmp/jdi-trust /tmp/jdi-probe-blocked`.
- `claude plugin enable jdi@just-do-it`.

**Acceptance-criteria mapping.**

| AC | Proven by |
|---|---|
| 1. Researcher delegated to a separate Herdr agent under `/jdi:prep` | Scenario A |
| 2. The Butler waits and resumes on settled or blocked | Scenarios A, D, E2 and I (a wave) |
| 3. A blocked worker is inspected and handled deliberately | Scenarios D, E, E2 (idle without a result file) and F, plus I (blocked inside a wave) |
| 4. Completion requires a valid artifact | Scenarios A, C1 and F, plus `HerdrOperationsTest` (H7) |
| 5. Validation happens before `PLAN.md` changes | Scenario A, plus `ValidationGateTest` |
| 6. A different harness and model for the worker | Scenarios A and C (and I for a wave); B is the same-harness control that must stay a native subagent |
| 7. Unavailable, disabled, misconfigured or unlaunchable Herdr is announced and falls back | Scenario G (1)-(7), plus `TransportSelectionTest` |
| 8. No new keys means today's behavior | Scenario H, plus `DelegationBlockTest` (default `native`) |
| 9. `/jdi:herd` stays ticket-level fan-out | Scenario K, plus `HerdCommandTest` |
| 10. Bodies stay provider-neutral | `HerdrConfinementTest` |
| 11. Every lifecycle-required site is updated | the Step 2, 5, 7, 8 and 9 tests, plus the `grep` checks |
| 12. The suite passes | Scenario L |
| 13. A live procedure exists | this section |

## Risks

1. **A worker may be unable to write under `.git`.** Claude or opencode may raise a permission dialog for a path under `.git`. In a linked worktree the git dir is outside the worktree entirely. Codex's `workspace-write` keeps `.git` read-only. Mitigation: H7 makes a missing result a validation failure, announced with its reason, never a silent success. Blocked dialogs go to the user. Probes P3 measure all cases before any scenario runs. No runs-path override key is added in this release. If P3 shows claude or opencode cannot write there without a dialog on every run, that is a design finding for the user before merge, not something the Executor works around.
2. **An unverified Herdr response shape.** The exit codes and JSON for `timeout`, `agent_blocked` and `agent_prompt_stalled`, and which field in `agent get` holds the state, were not observed. The plan did not run non-`--help` commands. Mitigation: H5 classifies from the JSON on both streams and never from the exit code alone. Probes P1 and P6 run before the scenarios, and the probe gate stops the UAT on a contradiction.
3. **Closing the pane may not stop the worker** (P4). If a worker survives `pane close`, every run leaks a process that may still write files. Mitigation: P4 is a gate, and the contingency is an explicit quit in H8 before the close.
4. **Claude's lifecycle detection is coarse.** Herdr reports the Claude hook integration as outdated and falls back to screen rules, so `unknown` may be frequent for claude workers. Mitigation: `unknown` never counts as success, the wait loop continues under the deadline, and the deadline question lets the user accept a result they have checked. H2 states the integration gap once.
5. **Unverified Codex model flag and writable root.** Codex's interactive `-m` and the `--add-dir` writable root are unverified because `codex` is not installed here. Mitigation: Scenario C is marked as requiring an install, and the plan tells the Executor to confirm the flags with `codex --help` first. A wrong flag fails H4 and falls back with an announcement.
6. **`harnesses.<kind>.args` is shared by the exec and Herdr paths.** A flag valid only for `claude -p`, or only for the TUI, breaks the other path. Mitigation: `reference/config.md` and H4 state that the arguments reach both paths, and that the user should write flags valid in both. The pre-spawn line prints them.
7. **No model configured on another CLI.** A role with a `harness` but no `models.<role>.model` runs on that CLI's own default. This is today's rung-2 behavior too; only roles on another CLI are affected. Mitigation: H2 says so in the pre-spawn line.
8. **Startup cost of interactive panes.** Under `auto`, a role on another CLI starts a full interactive session instead of a one-shot command. Only roles the user already put on another CLI are affected. Mitigation: the default stays `native`, the docs recommend `config.local.yml` for `auto`, and a transport-level failure switches the rest of the run to native once.
9. **Shell-call timeouts.** Claude Code's Bash tool caps a call at 600000 ms, and other harnesses may cap lower. A `herdr agent wait` without `--timeout` is indefinite. Mitigation: `--timeout` is mandatory, 300000 ms per call, with the shell tool's own timeout set above it and a lower-cap rule. The overall deadline is separate.
10. **The Butler's own sandbox.** A Codex Butler under `workspace-write` cannot create `.git/jdi/runs/`, and a sandboxed shell may block Herdr's Unix socket. Mitigation: both show up as observed failures (H3 as a transport failure, H1 check (c)) and are announced, followed by a native run.
11. **Behavior change on the rung-4 path under `native`.** A user whose role runs on a kind with no exec mode (for example `gemini`) now gets `agent start` instead of `pane run`. Mitigation: this is the only change for a user with no new keys, the CHANGELOG states it, and the phase still runs.
12. **Hand-maintained drift.** New prose could reintroduce "tier" (`TierVocabularyTest`) or an em dash, or split a sentence that a test pins. Mitigation: the `grep` checks in the Testing Strategy, plus the whitespace-normalized assertions.
14. **Many interactive panes in a wide wave.** A large wave on another CLI opens many sessions and panes. Mitigation: the cap of 4 open panes, one wave tab, and every pane and the tab closed on every exit.
15. **Multi-worker wait complexity.** The Butler cycles over several workers with short timeouts, so a slow or `unknown` worker must not starve attention from a blocked one. Mitigation: the H5 table applies per worker on every cycle, blocked panes are named as soon as seen, and the overall deadline covers the whole wave. UAT Scenario I exercises a blocked worker beside a running one.
16. **An answer given in a pane can widen what a worker writes.** The user approving a command in a worker's pane may let it edit outside its task, and in a shared tree only the combined file check catches it, without attributing it to a task. Mitigation: the combined check against the union of the wave's `## Files` runs before any commit, and an out-of-bounds path is reported and blocks committing until the user decides.
13. **Confusion if the herd wave is dropped.** The architecture doc names H9 and `/jdi:herd`. Mitigation: Step 6 describes H9 as the contract `/jdi:herd` must meet. If Wave 3 is dropped, the Step 9 CHANGELOG omits the herd bullet, and PR #5 is rebased onto H1, H2 and H4b instead of closing.

## Tasks

**Wave 1** — run together
- [ ] 01 — Write `reference/herdr.md` and enumerate it (depends on: none)
- [ ] 02 — Add the `delegation` block to the config documents (depends on: none)
- [ ] 03 — Rewrite the transport in `reference/delegation.md`, the Butler and the Feedbacker (depends on: none)

**Wave 2**
- [ ] 05 — User-facing docs: init, help, README (depends on: 01, 02)
- [ ] 06 — Architecture docs (depends on: 01, 02, 03)

**Wave 3** — separable: 07 and 08 are the `/jdi:herd` layer; drop them to rebase PR #5 onto `reference/herdr.md` H1, H2 and H4 instead of superseding it
- [ ] 04 — Command step-0 lines and hand-off sites (depends on: 02, 03, 06)
- [ ] 07 — The herd config block (depends on: 02, 06)
- [ ] 08 — `commands/herd.md`, H9, and the command enumerations (depends on: 01, 05, 06)

**Wave 4**
- [ ] 09 — Release 1.0.10 (depends on: 04, 05, 06, 07, 08)

**Wave 5**
- [ ] 10 — UAT: live Herdr validation (depends on: 09)
