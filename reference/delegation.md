# Delegation and models

JDI is a workflow, not a product of any one agent harness. It runs under Claude Code, Codex,
OpenCode, and anything else that can read markdown and edit files. The workflow prose therefore
never names a tool, a provider, or a model. It names a **role**, and `.jdi/config.yml` says what
that role runs on and where. This file says how to turn those into whatever the current harness
actually offers.

## Roles

JDI has eight roles. Seven are delegatable; one is you.

| Role | Definition |
|---|---|
| **Butler** | `roles/butler.md` — the orchestrator. This is the session you are already in |
| **Researcher** | `agents/researcher.md` |
| **Planner** | `agents/planner.md` |
| **Splitter** | `agents/splitter.md` |
| **Executor** | `agents/executor.md` |
| **Synthesizer** | `agents/synthesizer.md` |
| **PR Writer** | `agents/pr-writer.md` |
| **Feedbacker** | `agents/feedbacker.md` |

The Butler is never spawned. It is the voice of the main session: it asks the questions, presents
the results, and decides when to hand off. Every JDI command is written to the Butler.

## What each role wants from a model

`models` in `.jdi/config.yml` names a model for each of the seven delegatable roles. None of the
descriptions below is a default or a vendor recommendation — they say what the phase is asking for,
so you can decide what your account actually has that fits.

| Role | For | Wants |
|---|---|---|
| **Researcher** | finding the prior art, reading the code that is about to change, drafting architecture docs | the strongest reasoning model available; long context; patience with ambiguity |
| **Planner** | turning context into a numbered plan, weighing trade-offs, sequencing | the strongest reasoning model available; long context; patience with ambiguity |
| **Executor** | implementing one task against the plan and the surrounding code | the strongest reasoning model available; long context; patience with ambiguity |
| **Feedbacker** | adversarial review of another role's output, and of the prompt that produced it | the strongest reasoning model available; long context; patience with ambiguity |
| **Splitter** | breaking an approved plan into atomic, dependency-ordered tasks | a solid, capable model — the work is structured transformation, not discovery |
| **Synthesizer** | condensing a plan folder into one durable record | a solid, capable model — the work is structured transformation, not discovery |
| **PR Writer** | turning the condensed plan and the git history into a PR a reviewer can act on | a solid, capable model — the work is structured transformation, not discovery |

The Butler is absent from the table because it has no key. It is the session you are already in,
running on whatever model you started it with, and its own work — orchestration, status, marking
tasks done, committing — is mechanical work with a clear spec that a cheap, quick model does well.

Leaving the `models` block out, or leaving a role's entry empty, runs that role in this session's
harness on the model the session is already using. That is a supported configuration, not a degraded
one: running all seven roles on one model changes nothing about the workflow's shape.

One rule survives every mapping: **the Feedbacker should not run on the same model and harness as
the agent whose output it is reviewing** where the config offers a choice. A model reviewing its own
output confirms it. If no second model or harness is available, run the review anyway and note that
producer and reviewer were the same model on the same harness, so the user can weigh the verdict
accordingly.

## Choosing the transport

A role on this session's own CLI never runs under Herdr. A role with no `models.<role>.harness`, or
one that names the Butler's own kind, is delegated by rung 1 (or rung 3) of *How to delegate*
exactly as before, and its progress is watchable in the harness itself.

For a role whose `models.<role>.harness` names another CLI (rung 2), `delegation.transport` in
`.jdi/config.yml` decides how that CLI runs:

| `delegation.transport` | What happens |
|---|---|
| `native` (default) | Today's rung 2, unchanged: the CLI's own non-interactive mode. Herdr is reached only through rung 4, for a kind with no exec mode. Nothing is probed at step 0 |
| `auto` | Step 0 performs H1. When it succeeds, rung 2 runs the other CLI as its interactive agent in a Herdr pane, where the user can answer it. Outside Herdr, exactly `native`, and nothing is said; announces once when inside Herdr but a later check fails |
| `herdr` | As `auto`, but announces any failed H1 check once, then delegates as `native` for the run |

Any other value: announce once, and treat it as `native`. H1 and every other Herdr operation are in
`reference/herdr.md`.

A Butler runs one phase at a time. Inside a phase, only a wave runs several workers at once, and the
Butler waits for all of them before doing anything else in the command.

Detect, never repair. The Butler never starts a Herdr server or installs an integration to make a
check pass. A failed check hands the role back to native resolution, and the phase always runs.

## How to delegate

Delegation follows observed runtime capability, not the harness name.

When a command says *"delegate to the **Planner** role"*, do whichever of these the current harness
supports, in this order — unless the configuration selects rung 2:

**1. The harness has first-class subagents** (Claude Code's Agent tool, Codex subagents, OpenCode's
subagent mode). Prefer a matching JDI role already registered by the harness — `jdi:researcher`,
`jdi-researcher`, or similar — because its instructions are already loaded. Spawn it using the
role's model from the config.

When no matching JDI role is registered, spawn a suitable generic subagent and give it the
installed `agents/<role>.md` definition as its instructions, the role's model from the config, and
exactly the inputs the role's *What it receives* section declares — no more. This remains the
preferred path: the role gets a clean context window, and the orchestrator's context is not flooded
by the role's reading.

**2. A second non-interactive session** — another agent CLI, invoked non-interactively, reporting
back through a file. This is a **chosen** path, not merely a fallback for a harness that lacks
subagents: when `models.<role>.harness` names a kind other than the one you are running in, this is
the path the configuration asked for, and it is taken even where rung 1 was available. It is also
still the fallback when this harness has no subagents at all. `## Where a role runs` says how to
drive it. When `delegation.transport` is `auto` or `herdr` and step 0 detected Herdr, rung 2 runs
the other CLI as its interactive agent in a Herdr pane instead of its non-interactive mode
(`reference/herdr.md` H2 to H8). On any Herdr failure: announce once, and run the same role through
the CLI's non-interactive mode; it is never retried on Herdr in the same phase, and the phase is
never skipped.

**3. Neither.** **Adopt the role inline.** Read the role's definition file, announce the switch
("— adopting the Researcher role —"), follow that file as your own operating instructions for the
phase, produce exactly the outputs its *What it returns* section lists, then announce the return
and go back to being the Butler.

Path 3 is a first-class fallback, not a failure. It costs a shared context window and the loss of a
separate model for the phase; it keeps every other property of the workflow. **Do not silently skip
a role because delegation is unavailable** — a phase that never ran is the failure, not the
mechanism it ran through.

## Delegating several roles at once

`/jdi:execute`, `/jdi:next` and `/jdi:yolo` hand a whole **wave** of tasks to the Executor at the
same time — one Executor per task, all in the same working tree (`reference/plan-store.md`,
*Waves*). Each delegation is resolved exactly as a single one would be, by the ladder above and the
rungs below; what changes is only that they overlap:

- **Rung 1, subagents** — spawn every Executor of the wave in **one** turn, so the harness runs
  them concurrently, then wait for all of them. Spawning one, waiting, and spawning the next is
  sequential execution with extra steps. If the harness caps concurrent subagents, fill the cap and
  start the next task as each slot frees.
- **Rung 2, a second non-interactive session** — start one process per task, each reporting through
  **its own** file, and wait for all of them. Under Herdr that is one pane per task, all started
  together in one wave tab, each with its own run directory, at most 4 open at once
  (`reference/herdr.md`, *Waves*); the Butler waits on every worker, sends the user to any pane that
  is blocked or asking, and every pane JDI opened is closed on every exit.
- **Rung 3, inline** — one context window cannot run two roles at once. **Say so once** ("this
  harness has no subagents; running the wave's tasks one after another") and run the wave's tasks
  sequentially, in number order. Everything else about a wave — the file guard, verification after
  the wave, one commit per task by path — still applies.

Each Executor is handed one task and told which sibling tasks are running alongside it and which
paths are theirs. Let the whole wave settle before acting on any one report: a sibling that is
still running is not cancelled because another failed. Roles with a single instance per phase —
every role but the Executor — are never fanned out this way.

## Where a role runs

`models.<role>.harness` names a key in `harnesses:`, and that key is the agent CLI kind the role
runs in. `harnesses.<kind>.args` are handed to that CLI verbatim, after its own flags;
`harnesses.<kind>.env` is set on the process — or, under Herdr, on the pane — that runs it. JDI
composes, merges and translates neither. Under `transport: native`, resolution is exec-first, Herdr
second. Under `auto` or `herdr` with Herdr detected, a role on another CLI runs in a Herdr pane
first, and exec is its fallback.

**Prefer the CLI's own non-interactive mode.** It returns a lossless report, allocates no pane, and
leaves nothing to clean up. The three JDI knows:

- `codex` → `codex exec -m <model> -o <file> "<prompt>"`, then read `<file>`. Verified flags:
  `-m/--model`, `-o/--output-last-message`.
- `opencode` → `opencode run -m <provider/model> --agent jdi-<role> --format json "<prompt>"`.
  Verified flags: `-m/--model`, `--agent`, `--format json`.
- `claude` → `claude -p --model <alias> --output-format json "<prompt>"`. Verified flags:
  `-p/--print`, `--model`, `--output-format text|json|stream-json`.

`harness: claude` is a first-class value, not merely the no-op case of naming the session's own
kind. The reverse direction is the point: a Codex or OpenCode session putting a role back on Claude
spawns `claude -p` exactly as a Claude session spawns `codex exec`.

The model flag is the one flag JDI composes from the config, on every separate-process path, exactly
as above.

**Print the spawn line first.** This rule applies to every separately spawned process: the
non-interactive command and the Herdr agent alike. The line is the first output of the spawn
itself: the same shell command prints it and then spawns, joined by `&&` so that the spawn does not
run if the print did not. The template, as one line:

```text
JDI spawn <run-id or "-">: <Role> on <kind> (<model | CLI default>) - args: <verbatim | none> - env keys: <keys | none> - run dir: <path | none>
```

`<run-id>` and the run dir exist only on a path that creates a run directory, so the
non-interactive command prints `-` and `none`. `args` lists every value from
`harnesses.<kind>.args` verbatim, and `env keys` lists the keys of `harnesses.<kind>.env` and never
their values. `reference/herdr.md` H4 adds the agent name to the line. A wave prints one line per
process.

The command has this form, where `<spawn command>` is one of the three non-interactive commands
above, exactly as written there:

```text
printf '%s\n' "JDI spawn -: <Role> on <kind> (<model | CLI default>) - args: <verbatim | none> - env keys: <keys | none> - run dir: none" && <spawn command>
```

Under Herdr the spawn is the pane split, and `reference/herdr.md` H4 step 1 gives that command in
the same form. The Butler also repeats the line in its visible message to the user in the same
turn. A summary never claims that the spawn line was printed unless the line appears in that
command's output. The line is tied to the spawn command because a live run skipped a rule stated
only as prose and then reported the line as printed. A spawn without this line printed first is a
defect. This is the same rule that *What delegation does not grant* states, that every flag is
printed back before the spawn, now with a fixed shape. A subagent and an inline adoption are not
separately spawned processes, so they print no spawn line.

**Herdr.** Under `native`, Herdr is used only when the kind has no exec mode JDI knows. Under `auto`
or `herdr` it is how rung 2 runs another CLI when Herdr is detected. Every Herdr step (detection,
pane, start, prompt and wait, states, the result contract, waves, pane close) is in
`reference/herdr.md` and nowhere else. It uses Herdr's agent surface and receives the report through
a file, and `reference/herdr.md` gives the reason.

**A pane JDI created is JDI's to close** (H8). Every exit from a Herdr path, whether success,
timeout, or any of the failure rungs below, closes that pane before it announces. A failed
delegation must not leak a pane per attempt.

**Role instructions have to travel.** Name the target's registered role where it has one
(`opencode run --agent jdi-<role>`; the files exist at `~/.config/opencode/agent/jdi-*.md`, produced
by `bin/sync-opencode.sh`). Otherwise **inline the role file** — read the installed
`agents/<role>.md` and pass its text as part of the prompt. Take a plugin-root path **only from an
explicit config value, never derived**: the Codex and Claude snapshots are version-pinned under
different layouts and share no derivation rule, and
`docs/harness-adapter-architecture.md:192-195` forbids searching ancestors for a plausible checkout.
Under Herdr, the role file is copied into the run's `prompt.md` (`reference/herdr.md` H3).

## What delegation does not grant

Delegation never grants additional authority, and JDI never composes any. An in-harness subagent
and an inline adoption run inside this session's own sandbox and approval policy.
**A separately spawned CLI does not** — it is another process that resolves its own sandbox,
approval policy and credentials from its own configuration, which may be broader or narrower than
this session's. JDI composes no authority-affecting flag and translates none between kinds: every
flag a spawned CLI receives is a literal value the user wrote in `harnesses.<kind>.args`, passed
through verbatim and **printed back before the spawn**. Any external mutation must still be
allowed by the active command and the Butler's rules.

A Herdr worker is a separately spawned CLI in this sense. The worker's approval, permission and
trust dialogs belong to the user, and the Butler never answers one. The Butler answers a worker's
content question only from context it already holds, and says so. A worker writes only its run
directory and what the active command lets the role write, and the Butler checks the tree afterward
(H7).

## When the configuration cannot be honoured

Rungs 1–9 settle **where** the role runs. Rungs 10–12 settle **which model** it runs on, inside
wherever 1–9 landed. When a harness rung and a model rung both fire — which is the common case,
because a model chosen for another CLI is usually one this harness cannot express — that is **one
announcement, not two**: name what was configured, what was reachable, and what the role is actually
about to run on.

The first rung that applies wins. Every rung is an observation, never an assumption.

1. **No `harness:` for this role.** Run it in this session's harness. **Silent** — nothing was
   configured and nothing was skipped.
2. **`harness:` names this session's own kind.** Delegate normally, rung 1 of *How to delegate*.
   **Silent** — the configuration was honoured.
3. **The named CLI is not on `PATH`.** Announce and go to the floor. Detection is an observation:
   resolve the binary, do not infer from a failed run.
4. **JDI knows no non-interactive exec mode for that kind.** Try the Herdr transport,
   `reference/herdr.md` H1 to H8 (rungs 6-9).
5. **The role's instructions cannot be resolved for that CLI.** No registered role name, and the
   installed `agents/<role>.md` cannot be read to inline. Announce and go to the floor. **Never
   derive a plugin path** to close this gap.
6. **Herdr is wanted but not detected.** H1 failed at step 0 (or, for rung 4 under `native`, when
   the role was delegated).
7. **The kind is not one Herdr supports, or its CLI is not installed.** Herdr's `kinds:` line lists
   the kinds it supports; installed means `<kind>` resolves on `PATH`. Integration status affects
   only detection quality.
8. **The pane or the agent cannot be started.**
9. **The run started but produced no valid result.** H7 failed, or the state stayed `unknown` or
   timed out and the user chose to abandon. `unknown` does not prove completion.

   For rungs 6 to 9: close the pane JDI opened (H8), announce, and continue as `native` would
   resolve the role: rung 2's non-interactive mode, or the floor where rung 4 sent a kind with no
   exec mode.

10. **The model cannot be expressed in the harness that will run the role.** Claude Code's Agent
    tool takes `model` as an enum (`sonnet | opus | haiku | fable`), so a full identifier like
    `claude-opus-5` cannot be passed at spawn time there; another kind may reject an unprefixed
    name. This is knowable **before** the spawn, from the harness's own schema. Announce and run the
    role on that harness's default model. Never substitute a different identifier, and never
    silently drop it.
11. **The configured model is unreachable** — authentication, quota, or a retired identifier.
    Knowable only after the attempt. Announce and run on the harness's default.
12. **The floor.** Run the role in this session's harness, on its configured model if this session
    can both express and reach it, otherwise on the session's own model — adopting the role inline
    if there are no subagents. **The phase always runs.**

Four directions the ladder never takes:

- **Never skip the phase.** A phase that never ran is the failure; the mechanism it ran through is
  not. The floor is always available.
- **Never acquire a flag the user did not write.** JDI composes only the invocation and the model
  flag, adds no authority-affecting argument of its own, and translates none between kinds. A permission-bypass flag in `harnesses.<kind>.args` is a thing the user typed,
  and it is printed back before the spawn.
- **Never land somewhere less supervised.** Degrading a harness means coming **back into this
  session**, which is the most supervised place available — never onward to a third CLI, and never
  into a broader approval policy in order to make a spawn succeed.
- **Never promote a model.** An unreachable model falls to the session's or the harness's default.
  It is never swapped for a stronger or more expensive one because that one happened to be
  reachable.

One shape predates this schema and must not be guessed at. A `models:` block whose keys are `deep`,
`standard` and `fast` is the pre-1.0.5 shape. It names no role, so **nothing in it is read**. Say so
once, name `reference/config.md` as the current schema, and run every role on the session's own
model for that run.

## Harness-specific metadata

Anything that is genuinely harness-specific *about a file* — a tool allowlist, a slash command's
argument hint — lives in that file's **YAML frontmatter**, never in its prose. Adapters strip or
rewrite frontmatter per harness; the body is shared verbatim. If you find yourself writing a tool
name into the body of a command or a role, it belongs in frontmatter instead.

A model name is not a fact about a file. It is a fact about the user's account and the harness that
will run the role, it has no single right answer across two repositories, and it therefore lives in
`.jdi/config.yml` under `models.<role>.model` — and nowhere else. A role file's frontmatter must not carry
a `model:`.
