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

One rule survives every mapping: **the Feedbacker should not be the same model as the agent whose
output it is reviewing** where the config offers a choice. A model reviewing its own output
confirms it. If no second model is available, run the review anyway and note that producer and
reviewer were the same model, so the user can weigh the verdict accordingly.

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
drive it.

**3. Neither.** **Adopt the role inline.** Read the role's definition file, announce the switch
("— adopting the Researcher role —"), follow that file as your own operating instructions for the
phase, produce exactly the outputs its *What it returns* section lists, then announce the return
and go back to being the Butler.

Path 3 is a first-class fallback, not a failure. It costs a shared context window and the loss of a
separate model for the phase; it keeps every other property of the workflow. **Do not silently skip
a role because delegation is unavailable** — a phase that never ran is the failure, not the
mechanism it ran through.

## Where a role runs

`models.<role>.harness` names a key in `harnesses:`, and that key is the agent CLI kind the role
runs in. `harnesses.<kind>.args` are handed to that CLI verbatim, after its own flags;
`harnesses.<kind>.env` is set on the process — or, under Herdr, on the pane — that runs it. JDI
composes, merges and translates neither. Resolution is **exec-first, Herdr second**.

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

**Use Herdr only** when the kind has no exec mode JDI knows, or when the user has asked to watch the
run. Drive it with `herdr pane split` → `herdr pane run <PANE_ID> <command>` → `herdr pane
wait-output --match <sentinel> --timeout <ms> <PANE_ID>` → read the file the command was told to
write. **Not `herdr agent start`**, which is the primitive for an interactive occupant, and not
`herdr agent read`: that is a terminal scrape in every mode, and it cannot recover rows lost to the
alternate screen. A role's prose report must arrive through a file, never through the pane buffer.

**A pane JDI created is JDI's to close.** Every exit from a Herdr path — success, timeout, or any of
the failure rungs below — runs `herdr pane close <pane_id>` before it announces. A failed delegation
must not leak a pane per attempt.

**Role instructions have to travel.** Name the target's registered role where it has one
(`opencode run --agent jdi-<role>`; the files exist at `~/.config/opencode/agent/jdi-*.md`, produced
by `bin/sync-opencode.sh`). Otherwise **inline the role file** — read the installed
`agents/<role>.md` and pass its text as part of the prompt. Take a plugin-root path **only from an
explicit config value, never derived**: the Codex and Claude snapshots are version-pinned under
different layouts and share no derivation rule, and
`docs/harness-adapter-architecture.md:191-194` forbids searching ancestors for a plausible checkout.

## What delegation does not grant

Delegation never grants additional authority, and JDI never composes any. An in-harness subagent and
an inline adoption run inside this session's own sandbox and approval policy. **A separately spawned
CLI does not** — it is another process that resolves its own sandbox, approval policy and
credentials from its own configuration, which may be broader or narrower than this session's. JDI
composes no authority-affecting flag and translates none between kinds: every flag a spawned CLI
receives is a literal value the user wrote in `harnesses.<kind>.args`, passed through verbatim and
**printed back before the spawn**. Any external mutation must still be allowed by the active command
and the Butler's rules.

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
4. **JDI knows no non-interactive exec mode for that kind.** Try the Herdr transport (rungs 6–8).
   If Herdr is unavailable, announce and go to the floor.
5. **The role's instructions cannot be resolved for that CLI.** No registered role name, and the
   installed `agents/<role>.md` cannot be read to inline. Announce and go to the floor. **Never
   derive a plugin path** to close this gap.
6. **Herdr is wanted but not detected** — no binary, no `HERDR_ENV`, or no server answering on the
   socket. Announce and go to the floor.
7. **Herdr does not report the kind installed.** Announce and go to the floor. Herdr's `kinds:`
   line is the observation; an absent kind is not a reason to try anyway.
8. **The pane cannot be created.** Announce and go to the floor. Nothing to close.
9. **The run started but never reported usably** — the output file was never written, or the status
   stayed `unknown` with nothing readable. Herdr's statuses are exhaustively
   `idle | working | blocked | done | unknown`, and `unknown` does **not** prove completion.
   **Close the pane JDI opened**, announce, go to the floor.
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
- **Never acquire a flag the user did not write.** JDI adds no argument of its own and translates
  none between kinds. A permission-bypass flag in `harnesses.<kind>.args` is a thing the user typed,
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
