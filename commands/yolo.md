---
description: "Auto-pilot: mark done and execute every remaining task in the plan, a parallel wave at a time, stopping on the first failure."
argument-hint: "[plan slug]"
---

# JDI: YOLO

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). **Delegates to: Executor**.

Automatically mark what was executed done and execute every remaining task in the plan, a **wave**
at a time — every task that is ready, run concurrently — without stopping for feedback.

0. **Load the JDI config** — Read `.jdi/config.yml` at the repository root; fall back to defaults
   in `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory — `${CLAUDE_PLUGIN_ROOT}/reference/config.md`,
   or, if that variable does not resolve, `reference/` one level up from this command file).
   Then, if `.jdi/config.local.yml` exists beside it, layer it over the result key by key: a mapping
   merges, a scalar or a list replaces the whole value, and a key it does not name is left alone. It
   is the personal, per-checkout override and is never committed — say in one line which top-level
   blocks it overrides (never the values), and say so if git tracks it, because it is meant to be
   ignored.

**Find the plan** — Locate the plan matching `$ARGUMENTS`, or the most recent one, per JDI's
`reference/plan-store.md`. Read `PLAN.md` for the task checklist.

**Before the loop — ensure the research findings reached the issue (durable-memory gate).** Read
`Issue:` and `Issue URL:` from `PLAN.md`. If there is an issue, check its comments for one
beginning with `tracker.research_comment_heading`. If none is there, post it now from
`## References` plus any architecture doc — the same comment `/jdi:research` writes, backfilled here
so the issue carries the research record before any task runs. See **T5** in JDI's
`reference/tracker.md`. Skip and say so when `Issue: none`; warn but proceed if the tracker is
unreachable.

**Before the loop — resolve the TDD decision for this plan.** Do this **only when `PLAN.md` carries
no `- Started:` line**, which means this plan has never been executed by any command. If
`tdd.enabled` is not `true`, do nothing and say nothing; otherwise perform **TS1** from JDI's
`reference/testing.md` and record its result as a `- TDD:` line in `PLAN.md`'s metadata. Where the
first task's purpose is to build the environment the runner needs, perform that task inline as part
of TS1 — the gate cannot be proven against something the first task has not created yet, and a
neighbouring container proves a runner for a different checkout. See *When the runner does not
exist yet* in `reference/testing.md`. Then add a
`Started: YYYY-MM-DD` line yourself, exactly as `/jdi:execute`'s first-task check does, so the plan
carries the same "execution has begun" marker whichever command began it.

**Gate on `- Started:`, not on the checklist.** A plan whose first task was run by `/jdi:execute`
still has every box unchecked — that command deliberately leaves ticking to `/jdi:done` — so
checklist state cannot tell "never run" from "already running". Reading it as "never run" would let
a user flip `tdd.enabled` after one task and have this command turn TDD **on** part-way through a
plan that began without it, which is exactly what the next sentence forbids. Anything other than a
missing `- Started:` is a resumption: read the `TDD:` line that is there, or the absence of one, and
re-detect nothing, because a plan that began without TDD must not be turned on part-way through.
This is the only place this command resolves TDD: once per run, never once per task, and TS1's
ambiguous rung asks the user here, at the top, rather than mid-flight.

Then loop through the following cycle until every task is complete. A **wave** is every unchecked
task whose dependencies are all done — see *Waves* in JDI's `reference/plan-store.md`. It is
computed from the task files' `Depends on:` on every pass, never read off the wave headings in
`## Tasks`, and a wave of one task is the old one-by-one loop exactly. That section's two
exceptions apply on every pass: the UAT task never shares a wave, and a `## Tasks` with no
`**Wave N**` headings at all is a plan split before waves existed — run it one task at a time in
number order, and say so once, before the loop.

---

## Cycle — repeat for each wave

### Step 1 — Mark the current wave done

Skip on the first iteration if nothing has been executed yet. The tasks to mark are the unchecked
ones whose dependencies are all done **and** whose work is in the tree; fix that set before marking
anything, because marking one done makes its dependents eligible. An eligible task with nothing
changed under its `## Files` and no Executor report was held back or never ran — leave it for
Step 2. For **each** task in the set, in number order, one at a time:

1. **Update the task file** — `status: pending` → `status: done`.
2. **Update `PLAN.md`** — tick **that task only** off (`- [ ]` → `- [x]`).
3. **Commit this task on its own, by path.** The index holds the whole wave's work, so never stage
   or commit "everything": commit exactly this task's `## Files`, any extra path its Executor
   reported, its task file, and `PLAN.md`. **Each task gets its own commit — never squash several
   tasks, or a wave, into one.** Follow the commit format the repo's `CLAUDE.md` / `AGENTS.md`
   prescribes, or the style of the recent `git log`, and put the task number and title in the body.
   Check `git status --short` column 2 for unstaged work on this task's paths first. In `external`
   plan mode, update the status in the service and commit only the code.
4. **Close the piece.** If `split.pieces` is `tasks` or `subtickets` and the task file carries a
   `Ticket:` line, perform **T8** from JDI's `reference/tracker.md` — tick the checklist item, or
   transition the child issue to its Done state. Skip in `commits` mode and when there is no
   `Ticket:` line. Warn, never fail: a tracker that will not accept the write is not a reason to
   stop the loop.

### Step 2 — Execute the next wave

1. **Pick the wave** — **every** unchecked task whose dependencies are all complete, not only the
   first. Read each of those task files.
2. **Verify the dependencies and the file guard** — confirm every dependency has `status: done`; a
   task with one unmet simply is not in this wave. If no task is eligible, **stop** and tell the
   user which dependencies are blocking. Then compare the wave's `## Files`: where two tasks name
   the same path, keep the lower-numbered one, hold the other for the next wave, and say so once.
3. **Delegate to the Executor, once per task, all at once** — hand each task of the wave to its own
   **Executor**, starting them **together** rather than one after another; see *Delegating several
   roles at once* in JDI's `reference/delegation.md`. Where this harness cannot run roles
   concurrently, say so **once for the run** and execute each wave's tasks in number order,
   adopting the role inline if there are no subagents at all. Say which tasks are running
   together. Pass each Executor its own task file content, the sibling tasks running alongside it
   with their `## Files` (or that it runs alone), `PLAN.md` for context, and the referenced
   architecture docs. Read the
   `TDD:` line in `PLAN.md` as well: `on` means pass that decision and the proven invocation the
   line names, and instruct the Executor to perform **TS2** from JDI's `reference/testing.md` — the
   failing test first, the implementation after it, and both runs returned as evidence. A line
   reading `off`, a missing line, and an unparseable line all mean the same thing: this plan runs
   without TDD. Say nothing to the user — but **state it to the Executor anyway**, as a literal
   `TDD: off` line in the dispatch: a dispatch silent on TDD is indistinguishable, to the role
   receiving it, from one where the decision was resolved and lost in the handover.
   **Never run TS1 here** — a plan running without TDD writes no line either, so a
   missing line is not an invitation to detect one. No line means no TDD, for every command,
   always; detecting here would let a mid-plan config flip turn TDD on part-way through a plan.
   Instruct it to implement the task, follow the codebase's existing patterns, run the task's
   verification steps, and report what was done, every path it touched, and any issues. Remind it:
   stage every edit by path — its own paths only — never stash, never touch a sibling's file, do
   not commit or push.
4. **Self-verify, once the wave has settled** — wait for **every** Executor in the wave to report; a
   sibling still running is never cancelled because another failed. Then **run each task's
   verification steps yourself**, against the settled tree, to confirm independently that the work
   passes, and check every changed path is claimed by exactly one task. Do not trust an Executor's
   report alone; a role that just wrote the code is the worst judge of whether it works, and one
   that verified while its siblings were mid-edit is a weaker witness still. Always verify. When the
   `TDD:` line says `on`, confirm the task's new tests are in `git diff --staged` and that your own
   run is green; **do not reproduce the red** — read the Executor's captured red and check it names
   the new assertion failing, since an import, syntax, or collection error is a broken test rather
   than red evidence and counts as none.
5. **Check for failure** — if any verification step of any task in the wave fails, **stop the loop
   at the end of this wave**. Show the user which task failed, its diff, the failing output, and
   what went wrong — and which of its siblings passed — and ask how to proceed. Mark nothing from
   this wave done: a sibling's green may not survive the fix. Do **not** continue to the next wave.
   An Executor that reported a collision with a sibling's path is not a failure of the loop: let
   the wave settle, then run that task on its own before moving on, and say the split was wrong
   about those two. An auto-pilot that carries on past a red build produces a branch
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

The next pass marks the whole wave done, one commit per task, and picks up whatever those tasks
unblocked.

---

## When every task is complete

After the final task is committed, say the plan is done, show a summary of the completed tasks with
their commit SHAs — grouped by the wave they ran in — and suggest `/jdi:pr`.

If the UAT task was executed by an agent rather than by the user, **say that explicitly** — an
agent running through UAT scenarios is a smoke test, not user acceptance, and `/jdi:pr` will ask
again.
