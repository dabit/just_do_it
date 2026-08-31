---
description: "Kick off a new JDI task — create the feature branch and the initial plan, optionally linked to an issue."
argument-hint: "<what you are about to build>"
---

# JDI: Start

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). No delegation.

You are kicking off a new task. The user wants to work on: $ARGUMENTS

Follow these steps:

0. **Load the JDI config** — Read `.jdi/config.yml` at the repository root; fall back to defaults
   recorded in `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory — `${CLAUDE_PLUGIN_ROOT}/reference/config.md`,
   or, if that variable does not resolve, `reference/` one level up from this command file).
   Everything below refers to `tracker`, `plans`, `docs`, and `git` from that config. If no config
   exists anywhere, say so once and ask only the questions this command actually needs; suggest
   `/jdi:init` at the end.

1. **Identify the issue** — Perform **T1** from JDI's `reference/tracker.md`: ask whether there is
   an issue for this work, and use it if the user names one. If a tracker is configured and the
   user gives an ID or URL, perform **T2** and fetch the issue's details to enrich your
   understanding. No issue is a perfectly good answer — say you are proceeding without one and move
   on. `tracker.name: none` skips this step entirely; say so.

2. **Derive a slug** — Build a short kebab-case slug from the task description. If there is an
   issue, prefix it with the normalised issue ID (`eng-123-add-presence-indicators`). If not, use
   the description alone (`add-presence-indicators`).

3. **Establish the base commit and create the feature branch (freshness gate)** — Before anything
   is written, in the repository the work targets: run `git fetch origin --prune`, then report the
   current branch, its divergence from the default branch
   (`git rev-list --left-right --count origin/<default>...HEAD`), and whether the tree is clean.
   Resolve `<default>` from `git.default_branch`, or detect it with
   `git symbolic-ref refs/remotes/origin/HEAD` when that is `auto`.

   Then **create the feature branch here**, before the plan exists. Everything the later phases
   produce — the plan folder, a new architecture doc — then lands somewhere committable, so the
   work can be paused or handed off at any phase rather than only after planning.

   Read the current branch with `git branch --show-current`. **An empty result means detached
   HEAD** — common in a submodule or a bare checkout — and counts as "not on a feature branch". If
   the current branch does not already name this work:

   ```sh
   git switch -c <branch-name> origin/<default-branch>
   ```

   Branch **from `origin/<default>`, never from a stale HEAD.** A checkout is routinely tens of
   commits behind, and branching off it produces a pull request diff full of other people's
   commits. Build `<branch-name>` with **T6** from `reference/tracker.md`: the tracker's own
   suggestion when it offers one, otherwise the slug, with whatever prefix convention the repo's
   `CLAUDE.md` or `git.branch_prefix` prescribes.

   Do **not** move the issue to In Progress here. Creating a plan folder is not yet work anyone is
   waiting on; that transition belongs with planning (`/jdi:plan` step 2), so the board does not
   claim progress on work that has only been named.

4. **Create the plan** — Create `PLAN.md` for the new plan, per JDI's `reference/plan-store.md`
   (under `<plans.path>/<slug>/` in `repo` mode; in `plans.location` via the service's own tools in
   `external` mode). In `repo` mode, **check `git check-ignore -q <plans.path>` first** — a
   gitignored plans folder loses the plan silently. Stop and tell the user if it is ignored.

   ```
   # <Title>

   - Tracker: <tracker name, or none>
   - Project: <project name, or none>
   - Issue: <issue id, or none>
   - Issue URL: <url, or none>
   - Created: YYYY-MM-DD
   - Base commit: <default-branch ref> @ <SHA from step 3>
   - Summary: <one line>
   ```

   The plan is intentionally minimal at this stage — the details come later. The base commit
   matters: everything the later phases cite is only valid against the commit it was read from.

5. **Suggest the next step** — Tell the user the plan is ready, name the branch you created, and
   suggest `/jdi:research` to find or write the architecture docs for this area.

   If they want to stop here, offer to commit the plan on its own — `docs: Add <slug> plan` — so
   the work is resumable later or by someone else. In `external` plan mode there is nothing to
   commit; say instead that the plan is saved in `<plans.service>` and the branch is waiting.
   **Offer it; never commit as a side effect of starting.**
