---
description: "Throw the existing implementation plan away and write a fresh one."
argument-hint: "[plan slug]"
---

# JDI: Re-Plan

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). **Delegates to: Planner** (deep).

Re-write the implementation plan from scratch, even though one already exists. This forces a fresh
planning pass — use it when the research has changed, when a decision has been reversed, or when
the existing plan does not survive scrutiny.

Which plan, and anything the user wants changed about it: $ARGUMENTS

Follow `/jdi:plan` in full — including step 0's config load and step 1's plan lookup, which uses the
argument above — with four differences:

1. **The branch and the issue status are already handled.** `/jdi:plan` step 2 creates the branch
   and moves the issue to In Progress. By the time you are re-planning, both have happened. Verify
   them rather than redoing them, and only fix what is actually missing.

2. **Re-ask the clarifying questions rather than reusing the old answers.** A re-plan is usually
   triggered by something the first pass got wrong, and the first pass's answers are exactly what
   is under suspicion. Present what was previously decided, ask what has changed, and let the user
   confirm or revise each one. Do not silently inherit.

3. **Replace, do not append.** Write the new plan over the existing `## Implementation Plan`,
   `## Testing Strategy`, and `## Risks` sections. Preserve the metadata and `## References`
   untouched — unless the research itself is stale, in which case stop and suggest
   `/jdi:reresearch` first.

4. **Reconcile the tasks.** If `## Tasks` already has a checklist, the old task files now describe a
   plan that no longer exists.
   - **No task has been executed yet:** delete the numbered task files and clear the checklist. Say
     that you did. The user re-runs `/jdi:split` on the new plan.
   - **Some tasks are already done:** do **not** delete them — they describe commits that exist.
     List which tasks are complete, state plainly which of them the new plan invalidates, and ask
     the user how to proceed before touching anything. Silently rewriting the plan under completed
     work is how a branch ends up with commits nothing explains.

Do **not** write any code. The goal of this command is a plan the user believes in.
