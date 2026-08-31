---
description: "Condense the plan, push the branch, and open the pull request."
argument-hint: "[plan slug]"
---

# JDI: PR

**Role: Butler** — JDI's orchestrator (`roles/butler.md`).
**Delegates to: Synthesizer** (standard), **PR Writer** (standard).

Create a pull request for the current plan.

Follow these steps:

0. **Load the JDI config** — Read `.jdi/config.yml` at the repository root; fall back to defaults
   in `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory — `${CLAUDE_PLUGIN_ROOT}/reference/config.md`,
   or, if that variable does not resolve, `reference/` one level up from this command file).

1. **Find the plan** — Locate the plan matching `$ARGUMENTS`, or the most recent one, per JDI's
   `reference/plan-store.md`. Read `PLAN.md` for the full scope and the issue reference.

2. **Reconcile the UAT status** — If the UAT task is still unchecked, ask the user whether UAT
   actually ran. **Mark it done only on confirmation.** If it has not run — common when the PR ships
   code whose enablement is a later operational step — leave it not-done, and instruct the
   Synthesizer to carry the outstanding procedure into the condensed `PLAN.md` under a
   **Remaining work** section **exempt from the compression target**, since deleting the task files
   makes the plan its only home. **Never record UAT as done by inference from "a PR is being
   opened."**

3. **Verify completeness** — Check that every task is marked done. If any non-UAT task is still
   pending, warn the user and ask whether to proceed anyway.

4. **Confirm the feature branch** — It should already exist: `/jdi:start` and `/jdi:prep` create it
   before the plan folder, and `/jdi:plan` confirms it. Verify you are on it and not on detached
   HEAD. Only if there is no feature branch — an older plan, or a flow that skipped planning —
   create one now from `origin/<default>` using the plan slug, following the repo's branch
   conventions, and **note in the report that the branch was created late**, since any commits made
   before this point landed somewhere else.

5. **Condense the plan into a single file** — The per-task files have served their purpose during
   execution; collapse them so the plan folder stops bloating the repository at HEAD. Hand off to
   the **Synthesizer** role at the **standard** tier; see JDI's `reference/delegation.md`, and adopt
   the role inline if this harness has no subagents. Pass it:
   - the current `PLAN.md`
   - every numbered task file, including UAT
   - the git log since the branch diverged (`git log --oneline origin/<default>..HEAD`)

   Instruct it to produce a single condensed `PLAN.md` that **preserves** the metadata, the
   references (paths only — git history has the line numbers), the **decisions** (anything that
   deviates from the obvious approach: infrastructure kept deliberately with its rationale, scope
   deferred to a later phase, plan gaps caught during execution), the **outcome** (what shipped,
   what is deferred and under which issue), and the **test result** — which may state only what the
   source files record. It must never add or strengthen a coverage claim, and never contradict a
   preserved plan gap.

   And **drops** the per-task Why / Description / Files / Verification sections, the step-by-step
   verification commands (now in git history), the suggested per-task commit messages, the
   status and dependency boilerplate, the verbose batch-ordering rationale (keep the *result*, not
   the *process*), and the `## Tasks` checklist — the commits are the task list now.

   The condensed plan should typically be **70–80% smaller**. If it is not, the synthesis kept too
   much: push back and ask for a harder cut.

   Then:
   - Write the condensed content over `PLAN.md`.
   - Delete every numbered task file in the plan folder (`rm <plans.path>/<slug>/[0-9]*-*.md`).
   - Stage the rewritten `PLAN.md` and all the deletions.

   **In `external` plan mode:** the condensation still happens — rewrite the plan document in place
   in the service and delete or archive the task documents there — but there is nothing to stage
   and nothing to commit. The pull request body then carries the decisions and the outcome, because
   it is the only place a reviewer will see them. Skip step 6 entirely.

6. **Commit the synthesis** — Make a new commit on the feature branch:
   `docs: Condense <slug> plan into single file`. **Do not amend the earlier commits** — the
   per-task commits stay as they are for bisectability; only HEAD carries the slim plan folder.

7. **Push** — Push the branch to the remote with `-u`.

8. **Delegate to the PR Writer** — Hand off to the **PR Writer** role at the **standard** tier. Pass
   it the condensed `PLAN.md`, the git log since the branch diverged, and the issue reference.
   Instruct it to produce:
   - a PR title following the repo's own conventions (read `CLAUDE.md` / `AGENTS.md` and the recent
     `git log` for the house style)
   - a PR body with a summary, the issue reference if there is one, and the key decisions and scope
     from the condensed plan — which is now the source of truth for what shipped. It must carry the
     plan's open risks and deliberately-untested gaps forward, and verify the per-file list against
     `git diff origin/<default>...HEAD --stat`.

9. **Create the pull request** — Open it with the title and body from the PR Writer. Use whatever
   the repo's forge provides (`gh pr create` for GitHub, `glab mr create` for GitLab, the forge's
   own MCP tools). If nothing is available, print the title and body and tell the user to open it
   by hand.

10. **Move the issue to In Review** — Perform **T4** from JDI's `reference/tracker.md`: transition
    the issue to its **In Review** state now that the pull request is open, resolving the state by
    listing the tracker's workflow states rather than hardcoding a name or an ID, and assign it to
    the PR author if it is unassigned. This mirrors the In Progress transition at the start of the
    work. **Skip gracefully — never fail the command** — when there is no issue, no matching state
    exists, or the tracker is unreachable. Say which of those happened.

11. **Report** — Show the user the pull request URL, and name anything that was skipped: an unrun
    UAT, a tracker transition that did not happen, a task left pending.
