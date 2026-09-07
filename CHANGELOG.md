# Changelog

## 1.0.4

**`/jdi:herd` preps a list of issues in parallel — one git worktree, one agent, one `/jdi:prep` each.**

- New `/jdi:herd` command and a new optional `herd` block in `.jdi/config.yml` — `kind`,
  `max_parallel`, `args`, `env` and `seed`, every one of them defaulted. A repo that sets none of them, or
  omits the block entirely, is unaffected: no other command reads it, and nothing about an existing
  workflow changes because the command now exists.
- **One worktree per issue, on a scratch branch.** Parallel preps in a single checkout would fight
  over the branch `/jdi:prep` creates at its step 6. The scratch branch deliberately does **not**
  name the issue, because `/jdi:prep` keeps a branch that already names the work — a scratch branch
  carrying the issue ID would be adopted, and the plan would lose its **T6** slug.
- **It sets work up; it does not supervise it.** A spawned agent that stops at a question holds its
  turn and runs no tools, so it cannot call for help at the moment help is needed. The command
  offers a poll instead, reports which agent is waiting and what it asked, and names every worktree,
  workspace and scratch branch it created so they can be cleaned up.
- **Validates, never repairs.** No Herdr pane, no binary, no server socket, or no such agent kind
  each end the run with that reason. `/jdi:herd` starts no server, installs nothing, and never
  degrades to a sequential `/jdi:prep`: a herd that quietly became one prep is indistinguishable
  from a herd that worked.
- **`herd.seed` puts the gitignored state back.** A worktree comes from `origin/<default>`, so
  `.env` files, installed dependencies and local database names are simply absent from it. Left
  empty, each agent discovers that mid-run and repairs it differently — and two agents that settle
  on the same test database manufacture thousands of failures that read as a regression in the
  branch under test. `seed.copy`, `seed.set` and `seed.setup` are declarative and infer nothing: JDI
  never guesses that a repo is Rails, that `.env` exists, or which key names a database. `{{n}}`
  expands to the worktree index, which is how a shared resource becomes a per-worktree one. A
  `setup` command that exits non-zero disqualifies its worktree — no agent is started there,
  and the herd continues with the rest.
- **`herd.args` and `herd.env` are pass-through.** JDI composes no flag and translates none between
  agent kinds, so a permission-bypass flag is a value the user wrote down rather than a mode JDI
  entered on their behalf. `env` is enough to run a herd under a different account or profile —
  which also means the agents read *that* profile's settings, plugins and credentials, and JDI must
  be installed there for `/jdi:prep` to exist at all.

## 1.0.3

**Opt in and the Executor writes the failing test first — once the suite has been watched to run.**

- New `tdd` block in `.jdi/config.yml` — `enabled` (default `false`) and `test_instructions`. A repo
  that does not set the key behaves **exactly** as it did: no `TDD:` line is written, nothing is
  announced, and the `PLAN.md` a run produces is byte-identical to what it produced before the key
  existed. Off is silent, because nothing was skipped.
- Two named operations in `reference/testing.md`. **TS1** proves the test suite runs — the Butler,
  once per plan, before the first task. **TS2** writes the failing test first — the Executor, once
  per task, and only when TS1 said `on`. TS1's answer is one `TDD:` line in `PLAN.md`'s metadata:
  `on` names the date and the exact command that was proven, `off` names the rung that applied and
  the evidence for it.
- **Proven, not assumed.** TS1 derives an invocation, says out loud where it got it, and then
  watches the runner actually run before honouring the setting. A `tests/` folder, a `spec/`
  directory, a Makefile target, or a manifest dependency on a test framework is not evidence, and
  "no error" is not proof. **The exit code is not the signal** — `python3 -m unittest` exits `5` on
  "Ran 0 tests", which in a repo that has none yet is still proof the runner runs, while a wrapper
  that swallowed a missing interpreter can exit `0` and prove nothing. Proof is a printed
  test-result tally.
- **Degrades down, never up.** An unproven runner, an unreachable environment, or an ambiguity with
  nobody there to answer it all mean off for that plan, announced with the command that was tried
  and the output showing why it is not proof. Nothing turns TDD *on* that the configuration did not
  — not a `tests/` folder that appears mid-plan, and not a suite created by the plan's own first
  task. Fabricated red-run evidence is a worse outcome than not running TDD at all.
- **A plan whose first task ran before this key existed simply runs without TDD.** TS1 resolves once
  per plan and its line is never rewritten, so editing `.jdi/config.yml` mid-plan changes nothing
  until the next plan. **No line means no TDD, for every command, always** — a plan started before
  the key carries no `TDD:` line, is indistinguishable from one that started with TDD off, and
  neither is an invitation to go looking for a test runner or to ask the user about one.
- **`test_instructions` is prose, not a command.** An agent reads it and translates it into an
  invocation for the environment in front of it; the literal text is usually not runnable as typed,
  because the real invocation depends on a container, a service, or a working directory. "run
  `bin/rails test` inside the devcontainer" is a *better* answer than a bare `bin/rails test`.
  Leave it empty and the Butler works the invocation out from the repository itself.
- **`tdd` never changes what gets committed.** Tests and implementation land in the same commit, one
  per task, exactly as without it. TDD changes the order they are written in, not the history. A
  task with no testable behaviour is an announced skip, never a fabricated test, and a task is never
  complete at red — the Executor returns both the red run and the green.
- `/jdi:init` now asks about TDD, and asks **every time**: unlike the split pieces it depends on no
  tracker, so there is no configuration in which the question is skipped. It proposes
  `test_instructions` from what the repo already says about itself, tries the invocation once, and
  records the setting even when the run proved nothing — where that is still what the user wants.
  The config records intent, and the Butler re-checks it once per plan.
- **A `tests/` suite, the repository's first.** 15 tests on Python's standard-library `unittest`,
  with no third-party dependency and no install step: run `python3 -m unittest discover -s tests -v`
  from the repository root. They guard what this repo has historically half-finished — the version
  agreeing across `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` and the newest
  `CHANGELOG.md` heading; `reference/config.md`'s schema block, its defaults table and
  `jdi.config.example.yml` agreeing with one another; the enumerations in `README.md`, `AGENTS.md`
  and `reference/delegation.md` matching the `commands/`, `agents/` and `reference/` directories;
  and every command and role file carrying frontmatter with a description and a non-empty body.

## 1.0.2

**The splitter is configurable: pieces become subtickets, tracker tasks, or just commits.**

- New `split.pieces` key in `.jdi/config.yml` — `commits` (the default), `tasks`, or `subtickets`.
  It says what a split piece becomes **in addition to** a task file and a commit; the task files and
  the one-commit-per-task rhythm are identical in all three modes, so an existing repo with no such
  key behaves exactly as it did.
- `subtickets` mirrors every task, UAT included, as a child issue of the plan's issue — a Linear
  sub-issue, a Jira sub-task, a GitHub sub-issue. `tasks` mirrors them as a checklist on the issue
  where the tracker has one.
- Two new tracker operations in `reference/tracker.md`: **T7** materialises the pieces at split
  time, **T8** closes a piece when its task is marked done. `/jdi:split` and `/jdi:prep` call T7;
  `/jdi:done`, `/jdi:next`, and `/jdi:yolo` call T8.
- **Degrades down, never up.** No tracker, no issue, no reachable integration, no native checklist,
  or a declined confirmation all mean `commits` for that run, announced out loud. A configured
  `tasks` never quietly becomes `subtickets` — creating issues nobody asked for is the worse
  failure. Sub-issue creation asks once for the whole batch, listing the titles.
- Each mirrored task file records a `Ticket:` line, so re-running `/jdi:split` updates the mirror
  instead of stacking duplicates — the same idempotency rule T5 uses for the research comment.
- `/jdi:init` asks the new question, but only when a tracker is configured, and says plainly whether
  that tracker can express the mode being chosen.

## 1.0.1

**Installable at user scope or project scope.**

- **Claude Code** — documented `--scope project`, which writes a committable
  `.claude/settings.json` so JDI arrives with a clone. `examples/claude-project-settings.json` is
  the equivalent file for merging into settings that already exist.
- **OpenCode** — `bin/sync-opencode.sh` gained `--project [dir]`, alongside the existing (default)
  `--global`. Project mode writes `.opencode/{command,agent}/`, copies the reference files and roles
  into `.opencode/jdi/`, and rewrites every path **repo-relative** — the result holds no absolute
  paths and is committable. Also added `--help`.
- **Codex** — has no project scope; `codex plugin add` takes no `--scope` and records the install in
  `~/.codex/config.toml` machine-wide. Documented rather than worked around.
- Documented two things that bite when committing a project install: a directory source gets
  absolutized by the CLI (so use the `github` source for anything committed), and a marketplace
  **name** holds only one source per machine, so a local user-scope declaration blocks a git-URL
  project-scope one under the same name.

## 1.0.0

Initial extraction of the JDI workflow into a standalone, installable plugin.

- 16 commands, 7 delegatable roles, and the Butler orchestrator role.
- **Tracker-agnostic** — Linear, Jira, GitHub Issues, another, or none. `reference/tracker.md`
  defines six operations every command calls by name; each is capability-detected and skippable.
- **Plan-store-agnostic** — a folder in the repo (default) or an external service such as Obsidian
  or recuerd0. `reference/plan-store.md` carries the per-step differences, since external storage
  changes what is committable at every pause point.
- **Harness- and model-agnostic** — command and role bodies name roles and reasoning tiers
  (`deep` / `standard` / `fast`), never tools, models, or vendors. `reference/delegation.md` maps
  those onto whatever the harness offers, with inline role adoption as a first-class fallback where
  there are no subagents. Runs on Claude Code, Codex, and OpenCode.
- Per-repo configuration in `.jdi/config.yml`, written interactively by `/jdi:init`.
