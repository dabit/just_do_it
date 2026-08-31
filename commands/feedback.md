---
description: "Critique the latest output on demand — verdict, output fixes, and proposed prompt improvements."
argument-hint: "[what to review, e.g. \"the plan\", \"the last diff\", \"the researcher's prompt\"]"
---

# JDI: Feedback

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). **Delegates to: Feedbacker** (deep).

Have the Feedbacker — JDI's standing quality authority — critique an output on demand.

**This is the only way the Feedbacker runs.** It is not wired into the producing commands as an
automatic gate. Use it deliberately: to review the latest output, to review a named one, or to audit
a role's prompt directly.

Follow these steps:

0. **Load the JDI config** — Read `.jdi/config.yml` at the repository root; fall back to defaults in
   `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory — `${CLAUDE_PLUGIN_ROOT}/reference/config.md`).

1. **Determine what to review** — If `$ARGUMENTS` names an output, a role, or a plan ("the plan",
   "the last diff", "the researcher's prompt"), target that. Otherwise default to the most recent
   producing-role output in this session: the research findings, the plan, the task split, the
   latest execution diff, or the PR content.

2. **Find the plan** — Locate the plan matching `$ARGUMENTS`, or the most recent one, per JDI's
   `reference/plan-store.md`. Read `PLAN.md` for context.

3. **Delegate to the Feedbacker** — Hand off to the **Feedbacker** role at the **deep** tier; see
   JDI's `reference/delegation.md`, and adopt the role inline if this harness has no subagents.
   Where the config maps more than one model, **pick a different model from the one that produced
   the output** — a model reviewing its own work confirms it. If only one is available, run the
   review anyway and say that producer and reviewer were the same model.

   Pass it:
   - the output under review
   - which role produced it, and that role's definition file
   - the driving command file, `PLAN.md`, and any referenced docs

   Instruct it to return a verdict — **pass** or **needs work** — the specific gaps, and, when
   relevant, both an **output fix** (re-run instructions for the producing role) and a **prompt
   fix** (before → after edits to the responsible role or command).

   Run the review and consume its verdict in the same active turn where practical. A background
   delegation left running across an idle wait does not survive a harness restart and is silently
   orphaned; if it does not return promptly, run the review inline yourself, say the fallback ran,
   and proceed.

4. **Present the verdict** — Show the user:
   - the verdict and the reasoning
   - on **needs work**: the output-fix instructions, and an offer to re-run the producing role to
     correct this output — one re-run, then hand back to the user
   - any proposed prompt edits, before → after, for the user to approve

   **Do not edit role or command files without explicit sign-off.** A prompt is a shared
   abstraction: a fix that helps this plan may cost every other one.

5. **Apply only what is approved** —
   - An approved **output re-run**: hand the fix instructions back to the producing role, re-run it,
     and review the result.
   - An approved **prompt fix**: JDI's role and command files ship inside the installed plugin,
     which for most harnesses is a read-only cache that the next update overwrites. Apply the edit
     to the **JDI source repository** — the checkout the plugin was installed from — not to the
     installed copy. If the user does not have that checkout available, hand them the exact
     before → after diff and the file's path within the plugin, and say where it needs to land.
   - A fix that is specific to **this** repository — a convention only this team follows — does not
     belong in JDI at all. Offer it for the repo's own `CLAUDE.md` / `AGENTS.md` instead.
