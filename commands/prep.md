---
description: "Prepare a task end to end — start, research, plan, and split in one pass, stopping only for real questions."
argument-hint: "<what you are about to build>"
---

# JDI: Prep

**Role: Butler** — JDI's orchestrator (`roles/butler.md`).
**Delegates to: Researcher** (deep), **Planner** (deep), **Splitter** (standard).

Prepare a new JDI task end to end, without writing implementation code. This combines
`/jdi:start`, `/jdi:research`, `/jdi:plan`, and `/jdi:split` into one flow. The user wants to work
on: $ARGUMENTS

**Stop only when you genuinely need user input.** Do not stop for approval between phases.

Follow these steps:

1. **Load the JDI config** — Read `.jdi/config.yml` at the repository root; fall back to defaults
   recorded in `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory —
   `${CLAUDE_PLUGIN_ROOT}/reference/config.md`). Everything below refers to `tracker`, `plans`,
   `docs`, and `consumers` from it.

2. **Determine the tracking context** — If the config records a tracker, confirm that this work
   uses it or something else. If it records none, ask whether the work is tracked in Jira, Linear,
   GitHub Issues, another tracker, or not at all. "Not tracked" is a fine answer.

3. **Determine the issue reference** — Perform **T1** from JDI's `reference/tracker.md`. If the user
   already gave an issue ID or URL, use it. Otherwise, if the work is tracked, ask whether they
   want to give an existing issue, create a new one now, or continue without one. **Never create an
   issue without explicit confirmation.**

4. **Create the issue, if asked** — Perform **T3**: ask for the project, defaulting to
   `tracker.project`, and the team, defaulting to `tracker.team`. Create it only if the tracker
   exposes issue creation in this session. If it does not, say so and ask whether to continue
   without an issue or to have the user create one and hand back the ID. List any label or field
   values before setting them — never invent one.

5. **Fetch the issue context** — Perform **T2** and read the issue's details to enrich your
   understanding. With no integration, continue on the metadata the user provided.

6. **Derive a slug, establish the base commit, and create the feature branch (freshness gate)** —
   Build a short kebab-case slug from the task description, prefixed with the normalised issue ID
   when there is one.

   Before delegating to anything, in the repository the work targets: run `git fetch origin
   --prune`, then report the current branch, its divergence from the default branch
   (`git rev-list --left-right --count origin/<default>...HEAD`), and whether the tree is clean.
   Resolve `<default>` from `git.default_branch`, detecting it with
   `git symbolic-ref refs/remotes/origin/HEAD` when that is `auto`.

   Then **create the feature branch now, at prep time** — not later at implementation time — so the
   plan is committable and the work can be paused (see step 17). Read the current branch with
   `git branch --show-current`; **an empty result means detached HEAD** and counts as "not on a
   feature branch". If the current branch does not already name this work:

   ```sh
   git switch -c <branch-name> origin/<default-branch>
   ```

   Branch **from `origin/<default>`, never from a stale HEAD** — a checkout is routinely tens of
   commits behind, and branching off it produces a pull request diff full of other people's
   commits. Build `<branch-name>` with **T6** from `reference/tracker.md`.

   Then perform **T4** and move the issue to **In Progress**, resolving the state by listing the
   tracker's workflow states rather than hardcoding an ID. Leave it alone if it is already In
   Progress or later; skip entirely when there is no issue.

   Record the base commit SHA in `PLAN.md`'s metadata so a later reconciliation can tell what the
   plan was written against. **Research and planning citations are only valid against the commit
   they were produced from.** A reconciliation after a base-commit change must re-verify every
   `file:line` in the plan — **including `## References`**, not only the sections being rewritten.

7. **Create the plan** — Create `PLAN.md` for the new plan, per JDI's `reference/plan-store.md`
   (under `<plans.path>/<slug>/` in `repo` mode; in `plans.location` via the service's own tools in
   `external` mode). In `repo` mode, **run `git check-ignore -q <plans.path>` first** — a gitignored
   plans folder loses the plan silently. Stop and tell the user if it is ignored.

   ```
   # <Title>

   - Tracker: <tracker name, or none>
   - Project: <project name, or none>
   - Issue: <issue id, or none>
   - Issue URL: <url, or none>
   - Created: YYYY-MM-DD
   - Base commit: <default-branch ref> @ <SHA>
   - Summary: <one line>

   ## References

   ## Implementation Plan

   ## Testing Strategy

   ## Risks

   ## Tasks
   ```

   Leave the sections empty for now.

8. **Delegate to the Researcher** — Hand off to the **Researcher** role at the **deep** tier; see
   JDI's `reference/delegation.md`, and adopt the role inline if this harness has no subagents.
   Give it the task description from `PLAN.md`, the `docs.path`, the plan store location, and the
   `consumers` list. Instruct it to return:
   - related past plans
   - relevant docs
   - key code findings, with citations
   - recommended references to add to `PLAN.md`
   - whether a missing architecture document should be drafted

9. **Update the references** — Merge the findings into `## References`, preserving anything useful
   that is already there. **Spot-check a couple of the load-bearing `file:line` citations against
   the real files before writing them in** — a plan built on a hallucinated reference misleads
   every later step.

10. **Draft a missing architecture doc when one is needed** — If no useful architecture doc exists,
    do not stop just to ask permission. Delegate to the **Researcher** again at the **deep** tier,
    have it draft a suitable architecture document, write that draft to `<docs.path>/` with a
    descriptive filename, and add it to `## References`. Stop only if a real ambiguity prevents a
    reasonable draft. An architecture doc goes in the repository and is committed with the code, in
    both plan-store modes.

11. **Record the findings on the issue (durable memory)** — Once `## References` is populated,
    perform **T5** from `reference/tracker.md`: upsert the research-findings comment on the issue.
    The issue is the durable record; the plan folder is not. Skip and say so when `Issue: none`;
    warn but do not fail if the tracker is unreachable.

12. **Clarify only the true ambiguities** — If something important about the scope, the behaviour,
    or the constraints is still unclear, ask before planning. **Do not ask for approval to
    continue.** Ask only what materially changes the output; for the rest, pick the obvious default
    and say which one you picked.

13. **Delegate to the Planner** — Hand off to the **Planner** role at the **deep** tier. Pass it the
    current `PLAN.md`, the referenced docs, and the clarified answers. Instruct it to produce:
    - a detailed implementation plan
    - a testing strategy
    - the risks and watchouts
    - open questions, only if the plan cannot be completed safely without them

14. **Resolve any follow-up gaps** — If the Planner returns open questions, ask them and re-run it.

15. **Update `PLAN.md`** — Write the Planner's output into `## Implementation Plan`,
    `## Testing Strategy`, and `## Risks`, preserving the metadata and references.

    When a user decision lands after the Planner returned — a declined step, a follow-up issue now
    filed — **reconcile every mention of it across `PLAN.md` and the task files**: the decisions,
    the steps, the `## Tasks` checklist, and any "file an issue" instruction, which must now name
    the existing issue ID instead of re-instructing creation. A decision recorded in one section and
    contradicted in another is not a blemish; it is an instruction a later agent will follow.

16. **Split into tasks** — Follow `/jdi:split` steps 2 through 4: judge whether splitting is worth
    it, then either write the combined task file plus UAT yourself or delegate to the **Splitter**
    at the **standard** tier. State the decision and the reason. The final task is always UAT, and
    it maps every clause of the issue's acceptance criteria to the scenario or test that proves it.

17. **Present the prepared plan** — Summarise what you created, note which splitting path you took
    (and why, if it was a close call), list the generated tasks, and suggest `/jdi:yolo` as the next
    step.

    Also offer the pause: because the branch was created in step 6, the plan and task files can be
    committed on their own — `docs: Add <slug> plan` — leaving the work resumable later or by
    someone else with nothing implemented. In `external` plan mode there is nothing to commit; say
    instead that the plan is saved in `<plans.service>` and the branch is waiting. **Only commit if
    the user asks; never as a side effect of preparing.**

Do **not** write implementation code. Do **not** stop for approval between phases.
