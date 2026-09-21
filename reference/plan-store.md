# Plan storage

A JDI plan is a folder with one `PLAN.md` and, between `/jdi:split` and `/jdi:pr`, a set of
numbered task files:

```
<plans.path>/<slug>/
  PLAN.md              # metadata, references, implementation plan, testing strategy, risks, tasks
  01-<task-slug>.md    # one task: status, dependencies, why, description, files, verification
  02-<task-slug>.md
  ...
  NN-uat.md            # final task: user acceptance scenarios
```

Where that folder physically lives is `plans.mode` in `.jdi/config.yml`.

A task file also carries a `Ticket:` line when `split.pieces` mirrors the pieces into the tracker as
tasks or subtickets — see **T7** in `reference/tracker.md`. That mirror is additive: the task files
and the one-commit-per-task rhythm below are identical in all three `split.pieces` modes.

`PLAN.md` itself carries a `TDD:` line, written into the metadata block alongside `- Started:`,
when `tdd.enabled` was `true` at the start of that plan — see **TS1** in `reference/testing.md`.
It has two shapes:

```
- TDD: on — proven YYYY-MM-DD with `<the invocation that ran>`
- TDD: off — <the TS1 rung that applied, and the evidence for it>
```

**Its absence means TDD was never enabled for that plan**, and it is not a gap to be filled: a plan
written before the `tdd` key existed and a plan whose TS1 stopped at its first rung look identical,
deliberately. The line is written once, before the first task, and is never rewritten for that
plan — every later command **reads** it rather than re-detecting anything, so changing
`.jdi/config.yml` mid-plan has no effect until the next one.

## Waves

Tasks are executed a **wave** at a time, and a wave is always derived, never stored: it is **every
unchecked task whose `Depends on:` tasks all have `status: done`**. `/jdi:execute`, `/jdi:next` and
`/jdi:yolo` run the whole wave at once, one Executor per task, concurrently — see *Delegating
several roles at once* in `reference/delegation.md`. The `**Wave N**` headings the Splitter writes
into `## Tasks` are a picture of that for the reader; `Depends on:` is the authority, and the
commands compute the wave from it each time. A wave of one task is exactly the one-task-at-a-time
flow, so a plan that is a strict chain runs as it always did.

Two exceptions, both of which narrow a wave and neither of which widens one:

- **UAT always runs alone, last.** The UAT task is never part of a wave with anything else,
  whatever its `Depends on:` says: it is eligible only when every other task is done.
- **A plan with no `**Wave N**` headings in `## Tasks` was split before waves existed, and runs one
  task at a time, in number order** — each wave is the single lowest-numbered eligible task. Its
  dependencies were written when number order was a guarantee, so a `Depends on: None` there never
  promised independence. Say so once ("this plan was not split for parallel execution; running its
  tasks in order") and suggest `/jdi:split` again if the user wants it cut for parallelism. This is
  the one thing the headings decide; *which* tasks share a wave still comes from `Depends on:`.

Every Executor in a wave works in the **same working tree**. Three rules make that safe:

1. **The guard — same-wave tasks must be file-disjoint.** Before spawning, compare the `## Files`
   of the wave's tasks. The Splitter is supposed to guarantee no overlap; the Butler checks anyway.
   Where two tasks name the same path, the lower-numbered one runs in this wave and the other is
   held for the next, said out loud once. Never run two Executors that may edit one file.
2. **Verify after the wave settles, never during it.** An Executor's own verification ran while its
   siblings were mid-edit, so it is weaker evidence than usual. Wait for every Executor in the wave
   to report, then run each task's Verification yourself against the settled tree.
3. **One commit per task, by path.** A wave leaves several tasks' work staged in one index, so a
   task is never committed with "everything staged". Commit each task on its own, in number order,
   naming exactly its paths: its `## Files`, any extra path its Executor reported touching, and its
   own task file — plus `PLAN.md`, ticked for that task only, so each commit carries its own tick.
   Never `git add -A` and never a bare `git commit` while another task's work is staged. A changed
   path that no task in the wave claims is a question for the user, not something to fold into
   whichever commit is nearest.

The trade-off is said once, here: each commit in a wave was verified against the whole wave's tree,
not against a tree holding that task alone. Disjoint files and independent verification keep that
honest in practice, and the wave's last commit is always a fully verified state.

## `plans.mode: repo` (default)

Plans are files under `<plans.path>/` in the repository being changed, and they are **committed
with the code they describe**. This is the preferred mode: the plan is versioned, reviewable in the
pull request, and travels with the branch.

Read and write them with ordinary file tools. The commit points are:

| Moment | Commit |
|---|---|
| A pause after `/jdi:start`, `/jdi:research`, `/jdi:plan`, or `/jdi:prep` | `docs: Add <slug> plan` — offered, never automatic |
| Before the first task is executed (`/jdi:execute`, `/jdi:yolo`) | `chore: Approve plan for <slug>` — the whole plan folder plus any new architecture doc |
| Each completed task (`/jdi:done`, `/jdi:next`, `/jdi:yolo`) | one commit per task, never squashed — a wave of three tasks is three commits, each by path (see *Waves*) |
| Plan condensation at PR time (`/jdi:pr`) | `docs: Condense <slug> plan into single file` |

**A repo whose plans folder is gitignored is the trap to check for.** Run
`git check-ignore -q <plans.path>` before writing the first plan. If the path is ignored, the files
will land on disk, `git status` will never mention them, and the plan will be silently lost on a
fresh clone. Stop and tell the user; offer to un-ignore the path, to pick another path, or to
switch to `external` mode.

## `plans.mode: external`

Plans live in a note-taking or knowledge service — `plans.service` names it (Obsidian, recuerd0,
Notion, a wiki), `plans.location` names the vault, notebook, space, or parent page. **Nothing
plan-shaped is committed to the repository** in this mode.

Structure is preserved as documents: one parent document per plan, named `<slug>`, with the task
files as child documents or as clearly delimited sections of it, in the same order and with the
same headings the repo mode uses. The `## Tasks` checklist in the parent document remains the
master todo list.

Read and write through the service's MCP tools. If the service exposes no reachable integration in
this session, say so and ask the user whether to fall back to `repo` mode for this piece of work or
to paste/receive the plan contents by hand — do not silently write plan files into the repository
that the config says should not hold them.

Every commit point in the repo-mode table above is **skipped** in this mode, with two consequences
commands must honour:

- The "you can pause here, the plan is committed and resumable" offer is replaced by "the plan is
  saved in `<service>`" — the branch still exists, but it carries no plan.
- At PR time, condensation still happens (the plan document is rewritten in place, slimmed), but
  there are no task files to delete from the repo and no plan commit to make. The task documents
  are deleted or archived in the service instead, and the PR body carries the plan's decisions and
  outcome, because the pull request is now the only place a reviewer sees them.

An architecture doc written during `/jdi:research` is **not** a plan. It goes to `<docs.path>/` in
the repository and is committed with the code in both modes.

## Finding the current plan

Commands that say "find the plan" mean: the plan matching `$ARGUMENTS` if the user named one,
otherwise the most recently modified plan in `<plans.path>/` (repo mode) or in `plans.location`
(external mode). If several are plausible, ask rather than guess — operating on the wrong plan
corrupts two of them.
