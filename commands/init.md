---
description: "Set up JDI in this repository — write .jdi/config.yml after asking about the issue tracker, what the split pieces become, whether the Executor writes tests first, where plans and docs live, and which model each role runs on."
argument-hint: "[optional notes about how this repo works]"
---

# JDI: Init

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). No delegation; this is a conversation.

Set JDI up for this repository by writing `.jdi/config.yml`. Additional context from the user:
$ARGUMENTS

The full schema, the defaults, and example model mappings are in JDI's `reference/config.md` — in the
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

6. **Ask where plans should live** — Two modes, from `reference/plan-store.md`:
   - **`repo`** (recommended, the default) — plans are files in this repository, committed with the
     code they describe. Ask for the folder; default `plans`.
   - **`external`** — plans live in a note service (Obsidian, recuerd0, Notion, a wiki). Ask which
     service and which vault, notebook, or parent page. Nothing plan-shaped is committed to the
     repo in this mode.

   **If the answer is `repo`, run `git check-ignore -q <path>` on the chosen folder.** A gitignored
   plans folder is the trap worth catching now: the files land on disk, `git status` never mentions
   them, and the plan is silently gone on a fresh clone. If it is ignored, say so plainly and offer
   to un-ignore it, pick a different folder, or switch to `external`.

7. **Ask where architecture docs live** — The folder `/jdi:research` reads from and writes new
   architecture documents into. Default `doc`; propose whatever step 2 found.

8. **Ask which model each role runs on — optional, and say that it is optional** — JDI has seven
   delegatable roles: Researcher, Planner, Splitter, Executor, Synthesizer, PR Writer, and
   Feedbacker. Offer to name a model for each (`models.<role>.model`), **proposing rather than
   asking from zero**: `reference/delegation.md` says what each phase wants from a model, and this
   session already knows what harness it is. Make clear that leaving a role empty — or skipping the
   whole block — is fully supported: that role then runs on the session's own model and nothing
   about the workflow changes.

   **The value is handed to the harness that will run the role, exactly as written**, so write the
   identifier that harness accepts: Claude Code's Agent tool takes an alias (`opus`, `sonnet`,
   `haiku`), while Codex and OpenCode take full identifiers. A model a harness cannot express is
   announced and the role runs on that harness's own default; it is never silently swapped.

   Then ask whether any role should run in a **different agent CLI** (`models.<role>.harness` —
   `claude`, `codex`, or `opencode`). Naming none is the normal answer, and it is the one to
   propose.

   **Only if the user named another harness for at least one role**, ask about the `harnesses:`
   block for the kinds they named: the `args` handed to that CLI and the `env` set on the process
   that runs it. Say plainly that both are passed through exactly as written — JDI composes,
   merges and translates nothing, and adds no flag of its own, so an approval- or sandbox-affecting
   flag is one the user typed and JDI prints it back before it spawns anything — and that paths
   must be absolute, because a leading `~` arrives as a literal tilde. Skip this question entirely
   when no role names another harness: there is no CLI to configure.

   **If the file already carries a `models:` block keyed by `deep`, `standard`, and `fast`, say
   so.** That is the pre-1.0.5 shape: it names no role, so nothing in it is read. Offer to rewrite
   it per role rather than keep a block that has no effect — this is the one place step 1's "keep
   every value the user does not change" would otherwise preserve something dead.

9. **Ask about consumers — optional** — Sibling repositories or client codebases that consume this
   repo's public interfaces (APIs, webhooks, published packages, tool surfaces). The Researcher
   sweeps these when a change alters an externally-consumed contract. Skip if there are none.

10. **Write `.jdi/config.yml`** — Write the file with the answers, keeping the schema's comments so
    the next reader can edit it by hand. Omit optional blocks the user skipped rather than writing
    empty scaffolding.

11. **Offer to record the branch and commit conventions where they belong** — JDI deliberately does
    **not** configure branch naming or commit message format: it reads them from the repo's own
    `CLAUDE.md` / `AGENTS.md`, which is where a team already writes them down. If neither file
    states them and the user told you what they are, offer to add them there. Do not write to those
    files without saying you are about to.

12. **Report and point at the next step** — Show the config you wrote, name anything you
    deliberately left unset, and suggest `/jdi:prep "<the first thing they want to build>"` — or
    `/jdi:help` for the tour.
