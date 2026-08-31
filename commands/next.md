---
description: "Mark the current task complete, then immediately execute the next one."
argument-hint: "[plan slug]"
---

# JDI: Next

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). **Delegates to: Executor** (deep).

Mark the current task as complete, then immediately execute the next one. This is `/jdi:done`
followed by `/jdi:execute`, in a single step.

0. **Load the JDI config** — Read `.jdi/config.yml` at the repository root; fall back to defaults in
   `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory — `${CLAUDE_PLUGIN_ROOT}/reference/config.md`).

---

## Phase 1 — Mark the current task done

1. **Find the current task** — Locate the plan matching `$ARGUMENTS`, or the most recent one, per
   JDI's `reference/plan-store.md`. Read `PLAN.md` and find the first unchecked task in the
   checklist — that is the one just executed.

2. **Update the task file** — Change `status: pending` to `status: done`.

3. **Update `PLAN.md`** — Tick the task off the checklist (`- [ ]` → `- [x]`).

4. **Commit** — Stage everything belonging to this task and commit it, following the commit format
   the repo's `CLAUDE.md` / `AGENTS.md` prescribes, or the style of the recent `git log`. Put the
   task number and title in the body. Check `git status --short` column 2 for unstaged work first.
   In `external` plan mode, update the task status in the service and commit only the code.

---

## Phase 2 — Execute the next task

5. **Check for remaining tasks** — If everything is now complete, say so and suggest `/jdi:pr`.
   Stop here.

6. **Pick the next task** — Find the first unchecked task whose dependencies are all complete. Read
   that task file.

7. **Verify the dependencies** — Confirm every dependency has `status: done`. If not, tell the user
   which ones are blocking, and stop.

8. **Delegate to the Executor** — Hand off to the **Executor** role at the **deep** tier; see JDI's
   `reference/delegation.md`, and adopt the role inline if this harness has no subagents. Pass it
   the task file content, `PLAN.md` for context, and the referenced architecture docs. Instruct it
   to implement the task, follow the codebase's existing patterns, run the task's verification
   steps, and report what was done plus any issues. Remind it: stage every edit, never stash, do
   not commit or push.

9. **Verify independently** — Run the task's verification steps yourself. The Executor's report is
   evidence, not proof.

10. **Show the diff** — Run `git diff` (and `git diff --staged`) and present it with a brief
    explanation of what changed and why. If verification failed, lead with that.

11. **Ask for feedback** — Ask whether this looks correct and whether any changes are needed. If
    they are happy, suggest `/jdi:next` to continue, or `/jdi:done` if this was the last task.

Do **not** mark the new task done. Wait for the user's feedback first.
