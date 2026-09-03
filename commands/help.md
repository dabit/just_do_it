---
description: "Explain the Just Do It (JDI) workflow — the commands, the roles, the tiers, and the typical flow."
---

# JDI: Help

**Role: Butler** — JDI's orchestrator (`roles/butler.md`).

Explain the Just Do It (JDI) workflow to the user. Print the following, then add one closing line
naming what this repository is currently configured for — the tracker, the plan store, what the
split pieces become, whether TDD is on, and whether `.jdi/config.yml` exists at all. If it does not,
say `/jdi:init` writes it, and that JDI works without it by asking as it goes.

---

## Just Do It (JDI)

A structured dev workflow that takes a change from idea to pull request. It works with any issue
tracker or none, stores plans in the repo or in a note service, and runs on any agent harness.

### Commands

| Command | Roles | Tier | What it does |
|---|---|---|---|
| `/jdi:init` | Butler | fast | Set JDI up for this repo — tracker, split pieces, TDD, plan store, docs folder. Writes `.jdi/config.yml`. |
| `/jdi:prep` | Butler + Researcher + Planner + Splitter | fast + deep + standard | Run start, research, plan, and split in one pass. Stops only for real questions, and leaves a task list ready for `/jdi:yolo`. |
| `/jdi:start` | Butler | fast | Kick off a task — describe it, optionally link an issue. Creates the branch and the initial `PLAN.md`. |
| `/jdi:research` | Researcher | deep | Find or create the architecture docs for the area being changed. Searches past plans. Writes the findings back to the issue. |
| `/jdi:plan` | Butler + Planner | deep | Clarify the ambiguities with you, then write the implementation plan on top of the research. |
| `/jdi:split` | Splitter | standard | Break the plan into atomic, dependency-ordered tasks with verification steps. Ends with a UAT task. Mirrors them to the tracker if `split.pieces` says so. |
| `/jdi:execute` | Butler + Executor | deep | Implement the next pending task. Shows the diff and asks for your feedback. Proves the test suite runs, once per plan, when `tdd.enabled` is on. |
| `/jdi:done` | Butler | fast | Mark the current task complete, update the checklist, and commit. |
| `/jdi:next` | Butler + Executor | deep | `/jdi:done` then `/jdi:execute`, in one step. Reads the plan's TDD decision; never re-decides it. |
| `/jdi:yolo` | Butler + Executor | deep | Auto-pilot: done + execute every remaining task. Stops on the first failure — but the expected red inside a TDD task is required evidence, not a failure, and does not stop it. |
| `/jdi:pair` | Butler + Executor ×2 | deep | Auto-pilot the remaining tasks as a pair: two agents in two Herdr panes ping-ponging a failing test, with the Butler driving the turns and taking neither side. Needs TDD on and a Herdr session; degrades by asking, never silently. |
| `/jdi:status` | Butler | fast | Show progress on the current plan. |
| `/jdi:help` | Butler | fast | Print this command table and the typical flow, then say what this repository is configured for. |
| `/jdi:pr` | Butler + Synthesizer + PR Writer | standard | Condense the plan, push, and open the pull request. |
| `/jdi:feedback` | Butler + Feedbacker | deep | Critique the latest output on demand — verdict, fixes, and proposed prompt improvements. |
| `/jdi:replan` | Butler + Planner | deep | Throw the plan away and write a fresh one. |
| `/jdi:reresearch` | Butler + Researcher | deep | Throw the research away and look again. |

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

### Tiers, not models

JDI names three tiers instead of models, so it runs anywhere: **deep** (research, planning,
implementation, review), **standard** (splitting, condensing, PR writing), and **fast**
(orchestration, status, commits). Map them to real models in `.jdi/config.yml`, or leave them
unset and run everything on the session's own model — both are fully supported.

Where the harness has no subagents, roles are adopted inline instead of spawned. The phases still
run; they just share one context window.

---
