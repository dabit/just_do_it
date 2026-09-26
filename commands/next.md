---
description: "Mark the wave just executed complete, then immediately execute the next one — in parallel where the plan allows."
argument-hint: "[plan slug]"
---

# JDI: Next

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). **Delegates to: Executor**.

Mark what was just executed as complete, then immediately execute the next wave — every task that
is now ready, at the same time. This is `/jdi:done` followed by `/jdi:execute`, in a single step.

0. **Load the JDI config** — Read `.jdi/config.yml` at the repository root; fall back to defaults
   in `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory — `${CLAUDE_PLUGIN_ROOT}/reference/config.md`,
   or, if that variable does not resolve, `reference/` one level up from this command file).
   Then, if `.jdi/config.local.yml` exists beside it, layer it over the result key by key: a mapping
   merges, a scalar or a list replaces the whole value, and a key it does not name is left alone. It
   is the personal, per-checkout override and is never committed — say in one line which top-level
   blocks it overrides (never the values), and say so if git tracks it, because it is meant to be
   ignored.

   **Then resolve the delegation transport, once** - If `delegation.transport` is `auto` or
   `herdr`, perform **H1** from JDI's `reference/herdr.md` here and nowhere else, and use its answer
   for every delegation in this run; no role re-probes. With `herdr`, announce a failed check once,
   with what came back, and delegate as `native`. With `auto`, say nothing outside Herdr, and
   announce once when inside Herdr a later check fails. Any other value: say so once, then `native`.
   **With `delegation.transport` `native` or absent, say nothing at all**: run no Herdr command at
   step 0, and outside a ladder announcement never mention the transport, summaries included.

---

## Phase 1 — Mark the current wave done

1. **Find the current wave** — Locate the plan matching `$ARGUMENTS`, or the most recent one, per
   JDI's `reference/plan-store.md`. Read `PLAN.md` and find **every** unchecked task whose
   dependencies are all done — that is the wave just executed (*Waves*, in that file). Fix that
   set **now, before marking anything**: marking one task done makes its dependents eligible, and
   they were not executed. A task in the set with no work in the tree was held back or never ran:
   leave it unchecked, and it joins the wave Phase 2 runs.

2. **Mark and commit, one task at a time** — In number order, **one commit per task, never one for
   the wave**. For each: change its file's `status: pending` to `status: done`, tick **that task
   only** in `PLAN.md` (`- [ ]` → `- [x]`), and commit **by path** — its `## Files`, any extra path
   its Executor reported, its task file, and `PLAN.md` — because the index also holds its siblings'
   work. Never `git add -A`, never a bare `git commit`. Follow the commit format the repo's
   `CLAUDE.md` / `AGENTS.md` prescribes, or the style of the recent `git log`, with the task number
   and title in the body. Check `git status --short` column 2 for that task's paths first. In
   `external` plan mode, update the task status in the service and commit only the code.

3. **Close the pieces** — For each task just marked: if `split.pieces` is `tasks` or `subtickets`
   and the task file carries a `Ticket:` line, perform **T8** from JDI's `reference/tracker.md`:
   tick the checklist item, or transition the child issue to its Done state. Skip in `commits` mode
   and when there is no `Ticket:` line. Warn, never fail.

---

## Phase 2 — Execute the next wave

4. **Check for remaining tasks** — If everything is now complete, say so and suggest `/jdi:pr`.
   Stop here.

5. **Pick the wave** — Find **every** unchecked task whose dependencies are all complete, computed
   from each task file's `Depends on:`. The two exceptions in *Waves* apply: the UAT task never
   shares a wave, and a `## Tasks` with no `**Wave N**` headings is a plan split before waves
   existed, which runs one task at a time in number order, said once. Read every one of those task
   files.

6. **Verify the dependencies and the file guard** — Confirm every dependency has `status: done`. If
   no task is eligible, tell the user which dependencies are blocking, and stop. Compare the wave's
   `## Files`: where two tasks name the same path, keep the lower-numbered one, hold the other for
   the next wave, and say so once.

7. **Delegate to the Executor, once per task, all at once** — Hand each task of the wave to its own
   **Executor**, starting them **together**; see *Delegating several roles at once* in JDI's
   `reference/delegation.md`. Each Executor is resolved per *Delegating several roles at once*,
   including the transport `delegation.transport` selects; a worker waiting on the user is answered
   where it runs, and the wave settles before anything is verified or committed. Where this harness
   cannot run roles concurrently, say so once and run
   them in number order, adopting the role inline if there are no subagents at all. Tell the user
   which tasks are running together. Pass each Executor its own task file content, the sibling tasks
   running alongside it with their `## Files` (or that it runs alone), `PLAN.md` for context, and
   the referenced architecture docs. Read the `TDD:` line in `PLAN.md` as well: `on` means pass that
   decision and the proven invocation the line names, and instruct the Executor to perform **TS2**
   from JDI's `reference/testing.md` — the failing test first, the implementation after it, and both
   runs returned as evidence. A line reading `off`, a missing line, and an unparseable line all mean
   the same thing: this plan runs without TDD — say nothing to the user, and still state
   `TDD: off` to the Executor, since a dispatch that omits it cannot be told apart from one that
   lost it. **Never run TS1 here** — a plan running without TDD
   writes no line either, so a missing line is not an invitation to detect one. No line means no
   TDD, for every command, always; detecting here would let a mid-plan config flip turn TDD on
   part-way through a plan. Instruct it to implement the task, follow the codebase's existing
   patterns, run the task's verification steps, and report what was done, every path it touched, and
   any issues. Remind it: stage every edit by path — its own paths only — never stash, never touch a
   sibling's file, do not commit or push.

8. **Verify independently, once the wave has settled** — Wait for every Executor to report; one
   failure does not cancel the others. Then run **each** task's verification steps yourself, against
   the settled tree, and check every changed path is claimed by exactly one task. The Executor's
   report is evidence, not proof — less so when it verified with siblings mid-edit. When the `TDD:`
   line says `on`, confirm the task's new tests are in `git diff --staged` and that your own run is
   green; **do not reproduce the red** — read the Executor's captured red and check it names the new
   assertion failing, since an import, syntax, or collection error is a broken test rather than red
   evidence and counts as none. If a task that touched executable code carries neither red evidence
   nor a stated reason there was nothing to test, lead with that the way you would lead with a
   failed verification, and ask whether to accept it or send it back.

9. **Show the diff** — Run `git diff` (and `git diff --staged`) and present it **task by task**,
   with a brief explanation of what changed and why. If any verification failed, lead with that and
   name the task.

10. **Ask for feedback** — Ask whether this looks correct and whether any changes are needed. If
    they are happy, suggest `/jdi:next` to continue, or `/jdi:done` if this was the last wave.

Do **not** mark the new wave's tasks done. Wait for the user's feedback first.
