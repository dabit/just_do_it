---
description: "Explain the Just Do It (JDI) workflow — the commands, the roles, and the typical flow."
---

# JDI: Help

**Role: Butler** — JDI's orchestrator (`roles/butler.md`).

Explain the Just Do It (JDI) workflow to the user. Print the following, then add one closing line
naming what this repository is currently configured for — the tracker, the plan store, what the
split pieces become, whether TDD is on, whether Jev is on, which roles have a model configured
and whether any of them runs in another agent CLI, and whether `.jdi/config.yml` exists at all. If it does not, say
`/jdi:init` writes it, and that JDI works without it by asking as it goes.

---

## Just Do It (JDI)

A structured dev workflow that takes a change from idea to pull request. It works with any issue
tracker or none, stores plans in the repo or in a note service, and runs on any agent harness.

### Commands

| Command | Roles | What it does |
|---|---|---|
| `/jdi:init` | Butler | Set JDI up for this repo — tracker, split pieces, TDD, Jev, plan store, docs folder, models. Writes `.jdi/config.yml`. |
| `/jdi:prep` | Butler + Researcher + Planner + Splitter | Run start, research, plan, and split in one pass. Stops only for real questions, and leaves a task list ready for `/jdi:yolo`. |
| `/jdi:start` | Butler | Kick off a task — describe it, optionally link an issue. Creates the branch and the initial `PLAN.md`. |
| `/jdi:research` | Researcher | Find or create the architecture docs for the area being changed. Searches past plans. Writes the findings back to the issue. Ranks the candidate docs and screens `consumers` with Jev when `jev.enabled` is on. |
| `/jdi:plan` | Butler + Planner | Clarify the ambiguities with you, then write the implementation plan on top of the research. |
| `/jdi:split` | Splitter | Break the plan into atomic, dependency-ordered tasks with verification steps, cut so that as many as possible can run in parallel. Ends with a UAT task. Mirrors them to the tracker if `split.pieces` says so, and checks the split is really atomic with Jev when `jev.enabled` is on. |
| `/jdi:execute` | Butler + Executor | Implement the next wave — every task whose dependencies are done, one Executor each, in parallel. Shows the diff and asks for your feedback. Proves the test suite runs, once per plan, when `tdd.enabled` is on. |
| `/jdi:done` | Butler | Mark what was just executed complete, update the checklist, and commit — one commit per task, even when a wave ran several. |
| `/jdi:next` | Butler + Executor | `/jdi:done` then `/jdi:execute`, in one step. Reads the plan's TDD decision; never re-decides it. |
| `/jdi:yolo` | Butler + Executor | Auto-pilot: done + execute every remaining task, a parallel wave at a time. Stops on the first failure — but the expected red inside a TDD task is required evidence, not a failure, and does not stop it. |
| `/jdi:status` | Butler | Show progress on the current plan. |
| `/jdi:pr` | Butler + Synthesizer + PR Writer | Condense the plan, push, and open the pull request. |
| `/jdi:feedback` | Butler + Feedbacker | Critique the latest output on demand — verdict, fixes, and proposed prompt improvements. Orders the findings with Jev when `jev.enabled` is on. |
| `/jdi:replan` | Butler + Planner | Throw the plan away and write a fresh one. |
| `/jdi:reresearch` | Butler + Researcher | Throw the research away and look again. |

**On the Feedbacker:** it reviews on demand only. It is not a gate on the producing commands —
invoke it deliberately with `/jdi:feedback` when you want an output or a prompt audited. It never
edits a prompt without your sign-off.

### Typical flow

```
/jdi:prep "Add presence indicators to pages"
/jdi:yolo
/jdi:pr
  — or, one phase at a time —
/jdi:start "Add presence indicators to pages"
/jdi:research
/jdi:plan
/jdi:split
/jdi:execute  ←─┐
/jdi:done     ──┘ repeat until every task is done
  — or —
/jdi:next     ←── repeat (done + execute in one step)
  — or —
/jdi:yolo     ←── auto-pilot the remaining tasks
/jdi:pr
```

You can stop after any phase. From `/jdi:start` onward the feature branch exists, so the plan and
the research are committable on their own and the work is resumable later or by someone else.

### Plan structure

```
<plans folder>/<slug>/
  PLAN.md              # metadata, references, implementation plan, testing strategy, risks, tasks
  01-<task-slug>.md    # one task: status, dependencies, why, description, files, verification
  02-<task-slug>.md
  ...
  NN-uat.md            # final task: user acceptance scenarios
```

At PR time the task files collapse back into a single slim `PLAN.md` — the commits are the task
list by then.

### Tasks run in parallel

The Splitter cuts the plan for parallelism: it keeps dependencies to the ones that are real,
extracts what several tasks share into an early task so the rest fan out from it, and makes sure
tasks that can run together never touch the same file. `/jdi:execute`, `/jdi:next` and `/jdi:yolo`
then run a **wave** at a time — every task whose dependencies are done, one Executor each, at once —
verify each task once the wave has settled, and still commit **one task per commit**. A plan that is
honestly a chain — or one split before 1.0.7, with no wave headings — runs one task at a time, as
before; UAT always runs alone, last; and a harness that cannot run roles concurrently says so once
and runs each wave in order.

### What the pieces become

Every task file lands as its own commit — that is `split.pieces: commits`, the default, and it
needs no tracker. Set `split.pieces` to `tasks` or `subtickets` in `.jdi/config.yml` and each piece
is **also** mirrored onto the issue: a checklist item where the tracker has one, or a child issue
(Linear sub-issue, Jira sub-task, GitHub sub-issue). The mirror is additive — the task files and
the one-commit-per-task rhythm are the same either way — and it ticks itself off as tasks are
marked done. A mode the tracker cannot honour falls back to `commits` and says so.

### Test-first execution

Off by default, and **silent** when off: with `tdd.enabled` unset or `false`, no command running a
plan says a word about TDD — not even that it is off — and the workflow is exactly what it was
before the key existed. Set it to `true` and the Executor writes the failing test first, then the
implementation, and reports the red run as the evidence that the order was real — a task is not
complete at red, so both runs come back. Tests and implementation still land in the same commit,
one per task; only the order they are written in changes.

The runner is **proven, not assumed**. Before the first task of a plan, the Butler derives an
invocation and watches it run, scoped to one file or one directory, and records the answer as a
`TDD:` line in `PLAN.md`. Every later command reads that line and none re-decides it, so editing
`.jdi/config.yml` mid-plan changes nothing until the next plan. A runner it cannot prove — no such
command, an unreachable container, a dependency error — degrades that plan to off **out loud**,
naming what it tried and what came back. `tdd.test_instructions` helps it get there: prose an agent
reads and translates ("run `bin/rails test` inside the devcontainer"), never a string JDI executes.

Where a task has no testable behaviour — documentation, prose, configuration — the Executor
announces the skip and implements normally. A test invented to satisfy the mode would be worse than
no test at all: it produces a green suite and a red-run transcript that prove nothing while looking
precisely like proof.

### Typed judgments with Jev

Off by default, and **silent** when off: with `jev.enabled` unset or `false`, no role sends
anything anywhere and no command mentions it — not even to say it is off. Set it to `true` and five
named operations become available (`reference/jev.md`, J1–J5): the Researcher ranks candidate
architecture docs so the constraining ones are read first and screens `consumers` for contract
breakage, the tracker operations resolve an idiosyncratic workflow state name by role, the Splitter
checks a fresh split is really atomic, and the Feedbacker orders its findings by consequence.

Jev is TypeSafe's System One model. It returns a probability or a chosen option rather than prose,
it sees no tools and writes no files, and **it narrows a list a role already has — it never
decides**. It is never the reason a step is skipped, a tracker is written, a commit is made, or a
pull request is opened. Those stay the role's judgment and your approval, exactly as they are with
the key off.

It **degrades to more work, never less**. No key, no network, a failed request, or a state too big
for one request all mean the role reads every candidate itself — which is what it does with the key
off. The Butler runs that ladder once, before it delegates anything, and announces the fallback a
single time rather than at every step. The key is read from `$TYPESAFE_API_KEY` or
`~/.config/typesafe/api_key`; it never belongs in `.jdi/config.yml`, which is a committed file.

### Roles and models

JDI's prose names roles, never models, so it runs anywhere. `.jdi/config.yml` maps each of the seven
delegatable roles — Researcher, Planner, Splitter, Executor, Synthesizer, PR Writer, Feedbacker —
to the model it runs on, and optionally to the agent CLI it runs in, so one role can sit on Codex or
OpenCode while the rest stay here. Leave the `models` block out and everything runs on the session's
own model — that is fully supported, not a degraded mode.

A harness or a model that cannot be honoured is **announced once** and the phase still runs. JDI
falls back into this session rather than skipping a phase, and never substitutes a different model
of its own choosing.

Where the harness has no subagents, roles are adopted inline instead of spawned. The phases still
run; they just share one context window.

---
