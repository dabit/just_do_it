---
description: "Clarify the ambiguities, then write the implementation plan on top of the research."
argument-hint: "[plan slug]"
---

# JDI: Plan

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). **Delegates to: Planner** (deep).

Write the implementation plan from the research and context gathered so far.

Follow these steps:

0. **Load the JDI config** — Read `.jdi/config.yml` at the repository root; fall back to defaults
   in `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory — `${CLAUDE_PLUGIN_ROOT}/reference/config.md`,
   or, if that variable does not resolve, `reference/` one level up from this command file).

1. **Find the plan** — Locate the plan matching `$ARGUMENTS`, or the most recent one, per JDI's
   `reference/plan-store.md`. Read `PLAN.md`.

2. **Confirm the feature branch, then mark the issue In Progress** — `/jdi:start` (step 3) and
   `/jdi:prep` (step 6) create the branch before the plan folder exists, so it should already be
   here. Verify it; create it only as a fallback for a plan that predates that behaviour.

   Read the current branch with `git branch --show-current`. **An empty result means detached
   HEAD** and counts as "not on a feature branch". If the branch does not name this work (match the
   issue ID case-insensitively when there is one, otherwise the slug):

   ```sh
   git fetch origin
   git switch -c <branch-name> origin/<default-branch>
   ```

   Branch **from `origin/<default>`, not from the current HEAD** — branching off a stale HEAD is
   what produces a pull request diff full of other people's changes. Build `<branch-name>` with
   **T6** from JDI's `reference/tracker.md`.

   With the branch in place, perform **T4** and move the issue to **In Progress**. Resolve the
   destination state by listing the tracker's workflow states, never by hardcoding a name or an ID.
   Leave it alone if it is already In Progress or later. Skip entirely — and say so — when there is
   no issue or no tracker.

3. **Check for research** — Does `PLAN.md` have a `## References` section? If there are **no
   references**, tell the user no research has been done and ask whether to proceed without it or
   run `/jdi:research` first. Do not continue until they confirm.

4. **Clarify the scope** — Unless the task description already settles it, ask which layers of the
   system this change covers — the API, the client, the data layer, the background work, more than
   one of them. This determines how wide the plan has to reach. Read the repo's `AGENTS.md` /
   `CLAUDE.md` for what its layers actually are rather than assuming a stack.

5. **Clarify the ambiguities** — If anything about the task is unclear, ambiguous, or has more than
   one reasonable approach, ask before planning:
   - *Scope*: "Should this apply to every workspace, or only the current one?"
   - *Behaviour*: "What should happen when X edge case occurs?"
   - *Approach*: "There are two ways to do this — A or B. Which do you prefer?"
   - *Dependencies*: "This touches feature X — handle that here, or separately?"

   **Do not guess or assume.** Get clarity first, then plan. Ask only what materially changes the
   output; for the rest, pick the obvious default and say which one you picked.

6. **Delegate to the Planner** — Once the ambiguities are resolved, hand off to the **Planner** role
   at the **deep** tier; see JDI's `reference/delegation.md`, and adopt the role inline if this
   harness has no subagents. Pass it:
   - the full `PLAN.md` content, including the references
   - the referenced architecture docs
   - the user's answers to the clarifying questions

   Instruct it to produce a detailed implementation plan with:
   - a numbered list of implementation steps, each naming the files to create or modify and the
     approach and key decisions
   - any migrations, background jobs, or infrastructure changes needed
   - a testing strategy: what to add, what to update
   - the risks and things to watch out for

7. **Update `PLAN.md`** — Write the Planner's output into `## Implementation Plan`,
   `## Testing Strategy`, and `## Risks`, preserving the metadata and references above them.

   When a user decision lands after the Planner returned — a declined step, a follow-up issue now
   filed — **reconcile every mention of it across the whole plan**: the decisions, the steps, the
   task checklist, and any "file an issue" instruction, which must now name the existing issue ID
   instead of re-instructing creation. A decision recorded in one section and contradicted in
   another is not a blemish; it is an instruction a later agent will follow.

8. **Present the plan** — Show it to the user and wait for approval before any code is written.
   Suggest `/jdi:split` as the next step.

   Also offer the pause: the branch already exists, so the plan can be committed on its own —
   `docs: Add <slug> plan` — leaving the work resumable with nothing implemented. In `external`
   plan mode, say instead that the plan is saved in `<plans.service>`. **Only commit if the user
   asks.**

Do **not** write any code yet. The goal of this command is alignment on the approach.
