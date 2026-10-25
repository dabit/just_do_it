---
description: "Just do it — read the code, plan in ten lines, build, verify, open the PR, work the review, and merge."
argument-hint: "<issue id, URL, or a one-line description of the change>"
---

# JDI: Do

**Role: Butler** — JDI's orchestrator (`roles/butler.md`).
**Delegates to:** nobody.

Take one change from request to merged pull request in a single session, without a plan folder,
task files or a stop between phases. The work is `$ARGUMENTS`.

**Why this exists.** `/jdi:prep` → `/jdi:yolo` → `/jdi:pr` writes the plan before anyone has had
the code open, records it in files, and stops at every phase for a go. That is the right cost for a
change that is large, ambiguous or risky. For a change one session can hold in its head, it inverts
the thinking: the implementing session's job becomes compliance with a plan written by someone who
could not see the road, and the record outweighs the change. **The plan belongs to the session that
can see the road**, so here the same session reads, plans, builds and ships, and the plan dies with
the session. The commits, the PR description and the review threads are the record.

**The request is the authorization.** Running this command authorizes the whole path to merge for
the change it names. Do not ask for a go between phases. Stop only for the reasons in step 5.

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

   **Then resolve Jev, once** — If `jev.enabled` is `true`, run the ladder in JDI's
   `reference/jev.md` here and nowhere else, exactly as `/jdi:pr` step 0 does. This command ranks
   nothing of its own; the resolved answer exists so that **T4**'s state lookup can use **J3**.
   **With `jev.enabled` false or absent, say nothing at all** — nothing was skipped.

   **Read the repository's own instructions** — the root `CLAUDE.md` / `AGENTS.md` and the ones for
   the area the change touches. They decide the branch and commit conventions, how a change ships,
   what review it needs, which merge method is allowed, and what the repository names as needing a
   person's sign-off. Every later step defers to them. Where they say an agent may not merge, or
   name a ship script, that wins over this file.

1. **Identify the work** — `$ARGUMENTS` is an issue id, an issue or page URL, or a description.
   Run **T1** and **T2** from JDI's `reference/tracker.md` when it names an issue. Empty arguments:
   ask for the change in one line and stop until it comes. Never create an issue here (**T3** needs
   the user's explicit confirmation, and this command does not ask for one).

   **One slice, never the whole outcome.** The target is one deliverable slice: a single issue, a
   sub-issue, a seam. If it is a container for other work (an epic, a parent with sub-issues, a
   commission whose children are seams), do not build the parent. List its unfinished children in
   one line each, recommend the one to start with, and stop. Building a container in one session is
   the plan that sprawls, and its children already say where the cuts are. A container with no
   children yet is the *too big for one session* stop in step 5: recommend `/jdi:prep`.

2. **Branch** — From a fresh `origin/<default>`, create the feature branch with **T6** and the
   repository's convention. Never work on the default branch, and never push to it. If the current
   branch already carries unrelated work, say so and stop rather than mixing the two. Move the issue
   to In Progress with **T4**.

3. **Read the code — no edits yet** — Open the files the change actually involves, and the tests
   beside them. Read `git log` / `git blame` on code you do not understand. Look in `plans.path` for
   a past plan over the same area, and read its decisions. Do this yourself: the session that reads
   the code is the session that builds it, so this step delegates nothing.

4. **Plan — ten lines in chat, not a document** — Post it in the message body. No plan folder, no
   task files, no tracker comment. Four fields, each at most 60 words:

   - **Change:** what will be different, in one or two sentences, for the person who uses it.
   - **Files:** the files to edit or add.
   - **Proof:** the tests that will show it works, and the check you will run by hand if any.
   - **Stops:** anything in step 5 this change could run into, or `none`.

   With `tdd.enabled` true, run **TS1** from JDI's `reference/testing.md` now and add its `TDD:`
   line as a fifth field. There is no plan file to hold it, so the chat plan is where it is written
   once and read back for the rest of this run. With `tdd.enabled` false or absent, say nothing
   about TDD.

   **Then continue.** The plan is shown, not submitted: do not wait for approval of it.

5. **The only reasons to stop before merge** — Stop, say which one in a sentence, leave a visible
   trace (push the branch, and note it on the issue only if the repository's instructions allow),
   and hand back:

   - **Too big for one session.** The change will not fit one reviewable pull request, or step 3
     turned up a design question with more than one defensible answer. Recommend `/jdi:prep` with
     what you learned. This is the expected exit for large work, not a failure.
   - **A product decision outside the request.** The request does not say how something visible
     should behave, and the code does not settle it either. Ask that one question, offering only
     options whose premise you have read.
   - **A change the repository reserves for a person.** Whatever its own instructions name as
     needing sign-off: commonly CI workflows, deploy configuration, permissions or authorization,
     secrets, destructive migrations, repository settings. Stop at the point the repository names:
     before the edit when it says the edit itself needs sign-off, before merge otherwise.
   - **The review does not converge** (step 9).
   - **The user said to stop** at the PR, or paused shipping.

   Anything else immaterial that is unclear: pick the obvious default, say which one you picked, and
   keep going.

6. **Build** — Implement the plan. Keep the diff to the change: no drive-by refactors, no
   speculative abstraction. Every behaviour change comes with a test that would fail without it;
   where a change has no testable behaviour, say why in one line (and carry that line into the PR
   description in whatever form the repository asks for). With a `TDD:` line from step 4 that says
   on, write the failing test first and show the red run before the green one (**TS2**). Commit in
   small steps with the repository's message convention, and commit by path, never a bare
   `git commit` that takes whatever is staged.

   If the plan turns out wrong, change it: say in one line what changed and why, then carry on. The
   plan exists to be corrected by the code.

7. **Verify** — Run the focused tests while you iterate, then the repository's full local gates
   once the diff settles: tests, type checks, linters, whatever its instructions name. For a UI
   change, run the app and look at it, as the repository's instructions prescribe. A gate that
   cannot run here is not a pass: name it, name what you tried, and leave it to CI out loud.

8. **Open the pull request** — If the repository names a ship script or procedure, use it. Otherwise
   push with `-u` and open the pull request against the default branch. The description says what
   changed and why, how it was verified (including what was not), and links the issue. Move the
   issue to In Review with **T4**.

9. **Work the review to green** — Wait for the required checks and the review the repository relies
   on. Then, for each round:

   - **A failing check:** read its log. Fix a real failure. A failure that does not reproduce and
     touches nothing in the diff may be re-run once; a second failure is real.
   - **Each review thread:** fix it, or answer it with the reason it should stand. Read the code the
     thread is about before judging it. Resolve a thread only when it is fixed or answered.
   - Push, and wait for the review of the new head commit — not the previous one.

   **Bound the loop.** Count rounds. When a round finds nothing new, you are done. When two rounds in
   a row raise threads about your own previous fixes, or the threads are about wording rather than
   behaviour, the loop is not converging: stop and hand back with the open threads listed.

10. **Merge** — When every required check passes on the head commit, and no thread is unresolved,
    merge with a method the repository allows. Read the allowed methods instead of assuming one;
    never use an admin override, and never bypass a required check. Skip this step only for a reason
    in step 5. **Merging is not deploying:** do not start a production rollout unless the
    repository's instructions tell you to.

11. **Close out** — Read the merge back (the PR shows merged, the commit is on the default branch).
    Close or advance the issue as the repository's tracker workflow does when a PR merges; with
    automation that closes it on merge, read the state back rather than writing it. Delete the
    remote branch if the repository does. Then report in a few lines: the PR and its merge commit,
    what changed for the person who uses it, how it was verified, and anything left undone.

**What this command never does:** write a plan folder or task files, delegate the plan, wait for an
approval of its plan, push to the default branch, force-push a branch someone else has pushed to,
merge with a failing or skipped required check, or claim a check passed that it did not watch pass.
