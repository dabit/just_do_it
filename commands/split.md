---
description: "Break the current plan into atomic, dependency-ordered tasks, ending with a UAT task."
argument-hint: "[plan slug]"
---

# JDI: Split

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). **Delegates to: Splitter**.

Break the current plan into atomic, actionable tasks.

Follow these steps:

0. **Load the JDI config** — Read `.jdi/config.yml` at the repository root; fall back to defaults
   in `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory — `${CLAUDE_PLUGIN_ROOT}/reference/config.md`,
   or, if that variable does not resolve, `reference/` one level up from this command file).

   **Then resolve Jev, once** — If `jev.enabled` is `true`, run the ladder in JDI's
   `reference/jev.md` here and nowhere else: find a key (`$TYPESAFE_API_KEY`, else
   `~/.config/typesafe/api_key`), and send one throwaway question against a couple of sentences of
   state. Jev is available for this run only once a real request has come back with a real answer —
   a key that exists is not proof and the absence of an error is not proof. On the first rung that
   fails, say so **once**, with what you tried and what came back, and treat this run as
   `jev.enabled: false` from there on. Then hand the role "Jev is available" or nothing as a
   resolved fact; it never reads the key or re-probes. **With `jev.enabled` false or absent, say
   nothing at all** — nothing was skipped.

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
   - the plan contains pieces that share no files and no state, and so could be implemented **at
     the same time** — `/jdi:execute` and `/jdi:yolo` run every eligible task concurrently, so a
     cut that lets two pieces overlap is a real boundary, not a cosmetic one
   - more than roughly five distinct edits with non-trivial sequencing

   When in doubt, prefer fewer tasks. **State the decision and the reason** before proceeding.

3. **Generate the task files** — Two paths, depending on step 2.

   **(a) Skip-Splitter path.** Write the task files yourself:
   - `01-<implement-slug>.md` — Why, Description (copy the Implementation Plan verbatim or
     summarise its steps, keeping the file paths and snippets), Files, and Verification commands
     (lint plus targeted tests).
   - `02-uat.md` — the UAT task, per the UAT rules below, with `Depends on: 01`.

   Then replace `## Tasks` in `PLAN.md` with a checklist linking to them — normally two items, each
   under its own `**Wave N**` heading exactly as path (b) writes them, since a checklist without
   wave headings is read as a plan split before waves existed. A
   piece in a separate repository, or one the plan explicitly defers, may earn its own task file;
   that is not over-splitting.

   **(b) Splitter path.** Hand off to the **Splitter** role; see JDI's
   `reference/delegation.md`, and adopt the role inline if this harness has no subagents. Pass it
   the full `PLAN.md`, the referenced architecture docs, the plan folder path, and whether Jev
   is available, and instruct it to:

   - **Split into atomic tasks** — the smallest *meaningful* units of work, each independently
     implementable and verifiable. One task per migration, per data-model change, per service, per
     interface surface; separate the layers when they can genuinely be done independently; extract
     a shared concern several tasks depend on into its own task. **Aim for the minimum number that
     captures real boundaries.**
   - **Determine dependencies** — a task depends on another only if it literally cannot be started
     without it. A dependency is never a preferred reading order; the numbering carries that.
   - **Prioritise parallelisation** — perform the *Analysing for parallelism* pass in the
     Splitter's role file: find the independent pieces, shorten the longest dependency chain by
     extracting what several tasks share into an early task of its own, and make sure **no two
     tasks that could run together name the same path in `## Files`**. Every task with its
     dependencies done is executed at the same time as its siblings, in one working tree, and is
     committed by exactly the paths its `## Files` lists — so that list must be complete.
   - **Write numbered task files** in the plan folder — `01-<task-slug>.md`, `02-<task-slug>.md`,
     … — numbered in an execution order that respects the dependencies. Each contains: `status:
     pending` at the top, a title, its dependencies (or None), a **Why** in one or two sentences, a
     **Description**, the **Files** to create, modify, or delete, and **Verification** — the
     specific commands or checks that confirm the task is done, each with its expected outcome, and
     each able to pass on this task's work alone while a sibling is still half-finished.
   - **Write the UAT task last** — see below.
   - **Update `PLAN.md`** with the master checklist, grouped by wave — a wave being the tasks whose
     dependencies are all in earlier waves, derived from `Depends on:` and never declared
     separately:
     ```
     ## Tasks

     **Wave 1** — run together
     - [ ] 01 — Task title (depends on: none)
     - [ ] 02 — Task title (depends on: none)

     **Wave 2**
     - [ ] 03 — Task title (depends on: 01, 02)

     **Wave 3**
     - [ ] 04 — UAT (depends on: 03)
     ```

4. **The UAT task** — The final numbered task is always UAT, whichever path was taken. It depends
   on every other task, so it is the last wave and runs alone. It contains
   user-facing scenarios derived from the plan, with step-by-step instructions the user can follow
   to verify the feature end to end, the expected outcome of each, and the edge cases to check.

   **Map every clause of the issue's acceptance criteria** — both what must now work and what must
   not break — to the scenario or test that proves it. When a clause cannot be observed on merge,
   say so explicitly, state what proves the mechanism instead, and record where the deferral will
   be exercised. Do not imply coverage that does not exist: an acceptance criterion with no
   scenario is how work gets closed on an unobserved claim.

5. **Materialise the pieces** — Read `split.pieces` from the config: `commits` (the default),
   `tasks`, or `subtickets`.

   **`commits`** — nothing to do. The task files are the pieces, and each one becomes a commit when
   it is marked done. Say nothing; there is nothing to skip.

   **`tasks` or `subtickets`** — perform **T7** from JDI's `reference/tracker.md`: mirror every task
   file, UAT included, as a checklist item on the issue or as a child issue of it. Ask **once** for
   the batch before creating any child issue, listing the titles. Record what each write produced as
   a `Ticket:` line in the task file it came from, so a re-split updates the mirror instead of
   duplicating it. Announce any rung of T7's degradation ladder you land on — no tracker, no issue,
   no native support, or a declined confirmation all mean this plan runs as `commits`, out loud.

   The mirror is **additive**. Whatever `split.pieces` says, the task files stay where they are and
   `/jdi:execute` and `/jdi:done` keep working off them, one commit per task. A tracker mirror that
   makes the work visible to people outside the repository is the only thing being added.

6. **Present the tasks** — Summarise the tasks wave by wave: which run together, the widest wave,
   and the critical path — the longest dependency chain, which is the floor on how long execution
   takes. Name any dependency that exists only because two tasks share a file. Before presenting,
   check the Splitter's work yourself: no dependency points at a later number, and no two tasks
   without a dependency path between them share a path in `## Files`. Note which path step 2 took
   and why if it was a close call, name the pieces that were mirrored to the tracker (or say the run
   is `commits`), and suggest `/jdi:execute` — or `/jdi:yolo` to run them all.

Do **not** write any implementation code. This command produces task documents only.
