---
description: "Set up JDI in this repository — write .jdi/config.yml after asking about the issue tracker, where plans live, and where docs live."
argument-hint: "[optional notes about how this repo works]"
---

# JDI: Init

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). No delegation; this is a conversation.

Set JDI up for this repository by writing `.jdi/config.yml`. Additional context from the user:
$ARGUMENTS

The full schema, the defaults, and example tier mappings are in JDI's `reference/config.md` — in
the JDI plugin's own directory (`${CLAUDE_PLUGIN_ROOT}/reference/config.md`). Read it before
asking anything.

Follow these steps:

1. **Check what already exists** — If `.jdi/config.yml` is already here, read it and say what it
   currently records. This becomes an edit, not a fresh write: keep every value the user does not
   change.

2. **Learn what the repo already says about itself** — Read `AGENTS.md`, `CLAUDE.md`, and
   `README.md` if present. Look for a stated issue tracker, a plans or docs folder, branch and
   commit conventions, and sibling repos that consume this one's interfaces. Look at the directory
   listing too: an existing `plans/`, `doc/`, `docs/`, or `architecture/` folder is strong evidence.
   **Propose what you found rather than asking from zero** — the user should be confirming, not
   dictating.

3. **Ask about the issue tracker** — Which tracker, if any, tracks work in this repo: Linear, Jira,
   GitHub Issues, something else, or none. Then, unless it is `none`:
   - the default project or board for new issues
   - the team or workspace it belongs to
   - the issue key prefix (`ENG` for `ENG-1234`), which JDI uses to build plan slugs and to
     recognise whether a branch already names the issue

   Check which trackers actually have a reachable integration in this session and say so — a
   configured tracker with no integration still works, JDI just degrades to the metadata the user
   types by hand.

4. **Ask where plans should live** — Two modes, from `reference/plan-store.md`:
   - **`repo`** (recommended, the default) — plans are files in this repository, committed with the
     code they describe. Ask for the folder; default `plans`.
   - **`external`** — plans live in a note service (Obsidian, recuerd0, Notion, a wiki). Ask which
     service and which vault, notebook, or parent page. Nothing plan-shaped is committed to the
     repo in this mode.

   **If the answer is `repo`, run `git check-ignore -q <path>` on the chosen folder.** A gitignored
   plans folder is the trap worth catching now: the files land on disk, `git status` never mentions
   them, and the plan is silently gone on a fresh clone. If it is ignored, say so plainly and offer
   to un-ignore it, pick a different folder, or switch to `external`.

5. **Ask where architecture docs live** — The folder `/jdi:research` reads from and writes new
   architecture documents into. Default `doc`; propose whatever step 2 found.

6. **Ask about model tiers — optional, and say that it is optional** — JDI runs three tiers: `deep`
   (research, planning, implementation, review), `standard` (splitting, condensing, PR writing), and
   `fast` (orchestration, status, commits). Offer to map them to concrete models for whatever
   harness and provider the user runs, and make clear that leaving them empty is fully supported:
   every tier then runs on the session's own model and nothing about the workflow changes.

7. **Ask about consumers — optional** — Sibling repositories or client codebases that consume this
   repo's public interfaces (APIs, webhooks, published packages, tool surfaces). The Researcher
   sweeps these when a change alters an externally-consumed contract. Skip if there are none.

8. **Write `.jdi/config.yml`** — Write the file with the answers, keeping the schema's comments so
   the next reader can edit it by hand. Omit optional blocks the user skipped rather than writing
   empty scaffolding.

9. **Offer to record the branch and commit conventions where they belong** — JDI deliberately does
   **not** configure branch naming or commit message format: it reads them from the repo's own
   `CLAUDE.md` / `AGENTS.md`, which is where a team already writes them down. If neither file states
   them and the user told you what they are, offer to add them there. Do not write to those files
   without saying you are about to.

10. **Report and point at the next step** — Show the config you wrote, name anything you deliberately
    left unset, and suggest `/jdi:prep "<the first thing they want to build>"` — or `/jdi:help` for
    the tour.
