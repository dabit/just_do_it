---
description: "Mark the task — or every task of the wave — just executed complete, tick it off the plan, and commit each on its own."
argument-hint: "[plan slug]"
---

# JDI: Done

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). No delegation.

Mark what was just executed as complete: one task, or every task of a wave that ran in parallel.

Follow these steps:

0. **Load the JDI config** — Read `.jdi/config.yml` at the repository root; fall back to defaults
   in `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory — `${CLAUDE_PLUGIN_ROOT}/reference/config.md`,
   or, if that variable does not resolve, `reference/` one level up from this command file).
   Then, if `.jdi/config.local.yml` exists beside it, layer it over the result key by key: a mapping
   merges, a scalar or a list replaces the whole value, and a key it does not name is left alone. It
   is the personal, per-checkout override and is never committed — say in one line which top-level
   blocks it overrides (never the values), and say so if git tracks it, because it is meant to be
   ignored.

1. **Find the current wave** — Locate the plan matching `$ARGUMENTS`, or the most recent one, per
   JDI's `reference/plan-store.md`. Read `PLAN.md` and find **every** unchecked task whose
   dependencies are all done — that is the wave just executed (*Waves*, in that file), and it is
   often more than one task. Fix that set **now, before marking anything**: marking one task done
   makes its dependents eligible, and they were not executed. If one of them shows no work in the
   tree — nothing changed under its `## Files`, and no Executor reported on it — it was held back or
   never ran: leave it unchecked and say so.

2. **Mark and commit** — **One task at a time, in number order, one commit each — never one commit
   for the wave.** For each task: set its file to `status: done`, tick **that task only** in
   `PLAN.md` (`- [ ]` → `- [x]`), then commit **by path** — its `## Files`, any extra path its
   Executor reported, its task file, and `PLAN.md` — and nothing else, because the index also holds
   its siblings' work. Never `git add -A`, and never a bare `git commit`. Follow the commit message
   format the repo's `CLAUDE.md` / `AGENTS.md` prescribes; if neither states one, match the style of
   the recent `git log`. Put the task number and title in the commit body.

   Before each commit, run `git status --short` and check column 2 for that task's paths. Anything
   other than `??` there is unstaged work that belongs in this commit. After the last one, nothing
   staged or modified should remain; a leftover path no task claimed is a question for the user.

   In `external` plan mode, the task status lives in the service, not in the repo — update it
   there, and commit only the code.

3. **Close the pieces** — For each task just marked: if `split.pieces` is `tasks` or `subtickets`
   and the task file carries a `Ticket:` line, perform **T8** from JDI's `reference/tracker.md`:
   tick the checklist item, or transition the child issue to its Done state. Skip in `commits` mode,
   and skip when there is no `Ticket:` line — the split either ran as `commits` or degraded to it.
   Warn, never fail: the commit is the real record.

4. **Next up** — Tell the user what is done, with each commit's SHA. If tasks remain, show the next
   wave — which tasks will run together — and suggest `/jdi:execute` to continue, or `/jdi:next` to
   roll straight on. If everything is complete, say so and suggest `/jdi:pr`.
