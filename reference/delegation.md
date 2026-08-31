# Delegation and model tiers

JDI is a workflow, not a product of any one agent harness. It runs under Claude Code, Codex,
OpenCode, and anything else that can read markdown and edit files. The workflow prose therefore
never names a tool, a provider, or a model. It names a **role** and a **tier**, and this file says
how to turn those into whatever the current harness actually offers.

## Roles

JDI has eight roles. Seven are delegatable; one is you.

| Role | Tier | Definition |
|---|---|---|
| **Butler** | fast | `roles/butler.md` — the orchestrator. This is the session you are already in |
| **Researcher** | deep | `agents/researcher.md` |
| **Planner** | deep | `agents/planner.md` |
| **Splitter** | standard | `agents/splitter.md` |
| **Executor** | deep | `agents/executor.md` |
| **Synthesizer** | standard | `agents/synthesizer.md` |
| **PR Writer** | standard | `agents/pr-writer.md` |
| **Feedbacker** | deep | `agents/feedbacker.md` |

The Butler is never spawned. It is the voice of the main session: it asks the questions, presents
the results, and decides when to hand off. Every JDI command is written to the Butler.

## How to delegate

When a command says *"delegate to the **Planner** role at the **deep** tier"*, do whichever of
these the current harness supports, in this order:

**1. The harness has first-class subagents** (Claude Code's Agent tool, OpenCode's subagent mode).
Spawn one, using the role's definition file as its instructions and the tier's model from the
config. Pass it exactly the inputs the role's *What it receives* section lists — no more. This is
the preferred path: the role gets a clean context window, and the orchestrator's context is not
flooded by the role's reading.

**2. The harness has no subagents, but can run a second session** (a CLI you can invoke
non-interactively). Shell out to it with the role file and the inputs as the prompt, and read back
its report.

**3. Neither.** **Adopt the role inline.** Read the role's definition file, announce the switch
("— adopting the Researcher role —"), follow that file as your own operating instructions for the
phase, produce exactly the outputs its *What it returns* section lists, then announce the return
and go back to being the Butler.

Path 3 is a first-class fallback, not a failure. It costs a shared context window and the loss of
tier separation; it keeps every other property of the workflow. **Do not silently skip a role
because delegation is unavailable** — a phase that never ran is the failure, not the mechanism it
ran through.

## Tiers

A tier is a statement about how much reasoning a phase deserves, not about a vendor.

| Tier | For | Wants |
|---|---|---|
| **deep** | research, planning, implementation, adversarial review | the strongest reasoning model available; long context; patience with ambiguity |
| **standard** | splitting a plan into tasks, condensing it, writing the PR | a solid mid-tier model — the work is structured transformation, not discovery |
| **fast** | orchestration, status updates, marking tasks done, committing | a cheap, quick model — mechanical work with a clear spec |

`models` in `.jdi/config.yml` maps the three tiers to concrete model identifiers. It is the
authority: when it names a model for a tier, spawn that tier's role on that model.

When it does not — an empty tier, no config file, or a mapped model this harness cannot reach —
fall back in this order: the role file's own frontmatter default, if the harness honours one; then
whatever model the session is already running. Say once which fallback you took. A tier mapping is
an optimisation. Running all three tiers on a single model is a valid, supported configuration and
changes nothing about the workflow's shape.

One rule survives every mapping: **the Feedbacker should not be the same model as the agent whose
output it is reviewing** where the config offers a choice. A model reviewing its own output
confirms it. If no second model is available, run the review anyway and note that producer and
reviewer were the same model, so the user can weigh the verdict accordingly.

## Harness-specific metadata

Anything that is genuinely harness-specific — a concrete model name, a tool allowlist, a slash
command's argument hint — lives in a file's **YAML frontmatter**, never in its prose. Adapters
strip or rewrite frontmatter per harness; the body is shared verbatim. If you find yourself writing
a tool name or a model name into the body of a command or a role, it belongs in frontmatter or in
the config instead.
