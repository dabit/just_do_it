---
description: "Find or create the architecture documentation for the area about to change, and record the findings on the issue."
argument-hint: "[plan slug]"
---

# JDI: Research

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). **Delegates to: Researcher** (deep).

Find or create architecture documentation for the area we are about to change.

Follow these steps:

0. **Load the JDI config** — Read `.jdi/config.yml` at the repository root; fall back to defaults
   in `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory — `${CLAUDE_PLUGIN_ROOT}/reference/config.md`,
   or, if that variable does not resolve, `reference/` one level up from this command file).
   Everything below refers to `tracker`, `plans`, `docs`, and `consumers` from that config.

1. **Find the plan** — Locate the plan matching `$ARGUMENTS`, or the most recent one, per JDI's
   `reference/plan-store.md`. Read `PLAN.md` to understand what we are working on. If several plans
   are plausible, ask rather than guess.

2. **Confirm the base commit is current (freshness gate)** — Before delegating: run
   `git fetch origin --prune`, then compare HEAD against the default branch
   (`git rev-list --left-right --count origin/<default>...HEAD`). **If HEAD is behind, stop and
   re-base the work on `origin/<default>` before researching** — a Researcher is only as accurate
   as the tree it reads, and every `file:line` it returns is silently wrong on a stale checkout.

   Record the base commit in `PLAN.md`'s metadata. If the plan already records one and it no longer
   matches HEAD, say so, and treat **every** existing citation as needing re-verification against
   the new base — including those under `## References`, not only the sections being rewritten.

3. **Delegate to the Researcher** — Hand off to the **Researcher** role at the **deep** tier; see
   JDI's `reference/delegation.md` for how to delegate under this harness, and adopt the role
   inline if it has no subagents. Give it the task description from `PLAN.md`, the `docs.path`, the
   plan store location, and the `consumers` list, and instruct it to:

   a. **Search for past plans** — Search the plan store for previous plans that touched the same
      area or a related feature. Read their `PLAN.md` files and note the relevant ones.

   b. **Search for existing docs** — Search `<docs.path>` for architecture or design documents
      covering the area being changed.

   c. **Report findings** — Return relevant past plans, relevant docs, key code findings with
      citations, and whether an architecture doc exists for this area.

4. **Present the findings** — Show the user what the Researcher found. **Sanity-check it yourself
   first:** spot-check a couple of the load-bearing `file:line` citations against the real files
   rather than relaying them unverified. A plan built on a hallucinated reference misleads every
   later step.
   - Add relevant past plans to `PLAN.md` under `## References`.
   - Summarise the key points of any relevant architecture doc and reference it from `PLAN.md`.
   - If **no relevant doc exists**, tell the user and ask whether to write one.

5. **Write the missing doc (if approved)** — If the user agrees, delegate to the **Researcher**
   again at the **deep** tier to explore the codebase and understand the current architecture:
   - the key data models and their relationships
   - the important controllers, services, handlers, or use cases involved
   - how data flows through the system
   - any relevant background work, queues, or integrations

   Write the result to `<docs.path>/` with a descriptive filename (`architecture-<area>.md`) and
   add it to `## References`. **An architecture doc is not a plan** — it goes in the repository and
   is committed with the code, in both plan-store modes.

6. **Record the findings on the issue (durable memory)** — Perform **T5** from JDI's
   `reference/tracker.md`: upsert a comment on the issue whose first line is exactly
   `tracker.research_comment_heading`, carrying the findings just added to `PLAN.md` — past plans,
   related docs, key files, compatibility and gotcha notes, and a link to any architecture doc from
   step 5. The write is idempotent: update the existing comment if one is already there, so
   re-running research refreshes the record instead of stacking duplicates.

   The issue is the durable record; a local plan folder is not. Skip and say so when `Issue: none`
   or no tracker is configured — a missing issue must never block the workflow. Warn but do not
   fail if the tracker is unreachable, and note that the findings still live in `PLAN.md`.

7. **Suggest the next step** — Tell the user research is done and suggest `/jdi:plan`.

   If they want to stop here, offer to commit what the research produced — the updated `PLAN.md`
   and any new architecture doc — as `docs: Add <slug> research`. The branch already exists
   (`/jdi:start` step 3), so this is a real pause point: the findings survive on the branch instead
   of living only in an untracked working tree. In `external` plan mode, only the architecture doc
   is committable; say that the plan itself is saved in `<plans.service>`. **Offer it; never commit
   as a side effect of researching.**
