---
description: "Implement the next pending task from the plan, show the diff, and ask for feedback."
argument-hint: "[plan slug]"
---

# JDI: Execute

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). **Delegates to: Executor** (deep).

Execute the next pending task from the plan.

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
      say nothing: write no line, and announce no skip. Otherwise perform **TS1** from JDI's
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

3. **Pick the next task** — Find the first unchecked task in the checklist whose dependencies are
   all complete. Read that task file.

4. **Verify the dependencies** — Confirm every task listed as a dependency has `status: done`. If
   not, tell the user which ones must be completed first, and stop.

5. **Delegate to the Executor** — Hand off to the **Executor** role at the **deep** tier; see JDI's
   `reference/delegation.md`, and adopt the role inline if this harness has no subagents. Pass it:
   - the task file content
   - `PLAN.md` for the overall context
   - the referenced architecture docs
   - the TDD decision for this plan, read from the `TDD:` line in `PLAN.md`. `on` means pass that
     decision, the proven invocation the line names, and any pre-existing failure TS1 reported, and
     instruct the Executor to perform **TS2** from JDI's `reference/testing.md`: the failing test
     first, the implementation after it, and both runs returned as evidence. A line reading `off`, a
     missing line, and a line in neither of TS1's two shapes all mean the same thing — pass nothing
     and say nothing.

   Instruct it to implement the work described in the task file, follow the existing patterns and
   conventions in the codebase, run the task's verification steps, and return a summary of what was
   done plus any issues encountered. Remind it of the Executor's staging discipline: stage every
   edit, never stash, and do not commit or push.

6. **Verify independently** — Run the task's verification steps **yourself**. The Executor's report
   is evidence, not proof: a role that just wrote the code is the worst judge of whether it works.
   Spot-check any load-bearing citation in its report too.

   When the plan's `TDD:` line says `on`, verify the ordering too: confirm the task's new tests are
   in `git diff --staged` and that your own run of the proven invocation is green. **Do not
   reproduce the red** — read the Executor's captured red instead, and check it names the new
   assertion failing. A red that is an import, syntax, or collection error is a broken test rather
   than red evidence, and counts as none. If a task that touched executable code carries neither red
   evidence nor a stated reason there was nothing to test, lead with that the way you would lead
   with a failed verification, and ask the user whether to accept the task or send it back.

7. **Show the diff** — Run `git diff` (and `git diff --staged`) to show the user exactly what
   changed, with a brief explanation of the changes and why they were made. If verification failed,
   lead with that, not with the diff.

8. **Ask for feedback** — Ask the user whether this looks correct and whether any changes are
   needed. If they are happy, suggest `/jdi:done` to mark the task complete, or `/jdi:next` to mark
   it done and start the following one.

Do **not** update the task's status. Do **not** mark it done. That is `/jdi:done`'s job — wait for
the user's feedback first.
