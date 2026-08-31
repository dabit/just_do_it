---
description: "Break the current plan into atomic, dependency-ordered tasks, ending with a UAT task."
argument-hint: "[plan slug]"
---

# JDI: Split

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). **Delegates to: Splitter** (standard).

Break the current plan into atomic, actionable tasks.

Follow these steps:

0. **Load the JDI config** — Read `.jdi/config.yml` at the repository root; fall back to defaults in
   `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory — `${CLAUDE_PLUGIN_ROOT}/reference/config.md`).

1. **Find the plan** — Locate the plan matching `$ARGUMENTS`, or the most recent one, per JDI's
   `reference/plan-store.md`. Read `PLAN.md` for the full scope.

2. **Decide whether splitting is worth it** — Judge the Implementation Plan before delegating. The
   goal is the **minimum** number of tasks needed to land the change with confidence, not maximum
   granularity. Over-splitting bloats the commit history with mark-done ceremony and forces context
   shifts that help neither reviewers nor `git bisect`.

   **Skip the Splitter** — write one combined task file plus UAT yourself — when any of:
   - three or fewer files touched, and all the changes must land atomically
   - the plan reads as a single coherent edit (add a flag and the tests that prove it; gate a job
     and update its tests)
   - no independent layers — the production code and its tests must land together to compile or
     pass at all
   - the task boundaries would be cosmetic: no independent review, revert, or test value

   **Run the Splitter** when any of:
   - the work crosses independent layers (migration → backfill → API → UI; an infrastructure
     accessory → the code that calls it)
   - the plan has natural checkpoints — one piece could realistically ship or be reviewed before
     the next starts
   - some subtasks are independently reviewable, revertable, or testable
   - more than roughly five distinct edits with non-trivial sequencing

   When in doubt, prefer fewer tasks. **State the decision and the reason** before proceeding.

3. **Generate the task files** — Two paths, depending on step 2.

   **(a) Skip-Splitter path.** Write the task files yourself:
   - `01-<implement-slug>.md` — Why, Description (copy the Implementation Plan verbatim or
     summarise its steps, keeping the file paths and snippets), Files, and Verification commands
     (lint plus targeted tests).
   - `02-uat.md` — the UAT task, per the UAT rules below.

   Then replace `## Tasks` in `PLAN.md` with a checklist linking to them — normally two items. A
   piece in a separate repository, or one the plan explicitly defers, may earn its own task file;
   that is not over-splitting.

   **(b) Splitter path.** Hand off to the **Splitter** role at the **standard** tier; see JDI's
   `reference/delegation.md`, and adopt the role inline if this harness has no subagents. Pass it
   the full `PLAN.md`, the referenced architecture docs, and the plan folder path, and instruct it
   to:

   - **Split into atomic tasks** — the smallest *meaningful* units of work, each independently
     implementable and verifiable. One task per migration, per data-model change, per service, per
     interface surface; separate the layers when they can genuinely be done independently; extract
     a shared concern several tasks depend on into its own task. **Aim for the minimum number that
     captures real boundaries.**
   - **Determine dependencies** — a task depends on another only if it literally cannot be started
     without it.
   - **Write numbered task files** in the plan folder — `01-<task-slug>.md`, `02-<task-slug>.md`,
     … — numbered in an execution order that respects the dependencies. Each contains: `status:
     pending` at the top, a title, its dependencies (or None), a **Why** in one or two sentences, a
     **Description**, the **Files** to create or modify, and **Verification** — the specific
     commands or checks that confirm the task is done, each with its expected outcome.
   - **Write the UAT task last** — see below.
   - **Update `PLAN.md`** with the master checklist:
     ```
     ## Tasks
     - [ ] 01 — Task title (depends on: none)
     - [ ] 02 — Task title (depends on: 01)
     - [ ] 03 — UAT
     ```

4. **The UAT task** — The final numbered task is always UAT, whichever path was taken. It contains
   user-facing scenarios derived from the plan, with step-by-step instructions the user can follow
   to verify the feature end to end, the expected outcome of each, and the edge cases to check.

   **Map every clause of the issue's acceptance criteria** — both what must now work and what must
   not break — to the scenario or test that proves it. When a clause cannot be observed on merge,
   say so explicitly, state what proves the mechanism instead, and record where the deferral will
   be exercised. Do not imply coverage that does not exist: an acceptance criterion with no
   scenario is how work gets closed on an unobserved claim.

5. **Present the tasks** — Summarise the tasks and their dependencies, note which path step 2 took
   and why if it was a close call, and suggest `/jdi:execute` — or `/jdi:yolo` to run them all.

Do **not** write any implementation code. This command produces task documents only.
