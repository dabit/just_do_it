---
description: "Show progress on the current plan — what is done, what is next."
argument-hint: "[plan slug]"
---

# JDI: Status

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). No delegation.

Show the current status of the plan.

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

1. **Find the plan** — Locate the plan matching `$ARGUMENTS`, or the most recent one, per JDI's
   `reference/plan-store.md`. Read `PLAN.md`.

2. **Show the progress** — Display the task checklist, marking what is done and what is pending,
   with a summary line like "3/7 tasks complete".

3. **Show the next wave** — Identify every pending task whose dependencies are all done — the wave
   `/jdi:execute` would run together (*Waves*, in JDI's `reference/plan-store.md`) — and show each
   one's title and description, so the user knows what is up next. For the tasks still waiting,
   name the dependency blocking each.

4. **Show the ground truth** — The checklist records intent; git records what happened. Report the
   current branch, whether the tree is clean (`git status -sb`), and whether the branch is pushed.
   **Never assert commit, push, or merge state from recall** — check it in this session or do not
   claim it. If the checklist and the git history disagree, say so plainly: that gap is the most
   useful thing this command can surface.
