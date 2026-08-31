---
description: "Mark the current task complete, tick it off the plan, and commit."
argument-hint: "[plan slug]"
---

# JDI: Done

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). No delegation.

Mark the current task as complete.

Follow these steps:

0. **Load the JDI config** — Read `.jdi/config.yml` at the repository root; fall back to defaults in
   `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory — `${CLAUDE_PLUGIN_ROOT}/reference/config.md`).

1. **Find the current task** — Locate the plan matching `$ARGUMENTS`, or the most recent one, per
   JDI's `reference/plan-store.md`. Read `PLAN.md` and find the first unchecked task in the
   checklist — that is the one just executed.

2. **Update the task file** — Change `status: pending` to `status: done`.

3. **Update `PLAN.md`** — Tick the task off the checklist (`- [ ]` → `- [x]`).

4. **Commit** — Stage everything belonging to this task and commit it. Follow the commit message
   format the repo's `CLAUDE.md` / `AGENTS.md` prescribes; if neither states one, match the style
   of the recent `git log`. Put the task number and title in the commit body.

   Before committing, run `git status --short` and check column 2. Anything other than `??` there
   is unstaged work that belongs in this commit.

   In `external` plan mode, the task status lives in the service, not in the repo — update it
   there, and commit only the code.

5. **Next up** — Tell the user the task is done. If tasks remain, show what is next and suggest
   `/jdi:execute` to continue, or `/jdi:next` to roll straight on. If everything is complete, say
   so and suggest `/jdi:pr`.
