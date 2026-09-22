---
description: "Implement the next wave of pending tasks from the plan — in parallel where the plan allows — show the diff, and ask for feedback."
argument-hint: "[plan slug]"
---

# JDI: Execute

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). **Delegates to: Executor**.

Execute the next pending wave of the plan: every task that is ready to run, at the same time. A
wave of one is a single task, executed exactly as it always was.

Follow these steps:

0. **Load the JDI config** — Read `.jdi/config.yml` at the repository root; fall back to defaults
   in `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory — `${CLAUDE_PLUGIN_ROOT}/reference/config.md`,
   or, if that variable does not resolve, `reference/` one level up from this command file).

1. **Find the plan** — Locate the plan matching `$ARGUMENTS`, or the most recent one, per JDI's
   `reference/plan-store.md`. Read `PLAN.md` for the task checklist.

2. **First-task check** — If `PLAN.md` carries no `- Started:` line, the plan has just been
   approved and has never been executed. Before any implementation begins:

   **Gate on `- Started:`, not on the checklist.** This step writes that line, so its absence is
   the only reliable "this plan has never run" signal. Checklist state is not: this command
   deliberately leaves the task it just executed unchecked (see the closing note), so "every task
   is still unchecked" stays true after a task has already been implemented, and re-running this
   check would re-resolve decisions the plan has already made.

   a. **Ensure the research findings reached the issue (durable-memory gate).** Read `Issue:` and
      `Issue URL:` from `PLAN.md`. If there is an issue, check its comments for one beginning with
      `tracker.research_comment_heading`. If none is there, post it now from `## References` plus
      any architecture doc — this is the same comment `/jdi:research` writes, backfilled here so
      the findings are never lost before code is written. See **T5** in JDI's
      `reference/tracker.md`. Skip and say so when `Issue: none`; warn but proceed if the tracker
      is unreachable.

   b. **Resolve the TDD decision for this plan.** If `tdd.enabled` is not `true`, do nothing and
      say nothing: write no line, and announce no skip. Where the first task's purpose is to build
      the environment the runner needs, perform that task inline as part of TS1 rather than proving
      the runner against a neighbouring environment — see *When the runner does not exist yet* in
      `reference/testing.md`. Otherwise perform **TS1** from JDI's
      `reference/testing.md` and record its result as a `- TDD:` line in `PLAN.md`'s metadata. This
      runs before `c`'s commit, so the decision rides the plan-approval commit. TS1 answers once
      per plan, every later command reads that answer, and editing `.jdi/config.yml` mid-plan
      changes nothing until the next plan.

   c. **Commit the approved plan.** Add a `Started: YYYY-MM-DD` timestamp to the top of `PLAN.md`
      and commit the entire plan folder — `PLAN.md` plus every task file — along with any new
      architecture doc created during research, as `chore: Approve plan for <slug>`. This captures
      the approved plan and the research before any implementation exists.

      In `external` plan mode there is no plan folder to commit: commit only the architecture doc,
      write the `Started:` timestamp into the plan document in the service, and say that the plan
      itself lives in `<plans.service>`.

3. **Pick the wave** — Find **every** unchecked task in the checklist whose dependencies are all
   complete, not only the first; that set is the wave (*Waves*, in JDI's `reference/plan-store.md`).
   Compute it from each task file's `Depends on:`, not from the wave headings in `## Tasks` — with
   that section's two exceptions: the UAT task never shares a wave, and a `## Tasks` with no
   `**Wave N**` headings at all is a plan split before waves existed, which runs one task at a time
   in number order, said once. Read every task file in it. If unchecked tasks exist whose work is
   already in the tree — a wave that was executed and never marked done — stop and suggest
   `/jdi:done` first rather than executing them again.

4. **Verify the dependencies and the file guard** — Confirm every dependency of every task in the
   wave has `status: done`. If no task is eligible, tell the user which dependencies are blocking,
   and stop. Then compare the wave's `## Files`: where two tasks name the same path, keep the
   lower-numbered one in this wave, hold the other for the next, and say so once.

5. **Delegate to the Executor, once per task, all at once** — Hand each task of the wave to its own
   **Executor**, starting them **together** rather than one after another; see *Delegating several
   roles at once* in JDI's `reference/delegation.md`. Where this harness cannot run roles
   concurrently, say so once and run the wave's tasks in number order, adopting the role inline if
   there are no subagents at all. Tell the user which tasks are running together. Pass each
   Executor:
   - the task file content — its own task only
   - the sibling tasks running alongside it with their `## Files` (or that it runs alone)
   - `PLAN.md` for the overall context
   - the referenced architecture docs
   - the TDD decision for this plan, read from the `TDD:` line in `PLAN.md`. `on` means pass that
     decision, the proven invocation the line names, and any pre-existing failure TS1 reported, and
     instruct the Executor to perform **TS2** from JDI's `reference/testing.md`: the failing test
     first, the implementation after it, and both runs returned as evidence. A line reading `off`, a
     missing line, and a line in neither of TS1's two shapes all mean the same thing — this plan
     runs without TDD. **Say nothing to the user; state it to the Executor anyway.** Every dispatch
     carries the decision as a literal line — `TDD: off` or `TDD: on — <invocation>` — because to
     the receiving role, a dispatch that does not mention TDD is indistinguishable from one where
     the decision was resolved and dropped in the handover, and the two demand opposite behaviour.
     TS1 rung 1's silence governs what the *user* is told and what `PLAN.md` records; it does not
     reach the handover between two roles.

   Instruct it to implement the work described in the task file, follow the existing patterns and
   conventions in the codebase, run the task's verification steps, and return a summary of what was
   done, every path it touched, and any issues encountered. Remind it of the Executor's staging
   discipline: stage every edit **by path, its own paths only**, never stash, never touch a
   sibling's file, and do not commit or push.

6. **Verify independently, once the wave has settled** — Wait for every Executor in the wave to
   report; a failure in one does not cancel the others. Then run **each** task's verification steps
   **yourself**, against the settled tree. The Executor's report is evidence, not proof: a role
   that just wrote the code is the worst judge of whether it works, and one that verified while its
   siblings were mid-edit is a weaker witness still. Spot-check any load-bearing citation in each
   report too, and check every changed path is claimed by exactly one task — its `## Files` or its
   Executor's report. A collision an Executor reported means the split was wrong about those two
   tasks: finish the wave, then run the blocked task on its own.

   When the plan's `TDD:` line says `on`, verify the ordering too: confirm the task's new tests are
   in `git diff --staged` and that your own run of the proven invocation is green. **Do not
   reproduce the red** — read the Executor's captured red instead, and check it names the new
   assertion failing. A red that is an import, syntax, or collection error is a broken test rather
   than red evidence, and counts as none. If a task that touched executable code carries neither red
   evidence nor a stated reason there was nothing to test, lead with that the way you would lead
   with a failed verification, and ask the user whether to accept the task or send it back.

7. **Show the diff** — Run `git diff` (and `git diff --staged`) to show the user exactly what
   changed, **task by task** — each task's paths under its own heading — with a brief explanation
   of the changes and why they were made. If any verification failed, lead with that and name the
   task, not with the diff.

8. **Ask for feedback** — Ask the user whether this looks correct and whether any changes are
   needed. If they are happy, suggest `/jdi:done` to mark the wave's tasks complete — one commit
   each — or `/jdi:next` to do that and start the following wave.

Do **not** update any task's status. Do **not** mark anything done. That is `/jdi:done`'s job —
wait for the user's feedback first.
