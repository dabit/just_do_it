---
description: "Auto-pilot: mark done and execute every remaining task in the plan, stopping on the first failure."
argument-hint: "[plan slug]"
---

# JDI: YOLO

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). **Delegates to: Executor** (deep).

Automatically mark the current task done and execute every remaining task in the plan, one by one,
without stopping for feedback.

0. **Load the JDI config** — Read `.jdi/config.yml` at the repository root; fall back to defaults
   in `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory — `${CLAUDE_PLUGIN_ROOT}/reference/config.md`,
   or, if that variable does not resolve, `reference/` one level up from this command file).

**Find the plan** — Locate the plan matching `$ARGUMENTS`, or the most recent one, per JDI's
`reference/plan-store.md`. Read `PLAN.md` for the task checklist.

**Before the loop — ensure the research findings reached the issue (durable-memory gate).** Read
`Issue:` and `Issue URL:` from `PLAN.md`. If there is an issue, check its comments for one
beginning with `tracker.research_comment_heading`. If none is there, post it now from
`## References` plus any architecture doc — the same comment `/jdi:research` writes, backfilled here
so the issue carries the research record before any task runs. See **T5** in JDI's
`reference/tracker.md`. Skip and say so when `Issue: none`; warn but proceed if the tracker is
unreachable.

**Before the loop — resolve the TDD decision for this plan.** Do this only when every task in the
checklist is still unchecked and `PLAN.md` carries no `TDD:` line: if `tdd.enabled` is not `true`,
do nothing and say nothing; otherwise perform **TS1** from JDI's `reference/testing.md` and record
its result as a `- TDD:` line immediately after `- Started:` in `PLAN.md`. Anything else is a
resumption — read the line that is there, or the absence of one, and re-detect nothing, because a
plan that began without TDD must not be turned on part-way through. This is the only place this
command resolves TDD: once per run, never once per task, and TS1's ambiguous rung asks the user
here, at the top, rather than mid-flight.

Then loop through the following cycle until every task is complete.

---

## Cycle — repeat for each task

### Step 1 — Mark the current task done

Skip on the first iteration if no task has been executed yet. If there is a previously executed but
unchecked task:

1. **Update the task file** — `status: pending` → `status: done`.
2. **Update `PLAN.md`** — tick the task off (`- [ ]` → `- [x]`).
3. **Commit this task on its own.** Stage everything for this task and commit. **Each task gets its
   own commit — never squash several tasks into one.** Follow the commit format the repo's
   `CLAUDE.md` / `AGENTS.md` prescribes, or the style of the recent `git log`, and put the task
   number and title in the body. Check `git status --short` column 2 for unstaged work first. In
   `external` plan mode, update the status in the service and commit only the code.
4. **Close the piece.** If `split.pieces` is `tasks` or `subtickets` and the task file carries a
   `Ticket:` line, perform **T8** from JDI's `reference/tracker.md` — tick the checklist item, or
   transition the child issue to its Done state. Skip in `commits` mode and when there is no
   `Ticket:` line. Warn, never fail: a tracker that will not accept the write is not a reason to
   stop the loop.

### Step 2 — Execute the next task

1. **Pick the next task** — the first unchecked task whose dependencies are all complete. Read that
   task file.
2. **Verify the dependencies** — confirm every dependency has `status: done`. If one is unmet, skip
   this task and try the next eligible one. If no task is eligible, **stop** and tell the user which
   dependencies are blocking.
3. **Delegate to the Executor** — hand off to the **Executor** role at the **deep** tier; see JDI's
   `reference/delegation.md`, and adopt the role inline if this harness has no subagents. Pass it
   the task file content, `PLAN.md` for context, and the referenced architecture docs. Read the
   `TDD:` line in `PLAN.md` as well: `on` means pass that decision and the proven invocation the
   line names, and instruct the Executor to perform **TS2** from JDI's `reference/testing.md` — the
   failing test first, the implementation after it, and both runs returned as evidence. A line
   reading `off`, a missing line, and an unparseable line all mean the same thing: pass nothing and
   say nothing. **Never run TS1 here** — a plan running without TDD writes no line either, so a
   missing line is not an invitation to detect one. No line means no TDD, for every command,
   always; detecting here would let a mid-plan config flip turn TDD on part-way through a plan.
   Instruct it to implement the task, follow the codebase's existing patterns, run the task's
   verification steps, and report what was done plus any issues. Remind it: stage every edit, never
   stash, do not commit or push.
4. **Self-verify** — after the Executor finishes, **run the task's verification steps yourself** to
   confirm independently that the work passes. Do not trust the Executor's report alone; a role that
   just wrote the code is the worst judge of whether it works. Always verify. When the `TDD:` line
   says `on`, confirm the task's new tests are in `git diff --staged` and that your own run is
   green; **do not reproduce the red** — read the Executor's captured red and check it names the new
   assertion failing, since an import, syntax, or collection error is a broken test rather than red
   evidence and counts as none.
5. **Check for failure** — if any verification step fails, **stop the loop immediately**. Show the
   user the diff, the failing output, and what went wrong, and ask how to proceed. Do **not**
   continue to the next task. An auto-pilot that carries on past a red build produces a branch
   nobody can bisect.

   The failure being checked is the outcome of **your own** run in item 4, against the tree as it
   stands now. Under TDD the Executor's report will contain a failing test run: that red is required
   evidence, captured before the implementation existed, and it is a record of a past state, not a
   verification result. Do not treat it as one. If your own item-4 run is green, the task passed,
   whatever red the report contains; if your own run is red, stop, whatever the report says.

   One new stop: TDD is on, the task touched executable code, and the report carries neither red-run
   evidence nor a stated reason there was nothing to test. Stop the loop and show the report — that
   is the same class of failure as a verification that was never run.

### Step 3 — Loop back to Step 1

---

## When every task is complete

After the final task is committed, say the plan is done, show a summary of the completed tasks with
their commit SHAs, and suggest `/jdi:pr`.

If the UAT task was executed by an agent rather than by the user, **say that explicitly** — an
agent running through UAT scenarios is a smoke test, not user acceptance, and `/jdi:pr` will ask
again.
