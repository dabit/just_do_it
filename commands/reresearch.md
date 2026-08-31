---
description: "Throw the existing research away and look again from scratch."
argument-hint: "[plan slug]"
---

# JDI: Re-Research

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). **Delegates to: Researcher** (deep).

Re-run research from scratch, even though research has already been done. This forces a fresh look
at the codebase and the docs — use it when the tree has moved, when the scope has changed, or when
the first pass does not survive scrutiny.

Follow `/jdi:research` in full, with three differences:

1. **Do not skip because references already exist.** The point of this command is to replace them.

2. **The freshness gate matters more here, not less.** Re-research is usually triggered by the tree
   having moved. Run `git fetch origin --prune` and compare HEAD against the default branch. Record
   the new base commit in `PLAN.md`'s metadata, and if it differs from the one already recorded,
   say so and treat **every** existing citation in the plan as stale until re-verified — including
   those under `## References`, not only the sections being rewritten.

3. **Replace, do not append.** Write the new findings over the existing `## References` section
   rather than adding a second set beside it. Two generations of references in one plan is worse
   than either alone: a later reader cannot tell which was checked against which commit.

   Where the new research **contradicts** the old, say so explicitly to the user before overwriting
   — a contradiction between two passes is a finding in its own right, and it is often the reason
   the re-run was asked for. Carry it into the plan's `## Risks` if it changes the approach.

Then, as in `/jdi:research`, upsert the research-findings comment on the issue (**T5** in JDI's
`reference/tracker.md`). The write is idempotent by design: the re-run updates the same comment, so
the issue carries the current findings rather than an archaeological record.

Finish by suggesting `/jdi:replan` — a plan built on the old research is now suspect, and re-running
research without re-running planning leaves the two out of step.
