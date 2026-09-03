---
description: "Set up JDI in this repository — write .jdi/config.yml after asking about the issue tracker, what the split pieces become, whether the Executor writes tests first, which two agents pair, and where plans and docs live."
argument-hint: "[optional notes about how this repo works]"
---

# JDI: Init

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). No delegation; this is a conversation.

Set JDI up for this repository by writing `.jdi/config.yml`. Additional context from the user:
$ARGUMENTS

The full schema, the defaults, and example tier mappings are in JDI's `reference/config.md` — in the
JDI plugin's own directory (`${CLAUDE_PLUGIN_ROOT}/reference/config.md`, or, if that variable does
not resolve, `reference/` one level up from this command file). Read it before asking anything.

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

4. **Ask what the split pieces should become — only if the tracker is not `none`** — When
   `/jdi:split` breaks a plan into pieces, those pieces are always task files that each land as
   their own commit. Ask whether they should *also* be mirrored into the tracker:
   - **`commits`** (the default) — nothing is written to the tracker. Recommend it unless the user
     wants the breakdown visible to people who never open the repository.
   - **`tasks`** — each piece becomes a task or checklist item on the issue, where the tracker has
     such a thing. Say plainly whether the configured tracker does: Linear has no first-class issue
     checklist, Jira's is an add-on, GitHub Issues has task lists in the issue body. Where it does
     not, this setting falls back to `commits` at split time, out loud.
   - **`subtickets`** — each piece becomes a child issue of the plan's issue (Linear sub-issue,
     Jira sub-task, GitHub sub-issue). Mention that this creates issues, one per task, and that
     `/jdi:split` will still ask before it does.

   Skip this question entirely when the tracker is `none` — there is nothing to mirror onto — and
   write `commits`.

5. **Ask whether the Executor should write tests first** — Off by default, and off means nothing
   changes: the Executor writes tests and implementation in whatever order the task calls for, and
   no command says a word about TDD while a plan runs — not even that it is off. Ask whether they
   want it on (`tdd.enabled`).

   On a yes, **propose `tdd.test_instructions` rather than asking from zero** — a test script in the
   manifest, a Makefile or `just` target, a `bin/` wrapper, a devcontainer or compose service the
   README names, or whatever step 2 already read that says how tests are run here. Say plainly that
   the value is **prose a later agent reads and translates into an invocation**, not a command JDI
   executes: "run `bin/rails test` inside the devcontainer" is a *better* answer than a bare
   `bin/rails test`, because the real invocation depends on a container, a service, or a working
   directory that a bare command string cannot carry.

   **Then actually try it once**, scoped as narrowly as the runner allows — one file or one
   directory, seconds rather than a full suite. This is step 3's integration check pointed at a test
   runner: prove the capability, do not record an aspiration. **Read the output, not the exit
   code.** Proof is a printed test-result tally — the runner reached the point of counting tests and
   said so, and "ran 0 tests" in a repository that has none yet is still proof that the runner runs.
   A command not found, a missing interpreter, a dependency-resolution error, an unreachable
   container, a timeout, or a prompt waiting for input is not proof, whatever it exited with. Say
   which invocation you tried and what it printed.

   **If it did not run, say so and record the setting anyway** when that is still what the user
   wants. The config records the intent; the Butler re-checks it once per plan, and a runner it
   cannot prove degrades that plan to off out loud rather than fabricating evidence. Writing the
   setting down before the environment is fixed loses nothing.

   Ask this question every time. Unlike the split pieces, TDD does not depend on a tracker, so there
   is no configuration in which it is skipped.

6. **Ask which two agents should pair — only if `herdr` is on `PATH`** — `/jdi:pair` runs a plan as
   two agents ping-ponging a failing test in two Herdr panes (`reference/pairing.md`). **There is no
   on/off switch.** `pair.agents` never says *whether* to pair — running `/jdi:pair` is the whole of
   the intent — it only names *which* two agents to pair when that command is run. A repository that
   fills the block in and never runs the command behaves exactly like one that leaves it empty, and
   no other command reads it.

   **Propose kinds rather than asking from zero**, and offer only kinds that stand a chance of
   clearing all three of P1's layers (`reference/pairing.md`, rung 4): the kind is in the list
   `herdr agent` prints, Herdr can classify its lifecycle state, and it resolves under `command -v`.
   All three are answerable here and now, and layer 2 is the one most easily got wrong: it asks
   whether Herdr can **classify** the kind's lifecycle state, not whether an integration is
   current. `herdr agent explain --file <any path> --agent <kind> --verbose` answers it with no
   pane running. An outdated integration is a warning, not a refusal — say the version gap and
   carry on. Asking the wrong question here makes `/jdi:init` propose a narrower set than
   `/jdi:pair` would accept on the same machine, which is worse than not proposing at all.

   **Name the environment you measured in** — the `PATH` layer is the one most likely to differ
   between this shell and the machine the plan later runs on. **Do not probe with a bare `herdr`**:
   that launches or attaches the TUI and takes over the terminal you are speaking through. Print the
   command group instead.

   This is step 5's prove-the-capability check pointed at a multiplexer, with one difference worth
   saying out loud: `/jdi:pair` re-runs every layer in full on every invocation, because an agent
   name is a handle on a live process and panes never survive a session. Nothing written here is
   inherited as evidence — it only spares `/jdi:pair` the question. So a kind that fails a layer
   today is still worth recording if that is what the user wants: say the failure out loud at the
   time, and say that it will fail again here on the next run.

   Say plainly that the value is **prose a later agent reads and translates**, exactly as
   `tdd.test_instructions` is: "claude and opencode, both started in this repository" is the shape,
   not a list JDI parses and not a command it executes.

   Skip this question entirely when `herdr` is not on `PATH` — there is no multiplexer here to pair
   in, so every answer would be unusable. Say once that `/jdi:pair` asks which two agents to pair
   inline when it is actually needed, and offers to persist the answer then, and write no `pair`
   block.

7. **Ask where plans should live** — Two modes, from `reference/plan-store.md`:
   - **`repo`** (recommended, the default) — plans are files in this repository, committed with the
     code they describe. Ask for the folder; default `plans`.
   - **`external`** — plans live in a note service (Obsidian, recuerd0, Notion, a wiki). Ask which
     service and which vault, notebook, or parent page. Nothing plan-shaped is committed to the
     repo in this mode.

   **If the answer is `repo`, run `git check-ignore -q <path>` on the chosen folder.** A gitignored
   plans folder is the trap worth catching now: the files land on disk, `git status` never mentions
   them, and the plan is silently gone on a fresh clone. If it is ignored, say so plainly and offer
   to un-ignore it, pick a different folder, or switch to `external`.

8. **Ask where architecture docs live** — The folder `/jdi:research` reads from and writes new
   architecture documents into. Default `doc`; propose whatever step 2 found.

9. **Ask about model tiers — optional, and say that it is optional** — JDI runs three tiers: `deep`
   (research, planning, implementation, review), `standard` (splitting, condensing, PR writing), and
   `fast` (orchestration, status, commits). Offer to map them to concrete models for whatever
   harness and provider the user runs, and make clear that leaving them empty is fully supported:
   every tier then runs on the session's own model and nothing about the workflow changes.

10. **Ask about consumers — optional** — Sibling repositories or client codebases that consume this
    repo's public interfaces (APIs, webhooks, published packages, tool surfaces). The Researcher
    sweeps these when a change alters an externally-consumed contract. Skip if there are none.

11. **Write `.jdi/config.yml`** — Write the file with the answers, keeping the schema's comments so
    the next reader can edit it by hand. Omit optional blocks the user skipped rather than writing
    empty scaffolding.

12. **Offer to record the branch and commit conventions where they belong** — JDI deliberately does
    **not** configure branch naming or commit message format: it reads them from the repo's own
    `CLAUDE.md` / `AGENTS.md`, which is where a team already writes them down. If neither file
    states them and the user told you what they are, offer to add them there. Do not write to those
    files without saying you are about to.

13. **Report and point at the next step** — Show the config you wrote, name anything you
    deliberately left unset, and suggest `/jdi:prep "<the first thing they want to build>"` — or
    `/jdi:help` for the tour.
