# Changelog

## 1.0.4

**`/jdi:pair` runs a plan as two agents ping-ponging a failing test — but only when you ask.**

- **A repository that does not set the `pair` key is unaffected.** The block has no `enabled` key,
  because it never says *whether* to pair — only *which* two agents to pair. `/jdi:pair` is never
  invoked unless a user types it, and `/jdi:yolo`, `/jdi:execute` and `/jdi:next` stay single-agent
  regardless of what the block says. Nothing detects pairing, and no other command reads the key.
- **Ping-pong, rotating on the red/green boundary.** One agent writes a failing test and hands it
  over; the other reproduces it, makes it pass, refactors, and writes the next failing test. TDD is
  a prerequisite rather than a coincidence — the rotation point *is* the red/green boundary
  `reference/testing.md`'s **TS2** already turns on, so the swap is structural rather than a timer.
- **An agent asked to review and approve will approve.** "LGTM" costs one token, satisfies the
  instruction as written, and is indistinguishable in a transcript from a review that happened; no
  amount of "review carefully" changes what the cheapest compliant answer is. So the protocol does
  not ask for a review: **the receiver must re-run the incoming failing test itself, and confirm it
  fails on the named assertion, before it may implement.** `reference/testing.md` records that the
  Butler does not reproduce red, because a throwaway worktree or a second clone on every task costs
  more than the check is worth — **the partner does it for free, because it must run the test
  before it can implement.** Every red is independently verified by a second party that neither
  wrote the test nor chose the assertion. That is this mode's whole quality claim.
- **Two requirements, checked at run time.** A resolved `TDD: on` line in the plan — not merely
  `tdd.enabled`, because TDD can be configured on and still resolve off — and a Herdr session
  (`HERDR_ENV=1`). Either unmet and the run is not paired: the Butler announces which rung stopped
  it and offers to run the plan single-agent instead.
- **Degrades to not pairing, never to a half-pair.** One pane up and the other refused is a
  failure, not a degraded mode — a single agent taking both sides of a ping-pong is exactly the
  rubber stamp the protocol exists to prevent. Degradation is never automatic, and nothing turns
  pairing on that the user did not type.
- New `reference/pairing.md`, three operations under the `P` prefix. **P1** proves the pair can run
  — an eight-rung ladder, re-run in full on every invocation, because an agent name is a handle on
  a live process and panes never survive a session. **P2** is the exchange: a five-part handoff
  carrying the failing test, the red transcript, the test-list delta, the parked-notes ledger, and
  a read receipt with content. **P3** is the Butler moving reports between two panes and checking
  their shape, never their substance. Driver and navigator are turn assignments inside the existing
  Executor role, so no new spawnable agent type was added.
- Two new bidirectional test guards, on `commands/help.md`'s command table and `roles/butler.md`'s
  ownership table. Adding the first immediately found `/jdi:help` missing from its own table — 15
  commands listed against 16 files in `commands/` — so a user who ran `/jdi:help` never learned the
  command exists. The suite is 17 tests.
- `/jdi:init` now asks which two agents to pair, **but only when `herdr` is on `PATH`** — with no
  multiplexer to pair in, every answer would be unusable, so the question is skipped and no `pair`
  block is written. When it does ask, it proposes kinds rather than asking from zero: it settles
  P1's first and third layers here and now, takes `herdr integration status` as the evidence for
  the second, and says out loud that the second's definitive answer needs a live pane — and that
  `/jdi:pair` re-runs every layer in full on every invocation regardless.
- **The honest cost.** Arisholm et al. found pairing's overall correctness gain **not significant**
  for ~84% more effort, with the gains confined to complex tasks and less-expert pairs; two panes
  each carrying a full context per turn roughly doubles token cost on top. `/jdi:pair` is a
  deliberate choice for a hard task, not a default — which is why it is its own command rather than
  a flag on `/jdi:yolo`.
- **Deliberately left out of scope**, each for a stated reason: `commands/prep.md`'s config-block
  list (prep never resolves P1), `commands/status.md` (matching both earlier config-key releases),
  `agents/planner.md` (its "say which test proves which step" bullet is already the granularity P2
  consumes), a new `agents/*.md` role file (a file in `agents/` registers a spawnable agent type,
  and a "driver" reachable as an in-process subagent — not in a pane, unable to ping-pong — is
  worse than one nothing can instantiate), `bin/sync-opencode.sh` (glob-driven, so it needs no
  edit), and this changelog's own 1.0.0 entry (a historical record of what shipped then, so its
  command count is not a number to update).

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
